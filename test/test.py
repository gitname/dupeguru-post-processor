import unittest
from main import get_file_paths_from_csv_file
from os import path


class TestGetFilePathsFromCsvFile(unittest.TestCase):
    path_to_csv_file_01 = "./test/data/csv/01_headings.csv"
    path_to_csv_file_02 = "./test/data/csv/02_normal.csv"

    def test_01_headings(self):
        paths = get_file_paths_from_csv_file(self.path_to_csv_file_01)
        self.assertEqual(paths, [])

    def test_02_normal(self):
        paths = get_file_paths_from_csv_file(self.path_to_csv_file_02)
        self.assertEqual(paths, [
            f'C:{path.sep}carrot{path.sep}daikon{path.sep}banana.bbb',
            f'h:{path.sep}hyena{path.sep}giraffe',
            f'{path.sep}bash{path.sep}csh',
        ])


if __name__ == '__main__':
    unittest.main()
