#coding=utf8
import threading as THD

import matplotlib.pyplot as PLT

from gui_impl.qt_mvc_impl import *
from .qtableview_utility import *
from .position_editor import PosEditor
from engine_algorithm.calculate_engine import Engine
from utility.messager import MessageQueue
from utility.self_defined_types import *


#ui created by qt designer
from qt_ui import ui_main_window


#############################################################################

def decorateAndPlot(sp, x_ls, y_ls, title=None, central_x=0):
    sp.plot(x_ls, y_ls, color="green", linewidth=2, linestyle="-")
    sp.plot([central_x,central_x], sp.get_ylim(), color="blue", linewidth=0.5, linestyle="--")
    if title:
        sp.set_title(title)
    sp.grid(True)
    return

def plotZeroLine(sp):
    sp.plot(sp.get_xlim(), [0,0], color="blue", linewidth=0.5, linestyle="-")

#############################################################################

class OptionCalculator(QMainWindow, ui_main_window.Ui_MainWindow):
    POSITION_TABLE_HEADERS = ('group', 'code', 'type', 'strike', 'expiry', 'left_days',
                              'lots', 'dir', 'open_price', 'delta', 'gamma', 'vega',
                              'theta', 'implied_vol', 'intrnic', 'time_value', 'last_price',
                              'float_profit', 'margin', 'income')

    PORTFOLIO_TABLE_HEADERS = ('group', 'ptf_profit', 'ptf_delta', 'ptf_gamma',
                               'ptf_vega', 'ptf_margin', 'ptf_income', 'ptf_principal')

    #-----------------------------------------------------------------------
    def __init__(self, parent=None):
        super(OptionCalculator, self).__init__(parent)
        self.setupUi(self)
        #define signal&slot
        self.connect(self.fresh_quotes_button, SIGNAL('clicked()'), self.__onRefreshQuoteBtClicked)
        self.connect(self.edit_position_button, SIGNAL('clicked()'), self.__onEditPosBtClicked)
        self.connect(self.plot_button, SIGNAL('clicked()'), self.__onPlotBtClicked)
        self.connect(self, SIGNAL('PLOT_SENSIBILITY'), self.__plotGreeksSensibility)
        self.connect(self, SIGNAL('PLOT_EXERCISE_CURVE'), self.__plotExerciseCurve)
        self.connect(self, SIGNAL('SET_ETF_DISPLAY'), self.__setEtfDataDisplay)
        self.connect(self, SIGNAL('SET_CENTRAL_DISPLAY'), self.__setCentralTableDisplay)
        #init position vtable
        self.pos_model = MatrixModel(self)
        self.pos_deleg = AutoFormDelegate(self)
        self.position_vtable.setItemDelegate(self.pos_deleg)
        self.position_vtable.setModel(self.pos_model)
        #init portfolio vtable
        self.ptf_model = MatrixModel(self)
        self.ptf_deleg = AutoFormDelegate(self)
        self.portfolio_vtable.setItemDelegate(self.ptf_deleg)
        self.portfolio_vtable.setModel(self.ptf_model)
        #show
        self.pos_model.setSize(0, OptionCalculator.POSITION_TABLE_HEADERS)
        self.ptf_model.setSize(0, OptionCalculator.PORTFOLIO_TABLE_HEADERS)
        self.show()
        #gui communication
        self.msg = MessageQueue()
        self.msg_event = THD.Event()
        self.msg_thread = THD.Thread(target=self.__handleMessage)
        self.msg_thread.start()
        #data engine
        self.engine = Engine(self)
        self.engine.qryInitialize()
        #flow control
        self.is_updating = False
        self.auto_refresh_timer = None
        self.__startAutoRefresh()
        #qt child
        self.edit_dialog = PosEditor(self)
        self.edit_dialog.setControler(self)
        return

    def quit(self):
        if not self.auto_refresh_timer is None:
            self.auto_refresh_timer.cancel()
        self.engine.quit()
        self.__pushMsg(MessageTypes.QUIT)
        self.msg_thread.join()
        return

    #-------------------------------------------------------------------------
    def onRepTableFeed(self, pos_data, ptf_data):
        self.__pushMsg(MessageTypes.REPLY_TABLE_FEED, (pos_data, ptf_data))

    def onRepEtfQuoteFeed(self, etf_data):
        self.__pushMsg(MessageTypes.REPLY_ETF_QUOTE_FEED, etf_data)

    def onRepCalGreeksSensibility(self, plot_data, x_axis_type):
        self.__pushMsg(MessageTypes.REPLY_CAL_SENSI, (plot_data, x_axis_type))

    def onRepCalExerciseCurve(self, plot_data):
        self.__pushMsg(MessageTypes.REPLY_EXERCISE_CURVE, plot_data)

    def onRepPositionBasedataFeed(self, positions):
        self.__pushMsg(MessageTypes.REPLY_POSITION_BASEDATA_FEED, positions)

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
            elif msg.type is MessageTypes.REPLY_CAL_SENSI:
                self.emit(SIGNAL('PLOT_SENSIBILITY'), msg.content[0], msg.content[1])
            elif msg.type is MessageTypes.REPLY_EXERCISE_CURVE:
                self.emit(SIGNAL('PLOT_EXERCISE_CURVE'), msg.content)
            elif msg.type is MessageTypes.REPLY_POSITION_BASEDATA_FEED:
                self.__updatePosEditorData(msg.content)
            elif msg.type is MessageTypes.QUIT:
                break
        return

    def __pushMsg(self, msg_type, content=None):
        self.msg.pushMsg(msg_type, content)
        self.msg_event.set()
    #----------------------------------------------------------------------
    def onEditorClickBtSaveAll(self, position_data):
        self.engine.qryReloadPositions(position_data)
        self.__queryUpdateData()

    def onEditorClickBtReloadPosition(self):
        self.engine.qryReloadPositions()
        self.engine.qryPositionBasedata()
        self.__queryUpdateData()

    #----------------------------------------------------------------------
    def __onRefreshQuoteBtClicked(self):
        self.__queryUpdateData()

    def __onEditPosBtClicked(self):
        self.edit_dialog.wakeupEditor()
        self.engine.qryPositionBasedata()

    def __onPlotBtClicked(self):
        x_axis_type = self.greeks_x_axis_combobox.currentIndex()
        if self.portfolio_checkBox.isChecked():
            id_ls = list()
            for r in getSelectedRows(self.portfolio_vtable):
                item = self.ptf_model.getValue(r, 0)
                try:
                    id_ls.append(int(item))
                except:
                    pass
            if id_ls:
                if x_axis_type == 0:
                    self.engine.qryCalGreeksSensibilityByGroup(id_ls, X_AXIS_TYPE.PRICE)
                elif x_axis_type == 1:
                    self.engine.qryCalGreeksSensibilityByGroup(id_ls, X_AXIS_TYPE.VOLATILITY)
                elif x_axis_type == 2:
                    self.engine.qryCalGreeksSensibilityByGroup(id_ls, X_AXIS_TYPE.TIME)
                elif x_axis_type == 3:
                    self.engine.qryExerciseCurveByGroup(id_ls)
        else:
            row_ls = getSelectedRows(self.position_vtable)
            if row_ls:
                if x_axis_type == 0:
                    self.engine.qryCalGreeksSensibilityByPosition(row_ls, X_AXIS_TYPE.PRICE)
                elif x_axis_type == 1:
                    self.engine.qryCalGreeksSensibilityByPosition(row_ls, X_AXIS_TYPE.VOLATILITY)
                elif x_axis_type == 2:
                    self.engine.qryCalGreeksSensibilityByPosition(row_ls, X_AXIS_TYPE.TIME)
                elif x_axis_type == 3:
                    self.engine.qryExerciseCurveByPosition(row_ls)
        return

    #-------------------------------------------------------------------
    def __startAutoRefresh(self):
        self.__queryUpdateData()
        self.auto_refresh_timer = THD.Timer(300, self.__startAutoRefresh)
        self.auto_refresh_timer.start()

    def __queryUpdateData(self):
        if not self.is_updating:
            self.is_updating = True
            self.engine.qryUpdateData()
            self.engine.qryEtfQuoteFeed()
            self.engine.qryTableDataFeed()

    def __setEtfDataDisplay(self, etf_data):
        self.update_time_label.setText('%s' % etf_data.getByHeader(0, 'update_time').strftime(r'%H:%M:%S'))
        self.etf_openprice_label.setText('open: %.3f' % etf_data.getByHeader(0, 'open_price'))
        self.etf_highprice_label.setText('high: %.3f' % etf_data.getByHeader(0, 'high_price'))
        self.etf_lowprice_label.setText('low: %.3f' % etf_data.getByHeader(0, 'low_price'))
        self.etf_lastprice_label.setText('last: %.3f' % etf_data.getByHeader(0, 'last_price'))

    def __setCentralTableDisplay(self, pos_data, ptf_data):
        self.pos_model.setTableContent(pos_data)
        self.ptf_model.setTableContent(ptf_data)
        #notify_updating_completed
        self.is_updating = False
        return

    def __updatePosEditorData(self, pos_table_handler):
        self.edit_dialog.setEditTableContent(pos_table_handler)

    def __plotGreeksSensibility(self, p_data, x_axis_type):
        if x_axis_type == X_AXIS_TYPE.PRICE:
            figure_name = 'by price'
        elif x_axis_type == X_AXIS_TYPE.VOLATILITY:
            figure_name = 'by volatility'
        elif x_axis_type == X_AXIS_TYPE.TIME:
            figure_name = 'by time'
        else:
            figure_name = ''

        fig = PLT.figure()
        fig.suptitle(figure_name)

        sp = fig.add_subplot(2, 2, 1)
        decorateAndPlot(sp, p_data['ax_x'], p_data['delta'],
                        title='delta', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 2)
        decorateAndPlot(sp, p_data['ax_x'], p_data['gamma'],
                        title='gamma', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 3)
        decorateAndPlot(sp, p_data['ax_x'], p_data['vega'],
                        title='vega', central_x=p_data['central_x'])

        sp = fig.add_subplot(2, 2, 4)
        decorateAndPlot(sp, p_data['ax_x'], p_data['theta'],
                        title='theta', central_x=p_data['central_x'])

        PLT.show()
        return

    def __plotExerciseCurve(self, plot_data):
        fig = PLT.figure()
        fig.suptitle('Theoretical earnings curve')

        sp = fig.add_subplot(1, 1, 1)
        decorateAndPlot(sp, plot_data['ax_x'], plot_data['exercise_profit'],
                        central_x=plot_data['central_x'])
        plotZeroLine(sp)

        PLT.show()
        return







