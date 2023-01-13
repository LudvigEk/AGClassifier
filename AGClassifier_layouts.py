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

# *******************************************************

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


# ***********************************************************

def layout_compositor(variable_layout, image_viewer_layout):
    # Compose the layout from the variable parts
    # and the fixed parts
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


def layoutSelector():
    # Todo
    # GUI interface to select the layout
    # With an image preview of the various layouts ?
    # The variable parts of the layouts are stored as pickle files

    # Select pickle file
    layout_pickle_file = sg.popup_get_file("Select layout pickle file",
                                           file_types=(("Pickled layout files", "*.pickle"),))

    # Read the pickle file
    with open(layout_pickle_file, 'rb') as f:

        variable_layout_dict = pickle.load(f)

        variable_layout = variable_layout_dict["variable_layout"]
        number_of_images = variable_layout_dict["number_of_images"]

        if number_of_images == 1:
            image_viewer_layout = iv_column_1_image
        elif number_of_images == 2:
            image_viewer_layout = iv_column_2_images
        else:
            raise ValueError('Corrupted layout, number of images in the image viewer columns must be 1 or 2')

    layout = layout_compositor(variable_layout, image_viewer_layout)

    return layout
