#coding=utf8
import enum

class AutoEnums(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class MessageTypes(AutoEnums):
    QUIT = ()
    INITIALIZE = ()
    UPDATE_ALL = ()
    UPDATE_QUOTE_DATA = ()

    GUI_QUERY_TABLE_FEED = ()
    GUI_QUERY_ETF_QUOTE_FEED = ()
    GUI_QUERY_CAL_SENSI = ()
    GUI_QUERY_EXERCISE_CURVE = ()
    GUI_QUERY_POSITION_BASEDATA_FEED = ()

    GUI_QUERY_RELOAD_POSITIONS = ()

    REPLY_TABLE_FEED = ()
    REPLY_ETF_QUOTE_FEED = ()
    REPLY_CAL_SENSI = ()
    REPLY_EXERCISE_CURVE = ()
    REPLY_POSITION_BASEDATA_FEED = ()

    SAVE_POSITION_CSV = ()

#indicate the x data class
class XAxisType(AutoEnums):
    PRICE = ()
    VOLATILITY = ()
    TIME = ()

class PassedIndexType(AutoEnums):
    GROUP = ()
    ROW = ()