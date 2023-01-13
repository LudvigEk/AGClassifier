#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PySimpleGUI as sg

from AGClassifier_utilities import createInvalidSelectWindow, createInvalidCustomWindow, \
    createNoSamplePDF, createCompleteWindow, get_page, checkIfDiscarded, checkIfInIndexFiles


def event_handler(event, values, window, input_folder, output_folder):
    # Handle events, for now just accept any event and print it
    print("Event: ", event)
    return


def event_loop(window, input_folder, output_folder):
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        else:
            event_handler(event, values, window, input_folder, output_folder)
    return
