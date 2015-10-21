#coding=utf8
import threading as THD
import datetime as DT

import engine_algorithm.data_analyser as ANALYSER
import engine_algorithm.database_adaptor as DADAPTOR

from utility.data_handler import TableHandler
from marketdata.marketdata_adaptor import MarketdataAdaptor
from utility.messager import MessageQueue
from utility.self_defined_types import MessageTypes, PassedIndexType, XAxisType

################################################################
class Engine:
    etf_code = '510050.SH'
    ETF_QUOTE_HEADERS = ('last_price', 'open_price', 'high_price',
                         'low_price', 'update_time')

    STATISTICS_HEADERS = ('implied_vol', 'delta', 'gamma', 'vega',
                          'theta', 'intrnic', 'time_value')

    #-------------------------------------------------------------
    def __init__(self, gui):
        self.gui = gui
        #original position table
        self.ori_positions = None
        #etf quote
        self.etf = TableHandler()
        self.etf.reset(1, Engine.ETF_QUOTE_HEADERS, -1)
        #marketdata service
        self.md  = MarketdataAdaptor()
        #database service
        self.dp = DADAPTOR.DataProxy()
        self.__reloadPositions()
        #flow control
        self.last_sync_time = DT.datetime.now()
        #gui communication
        self.msg = MessageQueue()
        self.msg_event = THD.Event()
        self.msg_thread = THD.Thread(target=self.__handleMessage)
        self.msg_thread.start()
        return

    def quit(self):
        self.__pushMsg(MessageTypes.QUIT)
        self.msg_thread.join()

    #-------------------------------------------------------------
    def qryUpdateData(self):
        self.__pushMsg(MessageTypes.UPDATE_QUOTE_DATA)

    def qryEtfQuoteFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_ETF_QUOTE_FEED)

    def qryTableDataFeed(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_TABLE_FEED)

    def qryPositionBasedata(self):
        self.__pushMsg(MessageTypes.GUI_QUERY_POSITION_BASEDATA_FEED)

    def qryCalGreeksSensibilityByGroup(self, option_group_id, stock_group_id, x_axis_type):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI,
                       (option_group_id, stock_group_id,
                       PassedIndexType.GROUP, x_axis_type))

    def qryCalGreeksSensibilityByPosition(self, option_rows, stock_rows, x_axis_type):
        self.__pushMsg(MessageTypes.GUI_QUERY_CAL_SENSI,
                       (option_rows, stock_rows,
                        PassedIndexType.ROW, x_axis_type))

    def qryExerciseCurveByGroup(self, option_group_id, stock_group_id):
        self.__pushMsg(MessageTypes.GUI_QUERY_EXERCISE_CURVE,
                       (option_group_id, stock_group_id, PassedIndexType.GROUP))

    def qryExerciseCurveByPosition(self, option_rows, stock_rows):
        self.__pushMsg(MessageTypes.GUI_QUERY_EXERCISE_CURVE,
                       (option_rows, stock_rows, PassedIndexType.ROW))

    def qryReloadPositions(self, positions_data=None):
        self.__pushMsg(MessageTypes.GUI_QUERY_RELOAD_POSITIONS, positions_data)

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
                self.__updateData()
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
            elif msg.type is MessageTypes.GUI_QUERY_CAL_SENSI:
                self.__calGreekSensibility(msg.content[0], msg.content[1],
                                           msg.content[2], msg.content[3])

            elif msg.type is MessageTypes.GUI_QUERY_EXERCISE_CURVE:
                self.__calOptionExerciseProfitCurve(msg.content[0], msg.content[1],
                                                    msg.content[2])

            elif msg.type is MessageTypes.GUI_QUERY_RELOAD_POSITIONS:
                self.__reloadPositions(msg.content)

            elif msg.type is MessageTypes.QUIT:
                break
        #thread terminate
        return

    #-----------------------------------------------------------
    #positions should be a instance of TableHandler
    def __reloadPositions(self, positions=None):
        if type(positions) is TableHandler:
            pos = positions.toDataFrame()
        else:
            pos, err = DADAPTOR.loadPositionCsv()
            if not err is None:
                raise Exception('load position csv failed ...')
        #save pos
        self.ori_positions = pos
        #separate data
        option_rows = list()
        stock_rows = list()
        for r in range(0, pos.shape[0]):
            code = pos['code'].iat[r]
            contract_type = self.md.getContractType(code)
            if contract_type in ['call', 'put']:
                option_rows.append(r)
            else:
                stock_rows.append(r)
        option_df = pos.iloc[option_rows, :]
        stock_df = pos.iloc[stock_rows, :]
        self.dp.initialize(option_df, stock_df)
        self.__updateData(True)
        return

    def __updateData(self, update_baseinfo=False):
        self.last_sync_time = DT.datetime.now()
        #stock
        self.__updateEtfData()
        stk = self.dp.getStockData()
        for r in range(0, stk.rows()):
            self.__updateStockRow(r)
        #option
        opt = self.dp.getOptionData()
        for r in range(0, opt.rows()):
            if update_baseinfo:
                self.__updateRowBaseInfos(r)
            self.__updateOptionRow(r)
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

    def __updateStockRow(self, irow):
        pos = self.dp.getStockData()
        last_price = self.etf.getByHeader(0, 'last_price')
        float_profit = ANALYSER.getFloatProfit(pos.getByHeader(irow, 'dir'),
                                               pos.getByHeader(irow, 'lots'),
                                               pos.getByHeader(irow, 'open_price'),
                                               last_price, self.md.getStockMultiplier())
        pos.setByHeader(irow, 'last_price', last_price)
        pos.setByHeader(irow, 'float_profit', float_profit)
        return

    #update basic_infos like expiry, strike_price etc.
    def __updateRowBaseInfos(self, irow):
        pos = self.dp.getOptionData()
        code = pos.getByHeader(irow, 'code')
        pos.setByHeader(irow, 'type', self.md.getContractType(code))
        pos.setByHeader(irow, 'strike', self.md.getStrikePrice(code))
        pos.setByHeader(irow, 'expiry', self.md.getExerciseDate(code))
        pos.setByHeader(irow, 'left_days', self.md.getDaysBeforeExercise(code))
        return

    #update
    def __updateOptionRow(self, irow):
        pos = self.dp.getOptionData()
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
            stat = ANALYSER.getStatistics(S, K, T, last_price, True)
        elif opt_type.lower() == 'put':
            stat = ANALYSER.getStatistics(S, K, T, last_price, False)
        if stat:
            for header in Engine.STATISTICS_HEADERS:
                pos.setByHeader(irow, header, stat[header])
        #trade state
        float_profit = ANALYSER.getFloatProfit(pos.getByHeader(irow, 'dir'),
                                               pos.getByHeader(irow, 'lots'),
                                               pos.getByHeader(irow, 'open_price'),
                                               last_price, self.md.getOptionMultiplier())
        pos.setByHeader(irow, 'float_profit', float_profit)
        return

    def __feedDataTable(self):
        opt_data = TableHandler()
        opt_data.copyDataframe(self.dp.getOptionData().getDataFrame())
        stk_data = TableHandler()
        stk_data.copyDataframe(self.dp.getStockData().getDataFrame())
        ptf_data = TableHandler()
        ptf_data.copyDataframe(self.dp.getPortfolioData().getDataFrame())
        self.gui.onRepTableFeed(opt_data, stk_data, ptf_data)
        return

    def __feedEtfQuote(self):
        snap_etf = TableHandler()
        snap_etf.copy(self.etf)
        self.gui.onRepEtfQuoteFeed(snap_etf)
        return

    def __feedPositionBaseData(self):
        tdata = TableHandler()
        tdata.copyDataframe(self.ori_positions)
        self.gui.onRepPositionBasedataFeed(tdata)
        return

    def __calGreekSensibility(self, option_idx, stock_idx, idx_type, x_axis_type):
        opt = self.dp.getOptionData()
        stk = self.dp.getStockData()
        if idx_type is PassedIndexType.GROUP:
            opt_data = opt.getPositionDataByGroupId(option_idx)
            stk_data = stk.getPositionDataByGroupId(stock_idx)
        elif idx_type is PassedIndexType.ROW:
            opt_data = opt.getPositionDataByRowIdx(option_idx)
            stk_data = stk.getPositionDataByRowIdx(stock_idx)
        else:
            return

        if x_axis_type is XAxisType.PRICE:
            rtn = ANALYSER.getGreeksSensibilityByPrice(opt_data, stk_data,
                                                       self.etf.getByHeader(0, 'last_price'))
        elif x_axis_type is XAxisType.VOLATILITY:
            rtn = ANALYSER.getGreeksSensibilityByVolatility(opt_data, stk_data,
                                                            self.etf.getByHeader(0, 'last_price'))
        elif x_axis_type is XAxisType.TIME:
            rtn = ANALYSER.getGreeksSensibilityByTime(opt_data, stk_data,
                                                      self.etf.getByHeader(0, 'last_price'))
        else:
            return

        self.gui.onRepCalGreeksSensibility(rtn, x_axis_type)
        return

    def __calOptionExerciseProfitCurve(self, option_idx, stock_idx, idx_type):
        opt = self.dp.getOptionData()
        stk = self.dp.getStockData()
        if idx_type is PassedIndexType.GROUP:
            opt_data = opt.getPositionDataByGroupId(option_idx)
            stk_data = stk.getPositionDataByGroupId(stock_idx)
        elif idx_type is PassedIndexType.ROW:
            opt_data = opt.getPositionDataByRowIdx(option_idx)
            stk_data = stk.getPositionDataByRowIdx(stock_idx)
        else:
            return

        rtn = ANALYSER.getExerciseProfitCurve(opt_data, stk_data,
                                              self.etf.getByHeader(0, 'last_price'))
        self.gui.onRepCalExerciseCurve(rtn)
        return


