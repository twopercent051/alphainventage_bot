from datetime import datetime
from typing import Optional

from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Font
import os


class ExcelFile:
    def __init__(self):
        self.tickers_path = f"{os.getcwd()}/tickers_list.xlsx"
        self.result_path = f"{os.getcwd()}/result_list.xlsx"

    @staticmethod
    def __reformat_date(date: Optional[datetime]) -> str:
        result = date.strftime("%d-%m-%Y %H:%M") if date else "---"
        return result

    def create_tickers_file(self, tickers: list):
        wb = Workbook()
        ws = wb.active
        ws.append(
            (
                "Тикер",
            )
        )
        title_ft = Font(bold=True)
        for row in ws['A1:T1']:
            for cell in row:
                cell.font = title_ft
        for ticker in tickers:
            ws.append(
                (
                    ticker
                )
            )
        wb.save(self.tickers_path)

    def read_tickers_file(self) -> Optional[list]:
        wb = load_workbook(filename=self.tickers_path)
        ws = wb.active
        data = []
        for row in ws.iter_rows(min_row=2):
            try:
                if not row[0].value:
                    continue
                data.append(row[0].value)
            except (ValueError, Exception):
                return None
        return data
