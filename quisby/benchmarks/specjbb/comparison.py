from itertools import groupby

import quisby.config as config
from quisby.sheet.sheet_util import (
    create_spreadsheet,
    append_to_sheet,
    read_sheet,
    get_sheet,
    create_sheet,
)
from quisby.util import combine_two_array_alternating
from quisby.benchmarks.specjbb.graph import graph_specjbb_data


def compare_specjbb_results(spreadsheets, spreadsheetId, test_name, table_name=[]):
    values = []
    results = []
    spreadsheet_name = []

    for spreadsheet in spreadsheets:
        values.append(read_sheet(spreadsheet, range=test_name))
        spreadsheet_name.append(get_sheet(spreadsheet, range=[])["properties"]["title"])

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(value, key=lambda x: x != []) if k)

    list_1 = list(values[0])
    list_2 = list(values[1])

    for value in list_1:
        results.append([""])
        for ele in list_2:

            if value[0][0] in table_name and ele[0][0] in table_name:
                if value[0][0] == ele[0][0]:
                    if value[1][0].split(".")[0] == ele[1][0].split(".")[0]:
                        results = combine_two_array_alternating(results, value, ele)
                        break

            elif value[0][0] == "Cost/Hr":
                results += value
                break

            elif value[0][0] == ele[0][0]:

                results.append(value[0])
                results = combine_two_array_alternating(results, value[1:], ele[1:])
                break

    create_sheet(spreadsheetId, test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_specjbb_data(spreadsheetId, test_name)


if __name__ == "__main__":
    spreadsheets = [
        "",
        "",
    ]
    test_name = "specjbb"

    compare_specjbb_results(spreadsheets, test_name, ["Peak", "Peak/$eff"])
