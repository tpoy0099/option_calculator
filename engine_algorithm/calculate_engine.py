#coding=utf8
import threading as THD

from utility.messager import MessageQueue
from utility.self_defined_types import *
from marketdata.database_adaptor import DataProxy
from marketdata.marketdata_adaptor import MarketdataAdaptor
from engine_algorithm.data_analyser import *
from utility.data_handler import *


################################################################
class Engine:
    etf_code = '510050.SH'
    ETF_QUOTE_HEADERS = ('last_price', 'open_price', 'high_price',
                         'low_price', 'update_time')
    STATISTICS_HEADERS = ('implied_vol', 'delta', 'gamma', 'vega',
                          'theta', 'intrnic', 'time_value')
    ##
    SYNC_INTERVAL = DT.timedelta(seconds=1)

    def __init__(self, gui):
        #marketdata service
        self.md  = MarketdataAdaptor()
        #database service
        self.dp  = DataProxy()
        #etf quote
        self.etf = TableHandler()
        self.etf.reset(1, Engine.ETF_QUOTE_HEADERS, -1)
        #flow control
        self.last_sync_time = DT.datetime.now()
        #gui communication
        self.msg = MessageQueue()
        self.msg_event = THD.Event()
        self.msg_thread = THD.Thread(target=self.__handleMessage)
        self.msg_thread.start()
        self.gui = gui
        return

    #-------------------------------------------------------------
    def qryUpdateData(self):
        self.__pushMsg(MessageTypes.UPDATE_QUOTE_DATA)

    def qryEtfQuoteFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_ETF_QUOTE_FEED)

    def qryTableDataFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_TABLE_FEED)

    def qryPositionBasedata(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_POSITION_BASEDATA_FEED)

    def qryCalGreeksSensibilityByGroup(self, group_id_ls, x_axis_type):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_PTF,
                       (group_id_ls, PASS_INDEX_TYPE.GROUP, x_axis_type))

    def qryCalGreeksSensibilityByPosition(self, pos_row_idx, x_axis_type):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI_POS,
                       (pos_row_idx, PASS_INDEX_TYPE.ROW, x_axis_type))

    def qryReloadPositions(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_RELOAD_POSITIONS)

    def initialize(self):
        self.__pushMsg(MessageTypes.INITIALIZE)

    def quit(self):
        self.__pushMsg(MessageTypes.QUIT)
        self.msg_thread.join()

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
            elif msg.type is MessageTypes.UPDATE_QUOTE_DATA:
                self.__updateQuoteData()
            elif msg.type is MessageTypes.UPDATE_ALL:
                pass
            #qry engine provide table data
            elif msg.type is MessageTypes.GUI_QUERY_TABLE_FEED:
                self.__feedDataTable()
            #qry etf data
            elif msg.type is MessageTypes.GUI_QUERY_ETF_QUOTE_FEED:
                self.__feedEtfQuote()
            #qry position base data for editor
            elif msg.type is MessageTypes.GUI_QUERY_POSITION_BASEDATA_FEED:
                self.__feedPositionBaseData()
            #cal greeks sensibility
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_PTF:
                self.__calGreekSensibility(msg.content[0], msg.content[1], msg.content[2])
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI_POS:
                self.__calGreekSensibility(msg.content[0], msg.content[1], msg.content[2])
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
        self.dp.initialize()
        self.__updateAll()
        return

    def __reloadPositions(self):
        self.dp = DataProxy()
        self.__initialize()
        self.__feedEtfQuote()
        self.__feedDataTable()
        return

    def __updateQuoteData(self):
        self.last_sync_time = DT.datetime.now()
        self.__updateEtfData()
        pos = self.dp.getPositionDataHandler()
        for r in range(0, pos.rows()):
            self.__updateRow(r)
        #update database
        self.dp.updateData()
        return

    def __updateAll(self):
        self.last_sync_time = DT.datetime.now()
        self.__updateEtfData()
        pos = self.dp.getPositionDataHandler()
        for r in range(0, pos.rows()):
            self.__updateRowBaseInfos(r)
            self.__updateRow(r)
        #update database
        self.dp.updateData()
        return

    #update etf price data
    def __updateEtfData(self):
        etf_last_price = self.md.getLastprice(Engine.etf_code)
        self.etf.setByHeader(0, 'last_price', etf_last_price)
        self.etf.setByHeader(0, 'update_time', self.md.getLastUpdateTime(Engine.etf_code))
        if not self.etf.getByHeader(0, 'open_price') < 0:
            self.etf.setByHeader(0, 'high_price', max(etf_last_price, self.etf.getByHeader(0, 'high_price')))
            self.etf.setByHeader(0, 'low_price', min(etf_last_price, self.etf.getByHeader(0, 'low_price')))
        else:
            O = self.md.getDailyOpen(Engine.etf_code)
            H = self.md.getDailyHigh(Engine.etf_code)
            L = self.md.getDailyLow(Engine.etf_code)
            if O and H and L:
                self.etf.setByHeader(0, 'open_price', O)
                self.etf.setByHeader(0, 'high_price', H)
                self.etf.setByHeader(0, 'low_price', L)
        return

    #update basic_infos like expiry, strike_price etc.
    def __updateRowBaseInfos(self, irow):
        pos = self.dp.getPositionDataHandler()
        code = pos.getByHeader(irow, 'code')
        pos.setByHeader(irow, 'type', self.md.getContractType(code))
        pos.setByHeader(irow, 'strike', self.md.getStrikePrice(code))
        pos.setByHeader(irow, 'expiry', self.md.getExerciseDate(code))
        pos.setByHeader(irow, 'left_days', self.md.getDaysBeforeExercise(code))
        return

    #update
    def __updateRow(self, irow):
        pos = self.dp.getPositionDataHandler()
        code = pos.getByHeader(irow, 'code')
        last_price = self.md.getLastprice(code)
        pos.setByHeader(irow, 'last_price', last_price)
        ###################################
        S = self.etf.getByHeader(0, 'last_price')
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
        return

    def __feedDataTable(self):
        pos_df = self.dp.getPositionDataHandler().getDataFrame().copy()
        pos_data = TableHandler()
        pos_data.copyFromDataframe(pos_df)
        ptf_df = self.dp.getPortfolioDataHandler().getDataFrame().copy()
        ptf_data = TableHandler()
        ptf_data.copyFromDataframe(ptf_df)
        self.gui.onRepTableFeed(pos_data, ptf_data)
        return

    def __feedEtfQuote(self):
        snap_etf = TableHandler()
        snap_etf.copy(self.etf)
        self.gui.onRepEtfQuoteFeed(snap_etf)
        return

    def __feedPositionBaseData(self):
        tdata = TableHandler()
        base_pos = self.dp.getOriginPosHandler()
        tdata.copyFromDataframe(base_pos.getDataFrame())
        self.gui.onRepPositionBasedataFeed(tdata)
        return

    def __calGreekSensibility(self, idx_ls, idx_type, x_axis_type):
        if idx_type is PASS_INDEX_TYPE.GROUP:
            sli_data = self.dp.getPositionDataByGroupId(idx_ls)
        elif idx_type is PASS_INDEX_TYPE.ROW:
            sli_data = self.dp.getPositionDataByRowIdx(idx_ls)
        else:
            return

        if x_axis_type is X_AXIS_TYPE.PRICE:
            rtn = getGreeksSensibilityByPrice(sli_data, self.etf.getByHeader(0, 'last_price'))
        elif x_axis_type is X_AXIS_TYPE.VOLATILITY:
            rtn = getGreeksSensibilityByVolatility(sli_data, self.etf.getByHeader(0, 'last_price'))
        elif x_axis_type is X_AXIS_TYPE.TIME:
            rtn = getGreeksSensibilityByTime(sli_data, self.etf.getByHeader(0, 'last_price'))
        else:
            return

        self.gui.onRepCalGreeksSensibility(rtn, x_axis_type)
        return


