import datetime
import os
import re
import numpy as np
import openpyxl
import pandas as pd


def process_bus_excel_data(base_dir: str) -> pd.DataFrame:
    """
    指定されたディレクトリ内のバス乗降実績Excelを一括で読み込み、
    縦持ちデータフレームに整形。
    """
    file_names = os.listdir(base_dir)
    df_list = []

    for file_name in file_names:
        file_path = os.path.join(base_dir, file_name)

        if not (os.path.isfile(file_path) and file_path.endswith(".xlsx")):
            continue

        year = int(re.search(r"(\d{4})年", file_name).group(1))
        month = int(re.search(r"(\d{1,2})月", file_name).group(1))

        wb = openpyxl.load_workbook(file_path)
        sheet_names = [
            sheet_name
            for sheet_name in wb.sheetnames
            if re.match(r"\d{1,2}日", sheet_name)
        ]

        for sheet_name in sheet_names:
            day = int(re.search(r"(\d{1,2})日", sheet_name).group(1))
            date = datetime.datetime(year, month, day)
            ws = wb[sheet_name]

            data_matrix = np.array(list(ws.values))
            row_start = np.where(data_matrix[:, 0] == "停留所名")[0][0] + 1
            row_end = np.where(data_matrix[:, 0] == "合計")[0][0] - 1
            column_start = 1
            columns_end = np.where(data_matrix[2, :] == "合計")[0][0] - 1

            for j in range(column_start, columns_end + 1, 2):
                direction = data_matrix[1, j]
                departure_time = data_matrix[2, j]
                ride = data_matrix[row_start : row_end + 1, j]
                get_off = data_matrix[row_start : row_end + 1, j + 1]

                df_tmp = pd.DataFrame(
                    {
                        "date": date,
                        "direction": direction,
                        "departure_time": departure_time,
                        "ride": ride,
                        "get_off": get_off,
                    }
                )

                if direction == "停留所A出発":
                    df_tmp["stop_sequence"] = range(1, len(df_tmp) + 1)
                else:
                    df_tmp["stop_sequence"] = range(len(df_tmp), 0, -1)

                df_list.append(df_tmp)

    if not df_list:
        raise ValueError("処理対象となるデータが存在しません。")

    return pd.concat(df_list, axis=0)


def main():
    input_dir = "./sample-data/"
    output_dir = "./output/"
    output_filepath = os.path.join(output_dir, "整形済みバス実績データ.csv")

    df_transformed = process_bus_excel_data(input_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df_transformed.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    main()