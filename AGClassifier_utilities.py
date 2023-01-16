#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
import os
import sys

import PySimpleGUI as sg


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
                'Invalid selection, too many X- or Y- limits\nYou may only select up to one X-limit and up to one '
                'Y-limit.\nIt is allowed to select no limit at all for an image, as well as just one X- or Y- '
                'limit\nand an unlimited amount of custom limits.'),
            sg.Button('OK', size=(8, 4))
        ]
    ]
    invalid_select_window = sg.Window("Invalid Selection", invalid_selection_layout)
    debug_event, debug_values = invalid_select_window.read()
    if debug_event == "OK" or debug_event == sg.WIN_CLOSED:
        invalid_select_window.close()
    return


def update_image(window_ref, image_index, file_list, page_no=0, b_forward_on_invalid=True):
    """
    Commence the QC process or jump to the selected image.
    :param window_ref: reference to the main window
    :param image_index: index of the image to jump to
    :param file_list: list of files to process
    :param page_no: page number of the PDF to jump to. Default is 0. This can be a tuple of page numbers.
    :param b_forward_on_invalid: if True, the program will jump to the next image if the selected image is invalid,
    otherwise it will jump to the previous image. Default is True.
    :return:
    """

    # Validate page_no format
    if not isinstance(page_no, int):
        if isinstance(page_no, tuple):
            for elem in page_no:
                if not isinstance(elem, int):
                    raise TypeError("page_no must be an integer or a tuple of integers.")
        raise TypeError("page_no must be an integer or a tuple of integers.")

    # Validate image_index, if invalid, try next image (or previous depending on flag) until valid or end of list
    if b_forward_on_invalid:
        image_increment = 1
    else:
        image_increment = -1
    while check_if_discarded(image_index, file_list):
        image_index += image_increment


    # Load found valid image
    filename = file_list[image_index]

    cleaned_name = os.path.basename(filename).replace(".pdf", "")

    window_ref["-TOUT-"].update(cleaned_name)
    countStr = str(image_index) + "/" + str(len(file_list))
    window_ref["-COUNT-"].update(countStr)

    # Open image X from pdf
    try:
        doc = fitz.open(filename)
    except FileNotFoundError:
        raise FileNotFoundError("File not found: " + filename)

    page_count = len(doc)
    dlist_tab = [None] * page_count
    if isinstance(page_no, int):
        cur_page = page_no
        window_x_size = 320
        window_y_size = 280
    else:
        cur_page = page_no[0]
        window_x_size = 160
        window_y_size = 140

    data = get_page(cur_page, dlist_tab, doc)  # show page 1 for start
    window_ref["-IMAGE-"].update(data=data, size=(window_x_size, window_y_size))

    # Check if in any index:
    sampleInIndexFiles = check_if_in_index_files(image_index, file_list)
    window_ref["-INDEX-"].update(sampleInIndexFiles)

    # If image_index is a tuple, then load/update the second image
    if isinstance(image_index, tuple):
        second_page = page_no[1]
        second_image_data = get_page(second_page, dlist_tab, doc)
        window_ref["-IMAGE2-"].update(data=second_image_data, size=(window_x_size, window_y_size))


def create_pdf_window(fname, ID):
    """
    Creates a window with a PDF of all images belonging to the same sample.
    :param fname: filename containing the PDF
    :param ID: sample ID
    :return:
    """
    #
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

    data = get_page(cur_page, dlist_tab, doc)  # show page 1 for start
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

    window = sg.Window(ID, layout,
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
            data = get_page(cur_page, dlist_tab, doc)
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
    return sg.Window("Complete", layout)


def get_page(pno, dlist_tab, doc):
    """

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
        dlist_tab[pno] = doc[pno].getDisplayList()
        dlist = dlist_tab[pno]
    pix = dlist.getPixmap(alpha=False)
    return pix.getPNGData()


def check_if_discarded(image_index, file_list):
    """
    Check if the sample is in the discarded list.
    :param image_index:
    :param file_list:
    :return:
    """
    if image_index >= len(file_list):
        return False

    # TODO update this once the .yaml format is updated. For now just accept all samples.
    return False

    discard_list = []
    discard_file = values["-OUT_FOLDER-"] + "/discard.txt"

    if os.path.exists(discard_file):
        with open(discard_file, 'r', newline='\n') as f:
            discard_list = f.read().splitlines()

    filename = os.path.join(

        values["-FOLDER-"], file_list[image_index]

    )
    cleaned_name = cleaned_name = os.path.basename(filename).replace(".pdf", "")

    if any([cleaned_name in x for x in discard_list]):
        return True
    else:
        return False


def check_if_in_index_files(image_index, file_list):
    """
    Check if the sample is in the file list.
    :param image_index:
    :param file_list:
    :return:
    """

    # TODO update this once the .yaml format is updated. For now just accept all samples.
    return ""

    filename = os.path.join(

        values["-FOLDER-"], file_list[image_index]

    )
    cleaned_name = cleaned_name = os.path.basename(filename).replace(".pdf", "")
    population_name = str(values["-PREFIX-"])

    index_files_for_pop = glob(values["-OUT_FOLDER-"] + "/*.txt")
    files_w_sample = []
    if isinstance(index_files_for_pop, list):
        for index_file in index_files_for_pop:
            with open(index_file, 'r', newline='\n') as f:
                content = f.read().splitlines()
                if cleaned_name in content:
                    files_w_sample.append(os.path.basename(index_file).replace(".txt", ""))  # Cross-platform
                    # files_w_sample.append(index_file.split("/")[-1].replace(".txt",""))
    elif isinstance(index_files_for_pop, str):
        with open(index_files_for_pop, 'r', newline='\n') as f:
            content = f.read().splitlines()
            if cleaned_name in content:
                files_w_sample.append(os.path.basename(index_files_for_pop).replace(".txt", ""))  # Cross-platform
                # files_w_sample.append(index_files_for_pop.split("/")[-1].replace(".txt", ""))
    else:
        return ""
    outStr = ""
    for entry in files_w_sample:
        outStr = entry + " " + outStr
    return outStr

