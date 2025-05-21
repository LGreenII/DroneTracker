# frontend.py (rewritten to use raw Leaflet map)
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QColorDialog, QMessageBox
from PyQt5.QtCore import QTimer, QUrl, QObject, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from backend import DroneManager
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtCore import Qt

## Map Click Signal
class JSBridge(QObject):
    mapClickedSignal = pyqtSignal(float, float)  # lat, lon
    droneRightClickedSignal = pyqtSignal(str) # droneID of drone to be removed

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(float, float)
    def mapClicked(self, lat, lon):
        self.mapClickedSignal.emit(lat, lon)

    @pyqtSlot(str)
    def droneRightClicked(self, drone_id):  # slot for listening for right click
        self.droneRightClickedSignal.emit(drone_id)

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

    def initUI(self,):
        self.setWindowTitle('Drone Package Tracker')
        self.setGeometry(100, 100, 1000, 600)

        self.layout = QHBoxLayout()

        # Max size for left drone List and buttons
        max_size = 250

        self.droneList = QListWidget()
        self.droneList.setFixedWidth(max_size)
        self.droneList.itemClicked.connect(self.center_on_drone)
        self.addDroneBtn = QPushButton("Add Drone")
        self.addDroneBtn.setFixedWidth(max_size)
        self.addDroneBtn.clicked.connect(self.add_drone)

        ## Auto Assign check box
        self.autoColorCheckBox = QCheckBox("Auto-Assign Drone Colors")
        self.leftLayout = QVBoxLayout()  # Make sure this is not None
        self.autoColorCheckBox.setChecked(False)  # default is manual

        self.removeDroneBtn = QPushButton("Remove Drone")
        self.removeDroneBtn.setFixedWidth(max_size)
        self.removeDroneBtn.clicked.connect(self.remove_drone)

        self.leftLayout.addWidget(self.droneList)
        self.leftLayout.addWidget(self.addDroneBtn)
        self.leftLayout.addWidget(self.removeDroneBtn)
        self.leftLayout.addWidget(self.autoColorCheckBox)

        self.map_view = QWebEngineView()
        self.bridge = JSBridge()
        self.bridge.mapClickedSignal.connect(self.add_drone_at_location) #Add Drone on left click
        self.bridge.droneRightClickedSignal.connect(self.remove_drone_by_id) #remove drone on right click
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.map_view.page().setWebChannel(self.channel)

        self.generate_map_html()

        self.layout.addLayout(self.leftLayout)
        self.layout.addWidget(self.map_view)

        self.setLayout(self.layout)

    def add_drone_at_location(self, lat, lon):
        drone_id = f"Drone_{len(self.manager.drones) + 1}"
        if self.autoColorCheckBox.isChecked():
            import colorsys
            total = len(self.manager.drones)
            hue = (total * 0.618033988749895) % 1
            r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.8, 0.95)]
            color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            qcolor = QColorDialog.getColor()
            if not qcolor.isValid():
                return
            color = qcolor.name()

        self.drone_colors[drone_id] = color

        # Add a new DroneSensorInterface and override the initial coordinates
        self.manager.add_drone(drone_id)
        self.manager.drones[drone_id].latitude = lat
        self.manager.drones[drone_id].longitude = lon
        self.manager.drones[drone_id].trail = [(lat, lon)]

        self.droneList.addItem(drone_id)

    def remove_drone_by_id(self, drone_id):
        reply = QMessageBox.question(
            self,
            'Confirm Removal',
            f"Are you sure you want to remove {drone_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if drone_id in self.manager.drones:
                self.manager.remove_drone(drone_id)
                self.drone_colors.pop(drone_id, None)
                self.telemetry_data.pop(drone_id, None)
                self.map_view.page().runJavaScript(f"removeDrone('{drone_id}')")

                # Remove from list widget
                items = self.droneList.findItems(drone_id, Qt.MatchExactly)
                if items:
                    index = self.droneList.row(items[0])
                    self.droneList.takeItem(index)

                self.show_toast(f"{drone_id} has been removed.")

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
            let map = L.map('map').setView([34.7295, -86.5853], 11);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            
            let droneMarkers = {};
            let dronePaths = {};

            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.bridge = channel.objects.bridge;
            });
            
            map.on('click', function(e) {
                let lat = e.latlng.lat;
                let lon = e.latlng.lng;
                if (window.bridge && window.bridge.mapClicked) {
                    window.bridge.mapClicked(lat, lon);
                }
            });


            window.updateDrone = function(drone_id, lat, lon, trail, popup, color) {
                if (droneMarkers[drone_id]) {
                    droneMarkers[drone_id].setLatLng([lat, lon]).bindPopup(popup);
                } else {
                    let marker = L.circleMarker([lat, lon], { radius: 6, color: color }).addTo(map);
                    marker.bindPopup(popup);

                    // NEW: Right-click listener
                marker.on('contextmenu', function(e) {
                    if (window.bridge && window.bridge.droneRightClicked) {
                    window.bridge.droneRightClicked(drone_id);
                    }
                });

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

        # if auto-assign color check box is selected, color is generated
        # else user manually picks with color picker window
        drone_id = f"Drone_{len(self.manager.drones)+1}"
        if self.autoColorCheckBox.isChecked():
            # Auto-assign color
            import colorsys
            total = len(self.manager.drones)
            hue = (total * 0.618033988749895) % 1  # Golden ratio-based hue
            r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.8, 0.95)]
            color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            # Manual color picker
            qcolor = QColorDialog.getColor()
            if not qcolor.isValid():
                return
            color = qcolor.name()
        self.drone_colors[drone_id] = color
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
                self.show_toast(f"{drone_id} has been removed.")

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

    def show_toast(self, message, duration=2000):
        toast = QLabel(message, self)
        toast.setStyleSheet("""
                background-color: rgba(50, 50, 50, 200);
                color: white;
                padding: 10px;
                border-radius: 5px;
            """)
        toast.setWindowFlags(Qt.ToolTip)
        toast.adjustSize()

        x = self.width() - toast.width() - 20
        y = self.height() - toast.height() - 20
        toast.move(x, y)
        toast.show()

        # Keep a reference to avoid garbage collection
        animation = QPropertyAnimation(toast, b"windowOpacity", self)
        animation.setDuration(1000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Wait before starting the fade-out
        QTimer.singleShot(duration, animation.start)

        # Clean up
        def cleanup():
            toast.deleteLater()
            self._active_toasts.remove(animation)

        animation.finished.connect(cleanup)

        # Store the animation to keep it alive
        if not hasattr(self, '_active_toasts'):
            self._active_toasts = []
        self._active_toasts.append(animation)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PackageTrackerApp()
    window.show()
    sys.exit(app.exec_())

