""" ETL Auxiliary Functions """
import os


def get_file_info(file_name):
    """
    Parse file_name and returns (type, [year, month, day])

    Args:
        file_name (str): Name of the file
    """
    file_type = file_name.split(".")[0][:-9]
    file_date = file_name.split(".")[0][-8:]
    date_y = file_date[:4]
    date_m = file_date[4:6]
    date_d = file_date[6:8]

    return file_type, [date_y, date_m, date_d]


def generate_filtered_files(raw_files):
    """
    Return a set of all filtered files that should exist in the S3 bucket
    of filtered files, based on the raw_files.

    Args:
        raw_files (list): List with all the files in the raw data bucket
    """
    with open("./cloud/lambda_functions/Crawler-Master/IBX50.txt") as f:
        stock_list = f.readlines()
    stock_list = list(map(str.strip, stock_list))

    filtred_files = []
    for file in raw_files:
        for stock in stock_list:
            ftype, date = get_file_info(file)
            filtred_files.append(
                f"{date[0]}/{date[1]}/{date[2]}/{ftype}_{stock}.parquet"
            )
    return set(filtred_files)


def raw_unfiltered_files(unfiltered_files):
    """
    Return a set of raw_files that weren't filtered correctly.

    Args:
        unfiltered_files (list): List with all the unfiltered files
    """
    raw_unfiltred = []
    for file in unfiltered_files:
        file_date = "".join(file.split("/")[:3])
        file_type = "_".join(file.split("/")[3].split("_")[:2])
        raw_unfiltred.append(f"{file_type}_{file_date}.gz")
    return set(raw_unfiltred)
