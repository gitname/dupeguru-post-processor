import unittest
from main import get_file_paths_from_csv_file, get_file_paths_within_folder
from os import path
import tempfile


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


if __name__ == '__main__':
    unittest.main()
