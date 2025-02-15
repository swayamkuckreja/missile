"""
@time: 23:52 02-02-2025
@author: kuckreja
@purpose: Model aerodynamics of guided missile
@source: "Tactical Missile Design - Eugene L. Fleeman"
"""

import numpy as np
from requirements import *
from baseline import BaselineMissile

# Assume Standard SI units and type float unless explicity stated!

#-------------------------------------------------
# 2.1) Diameter Tradeoff
#-------------------------------------------------
# Finds drag force [N] (minimise)
def drag_force(C_D, dyn_pressure, diameter_body): 
    return 0.785 * C_D * dyn_pressure * diameter_body ** 2 

# Finds threat detection range [m] (maximise)
def detection_range(temp_receiver, bandwidth, noise_factor, radar_cross_section_target,
                    n: int, freq_transmitter, loss_factor_transmitter,
                    signal_to_noise_target_detection, power_transmitter, diameter_antenna):
    c = 3e8  # light [m/s]
    k = 1.38e-23  # Boltzmann [J/K]
    wavelength = c / freq_transmitter
    Pr = k * temp_receiver * bandwidth * noise_factor
    numerator = np.pi * radar_cross_section_target * (n ** 0.75)
    denominator = 64 * (wavelength ** 2) * Pr * loss_factor_transmitter * signal_to_noise_target_detection
    return ((numerator / denominator) ** 0.25) * (power_transmitter ** 0.25) * diameter_antenna

# Finds the missile bodies first eigen frequency [Hz] (should > 2x actuator frequency!)
# NOTE: Use imperical units 
def body_first_eigenfreq(E_avg_body, t_avg_body, fineness_ratio_body, weight_body):
    """
    Body length-weighted stiffness [psi]
    Body length-weighted thickness [inches]
    Length to diameter ratio [-]
    Weight of the body [lbs]
    """
    stiffness_term = E_avg_body * t_avg_body
    inertia_term = weight_body * fineness_ratio_body
    return (18.75 * (stiffness_term / inertia_term) ** 0.5) / (2 * np.pi)

#-------------------------------------------------
# 2.2) Nose Fineness Ratio
#-------------------------------------------------
# Some example numbers
fineness_ratio_nose_HIGH = 5  # (low drag and radar cross section)
fineness_ratio_nose_LOW = 0.5  # (high propellant and good sensing)
fineness_ratio_nose_MEDIUM = 2  # (compramised 'jack of all trates')




if __name__ == '__main__':
    # Verification: Unit tests
    # Detection range test (passing)
    det_range = detection_range(temp_receiver=290, bandwidth=1e6, noise_factor=5,
                                radar_cross_section_target=10, n=100, freq_transmitter=10e9,
                                loss_factor_transmitter=5, signal_to_noise_target_detection=10,
                                power_transmitter=1000, diameter_antenna=0.2032)
    print(f"Maximum detection range: {det_range} meters")

    # First eigen mode test (passing)
    body_eigenmode_one = body_first_eigenfreq(E_avg_body=19.5 * 10**6, t_avg_body=0.12,
                                              fineness_ratio_body=18, weight_body=500)
    print(f"Body first eigenfrequency: {body_eigenmode_one} Hz")
