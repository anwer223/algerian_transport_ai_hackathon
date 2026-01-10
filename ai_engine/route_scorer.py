#!/usr/bin/env python3


import math
from datetime import datetime

class RouteScorer:
   
    
    @staticmethod
    def calculate_traffic_score(area: str, time_obj: datetime) -> float:
      
        hour = time_obj.hour
        weekday = time_obj.weekday()  # 0=Monday, 6=Sunday
        
        # Known congested areas in Algiers
        congested_areas = ["الجزائر الوسطى", "باب الوادي", "الحراش"]
        
        base_score = 0.8
        
        # Time penalties
        if 7 <= hour <= 9:  # Morning rush
            base_score -= 0.4
        elif 16 <= hour <= 19:  # Evening rush
            base_score -= 0.3
        elif hour == 12 and weekday == 4:  # Friday noon
            base_score -= 0.5
        
        # Area penalties
        if area in congested_areas:
            base_score -= 0.2
        
        # Ensure score is between 0.1 and 1.0
        return max(0.1, min(1.0, base_score))
    
    @staticmethod
    def calculate_weather_impact(mode: str, weather_condition: str = "sunny") -> float:
    
        weather_impact = {
            "bicycle": {"sunny": 1.0, "rain": 0.3, "hot": 0.7, "cold": 0.8},
            "metro": {"sunny": 1.0, "rain": 1.2, "hot": 1.0, "cold": 1.0},
            "bus": {"sunny": 1.0, "rain": 1.1, "hot": 0.9, "cold": 0.9},
            "yassir": {"sunny": 1.0, "rain": 1.3, "hot": 1.0, "cold": 1.0},
            "car": {"sunny": 1.0, "rain": 0.8, "hot": 1.0, "cold": 1.0},
            "walk": {"sunny": 1.0, "rain": 0.2, "hot": 0.5, "cold": 0.6}
        }
        
        return weather_impact.get(mode, {}).get(weather_condition, 1.0)
    
    @staticmethod
    def calculate_route_safety(mode: str, start_area: str, end_area: str) -> float:
        """
        Calculate safety score for route (0-1, higher = safer)
        """
        safety_scores = {
            "bicycle": 0.7,
            "metro": 0.9,
            "bus": 0.6,
            "yassir": 0.8,
            "car": 0.8,
            "walk": 0.5
        }
        
        base_safety = safety_scores.get(mode, 0.5)
        
        # Adjust based on areas (simplified)
        safe_areas = ["الجزائر الوسطى", "المرادية", "الحامة"]
        risky_areas = ["باب الوادي", "القصبة ليلاً"]
        
        if start_area in safe_areas and end_area in safe_areas:
            base_safety += 0.1
        elif start_area in risky_areas or end_area in risky_areas:
            base_safety -= 0.2
        
        return max(0.1, min(1.0, base_safety))
    
    @staticmethod
    def calculate_energy_savings(mode: str, distance_km: float) -> dict:
        """
        Calculate energy and cost savings compared to private car
        
        Returns:
            Dictionary with energy and subsidy savings
        """
        # Energy consumption in kWh per km
        energy_per_km = {
            "car": 0.20,      # Private car
            "yassir": 0.20,   # Similar to car (shared but extra routing)
            "bus": 0.05,      # Per passenger-km
            "metro": 0.03,
            "tram": 0.02,
            "bicycle": 0.0,
            "walk": 0.0
        }
        
        car_energy = energy_per_km["car"] * distance_km
        mode_energy = energy_per_km.get(mode, 0.1) * distance_km
        
        energy_saved = car_energy - mode_energy
        
        # Algerian subsidy: ~8 DZD per kWh
        subsidy_saved = energy_saved * 8
        
        return {
            "energy_saved_kwh": round(energy_saved, 2),
            "subsidy_saved_dzd": round(subsidy_saved, 2),
            "co2_saved_kg": round(energy_saved * 0.4, 2)  # ~0.4kg CO2 per kWh
        }
