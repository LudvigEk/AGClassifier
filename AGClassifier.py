#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from AGClassifier_layouts import layout_selector

from AGClassifier_event_manager import event_loop
from AGClassifier_utilities import set_correction_yaml_global

import os


def select_folders():
    """
    Initial popups to select input and output folders
    :return: input_folder, output_folder
    """
    # TODO error/invalid handling
    input_folder = sg.popup_get_folder(message="Hello! Welcome to the AliGater Classifier.\nPlease select the folder "
                                               "where the images are:",
                                       title="Select input folder")
    while input_folder is None or input_folder == "":
        # if no folder is selected, make a popup requesting the user to select a folder
        sg.popup("Invalid folder. Please select a valid input folder")
        input_folder = sg.popup_get_folder("Select input folder")
    #output_folder = sg.popup_get_folder("Select the folder where the output should be saved:",
    #                                    title="Select output folder")
    #while output_folder is None or output_folder == "":
    #    sg.popup("Please select a valid output folder")
    #    output_folder = sg.popup_get_folder("Select output folder")

    # Check if an output folder already exists in the input folder
    output_folder = os.path.join(input_folder, "output")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    # The file that will store all the output
    correction_yaml_file = os.path.join(output_folder, "correction.yaml")
    set_correction_yaml_global(correction_yaml_file)

    if not os.path.exists(correction_yaml_file):
        open(correction_yaml_file, "w").close()

    return input_folder, correction_yaml_file


def main():
    """
    Main function
    :return:
    """

    # First select input and output folders
    input_folder, yaml_file = select_folders()

    # Then select layout
    layout, event_descriptor_dict, page_no, gate_name = layout_selector(input_folder)

    # Create the window
    window = sg.Window(title="AliGater image classifier", layout=layout, resizable=True, finalize=True)

    # Bind arrows to next/previous image
    window.bind("<Right>", "DONE, next image")
    window.bind("<Left>", "Previous image")

    # Run the event loop
    event_loop(window, input_folder, event_descriptor_dict, page_no, gate_name)

    window.close()

    return


if __name__ == "__main__":
    main()
