#!/usr/bin/env python3
from collections import OrderedDict
from itertools import dropwhile
import argparse
import os.path
import pandas as pd

parser = argparse.ArgumentParser(description="Converts ALE file from Alexa for Resolve to get more info.")
parser.add_argument("ale_file", metavar="ALE", type=argparse.FileType(mode="r"))
parser.add_argument("csv_file", metavar="CSV", nargs="?", default=None)

def main():
    args = parser.parse_args()

    columns, data = convert_ale_to_dict(args.ale_file)
    args.ale_file.close()

    df = pd.DataFrame(data, columns=columns)

    csv_path = args.csv_file or os.path.join(os.path.expanduser("~/Desktop/"), os.path.basename(args.ale_file.name.replace(".ale", ".csv")))

    fixed_df = df.rename(
        columns={
            "Source File": "File Name",
            "Duration": "Duration TC",
            "FPS": "Shot Frame Rate",
            "Sensor_fps": "Camera FPS",
            "Start": "Start TC",
            "End": "End TC",
            "Camera_index": "Camera #",
            "Reel_name": "Reel Name",
            "Shutter_angle": "Shutter Angle",
            "White_balance": "White Point (Kelvin)",
            "Cc_shift": "White Balance Tint",
            "Exposure_index": "ISO",
        }
    )

    fixed_df["Camera #"] = fixed_df["Camera #"].str.replace("_", "")
    source_file_path = os.path.dirname(os.path.realpath(args.ale_file.name))

    if "Clip Directory" not in fixed_df.columns:
        fixed_df["Clip Directory"] = ""

    for index, camera_file in enumerate(fixed_df["File Name"]):
        hde_file = camera_file.replace("_a", "_h")
        camera_path = os.path.join(source_file_path, camera_file)

        if os.path.exists(camera_path):
            print(f"The original file exists! No HDE modification needed for {camera_file}.")
            fixed_df.at[index, "Clip Directory"] = source_file_path
        elif os.path.exists(os.path.join(source_file_path, hde_file)):
            print(f"The HDE file exists! Modified filename to: {hde_file}.")
            fixed_df.at[index, "Clip Directory"] = source_file_path
            fixed_df.at[index, "File Name"] = hde_file
        else:
            print(f"Camera files not found. Leaving filename {camera_file} alone.")
            fixed_df.at[index, "Clip Directory"] = None

    slimed = fixed_df[
        ["File Name", "Clip Directory", "Start TC", "End TC", "Duration TC", "Shot Frame Rate", "Camera FPS", "Camera #",
         "Reel Name", "Shutter Angle", "White Point (Kelvin)", "White Balance Tint", "ISO"]
    ].copy()

    slimed.to_csv(csv_path, encoding="utf16", index=False)

def convert_ale_to_dict(file):
    with file as f:
        f_iter = iter(f)

        f_iter = dropwhile(lambda line: "Column" not in line.rstrip(), f_iter)
        column_line = next_or_none(f_iter)
        if column_line is None:
            raise Exception("No columns found")

        column_names_line = next_or_none(f_iter)
        if column_names_line is None:
            raise Exception("No values for columns")

        columns = column_names_line.replace("\n", "").split("\t")

        f_iter = dropwhile(lambda line: "Data" not in line.rstrip(), f_iter)
        data_line = next_or_none(f_iter)
        if data_line is None:
            raise Exception("No data found")

        data = []
        for data_values_line in f_iter:
            values = data_values_line.replace("\n", "").split("\t")
            values_dict = OrderedDict(zip(columns, values))
            data.append(values_dict)

    return columns, data

def next_or_none(iter):
    try:
        return next(iter)
    except StopIteration:
        return None

if __name__ == "__main__":
    main()
