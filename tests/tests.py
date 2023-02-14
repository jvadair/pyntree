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


if __name__ == '__main__':
    unittest.main()
