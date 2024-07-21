import threading
import time
from .traffic_light_service import TrafficLightService

class TrafficLightRegularService:
    def __init__(self, traffic_light_service: TrafficLightService):
        self.traffic_light_service = traffic_light_service
        self.timer = None

    def _update_traffic_lights(self):
        self.traffic_light_service.update_traffic_state_lights()
        # Schedule the next update
        self.timer = threading.Timer(1.0, self._update_traffic_lights)
        self.timer.start()

    def start(self):
        # Start the background task
        self._update_traffic_lights()

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()

if __name__ == "__main__":
    traffic_light_service = TrafficLightService()
    background_service = TrafficLightRegularService(traffic_light_service)
    try:
        background_service.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        background_service.stop()