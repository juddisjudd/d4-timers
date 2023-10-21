import tkinter as tk
import requests
from datetime import datetime, timedelta
import pytz

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
    
def get_next_world_boss_event(world_boss_times):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for event in world_boss_times:
        event_time = datetime.strptime(event['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
        if event_time > now:
            return event_time, event['boss']
    return None, None

class HelltideOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
        api_data = self.fetch_api_data()
        self.helltide_times = parse_helltide_times(api_data)
        self.world_boss_times = api_data['world_boss']
        
        self.title("Helltide Timer")
        self.geometry("250x135+100+100")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.7)
        self.configure(bg='black')
        
        self.label = tk.Label(self, text="", font=("PT Serif", 12, "bold"), bg="black", fg="white")
        self.label.pack(pady=6)
        
        self.world_boss_prefix_label = tk.Label(self, text="Next World Boss:", font=("PT Serif", 12, "bold"), bg="black", fg="white")
        self.world_boss_prefix_label.pack(pady=(0, 0))

        self.boss_name_label = tk.Label(self, text="", font=("PT Serif", 12, "bold"), bg="black", fg="red")
        self.boss_name_label.pack(pady=(0, 0))

        self.spawn_timer_label = tk.Label(self, text="", font=("PT Serif", 12, "bold"), bg="black", fg="white")
        self.spawn_timer_label.pack(pady=0)
        
        self.resizable(False, False)
        self.overrideredirect(True)
        self.bind("<Control-q>", self.close_window)
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.perform_drag)
        self.x = 0
        self.y = 0
        
        self.update_timer()

    def fetch_api_data(self):
        data_url = "https://helltides.com/api/schedule"
        data = fetch_api_data(data_url)
        if data:
            return data
        else:
            print("Failed to fetch data from the API.")
            return {"helltide": [], "world_boss": []}

    def update_timer(self):
        next_event, is_active = get_next_helltide_event(self.helltide_times)
        if next_event:
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            if is_active:
                remaining_time = (next_event + timedelta(hours=1)) - now
                self.label.config(text=f"Helltide Active: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")
            else:
                remaining_time = next_event - now
                self.label.config(text=f"Until Next Helltide: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")

        world_boss_time, boss_name = get_next_world_boss_event(self.world_boss_times)
        if world_boss_time:
            remaining_time = world_boss_time - now
            self.boss_name_label.config(text=boss_name)
            self.spawn_timer_label.config(text=f"Spawns in: {str(timedelta(seconds=round(remaining_time.total_seconds())))}")
        else:
            self.world_boss_times = self.fetch_api_data()["world_boss"]

        self.after(1000, self.update_timer)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def perform_drag(self, event):
        self.geometry(f"+{event.x_root - self.x}+{event.y_root - self.y}")

    def close_window(self, event=None):
        self.destroy()

if __name__ == "__main__":
    app = HelltideOverlay()
    app.mainloop()
