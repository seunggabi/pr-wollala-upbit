import csv
import io

import pandas as pd
from PySide6 import QtWidgets, QtCore, QtGui


class OrderHistoryTableView(QtWidgets.QTableView):
    sumFinished = QtCore.Signal(pd.DataFrame, float)
    meanFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)
    bidMinusAskFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)
    askMinusBidFinished = QtCore.Signal(pd.DataFrame, pd.DataFrame, float)

    def __init__(self, parent=None):
        super(OrderHistoryTableView, self).__init__(parent=parent)
        self.sum_action = QtGui.QAction('합', parent=self)
        self.sum_action.setStatusTip('선택 된 Cell 값들을 더합니다.')
        self.sum_action.triggered.connect(self.sum)

        self.mean_action = QtGui.QAction('평균단가', parent=self)
        self.mean_action.setStatusTip('평균단가를 구합니다.')
        self.mean_action.triggered.connect(self.mean)

        self.bid_minus_ask_action = QtGui.QAction('매수 - 매도', parent=self)
        self.bid_minus_ask_action.setStatusTip('선택 된 Cell 값들 중 매수영역의 값과 매도영역의 값의 차를 구합니다.')
        self.bid_minus_ask_action.triggered.connect(self.bid_minus_ask)

        self.ask_minus_bid_action = QtGui.QAction('매도 - 매수', parent=self)
        self.ask_minus_bid_action.setStatusTip('선택 된 Cell 값들 중 매도영역의 값과 매수영역의 값의 차를 구합니다.')
        self.ask_minus_bid_action.triggered.connect(self.ask_minus_bid)

        self.copy_action = QtGui.QAction("복사", parent=self)
        self.copy_action.setStatusTip('선택 된 Cell의 내용을 클립보드에 복사합니다.')
        self.copy_action.triggered.connect(self.copySelection)

        self.menu = QtWidgets.QMenu(parent=self)

    # Ctrl+C 처리
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelection()

    # csv 형태로 클립보드에 복사
    @QtCore.Slot()
    def copySelection(self):
        selection = self.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()

            # 숫자 뒤의 KRW, BTC 문자 삭제
            for i, _v in enumerate(table):
                for j, _p in enumerate(table[i]):
                    table[i][j] = table[i][j].replace(',', '')
                    table[i][j] = table[i][j].replace(' KRW', '')
                    table[i][j] = table[i][j].replace(' BTC', '')
                    table[i][j] = table[i][j].replace(' %', '')
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            copy_str = stream.getvalue().replace(' KRW', '')
            copy_str = copy_str.replace(' BTC', '')
            QtWidgets.QApplication.clipboard().setText(copy_str)

    def contextMenuEvent(self, event):
        self.menu.clear()
        self.menu.addAction(self.copy_action)

        selected_haeder_set = set(
            map(lambda i: i.model().headerData(i.column(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole),
                self.selectedIndexes()))

        # 같은 Column 선택 & 선택 cell 1개 이상
        if len(selected_haeder_set) == 1 and len(self.selectedIndexes()) > 1:
            if "거래수량" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
                self.menu.addAction(self.bid_minus_ask_action)
            if "거래단가" in selected_haeder_set:
                self.menu.addAction(self.mean_action)
            if "거래금액" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
                self.menu.addAction(self.ask_minus_bid_action)
            if "수수료" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
            if "정산금액" in selected_haeder_set:
                self.menu.addAction(self.sum_action)
                self.menu.addAction(self.ask_minus_bid_action)

        if len(self.menu.actions()) > 0:
            self.menu.popup(QtGui.QCursor.pos())

    @QtCore.Slot()
    def sum(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]

        sum_df = df.reindex(selected_row_list)[header_text]
        result = sum_df.sum()
        self.sumFinished.emit(sum_df, result)

    @QtCore.Slot()
    def mean(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        trading_volume_df = df["거래수량"]
        trading_volume_df = trading_volume_df.reindex(selected_row_list)
        trading_price_df = df.reindex(selected_row_list)[header_text]

        result = (trading_volume_df * trading_price_df).sum() / trading_volume_df.sum()
        self.meanFinished.emit(trading_volume_df, trading_price_df, result)

    @QtCore.Slot()
    def bid_minus_ask(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        buy_df = df[df["종류"] == "매수"]
        ask_df = df[df["종류"] == "매도"]
        buy_df = buy_df.reindex(selected_row_list)[header_text]
        ask_df = ask_df.reindex(selected_row_list)[header_text]

        result = buy_df.sum() - ask_df.sum()
        self.bidMinusAskFinished.emit(buy_df, ask_df, result)

    @QtCore.Slot()
    def ask_minus_bid(self):
        df = self.model().df
        selected_col = [i.column() for i in self.selectedIndexes()][0]
        selected_row_list = [i.row() for i in self.selectedIndexes()]
        header_text = df.columns[selected_col]
        buy_df = df[df["종류"] == "매수"]
        ask_df = df[df["종류"] == "매도"]
        buy_df = buy_df.reindex(selected_row_list)[header_text]
        ask_df = ask_df.reindex(selected_row_list)[header_text]

        result = ask_df.sum() - buy_df.sum()
        self.bidMinusAskFinished.emit(ask_df, buy_df, result)
