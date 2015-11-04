#coding=utf8
import copy
import pandas as PD

class TableHandler:
    def __init__(self):
        self.table = list()
        self.rows = 0
        self.columns = 0
        self.hori_headers = tuple()

    def getHoriHeader(self, index):
        try:
            return self.hori_headers[index]
        except:
            return None

    def getHeaderIndex(self, header):
        try:
            return self.hori_headers.index(header)
        except:
            return None

    #--------------------------------------------
    def clear(self):
        self.table = list()
        self.rows = 0
        self.columns = 0
        self.hori_headers = tuple()

    def clearContent(self):
        self.table = list()
        self.rows = 0

    def reset(self, rows, hori_headers, def_value=''):
        if len(hori_headers) < 1:
            return
        self.rows = rows
        self.columns = len(hori_headers)
        self.hori_headers = tuple(hori_headers)
        self.table = list()
        for r in range(0, self.rows):
            self.table.append([def_value]*self.columns)
        return

    def copy(self, rv):
        if not type(rv) == TableHandler:
            return False
        self.table = copy.deepcopy(rv.table)
        self.rows = rv.rows
        self.columns = rv.columns
        self.hori_headers = copy.deepcopy(rv.hori_headers)
        return True

    #located by header
    def copyContent(self, rv):
        if not type(rv) == TableHandler:
            return False
        self.clearContent()
        self.addRows(rv.rows)
        for r in range(0, rv.rows):
            for idx in range(0, rv.columns):
                h = rv.getHoriHeader(idx)
                if not h in self.hori_headers:
                    continue
                self.setByHeader(r, h, rv.get(r, idx))
        return True

    def copyDataframe(self, df):
        self.table = list()
        self.rows = df.shape[0]
        self.columns = df.shape[1]
        self.hori_headers = tuple(df.columns)
        for pr in df.iterrows():
            self.table.append(list(pr[1]))
        return

    def addRows(self, n=1):
        for i in range(0,n):
            self.table.append(['']*self.columns)
        self.rows += n

    #notice the row_index hold by outsider will overdue
    def delRows(self, row_list):
        row_list.sort(reverse=True)
        for r in row_list:
            if r < self.rows:
                self.rows -= 1
                del self.table[r]
        return

    #---------------------------------------------------
    def get(self, row, col):
        try:
            return self.table[row][col]
        except:
            return None

    def getByHeader(self, row, header):
        try:
            c = self.hori_headers.index(header)
            return self.table[row][c]
        except:
            return None

    def set(self, row, col, value):
        try:
            self.table[row][col] = value
            return True
        except:
            return False

    def setByHeader(self, row, header, value):
        try:
            c = self.hori_headers.index(header)
            self.table[row][c] = value
            return True
        except:
            return False

    def setAll(self, value):
        for r in range(0, self.rows):
            for c in range(0, self.columns):
                self.table[r][c] = value

    #---------------------------------------------
    def toDataFrame(self):
        data_cpy = copy.deepcopy(self.table)
        for r in range(0, self.rows):
            for c in range(0, self.columns):
                try:
                    num = float(data_cpy[r][c])
                    if num % 1 == 0:
                        num = int(num)
                    data_cpy[r][c] = num
                except:
                    pass
        return PD.DataFrame(data_cpy, columns=self.hori_headers)


#############################################################

class DataframeHandler:
    def __init__(self, df=None):
        self.df = df

    def attachToExistedDataframe(self, df):
        self.df = df
        return

    #def createAndAttachDataframe(self, headers):
    #    self.dataf = PD.DataFrame(columns=headers)

    def good(self):
        return not self.df is None

    def getDataFrame(self):
        return self.df

    #----------------------------------------------
    def rows(self):
        return self.df.shape[0]

    def columns(self):
        return self.df.shape[1]

    #return (rows, columns)
    def shape(self):
        return self.df.shape

    #return (header1, header2, ...)
    def headers(self):
        return tuple(self.df.columns)

    #return row_indexs (index1, index2, ...)
    def indexs(self):
        return tuple(self.df.index)

    #get columns index_num
    def getHeaderIndex(self, header):
        return self.df.columns.get_loc(header)

    #get cell content, starts from 0
    def get(self, irow, icol):
        return self.df.iat[irow, icol]

    def getByHeader(self, irow, header):
        return self.df[header].iat[irow]

    def getByIndexAndHeader(self, row_index, header, index_name=None, inner_loc=0):
        if index_name is None:
            return self.df[header][row_index]
        else:
            sli = self.df.xs(row_index, level=index_name)
            return sli[header].iat[inner_loc]

    #----------------------------------------------------------
    #set single cell
    def set(self, irow, icol, new_value):
        try:
            self.df.iloc[irow, icol] = new_value
        except:
            pass
        return

    #set single cell locate by header
    def setByHeader(self, irow, header, new_value):
        try:
            self.df[header].iat[irow] = new_value
        except Exception as err:
            pass
        return

#####################################################################
if __name__ == '__main__':
    th = TableHandler()
    d = PD.DataFrame([[1,1,1,1],[2,2,2,2],[3,3,3,3]])
    print(d)
    th.copyDataframe(d)
    for r in th.table:
        print(r)
