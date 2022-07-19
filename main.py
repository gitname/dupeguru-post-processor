# This script can be used to generate a list of files that exist within a folder, but are not listed within a CSV file.
# It is based upon the conversation here: https://github.com/arsenetar/dupeguru/issues/218#issuecomment-1188238170

import logging
import sys
import argparse
import csv
import os

# Configure logging so entries are sent to STDOUT.
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


def get_file_paths_from_folder(path_to_folder):
    """Returns a list containing the path of each file within the specified folder and all of its descendant folders."""

    file_paths = []
    for current_folder_path, child_folder_names, child_file_names in os.walk(path_to_folder):
        for child_file_name in child_file_names:
            file_path = os.path.join(current_folder_path, child_file_name)
            file_paths.append(file_path)
    logging.debug(file_paths)

    return file_paths


def get_file_paths_from_csv_file(path_to_csv_file):
    """Returns a list of file paths assembled from the specified CSV file, which was exported from dupeGuru."""

    # Note: Python docs recommend the use of `newline=""` here. See: https://docs.python.org/3/library/csv.html
    with open(path_to_csv_file, newline="") as csv_file:
        reader = csv.reader(csv_file)

        # Get the indices of the folder and filename columns.
        header = next(reader)
        folder_col_idx = [idx for (idx, s) in enumerate(header) if s == "Folder"][0]
        filename_col_idx = [idx for (idx, s) in enumerate(header) if s == "Filename"][0]
        logging.debug(f"Folder column number   : {folder_col_idx}")
        logging.debug(f"Filename column number : {filename_col_idx}")

        # Build a file path from each non-empty row (reminder: In Python, empty strings are False-y).
        # Note: We already iterated to the header row above, so that row will not be included in the iteration below.
        file_paths = [f"{os.path.join(row[folder_col_idx], row[filename_col_idx])}" for row in reader if any(row)]
        logging.debug(file_paths)

        return file_paths


def main(path_to_folder, path_to_csv_file, path_to_output_file):
    logging.info(f'Folder       : {path_to_folder}')
    logging.info(f'dupeGuru CSV : {path_to_csv_file}')
    logging.info(f'Output file  : {path_to_output_file}')

    file_paths_from_folder = get_file_paths_from_folder(path_to_folder)
    file_paths_from_csv_file = get_file_paths_from_csv_file(path_to_csv_file)

    # Determine which file paths from the folder are not in the list of file paths from the CSV file.
    distinct_file_paths_from_folder = set(file_paths_from_folder)
    distinct_file_paths_from_csv_file = set(file_paths_from_csv_file)
    logging.info(f"Number of distinct file paths from folder   : {len(distinct_file_paths_from_folder)}")
    logging.info(f"Number of distinct file paths from CSV file : {len(distinct_file_paths_from_csv_file)}")
    differences = distinct_file_paths_from_folder.difference(distinct_file_paths_from_csv_file)
    logging.info(f"Number of differences                       : {len(differences)}")

    # Either write the results to a CSV file or print them to STDOUT.
    if path_to_output_file is None:
        print('\n'.join(differences))
    else:
        with open(path_to_output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            rows = [[path] for path in differences]  # gives `rows` the shape: `[ [path_1], [path_2], ..., [path_N] ]`
            writer.writerows(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare a folder to a CSV file exported from dupeGuru.')
    parser.add_argument('path_to_folder',
                        help='Path to folder')
    parser.add_argument('path_to_csv_file',
                        help='Path to CSV file exported from dupeGuru')
    parser.add_argument('-o', '--path_to_output_file',
                        help='Path at which you want this script to store the CSV file it generates.')
    args = parser.parse_args()

    main(args.path_to_folder, args.path_to_csv_file, args.path_to_output_file)
