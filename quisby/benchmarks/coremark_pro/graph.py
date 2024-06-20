


from quisby.sheet.sheet_util import read_sheet,clear_sheet_charts,get_sheet,append_empty_row_sheet
from quisby.sheet.sheetapi import sheet
import time


def create_series_range_list_coremark_pro_process(column_count, sheetId, start_index, end_index):
    series = []

    for index in range(column_count):

        series.append(
            {
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": sheetId,
                                "startRowIndex": start_index,
                                "endRowIndex": end_index,
                                "startColumnIndex": index + 1,
                                "endColumnIndex": index + 2,
                            }
                        ]
                    }
                },
                "type": "COLUMN",
            }
        )

    return series


def create_series_range_list_coremark_pro_compare(column_count, sheetId, start_index, end_index):
    series = [
        {
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2,
                        }
                    ]
                }
            },
            "targetAxis": "LEFT_AXIS",
            "type": "COLUMN",
        },
        {
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        }
                    ]
                }
            },
            "targetAxis": "LEFT_AXIS",
            "type": "COLUMN",
        },
        {
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": 3,
                            "endColumnIndex": 4,
                        }
                    ]
                }
            },
            "targetAxis": "RIGHT_AXIS",
            "type": "LINE",
        },
    ]
    return series


def graph_coremark_pro_data(spreadsheetId, range, action):
    GRAPH_COL_INDEX = 1
    GRAPH_ROW_INDEX = 1
    start_index = 0
    end_index = 0

    data = read_sheet(spreadsheetId, range)
    if len(data) > 500:
        append_empty_row_sheet(spreadsheetId, 3000, "coremark_pro")

    header = []
    for index, row in enumerate(data):
        if "System name" in row:
            start_index = index
            iteration = data[index - 1][0]
            header.extend(row)
        if start_index:
            if not row:
                end_index = index
            if index + 1 == len(data):
                end_index = index + 1

        if end_index:

            graph_data = data[start_index:end_index]
            column_count = len(graph_data[0])

            sheetId = get_sheet(spreadsheetId, range)["sheets"][0]["properties"][
                "sheetId"
            ]

            requests = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "%s : %s : %s" % (range, "score", iteration),
                            "basicChart": {
                                "chartType": "COMBO",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {"position": "BOTTOM_AXIS", "title": ""},
                                    {
                                        "position": "LEFT_AXIS",
                                        "title": "Score",
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
                                "series": globals()[f'create_series_range_list_coremark_pro_{action}'](column_count,
                                                                                                       sheetId,
                                                                                                       start_index,
                                                                                                       end_index),
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
                GRAPH_ROW_INDEX = end_index

            body = {"requests": requests}

            sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

            # Reset variables
            start_index, end_index = 0, 0

            time.sleep(3)