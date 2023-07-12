import sys
import numpy as np

sys.path.append('../backend')
from Model import Model
import params


class Optics(Model):
    def __init__(self, resolution=params.resolution, focal_length=params.focal_length, pitch=params.pitch):
        super().__init__(input_tuple={"P": (1,)}, output_tuple={"P_distribution": resolution})
        self.pixsize_h, self.pixsize_v = resolution
        self.focal_length = focal_length
        self.pitch = pitch

    def process(self, input_data=None, args=None):
        if input_data == None:
            raise ValueError("Input data cannot be None")

        ''' Define array for saving distribution factor results for each pixel'''
        distrib_fact = np.ones((self.pixsize_v, self.pixsize_h))

        ''' Define variables for iterations over one quadrant of the sensor'''
        row_half = self.pixsize_v / 2
        col_half = self.pixsize_h / 2
        half_pitch = self.pitch / 2
        pitch = self.pitch
        fl = self.focal_length
        row = np.arange(0, int(row_half), 1)
        col = np.arange(0, int(col_half), 1)
        P = input_data["P"]

        ''' Calculate IR power distribution factor'''
        for r in row:
            row1 = int(row_half - 1 - r)
            row2 = int(row_half + r)

            for c in col:
                a = np.sqrt((half_pitch + r * pitch) ** 2 + (half_pitch + c * pitch) ** 2)
                b = np.sqrt(a ** 2 + fl ** 2)
                fact = (fl / b) ** 4
                col1 = int(col_half + c)
                col2 = int(col_half - 1 - c)

                # print(col1, col2)

                distrib_fact[row1][col1] = fact  # 1st quadrant
                distrib_fact[row2][col1] = fact  # 2nd quadrant
                distrib_fact[row2][col2] = fact  # 3rd quadrant
                distrib_fact[row1][col2] = fact  # 4th quadrant

        ''' Define iterative rows for IR power distribution calculation'''
        row_pd = np.arange(0, self.pixsize_v, 1)
        col_pd = np.arange(0, self.pixsize_h, 1)

        ''' Define array for saving power distribution calculated values '''
        pow_distrib = np.ones((self.pixsize_v, self.pixsize_h))

        ''' Calculating IR power distribution over sensor area '''
        for r in row_pd:
            for co in col_pd:
                pow_distrib[r][co] = distrib_fact[r][co] * P
        return {"P_distribution": pow_distrib}
