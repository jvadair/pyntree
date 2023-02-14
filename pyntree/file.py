from os.path import exists
from pyntree.errors import Error
import compress_pickle as pickle
# from json import load as load_json
# from json import dumps as save_json
# from json.decoder import JSONDecodeError
# from pyndb.encryption import encrypt, decrypt, InvalidToken

EXTENSIONS = {
    "txt": "txt",
    "pyn": "pyn",
    "pyndb": "pyn",
    **pickle.get_registered_extensions()
}


class File:
    def __init__(self, data, filetype=None, autosave=False, save_on_close=False):
        """
        Load a file for use with a Node object.

        Filetype options:

        - pyn (Serialized data) (default)
        - txt (plain text data)
        - json

        :param data: The filename or dictionary object
        :param filetype: The type of data stored/to store
        :param autosave: Save the file when Nodes are updated
        :param save_on_close: Whether to save the file when this object is destroyed (irrelevant if autosave = True)
        """
        if filetype is None:  # Infer from extension
            filetype = 'pyn'  # Default filetype
            if type(data) is str:
                if len(data.rsplit('.')) > 1:  # If filename has extension
                    ext = data.rsplit('.')[-1]
                    if ext in EXTENSIONS.keys():  # And it's a valid one
                        filetype = EXTENSIONS[ext]  # Then use that
        self.filetype = filetype
        self.autosave = autosave
        self.save_on_close = save_on_close
        if type(data) is str:  # Helps a Data class work
            if not exists(data):
                open(data, 'w').close()  # Create file if it doesn't exist
            if filetype == 'pyn' or filetype in pickle.get_known_compressions():
                self.file = open(data, 'rb+')
            else:
                self.file = open(data, 'r+')
            self.data = self.read_data()  # Not to be confused with the data parameter
        else:
            self.data = data

    # noinspection PyTypeChecker
    def read_data(self):
        self.file.seek(0)
        if self.filetype == 'pyn':
            return pickle.loads(self.file.read(), None)
        elif self.filetype == 'txt':
            return eval(self.file.read())
        elif self.filetype in pickle.get_known_compressions():
            return pickle.loads(self.file.read(), self.filetype)

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
