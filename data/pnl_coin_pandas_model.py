import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor


class PnlCoinPandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.df = dataframe.round(9)
        self.df = self.df.reset_index(drop=True)
        self.plus_profit_row = self.df.index[(self.df['수익률'] >= 0)].tolist()
        self.minus_profit_row = self.df.index[(self.df['수익률'] < 0)].tolist()

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel
        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel
        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self.df.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel
        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None
        elif role == Qt.BackgroundRole:
            red = QColor(238, 64, 53, 200)
            blue = QColor(3, 146, 207, 200)
            gray = QColor(116, 109, 105, 70)
            if index.row() in self.plus_profit_row:
                return QBrush(red)
            elif index.row() in self.minus_profit_row:
                return QBrush(blue)
            else:
                return QBrush(gray)
        elif role == Qt.TextAlignmentRole:
            target_data = self.df.iloc[index.row(), index.column()]
            if isinstance(target_data, float):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            else:
                return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            target_data = self.df.iloc[index.row(), index.column()]
            if index.column() == 1:  # 총 매수 수량
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 1] % 1 == 0:
                    return f'{target_data:,.0f}'
                else:
                    return f'{target_data:,.8f}'
            elif index.column() == 2:  # 총 매도 수량
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 2] % 1 == 0:
                    return f'{target_data:,.0f}'
                else:
                    return f'{target_data:,.8f}'
            elif index.column() == 3:  # 미실현수량
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 3] % 1 == 0:
                    return f'{target_data:,.0f}'
                else:
                    return f'{target_data:,.8f}'
            elif index.column() == 4:  # 총 매수금액
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 0].startswith("KRW"):
                    return f'{target_data:,.0f} KRW'
                elif self.df.iloc[index.row(), 0].startswith("BTC"):
                    return f'{target_data:,.8f} BTC'
            elif index.column() == 5:  # 총 매도금액
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 0].startswith("KRW"):
                    return f'{target_data:,.0f} KRW'
                elif self.df.iloc[index.row(), 0].startswith("BTC"):
                    return f'{target_data:,.8f} BTC'
            elif index.column() == 6:  # 매수 평단가
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 0].startswith("KRW"):
                    return f'{target_data:,.0f} KRW'
                elif self.df.iloc[index.row(), 0].startswith("BTC"):
                    return f'{target_data:,.8f} BTC'
            elif index.column() == 7:  # 매도 평단가
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 0].startswith("KRW"):
                    return f'{target_data:,.0f} KRW'
                elif self.df.iloc[index.row(), 0].startswith("BTC"):
                    return f'{target_data:,.8f} BTC'
            elif index.column() == 8:  # 실현손익
                if pd.isnull(target_data):
                    return ""
                elif self.df.iloc[index.row(), 0].startswith("KRW"):
                    return f'{target_data:,.0f} KRW'
                elif self.df.iloc[index.row(), 0].startswith("BTC"):
                    return f'{target_data:,.8f} BTC'
            elif index.column() == 9:  # 수익률
                if pd.isnull(target_data):
                    return ""
                else:
                    return f'{target_data:,.2f} %'
            else:
                return str(target_data)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        """Override method from QAbstractTableModel
        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

        return None
