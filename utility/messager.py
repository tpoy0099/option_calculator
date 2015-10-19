#coding=utf8
import threading as THD
import datetime as DT

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