from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QSound
import requests
from datetime import datetime, timedelta
import pytz
import os

def fetch_api_data(url):
    """Fetch the API data and return it as a dictionary."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def parse_helltide_times(data):
    """Parse helltide times from the data and return them as datetime objects."""
    times = [item["startTime"] for item in data["helltide"]]
    return [datetime.fromisoformat(time.replace("Z", "+00:00")) for time in times]

def get_next_helltide_event(helltide_times):
    """Get the next helltide event based on the current time and determine if it's currently active."""
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for time in helltide_times:
        if time <= now < (time + timedelta(hours=1)):
            return time, True
        elif (time - timedelta(hours=2, minutes=15)) <= now < time:
            return time, False
    return None, False

def parse_legion_times(data):
    """Parse legion times from the data and return them as datetime objects."""
    times = [item["startTime"] for item in data["legion"]]
    return [datetime.fromisoformat(time.replace("Z", "+00:00")) for time in times]

def get_next_legion_event(legion_times):
    """Get the next legion event based on the current time and determine if it's currently active."""
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for time in legion_times:
        if time <= now < (time + timedelta(minutes=3)):
            return time, True
        elif now < time:
            return time, False
    return None, False

def get_next_world_boss_event(world_boss_times):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for event in world_boss_times:
        event_time = datetime.strptime(event['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
        if event_time > now:
            return event_time, event['boss']
    return None, None

class HelltideOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Fetch API Data
        api_data = self.fetch_api_data()
        self.helltide_times = parse_helltide_times(api_data)
        self.world_boss_times = api_data['world_boss']
        self.legion_times = parse_legion_times(api_data)

        # Set up the UI
        self.setWindowTitle("Helltide Timer")
        self.setGeometry(100, 100, 200, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.7)
        self.setStyleSheet("background-color: black;")

        # Layout
        layout = QVBoxLayout()

        # Labels
        self.label = QLabel(self)
        self.label.setFont(QFont("PT Serif", 12, QFont.Bold))
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

        self.legion_label = QLabel(self)
        self.legion_label.setFont(QFont("PT Serif", 12, QFont.Bold))
        self.legion_label.setStyleSheet("color: #E3CF57;")
        layout.addWidget(self.legion_label)

        self.world_boss_prefix_label = QLabel("Next World Boss:", self)
        self.world_boss_prefix_label.setFont(QFont("PT Serif", 12, QFont.Bold))
        self.world_boss_prefix_label.setStyleSheet("color: white;")
        layout.addWidget(self.world_boss_prefix_label)

        self.boss_name_label = QLabel(self)
        self.boss_name_label.setFont(QFont("PT Serif", 12, QFont.Bold))
        self.boss_name_label.setStyleSheet("color: red;")
        layout.addWidget(self.boss_name_label)

        self.spawn_timer_label = QLabel(self)
        self.spawn_timer_label.setFont(QFont("PT Serif", 12, QFont.Bold))
        self.spawn_timer_label.setStyleSheet("color: white;")
        layout.addWidget(self.spawn_timer_label)

        # Set layout
        self.setLayout(layout)

        # Timer to periodically update the UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        # Dragging
        self.is_dragging = False
        self.drag_position = self.pos()

        # Start the timer update
        self.update_timer()

    def fetch_api_data(self):
        data_url = "https://helltides.com/api/schedule"
        data = fetch_api_data(data_url)
        if data:
            return data
        else:
            print("Failed to fetch data from the API.")
            return {"helltide": [], "world_boss": [], "legion": []}

    def update_timer(self):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)

        # Update Helltide Timer
        next_event, is_active = get_next_helltide_event(self.helltide_times)
        if next_event:
            if is_active:
                remaining_time = (next_event + timedelta(hours=1)) - now
                self.label.setText(f"Helltide Active: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")
            else:
                remaining_time = next_event - now
                self.label.setText(f"Until Next Helltide: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")

        # Update Legion Timer
        next_legion_event, legion_active = get_next_legion_event(self.legion_times)
        if next_legion_event:
            if legion_active:
                remaining_time = (next_legion_event + timedelta(minutes=25)) - now
                self.legion_label.setText(f"Legion Active: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")
            else:
                remaining_time = next_legion_event - now
                self.legion_label.setText(f"Until Next Legion: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")

        # Update World Boss Timer
        world_boss_time, boss_name = get_next_world_boss_event(self.world_boss_times)
        if world_boss_time:
            remaining_time = world_boss_time - now
            self.boss_name_label.setText(boss_name)
            self.spawn_timer_label.setText(f"Spawns in: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")
        else:
            self.world_boss_times = self.fetch_api_data()["world_boss"]

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = HelltideOverlay()
    window.show()
    app.exec_()
