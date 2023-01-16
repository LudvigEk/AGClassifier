#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from glob import glob

from AGClassifier_utilities import createInvalidSelectWindow, createInvalidCustomWindow, \
    createNoSamplePDF, createCompleteWindow, get_page, checkIfDiscarded, checkIfInIndexFiles, \
    createPDFWindow, start_gating


def check_event_categories(event_list, event_descriptor_dict):
    # Check that only one event of each category is present
    # Custom_ events are an exception to this rule
    # Custom_ events can be selected multiple times
    event_categories = []
    for event in event_list:
        if "_" in event:
            event_category = event_descriptor_dict[event].split("_")[0]
            if event_category is not "CUSTOM_":
                event_categories.append(event_category)
        else:
            event_categories.append(event)
    event_categories = set(event_categories)
    if len(event_categories) < len(event_list):
        createInvalidSelectWindow()
        return False
    else:
        return True


def limit_event_handler(event_list, output_folder, event_descriptor_dict):
    # Check if event exists in the button_descriptor_dict
    # If not, raise
    for event in event_list:
        if event.split("_")[0] != "CUSTOM" and event in event_descriptor_dict.keys():
            # If so, get the descriptor
            descriptor = event_descriptor_dict[event]
            # print it to the console
            print("event descriptor: ", descriptor)
        elif event.split("_")[0] == "CUSTOM":
            # Just print the event to the console and continue
            print("event descriptor: ", event)
        else:
            raise_str = "Event " + str(event) + " not found in event_descriptor_dict and is not a custom event"
            raise ValueError(raise_str)
    return


def context_event_handler(event_list, input_folder, output_folder):
    # TODO
    # Handle static, contextual events
    # These are events that are not defined in the event_descriptor_dict
    for event in event_list:
        print(event)
    return


def event_handler(event_list, input_folder, output_folder, event_descriptor_dict):
    # TODO
    # Handle events
    # At this point the events are valid (check_event_categories has been run)
    # Thus, we sort the event_list into limit and context events
    # We call the context event handler first, then the limit event handler
    # 'START', 'Done, next image', 'Previous image' and 'Exit' are handled in the event loop
    context_events = []
    limit_events = []
    for event in event_list:
        if event.split("_")[0] in ["DISCARD", "Set this pop NA", "Open pdf", ]:
            context_events.append(event)
        else:
            limit_events.append(event)
    context_event_handler(context_events, input_folder, output_folder)
    limit_event_handler(limit_events, output_folder, event_descriptor_dict)
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


def initialise_file_list(input_folder, event_descriptor_dict):
    file_list = glob(input_folder + "/*.pdf")
    n_of_images = event_descriptor_dict["number_of_images"]

def event_loop(window, input_folder, output_folder, event_descriptor_dict):
    image_index = 0
    gated_samples = []
    file_list = glob(input_folder + "/*.pdf")

    file_list, page_no = initialise_file_list(input_folder, event_descriptor_dict)

    # Initialise the event list with no elements
    event_list = []
    while True:
        event, values = window.read()
        # First check for context events (start, exit, previous, discard, set to na, open pdf)
        if is_context_event(event):
            # The open pdf event is a special case, it does not clear the event list
            if event == 'Open pdf':
                createPDFWindow()  # Returns True if pdf exists and is opened, False otherwise
            elif event == "DONE, next image":
                # First check that the event list is valid
                # This spawns an invalid selection window if not
                if check_event_categories(event_list, event_descriptor_dict):
                    # If so, run the event handler
                    limit_event_handler(event_list, output_folder, event_descriptor_dict)
                    # then clear the event list and go to the next sample
                    event_list = []
                    next_sample()
                else:
                    # If check_event_categories returns False, the event list is invalid
                    # Clear the event list and remain on the same sample
                    event_list = []
            else:
                # These other context events always clear the event list.
                event_list = []
                if event in ["set to na", "discard"]:
                    # These events should trigger a next sample call
                    next_sample()
                elif event in ["previous"]:
                    previous_sample()
                elif event == "START":
                    # Trigger start gating at sample X or from the beginning
                    # window_ref, image_index, file_list, page_no = 0
                    start_gating(window_ref=window, image_index=image_index, file_list=file_list, page_no=page_no)
                    continue
                else:
                    # Raise unknown context event
                    raise ValueError("Unknown context event: " + str(event))
        else:
            # If the event is not a context event, add it to the event list
            event_list.append(event)

    return
