#!/usr/bin/env python3
import pickle
import PySimpleGUI as sg

variable_layout = [
    [
        sg.Text("Currently selected corrections are: "),
        sg.Text("", key="-CORRECTIONS-"),
    ],
    [

        sg.Button('SINGLET bad -> review', size=(12, 4)),
    ],
    [

        sg.Button('PBMC-FSC 70k', size=(12, 4)),
        sg.Button('PBMC-FSC 80k', size=(12, 4)),
        sg.Button('PBMC-FSC 90k', size=(12, 4)),
        sg.Button('PBMC-FSC 100k', size=(12, 4)),

    ],
    [

        sg.Button('PBMC too large', size=(12, 4)),
        sg.Button('PBMC bad monocyte cluster', size=(12, 4)),
        sg.Button('PBMC total failure', size=(12, 4)),
        sg.Button('PBMC other -> review', size=(12, 4)),
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
    event_descriptor_dict = {"SINGLET bad -> review": "SINGLET_bad_review",
                             "PBMC-FSC 70k": "PBMC-FSC_70k",
                             "PBMC-FSC 80k": "PBMC-FSC_80k",
                             "PBMC-FSC 90k": "PBMC-FSC_90k",
                             "PBMC-FSC 100k": "PBMC-FSC_100k",
                             "PBMC too large": "PBMC_remove_more_debris",
                             "PBMC bad monocyte cluster": "PBMC_remove_less_debris",
                             "PBMC total failure": "PBMC_total_failure",
                             "PBMC other -> review": "PBMC_other_review",
                             "Custom 1": "CUSTOM_my_first_button",
                             "Custom 2": "CUSTOM_my_second_button",
                             "Custom 3": "CUSTOM_my_third_button"
                             }

    # Make into a dict
    # Caveat 'page_no' can be a integer or a tuple
    variable_layout_dict = {"gate_name": "singlet & pbmc", "number_of_images": 3, "page_indicies": (0, 1, 2), "variable_layout": variable_layout,
                            "event_descriptor_dict": event_descriptor_dict}

    # pickle the dict to file
    with open("../singlet_pbmc_v4.pickle", "wb") as f:
        pickle.dump(variable_layout_dict, f)

    # clear the dict
    variable_layout_dict = {}

    # Read the dict from file and print it to test
    with open("../singlet_pbmc_v4.pickle", "rb") as f:
        variable_layout_dict = pickle.load(f)
        # print
        print(variable_layout_dict)
