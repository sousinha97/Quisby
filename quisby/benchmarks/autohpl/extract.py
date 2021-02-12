import csv

from quisby.pricing import cloud_pricing
import quisby.config as config
from quisby.benchmarks.linpack.extract import linpack_format_data


def extract_autohpl_result(path):
    system_name = path.split("/")[4]

    with open(path) as file:
        results = []
        file_data = file.readlines()

        if len(file_data) > 1:
            header_row = file_data[0].split()
            data_row = file_data[1].split()

            data_dict = {}
            for key, value in zip(header_row, data_row):
                data_dict[key] = value

            results = linpack_format_data(
                results=results, system_name=system_name, gflops=data_dict["Gflops"]
            )

            if results:
                return results

        else:
            return None