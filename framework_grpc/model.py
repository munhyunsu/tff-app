class Model():
    def __init__(self, **kwargs):
        raise NotImplementedError

    def get_parameter(self):
        raise NotImplementedError

    def get_model(self):
        raise NotImplementedError

    def feed_train_result(self, result):
        raise NotImplementedError

