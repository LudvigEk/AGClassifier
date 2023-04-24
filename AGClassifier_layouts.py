#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import pickle
import sys
import os

# **************** Image viewer layouts ****************

iv_column_1_image = [

    [sg.Text("Image Viewer"), sg.Text(size=(120, 1), key="-WARNING-")],

    [sg.Text(size=(80, 1), key="-TOUT-"), sg.Text(size=(40, 1), key="-COUNT-")],

    [sg.Text("Sample ID exists in these indicies:")],

    [sg.Text(size=(120, 1), key="-INDEX-")],

    [sg.Image(key="-IMAGE-", size=(320, 280))],

]

iv_column_2_images = [

    [sg.Text("Image Viewer"), sg.Text(size=(120, 1), key="-WARNING-")],

    [sg.Text(size=(80, 1), key="-TOUT-"), sg.Text(size=(40, 1), key="-COUNT-")],

    [sg.Text("Sample ID exists in these indicies:")],

    [sg.Text(size=(120, 1), key="-INDEX-")],

    [sg.Image(key="-IMAGE-", size=(160, 140))],

    [sg.Image(key="-IMAGE2-", size=(160, 140))],

]

iv_column_3_images = [

    [sg.Text("Image Viewer"), sg.Text(size=(120, 1), key="-WARNING-")],

    [sg.Text(size=(80, 1), key="-TOUT-"), sg.Text(size=(40, 1), key="-COUNT-")],

    [sg.Text("Sample ID exists in these indicies:")],

    [sg.Text(size=(120, 1), key="-INDEX-")],

    [sg.Image(key="-IMAGE-", size=(160, 140))],

    [sg.Image(key="-IMAGE2-", size=(160, 140)), sg.Image(key="-IMAGE3-", size=(160, 140))],

]
# *****************  ***********************

# ***************** extra buttons ***********************
extra_buttons_column = [

    [
        sg.Button('Open pdf', pad=(0, 35), size=(16, 4)),
    ],
    [
        sg.Button("SAMPLE IS BAD", key='DISCARD', pad=(0, 35), size=(16, 4)),
    ],
    [
        sg.Button('Cannot answer / NA', key='NA', pad=(0, 35), size=(16, 4)),
    ],
]

# Static top part of the layout
top_layout = [
    [
        sg.Button('START', pad=(0, 25), size=(60, 4)), sg.Text("Sample No:"),
        sg.In(size=(5, 1), enable_events=True, key="-SAMPLENO-", pad=(0, 5))
    ]
]

# Static bottom part of the layout
bottom_layout = [
    [
        sg.Button('DONE, next image', size=(60, 4)),
    ],
    [
        sg.Button('Previous image', size=(60, 4)),
    ],
    [
        sg.Checkbox("Bind arrow keys to navigation", key="-BINDARROWS-", default=False, enable_events=True),
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


def layout_selector(images_dir=None):
    """
    GUI interface to select the layout. (With an image preview of the various layouts ?)
    The variable parts of the layouts are stored as pickle files, which are added to the fixed parts of the layout by
    the compositor. If a images_dir is given, the function will try to find a pickle file in the parent directory.
    Otherwise, the user will need to select the pickle file manually.
    :param images_dir: The directory where the images are. The expectation is that the pickle file is in the parent dir.
    If a single .pickle file is found in the parent dir, it is automatically selected. If there are none, or more than
    one, the user will need select the pickle file (from any directory).
    :return: layout, event_descriptor_dict, page_no, gate_name
    """
    # Check if there is a pickle file in the parent directory
    if images_dir is not None:
        potential_pickle_dir = os.path.dirname(images_dir)  # parent directory
        picke_files = [file for file in os.listdir(potential_pickle_dir) if file.endswith(".pickle")]
        if len(picke_files) == 1:  # If there is a single pickle in parent dir, choose that one
            sg.popup(f"Automatically detected pickle file: '{picke_files[0]}'.\nIf that is the right file, you don't"
                     f" need to select a pickle file manually. Press OK to continue :)",
                     title="Found pickle file!")
            layout_pickle_file = os.path.join(potential_pickle_dir, picke_files[0])
        else:
            # Select pickle file
            layout_pickle_file = sg.popup_get_file(message="Please select the layout 'pickle' file:",
                                                   title="Select layout pickle file",
                                                   default_path=potential_pickle_dir,
                                                   file_types=(("Pickled layout files", "*.pickle"),))
    else:
        # Select pickle file when no path is given
        layout_pickle_file = sg.popup_get_file(message="Please select the layout 'pickle' file:",
                                               title="Select layout pickle file",
                                               file_types=(("Pickled layout files", "*.pickle"),))
    #while layout_pickle_file is None or layout_pickle_file == "":
    #    sg.popup("Please select a valid layout pickle file")
    #    layout_pickle_file = sg.popup_get_file("Select layout pickle file",
    #                                           file_types=(("Pickled layout files", "*.pickle"),))
    # Read the pickle file
    with open(layout_pickle_file, 'rb') as f:

        variable_layout_dict = pickle.load(f)

        variable_layout = variable_layout_dict["variable_layout"]

        composite_variable_layout = top_layout + variable_layout + bottom_layout

        number_of_images = variable_layout_dict["number_of_images"]
        event_descriptor_dict = variable_layout_dict["event_descriptor_dict"]

        # page_no can be a tuple or a integer depending on 1 or 2+ number_of_images
        page_no = variable_layout_dict["page_indicies"]

        gate_name = variable_layout_dict["gate_name"]

        if number_of_images == 1:
            sys.stderr.write("1 image layout selected\n")
            image_viewer_layout = iv_column_1_image
        elif number_of_images == 2:
            sys.stderr.write("2 image layout selected\n")
            image_viewer_layout = iv_column_2_images
        elif number_of_images == 3:
            sys.stderr.write("3 image layout selected\n")
            image_viewer_layout = iv_column_3_images
        else:
            raise ValueError('Corrupted layout, number of images in the image viewer columns must be 1, 2 or 3')

    layout = layout_compositor(composite_variable_layout, image_viewer_layout)

    return layout, event_descriptor_dict, page_no, gate_name
