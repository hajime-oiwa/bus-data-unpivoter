import datetime
import pandas as pd
import numpy as np
import os
import openpyxl
import re

base_dir = "./sample-data/"
file_names = os.listdir(base_dir) 

df_list = []
for file_name in file_names:
    file_path = os.path.join(base_dir, file_name)

    if os.path.isfile(file_path) and file_path.endswith(".xlsx"):
        year = int(re.search(r"(\d{4})年", file_name).group(1))
        month = int(re.search(r"(\d{1,2})月", file_name).group(1))

        wb = openpyxl.load_workbook(file_path)
        sheet_names = [sheet_name for sheet_name in wb.sheetnames if re.match(r"\d{1,2}日", sheet_name)]

        for sheet_name in sheet_names:
            day = int(re.search(r"(\d{1,2})日", sheet_name).group(1))
            date = datetime.datetime(year, month, day)
            ws = wb[sheet_name]

            data_matrix = np.array(list(ws.values))
            row_start = np.where(data_matrix[:, 0] == "停留所名")[0][0] + 1
            row_end = np.where(data_matrix[:, 0] == "合計")[0][0] - 1
            column_start = 1
            columns_end = np.where(data_matrix[2, :] == "合計")[0][0] - 1

            stop_names = data_matrix[row_start:row_end + 1, 0]
            for j in range(column_start, columns_end + 1, 2):
                direction = data_matrix[1, j]
                departure_time = data_matrix[2, j]
                ride = data_matrix[row_start:row_end + 1, j]
                get_off = data_matrix[row_start:row_end + 1, j+1]
                df_tmp = pd.DataFrame(
                    {
                        "date": date,
                        "direction": direction,
                        "departure_time": departure_time,
                        "ride": ride,
                        "get_off": get_off
                    }
                )
                if direction == "停留所A出発":
                    df_tmp["stop_sequence"] = range(1, len(df_tmp) + 1)
                else:
                    df_tmp["stop_sequence"] = range(len(df_tmp), 0, -1)
                df_list.append(df_tmp)
    else:
        continue

df = pd.concat(df_list, axis=0)

if not os.path.exists("./output/"):
    os.mkdir("./output/")
df.to_csv("./output/整形済みバス実績データ.csv", index=None)

