#coding=utf8
import pandas as PD
from utility.data_handler import DataframeHandler

IDX = PD.IndexSlice
EMPTY_DATAFRAME = PD.DataFrame()
#################################################
OPTION_DF_HEADERS = ('group', 'code', 'type', 'strike', 'expiry', 'left_days',
                     'lots', 'dir', 'open_price', 'delta', 'gamma', 'vega',
                     'theta', 'implied_vol', 'intrnic', 'time_value', 'last_price',
                     'float_profit', 'margin', 'income', 'open_date')

STOCK_DF_HEADERS = ('group', 'code', 'lots', 'dir', 'open_price',
                    'last_price', 'float_profit', 'margin', 'open_date')

PORTFOLIO_DF_HEADERS = ('group', 'ptf_profit', 'ptf_delta', 'ptf_gamma', 'ptf_vega',
                        'ptf_theta', 'ptf_margin', 'ptf_income', 'ptf_principal')

##################################################
def loadPositionCsv(csvfile=r'./positions.csv'):
    try:
        df = PD.read_csv(csvfile, parse_dates=True, skip_blank_lines=True)
        df['code'] = df['code'].astype(str)
    except Exception as err:
        return None, err
    else:
        return df, None

###################################################
class PortfolioPositions:
    def __init__(self):
        self.option_multiplier = 10000
        self.stock_multiplier = 100
        #pd.dataframe
        self.option_df = None
        self.stock_df = None
        self.portfolio_df = None

    def initialize(self, option_df, stock_df):
        self.__setOptionPosition(option_df)
        self.__setStockPosition(stock_df)
        self.__initPortfolioData()
        return

    def __setOptionPosition(self, df):
        self.option_df = PD.DataFrame(columns=OPTION_DF_HEADERS)
        for header in df.columns:
            if header in OPTION_DF_HEADERS:
                self.option_df[header] = df[header].copy()
        #fill income
        self.option_df['income'] = (self.option_df['lots'] * self.option_df['dir']
                                    * self.option_df['open_price'] * self.option_multiplier
                                    * -1)
        #set multi index
        self.option_df = self.option_df.set_index([self.option_df['group'], self.option_df.index], drop=False)
        self.option_df.index.names = ['group_id', 'rows']
        return

    def __setStockPosition(self, df):
        self.stock_df = PD.DataFrame(columns=STOCK_DF_HEADERS)
        for header in df.columns:
            if header in STOCK_DF_HEADERS:
                self.stock_df[header] = df[header].copy()
        #fill margin
        self.stock_df['margin'] = (self.stock_df['lots'] * self.stock_df['dir']
                                   * self.stock_df['open_price'] * self.stock_multiplier)
        #set multi index
        self.stock_df = self.stock_df.set_index([self.stock_df['group'], self.stock_df.index], drop=False)
        self.stock_df.index.names = ['group_id', 'rows']
        return

    def __initPortfolioData(self):
        groups_id = set()
        if not self.option_df.empty:
            groups_id.update(self.option_df.index.get_level_values('group_id'))
        if not self.stock_df.empty:
            groups_id.update(self.stock_df.index.get_level_values('group_id'))
        groups_id = list(groups_id)
        groups_id.sort()
        #set dataframe
        self.portfolio_df = PD.DataFrame(index=groups_id,
                                         columns=PORTFOLIO_DF_HEADERS)
        self.portfolio_df['group'] = groups_id
        return

    def updateData(self):
        relative_multi = self.stock_multiplier / self.option_multiplier
        option_groups = list()
        stock_groups = list()
        if not self.option_df.empty:
            option_groups = self.option_df.index.get_level_values('group_id')
        if not self.stock_df.empty:
            stock_groups = self.stock_df.index.get_level_values('group_id')
        for i in self.portfolio_df.index:
            #options
            if i in option_groups:
                opt_pos = self.option_df.xs(i, level='group_id')
                self.portfolio_df.loc[i, 'ptf_profit'] = opt_pos['float_profit'].sum()
                self.portfolio_df.loc[i, 'ptf_delta'] = (opt_pos['delta'] * opt_pos['lots'] * opt_pos['dir']).sum()
                self.portfolio_df.loc[i, 'ptf_gamma'] = (opt_pos['gamma'] * opt_pos['lots'] * opt_pos['dir']).sum()
                self.portfolio_df.loc[i, 'ptf_vega'] = (opt_pos['vega'] * opt_pos['lots'] * opt_pos['dir']).sum()
                self.portfolio_df.loc[i, 'ptf_theta'] = (opt_pos['theta'] * opt_pos['lots'] * opt_pos['dir']).sum()
                self.portfolio_df.loc[i, 'ptf_margin'] = opt_pos['margin'].sum()
                self.portfolio_df.loc[i, 'ptf_income'] = opt_pos['income'].sum()
            #stocks
            if i in stock_groups:
                stk_pos = self.stock_df.xs(i, level='group_id')
                self.portfolio_df.loc[i, 'ptf_profit'] += stk_pos['float_profit'].sum()
                self.portfolio_df.loc[i, 'ptf_delta'] += (stk_pos['lots'] * stk_pos['dir']).sum() * relative_multi
                self.portfolio_df.loc[i, 'ptf_margin'] += stk_pos['margin'].sum()
        #principal
        self.portfolio_df['ptf_principal'] = (self.portfolio_df['ptf_margin'] -
                                              self.portfolio_df['ptf_income'])
        return

##################################################################
class PositionDataHandler(DataframeHandler):
    def __init__(self, df=None):
        super(PositionDataHandler, self).__init__(df)

    def getPositionDataByGroupId(self, group_id_ls):
        try:
            return self.df.loc[IDX[group_id_ls,:], :]
        except:
            return EMPTY_DATAFRAME

    def getPositionDataByRowIdx(self, row_idx_ls):
        try:
            return self.df.loc[IDX[:, row_idx_ls], :]
        except:
            return EMPTY_DATAFRAME

class DataProxy:
    def __init__(self):
        super(DataProxy, self).__init__()
        self.positions = PortfolioPositions()
        self.option_handler = None
        self.stock_handler = None
        self.portfolio_handler = None

    def initialize(self, option_df, stock_df):
        if option_df is None:
            option_df = PD.DataFrame(columns=OPTION_DF_HEADERS)
        if stock_df is None:
            stock_df = PD.DataFrame(columns=STOCK_DF_HEADERS)
        self.positions.initialize(option_df, stock_df)
        self.option_handler = PositionDataHandler(self.positions.option_df)
        self.stock_handler = PositionDataHandler(self.positions.stock_df)
        self.portfolio_handler = DataframeHandler(self.positions.portfolio_df)

    def updateData(self):
        self.positions.updateData()

    def getOptionData(self):
        return self.option_handler

    def getStockData(self):
        return self.stock_handler

    def getPortfolioData(self):
        return self.portfolio_handler

