from pyntree.file import File
from pyntree.errors import Error
from typing import Union


class Node:
    def __init__(
                 self,
                 file: Union[File, str, dict] = None,
                 path: list = None,
                 autosave: bool = False,
                 **file_args
                 ):
        """
        A Node is a class which acts as a dynamic getter and setter which remembers its position relative to other elements.
        Data is modified using the __gettattr__ and __setattr__ magic methods, which also have aliases named "set" and "get".
        A Node which represents the entirety of the data is called a "root node", and Nodes which are spawned by it are referred to as "child nodes".
        :param file: The File object from the root Node is further passed to children.
        :param path: The location of the data within the hierarchy
        :param autosave: This should be set by the root Node, but can be tweaked for each node if desired. All nodes spawned beneath this one will copy its autosave value.
        :param file_args: additional keyword arguments to be passed to a file object (intended for root nodes)
        """
        self.__dict__['path'] = [] if not path else path  # __dict__ is used because __setattr__ has been overridden
        # Set and get methods for easy/standard access to the dunder methods
        self.__dict__['get'] = self.__getattr__
        self.__dict__['set'] = self.__setattr__
        self.__dict__['file'] = file if type(file) is File else File(file, **file_args)

    def __getattr__(self, name):
        """
        Retrieves the Node with the requested name, even if that name is already a class attribute
        :param name:
        :return: The Node object for the name you specified
        """
        if name not in self():  # If key doesn't exist
            raise Error.NameNotFound(f"<RootNode>.{'.'.join(self.path)}{'.' if self.path else ''}{name} does not exist")
        return Node(file=self.file, path=self.path + [name])

    def __setattr__(self, name, value):
        target = self()  # Calls the __call__ function to get the target (which is a mutable value)
        target[name] = value  # Sets the final target to the desired value
        if self.file.autosave:
            self.file.save()

    def __call__(self, *args, **kwargs):
        if self.path:  # Root node will have a path equal to []
            target = self.file.data.get(self.path[0])
            for i in self.path[1:]:  # Iter over all but first
                target = target.get(i)
        else:
            target = self.file.data
        return target

    def delete(self, name=''):
        """
        Deletes the Node or the specified child Node
        :param name: If set, deletes a child Node, otherwise the function will delete this Node.
        :return:
        """
        if name:
            target = self()
            target.pop(name)
        else:
            if self.path:  # Root node will have a path equal to []
                target = self.file.data
                for i in self.path[0:-1]:  # Iter over all but last
                    target = target.get(i)
                target.pop(self.path[-1])
            else:
                self.file.data = {}