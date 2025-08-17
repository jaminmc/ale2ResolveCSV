#!/usr/bin/env python3
from collections import OrderedDict
from itertools import dropwhile
import argparse
import os.path
import pandas as pd

parser = argparse.ArgumentParser(
    description="Converts ALE file from Alexa for Resolve to get more info."
)
parser.add_argument("ale_file", metavar="ALE", type=argparse.FileType(mode="r"))
parser.add_argument("csv_file", metavar="CSV", nargs="?", default=None)


def main():
    args = parser.parse_args()

    columns, data = convert_ale_to_dict(args.ale_file)
    
    # Use context manager to handle file closing properly
    with args.ale_file:
        df = pd.DataFrame(data, columns=columns)

    if args.csv_file is not None:
        csv_path = args.csv_file
    else:
        pre, ext = os.path.splitext(args.ale_file.name)
        csv_path = pre + ".csv"
        # Put resulting file on desktop instead of master folder if destination file isn't specified.
        csv_path = os.path.expanduser("~/Desktop/") + os.path.basename(csv_path)
    
    # This is where we remap headers
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
        },
        inplace=False,
    )
    
    # This removed the _ that the production used for different formatting of filename.
    fixed_df["Camera #"] = fixed_df["Camera #"].str.replace("_", "")
    realpath = os.path.realpath(args.ale_file.name)
    sourcefile = os.path.dirname(realpath)

    # This changes the filenames to match HDE if the file exists. Also adds path to CSV

    if "Clip Directory" not in fixed_df.columns:
        fixed_df["Clip Directory"] = ""
    
    # Vectorized approach for better performance
    for index in fixed_df.index:
        CameraFile = str(fixed_df["File Name"][index])
        HDE_file = CameraFile.replace("_a", "_h")
        
        if os.path.exists(os.path.join(sourcefile, CameraFile)):
            print(
                "The original file exists! No HDE modification needed for "
                + CameraFile
                + "."
            )
            fixed_df["Clip Directory"][index] = sourcefile
        elif os.path.exists(os.path.join(sourcefile, HDE_file)):
            print("The HDE file exists! Modified filename to: " + HDE_file + ".")
            fixed_df["Clip Directory"][index] = sourcefile
            fixed_df["File Name"][index] = HDE_file
        else:
            print("Camera files not found. leaving filename", CameraFile, "alone.")
            fixed_df["Clip Directory"][index] = None

    # print(fixed_df)
    slimed = fixed_df[
        [
            "File Name",
            "Clip Directory",
            "Start TC",
            "End TC",
            "Duration TC",
            "Shot Frame Rate",
            "Camera FPS",
            "Camera #",
            "Reel Name",
            "Shutter Angle",
            "White Point (Kelvin)",
            "White Balance Tint",
            "ISO",
        ]
    ].copy()
    
    # fixed_df.to_csv("/tmp/test.csv", encoding='utf16', index=False)
    slimed.to_csv(csv_path, encoding="utf16", index=False)


def convert_ale_to_dict(f):
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

    return (columns, data)
    # dw = csv.DictWriter(f, fieldnames=columns)

    # dw.writeheader()

    # dw.writerows(data)


def next_or_none(iter):
    try:
        return next(iter)
    except StopIteration:
        return None


if __name__ == "__main__":
    main()
