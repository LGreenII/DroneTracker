# frontend.py (rewritten to use raw Leaflet map)
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QColorDialog, QMessageBox
from PyQt5.QtCore import QTimer, QUrl, QObject, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from backend import DroneManager

class JSBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

class PackageTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = DroneManager()
        self.telemetry_data = {}
        self.map_center = [40.75, -73.95]
        self.map_zoom = 11
        self.drone_colors = {}
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def initUI(self):
        self.setWindowTitle('Drone Package Tracker')
        self.setGeometry(100, 100, 1000, 600)

        self.layout = QHBoxLayout()

        self.droneList = QListWidget()
        self.droneList.itemClicked.connect(self.center_on_drone)
        self.addDroneBtn = QPushButton("Add Drone")
        self.addDroneBtn.clicked.connect(self.add_drone)
        self.removeDroneBtn = QPushButton("Remove Drone")
        self.removeDroneBtn.clicked.connect(self.remove_drone)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.droneList)
        leftLayout.addWidget(self.addDroneBtn)
        leftLayout.addWidget(self.removeDroneBtn)

        self.map_view = QWebEngineView()
        self.bridge = JSBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.map_view.page().setWebChannel(self.channel)

        self.generate_map_html()

        self.layout.addLayout(leftLayout)
        self.layout.addWidget(self.map_view)

        self.setLayout(self.layout)

    def generate_map_html(self):
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Drone Map</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style> #map { width: 100%; height: 100vh; } </style>
        </head>
        <body>
        <div id="map"></div>
        <script>
            let map = L.map('map').setView([40.75, -73.95], 11);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            let droneMarkers = {};
            let dronePaths = {};

            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.bridge = channel.objects.bridge;
            });

            window.updateDrone = function(drone_id, lat, lon, trail, popup, color) {
                if (droneMarkers[drone_id]) {
                    droneMarkers[drone_id].setLatLng([lat, lon]).bindPopup(popup);
                } else {
                    let marker = L.circleMarker([lat, lon], { radius: 6, color: color }).addTo(map);
                    marker.bindPopup(popup);
                    droneMarkers[drone_id] = marker;
                }

                if (dronePaths[drone_id]) {
                    map.removeLayer(dronePaths[drone_id]);
                }
                let polyline = L.polyline(trail, { color: color }).addTo(map);
                dronePaths[drone_id] = polyline;
            }

            window.removeDrone = function(drone_id) {
                if (droneMarkers[drone_id]) {
                    map.removeLayer(droneMarkers[drone_id]);
                    delete droneMarkers[drone_id];
                }
                if (dronePaths[drone_id]) {
                    map.removeLayer(dronePaths[drone_id]);
                    delete dronePaths[drone_id];
                }
            }

            window.centerOnDrone = function(lat, lon) {
                map.setView([lat, lon], map.getZoom());
            }
        </script>
        </body>
        </html>
        '''
        with open('map.html', 'w') as f:
            f.write(html_content)
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath('map.html')))

    def add_drone(self):
        drone_id = f"Drone_{len(self.manager.drones)+1}"
        color = QColorDialog.getColor()
        if not color.isValid():
            return
        self.drone_colors[drone_id] = color.name()
        self.manager.add_drone(drone_id)
        self.droneList.addItem(drone_id)

    def remove_drone(self):
        selected_item = self.droneList.currentItem()
        if selected_item:
            drone_id = selected_item.text()
            reply = QMessageBox.question(self, 'Confirm Removal', f"Are you sure you want to remove {drone_id}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.manager.remove_drone(drone_id)
                self.drone_colors.pop(drone_id, None)
                self.telemetry_data.pop(drone_id, None)
                self.map_view.page().runJavaScript(f"removeDrone('{drone_id}')")
                self.droneList.takeItem(self.droneList.row(selected_item))

    def update_data(self):
        self.telemetry_data = self.manager.get_all_telemetry()
        for drone_id, data in self.telemetry_data.items():
            lat = data['latitude']
            lon = data['longitude']
            battery = data['battery']
            trail = data['trail']
            popup = f"{drone_id}: Battery {battery:.1f}%"
            color = self.drone_colors.get(drone_id, 'blue')
            trail_js = json.dumps([[lat, lon] for lat, lon in trail])
            self.map_view.page().runJavaScript(
                f"updateDrone('{drone_id}', {lat}, {lon}, {trail_js}, '{popup}', '{color}')")

    def center_on_drone(self, item):
        drone_id = item.text()
        if drone_id in self.telemetry_data:
            lat = self.telemetry_data[drone_id]['latitude']
            lon = self.telemetry_data[drone_id]['longitude']
            self.map_view.page().runJavaScript(f"centerOnDrone({lat}, {lon})")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PackageTrackerApp()
    window.show()
    sys.exit(app.exec_())

