# Drone Package Tracker

## Overview

Drone Package Tracker is a desktop application that provides real-time tracking and monitoring of autonomous delivery drones within a local neighborhood. This project enables visualization and remote interaction with drones as they transport meals from pickup locations to delivery destinations.

The application uses a PyQt-based desktop frontend and a real-time map interface powered by Leaflet.js embedded in a local HTML file. Drones are represented with colored markers and path trails, updating as telemetry data changes.

## Features

- Add and remove drones dynamically via the UI
- Real-time drone telemetry updates
- Map-based interface with drone position and travel trail
- Interactive popup info windows showing drone status (e.g., battery level)
- Trail tracking of each drone's delivery route
- Simple user interactions (only through loading/unloading and dashboard interface)

## Tech Stack

### Frontend
- Python 3.x
- PyQt5 (QWebEngineView, QWebChannel)
- HTML + JavaScript (Leaflet.js for maps)
- Qt WebChannel integration for Python↔JavaScript communication

### Backend
- Python-based telemetry and drone management (via `DroneManager` class)

### Libraries and Tools
- [Leaflet.js](https://leafletjs.com/) (for rendering interactive maps)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [OpenStreetMap](https://www.openstreetmap.org/) (for tile layers)

## Usage

1. Install dependencies:
    ```bash
    pip install PyQt5
    ```

2. Run the application:
    ```bash
    python frontend.py
    ```

3. Use the GUI to:
   - Add drones (select a color to represent each one)
   - View their location and battery status on the map
   - Remove drones from tracking

## Future Enhancements

- Backend integration with live drone hardware or simulation APIs
- Persistent storage of drone flight logs
- Package payload tracking and delivery status
- User authentication and role-based access

## License

This project is licensed under the MIT License.
