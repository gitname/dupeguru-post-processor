import PySimpleGUI as sg
from uuid import uuid4
from os import path
from main import main

sg.theme('Default1')  # alternatives include, e.g., 'DarkGrey9'

layout = [[sg.Text('Select a folder, a CSV file and, optionally, an output folder, then click the Launch button.')],
          [sg.Text('Folder', size=(17, 1)), sg.Input(key="-FOLDER-"), sg.FolderBrowse()],
          [sg.Text('CSV File', size=(17, 1)), sg.Input(key="-CSV_FILE-"), sg.FileBrowse(file_types=["CSV .csv"])],
          [
              sg.Text('Output Folder (optional)', size=(17, 1), tooltip='If specified, the main script will generate '
                                                                        'a CSV file in this folder'),
              sg.Input(key="-OUTPUT_FOLDER-"),
              sg.FolderBrowse()
          ],
          [
              sg.Text('Log level', size=(17, 1)),
              sg.Radio('NOTSET (default)', "log_level_radio_group", key="-NOTSET-", default=True),
              sg.Radio('DEBUG', "log_level_radio_group", key="-DEBUG-"),
              sg.Radio('INFO', "log_level_radio_group", key="-INFO-"),
              sg.Radio('WARNING', "log_level_radio_group", key="-WARNING-"),
          ],
          [sg.Button('Launch', tooltip='Launch the main script with the specified parameters')]]

# Create the Window
window = sg.Window('dupeguru-post-processor (Graphical Launcher)', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    # If the user closed the window, terminate the GUI.
    if event == sg.WIN_CLOSED:
        break
    # Else, if the user clicked the Launch button, invoke the script's main function.
    elif event == 'Launch':
        # Retrieve and strip input values.
        path_to_folder = values["-FOLDER-"].strip()
        path_to_csv_file = values["-CSV_FILE-"].strip()
        path_to_output_folder = values["-OUTPUT_FOLDER-"].strip()

        # Normalize the log level.
        log_level = "DEBUG" if values["-DEBUG-"] \
            else "INFO" if values["-INFO-"] \
            else "WARNING" if values["-WARNING-"] \
            else "NOTSET"

        # Validate stripped input values.
        if not path.isdir(path_to_folder):
            sg.Popup("Folder path is invalid", keep_on_top=True)
            continue  # end this iteration
        elif not path.isfile(path_to_csv_file):
            sg.Popup("CSV file path is invalid", keep_on_top=True)
            continue
        elif len(path_to_output_folder) > 0 and not path.isdir(path_to_output_folder):
            sg.Popup("Output folder (optional) path was specified, but is invalid", keep_on_top=True)
            continue

        # If the user specified an output _folder_, generate an output file path; otherwise, default to None.
        path_to_output_file = None
        if len(path_to_output_folder) > 0:
            # Keep trying to generate a random file name that does not already exist.
            #
            # Note: This is not a foolproof way of preventing naming collisions. It is technically possible that some
            #       other process creates a file at the same path, between now (i.e. the time we perform this name
            #       collision check) and the time the main script creates a file at that path.
            #
            while True:
                random_file_name = f"{uuid4().hex}.csv"
                path_to_output_file = path.join(path_to_output_folder, random_file_name)
                if not path.isfile(path_to_output_file):
                    break  # stop iterating once we have a unique file name
            print(f"Output file path: {path.normpath(path_to_output_file)}\n")

        print("Launching dupeguru-post-processor...\n")
        main(
            path.normpath(path_to_folder),
            path.normpath(path_to_csv_file),
            path.normpath(path_to_output_file),
            log_level=log_level
        )

        sg.Popup("Done.", keep_on_top=True)

window.close()
