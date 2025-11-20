from flask import Flask, render_template, request, jsonify
import math
import random
from typing import Dict, Tuple

app = Flask(__name__)

class CollisionAvoidanceSystem:
    def __init__(self):
        self.critical_ttc_threshold = 10  # seconds
        self.trigger_distance = 500  # meters
        
    def calculate_ttc(self, distance: float, speed_a: float, speed_b: float) -> float:
        """Calculate Time-to-Collision in seconds"""
        if speed_a + speed_b <= 0:
            return float('inf')
        return distance / (speed_a + speed_b)
    
    def calculate_avoidance_maneuver(self, car_a: Dict, car_b: Dict, ttc: float) -> Dict:
        """Determine the best avoidance strategy"""
        
        if ttc > self.critical_ttc_threshold:
            return {
                "status": "safe",
                "alert_level": "none",
                "advice": "Maintain safe distance"
            }
        
        # Decision logic based on relative speeds and positions
        maneuvers = []
        alert_level = "warning"
        
        if ttc <= 5:
            alert_level = "critical"
        
        # Advise both vehicles to slow down
        maneuvers.append("Both vehicles reduce speed immediately")
        
        # Determine which vehicle should take primary avoidance action
        if car_a["speed"] >= car_b["speed"]:
            maneuvers.append("Vehicle A: Steer right onto shoulder")
            maneuvers.append("Vehicle B: Maintain course, prepare to brake")
        else:
            maneuvers.append("Vehicle B: Steer left onto shoulder") 
            maneuvers.append("Vehicle A: Maintain course, prepare to brake")
        
        return {
            "status": "collision_imminent",
            "alert_level": alert_level,
            "ttc": round(ttc, 2),
            "maneuvers": maneuvers,
            "safe_maneuver_applied": True
        }
    
    def simulate_avoidance(self, car_a: Dict, car_b: Dict, avoidance_data: Dict) -> Dict:
        """Simulate the outcome of the avoidance maneuver"""
        
        if avoidance_data["status"] == "safe":
            return {
                "collision_avoided": True,
                "min_distance": random.uniform(50, 100),
                "outcome": "Safe passage"
            }
        
        # Simulate physics of avoidance
        success_probability = min(0.95, 0.7 + (avoidance_data["ttc"] / 20))
        collision_avoided = random.random() < success_probability
        
        if collision_avoided:
            min_distance = random.uniform(5, 20)  # meters
            outcome = "Close call - collision avoided"
        else:
            min_distance = 0
            outcome = "COLLISION OCCURRED"
        
        return {
            "collision_avoided": collision_avoided,
            "min_distance": min_distance,
            "outcome": outcome
        }

cas_system = CollisionAvoidanceSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate-collision', methods=['POST'])
def calculate_collision():
    data = request.json
    
    car_a = {
        "speed": data.get("speed_a", 0),
        "position": data.get("position_a", 0)
    }
    
    car_b = {
        "speed": data.get("speed_b", 0), 
        "position": data.get("position_b", 500)
    }
    
    distance = abs(car_b["position"] - car_a["position"])
    
    # Calculate TTC
    ttc = cas_system.calculate_ttc(distance, car_a["speed"], car_b["speed"])
    
    # Get avoidance advice
    avoidance_data = cas_system.calculate_avoidance_maneuver(car_a, car_b, ttc)
    
    # Simulate outcome
    simulation_result = cas_system.simulate_avoidance(car_a, car_b, avoidance_data)
    
    response = {
        "distance": round(distance, 2),
        "ttc": round(ttc, 2),
        "avoidance_advice": avoidance_data,
        "simulation_result": simulation_result,
        "car_a": car_a,
        "car_b": car_b
    }
    
    return jsonify(response)

@app.route('/api/generate-random-scenario', methods=['GET'])
def generate_random_scenario():
    """Generate a random collision scenario for testing"""
    
    speed_a = random.uniform(60, 120)  # km/h
    speed_b = random.uniform(60, 120)  # km/h
    
    # Convert to m/s for calculations
    speed_a_ms = speed_a / 3.6
    speed_b_ms = speed_b / 3.6
    
    return jsonify({
        "speed_a": round(speed_a, 1),
        "speed_b": round(speed_b, 1),
        "speed_a_ms": round(speed_a_ms, 1),
        "speed_b_ms": round(speed_b_ms, 1)
    })

if __name__ == '__main__':
    app.run(debug=True)