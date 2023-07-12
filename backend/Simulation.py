
class Simulation:
    def __init__(self, models):
        self.models = models

    def is_compatible(self, input_model, output_model):
        for key in output_model.input_tuple:

            if key not in input_model.output_tuple:
                print("ERROR: Type mismatch for '"
                      + type(input_model).__name__ + "' and '"
                      + type(output_model).__name__ + "' key '"
                      + key + "' is not found")
                return False

            if input_model.output_tuple[key] != output_model.input_tuple[key]:
                print("ERROR: Shape mismatch for '"
                      + key + "' key in '"
                      + type(input_model).__name__ + "' and '"
                      + type(output_model).__name__ + "'")
                return False

        return True

    def process(self, index=0, input_data=None):
        output_data = []

        if index >= len(self.models):
            return input_data

        for args in self.models[index].args_list:
            print("Executing: " + type(self.models[index]).__name__)

            intermediate_data = self.models[index].process(input_data, args)

            result = self.process(index + 1, intermediate_data)
            output_data.append(result)

        return output_data
