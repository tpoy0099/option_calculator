#coding=utf8
import enum
import threading as THD
import datetime as DT

class AutoEnums(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class MessageTypes(AutoEnums):
    QUIT = ()
    INITIALIZE = ()
    UPDATEDATA = ()

    GUI_QUERY_TABLE_FEED = ()
    GUI_QUERY_ETF_QUOTE_FEED = ()
    GUI_QUERY_CAL_SENSI_BY_PRICE = ()
    GUI_QUERY_CAL_SENSI_BY_VOLA  = ()
    GUI_QUERY_CAL_SENSI_BY_TIME  = ()
    GUI_QUERY_CAL_SENSI_BY_PRICE_POS = ()
    GUI_QUERY_CAL_SENSI_BY_VOLA_POS  = ()
    GUI_QUERY_CAL_SENSI_BY_TIME_POS  = ()

    GUI_QUERY_RELOAD_POSITIONS = ()

    REPLY_TABLE_FEED = ()
    REPLY_ETF_QUOTE_FEED = ()
    REPLY_CAL_SENSI_BY_PRICE = ()
    REPLY_CAL_SENSI_BY_VOLA  = ()
    REPLY_CAL_SENSI_BY_TIME  = ()

class Message:
    def __init__(self, msg_type, content):
        self.time = DT.datetime.now()
        self.type = msg_type
        self.content = content

#Is thread safty
class MessageQueue:
    def __init__(self):
        self.msg_queue = list()
        self.lock = THD.RLock()

    def pushMsg(self, msg_type, content):
        self.lock.acquire()
        self.msg_queue.append(Message(msg_type, content))
        self.lock.release()

    def getMsg(self):
        msg = None
        self.lock.acquire()
        if len(self.msg_queue) > 0:
            msg = self.msg_queue.pop(0)
        self.lock.release()
        return msg