"""
@time: 11:05 06-02-2025
@author: kuckreja
@purpose: baseline missile specs for rocket-based air-to-air
"""

class BaselineMissile:
	def __init__(self, type: str) -> None:
		if type == "a2a": # air to air
			self.type: str = "a2a"
			self.name: str = "lockheed-sidewinder"
			self.diameter_body = 0.4 # m
			self.fineness_ratio_nose = 0.25
			self.mass_impact = 35.0 # kg 
			self.mass_takeoff = 50.0 # kg
			self.range = 8000.0 # m 
			self.alt_max_engagement = 9144.0 # m (30,000 ft)
			self.load_max = 30.0 # g's
			self.azimuth_coverage = 360.0 # deg
			self.freq_actuator = 15.916 # Hz


if __name__ == "__main__":
	print("baseline code was ran")
