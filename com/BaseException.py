

class BaseException(Exception):
    def __init__(self, str_length):
        super().__init__()
        self.str_length = str_length