#coding=utf8
import random
import datetime as DT
from wind_data_provider import WindProvider

##############################################################

WIND_PVD = WindProvider()

class MarketdataAdaptor:
    def getMultiplier(self, code):
        if code != '510050':
            return 10000
        else:
            return 100

    def getContractType(self, code):
        rtn_typ = WIND_PVD.getOptionDirType(code)
        if rtn_typ == '认购':
            return 'call'
        elif rtn_typ == '认沽':
            return 'put'
        return None

    def getStrikePrice(self, code):
        return WIND_PVD.getStrikePrice(code)

    def getExerciseDate(self, code):
        return WIND_PVD.getLastTradingDate(code).date()

    def getDaysBeforeExercise(self, code):
        return WIND_PVD.getOptionRemainingDays(code)

    def getLastprice(self, code):
        return WIND_PVD.getLastPrice(code)

    def getLastUpdateTime(self, code):
        return DT.datetime.now()