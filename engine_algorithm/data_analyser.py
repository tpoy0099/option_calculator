#coding=utf8
import datetime as DT

from engine_algorithm import bs_pricing_formula as BS

######################################################################
#trading days per year
DAYS_PER_YEAR = 365
#interest_rate
INT_R = 0.03

##############################################################
#analyse trade state
def getOptionIncome(trade_dir, lots, open_price, multiplier):
    if trade_dir > 0:
        return -open_price * lots * multiplier
    else:
        return open_price * lots * multiplier

def getFloatProfit(trade_dir, lots, open_price, last_price, multiplier):
    return (last_price - open_price) * trade_dir * lots * multiplier

def getPositionIncome(option_dir, lots, open_price):
    return option_dir * lots * open_price * -1

#期权最后交易日是第四个周三,实际结算为第四个周四
#但是实际上交易所可能针对节假日做相应调整, 该函数无法准确计算
#例如2015年10月22日是50etf期权理论交割日,
#但是实际因为国庆放假,交割推迟到了28日
#def findExpiryDate(year, month, target_weekday=4):
#    year = int(year)
#    month = int(month)
#    target_weekday = int(target_weekday)
#    day_of_week = DT.date(year, month, 1).weekday() + 1
#    if day_of_week <= target_weekday:
#        offset_days = 3 * 7 - day_of_week + target_weekday
#    else:
#        offset_days = 4 * 7 - day_of_week + target_weekday
#    return DT.date(year, month, 1 + offset_days)

#--------------------------------------------------------------------
def getTimeValue(strike_price, etf_price, option_price, is_call):
    if is_call:
        return option_price - max(etf_price - strike_price, 0)
    else:
        return option_price - max(strike_price - etf_price, 0)

def getIntrinsicValue(strike_price, etf_price, is_call):
    if is_call:
        return max(etf_price - strike_price, 0)
    else:
        return max(strike_price - etf_price, 0)

def getStatistics(S, K, T, opt_price, is_call, volatility=None):
    global DAYS_PER_YEAR, INT_R
    T /= DAYS_PER_YEAR
    res = dict()
    if is_call:
        res['implied_vol'] = BS.Implied_volatility_Call(S, K, INT_R, T, opt_price)
        if volatility is None:
            volatility = res['implied_vol']
        res['delta'] = BS.Delta_Call(S, K, INT_R, volatility, T)
        res['gamma'] = BS.Gamma(S, K, INT_R, volatility, T)
        res['vega'] = BS.Vega(S, K, INT_R, volatility, T) / 100
        res['theta'] = BS.Theta_Call(S, K, INT_R, volatility, T) / DAYS_PER_YEAR
        res['intrnic'] = getIntrinsicValue(K, S, True)
        res['time_value'] = getTimeValue(K, S, opt_price, True)
    else:
        res['implied_vol'] = BS.Implied_volatility_Put(S, K, INT_R, T, opt_price)
        if volatility is None:
            volatility = res['implied_vol']
        res['delta'] = BS.Delta_Put(S, K, INT_R, volatility, T)
        res['gamma'] = BS.Gamma(S, K, INT_R, volatility, T)
        res['vega'] = BS.Vega(S, K, INT_R, volatility, T) / 100
        res['theta'] = BS.Theta_Put(S, K, INT_R, volatility, T) / DAYS_PER_YEAR
        res['intrnic'] = getIntrinsicValue(K, S, False)
        res['time_value'] = getTimeValue(K, S, opt_price, False)
    return res

#-----------------------------------------------------------------
#return a list fill with imp_vol align by row number
#volatility.rows == option_df.rows
def getImpliedVolArray(option_df, asset_price):
    volatility = list()
    for r in range(0, option_df.shape[0]):
        row = option_df.iloc[r, :]
        if row['type'] == 'call':
            vol_f = BS.Implied_volatility_Call
        elif row['type'] == 'put':
            vol_f = BS.Implied_volatility_Put
        else:
            raise Exception('getImpliedVol with a None option data .')
        #fill
        volatility.append(vol_f(asset_price, row['strike'], INT_R,
                                row['left_days'] / DAYS_PER_YEAR,
                                row['last_price']))
    return volatility

def sumStocksDelta(stock_df):
    stock_delta = 0
    for r in range(0, stock_df.shape[0]):
        row = stock_df.iloc[r, :]
        stock_delta += 1 * 100 / 10000 * row['dir'] * row['lots']
    return stock_delta

def getGreeksSensibilityByTime(opt_df, stk_df, asset_price):
    res = {'central_x': 1, 'ax_x' : list(), 'delta': list(),
           'gamma': list(), 'vega' : list(), 'theta': list()}
    #expand x_axis range
    x_lower = 0.1
    x_upper = 2
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]
    #get data
    volatility = getImpliedVolArray(opt_df, asset_price)
    stock_delta = sumStocksDelta(stk_df)
    #option
    for F in res['ax_x']:
        delta = stock_delta
        gamma, vega, theta = 0, 0, 0
        for r in range(0, opt_df.shape[0]):
            row = opt_df.iloc[r, :]
            rtn = getStatistics(asset_price, row['strike'],
                                row['left_days'] * F,
                                row['last_price'],
                                row['type'] == 'call',
                                volatility[r])
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

def getGreeksSensibilityByVolatility(opt_df, stk_df, asset_price):
    res = {'central_x': 1, 'ax_x' : list(), 'delta': list(),
           'gamma': list(), 'vega' : list(), 'theta': list()}
    #expand x_axis range
    x_lower  = 0.1
    x_upper  = 2
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]
    #get data
    volatility = getImpliedVolArray(opt_df, asset_price)
    stock_delta = sumStocksDelta(stk_df)
    #option
    for F in res['ax_x']:
        delta = stock_delta
        gamma, vega, theta = 0, 0, 0
        for r in range(0, opt_df.shape[0]):
            row = opt_df.iloc[r, :]
            rtn = getStatistics(asset_price, row['strike'],
                                row['left_days'],
                                row['last_price'],
                                row['type'] == 'call',
                                volatility[r] * F)
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

def getGreeksSensibilityByPrice(opt_df, stk_df, asset_price):
    res = {'central_x': asset_price, 'ax_x' : list(), 'delta': list(),
           'gamma': list(), 'vega' : list(), 'theta': list()}
    #expand x_axis range
    x_lower  = asset_price * 0.7
    x_upper  = asset_price * 1.3
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]
    #get data
    volatility = getImpliedVolArray(opt_df, asset_price)
    stock_delta = sumStocksDelta(stk_df)
    #options
    for S in res['ax_x']:
        delta = stock_delta
        gamma, vega, theta = 0, 0, 0
        for r in range(0, opt_df.shape[0]):
            row = opt_df.iloc[r, :]
            rtn = getStatistics(S, row['strike'],
                                row['left_days'],
                                row['last_price'],
                                row['type'] == 'call',
                                volatility[r])
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

#--------------------------------------------------------------
def getExerciseProfitCurve(opt_df, stk_df, asset_price):
    res = {'central_x': asset_price, 'ax_x' : None,
           'exercise_profit': list()}

    x_lower  = asset_price * 0.5
    x_upper  = asset_price * 1.5
    step_len = (x_upper - x_lower) / 60
    price_range = [x_lower + s * step_len for s in range(0, 60)]

    section_point = set(opt_df['strike'])
    section_point.update(price_range)
    res['ax_x'] = list(section_point)
    res['ax_x'].sort()

    net_cost = (opt_df['open_price'] * -opt_df['dir'] * opt_df['lots']).sum() * 10000

    for price in res['ax_x']:
        profit = net_cost
        #stock
        for r in range(0, stk_df.shape[0]):
            row = stk_df.iloc[r, :]
            profit += getFloatProfit(row['dir'], row['lots'], row['open_price'],
                                     price, 100)
        #option
        for r in range(0, opt_df.shape[0]):
            row = opt_df.iloc[r, :]
            intrnic = getIntrinsicValue(row['strike'], price, row['type'] == 'call')
            profit += intrnic * row['dir'] * row['lots'] * 10000
        res['exercise_profit'].append(profit)
    return res

######################################################################
