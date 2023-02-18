import unittest
from pyntree import Node
from pyntree.file import EXTENSIONS
import os

os.chdir("..")

LOADABLE = [
    'tests/sample.txt',
    {'a': 1, 'b': {'c': 2}},
    "tests/sample.pyn",
    "tests/sample.pyn.gz",
    "tests/sample.json"
]


class FileLoading(unittest.TestCase):
    def test_basic_load(self):
        for item in LOADABLE:
            with self.subTest(msg=str(item)):
                db = Node(item)

    def test_blank_load(self):
        db = Node()
        self.assertEqual(db(), {})


class FileReading(unittest.TestCase):
    def setUp(self):
        self.databases = [Node(i) for i in LOADABLE]

    def test_layer_0(self):
        for db in self.databases:
            with self.subTest(msg=db.file.filetype):
                self.assertEqual(db(), {'a': 1, 'b': {'c': 2}})

    def test_layer_1(self):
        for db in self.databases:
            with self.subTest(msg=db.file.filetype):
                self.assertEqual(db.a(), 1)
                self.assertEqual(db.b(), {'c': 2})

    def test_layer_2(self):
        for db in self.databases:
            with self.subTest(msg=db.file.filetype):
                self.assertEqual(db.b.c(), 2)


class FileModification(unittest.TestCase):
    def test_layer_0(self):
        db = Node({})
        db.set('a', 1)
        self.assertEqual(db.a(), 1)

    def test_layer_1(self):
        db = Node({'a': {}})
        db.a.set('b', {})
        self.assertEqual(db.a.b(), {})

    def test_layer_2(self):
        db = Node({'a': {'b': {}}})
        db.a.b.set('c', 3)
        self.assertEqual(db.a.b.c(), 3)

    def test_alternate_set(self):
        db = Node({})
        db.z = 1
        # noinspection PyCallingNonCallable
        self.assertEqual(db.z(), 1)


class FileSaving(unittest.TestCase):
    def setUp(self):
        self.filetypes = EXTENSIONS.keys()

    def test_save(self):
        for ext in self.filetypes:
            with self.subTest(msg=ext):
                db = Node({'a': 1, 'b': {'c': 2}})
                db.file.switch_to_file('tests/testing_output.' + ext)
                db.save()
                self.assertEqual(Node('tests/testing_output.' + ext)(), db())
                os.remove('tests/testing_output.' + ext)

    def test_save_to_alternate_file(self):
        # Initial data
        db = Node({'a': 1, 'b': {'c': 2}})
        db.switch_to_file('tests/testing_output.txt')
        db.save()
        del db
        # Overwrite, but maintain original file object
        db = Node({'n': 1, 'b': {'c': 2}})
        db.switch_to_file('tests/testing_output_2.pyn')
        db.save(filename='tests/testing_output.txt')
        db.save()
        self.assertEqual(Node("tests/testing_output.txt")(), {'n': 1, 'b': {'c': 2}})
        self.assertEqual(Node("tests/testing_output_2.pyn")(), {'n': 1, 'b': {'c': 2}})
        os.remove("tests/testing_output.txt")
        os.remove("tests/testing_output_2.pyn")

    def test_dictionary_filename(self):
        db = Node({'a': 'b'})
        db.switch_to_file('tests/testing_savedict.json')
        db.save()
        self.assertEqual(Node('tests/testing_savedict.json')(), {'a': 'b'})
        os.remove('tests/testing_savedict.json')


class DeletionTests(unittest.TestCase):
    def test_layer_0(self):
        db = Node({'a': {'b': {'c': 'd'}}, 'b': "test"})
        db.delete()
        self.assertEqual(db(), {})

    def test_layer_1(self):
        db = Node({'a': {'b': {'c': 'd'}}, 'b': "test"})
        db.delete('a')
        self.assertEqual(db(), {'b': 'test'})

    def test_layer_1_alternate(self):
        db = Node({'a': {'b': {'c': 'd'}}, 'b': "test"})
        db.a.delete()
        self.assertEqual(db(), {"b": "test"})

    def test_layer_2(self):
        db = Node({'a': {'b': {'c': 'd'}}, 'b': "test"})
        db.a.delete('b')
        self.assertEqual(db(), {'a': {}, 'b': "test"})

    def test_layer_2_alternate(self):
        db = Node({'a': {'b': {'c': 'd'}}, 'b': "test"})
        db.a.b.delete()
        # noinspection PyCallingNonCallable
        self.assertEqual(db(), {'a': {}, 'b': "test"})


class FileScanningTests(unittest.TestCase):
    def setUp(self):
        self.db = Node({"val1": 'h', "val2": 'b'})

    def test_has(self):
        self.assertTrue(self.db.has("val1"))

    def test_values(self):
        self.assertEqual(self.db.values, ["val1", "val2"])


if __name__ == '__main__':
    unittest.main()
