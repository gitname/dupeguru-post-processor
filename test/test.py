import os
import unittest
from main import (
    get_file_paths_from_csv_file,
    get_file_paths_within_folder,
    write_to_csv_file
)
from os import path
import tempfile
import csv


class TestGetFilePathsFromCsvFile(unittest.TestCase):
    path_to_csv_file_01 = path.normpath("./test/data/csv/01_headings.csv")
    path_to_csv_file_02 = path.normpath("./test/data/csv/02_normal.csv")

    def test_01_headings(self):
        expectation = []
        paths = get_file_paths_from_csv_file(self.path_to_csv_file_01)
        self.assertEqual(paths, expectation)

    def test_02_normal(self):
        expectation = [
            f'C:{path.sep}carrot{path.sep}daikon{path.sep}banana.bbb',
            f'h:{path.sep}hyena{path.sep}giraffe',
            f'{path.sep}bash{path.sep}csh',
        ]
        paths = get_file_paths_from_csv_file(self.path_to_csv_file_02)
        self.assertEqual(paths, expectation)


class TestGetFilePathsWithinFolder(unittest.TestCase):
    path_to_nonexistent_folder = path.normpath("./test/data/does_not_exist")
    path_to_nonexistent_folder_slash = path.normpath("./test/data/does_not_exist/")
    path_to_parent_folder = path.normpath("./test/data/parent")
    path_to_parent_folder_slash = path.normpath("./test/data/parent/")
    path_to_child_folder = path.normpath("./test/data/parent/child")
    path_to_child_folder_slash = path.normpath("./test/data/parent/child/")

    def test_nonexistent_folder(self):
        expectation = []
        paths = get_file_paths_within_folder(self.path_to_nonexistent_folder)
        self.assertEqual(paths, expectation)
        paths = get_file_paths_within_folder(self.path_to_nonexistent_folder_slash)
        self.assertEqual(paths, expectation)

    def test_empty_folder(self):
        expectation = []
        with tempfile.TemporaryDirectory() as dir_path:  # Create temporary empty folder
            paths = get_file_paths_within_folder(dir_path)
            self.assertEqual(paths, expectation)

    def test_parent_folder(self):
        expectation = [
            path.abspath("./test/data/parent/CAPITAL.TXT"),
            path.abspath("./test/data/parent/lowercase.txt"),
            path.abspath("./test/data/parent/child/CAPITAL.TXT"),
        ]
        paths = get_file_paths_within_folder(self.path_to_parent_folder)
        self.assertEqual(paths, expectation)
        paths = get_file_paths_within_folder(self.path_to_parent_folder_slash)
        self.assertEqual(paths, expectation)

    def test_child_folder(self):
        expectation = [
            path.abspath("./test/data/parent/child/CAPITAL.TXT"),
        ]
        paths = get_file_paths_within_folder(self.path_to_child_folder)
        self.assertEqual(paths, expectation)
        paths = get_file_paths_within_folder(self.path_to_child_folder_slash)
        self.assertEqual(paths, expectation)


class TestWriteToCsvFile(unittest.TestCase):
    header_row = ["File", "Folder", "Filename", "Suffix (only)"]
    temp_file = None

    def setUp(self):
        """Create a temporary file before each test."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)

    def tearDown(self):
        """Close and delete the temporary file after each test."""
        self.temp_file.close()
        os.remove(self.temp_file.name)

    def test_empty_list(self):
        write_to_csv_file([], self.temp_file.name)
        with open(self.temp_file.name, 'r', encoding='utf8', newline='') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
            self.assertEqual(rows, [self.header_row])

    def test_nonempty_list(self):
        file_paths = [
            r"C:/A/B/C",  # forward slashes
            r"C:\A\B\C",  # no suffix
            r"C:\A\B\C.d",  # suffix
            r"C:\A\B\C.d.e",  # multiple suffixes
            r"C:\A\B\C d.e",  # space in file name
            r"C:\A B\C",  # space in folder name
        ]
        expected_rows = [
            self.header_row,
            [r"C:/A/B/C", r"C:/A/B", r"C", r""],
            [r"C:\A\B\C", r"C:\A\B", r"C", r""],
            [r"C:\A\B\C.d", r"C:\A\B", r"C.d", r".d"],
            [r"C:\A\B\C.d.e", r"C:\A\B", r"C.d.e", r".e"],
            [r"C:\A\B\C d.e", r"C:\A\B", r"C d.e", r".e"],
            [r"C:\A B\C", r"C:\A B", r"C", r""],
        ]
        write_to_csv_file(file_paths, self.temp_file.name)
        with open(self.temp_file.name, 'r', encoding='utf8', newline='') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
            self.assertEqual(rows, expected_rows)


if __name__ == '__main__':
    unittest.main()
