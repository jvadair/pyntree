class Error:
    class NameNotFound(Exception):
        pass

    class FileNameUnset(Exception):
        pass

    class NotANode(Exception):
        pass

    class EncryptionNotAvailable(Exception):
        pass