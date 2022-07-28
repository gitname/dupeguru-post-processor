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


def get_file_paths_within_folder(path_to_folder):
    """Returns a list containing the path of each file within the specified folder and all of its descendant folders."""

    file_paths = []
    for current_folder_path, child_folder_names, child_file_names in os.walk(path_to_folder):
        for child_file_name in child_file_names:
            file_path = os.path.join(current_folder_path, child_file_name)
            file_paths.append(file_path)

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
            logging.debug(f"Index of CSV column containing folder   : {folder_col_idx}")
            logging.debug(f"Index of CSV column containing filename : {filename_col_idx}")

            # Build a file path from each non-empty row (reminder: In Python, empty strings are False-y).
            # Note: We already iterated to the header row, so that row will not be included in the iteration below.
            file_paths = [f"{os.path.join(row[folder_col_idx], row[filename_col_idx])}" for row in reader if any(row)]
            logging.debug(file_paths)

        return file_paths


def main(path_to_folder, path_to_csv_file, path_to_output_file=None):
    """Entrypoint to the script."""

    logging.info(f'Folder       : {path_to_folder}')
    logging.info(f'dupeGuru CSV : {path_to_csv_file}')
    logging.info(f'Output file  : {path_to_output_file}')

    # Get a list of file paths from each source.
    file_paths_from_folder = get_file_paths_within_folder(path_to_folder)
    file_paths_from_csv_file = get_file_paths_from_csv_file(path_to_csv_file)
    logging.debug(f"Number of file paths from folder   : {len(file_paths_from_folder)}")
    logging.debug(f"Number of file paths from CSV file : {len(file_paths_from_csv_file)}")

    # Eliminate duplicate file paths from each list.
    distinct_file_paths_from_folder = set(file_paths_from_folder)
    distinct_file_paths_from_csv_file = set(file_paths_from_csv_file)
    logging.debug(f"Number of distinct file paths from folder   : {len(distinct_file_paths_from_folder)}")
    logging.debug(f"Number of distinct file paths from CSV file : {len(distinct_file_paths_from_csv_file)}")

    # Determine which file paths from the folder are not in the set of file paths from the CSV file.
    differences = distinct_file_paths_from_folder.difference(distinct_file_paths_from_csv_file)
    logging.info(f"Number of differences : {len(differences)}")

    sorted_differences = sorted(list(differences))

    # Either write the results to a CSV file or print them to STDOUT.
    if type(path_to_output_file) is str:
        with open(path_to_output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            rows = [[path] for path in sorted_differences]  # gives `rows` the shape: `[ [path_1], [path_2], ... ]`
            writer.writerows(rows)
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

    # Configure logging so entries are sent to STDOUT and so the threshold level is the one specified.
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName(args.log_level))

    main(args.folder, args.csv_file, args.output_csv_file)
