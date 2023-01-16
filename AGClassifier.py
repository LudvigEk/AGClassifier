#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Any

import PySimpleGUI as sg

from AGClassifier_layouts import layout_selector

from AGClassifier_event_manager import event_loop


def select_folders():
    """
    Initial popups to select input and output folders
    :return: input_folder, output_folder
    """
    input_folder = sg.popup_get_folder("Select input folder")
    output_folder = sg.popup_get_folder("Select output folder")

    return input_folder, output_folder


def main():
    """
    Main function
    :return:
    """

    # First select input and output folders
    input_folder, output_folder = select_folders()

    # Then select layout
    layout, event_descriptor_dict, page_no = layout_selector()

    # Create the window
    window = sg.Window(title="AliGater image classifier", layout=layout)

    # Run the event loop
    event_loop(window, input_folder, output_folder, event_descriptor_dict, page_no)

    window.close()

    return


if __name__ == "__main__":
    main()
