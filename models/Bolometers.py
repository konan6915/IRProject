import numpy as np
from numpy import exp
from scipy.constants import c, h, k

import params
from backend.Model import Model


class Bolometers(Model):
    def __init__(self, Tcam=params.Tcam, size_active=params.resolution, size_boundary=params.size_boundary,
                 size_blind=params.size_blind,
                 lambd=params.lambd, phi=params.phi, area=params.area, omega=params.omega,
                 R_ambient_med=params.R_ambient_med, R_ambient_tol=params.R_ambient_tol,
                 G_thermal_med=params.G_thermal_med, G_thermal_tol=params.G_thermal_tol,
                 C_thermal_med=params.C_thermal_med, C_thermal_tol=params.C_thermal_tol,
                 T_ambient=params.T_ambient, TCR=params.TCR, seed=123):

        self.Tcam = Tcam
        self.size_active_h = size_active[0]
        self.size_active_v = size_active[1]
        self.size_boundary_t = size_boundary[0]
        self.size_boundary_b = size_boundary[1]
        self.size_boundary_l = size_boundary[2]
        self.size_boundary_r = size_boundary[3]
        self.size_blind_t = size_blind[0]
        self.size_blind_b = size_blind[1]
        self.size_blind_l = size_blind[2]
        self.size_blind_r = size_blind[3]

        self.lambd_lower = lambd[0]
        self.lambd_upper = lambd[1]
        self.phi_r = phi[0]
        self.phi_s = phi[1]
        self.area = area
        self.omega = omega

        self.size_total_h = self.size_active_h + self.size_boundary_l + self.size_boundary_r \
                            + self.size_blind_l + self.size_blind_r
        self.size_total_v = self.size_active_v + self.size_boundary_t + self.size_boundary_b \
                            + self.size_blind_t + self.size_blind_b

        super().__init__(input_tuple={"P_distribution": size_active},
                         output_tuple={"P_total": (self.size_total_h, self.size_total_v),
                                       "R_ambient": (self.size_total_h, self.size_total_v),
                                       "G_thermal": (self.size_total_h, self.size_total_v),
                                       "C_thermal": (self.size_total_h, self.size_total_v),
                                       "R0": (self.size_total_h, self.size_total_v),
                                       "tau": (self.size_total_h, self.size_total_v)})

        self.R_ambient_med = R_ambient_med
        self.R_ambient_dev = R_ambient_med * R_ambient_tol
        self.G_thermal_med = G_thermal_med
        self.G_thermal_dev = G_thermal_med * G_thermal_tol
        self.C_thermal_med = C_thermal_med
        self.C_thermal_dev = C_thermal_med * C_thermal_tol
        self.T_ambient = T_ambient
        self.E_activation = -(TCR * k * self.T_ambient ** 2)

        self.seed = seed

        # Model is parametirized using camera's temperatures, store it into arguments
        # for caching mechanism
        super().set_args_list([Tcam])

    def _get_temperature_power_component(self, T):
        L = 0.0
        it = np.arange(1, 101, 1)
        x1 = (h * c) / (k * T * self.lambd_lower)
        x2 = (h * c) / (k * T * self.lambd_upper)

        '''Integration of Planks radiation function in wave length of interest band
           "BLACKBODY RADIATION FUNCTION" Chang, Rhee 1984'''
        for n in it:
            B1 = (2 * k ** 4 * T ** 4) / (h ** 3 * c ** 2) * exp(-n * x1) * (
                        x1 ** 3 / n + (3 * x1 ** 2) / n ** 2 + (6 * x1) / n ** 3 + 6 / n ** 4)
            B2 = (2 * k ** 4 * T ** 4) / (h ** 3 * c ** 2) * exp(-n * x2) * (
                        x2 ** 3 / n + (3 * x2 ** 2) / n ** 2 + (6 * x2) / n ** 3 + 6 / n ** 4)
            L += (B2 - B1)

        '''Calculating IR power that impignes on one pixel sensetive area, if it is
           located in the center of sensor'''
        return L * np.cos(self.phi_s) * self.area * np.cos(self.phi_r) * self.omega

    def _get_physical_parameters(self):
        size = (self.size_total_v, self.size_total_h)
        rng = np.random.default_rng(self.seed)
        R_ambient = rng.normal(loc=self.R_ambient_med, scale=self.R_ambient_dev, size=size)
        G_thermal = rng.normal(loc=self.G_thermal_med, scale=self.G_thermal_dev, size=size)
        C_thermal = rng.normal(loc=self.C_thermal_med, scale=self.C_thermal_dev, size=size)

        tau = C_thermal / G_thermal
        R0 = R_ambient / np.exp(self.E_activation / (k * self.T_ambient))

        return R_ambient, G_thermal, C_thermal, R0, tau

    def process(self, input_data=None, args=None):
        """ Camera temperatures as a parameter """
        if args:
            Tcam = args
        else:
            Tcam = self.Tcam

        P_temperature = self._get_temperature_power_component(Tcam)
        P_active = input_data["P_distribution"]

        P_pixels = np.zeros((self.size_total_v, self.size_total_h))

        active_start_h = self.size_boundary_l + self.size_blind_l
        active_stop_h = self.size_total_h - 1 - 1 - self.size_boundary_r + self.size_blind_r
        active_start_v = self.size_boundary_t + self.size_blind_t
        active_stop_v = self.size_total_v - 1 - 1 - self.size_boundary_b + self.size_blind_b
        P_pixels[active_start_v:active_stop_v, active_start_h:active_stop_h] = P_active
        P_total = P_pixels + P_temperature

        R_ambient, G_thermal, C_thermal, R0, tau = self._get_physical_parameters()

        return {
            "P_total": P_total,
            "R_ambient": R_ambient,
            "G_thermal": G_thermal,
            "C_thermal": C_thermal,
            "R0": R0,
            "tau": tau}
