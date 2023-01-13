#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from AGClassifier_utilities import createInvalidSelectWindow, createInvalidCustomWindow, \
    createNoSamplePDF, createCompleteWindow, get_page, checkIfDiscarded, checkIfInIndexFiles

def check_event_categories(event_list, event_descriptor_dict):
    # Check that only one event of each category is present
    # Custom_ events are an exception to this rule
    # Custom_ events can be selected multiple times
    event_categories = []
    for event in event_list:
        event_category = event_descriptor_dict[event].split("_")[0]
        if event_category is not "CUSTOM_":
            event_categories.append(event_category)
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

def context_event_handler(event, values, input_folder, output_folder):
    # TODO
    # Handle static, contextual events
    # These are events that are not defined in the event_descriptor_dict

    return
def next_sample():
    # TODO
    # Get the next sample
    # If there is no next sample, create a complete window and return False
    # If the next sample is discarded or already analysed, skip it and go to the next one
    # If the next sample is not discarded or analysed, display it and return True
    return True

def event_loop(window, input_folder, output_folder, event_descriptor_dict):
    # Initialise the event list with no elements
    event_list = []
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "DONE":
            # First check that the event list is valid
            # This spawns a invalid selection window if not
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
