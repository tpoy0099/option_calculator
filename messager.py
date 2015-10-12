#coding=utf8
import enum
import threading as THD
import datetime as DT

class MessageTypes(enum.Enum):
    QUIT = 0
    INITIALIZE = 1
    UPDATEDATA = 2

    GUI_QUERY_TABLE_FEED = 20
    GUI_QUERY_ETF_QUOTE_FEED = 21
    GUI_QUERY_CAL_SENSI_BY_PRICE = 22
    GUI_QUERY_CAL_SENSI_BY_VOLA  = 23
    GUI_QUERY_CAL_SENSI_BY_TIME  = 24

    REPLY_TABLE_FEED = 40
    REPLY_ETF_QUOTE_FEED = 41
    REPLY_CAL_SENSI_BY_PRICE = 42
    REPLY_CAL_SENSI_BY_VOLA  = 43
    REPLY_CAL_SENSI_BY_TIME  = 44

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