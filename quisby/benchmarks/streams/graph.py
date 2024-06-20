import time
from itertools import groupby

from quisby.sheet.sheetapi import sheet
from quisby.sheet.sheet_util import (
    clear_sheet_charts,
    append_to_sheet,
    read_sheet,
    get_sheet, append_empty_row_sheet
)


def create_series_range_list_stream_compare(column_index, len_of_func, sheetId, start_index, end_index):
    series = []
    len_of_func = column_index + len_of_func
    while(column_index < len_of_func):
        series.append(
        {
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": column_index,
                            "endColumnIndex": column_index+1,
                        }
                    ]
                }
            },
            "targetAxis": "LEFT_AXIS",
            "type": "COLUMN",
        },)
        column_index = column_index + 1

    series.append({
        "series": {
            "sourceRange": {
                "sources": [
                    {
                        "sheetId": sheetId,
                        "startRowIndex": start_index,
                        "endRowIndex": end_index,
                        "startColumnIndex": column_index,
                        "endColumnIndex": column_index+1,
                    }
                ]
            }
        },
        "targetAxis": "RIGHT_AXIS",
        "type": "LINE",
    },)
    column_index = column_index+1

    return series, column_index


def create_series_range_list_stream_process(column_index, len_of_func, sheetId, start_index, end_index):
    series = []

    for index in range(len_of_func):

        series.append(
            {
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": sheetId,
                                "startRowIndex": start_index,
                                "endRowIndex": end_index,
                                "startColumnIndex": column_index,
                                "endColumnIndex": column_index + 1,
                            }
                        ]
                    }
                },
                "type": "COLUMN",
            }
        )
        column_index += 1

    return series, column_index


def graph_streams_data(spreadsheetId, test_name, action):
    """
    Retreive each streams results and graph them up indvidually

    :sheet: sheet API function
    :spreadsheetId
    :test_name: test_name to graph up the data, it will be mostly sheet name
    """

    GRAPH_COL_INDEX = 1
    GRAPH_ROW_INDEX = 0
    start_index = 0
    end_index = 0
    data = read_sheet(spreadsheetId, "streams")
    if len(data) > 500:
        append_empty_row_sheet(spreadsheetId, 3000, test_name)
    if len(data) > 1000:
        append_empty_row_sheet(spreadsheetId, 1000, test_name)
    for index, row in enumerate(data):
        if "Max Throughput" in row:
            start_index = index

        if start_index:
            if row == []:
                end_index = index
            if index + 1 == len(data):
                end_index = index + 1

        if end_index:
            graph_data = data[start_index:end_index]
            column_count = len(graph_data[0])

            for _, items in groupby(graph_data[0][1:], key=lambda x: x.split("-")[0]):
                len_of_func = len(list(items))
                break
            column = 1

            for _ in range(column_count):
                if column >= column_count:
                    break

                sheetId = get_sheet(spreadsheetId, test_name)["sheets"][0][
                    "properties"
                ]["sheetId"]

                series, column = globals()[f'create_series_range_list_stream_{action}'](column, len_of_func, sheetId, start_index, end_index)

                requests = {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": "%s: %s" % (test_name, graph_data[0][0]),
                                "basicChart": {
                                    "chartType": "COMBO",
                                    "legendPosition": "BOTTOM_LEGEND",
                                    "axis": [
                                        {"position": "BOTTOM_AXIS", "title": ""},
                                        {
                                            "position": "LEFT_AXIS",
                                            "title": "Throughput (MB/s)",
                                        },
                                        {
                                            "position": "RIGHT_AXIS",
                                            "title": "%Diff",
                                        },
                                    ],
                                    "domains": [
                                        {
                                            "domain": {
                                                "sourceRange": {
                                                    "sources": [
                                                        {
                                                            "sheetId": sheetId,
                                                            "startRowIndex": start_index,
                                                            "endRowIndex": end_index,
                                                            "startColumnIndex": 0,
                                                            "endColumnIndex": 1,
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ],
                                    "series": series,
                                    "headerCount": 1,
                                },
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": sheetId,
                                        "rowIndex": GRAPH_ROW_INDEX,
                                        "columnIndex": column_count + GRAPH_COL_INDEX,
                                    }
                                }
                            },
                        }
                    }
                }

                if GRAPH_COL_INDEX >= 5:
                    GRAPH_ROW_INDEX += 20
                    GRAPH_COL_INDEX = 1
                else:
                    GRAPH_COL_INDEX += 6

                body = {"requests": requests}

                sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

                time.sleep(3)

            # Reset variables
            start_index, end_index = 0, 0
