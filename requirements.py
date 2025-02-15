"""
@time: 23:52 02-02-2025
@author: kuckreja
@purpose: requirments for missile, threat and mission
"""

# Missile Technical Requirements
max_engagement_altitude = 9144.0  # Meters (30,000 ft)
horizontal_defense_radius = 8000.0  # Meters
azimuth_coverage = 360  # Degrees 
initial_threat_error = 0.05  # Initial uncertainty in threats azimuth, range, altitude & velocity 


# Target Technical Requirements
target_max_mach = 3.0  # Mach
target_max_load = 3.0  # g's
target_max_ground_range = 100000  # Meters (1 to 100 km)
target_min_diameter = 0.1016 # Meters
target_max_diameter = 0.635  # Meters
target_min_length = 2.4384  # Meters
target_max_length = 6.096  # Meters
target_min_weight = 45.3592  # kg
target_max_weight = 1814.369  # kg


# Non-Technical Requirements 
cost_max = 10000  # USD
production_per_year = 1000  # Num missiles made per year
production_years = 10  # Num years produced
num_missiles_testing = 100  # Num missiles need for testing purposes
maintainance_years = 10  # Years between maintainances

