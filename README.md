# 🛩️ Drone Delivery Tracker

## Overview

**Drone Delivery Tracker** is a desktop-based application designed to monitor and interact with autonomous drones responsible for local meal delivery. The application provides real-time tracking, operational status, and command capabilities through a user-friendly dashboard interface.

This project enables safe, efficient, and minimal-intervention delivery of meals using autonomous drones, focusing on a specific neighborhood. User interaction is limited to two touchpoints:
- Loading packages onto drones
- Interfacing with the live dashboard

## 🚀 Key Features

- 📍 **Real-Time Drone Tracking**  
  View live locations of all active drones on an interactive map.

- 🧠 **Autonomous Navigation**  
  Drones calculate and follow optimal paths between pickup and drop-off points.

- 🧭 **Status Monitoring**  
  Monitor drone status (Idle, En Route, Delivering, Returning, Error).

- 📦 **Delivery Management**  
  Visual logs of pickup and drop-off events, including timestamps and drone IDs.

- 🖥️ **Interactive Dashboard UI**  
  Clean, responsive UI built to display active drone fleet data and diagnostics.

- 🔐 **Secure Communications**  
  Encrypted telemetry and control signals for reliable, remote interactions.

## 📂 Project Structure

```
drone-delivery-tracker/
├── backend/                # Backend services for drone communication & telemetry
│   ├── api/                # RESTful endpoints for dashboard updates
│   ├── controller/         # Drone command/response logic
│   └── database/           # Logs and delivery data storage
├── frontend/               # Dashboard GUI (Python + Streamlit or Qt)
├── drone_simulator/        # Simulated drone fleet for testing
├── utils/                  # Shared helpers and utilities
└── README.md               # Project documentation
```

## 🛠️ Tech Stack

- **Languages:** Python, C++
- **Frameworks:** Streamlit, Qt, Flask (or FastAPI), IMGUI
- **Libraries:** OpenCV (for visual feedback), NumPy, Requests, JSON, PySerial (if needed for hardware comms)
- **Other:** Google Maps API / Leaflet.js for map visualization, MQTT or WebSockets for real-time telemetry

## 📡 Drone Workflow

1. Drone awaits package loading at pickup station.
2. Drone receives delivery coordinates via backend.
3. Drone autonomously navigates to destination.
4. Package is dropped off.
5. Drone returns to base or awaits next task.
6. Dashboard updates continuously with status and position.

## 🧪 Development & Testing

To simulate the delivery environment, use the `drone_simulator/` to mimic drone behavior and validate tracking and communication logic.

```bash
cd drone_simulator/
python simulate_drone.py
```

For frontend testing:
```bash
cd frontend/
streamlit run dashboard.py
```

## 📌 Future Enhancements

- Integration with real drone hardware (e.g., DJI SDK, PX4, ArduPilot)
- Weather-aware route planning
- Object avoidance and obstacle detection
- Mobile app companion interface
- Analytics dashboard for delivery efficiency metrics

## 🤝 Contributing

Pull requests and suggestions are welcome! If you’re interested in drone software, AI-driven navigation, or delivery logistics, we’d love your help.

## 📃 License

[MIT License](LICENSE)

---

**Author**: Levon Green  
**Contact**: LevonGreen2@gmail.com  
**Location**: Huntsville, AL  
