#coding=utf8
import datetime as DT

from marketdata.wind_data_provider import WindProvider

##############################################################

WIND_PVD = WindProvider()

class MarketdataAdaptor:
    def getOptionMultiplier(self):
        return 10000

    def getStockMultiplier(self):
        return 100

    def getContractType(self, code):
        rtn_typ = WIND_PVD.getOptionDirType(code)
        if rtn_typ == '认购':
            return 'call'
        elif rtn_typ == '认沽':
            return 'put'
        elif rtn_typ is None:
            return 'stock'
        return None

    def getStrikePrice(self, code):
        return WIND_PVD.getStrikePrice(code)

    def getExerciseDate(self, code):
        return WIND_PVD.getLastTradingDate(code).date()

    def getDaysBeforeExercise(self, code):
        return WIND_PVD.getOptionRemainingDays(code)

    def getLastprice(self, code):
        return WIND_PVD.getLastPrice(code)

    def getDailyOpen(self, code):
        return WIND_PVD.getDailyOpenPrice(code)

    def getDailyHigh(self, code):
        return WIND_PVD.getDailyHighPrice(code)

    def getDailyLow(self, code):
        return WIND_PVD.getDailyLowPrice(code)

    def getLastUpdateTime(self, code):
        return DT.datetime.now()