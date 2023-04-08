class Error:
    class FileNameUnset(Exception):
        pass

    class NotANode(Exception):
        pass

    class EncryptionNotAvailable(Exception):
        pass
