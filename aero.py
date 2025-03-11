"""
@time: 23:52 02-02-2025
@author: kuckreja
@purpose: Model aerodynamics of guided missile
@source: "Tactical Missile Design - Eugene L. Fleeman"
"""

import numpy as np
from requirements import *
from baseline import BaselineMissile

# Assume Standard SI units and type: float unless explicity stated!

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

# Determines current drag coefficient c_d
def drag_coef(mach_num, fineness_ratio_body, fineness_ratio_nose, blunt_nose: bool,
              powered_flight: bool, dyn_pressure, length_body, diameter_body_base, area_nozzle_exit):
    # c_d(total) = c_d(wave) + c_d(skin fric) + c_d(base)
    def drag_coef_wave(mach_num, fineness_ratio_nose, blunt_nose):
        if mach_num >= 1:
            if blunt_nose == False:  # So a sharp/pointy nose edge
                c_d_wave = 3.6/((fineness_ratio_nose  * (mach_num - 1)) + 3)
            elif blunt_nose == True:  # So a slighty rounded nose edge TODO: Finish this part if time (pg. 24)
                c_d_wave = 3.6/((fineness_ratio_nose  * (mach_num - 1)) + 3)
        elif mach_num < 1:
            c_d_wave = 0
        return c_d_wave
    c_d_wave = drag_coef_wave(mach_num, fineness_ratio_nose)
    
    def drag_coef_skin(fineness_ratio_body, mach_num, dyn_pressure, length_body):
        return 0.053 * fineness_ratio_body * (mach_num/(dyn_pressure * length_body))**0.2
    c_d_skin = drag_coef_skin(fineness_ratio_body, mach_num, dyn_pressure, length_body)

    def drag_coef_base(mach_num, powered_flight, diameter_body_base):
        if powered_flight:
            if mach_num >= 1:
                return 0.25/mach_num
            elif mach_num < 1:
                return 0.12 + 0.13 * mach_num * mach_num
        elif not powered_flight:
            powered_reduction_factor = 1 - (area_nozzle_exit / (np.pi * (diameter_body_base/2)**2))
            if mach_num >= 1:
                return  powered_reduction_factor * (0.25/mach_num)
            elif mach_num < 1:
                return powered_reduction_factor * (0.12 + 0.13 * mach_num * mach_num)
    c_d_base = drag_coef_base(mach_num, powered_flight, diameter_body_base)
    
    return c_d_wave + c_d_skin + c_d_base

#-------------------------------------------------
# 2.3) Boattailing
#-------------------------------------------------
# Whether or not to taper the back of the missile. Reduces drag by 50 percent in subsonic
def boattailing_ratio(mach_cruise):
    if mach_cruise < 1:
        return 0.5  # d_boattail/d_ref(body) = 0.4 -> 0.8 typical (lower the better)
    elif mach_cruise >= 1:
        return 1  # No tapering for supersonic as flow sep -> increased drag

#-------------------------------------------------
# 2.4) Lifting Body
#-------------------------------------------------
# Magnitude of body normal force coefficient C_n_body (if need see sec 2.4 for C_n_alpha_body formula)
def normal_force_coef_body(major_minor_axis_ratio_body, fineness_ratio_body, angle_of_attack, bank_angle=0):
    a = abs(major_minor_axis_ratio_body * np.cos(bank_angle) + (1/major_minor_axis_ratio_body) * np.sin(bank_angle))
    b = abs(np.sin(2 * angle_of_attack) * np.cos(angle_of_attack/2)) + 2 * fineness_ratio_body * np.sin(angle_of_attack) * np.sin(angle_of_attack)
    return a * b

# Aero efficiency of the body L_body/D_body as func of alpha (maximise)
def lift_to_drag_ratio_body(normal_force_coef, drag_coef_zero_lift, angle_of_attack):
    """
    Usually L/D is overpredicted a bit for const alt 1g flight
    Usually alpha needed for L/D max is also overpredicted for the conditions above
    """
    a = (normal_force_coef * np.cos(angle_of_attack) - drag_coef_zero_lift * np.sin(angle_of_attack))
    b = (normal_force_coef * np.sin(angle_of_attack) + drag_coef_zero_lift * np.cos(angle_of_attack))
    return a / b

# C_p location of the body
def center_of_pressure_body(length_nose, length_body, angle_of_attack):
    return length_nose * (0.63 * (1 - np.sin(angle_of_attack) * np.sin(angle_of_attack)) + 0.5 * (length_body/length_nose) * np.sin(angle_of_attack) * np.sin(angle_of_attack))

#-------------------------------------------------
# 2.5) Wings vs No Wings
#-------------------------------------------------
"""
If subsonic (maybeee) add large wings (like actual ones not just tabs)
Usually for supersonic, L/D of body (see above) is usually enough due to the high dyn_pressures
"""

#-------------------------------------------------
# 2.6) Normal Force for Surfaces
#-------------------------------------------------


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
