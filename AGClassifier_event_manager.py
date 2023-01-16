#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import yaml
from glob import glob

from AGClassifier_utilities import create_invalid_select_window, create_invalid_custom_window, \
    create_no_sample_pdf, create_complete_window, get_page, check_if_discarded, check_if_in_index_files, \
    create_pdf_window, start_gating, add_to_output_yaml


def check_event_categories(event_list, event_descriptor_dict):
    """
    Check that only one event of each category is present
    Custom_ events are an exception to this rule
    Custom_ events can be selected multiple times
    :param event_list:
    :param event_descriptor_dict:
    :return:
    """
    event_categories = []
    for event in event_list:
        if "_" in event:
            event_category = event_descriptor_dict[event].split("_")[0]
            if event_category != "CUSTOM_":
                event_categories.append(event_category)
        else:
            event_categories.append(event)
    event_categories = set(event_categories)
    if len(event_categories) < len(event_list):
        create_invalid_select_window()
        return False
    else:
        return True


def limit_event_handler(event_list, output_folder, event_descriptor_dict):
    """
    Check if event exists in the button_descriptor_dict. If not, raise an error
    :param event_list: List of all "limit events" (i.e. events that are not context events) that were clicked.
    :param output_folder: The output folder where the output files will be saved. Defined by user on startup.
    :param event_descriptor_dict:
    :return:
    """
    descriptor_list = []
    for event in event_list:
        if event in event_descriptor_dict.keys():
            # If so, get the descriptor
            descriptor_list.append(event_descriptor_dict[event])

        else:
            raise_str = "Event " + str(event) + " not found in event_descriptor_dict and is not a custom event"
            raise ValueError(raise_str)
    add_to_output_yaml(output_folder, "test_name", descriptor_list, "test_value")

    return


def context_event_handler(event_list, input_folder, output_folder):
    """
    Handle static, contextual events
    These are events that are not defined in the event_descriptor_dict
    :param event_list:
    :param input_folder:
    :param output_folder:
    :return:
    TODO
    """
    for event in event_list:
        print(event)
    return


def next_sample():
    # TODO
    # Get the next sample
    # If there is no next sample, create a complete window and return False
    # If the next sample is discarded or already analysed, skip it and go to the next one
    # If the next sample is not discarded or analysed, display it and return True
    return True


def previous_sample():
    # TODO
    # Get the previous sample
    # If there is no previous sample, do nothing
    # If the previous sample is discarded, skip it and go to the previous one
    # Until a non-discarded sample is found or there are no more samples, in which case do nothing
    return True


def is_context_event(event):
    if event in ["START", "Done, next image", "Previous image", "Exit", "Open pdf", "Set this pop NA", "Discard"]:
        return True
    else:
        return False


def event_loop(window, input_folder, output_folder, event_descriptor_dict, page_no):
    #
    #
    #
    image_index = 0
    file_list = []
    file_list = glob(input_folder + "*.pdf") # initialise_parameters(event_descriptor_dict)

    # Initialise the event list with no elements
    event_list = []
    while True:
        event, values = window.read()
        # First check for context events (start, exit, previous, discard, set to na, open pdf)
        if is_context_event(event):
            # The open pdf event is a special case, it does not clear the event list
            if event == 'Open pdf':
                if create_pdf_window():  # Returns True if pdf exists and is opened, False otherwise
                    continue
            else:
                event_list = []
                if event in ["set to na", "discard"]:
                    # These events should trigger a next sample call
                    next_sample()
                elif event in ["previous"]:
                    previous_sample()
                else:
                    # Trigger start gating at sample X or from the beginning
                    start_gating(window_ref=window, image_index=image_index, file_list=file_list, page_no=page_no)  # TODO
                    continue

        if not context_event_handler(event, event_list):
            # If the event recieves
            if event == "DONE, next image":
                # First check that the event list is valid
                # This spawns an invalid selection window if not
                if check_event_categories(event_list, event_descriptor_dict):
                    # If so, run the event handler
                    limit_event_handler(event_list, output_folder, event_descriptor_dict)
                    # then clear the event list and go to the next sample
                    event_list = []
                    if not next_sample():
                        break
                else:
                    # Otherwise, clear the event list and keep going on the same sample
                    event_list = []
            else:
                event_list.append(event)
    return
