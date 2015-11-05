#coding=utf8
import numpy
import scipy.stats
from scipy.optimize import brentq

SQRT = numpy.sqrt
LOG  = numpy.log
EXP  = numpy.exp
NORM_CDF = scipy.stats.norm.cdf
NORM_PDF = scipy.stats.norm.pdf

IV_LOWER_BOUND = 1e-8
###################################################################
#K : option strike price
#S : price of the underlying asset
#r : risk-free interest rate, 0.03 as 3%
#sigma : asset volatility or implied volatility, 0.25 as 25%
#T : days before expiry, 31/365 as 31 days

#https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model#Black-Scholes_formula
#In practice, some sensitivities are usually quoted in scaled-down terms,
# to match the scale of likely changes in the parameters. For example,
# rho is often reported divided by 10,000 (1 basis point rate change),
# vega by 100 (1 vol point change),
# theta by 365 or 252
# (1 day decay based on either calendar days or trading days per year).

#Black and Scholes
def BlackScholes_d1(S, K, r, sigma, T):
    if sigma > IV_LOWER_BOUND:
        return (LOG(S/K) + (r + sigma**2 / 2) * T) / (sigma * SQRT(T))
    return scipy.inf if S > K else -scipy.inf

def BlackScholes_d2(S, K, r, sigma, T):
    #return (LOG_F(S/K) + (r - sigma**2 / 2) * T) / (sigma * SQRT(T))
    return BlackScholes_d1(S, K, r, sigma, T) - (sigma * SQRT(T))

#C(S,t) = N(d1)S - N(d2)Ke**(-rT)
def BlackScholes_Call_pricing(S, K, r, sigma, T):
    return (NORM_CDF(BlackScholes_d1(S, K, r, sigma, T)) * S -
            NORM_CDF(BlackScholes_d2(S, K, r, sigma, T)) * K * EXP(-r * T))

#P(S,t) = N(-d2)Ke**(-rT) - N(-d1)S
def BlackScholes_Put_pricing(S, K, r, sigma, T):
    return (NORM_CDF(-BlackScholes_d2(S, K, r, sigma, T)) * K * EXP(-r * T) -
            NORM_CDF(-BlackScholes_d1(S, K, r, sigma, T)) * S)

def Delta_Call(S, K, r, sigma, T):
    return NORM_CDF(BlackScholes_d1(S, K, r, sigma, T))

def Delta_Put(S, K, r, sigma, T):
    return NORM_CDF(BlackScholes_d1(S, K, r, sigma, T)) - 1

def Gamma(S, K, r, sigma, T):
    if sigma > IV_LOWER_BOUND:
        return NORM_PDF(BlackScholes_d1(S, K, r, sigma, T)) / (S * sigma * SQRT(T))
    return 0

def Vega(S, K, r, sigma, T):
    return NORM_PDF(BlackScholes_d1(S, K, r, sigma, T)) * S * SQRT(T)

def Theta_Call(S, K, r, sigma, T):
    return (-S * sigma * NORM_PDF(BlackScholes_d1(S, K, r, sigma, T)) / (2 * SQRT(T)) -
            r * K * EXP(-r * T) * NORM_CDF(BlackScholes_d2(S, K, r, sigma, T)))

def Theta_Put(S, K, r, sigma, T):
    return (-S * sigma * NORM_PDF(BlackScholes_d1(S, K, r, sigma, T)) / (2 * SQRT(T)) +
            r * K * EXP(-r * T) * NORM_CDF(-BlackScholes_d2(S, K, r, sigma, T)))

def Rho_Call(S, K, r, sigma, T):
    return K * T * EXP(-r * T) * NORM_CDF(BlackScholes_d2(S, K, r, sigma, T))

def Rho_Put(S, K, r, sigma, T):
    return -K * T * EXP(-r * T) * NORM_CDF(-BlackScholes_d2(S, K, r, sigma, T))

#http://www.codeandfinance.com/finding-implied-vol.html
#Newton's method
#def implied_volatility_newton(option_market_price, pricing_f, S, K, r, T):
#    MAX_ITERATIONS = 100
#    PRECISION = 1e-5
#    sigma = 0.5
#    for i in range(0, MAX_ITERATIONS):
#        price = pricing_f(S, K, r, sigma, T)
#        diff = option_market_price - price
#        #print(i, sigma, diff)
#        if abs(diff) < PRECISION:
#            return sigma
#        #x1 = x0 + f(x0) / f'(x0)
#        sigma = sigma + diff / Vega(S, K, r, sigma, T)
#    # value wasn't found, return best guess so far
#    return sigma

#Calculate the Black-Scholes implied volatility using the Brent method (for reference).
#Return float, a zero of f between a and b.
#f must be a continuous function, and [a,b] must be a sign changing interval.
#it means f(a) and f(b) must have different signs
def implied_volatility_brent(option_market_price, pricing_f, S, K, r, T):
    try:
        v =  brentq(lambda sigma : option_market_price - pricing_f(S, K, r, sigma, T),
                    0, 10)
        return v if v > IV_LOWER_BOUND else IV_LOWER_BOUND
    except:
        return IV_LOWER_BOUND

def Implied_volatility_Call(S, K, r, T, market_option_price):
    return implied_volatility_brent(market_option_price, BlackScholes_Call_pricing, S, K, r, T)

def Implied_volatility_Put(S, K, r, T, market_option_price):
    return implied_volatility_brent(market_option_price, BlackScholes_Put_pricing, S, K, r, T)

#############################################################
#comparing with
#http://www.fintools.com/resources/online-calculators/options-calcs/options-calculator/
def functional_testing(S0, K0, r0, T0, Call_price0, Put_price0):
    print('================ call option ================')
    sigma0 = Implied_volatility_Call(S0, K0, r0, T0, Call_price0)
    print('implied_vol: ', sigma0)
    if not sigma0 is None:
        print('BS_price: ', BlackScholes_Call_pricing(S0, K0, r0, sigma0, T0))
        print('Delta for 1.0 price change: ', Delta_Call(S0, K0, r0, sigma0, T0))
        print('Gamma for 1.0 price change: ', Gamma(S0, K0, r0, sigma0, T0))
        print('Vega for per 1% sigma change: ', Vega(S0, K0, r0, sigma0, T0) / 100)
        print('Theta for per year: ', Theta_Call(S0, K0, r0, sigma0, T0))
        print('Theta for per day: ', Theta_Call(S0, K0, r0, sigma0, T0) / 365)
        print('rho for per 100% rho change: ', Rho_Call(S0, K0, r0, sigma0, T0))
    print()
    print('================ put option ================')
    sigma0 = Implied_volatility_Put(S0, K0, r0, T0, Put_price0)
    print('implied_vol: ', sigma0)
    if not sigma0 is None:
        print('BS_price: ', BlackScholes_Put_pricing(S0, K0, r0, sigma0, T0))
        print('Delta for 1.0 price change: ', Delta_Put(S0, K0, r0, sigma0, T0))
        print('Gamma for 1.0 price change: ', Gamma(S0, K0, r0, sigma0, T0))
        print('Vega for per 1% sigma change: ', Vega(S0, K0, r0, sigma0, T0) / 100)
        print('Theta for per year: ', Theta_Put(S0, K0, r0, sigma0, T0))
        print('Theta for per day: ', Theta_Put(S0, K0, r0, sigma0, T0) / 365)
        print('rho for per 100% rho change: ', Rho_Put(S0, K0, r0, sigma0, T0))
    print()

if __name__ == '__main__':
    import datetime as DT
    S0 = 22135
    K0 = 25000
    r0 = 0.03
    T0 = (DT.date(2015,9,23) - DT.date(2015,9,11)).days / 365

    Call_price0 = 0
    Put_price0 = 1000

    functional_testing(S0, K0, r0, T0, Call_price0, Put_price0)