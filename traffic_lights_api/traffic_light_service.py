from datetime import datetime
from itertools import groupby
import json
from threading import Lock
from traffic_lights_api.models import TrafficLightModels, TrafficLightState

def serialize_enum(instance):
    serialized = json.dumps(instance.name).strip('"')
    return serialized

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Format the date however you like
            return obj.strftime("%H:%M:%S")
        # Let the base class default method raise the TypeError
        return super().default(obj)


class TrafficLightService:
    def __init__(self):
        current_datetime = datetime.now()
        light_configs = [
            ("North", 20, TrafficLightState.GREEN, 1, current_datetime),
            ("South", 20, TrafficLightState.GREEN, 1, current_datetime),
            ("East", 20, TrafficLightState.RED, 2, current_datetime),
            ("West", 20, TrafficLightState.RED, 2, current_datetime)
    ]
        self._lights = [TrafficLightModels(*config) for config in light_configs]
        pass

    def retrieve_lights(self):
        return self._lights
    pass
    
    def update_traffic_state_lights(self):
        current_time = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
        is_peak_hours = self.is_peak_hours(current_time)

        self.adjust_southbound_for_north_right_turn(current_time)

        for key, group in groupby(self._lights, lambda x: x.group_id):
            group_list = list(group)
            should_switch_to_yellow = any(l.current_light_state == TrafficLightState.GREEN and self.should_switch_from_green((current_time - l.last_light_state_time).total_seconds(), is_peak_hours, l.direction) for l in group_list)
            should_switch_to_red = any(l.current_light_state == TrafficLightState.YELLOW and (current_time - l.last_light_state_time).total_seconds() >= 5 for l in group_list)
            print(group_list)
            if should_switch_to_yellow:
                for light in group_list:
                    if light.current_light_state == TrafficLightState.RED:
                        break
                    light.current_light_state = TrafficLightState.YELLOW
                    light.last_light_state_time = current_time
                    if light.direction == "North":
                        light.is_direction_right_turn = False
            elif should_switch_to_red:
                for light in group_list:
                    light.current_light_state = TrafficLightState.RED
                    light.last_light_state_time = current_time
                self.set_opposite_direction_to_green(key)
                pass

    def set_opposite_direction_to_green(self, group_id):
        opposite_group_id = 2 if group_id == 1 else 1
        for light in filter(lambda l: l.group_id == opposite_group_id, self._lights):
            light.current_light_state = TrafficLightState.GREEN
            light.last_light_state_time = datetime.now()
            pass

    def is_peak_hours(self, time) -> bool:
        date_string_08 = "08:00:00"
        date_string_10 = "10:00:00"
        date_string_17 = "17:00:00"
        date_string_19 = "19:00:00"

        time = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
        morning_start = datetime.strptime(date_string_08, "%H:%M:%S")
        morning_end = datetime.strptime(date_string_10, "%H:%M:%S")
        evening_start = datetime.strptime(date_string_17, "%H:%M:%S")
        evening_end = datetime.strptime(date_string_19, "%H:%M:%S")

        return (morning_start <= time < morning_end) or (evening_start <= time < evening_end)
    pass

    def should_switch_from_green(self, elapsed_seconds, is_peak_hours, direction):
        required_seconds = 40 if is_peak_hours and direction in ["North", "South"] else 20
        return elapsed_seconds >= required_seconds
    pass

    def adjust_southbound_for_north_right_turn(self, current_time):

        is_peak_hours = self.is_peak_hours(current_time)
        north_light = next(filter(lambda l: l.direction == "North", self._lights), None)

        if north_light and north_light.current_light_state == TrafficLightState.GREEN and not north_light.is_direction_right_turn and self.should_activate_right_turn((current_time - north_light.last_light_state_time).total_seconds(), is_peak_hours):
            north_light.is_direction_right_turn = True
            for light in filter(lambda l: l.direction != "North", self._lights):
                if light.current_light_state != TrafficLightState.RED:
                    light.current_light_state = TrafficLightState.RED
                    light.last_light_state_time = current_time
                    pass

    def should_activate_right_turn(self, elapsed_seconds, is_peak_hours):
        green_duration = 40 if is_peak_hours else 20
        return elapsed_seconds >= (green_duration - 10)
    pass