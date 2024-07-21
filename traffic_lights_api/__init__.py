import threading
import azure.functions as func
import json

from .traffic_light_scenario import TrafficLightRegularService 
from .traffic_light_service import TrafficLightService, DateTimeEncoder

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        traffic_light_service = TrafficLightService()
        def run_in_background():
            traffic_light_service.update_traffic_state_lights()
        background_thread = threading.Thread(target=run_in_background)
        background_thread.start()

        if req.method == "GET":
            lights = traffic_light_service.retrieve_lights()
            lights = [light.__dict__ for light in lights]
            return func.HttpResponse(body=json.dumps(lights, cls=DateTimeEncoder), status_code=200)
        else:
            return func.HttpResponse("Unsupported HTTP method", status_code=405)
    except Exception as e:
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )