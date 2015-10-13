#coding=utf8
import threading as THD
import datetime as DT
from messager import MessageQueue, MessageTypes
from database_adaptor import DataProxy
from marketdata_adaptor import MarketdataAdaptor
from data_analyser import *

class Engine:
    etf_code = '510050.SH'
    STATISTICS_HEADERS = ('implied_vol', 'delta', 'gamma', 'vega',
                          'theta', 'intrnic', 'time_value')
    ##
    SYNC_INTERVAL = DT.timedelta(seconds=1)

    def __init__(self, gui):
        #marketdata service
        self.md  = MarketdataAdaptor()
        #database service
        self.db  = DataProxy()
        self.etf = None
        #flow control
        self.last_sync_time = DT.datetime.now()
        #gui communication
        self.msg = MessageQueue()
        self.msg_event = THD.Event()
        self.msg_thread = THD.Thread(target=self.__handleMessage)
        self.msg_thread.start()
        self.gui = gui
    #-------------------------------------------------------------
    def updateData(self):
        self.__pushMsg(MessageTypes.UPDATEDATA)

    def qryEtfQuoteFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_ETF_QUOTE_FEED)

    def qryTableDataFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_TABLE_FEED)

    def qryCalGreeksSensibilityByPrice(self, group_id_ls):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_PRICE, group_id_ls)

    def qryCalGreeksSensibilityByVolatility(self, group_id_ls):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_VOLA, group_id_ls)

    def qryCalGreeksSensibilityByTime(self, group_id_ls):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_TIME, group_id_ls)

    def qryCalGreeksSensibilityByPricePos(self, pos_row_idx):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_PRICE_POS, pos_row_idx)

    def qryCalGreeksSensibilityByVolatilityPos(self, pos_row_idx):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_VOLA_POS, pos_row_idx)

    def qryCalGreeksSensibilityByTimePos(self, pos_row_idx):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_BY_TIME, pos_row_idx)

    def initialize(self):
        self.__pushMsg(MessageTypes.INITIALIZE)

    def reloadPositions(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_RELOAD_POSITIONS)

    def quit(self):
        self.__pushMsg(MessageTypes.QUIT)
        self.msg_thread.join()

    #-------------------------------------------------------------
    def __pushMsg(self, msg_type, content=None):
        self.msg.pushMsg(msg_type, content)
        self.msg_event.set()

    def __handleMessage(self):
        while True:
            msg = self.msg.getMsg()
            if msg is None:
              self.msg_event.wait()
              self.msg_event.clear()
            #update marketdata order by user
            elif msg.type is MessageTypes.UPDATEDATA:
                self.__updateData()
            #qry engine provide table data
            elif msg.type is MessageTypes.GUI_QUERY_TABLE_FEED:
                self.__replyTableFeed()
            #qry etf data
            elif msg.type is MessageTypes.GUI_QUERY_ETF_QUOTE_FEED:
                self.__replyEtfQuoteFeed()
            #cal greeks sensibility
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_PRICE:
                self.__replyCalGreekSensiByPrice(msg.content)
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_VOLA:
                self.__replyCalGreekSensiByVolatility(msg.content)
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_TIME:
                self.__replyCalGreekSensiByTime(msg.content)
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_PRICE_POS:
                self.__replyCalGreekSensiByPricePos(msg.content)
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_VOLA_POS:
                self.__replyCalGreekSensiByVolatilityPos(msg.content)
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_BY_TIME_POS:
                self.__replyCalGreekSensiByTimePos(msg.content)
            #initialize
            elif msg.type is MessageTypes.INITIALIZE:
                self.__initialize()
            elif msg.type is MessageTypes.GUI_QUERY_RELOAD_POSITIONS:
                self.__reloadPositions()
            elif msg.type is MessageTypes.QUIT:
                break
        #thread terminate
        return

    def __initialize(self):
        self.db.initialize()
        pos = self.db.getPositionDataHandler()
        if pos.shape()[0] > 0:
            self.__updateData()
        return

    def __reloadPositions(self):
        self.db = DataProxy()
        self.__initialize()
        self.__replyEtfQuoteFeed()
        self.__replyTableFeed()

    def __updateData(self):
        self.last_sync_time = DT.datetime.now()
        self.__updateEtfData()
        pos = self.db.getPositionDataHandler()
        df_rows = pos.shape()[0]
        for r in range(0, df_rows):
            self.__updateRowBaseInfos(r)
            self.__updateRow(r)
        #update database
        self.db.updateData()

    #update etf price data
    def __updateEtfData(self):
        etf_last_price = self.md.getLastprice(Engine.etf_code)
        etf_last_time = self.md.getLastUpdateTime(Engine.etf_code)
        if self.etf:
            self.etf['update_time'] = etf_last_time
            self.etf['last_price'] = etf_last_price
            self.etf['high_price'] = max(etf_last_price, self.etf['high_price'])
            self.etf['low_price'] = min(etf_last_price, self.etf['low_price'])
        else:
            self.etf = {'last_price': etf_last_price,
                        'open_price': etf_last_price,
                        'high_price': etf_last_price,
                        'low_price' : etf_last_price,
                        'update_time': etf_last_time}

    #update basic_infos like expiry, strike_price etc.
    def __updateRowBaseInfos(self, irow):
        pos = self.db.getPositionDataHandler()
        code = pos.getByHeader(irow, 'code')
        pos.setByHeader(irow, 'type', self.md.getContractType(code))
        pos.setByHeader(irow, 'strike', self.md.getStrikePrice(code))
        pos.setByHeader(irow, 'expiry', self.md.getExerciseDate(code))
        pos.setByHeader(irow, 'left_days', self.md.getDaysBeforeExercise(code))

    #update
    def __updateRow(self, irow):
        pos = self.db.getPositionDataHandler()
        code = pos.getByHeader(irow, 'code')
        last_price = self.md.getLastprice(code)
        pos.setByHeader(irow, 'last_price', last_price)
        ###################################
        S = self.etf['last_price']
        K = pos.getByHeader(irow, 'strike')
        T = pos.getByHeader(irow, 'left_days')
        opt_type = pos.getByHeader(irow, 'type')
        #greeks
        stat = None
        if opt_type.lower() == 'call':
            stat = getStatistics(S, K, T, last_price, True)
        elif opt_type.lower() == 'put':
            stat = getStatistics(S, K, T, last_price, False)
        if stat:
            for header in Engine.STATISTICS_HEADERS:
                pos.setByHeader(irow, header, stat[header])
        #trade state
        float_profit = getFloatProfit(pos.getByHeader(irow, 'dir'),
                                      pos.getByHeader(irow, 'lots'),
                                      pos.getByHeader(irow, 'open_price'),
                                      last_price, self.md.getMultiplier(code))
        pos.setByHeader(irow, 'float_profit', float_profit)

    def __replyTableFeed(self):
        pos_data = self.db.getPositionDataHandler().getDataFrame().copy()
        pot_data = self.db.getPortfolioDataHandler().getDataFrame().copy()
        self.gui.replyQryTableFeed(pos_data, pot_data)

    def __replyEtfQuoteFeed(self):
        if self.etf:
            self.gui.replyQryEtfQuoteFeed(dict(self.etf))

    def __replyCalGreekSensiByPrice(self, group_id_ls):
        sli_data = self.db.getPositionDataByGroupId(group_id_ls)
        rtn = getGreeksSensibilityByPrice(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByPrice(rtn)

    def __replyCalGreekSensiByVolatility(self, group_id_ls):
        sli_data = self.db.getPositionDataByGroupId(group_id_ls)
        rtn = getGreeksSensibilityByVolatility(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByVolatility(rtn)

    def __replyCalGreekSensiByTime(self, group_id_ls):
        sli_data = self.db.getPositionDataByGroupId(group_id_ls)
        rtn = getGreeksSensibilityByTime(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByTime(rtn)

    def __replyCalGreekSensiByPricePos(self, pos_row_idx):
        sli_data = self.db.getPositionDataByRowIdx(pos_row_idx)
        rtn = getGreeksSensibilityByPrice(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByPrice(rtn)

    def __replyCalGreekSensiByVolatilityPos(self, pos_row_idx):
        sli_data = self.db.getPositionDataByRowIdx(pos_row_idx)
        rtn = getGreeksSensibilityByVolatility(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByVolatility(rtn)

    def __replyCalGreekSensiByTimePos(self, pos_row_idx):
        sli_data = self.db.getPositionDataByRowIdx(pos_row_idx)
        rtn = getGreeksSensibilityByTime(sli_data, self.etf['last_price'])
        self.gui.replyQryCalGreeksSensibilityByTime(rtn)


