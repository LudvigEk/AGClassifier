#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from glob import glob
import PySimpleGUI as sg

from AGClassifier_utilities import create_invalid_select_window, create_pdf_window, update_image, add_to_output_yaml, \
    collect_name_of_pdf_at_index, check_if_discarded, create_complete_window, check_if_in_yaml, remove_from_yaml, \
    create_discard_are_you_sure_popup, create_yaml_string



def check_event_categories(event_list, event_descriptor_dict) -> bool:
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


def limit_event_handler(event_list: list, event_descriptor_dict: dict, gate_name: str,
                        sample_name: str) -> None:
    """
    Deal with the so called 'limit events'. Update the output yaml file with by adding the name of the current sample
    under the selected descriptors.
    Check if event exists in the button_descriptor_dict. If not, raise an error.

    :param event_list: List of all "limit events" (i.e. events that are not context events) that were clicked.
    :param event_descriptor_dict: Maps the event/button names to the descriptors. Taken from the .pickle file.
    :param gate_name: Name of the gate. Taken from the .pickle file.
    :param sample_name: Name of the current sample. Taken from the PDF file name.
    :return: None
    """

    descriptor_list = []
    for event in event_list:
        if event in event_descriptor_dict.keys():
            # If so, get the descriptor
            descriptor_list.append(event_descriptor_dict[event])
        else:
            raise_str = "Event " + str(event) + " not found in event_descriptor_dict and is not a custom event"
            raise ValueError(raise_str)
    add_to_output_yaml(gate_name, descriptor_list, sample_name)

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

    if not isinstance(file_list, list) or not file_list:
        raise ValueError("No file list provided")
    if check_if_discarded(image_index, file_list=file_list):  # If the first sample is discarded, go to the next one
        image_index = next_sample(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no)

    yaml_update_string = create_yaml_string(image_index=image_index, file_list=file_list)
    update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no, sample_in_yaml_string=yaml_update_string)

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
    while check_if_discarded(image_index, file_list=file_list):  # Skip discarded samples
        image_index += 1

    # Check if new_index is out of scope. If so return False to finish
    if image_index >= len(file_list):
        create_complete_window()  # All samples have been analysed
        sys.exit(0)

    yaml_update_string = create_yaml_string(image_index=image_index, file_list=file_list)
    update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no, sample_in_yaml_string=yaml_update_string)

    return image_index


def previous_sample(window_ref, image_index, file_list, page_no):
    # Get the previous sample
    # If there is no previous sample, do nothing
    # If the previous sample is discarded, skip it and go to the previous one
    # Until a non-discarded sample is found or there are no more samples, in which case do nothing

    if image_index == 0:
        sg.popup("This is the first sample")
        return image_index
    else:
        image_index = image_index - 1

    while check_if_discarded(image_index, file_list=file_list):  # Skip discarded samples
        image_index -= 1
        if image_index == 0:
            break

    yaml_update_string = create_yaml_string(image_index=image_index, file_list=file_list)
    update_image(window_ref=window_ref, image_index=image_index, file_list=file_list, page_no=page_no, sample_in_yaml_string=yaml_update_string)

    return image_index


def is_context_event(event) -> bool:
    """
    Check if the event is a context event.

    :param event: PySimpleGUI event
    :return: True if the event is a context event, False otherwise
    """

    if event in ["START", "DONE, next image", "Previous image", "Exit", "WIN_CLOSED",
                 "Open pdf", "Set this pop NA", "DISCARD", "-SAMPLENO-"]:
        return True
    else:
        return False


def event_loop(window, input_folder, event_descriptor_dict, page_no, gate_name) -> None:
    """
    The event loop. This is the main function of the program.
    TODO handle image_index events
    TODO "-SAMPLENO-" events do not work properly if an incorrect index is entered by the user

    :param window: PySimpleGUI window
    :param input_folder: The input folder where the PDF files are located. Defined by user on startup.
    :param event_descriptor_dict: Maps the event/button names to the descriptors. Taken from the .pickle file.
    :param page_no: The page number of the PDF file that will be displayed.
    :param gate_name: Name of the gate being QC'd. Taken from the .pickle file.
    :param yaml_file: The output yaml file where the results will be stored.
    :return: None
    """

    image_index = 0
    file_list = glob(input_folder + "/*.pdf")  # initialise_parameters(event_descriptor_dict)
    if len(file_list) == 0 or file_list is None:
        raise ValueError("No pdf files found in input folder")

    # Initialise the event list with no elements
    event_list = []
    bOk = True
    while bOk:
        sample_name = collect_name_of_pdf_at_index(file_list, image_index)
        sample_in_yaml = check_if_in_yaml(sample_name, gate_name)  # Flag used to 'correct' if new limits
        if sample_in_yaml:
            # TODO; Popup too annoying?
            sg.popup(f"Sample {sample_name} has already been analysed for this gate!")
        event, values = window.read()
        # First check for context events (start, exit, previous, discard, set to na, open pdf)
        if is_context_event(event):
            # The open pdf event is a special case, it does not clear the event list
            if event == 'Open pdf':
                if create_pdf_window(file_list[image_index], 0):  # Returns True if pdf exists and is opened, False otherwise
                    continue
            elif event == "-SAMPLENO-":
                # if the input sampleno is a integer and in-bounds of the file list, update the image_index
                # save old image index first, then try to convert the input to an integer
                # if its also valid, replace image_index with this new value, otherwise use the old value
                old_image_index = image_index
                try:
                    image_index = int(values["-SAMPLENO-"])
                except ValueError:
                    image_index = old_image_index
                else:
                    if image_index < 0 or image_index >= len(file_list):
                        # Out of bounds, use old value
                        image_index = old_image_index
                        values["-SAMPLENO-"] = image_index
            elif event == "Exit" or event == "WIN_CLOSED":
                sys.exit(0)
            else:
                if event in ["Set this pop NA", "DISCARD"]:
                    if event == "DISCARD":
                        user_is_sure = create_discard_are_you_sure_popup()
                        if not user_is_sure:
                            pass
                        else:
                            add_to_output_yaml(gate_name="DISCARD",
                                               descriptors=['DISCARD'],
                                               sample_id=collect_name_of_pdf_at_index(file_list, image_index))
                    elif event == "Set this pop NA":
                        # Add the sample to the yaml file under the NA entry for that gate
                        add_to_output_yaml(gate_name=gate_name, descriptors=['NA'],
                                           sample_id=collect_name_of_pdf_at_index(file_list, image_index))
                    event_list = []
                    image_index = next_sample(window_ref=window, image_index=image_index,
                                              file_list=file_list, page_no=page_no)
                elif event in ["previous"]:
                    event_list = []
                    image_index = previous_sample(window_ref=window, image_index=image_index,
                                                  file_list=file_list, page_no=page_no)
                elif event == "START":
                    event_list = []
                    window["-CORRECTIONS-"].update(value=' '.join(event_list))  # Display the event list in the GUI
                    # Trigger update_image at sample X or from the beginning
                    image_index = start_analysis(window_ref=window, image_index=image_index,
                                                 file_list=file_list, page_no=page_no)
                elif event == "DONE, next image":
                    # First check that the event list is valid. This spawns an invalid selection window if not
                    if check_event_categories(event_list, event_descriptor_dict):
                        if sample_in_yaml and event_list:  # If sample was already in the yaml and new limits were given
                            remove_from_yaml(sample_name, gate_name)
                        # If so, run the limit event handler
                        limit_event_handler(event_list, event_descriptor_dict, gate_name, sample_name)
                        # then clear the event list and go to the next sample
                        event_list = []
                        image_index = next_sample(window_ref=window, image_index=image_index,
                                                  file_list=file_list, page_no=page_no)
                    else:
                        # Otherwise, clear the event list and keep going on the same sample
                        event_list = []
                    window["-CORRECTIONS-"].update(value=' '.join(event_list))  # Display the event list in the GUI
                elif event == "Previous image":
                    event_list = []
                    image_index = previous_sample(window_ref=window, image_index=image_index,
                                                  file_list=file_list, page_no=page_no)
        else:
            # If the event is not a context event, add it to the event list
            event_list.append(event)
            window["-CORRECTIONS-"].update(value=' '.join(event_list))  # Display the event list in the GUI

    return
