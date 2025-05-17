# backend.py
import random

# Simulated drone sensor interface
class DroneSensorInterface:
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.latitude = random.uniform(40.0, 41.0)
        self.longitude = random.uniform(-74.0, -73.0)
        self.altitude = random.uniform(100, 200)
        self.battery = 100.0
        self.trail = [(self.latitude, self.longitude)]

    def get_telemetry(self):
        self.latitude += random.uniform(-0.001, 0.001)
        self.longitude += random.uniform(-0.001, 0.001)
        self.battery -= random.uniform(0.01, 0.05)
        self.trail.append((self.latitude, self.longitude))
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'battery': max(self.battery, 0.0),
            'trail': self.trail
        }

# Backend Manager for drones
class DroneManager:
    def __init__(self):
        self.drones = {}

    def add_drone(self, drone_id):
        if drone_id not in self.drones:
            self.drones[drone_id] = DroneSensorInterface(drone_id)

    def remove_drone(self, drone_id):
        if drone_id in self.drones:
            del self.drones[drone_id]

    def get_all_telemetry(self):
        telemetry_data = {}
        for drone_id, drone in self.drones.items():
            telemetry_data[drone_id] = drone.get_telemetry()
        return telemetry_data
