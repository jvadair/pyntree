import unittest
from pyntree import Node
from pyntree.file import EXTENSIONS
import os
from datetime import datetime as dt

os.chdir("..")

BASIC_FILES = [
    'tests/sample.txt',
    {'a': 1, 'b': {'c': 2}},
    "tests/sample.pyn",
    "tests/sample.pyn.gz",
    "tests/sample.json"
]

ENCRYPTED_FILES = [
    "tests/encrypted.pyn",
    "tests/encrypted.json",
    "tests/encrypted.txt",
    "tests/encrypted.zip"
]

ADVANCED_FILES = [  # These hold different data, or load in different ways
    "tests/node-in-node.pyn"
]


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class FileLoading(unittest.TestCase):
    def test_basic_load(self):
        for item in BASIC_FILES:
            with self.subTest(msg=str(item)):
                db = Node(item)

    def test_blank_load(self):
        db = Node()
        self.assertEqual(db(), {})

    def test_serialized_load(self):
        db = Node('tests/serialized.pyn')
        self.assertTrue(True)

    def test_reload_from_file(self):
        db = Node('tests/sample_reloadme.txt')
        with open('tests/sample_reloadme.txt', 'w') as file:
            file.write("{'a': 2}")
            file.truncate()
        db.file.reload()
        self.assertEqual(db(), {'a': 2})
        with open('tests/sample_reloadme.txt', 'w') as file:  # Reset
            file.write("{'a': 1}")
            file.truncate()

    def test_load_new_file(self):
        for ext in EXTENSIONS:
            with self.subTest(msg=ext):
                db = Node(f'tests/newdb.{ext}')
                os.remove(f'tests/newdb.{ext}')

    def test_encryption(self):
        for item in ENCRYPTED_FILES:
            with self.subTest(msg=str(item)):
                db = Node(item, password="testing")

    def test_encryption_newfile(self):
        db = Node('tests/newdb.enc', filetype='pyn', password='pyntree', salt=os.urandom(32))
        os.remove('tests/newdb.enc')


class FileReading(unittest.TestCase):
    def setUp(self):
        self.databases = [Node(i) for i in BASIC_FILES]
        self.databases.append(Node(ADVANCED_FILES[0]).data())
        self.databases += [Node(i, password='testing') for i in ENCRYPTED_FILES]

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

    def test_star_args(self):
        db = Node(BASIC_FILES[0])
        self.assertEqual(str(db.get('a', 'b')), "[1, Node({'c': 2})]")  # str(list) -> list(*repr(item)) for some reason

    def test_serialized_read(self):
        db = Node('tests/serialized.pyn')
        self.assertEqual(db.time(), dt(2023, 3, 6, 21, 2, 8, 550653))


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

    def test_star_args(self):
        db = Node({'a': 1, 'b': 15})
        with self.subTest(msg="Without creation"):
            db.set('a', 'b', 2)
            self.assertEqual(db.a(), 2)
            self.assertEqual(db.b(), 2)
        with self.subTest(msg="With creation"):
            db.set('a', 'b', 'c', True)
            for item in 'abc':
                self.assertTrue(db.get(item)())

    def test_alternate_set(self):
        db = Node({})
        db.z = 1
        # noinspection PyCallingNonCallable
        self.assertEqual(db.z(), 1)


# noinspection PyMethodMayBeStatic
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

    def test_serialized_save(self):
        db = Node({'time': dt.now()})
        db.save('tests/testing_serialization.pyn')
        os.remove('tests/testing_serialization.pyn')
        self.assertTrue(True)

    def test_encrypted_save(self):
        for ext in EXTENSIONS:
            with self.subTest(msg=ext):
                db = Node({'a': 1, 'b': {'c': 2}}, password='testing')
                db.save(f'tests/newdb.{ext}')
                os.remove(f'tests/newdb.{ext}')

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
        db.save(filename='tests/testing_savedict.json')
        self.assertEqual(Node('tests/testing_savedict.json')(), {'a': 'b'})
        os.remove('tests/testing_savedict.json')

    def test_dictionary_filename_alt(self):
        db = Node({'a': 'b'})
        db.switch_to_file('tests/testing_savedict.json')
        db.save()
        self.assertEqual(Node('tests/testing_savedict.json')(), {'a': 'b'})
        os.remove('tests/testing_savedict.json')

    def test_node_in_node(self):
        db = Node({'a': Node()})
        db.save('tests/testing_save_NiN.pyn')
        os.remove('tests/testing_save_NiN.pyn')

    def test_save_after_password_set(self):
        db = Node({'a': 'b'})
        db.file.password = 'testing'
        db.save('tests/testing_encrypted_setpwd.pyn')
        self.assertEqual(Node('tests/testing_encrypted_setpwd.pyn', password='testing')(), {'a': 'b'})
        os.remove('tests/testing_encrypted_setpwd.pyn')

    def test_save_after_password_change(self):
        db = Node('tests/testing_encrypted_changepwd.pyn', password='testing1')
        db.a = 'b'
        db.file.password = 'testing2'
        db.save('tests/testing_encrypted_changepwd.pyn')
        self.assertEqual(Node('tests/testing_encrypted_changepwd.pyn', password='testing2')(), {'a': 'b'})
        os.remove('tests/testing_encrypted_changepwd.pyn')


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

    def test_star_args(self):
        db = Node({'a': '', 'b': '', 'c': ''})
        db.delete(*'abc')
        self.assertEqual(db(), {})


class FileScanningTests(unittest.TestCase):
    def setUp(self):
        self.db = Node({"val1": 'h', "val2": 'b'})

    def test_has(self):
        self.assertTrue(self.db.has("val1"))

    def test_has_star_args(self):
        self.assertTrue(self.db.has("val1", "val2"))

    def test_values(self):
        self.assertEqual(self.db._values, ["val1", "val2"])

    def test__str__(self):
        self.assertEqual(str(self.db), str({"val1": 'h', "val2": 'b'}))

    def test__str__final(self):
        self.assertEqual(str(self.db.val1), "h")

    def test__repr__(self):
        self.assertEqual(repr(self.db), "Node(" + str({"val1": 'h', "val2": 'b'}) + ")")

    def test__repr__final(self):
        self.assertEqual(repr(self.db.val1), "'h'")

    def test_name_layer_0_data(self):
        self.assertEqual(self.db._name, 'None')

    def test_name_layer_0_file(self):
        self.assertEqual(Node('tests/sample.txt')._name, 'tests/sample.txt')

    def test_name_layer_1(self):
        self.assertEqual(self.db.val1._name, 'val1')

    def test_get_children(self):
        self.assertEqual(self.db._children[0](), 'h')

    def test_where(self):
        db = Node({
            "a": {
                "b": 2
            },
            "b": {
                "b": 2
            },
            "c": {
                "b": 3
            }
        })
        matches = db.where(b=2)
        self.assertEqual(len(matches), 2)
        self.assertTrue(type(matches[0]) is Node)
        self.assertEqual(str(matches[0]), str({"b": 2}))

    def test_containing(self):
        db = Node({
            "a": {
                "h": 2
            },
            "b": {
                "b": 2
            },
            "c": {
                "b": 3
            }
        })
        matches = db.containing('b')
        self.assertEqual(len(matches), 2)
        self.assertTrue(type(matches[0]) is Node)
        self.assertEqual(str(matches[0]), str({"b": 2}))

    def test_getdict(self):
        db = Node({'a': {'b': {'c': 1}}})
        self.assertEqual(str(dict(db)), str({'a': {'b': {'c': 1}}}))


# noinspection PyCallingNonCallable
class ArithmeticTests(unittest.TestCase):
    def test_iadd_int(self):
        db = Node()
        db.a = 1
        db.a += 1
        self.assertEqual(db.a(), 2)

    def test_iadd_str(self):
        db = Node()
        db.a = 'a'
        db.a += 'bc'
        self.assertEqual(db.a(), 'abc')

    def test_isub_int(self):
        db = Node()
        db.a = 1
        db.a -= 1
        self.assertEqual(db.a(), 0)

    def test_imul_int(self):
        db = Node()
        db.a = 2
        db.a *= 3
        self.assertEqual(db.a(), 6)

    def test_imul_str(self):
        db = Node()
        db.a = 'a'
        db.a *= 3
        self.assertEqual(db.a(), 'aaa')

    def test_cmp(self):
        db = Node()
        db.a = 1
        db.b = 2
        self.assertTrue(db.a < db.b)
        self.assertTrue(db.a <= db.b)
        self.assertFalse(db.a > db.b)
        self.assertFalse(db.a >= db.b)
        self.assertFalse(db.a == db.b)
        self.assertTrue(db.a != db.b)

    def test_nested_operations(self):
        db = Node({'a': {'b': 1}})
        db.a.b += 1
        self.assertEqual(db.a.b(), 2)


if __name__ == '__main__':
    unittest.main()
