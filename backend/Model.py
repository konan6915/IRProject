
class Model:
    def __init__(self, input_tuple=None, output_tuple=None, args_list=None):
        if args_list is None:
            args_list = [None]
        self.input_tuple = input_tuple
        self.output_tuple = output_tuple
        self.args_list = args_list

    def set_args_list(self, args_list):
        self.args_list = args_list

    def process(self, input_data=None, args=None):
        raise NotImplementedError()
