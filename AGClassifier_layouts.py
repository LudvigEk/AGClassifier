#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import pickle

# **************** Image viewer layouts ****************

iv_column_1_image = [

    [sg.Text("Image Viewer")],

    [sg.Text(size=(80, 1), key="-TOUT-"), sg.Text(size=(40, 1), key="-COUNT-")],

    [sg.Text("Sample ID exists in these indicies:")],

    [sg.Text(size=(120, 1), key="-INDEX-")],

    [sg.Image(key="-IMAGE-", size=(320, 280))],

]

iv_column_2_images = [

    [sg.Text("Image Viewer")],

    [sg.Text(size=(80, 1), key="-TOUT-"), sg.Text(size=(40, 1), key="-COUNT-")],

    [sg.Text("Sample ID exists in these indicies:")],

    [sg.Text(size=(120, 1), key="-INDEX-")],

    [sg.Image(key="-IMAGE-", size=(160, 140)), sg.Image(key="-IMAGE2-", size=(160, 140))],

]

# *****************  ***********************

# ***************** extra buttons ***********************
extra_buttons_column = [

    [
        sg.Button('Open pdf', pad=(0, 35), size=(16, 4)),
    ],
    [
        sg.Button('DISCARD', pad=(0, 35), size=(16, 4)),
    ],
    [
        sg.Button('Set this pop NA', pad=(0, 35), size=(16, 4)),
    ],
]

# Static top part of the layout
top_layout = [
    [
        sg.Text("Page number of population:"),

        sg.In(size=(25, 1), enable_events=True, key="-POPULATION-", pad=(0, 5)),
        sg.Text("Sample No:"),
        sg.In(size=(5, 1), enable_events=True, key="-SAMPLENO-", pad=(0, 5))
    ],
    [
        sg.Text("OUTPUT INDEX FILE PREFIX:"),

        sg.In(size=(25, 1), enable_events=True, key="-PREFIX-"),
    ],
    [
        sg.Button('START', pad=(0, 25), size=(60, 4)),
    ]
]

# Static bottom part of the layout
bottom_layout = [
    [
        sg.Button('DONE, next image', size=(60, 4)),
    ],
    [
        sg.Button('Previous image', size=(60, 4)),
    ]
]


# ***********************************************************

def layout_compositor(variable_layout, image_viewer_layout):
    """
    Compose the layout from the variable part and the fixed parts
    :param variable_layout:
    :param image_viewer_layout:
    :return:
    """
    layout = [

        [

            sg.Column(variable_layout),

            sg.VSeperator(),

            sg.Column(image_viewer_layout),

            sg.VSeperator(),

            sg.Column(extra_buttons_column),

        ]

    ]
    return layout


def layout_selector():
    """
    GUI interface to select the layout. With an image preview of the various layouts ?
    The variable parts of the layouts are stored as pickle files
    :return:
    """

    # Select pickle file
    layout_pickle_file = sg.popup_get_file("Select layout pickle file",
                                           file_types=(("Pickled layout files", "*.pickle"),))

    # Read the pickle file
    with open(layout_pickle_file, 'rb') as f:

        variable_layout_dict = pickle.load(f)

        variable_layout = variable_layout_dict["variable_layout"]

        composite_variable_layout = top_layout + variable_layout + bottom_layout

        number_of_images = variable_layout_dict["number_of_images"]
        event_descriptor_dict = variable_layout_dict["event_descriptor_dict"]

        if number_of_images == 1:
            image_viewer_layout = iv_column_1_image
        elif number_of_images == 2:
            image_viewer_layout = iv_column_2_images
        else:
            raise ValueError('Corrupted layout, number of images in the image viewer columns must be 1 or 2')

    layout = layout_compositor(composite_variable_layout, image_viewer_layout)

    return layout, event_descriptor_dict
