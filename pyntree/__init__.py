from pyntree.file import File
from pyntree.errors import Error
from typing import Union, Any, List


class Node(object):
    # noinspection PyShadowingNames
    def __init__(
            self,
            file: Union[File, str, dict] = None,
            path: list = None,
            **file_args
    ) -> None:

        """
        A Node is a class which acts as a dynamic getter and setter which remembers its position relative to other
        elements. Data is modified using the __gettattr__ and __setattr__ magic methods, which also have aliases
        named "set" and "get". A Node which represents the entirety of the data is called a "root node",
        and Nodes which are spawned by it are referred to as "child nodes".

        Make sure to look at the documentation for the File class to understand the arguments available for **file_args

        :param file: The File object from the root Node is further passed to children.
        :param path: The location of the data within the hierarchy
        :param file_args: additional keyword arguments to be passed to  a file object (intended for root nodes)
        """
        self.__dict__['path'] = [] if not path else path  # __dict__ is used because __setattr__ has been overridden
        # Set and get methods for easy/standard access to the dunder methods
        self.__dict__['get'] = self.__getattr__
        self.__dict__['set'] = self.__setattr__
        if file is None:  # Allows for creating a node like so: Node()
            file = {}
        self.__dict__['file'] = file if type(file) is File else File(file, **file_args)
        self.__dict__['save'] = self.file.save
        self.__dict__['switch_to_file'] = self.file.switch_to_file

    def __getattr__(self, name, *names) -> Union['Node', List['Node']]:
        """
        Retrieves Nodes with the requested names, even if that name is already a class attribute.
        You must specify at least 1 name.
        :param name: The first, required name
        :param names: Any additional names
        :return: The Node object for the name you specified
        """
        names = (name,) + names
        requested = []
        for name in names:
            try:
                if name not in self():  # If key doesn't exist
                    raise AttributeError(
                        f"<RootNode>.{'.'.join(self.path)}{'.' if self.path else ''}{name} does not exist")
            except TypeError:  # Throw something more descriptive/accurate
                raise Error.NotANode(f"<RootNode>.{'.'.join(self.path)} is {type(self()).__name__}, not Node.")
            requested.append(Node(file=self.file, path=self.path + [name]))
        return requested if len(requested) > 1 else requested[0]  # Don't return a list if only 1 name specified

    def __setattr__(self, *args) -> None:  # We must use *args and split the list to make this work
        """
        :param args: The names to modify, followed by the value to set them to
        :return:
        """
        args = list(args)
        if not len(args) >= 2:
            raise TypeError("You must specify at least 1 name and a value for the set method.")
        value = args.pop(-1)
        names = args  # All arguments but last are names
        target = self()  # Calls the __call__ function to get the target (which is a mutable value)
        for name in names:
            target[name] = value  # Sets the final target to the desired value
        if self.file.autosave:
            self.file.save()

    def __call__(self) -> Any:
        if self.path:  # Root node will have a path equal to []
            target = self.file.data.get(self.path[0])
            for i in self.path[1:]:  # Iter over all but first
                target = target.get(i)
        else:
            target = self.file.data
        return target

    # Representation methods
    def __str__(self):
        """
        :return: A string representation of the data contained within the Node
        """
        return str(self())

    def __repr__(self):
        """
        :return: A string containing the code necessary to replicate the Node
        """
        if type(self()) is dict:
            return f'Node({self()})'
        else:
            return repr(self())

    def __getstate__(self):  # When pickled
        trim = self.file  # The File object is what contains all the relevant information, even for pure data Nodes.
        if trim.file:
            # Remove the '_io.BufferedRandom' object which can't be serialized
            trim.file.close()
            trim.file = None
        # Note: The path information will be discarded. This is intentional.
        return trim

    def __setstate__(self, state):
        file = state
        if file.name:  # If there is a filename
            file.switch_to_file(file.name)  # Reload the file object
        self.__init__(file)

    def __iter__(self):
        for k in self._values:
            v = self.get(k)()
            yield k, v

    def __getitem__(self, item):
        return self.get(item)()

    # Custom operations
    def delete(self, *names) -> None:
        """
        Deletes the Node or the specified child Node
        :param names: If set, deletes the specified child Nodes, otherwise the function will delete this Node.
        :return:
        """
        if names:
            target = self()
            for name in names:
                target.pop(name)
        else:
            if self.path:  # Root node will have a path equal to []
                target = self.file.data
                for i in self.path[0:-1]:  # Iter over all but last
                    target = target.get(i)
                target.pop(self.path[-1])
            else:
                self.file.data = {}

    def has(self, *items) -> bool:
        """
        Check if the specified child Node exists
        :param items: The items to check for
        :return:
        """
        for item in items:
            return True if item in self._values else False

    def where(self, **kwargs) -> List['Node']:
        """
        :param kwargs: Return all children with a child <kwarg> and its corresponding value
        :return: A list of Nodes matching the criteria
        """
        matches = []
        for name in self._values:
            child = self.get(name)
            for kwarg in kwargs:
                if child.has(kwarg) and child.get(kwarg)() == kwargs[kwarg]:  # Evaluated left to right, so no error
                    matches.append(child)

        return matches

    def containing(self, *args) -> List['Node']:
        """
        :param args: Return all children with children named <*args>
        :return: A list of Nodes matching the criteria
        """
        matches = []
        for name in self._values:
            child = self.get(name)
            for arg in args:
                if child.has(arg):
                    matches.append(child)

        return matches

    # Properties
    @property
    def _values(self) -> List[str]:
        """
        Returns the list of child Nodes this Node contains
        :return:
        """
        return list(self().keys())

    @property
    def _children(self) -> List['Node']:
        return [self.get(n) for n in self._values]

    @property
    def _name(self) -> str:
        """
        :return: The name of the child Node, or the filename for root Nodes, or 'None' for root nodes without a filename
        """
        if self.path:
            return self.path[-1]
        else:  # "None" for pure-data Nodes
            return str(self.file.name)

    @property
    def _val(self) -> Any:
        """
        :return: The Node's value, as it would be returned by __call__
        """
        return self()

    # Arithmetic operations - only for child Nodes since the operations don't work on dictionaries anyways
    def __iadd__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] += other
        return self()

    def __isub__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] -= other
        return self()

    def __imul__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] *= other
        return self()

    def __itruediv__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] /= other
        return self()

    def __ifloordiv__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] //= other
        return self()

    def __imod__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] %= other
        return self()

    def __ipow__(self, other):
        self.file.get_nested(*self.path[:-1])[self.path[-1]] **= other
        return self()

    # Comparison methods (<, >, <=, >=, ==, !=)
    def __lt__(self, other):
        return True if self() < other() else False

    def __le__(self, other):
        return True if self() <= other() else False

    def __gt__(self, other):
        return True if self() > other() else False

    def __ge__(self, other):
        return True if self() >= other() else False

    def __eq__(self, other):
        return True if self() == other() else False

    def __ne__(self, other):
        return True if self() != other() else False

