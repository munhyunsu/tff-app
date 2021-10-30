class Model():
    def __init__(self, **kwargs):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def get_compile(self):
        raise NotImplementedError

    def get_label(self):
        raise NotImplementedError

    def get_architecture(self):
        raise NotImplementedError

    def get_parameter(self):
        raise NotImplementedError
