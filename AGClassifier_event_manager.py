#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from glob import glob

from AGClassifier_utilities import create_invalid_select_window, create_pdf_window, update_image, add_to_output_yaml, \
    collect_name_of_pdf_at_index, check_if_discarded, create_complete_window


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


def limit_event_handler(event_list, output_folder, event_descriptor_dict, gate_name, sample_name):
    """
    Check if event exists in the button_descriptor_dict. If not, raise an error
    :param event_list: List of all "limit events" (i.e. events that are not context events) that were clicked.
    :param output_folder: The output folder where the output files will be saved. Defined by user on startup.
    :param event_descriptor_dict:
    :param gate_name:
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
    add_to_output_yaml(output_folder, gate_name, descriptor_list, sample_name)

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


def start_analysis(window_ref, image_index=0, file_list=[], page_no=0):
    """
    Start the analysis from the defined image index. Default is 0.
    If the specified sample is discarded or already analysed, skip it and go to the next one.
    If the specified sample is NOT discarded or analysed, display it and return the index.
    :param window_ref:
    :param image_index:
    :param file_list:
    :param page_no:
    :return:
    """
    # TODO

    if not isinstance(file_list, list) or not file_list:
        raise ValueError("No file list provided")
    if check_if_discarded(image_index, file_list):  # If the first sample is discarded, go to the next one
        image_index = next_sample(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no)
    image_index = update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no)

    return image_index


def next_sample(window_ref, image_index: int, file_list: list, page_no: int):
    """
    Go to the next sample. If the next sample is discarded, skip it and go to the next one instead. If the index is out
    of bounds, it means we have reached the last sample and we are done.
    :param window_ref:
    :param image_index:
    :param file_list:
    :param page_no:
    :return: int if a valid sample is found, False if there are no more samples
    """

    image_index = image_index + 1

    # Validate image_index, if invalid, try next image until valid or end of list
    while check_if_discarded(image_index, file_list):  # Skip discarded samples
        image_index += 1

    # Check if new_index is out of scope. If so return False to finish
    if image_index >= len(file_list):
        create_complete_window()  # All samples have been analysed
        return False
    image_index = update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no)

    return image_index


def previous_sample(window_ref, image_index, file_list, page_no):
    # TODO
    # Get the previous sample
    # If there is no previous sample, do nothing
    # If the previous sample is discarded, skip it and go to the previous one
    # Until a non-discarded sample is found or there are no more samples, in which case do nothing
    image_index = update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no,
                               b_forward_on_invalid=False)

    return image_index


def is_context_event(event) -> bool:
    """
    Check if the event is a context event
    :param event: PySimpleGUI event
    :return: True if the event is a context event, False otherwise
    """
    if event in ["START", "DONE, next image", "Previous image", "Exit", "WIN_CLOSED",
                 "Open pdf", "Set this pop NA", "Discard", "-SAMPLENO-"]:
        return True
    else:
        return False


def event_loop(window, input_folder, output_folder, event_descriptor_dict, page_no, gate_name) -> None:
    """
    The event loop. This is the main function of the program.
    TODO handle image_index events
    TODO "-SAMPLENO-" events do not work properly if an incorrect index is entered by the user

    :param window:
    :param input_folder:
    :param output_folder:
    :param event_descriptor_dict:
    :param page_no:
    :param gate_name:
    :return: None
    """
    image_index = 0
    file_list = glob(input_folder + "/*.pdf")  # initialise_parameters(event_descriptor_dict)
    if len(file_list) == 0 or file_list is None:
        raise ValueError("No pdf files found in input folder")

    # Initialise the event list with no elements
    event_list = []
    while True:
        event, values = window.read()
        print("Image index: ", image_index)
        sample_name = collect_name_of_pdf_at_index(file_list, image_index)
        print(f"E: {event}, V: {values}")
        print(f"Current sample name is {sample_name}")
        # First check for context events (start, exit, previous, discard, set to na, open pdf)
        if is_context_event(event):
            # The open pdf event is a special case, it does not clear the event list
            if event == 'Open pdf':
                if create_pdf_window():  # Returns True if pdf exists and is opened, False otherwise
                    continue
            elif event == "-SAMPLENO-":
                # if the input sampleno is a integer and in-bounds of the file list, update the image_index
                # save old image index first, then try to convert the input to an integer
                # if its also valid, replace image_index with this new value, otherwise use the old value
                old_image_index = image_index
                try:
                    image_index = int(values["-SAMPLENO-"])
                    # None, negative values, out of bounds values are all invalid. Use old value instead.
                    if image_index is None or image_index < 0 or image_index >= len(file_list):
                        raise ValueError
                except ValueError:
                    image_index = old_image_index
                else:
                    values["-SAMPLENO-"] = image_index
            elif event == "Exit" or event == "WIN_CLOSED":
                break
            else:
                if event in ["Set this pop NA", "DISCARD"]:
                    # TODO: include a popup that makes sure the user wants to discard the sample
                    event_list = []
                    # These events should trigger a next sample call
                    # next_sample(window_ref, image_index, file_list, page_no)
                    image_index = next_sample(window_ref=window, image_index=image_index,
                                              file_list=file_list, page_no=page_no)
                    if image_index is False:  # Win condition achieved
                        break
                elif event in ["previous"]:
                    event_list = []
                    image_index = previous_sample(window_ref=window, image_index=image_index,
                                                  file_list=file_list, page_no=page_no)
                elif event == "START":
                    event_list = []
                    # Trigger update_image at sample X or from the beginning
                    image_index = start_analysis(window_ref=window, image_index=image_index,
                                                 file_list=file_list, page_no=page_no)
                elif event == "DONE, next image":
                    # First check that the event list is valid
                    # This spawns an invalid selection window if not
                    if check_event_categories(event_list, event_descriptor_dict):
                        # If so, run the event handler
                        limit_event_handler(event_list, output_folder, event_descriptor_dict, gate_name, sample_name)
                        # then clear the event list and go to the next sample
                        event_list = []
                        image_index = next_sample(window_ref=window, image_index=image_index,
                                                  file_list=file_list, page_no=page_no)
                    else:
                        # Otherwise, clear the event list and keep going on the same sample
                        event_list = []
        else:
            # If the event is not a context event, add it to the event list
            event_list.append(event)

    return
