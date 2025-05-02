#!/usr/bin/env python3
import pickle
import FreeSimpleGUI as sg

variable_layout = [
    [
        sg.Text("Currently selected corrections are: "),
        sg.Text("", key="-CORRECTIONS-"),
    ],
    [
        sg.Button('CD45y 10^3', size=(12, 4)),
        sg.Button('CD45y 20^3', size=(12, 4)),
        sg.Button('CD45y 30^3', size=(12, 4))
    ],
    [
        sg.Button('CD34x 10^3', size=(12, 4)),
        sg.Button('CD34x 20^3', size=(12, 4)),
        sg.Button('CD34x 40^3', size=(12, 4)),
        sg.Button('CD34x 70^3', size=(12, 4)),
        sg.Button('CD34x 10^4', size=(12, 4))
    ],
    [
        sg.Button('CD34y 10^3', size=(12, 4)),
        sg.Button('CD34y 20^3', size=(12, 4)),
        sg.Button('CD34y failure', size=(12, 4)),
    ],
    [
        sg.Button('PBMC failure', size=(12, 4)),
    ],
    [
        sg.Text("Custom 1:", justification='right'),

        sg.In(size=(15, 1), enable_events=False, default_text=0, key="-CUSTOM1-"),

        sg.Text("Custom 2:", justification='right'),

        sg.In(size=(15, 1), enable_events=False, default_text=0, key="-CUSTOM2-"),

        sg.Text("Custom 3:", justification='right'),

        sg.In(size=(15, 1), enable_events=False, default_text=0, key="-CUSTOM3-"),
    ],
    [
        sg.Button('Custom 1', size=(16, 4), pad=(35, 0)),
        sg.Button('Custom 2', size=(16, 4), pad=(35, 0)),
        sg.Button('Custom 3', size=(16, 4), pad=(35, 0)),
    ],
]

if __name__ == "__main__":
    # Dictionary of elements emitting events (e.g. sg.Button or sg.In) and their names
    # Dictionary should be the <event> : <output text> as it would appear in the output file
    # special keyword "CUSTOM" means it's a sg.In field and the text value will be used
    # i.e. CUSTOM_Xlim_ where the user has entered 200 will result in Xlim_200
    # The first part before the underscore should be unique for the category of events,
    # Only one event per category can be selected at a time, i.e. if the user selects
    # two Xlim_ events, a popup will appear telling them to select only one
    # multiple CUSTOM_ events can be selected at the same time
    event_descriptor_dict = {"CD45y 10^3": "CD45y_10^3",
                             "CD45y 20^3": "CD45y_20^3",
                             "CD45y 30^3": "CD45y_30^3",
                             "CD34x 10^3": "CD34x_10^3",
                             "CD34x 20^3": "CD34x_20^3",
                             "CD34x 40^3": "CD34x_40^3",
                             "CD34x 70^3": "CD34x_70^3",
                             "CD34x 10^4": "CD34x_10^4",
                             "CD34y 10^3": "CD34y_10^3",
                             "CD34y 20^3": "CD34y_20^3",
                             "CD34y failure": "CD34y_failure",
                             "PBMC failure": "PBMC_failure",
                             "Custom 1": "CUSTOM_my_first_button",
                             "Custom 2": "CUSTOM_my_second_button",
                             "Custom 3": "CUSTOM_my_third_button"
                             }

    # Make into a dict
    # Caveat 'page_no' can be an integer or a tuple
    variable_layout_dict = {"gate_name": "cd45 & cd34", "number_of_images": 3, "page_indicies": (3, 4, 5), "variable_layout": variable_layout,
                            "event_descriptor_dict": event_descriptor_dict}

    # pickle the dict to file
    with open("../cd45_cd34_v6.pickle", "wb") as f:
        pickle.dump(variable_layout_dict, f)

    # clear the dict
    variable_layout_dict = {}

    # Read the dict from file and print it to test
    with open("../cd45_cd34_v6.pickle", "rb") as f:
        variable_layout_dict = pickle.load(f)
        # print
        print(variable_layout_dict)
