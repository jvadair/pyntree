import unittest
from pyntree import Node
from os import chdir
chdir("..")

LOADABLE = ['tests/sample.txt', {'a': 1, 'b': {'c': 2}}]


class FileLoading(unittest.TestCase):
    def test_basic_load(self):
        for item in LOADABLE:
            with self.subTest():
                db = Node(item)


class FileReading(unittest.TestCase):
    def setUp(self):
        self.databases = [Node(i) for i in LOADABLE]

    def test_layer_0(self):
        for db in self.databases:
            with self.subTest():
                self.assertEqual(db(), {'a': 1, 'b': {'c': 2}})

    def test_layer_1(self):
        for db in self.databases:
            with self.subTest():
                self.assertEqual(db.a(), 1)
                self.assertEqual(db.b(), {'c': 2})

    def test_layer_2(self):
        for db in self.databases:
            with self.subTest():
                self.assertEqual(db.b.c(), 2)


# class DataReading(FileReadingTXT):
#     def __init__(self):
#         super().__init__()
#         self.db = Node({})


if __name__ == '__main__':
    unittest.main()
