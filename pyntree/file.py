from os.path import exists
from pyntree.errors import Error
# from pickle import HIGHEST_PROTOCOL, UnpicklingError
# from pickle import load as load_pickle
# from pickle import dump as save_pickle
# from pickle import dumps as pickle_to_string
# from json import load as load_json
# from json import dumps as save_json
# from json.decoder import JSONDecodeError
# from pyndb.encryption import encrypt, decrypt, InvalidToken


class File:
    def __init__(self, data, filetype='txt', save_on_close=False):
        """
        Load a file for use with a Node object.

        Filetype options:

        - pyn (Serialized data) (default)
        - txt (plain text data)
        - json

        :param data: The filename or dictionary object
        :param filetype: The type of data stored/to store
        :param save_on_close: Whether to save the file when this object is destroyed
        """
        if filetype is None:
            filetype = 'pyn'  # Default filetype
        self.filetype = filetype
        self.save_on_close = save_on_close
        if type(data) is str:  # Helps a Data class work
            if not exists(data):
                open(data, 'w').close()  # Create file if it doesn't exist
            self.file = open(data, 'r+')
            self.data = self.read_data()  # Not to be confused with the data parameter
        else:
            self.data = data

    def read_data(self):
        self.file.seek(0)
        return eval(self.file.read())

    def switch_to_file(self, filename):
        """
        Closes the old file object (if it exists) and replaces it with a new one.
        :param filename: The name of the file to switch to
        :return:
        """
        if self.file:  # Close open file, unless pure data was loaded
            self.file.close()
        if not exists(filename):
            open(filename, 'w').close()  # Create file if it doesn't exist
        self.file = open(filename, 'r+')

    def save(self, filename=None):
        """
        Saves the data to the file
        :param filename: Save to a different filename
        """
        if not self.file and not filename:
            raise Error.FileNameUnset(
                "You have not specified a filename for this data."
                "Try setting the filename parameter or use switch_to_file."
            )
        file = self.file if not filename else open(filename, 'w')
        file.seek(0)
        file.write(str(self.data))
        file.truncate()
        if filename:
            file.close()  # Files not controlled by Nodes should be closed

    def __del__(self):
        if 'file' in self.__dict__.keys():  # If file attribute was set
            if self.save_on_close:
                self.save()
            self.file.close()
