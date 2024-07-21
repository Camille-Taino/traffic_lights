class TrafficLightState():
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class TrafficLightModels:
    def __init__(self, direction, green_light_duration, current_light_state, group_id, current_datetime, yellow_light_duration = 5,  is_direction_right_turn = True):
        self.direction = direction
        self.current_light_state = current_light_state 
        self.current_light_state_color = str(current_light_state)
        self.green_light_duration = green_light_duration
        self.yellow_light_duration = yellow_light_duration
        self.last_light_state_time = current_datetime
        self.is_direction_right_turn = is_direction_right_turn
        self.group_id = group_id