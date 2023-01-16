#!/usr/bin/env python3
import pickle
import PySimpleGUI as sg

variable_layout = [
    [

        sg.Button('Xlim 200', size=(8, 4)),
        sg.Button('Xlim 300', size=(8, 4)),
        sg.Button('Xlim 400', size=(8, 4)),
        sg.Button('Xlim 700', size=(8, 4)),

    ],
    [

        sg.Button('Ylim 100', size=(8, 4)),
        sg.Button('Ylim 150', size=(8, 4)),
        sg.Button('Ylim 200', size=(8, 4)),
        sg.Button('Ylim 300', size=(8, 4)),
    ],
    [
        sg.Text("Custom 1:", justification='right'),

        sg.In(size=(15, 1), enable_events=True, default_text=0, key="-CUSTOM1-"),

        sg.Text("Custom 2:", justification='right'),

        sg.In(size=(15, 1), enable_events=True, default_text=0, key="-CUSTOM2-"),

        sg.Text("Custom 3:", justification='right'),

        sg.In(size=(15, 1), enable_events=True, default_text=0, key="-CUSTOM3-"),
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
    event_descriptor_dict = {"Ylim 100": "Ylim_100",
                             "Ylim 150": "Ylim_150",
                             "Ylim 200": "Ylim_200",
                             "Ylim 300": "Ylim_300",
                             "Xlim 200": "Xlim_200",
                             "Xlim 300": "Xlim_300",
                             "Xlim 400": "Xlim_400",
                             "Xlim 700": "Xlim_700",
                             "Custom 1": "CUSTOM_",
                             "Custom 2": "CUSTOM_",
                             "Custom 3": "CUSTOM_"
                             }

    # Make into a dict
    # Caveat 'page_no' can be a integer or a tuple
    variable_layout_dict = {"number_of_images": 2, "page_indicies": (3, 4), "variable_layout": variable_layout,
                            "event_descriptor_dict": event_descriptor_dict}

    # pickle the dict to file
    with open("../variable_layout_dict.pickle", "wb") as f:
        pickle.dump(variable_layout_dict, f)

    # clear the dict
    variable_layout_dict = {}

    # Read the dict from file and print it to test
    with open("../variable_layout_dict.pickle", "rb") as f:
        variable_layout_dict = pickle.load(f)
        # print
        print(variable_layout_dict)
