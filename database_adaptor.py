#coding=utf8
import os
import pandas as PD
import datetime as DT

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
    CROSS_DF_HEADERS = ('group', 'pot_profit', 'pot_delta', 'pot_gamma', 'pot_vega',
                        'pot_margin', 'pot_income', 'pot_principal')

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
            self.cross_df['pot_profit'].loc[i] = group_sli['float_profit'].sum()
            self.cross_df['pot_delta'].loc[i] = (group_sli['delta'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['pot_gamma'].loc[i] = (group_sli['gamma'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['pot_vega'].loc[i] = (group_sli['vega'] * group_sli['lots'] * group_sli['dir']).sum()
            self.cross_df['pot_margin'].loc[i] = group_sli['margin'].sum()
            self.cross_df['pot_income'].loc[i] = group_sli['income'].sum()
            self.cross_df['pot_principal'].loc[i] = self.cross_df['pot_margin'].loc[i] - \
                                                    self.cross_df['pot_income'].loc[i]
        return

class MatrixHandler:
    def __init__(self):
        self.attached_df = None

    def attachDataframe(self, df):
        self.attached_df = df
        return

    def good(self):
        return not self.attached_df is None

    def getDataFrame(self):
        return self.attached_df

    #return (rows, columns)
    def shape(self):
        return self.attached_df.shape

    #return (header1, header2, ...)
    def headers(self):
        return tuple(self.attached_df.columns)

    #return row_indexs (index1, index2, ...)
    def indexs(self):
        return tuple(self.attached_df.index)

    #get columns index_num
    def getHeaderIndex(self, header):
        return self.attached_df.columns.get_loc(header)

    #get cell content, starts from 0
    def get(self, irow, icol):
        return self.attached_df.iat[irow, icol]

    def getByHeader(self, irow, header):
        return self.attached_df[header].iat[irow]

    def getByIndexAndHeader(self, row_index, header, index_name=None, inner_loc=0):
        if index_name is None:
            return self.attached_df[header][row_index]
        else:
            sli = self.attached_df.xs(row_index, level=index_name)
            return sli[header].iat[inner_loc]

    #set single cell
    def set(self, irow, icol, new_value):
        try:
            self.attached_df.iloc[irow, icol] = new_value
        except:
            return False
        else:
            return True

    #set single cell locate by header
    def setByHeader(self, irow, header, new_value):
        try:
            self.attached_df[header].iat[irow] = new_value
        except Exception as err:
            return False
        else:
            return True

##################################################################

class DataProxy(TradeGroupData):
    def __init__(self):
        super(DataProxy, self).__init__()
        self.pos = MatrixHandler()
        self.pot = MatrixHandler()
        self.ori_pos = MatrixHandler()

    def initialize(self, ori_position_df=None):
        super(DataProxy, self).initialize(ori_position_df)
        self.ori_pos.attachDataframe(self.ori_csv_df)
        self.pos.attachDataframe(self.pos_df)
        self.pot.attachDataframe(self.cross_df)

    def updateData(self):
        super(DataProxy, self).updateData()

    def getOriginPosHandler(self):
        pass

    def getPositionDataHandler(self):
        return self.pos

    def getPositionDataByGroupId(self, group_id_ls):
        df = self.pos.getDataFrame()
        return df.loc[IDX[group_id_ls,:], :].copy()

    def getPositionDataByRowIdx(self, row_idx_ls):
        df = self.pos.getDataFrame()
        return df.loc[IDX[:, row_idx_ls], :].copy()

    def getPortfolioDataHandler(self):
        return self.pot