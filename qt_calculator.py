#coding=utf8
import threading as THD
import matplotlib.pyplot as PLT
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#ui created by qt designer
import ui_main_window
from position_editor import PosEditor
from calculate_engine import Engine
from messager import MessageQueue, MessageTypes

#######################################################
FMT_INT_HEADERS = ('left_days', 'lots', 'dir', 'float_profit', 'margin', 'income',
                   'pot_profit', 'pot_margin', 'pot_income', 'pot_principal')

FMT_FLOAT_4_HEADERS = ('strike', 'open_price', 'intrnic', 'time_value', 'last_price',
                       'implied_vol')

FMT_FLOAT_6_HEADERS = ('delta', 'gamma', 'vega', 'theta', 'pot_delta', 'pot_gamma',
                       'pot_vega')

def getFormatStr(header, item):
    try:
        if header is None:
            return ''
        elif header in FMT_INT_HEADERS:
            return '%d' % item
        elif header in FMT_FLOAT_4_HEADERS:
            return '%.4f' % item
        elif header in FMT_FLOAT_6_HEADERS:
            return '%.6f' % item
    except:
        pass
    return str(item)

def setWidgetItemContent(item, header, value):
    item.setText(getFormatStr(header, value))

def convert2WidgetItem(item, header):
    return QTableWidgetItem(getFormatStr(item, header))

def addTableWidgetRows(table, n=1):
    rows = table.rowCount()
    table.setRowCount(rows + n)
    cols = table.columnCount()
    for i in range(rows, rows+n):
        for c in range(0, cols):
            table.setItem(i, c, QTableWidgetItem(''))

def getSelectedRows(QTable):
    row_list = list()
    selected_range = QTable.selectedRanges()
    for rg in selected_range:
        row_list.extend(list(range(rg.topRow(), rg.bottomRow()+1)))
    return row_list

#############################################################################

class OptionCalculator(QMainWindow, ui_main_window.Ui_MainWindow):
    POSITION_TABLE_HEADERS = ('group', 'code', 'type', 'strike', 'expiry', 'left_days',
                              'lots', 'dir', 'open_price', 'delta', 'gamma', 'vega',
                              'theta', 'implied_vol', 'intrnic', 'time_value', 'last_price',
                              'float_profit', 'margin', 'income')

    PORTFOLIO_TABLE_HEADERS = ('group', 'pot_profit', 'pot_delta', 'pot_gamma',
                               'pot_vega', 'pot_margin', 'pot_income', 'pot_principal')

    #-----------------------------------------------------------------------
    def __init__(self, parent=None):
        super(OptionCalculator, self).__init__(parent)
        self.setupUi(self)
        #define signal&slot
        self.connect(self.fresh_quotes_button, SIGNAL('clicked()'), self.__onRefreshQuoteBtClicked)
        self.connect(self.edit_position_button, SIGNAL('clicked()'), self.__onEditPosBtClicked)
        self.connect(self.greeks_sensibility_button, SIGNAL('clicked()'), self.__onPlotGreeksSensibilityClicked)
        self.connect(self, SIGNAL('PLOT_SENSIBILITY'), self.__plotGreeksSensibility)
        self.connect(self, SIGNAL('SET_ETF_DISPLAY'), self.__setEtfDataDisplay)
        self.connect(self, SIGNAL('SET_CENTRAL_DISPLAY'), self.__setCentralTableDisplay)
        #init self-defined display
        self.__setCentralTableHeaders()
        #show
        self.edit_dialog = None
        self.show()
        #gui communication
        self.msg = MessageQueue()
        self.msg_event = THD.Event()
        self.msg_thread = THD.Thread(target=self.__handleMessage)
        self.msg_thread.start()
        #data engine
        self.engine = Engine(self)
        self.engine.initialize()
        #flow control
        self.is_updating = False
        self.auto_refresh_timer = None
        self.__startAutoRefresh()
        return

    def quit(self):
        if not self.auto_refresh_timer is None:
            self.auto_refresh_timer.cancel()
        self.engine.quit()
        self.__pushMsg(MessageTypes.QUIT)
        self.msg_thread.join()
        return

    def replyQryTableFeed(self, pos_data, pot_data):
        self.__pushMsg(MessageTypes.REPLY_TABLE_FEED, (pos_data, pot_data))

    def replyQryEtfQuoteFeed(self, etf_data):
        self.__pushMsg(MessageTypes.REPLY_ETF_QUOTE_FEED, etf_data)

    def replyQryCalGreeksSensibilityByPrice(self, plot_data):
        self.__pushMsg(MessageTypes.REPLY_CAL_SENSI_BY_PRICE, plot_data)

    def replyQryCalGreeksSensibilityByVolatility(self, plot_data):
        self.__pushMsg(MessageTypes.REPLY_CAL_SENSI_BY_VOLA, plot_data)

    def replyQryCalGreeksSensibilityByTime(self, plot_data):
        self.__pushMsg(MessageTypes.REPLY_CAL_SENSI_BY_TIME, plot_data)

    def __pushMsg(self, msg_type, content=None):
        self.msg.pushMsg(msg_type, content)
        self.msg_event.set()

    def __handleMessage(self):
        while True:
            msg = self.msg.getMsg()
            if msg is None:
              self.msg_event.wait()
              self.msg_event.clear()
            #received data for display
            elif msg.type is MessageTypes.REPLY_TABLE_FEED:
                self.emit(SIGNAL('SET_CENTRAL_DISPLAY'), msg.content[0], msg.content[1])
            elif msg.type is MessageTypes.REPLY_ETF_QUOTE_FEED:
                self.emit(SIGNAL('SET_ETF_DISPLAY'), msg.content)
            elif msg.type is MessageTypes.REPLY_CAL_SENSI_BY_PRICE:
                self.emit(SIGNAL('PLOT_SENSIBILITY'), msg.content, 'by price')
            elif msg.type is MessageTypes.REPLY_CAL_SENSI_BY_VOLA:
                self.emit(SIGNAL('PLOT_SENSIBILITY'), msg.content, 'by volatility')
            elif msg.type is MessageTypes.REPLY_CAL_SENSI_BY_TIME:
                self.emit(SIGNAL('PLOT_SENSIBILITY'), msg.content, 'by time')
            elif msg.type is MessageTypes.QUIT:
                break
        return

    #----------------------------------------------------------------------
    def __startAutoRefresh(self):
        self.__queryUpdateData()
        self.auto_refresh_timer = THD.Timer(300, self.__startAutoRefresh)
        self.auto_refresh_timer.start()

    def __onRefreshQuoteBtClicked(self):
        self.__queryUpdateData()

    def __onEditPosBtClicked(self):
        self.edit_dialog = PosEditor(self)
        self.edit_dialog.show()

    #def __onReloadBtClicked(self):
    #    self.__setCentralTableHeaders()
    #    self.engine.reloadPositions()

    def __onPlotGreeksSensibilityClicked(self):
        x_axis_type = self.greeks_x_axis_combobox.currentIndex()
        if self.portfolio_checkBox.isChecked():
            id_ls = [i+1 for i in getSelectedRows(self.portfolio_table)]
            if id_ls:
                #col = OptionCalculator.PORTFOLIO_TABLE_HEADERS.index('group')
                #item = self.portfolio_table.item(curr_row, col)
                if x_axis_type == 0:
                    self.engine.qryCalGreeksSensibilityByPrice(id_ls)
                elif x_axis_type == 1:
                    self.engine.qryCalGreeksSensibilityByVolatility(id_ls)
                elif x_axis_type == 2:
                    self.engine.qryCalGreeksSensibilityByTime(id_ls)
                elif x_axis_type == 3:
                    pass
        else:
            row_ls = getSelectedRows(self.positions_table)
            if row_ls:
                if x_axis_type == 0:
                    self.engine.qryCalGreeksSensibilityByPricePos(row_ls)
                elif x_axis_type == 1:
                    self.engine.qryCalGreeksSensibilityByVolatilityPos(row_ls)
                elif x_axis_type == 2:
                    self.engine.qryCalGreeksSensibilityByTimePos(row_ls)
                elif x_axis_type == 3:
                    pass
        return

    #-------------------------------------------------------------------
    def __queryUpdateData(self):
        if not self.is_updating:
            self.is_updating = True
            self.engine.updateData()
            self.engine.qryEtfQuoteFeed()
            self.engine.qryTableDataFeed()

    def __setEtfDataDisplay(self, etf_data):
        self.update_time_label.setText('%s' % etf_data['update_time'].strftime(r'%H:%M:%S'))
        self.etf_openprice_label.setText('%.4f' % etf_data['open_price'])
        self.etf_highprice_label.setText('%.4f' % etf_data['high_price'])
        self.etf_lowprice_label.setText('%.4f' % etf_data['low_price'])
        self.etf_lastprice_label.setText('%.4f' % etf_data['last_price'])

    def __setCentralTableHeaders(self):
        #position table
        self.positions_table.clear()
        self.positions_table.setRowCount(0)
        self.positions_table.setColumnCount(len(OptionCalculator.POSITION_TABLE_HEADERS))
        self.positions_table.setHorizontalHeaderLabels(OptionCalculator.POSITION_TABLE_HEADERS)
        #portfolio table
        self.portfolio_table.clear()
        self.portfolio_table.setRowCount(0)
        self.portfolio_table.setColumnCount(len(OptionCalculator.PORTFOLIO_TABLE_HEADERS))
        self.portfolio_table.setHorizontalHeaderLabels(OptionCalculator.PORTFOLIO_TABLE_HEADERS)
        return

    def __setCentralTableDisplay(self, pos_data, pot_data):
        #position
        rows = self.positions_table.rowCount()
        if pos_data.shape[0] > rows:
            addTableWidgetRows(self.positions_table, pos_data.shape[0] - rows)
        for r in range(0, pos_data.shape[0]):
            for header in pos_data.columns:
                if not header in OptionCalculator.POSITION_TABLE_HEADERS:
                    continue
                content = pos_data[header].iat[r]
                c = OptionCalculator.POSITION_TABLE_HEADERS.index(header)
                item = self.positions_table.item(r, c)
                setWidgetItemContent(item, header, content)

        #portfolio
        rows = self.portfolio_table.rowCount()
        if pot_data.shape[0] > rows:
            addTableWidgetRows(self.portfolio_table, pot_data.shape[0] - rows)
        for r in range(0, pot_data.shape[0]):
            for header in pot_data.columns:
                if not header in OptionCalculator.PORTFOLIO_TABLE_HEADERS:
                    continue
                content = pot_data[header].iat[r]
                c = OptionCalculator.PORTFOLIO_TABLE_HEADERS.index(header)
                item = self.portfolio_table.item(r, c)
                setWidgetItemContent(item, header, content)

        #notify_updating_completed
        self.is_updating = False
        return

    @staticmethod
    def decorateAndPlot(sp, x_ls, y_ls, title=None, central_x=0):
        sp.plot(x_ls, y_ls, color="green", linewidth=2, linestyle="-")
        sp.plot([central_x,central_x], sp.get_ylim(), color="blue", linewidth=0.5, linestyle="--")
        if title:
            sp.set_title(title)
        sp.grid(True)
        return

    def __plotGreeksSensibility(self, p_data, figure_name=''):
        fig = PLT.figure()
        fig.suptitle(figure_name)

        sp = fig.add_subplot(2, 2, 1)
        self.decorateAndPlot(sp, p_data['ax_x'], p_data['delta'],
                             title='delta', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 2)
        self.decorateAndPlot(sp, p_data['ax_x'], p_data['gamma'],
                             title='gamma', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 3)
        self.decorateAndPlot(sp, p_data['ax_x'], p_data['vega'],
                             title='vega', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 4)
        self.decorateAndPlot(sp, p_data['ax_x'], p_data['theta'],
                             title='theta', central_x=p_data['central_x'])

        PLT.show()
        return





