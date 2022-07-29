import PySimpleGUI as sg
from main import main

sg.theme('Default1')  # alternatives include, e.g., 'DarkGrey9'

layout = [[sg.Text('Select a folder and CSV file, then click the Launch button.')],
          [sg.Text('Folder', size=(8, 1)), sg.Input(), sg.FolderBrowse()],
          [sg.Text('CSV File', size=(8, 1)), sg.Input(), sg.FileBrowse(file_types=["CSV .csv"])],
          [sg.Button('Launch')]]

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
        path_to_folder = values[0]
        path_to_csv_file = values[1]

        print("\nLaunching dupeguru-post-processor...\n")
        main(path_to_folder, path_to_csv_file)

window.close()
