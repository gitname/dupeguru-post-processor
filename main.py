"""
Summary:
    This script can be used to determine which files exist in a folder on your computer,
    but are not listed in a CSV file exported from dupeGuru (https://github.com/arsenetar/dupeguru/).

Reference:
    This script is based upon the following GitHub Issue:
    https://github.com/arsenetar/dupeguru/issues/218#issuecomment-1188238170

Usage:
    Invoking this script with the `--help` option will cause it to display usage information.

Notes:
    This script was designed to handle CSV files exported from dupeGuru following a _Filename_ or _Contents_ scan.
    This script does not correctly handle CSV files exported from dupeGuru following a _Folders_ scan, since this script
    does not get the folder paths from within the specified folder (although it may be updated to optionally do so).
"""

import logging
import sys
import argparse
import csv
import os
import pathlib

# Configure logging so entries are sent to STDOUT.
logging.basicConfig(stream=sys.stdout)

# Create a logger for this module.
log = logging.getLogger("main")


def get_file_paths_within_folder(path_to_folder):
    """Returns a list containing the path of each file within the specified folder and all of its descendant folders."""

    file_paths = []
    for current_folder_path, child_folder_names, child_file_names in os.walk(path_to_folder):
        for child_file_name in child_file_names:
            file_path = os.path.join(current_folder_path, child_file_name)
            abs_file_path = os.path.abspath(file_path)  # Force absolute path in case user specified the base relatively
            file_paths.append(abs_file_path)

    return file_paths


def get_file_paths_from_csv_file(path_to_csv_file):
    """Returns a list of file paths assembled from the specified CSV file, which was exported from dupeGuru."""

    file_paths = []

    # Note: Python docs recommend the use of `newline=""` here. See: https://docs.python.org/3/library/csv.html
    with open(path_to_csv_file, newline="") as csv_file:
        reader = csv.reader(csv_file)

        # Get the indices of the folder and filename columns.
        try:
            header = next(reader)
        except StopIteration:  # e.g. CSV file is empty
            pass
        else:
            folder_col_idx = [idx for (idx, s) in enumerate(header) if s == "Folder"][0]
            filename_col_idx = [idx for (idx, s) in enumerate(header) if s == "Filename"][0]
            log.debug(f"Index of CSV column containing folder   : {folder_col_idx}")
            log.debug(f"Index of CSV column containing filename : {filename_col_idx}")

            # Build a file path from each non-empty row (reminder: In Python, empty strings are False-y).
            for row in reader:
                if any(row):
                    filename = row[filename_col_idx]
                    folder_path = row[folder_col_idx]
                    file_path = os.path.join(folder_path, filename)
                    normalized_file_path = os.path.normpath(file_path)  # normalizes slashes based upon filesystem
                    file_paths.append(normalized_file_path)

        return file_paths


def main(path_to_folder, path_to_csv_file, path_to_output_file=None, log_level=logging.NOTSET):
    """Entrypoint to the script."""

    # Configure the logger so the threshold logging level is the one specified.
    level = logging.getLevelName(log_level) if type(log_level) is str else log_level
    log.setLevel(level)
    log.debug(f"Log level   : {log_level} ({level})")

    log.info(f'Folder       : {path_to_folder}')
    log.info(f'dupeGuru CSV : {path_to_csv_file}')
    log.info(f'Output file  : {path_to_output_file}')

    # Get a list of file paths from each source.
    file_paths_from_folder = get_file_paths_within_folder(path_to_folder)
    file_paths_from_csv_file = get_file_paths_from_csv_file(path_to_csv_file)
    log.debug(f"Number of file paths from folder   : {len(file_paths_from_folder)}")
    log.debug(f"Number of file paths from CSV file : {len(file_paths_from_csv_file)}")

    # Eliminate duplicate file paths from each list.
    distinct_file_paths_from_folder = set(file_paths_from_folder)
    distinct_file_paths_from_csv_file = set(file_paths_from_csv_file)
    log.debug(f"Number of distinct file paths from folder   : {len(distinct_file_paths_from_folder)}")
    log.debug(f"Number of distinct file paths from CSV file : {len(distinct_file_paths_from_csv_file)}")

    # Determine which file paths from the folder are not in the set of file paths from the CSV file.
    differences = distinct_file_paths_from_folder.difference(distinct_file_paths_from_csv_file)
    log.info(f"Number of differences : {len(differences)}")

    sorted_differences = sorted(list(differences))

    # Either write the results to a CSV file or print them to STDOUT.
    if type(path_to_output_file) is str:
        with open(path_to_output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)

            # Populate the header row (i.e. column names).
            header_row = ["File", "Folder", "Filename", "Suffix (only)"]
            writer.writerow(header_row)

            # Populate the data rows with the file path, folder path (no filename), filename, and file suffix.
            data_rows = []
            for path in sorted_differences:
                file_suffix = pathlib.Path(path).suffix
                (folder_path, filename) = os.path.split(path)
                data_rows.append([path, folder_path, filename, file_suffix])
            writer.writerows(data_rows)
    else:
        print('\n'.join(sorted_differences))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compares a folder to a CSV file exported from dupeGuru. Displays the '
                                                 'differences on the console (default) or writes them to a CSV file.')
    parser.add_argument('folder',
                        help='path to the folder with which you want to compare the CSV file exported from dupeGuru')
    parser.add_argument('csv_file',
                        help='path to the CSV file exported from dupeGuru')
    parser.add_argument('--output_csv_file', metavar='PATH',
                        help='if you use this option, the script will generate a CSV file at the path you specify; '
                             'otherwise, the script will display the results on the console')
    parser.add_argument('--log_level', metavar='LEVEL',
                        choices=('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), default='NOTSET',
                        help='specify a logging level for the script')
    args = parser.parse_args()

    main(args.folder, args.csv_file, args.output_csv_file, args.log_level)
