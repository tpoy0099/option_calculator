#coding=utf8
import datetime as DT

from engine_algorithm import bs_pricing_formula as BS


#trading days per year
DAYS_PER_YEAR = 250
#interest_rate
INT_R = 0.03

#期权最后交易日是第四个周三,实际结算为第四个周四
def findExpiryDate(year, month, target_weekday=4):
    year = int(year)
    month = int(month)
    target_weekday = int(target_weekday)
    day_of_week = DT.date(year, month, 1).weekday() + 1
    if day_of_week <= target_weekday:
        offset_days = 3 * 7 - day_of_week + target_weekday
    else:
        offset_days = 4 * 7 - day_of_week + target_weekday
    return DT.date(year, month, 1 + offset_days)

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
        res['vega'] = BS.Vega(S, K, INT_R, volatility, T)
        res['theta'] = BS.Theta_Call(S, K, INT_R, volatility, T)
        res['intrnic'] = getIntrinsicValue(K, S, True)
        res['time_value'] = getTimeValue(K, S, opt_price, True)
    else:
        res['implied_vol'] = BS.Implied_volatility_Put(S, K, INT_R, T, opt_price)
        if volatility is None:
            volatility = res['implied_vol']
        res['delta'] = BS.Delta_Put(S, K, INT_R, volatility, T)
        res['gamma'] = BS.Gamma(S, K, INT_R, volatility, T)
        res['vega'] = BS.Vega(S, K, INT_R, volatility, T)
        res['theta'] = BS.Theta_Put(S, K, INT_R, volatility, T)
        res['intrnic'] = getIntrinsicValue(K, S, False)
        res['time_value'] = getTimeValue(K, S, opt_price, False)
    return res

def getGreeksSensibilityByTime(pos_df, asset_price):
    res = {'central_x': 1,
           'ax_x' : list(),
           'delta': list(),
           'gamma': list(),
           'vega' : list(),
           'theta': list()}

    x_lower  = 0.1
    x_upper  = 2
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]

    vol_ls = list()
    for pr in pos_df.iterrows():
        row = pr[1]
        if row['type'] == 'call':
            vol_ls.append(BS.Implied_volatility_Call(asset_price, row['strike'], INT_R,
                                                     row['left_days']/DAYS_PER_YEAR,
                                                     row['last_price']))
        else:
            vol_ls.append(BS.Implied_volatility_Put(asset_price, row['strike'], INT_R,
                                                    row['left_days']/DAYS_PER_YEAR,
                                                    row['last_price']))

    for F in res['ax_x']:
        delta = 0
        gamma = 0
        vega  = 0
        theta = 0
        i_vol = 0
        for pr in pos_df.iterrows():
            row = pr[1]
            rtn = getStatistics(asset_price, row['strike'],
                                row['left_days'] * F,
                                row['last_price'],
                                row['type'] == 'call',
                                vol_ls[i_vol])
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
            i_vol += 1
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

def getGreeksSensibilityByVolatility(pos_df, asset_price):
    res = {'central_x': 1,
           'ax_x' : list(),
           'delta': list(),
           'gamma': list(),
           'vega' : list(),
           'theta': list()}

    x_lower  = 0.1
    x_upper  = 2
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]

    vol_ls = list()
    for pr in pos_df.iterrows():
        row = pr[1]
        if row['type'] == 'call':
            vol_ls.append(BS.Implied_volatility_Call(asset_price, row['strike'], INT_R,
                                                     row['left_days']/DAYS_PER_YEAR,
                                                     row['last_price']))
        else:
            vol_ls.append(BS.Implied_volatility_Put(asset_price, row['strike'], INT_R,
                                                    row['left_days']/DAYS_PER_YEAR,
                                                    row['last_price']))

    for F in res['ax_x']:
        delta = 0
        gamma = 0
        vega  = 0
        theta = 0
        i_vol = 0
        for pr in pos_df.iterrows():
            row = pr[1]
            rtn = getStatistics(asset_price, row['strike'],
                                row['left_days'],
                                row['last_price'],
                                row['type'] == 'call',
                                vol_ls[i_vol] * F)
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
            i_vol += 1
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

def getGreeksSensibilityByPrice(pos_df, asset_price):
    res = {'central_x': asset_price,
           'ax_x' : list(),
           'delta': list(),
           'gamma': list(),
           'vega' : list(),
           'theta': list()}

    x_lower  = asset_price * 0.7
    x_upper  = asset_price * 1.3
    step_len = (x_upper - x_lower) / 60
    res['ax_x'] = [x_lower + s * step_len for s in range(0, 60)]

    vol_ls = list()
    for pr in pos_df.iterrows():
        row = pr[1]
        if row['type'] == 'call':
            vol_ls.append(BS.Implied_volatility_Call(asset_price, row['strike'], INT_R,
                                                     row['left_days']/DAYS_PER_YEAR,
                                                     row['last_price']))
        else:
            vol_ls.append(BS.Implied_volatility_Put(asset_price, row['strike'], INT_R,
                                                    row['left_days']/DAYS_PER_YEAR,
                                                    row['last_price']))

    for S in res['ax_x']:
        delta = 0
        gamma = 0
        vega  = 0
        theta = 0
        i_vol = 0
        for pr in pos_df.iterrows():
            row = pr[1]
            rtn = getStatistics(S, row['strike'],
                                row['left_days'],
                                row['last_price'],
                                row['type'] == 'call',
                                vol_ls[i_vol])
            multi = row['dir'] * row['lots']
            delta += rtn['delta'] * multi
            gamma += rtn['gamma'] * multi
            vega  += rtn['vega']  * multi
            theta += rtn['theta'] * multi
            i_vol += 1
        #save one resault
        res['delta'].append(delta)
        res['gamma'].append(gamma)
        res['vega'].append(vega)
        res['theta'].append(theta)
    return res

######################################################################
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