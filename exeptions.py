
class DirectoryNotFound(Exception):
    def __init__(self, message, info):
        super().__init__(message)
        self.info = info

