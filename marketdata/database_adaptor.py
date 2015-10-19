#coding=utf8

from utility.data_handler import *

IDX = PD.IndexSlice

def loadPositionCsv(csvfile=r'./positions.csv'):
    try:
        df = PD.read_csv(csvfile, parse_dates=True, skip_blank_lines=True)
        df['code'] = df['code'].astype(str)
    except Exception as err:
        return None, err
    else:
        return df, None

class PositionData:
    PROSITION_DF_HEADERS = ('group', 'code', 'type', 'strike', 'expiry', 'left_days',
                            'lots', 'dir', 'open_price', 'delta', 'gamma', 'vega',
                            'theta', 'implied_vol', 'intrnic', 'time_value', 'last_price',
                            'float_profit', 'margin', 'income')

    def __init__(self):
        self.pos_df = None
        self.ori_csv_df = None

    def initialize(self, ori_pos_df=None):
        if ori_pos_df is None:
            ori_pos_df, err = loadPositionCsv()
        self.ori_csv_df = ori_pos_df
        self.createPositionDf()
        return

    def createPositionDf(self):
        self.pos_df = PD.DataFrame(columns=PositionData.PROSITION_DF_HEADERS)
        for header in self.pos_df.columns:
            if header in self.ori_csv_df.columns:
                self.pos_df[header] = self.ori_csv_df[header].copy()
        self.pos_df['income'] = self.pos_df['lots'] * self.pos_df['dir'] \
                                * self.pos_df['open_price'] * 10000 * -1
        return

class TradeGroupData(PositionData):
    CROSS_DF_HEADERS = ('group', 'ptf_profit', 'ptf_delta', 'ptf_gamma', 'ptf_vega',
                        'ptf_margin', 'ptf_income', 'ptf_principal')

    def __init__(self):
        super(TradeGroupData, self).__init__()
        self.cross_df = None

    def initialize(self, ori_pos_df=None):
        super(TradeGroupData, self).initialize(ori_pos_df)
        self.pos_df = self.pos_df.set_index([self.pos_df['group'], self.pos_df.index], drop=False)
        self.pos_df.index.names = ['group_id', 'index']
        #generate cross table indexed by group
        group_indexs = set(self.pos_df.index.get_level_values('group_id'))
        self.cross_df = PD.DataFrame(index=group_indexs, columns=TradeGroupData.CROSS_DF_HEADERS)

    def updateData(self):
        for i in self.cross_df.index:
            group_sli = self.pos_df.xs(i, level='group_id')
            self.cross_df['group'].loc[i] = i
            self.cross_df['ptf_profit'].loc[i] = group_sli['float_profit'].sum()
            self.cross_df['ptf_delta'].loc[i] = (group_sli['delta'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['ptf_gamma'].loc[i] = (group_sli['gamma'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['ptf_vega'].loc[i] = (group_sli['vega'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['ptf_margin'].loc[i] = group_sli['margin'].sum()
            self.cross_df['ptf_income'].loc[i] = group_sli['income'].sum()
            self.cross_df['ptf_principal'].loc[i] = self.cross_df['ptf_margin'].loc[i] - \
                                                    self.cross_df['ptf_income'].loc[i]
        return

##################################################################

class DataProxy(TradeGroupData):
    def __init__(self):
        super(DataProxy, self).__init__()
        self.pos = DataframeHandler()
        self.ptf = DataframeHandler()
        self.ori_pos = DataframeHandler()

    def initialize(self, ori_position_df=None):
        super(DataProxy, self).initialize(ori_position_df)
        self.ori_pos.attachToExistedDataframe(self.ori_csv_df)
        self.pos.attachToExistedDataframe(self.pos_df)
        self.ptf.attachToExistedDataframe(self.cross_df)

    def updateData(self):
        super(DataProxy, self).updateData()

    def getOriginPosHandler(self):
        return self.ori_pos

    def getPositionDataHandler(self):
        return self.pos

    def getPositionDataByGroupId(self, group_id_ls):
        df = self.pos.getDataFrame()
        return df.loc[IDX[group_id_ls,:], :].copy()

    def getPositionDataByRowIdx(self, row_idx_ls):
        df = self.pos.getDataFrame()
        return df.loc[IDX[:, row_idx_ls], :].copy()

    def getPortfolioDataHandler(self):
        return self.ptf