#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
import os
import sys
import yaml
import PySimpleGUI as sg

# Global variable correction_yaml_file, gets set by AGClassifier on selecting output folder
# All functions that need this filepath/global variable are in AGClassifier_utilities.py
global correction_yaml_file
correction_yaml_file = "correction.yaml"


def set_correction_yaml_global(path):
    """
    Set the global variable for the correction yaml file to the path specified.

    :param path: Path to the correction yaml file
    :return:
    """

    global correction_yaml_file
    correction_yaml_file = path


# Wrong selection window
def create_invalid_select_window():
    """
    Warn the user that they have made an invalid selection by selecting more than one button of the same category.

    :return:
    """

    reportStr = "Invalid selection, more than one in each category (xlim/ylim) is not allowed.\n"
    sys.stderr.write(reportStr)
    invalid_selection_layout = [
        [
            sg.Text(
                'Invalid selection: more than one correction of the same category were selected.\nYou may only select'
                ' up to one correction of the same category for a single image.\nThere is no limit for the amount of'
                ' custom corrections.\nIt is also allowed to select no correction at all for an image.'),
            sg.Button('OK', size=(8, 4))
        ]
    ]
    invalid_select_window = sg.Window("Invalid Selection", invalid_selection_layout)
    debug_event, debug_values = invalid_select_window.read()
    if debug_event == "OK" or debug_event == sg.WIN_CLOSED:
        invalid_select_window.close()
    return


def update_image(window_ref, image_index, file_list, page_no=0, sample_in_yaml_string=""):
    """
    Update the image being shown in the PySimpleGUI window. Replace the current image with the image at the page
    'page_no' of the file specified in 'file_list'['image_index'].

    :param window_ref: reference to the main window
    :param image_index: index of the PDF file name we want to jump to in the file list
    :param file_list: list of all PDF files to process
    :param page_no: page number of the PDF to jump to. Default is 0. This can be a tuple of page numbers.
    :param sample_in_yaml_string:
    :return: Updated image index
    """

    # Validate page_no format
    if not isinstance(page_no, int):
        if isinstance(page_no, tuple):
            for elem in page_no:
                if not isinstance(elem, int):
                    raise TypeError("page_no must be an integer or a tuple of integers.")
        else:
            raise TypeError("page_no must be an integer or a tuple of integers.")

    # Load found valid image
    filename = file_list[image_index]
    cleaned_name = os.path.basename(filename).replace(".pdf", "")

    window_ref["-TOUT-"].update(cleaned_name)
    countStr = str(image_index + 1) + "/" + str(len(file_list))
    window_ref["-COUNT-"].update(countStr)

    # Open image X from pdf
    try:
        doc = fitz.open(filename)
    except FileNotFoundError:
        raise FileNotFoundError("File not found: " + filename)

    page_count = len(doc)
    dlist_tab = [None] * page_count
    # Page no can either be single int, if a single image is shown
    # but tuple of ints if 2 images are shown
    # Resolution should be different
    window_x_size = 960
    window_y_size = 840
    if isinstance(page_no, int):
        cur_page = page_no
    else:
        window_x_size = window_x_size / 2
        window_y_size = window_y_size / 2
        cur_page = page_no[0]

    pixmap = get_page(cur_page, dlist_tab, doc, width=window_x_size, height=window_y_size)  # show page 1 for start
    data = pixmap.tobytes("png")
    window_ref["-IMAGE-"].update(data=data, size=(int(window_x_size), int(window_y_size)))

    # Show list of which gates this sample has been classified as in the yaml
    window_ref["-INDEX-"].update(sample_in_yaml_string)

    # If image_index is a tuple, then load/update the second image
    if isinstance(page_no, tuple):
        second_page = page_no[1]
        second_image_page = get_page(second_page, dlist_tab, doc, width=window_x_size, height=window_y_size)
        second_image_data = second_image_page.tobytes("png")
        window_ref["-IMAGE2-"].update(data=second_image_data, size=(window_x_size, window_y_size))

        # If image_index is a tuple of length 3, then load/update the third image as well
        if len(page_no) == 3:
            third_page = page_no[2]
            third_image_page = get_page(third_page, dlist_tab, doc, width=window_x_size, height=window_y_size)
            third_image_data = third_image_page.tobytes("png")
            window_ref["-IMAGE3-"].update(data=third_image_data, size=(window_x_size, window_y_size))

    # Refresh entire window
    window_ref.refresh()


def create_pdf_window(fname: str, window_name) -> bool:
    """
    Creates a window with a PDF of all images belonging to the same sample.

    :param fname: filename of the PDF
    :param window_name: name of the window to be created
    :return: False if an error happened, True otherwise
    """

    try:
        doc = fitz.open(fname)
    except FileNotFoundError:
        # Maybe print error?
        # Maybe done in the calling function?
        create_no_sample_pdf()
        return False
    page_count = len(doc)
    dlist_tab = [None] * page_count
    cur_page = 0
    old_page = 0

    page_data = get_page(cur_page, dlist_tab, doc, width=480, height=480)  # show page 1 for start
    data = page_data.tobytes("png")
    image_elem = sg.Image(data=data)
    goto = sg.InputText(str(cur_page + 1), size=(5, 1))

    layout = [
        [
            sg.Button('Prev'),
            sg.Button('Next'),
            sg.Text('Page:'),
            goto,
        ],
        [image_elem],
    ]
    my_keys = ("Next", "Next:34", "Prev", "Prior:33", "MouseWheel:Down", "MouseWheel:Up")

    window = sg.Window(window_name, layout,
                       return_keyboard_events=True, use_default_focus=False)

    while True:
        event, values = window.read(timeout=100)
        force_page = False
        if event == sg.WIN_CLOSED:
            break
        if event in ("Escape:27",):  # this spares me a 'Quit' button!
            break
        if event[0] == chr(13):  # surprise: this is 'Enter'!
            try:
                cur_page = int(values[0]) - 1  # check if valid
                while cur_page < 0:
                    cur_page += page_count
            except IndexError:
                cur_page = 0  # this guy's trying to fool me
            goto.update(str(cur_page + 1))
        elif event in ("Next", "Next:34", "MouseWheel:Down"):
            cur_page += 1
        elif event in ("Prev", "Prior:33", "MouseWheel:Up"):
            cur_page -= 1

        if cur_page >= page_count:  # wrap around
            cur_page = 0
        while cur_page < 0:  # we show conventional page numbers
            cur_page += page_count
        if event in my_keys or not values[0]:
            goto.update(str(cur_page + 1))

        if cur_page != old_page:
            force_page = True
        # Update
        if force_page:
            page_data = get_page(cur_page, dlist_tab, doc, width=480, height=480)
            data = page_data.tobytes("png")
            image_elem.update(data=data)
            old_page = cur_page
    return True


def create_invalid_custom_window(label, value):
    """
    Notify the user that the custom limit they entered for a custom button is invalid.

    :param label:
    :param value:
    :return:
    """

    reportStr = "Invalid custom " + str(label) + " limit, expected integer (whole number), found: " + str(value)
    sys.stderr.write(reportStr)
    invalid_custom_limit_layout = [
        [
            sg.Text(reportStr),
            sg.Button('OK', size=(8, 4))
        ]
    ]
    invalidCustomWindow = sg.Window("Invalid custom limit", invalid_custom_limit_layout)
    debug_event, debug_values = invalidCustomWindow.read()
    if debug_event == "OK" or debug_event == sg.WIN_CLOSED:
        invalidCustomWindow.close()
    return


def create_no_sample_pdf():
    """
    Notify the user that the sample they selected does not have a corresponding PDF.

    :return:
    """

    # TODO - specify expected filename/path of the missing pdf ?
    missing_file = [
        [
            sg.Text('No .pdf file found for the sample.'),
            sg.Button('OK', size=(8, 4))
        ]
    ]
    NoPDF_window = sg.Window("Missing PDF", missing_file)
    debug_event, debug_values = NoPDF_window.read()
    if debug_event == "OK" or debug_event == sg.WIN_CLOSED:
        NoPDF_window.close()
        return


def create_complete_window():
    """
    Popup window to notify user that all samples have been processed.

    :return: PySimpleGUI window
    """

    layout = [
        [
            sg.Text('All images in folders have been processed!'),
            sg.Button('OK', size=(8, 4))
        ]
    ]
    windowref = sg.Window("Complete", layout)
    debug_event, debug_values = windowref.read()
    if debug_event == "OK" or debug_event == sg.WIN_CLOSED:
        windowref.close()
    return


def get_page(pno, dlist_tab, doc, width=0, height=0):
    """
    Get specific page of the document using pix.

    :param pno: Page number
    :param dlist_tab:
    :param doc:
    :return:
    """

    reportStr = "doclength: " + str(len(doc)) + " pageno: " + str(pno)
    print(reportStr)
    if len(doc) <= pno:
        pno = len(doc) - 1
    dlist = dlist_tab[pno]
    if not dlist:  # create if not yet there
        dlist_tab[pno] = doc[pno].get_displaylist()
        dlist = dlist_tab[pno]

    # get raw pixmap
    raw_pixmap = dlist.get_pixmap(alpha=False)
    # if raw_pixmap.width / raw_pixmap.height < width / height:
    #    zoomY = height / raw_pixmap.height
    #    zoomX = width / raw_pixmap.width
    zoomY = height / raw_pixmap.height
    zoomX = width / raw_pixmap.width
    mat = fitz.Matrix(zoomX, zoomY)
    pix = dlist.get_pixmap(matrix=mat, alpha=False)
    return pix


def check_if_discarded(image_index: int, file_list: list) -> bool:
    """
    Check if the sample is in the discarded list.

    :param image_index: index of the sample in the file list
    :param file_list: list of all samples that have been discarded
    :return:
    """

    if image_index is None:
        print("WARNING, in check_if_discarded: image_index is None")
        return False

    if image_index >= len(file_list):
        print("WARNING, in check_if_discarded: image_index out of range")
        return False

    cleaned_name = collect_name_of_pdf_at_index(file_list, image_index)
    if check_if_in_yaml(cleaned_name, gate_name="DISCARD"):
        return True
    return False


def add_to_output_yaml(gate_name: str, descriptors: list, sample_id: str) -> None:
    """
    Add the corrections specified by the user to the yaml file specific to that gate.
    TODO: Fix duplicated sample IDs. Entries on each descriptor should be unique.

    :param gate_name: Name of the gate the corrections apply to. It will be used to create the output file name.
    :param descriptors: List of descriptors to be added/expanded upon in the output file.
    :param sample_id: ID of the sample the corrections apply to.
    :return:
    """

    # Read the output file, add the corrections to the appropriate sample, then write the file again.
    with open(correction_yaml_file, "r") as in_file:
        yaml_full_dict = yaml.safe_load(in_file)  # Dict of lists
        if yaml_full_dict is None:
            yaml_full_dict = {}
        # For each descriptor, if not already in yaml, add it. Otherwise, append to the list.
        if gate_name not in yaml_full_dict:
            yaml_full_dict[gate_name] = {}
        for descriptor in descriptors:
            if descriptor not in yaml_full_dict[gate_name].keys():
                yaml_full_dict[gate_name][descriptor] = [sample_id]
            else:
                if sample_id not in yaml_full_dict[gate_name][descriptor]:
                    yaml_full_dict[gate_name][descriptor].append(sample_id)
                yaml_full_dict[gate_name][descriptor].sort()  # TODO: natural sorting instead?

    with open(correction_yaml_file, "w") as out_file:
        yaml.safe_dump(yaml_full_dict, out_file)


def collect_name_of_pdf_at_index(pdf_list: list, image_index: int) -> str:
    """
    Collect the name of the sample from the pdf file name.

    :param pdf_list: list of pdf files
    :param image_index: index of the sample in the list
    :return: Name of the PDF file without the extension
    """

    filename = pdf_list[image_index]
    cleaned_name = os.path.basename(filename).replace(".pdf", "")

    return cleaned_name


def check_if_in_yaml(sample_name: str, gate_name: str) -> bool:
    """
    Check if the sample already appears in the yaml file. If so, warn the user that the sample they are looking at
    already has corrections assigned to it. TODO If new corrections are given, the old ones will be removed?

    :param sample_name: Name of the sample.
    :param gate_name: Name of the gate the corrections apply to.
    :return: True if the sample is already in the yaml file, False otherwise.
    """

    # test print correction_yaml_file
    # print("correct_yaml_file: ", correction_yaml_file)

    with open(correction_yaml_file, "r") as in_file:
        yaml_full_dict = yaml.safe_load(in_file)  # Dict of lists
        if yaml_full_dict is None or gate_name not in yaml_full_dict:
            return False  # If the file is empty, the sample is not in it. Same if the gate is not in the file.
        for descriptor in yaml_full_dict[gate_name]:
            if sample_name in yaml_full_dict[gate_name][descriptor]:
                return True
        else:
            return False


def remove_from_yaml(sample_name: str, gate_name: str) -> None:
    """
    Remove all appearances of the sample name at the specified gate from yaml file.

    :param sample_name: Name of the sample to be removed.
    :param gate_name: Name of the gate the corrections apply to.
    :return: None
    """

    # test print correction_yaml_file
    print("correct_yaml_file: ", correction_yaml_file)

    with open(correction_yaml_file, "r") as in_file:
        yaml_full_dict = yaml.safe_load(in_file)
        if (yaml_full_dict is not None) and (gate_name in yaml_full_dict):
            for descriptor in yaml_full_dict[gate_name]:
                if sample_name in yaml_full_dict[gate_name][descriptor]:
                    yaml_full_dict[gate_name][descriptor].remove(sample_name)
    with open(correction_yaml_file, "w") as out_file:
        yaml.safe_dump(yaml_full_dict, out_file)


def create_discard_are_you_sure_popup() -> bool:
    """
    Create a PySimpleGUI popup to confirm the user wants to discard the current sample.

    :return:
    """

    layout = [[sg.Text("Are you sure you want to discard this sample?")],
              [sg.Button("Yes"), sg.Button("No")]]
    window = sg.Window("Discard sample", layout)
    event, values = window.read()
    window.close()
    if event == "Yes":
        return True
    else:
        return False


def create_clear_sample_corrections_are_you_sure_popup() -> bool:
    """
    Create a PySimpleGUI popup to confirm the user wants to discard the current sample.

    :return:
    """

    layout = [[sg.Text("This will remove the previously saved corrections for this sample. Are you sure?")],
              [sg.Button("Yes"), sg.Button("No")]]
    window = sg.Window("Clear sample corrections", layout)
    event, values = window.read()
    window.close()
    if event == "Yes":
        return True
    else:
        return False


def post_window_warning(window_ref, warning_string: str) -> str:
    """
    Takes a string and pushes that to the window ref, without any other changes
    :return: None
    """

    window_ref["-WARNING-"].update(warning_string)
    window_ref.refresh()


def create_yaml_string(image_index: str, file_list: list) -> str:
    # For the given sample name, parse the yaml and collect all descriptors where it appears,
    # also check the discard descriptor.
    # Return a string with all the descriptors and discard status.
    # Split it up in 1 descriptor per line
    descriptors = ""

    sample_name = collect_name_of_pdf_at_index(file_list, image_index)

    with open(correction_yaml_file, "r") as in_file:
        yaml_full_dict = yaml.safe_load(in_file)
        if yaml_full_dict is not None:
            if "DISCARD" in yaml_full_dict.keys() and sample_name in yaml_full_dict["DISCARD"]["DISCARD"]:
                descriptors += "Discard\n"
            for gate_name in yaml_full_dict.keys():
                gate_descriptors = []
                for descriptor in yaml_full_dict[gate_name]:
                    if sample_name in yaml_full_dict[gate_name][descriptor]:
                        gate_descriptors.append(descriptor)
                if len(gate_descriptors) > 0:
                    descriptors += gate_name + ": " + ", ".join(gate_descriptors) + "\n"
    return descriptors


def update_event_descriptor_dict(old_dict: dict, new_values: list) -> dict:
    """
    Update the event descriptor dictionary (event_descriptor_dict) with the new values from the GUI.
    The contents of the three sg.In cells above the custom buttons will be made into descriptors in the dictionary.

    :param old_dict: Old event_descriptor_dict
    :param new_values: List containing the contents of the three sg.In cells above the custom buttons.
    :return: Dictionary with the updated values
    """
    new_dict = old_dict.copy()
    new_dict["Custom 1"] = "CUSTOM_" + new_values[0]
    new_dict["Custom 2"] = "CUSTOM_" + new_values[1]
    new_dict["Custom 3"] = "CUSTOM_" + new_values[2]

    return new_dict


def bind_arrows(window_ref):
    """
    Bind the left and right arrow keys to the DONE and Previous buttons.
    :param window:
    :return:
    """
    window_ref.bind("<Right>", "DONE, next image")
    window_ref.bind("<Left>", "Previous image")


def unbind_arrows(window_ref):
    """
    Unbind the left and right arrow keys from the DONE and Previous buttons.
    :param window:
    :return:
    """
    try:
        window_ref.TKroot.unbind("<Right>")
        window_ref.TKroot.unbind("<Left>")
    except AttributeError:
        print("WARNING: It was not possible to unbind key arrows."
              "See https://github.com/PySimpleGUI/PySimpleGUI/issues/5300#issuecomment-1140442135")
