#coding=utf8

FMT_INT_HEADERS = ('group', 'left_days', 'lots', 'dir', 'float_profit', 'margin',
                   'income', 'ptf_profit', 'ptf_margin', 'ptf_income', 'ptf_principal')

FMT_FLOAT_4_HEADERS = ('strike', 'open_price', 'intrnic', 'time_value', 'last_price',
                       'implied_vol')

FMT_FLOAT_6_HEADERS = ('delta', 'gamma', 'vega', 'theta', 'ptf_delta', 'ptf_gamma',
                       'ptf_vega', 'ptf_theta')

def getFormedStr(header, value):
    try:
        if header is None:
            pass
        elif header in FMT_INT_HEADERS:
            return '%d' % value
        elif header in FMT_FLOAT_4_HEADERS:
            return '%.4f' % value
        elif header in FMT_FLOAT_6_HEADERS:
            return '%.6f' % value
    except:
        pass
    return str(value)