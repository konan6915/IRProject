import numpy as np

import sys

sys.path.append('../backend')
from Model import Model
import params


class NUC(Model):
    def __init__(self, coef_a, coef_b, resolution=params.resolution, adc_resolution=params.adc_resolution,
                 visualize=False):
        self.size_h = resolution[0]
        self.size_v = resolution[1]
        self.coef_a = coef_a
        self.coef_b = coef_b
        self.adc_resolution = adc_resolution

        super().__init__(
            input_tuple={
                "ADC": (self.size_h, self.size_v)
            },
            output_tuple={
                "ADC": (self.size_h, self.size_v)
            }
        )

    @staticmethod
    def calculate_coefs(frames, temps, fpart_width=params.nuc_fpart):
        frame0 = frames[0]
        frame1 = frames[1]
        temp0 = temps[0]
        temp1 = temps[1]
        nuc_a = (temp0 - temp1) / (frame0 - frame1)
        nuc_b = (temp1 * frame0 - temp0 * frame1) / (frame0 - frame1)
        if fpart_width:
            step = 2 ** -fpart_width
            nuc_a = np.round(nuc_a / step) * step
            nuc_b = np.round(nuc_b / step) * step
        return nuc_a, nuc_b

    def process(self, input_data=None, args=None):
        corr = input_data['ADC'] * self.coef_a + self.coef_b
        adc_max = 2 ** self.adc_resolution - 1
        corr_sat = np.where(corr < adc_max, corr, adc_max)
        return {"ADC": corr_sat}
