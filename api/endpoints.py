#!/usr/bin/env python3


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ai_engine.recommendation_engine import TransportRecommender

router = APIRouter()

# Request/Response models
class RouteRequest(BaseModel):
    start: str
    end: str
    time: str = "08:00"
    preference: str = "balanced"
    day_type: str = "weekday"
    user_id: Optional[str] = None
    learn_from_choice: Optional[str] = None

class RouteResponse(BaseModel):
    success: bool
    route_count: int
    recommendations: List[dict]
    weather_info: dict
    processing_time_ms: float
    learning_enabled: bool

@router.post("/route", response_model=RouteResponse)
async def get_ai_route(request: RouteRequest):
    """
    Get AI-powered route recommendations with learning
    """
    import time
    start_time = time.time()
    
    try:
        # Initialize AI recommender with user learning
        recommender = TransportRecommender(
            preference=request.preference,
            user_id=request.user_id
        )
        
        # Get current weather
        current_weather = recommender.get_current_weather()
        
        # Get recommendations with learning
        recommendations = recommender.get_top_recommendations(
            start=request.start,
            end=request.end,
            departure_time=request.time,
            top_n=5,
            learn_from_choice=request.learn_from_choice
        )
        
        # Weather info - properly formatted
        weather_info = {
            "condition": current_weather.get('condition_ar', current_weather.get('condition', 'مشمس')),
            "temperature": current_weather.get('temp_formatted', '25°C'),  # Fixed: use formatted temperature
            "temp_value": current_weather.get('temp', 25),
            "humidity": current_weather.get('humidity', '65%'),
            "wind_speed": current_weather.get('wind_speed', '10 km/h'),
            "feels_like": current_weather.get('feels_like', '25°C'),
            "icon": current_weather.get('icon', '01d'),
            "impact": "طقس جيد للتنقل" if 'مطر' not in current_weather.get('condition_ar', '') else "انتبه للطقس"
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        return RouteResponse(
            success=True,
            route_count=len(recommendations),
            recommendations=recommendations,
            weather_info=weather_info,
            processing_time_ms=round(processing_time, 2),
            learning_enabled=bool(request.user_id)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/habits")
async def get_user_habits(user_id: str):
    """Get user's learned travel habits"""
    recommender = TransportRecommender(user_id=user_id)
    return {
        "user_id": user_id,
        "habits": recommender.user_habits,
        "total_trips": recommender.user_habits['total_trips'],
        "preferred_mode": max(recommender.user_habits['preferred_modes'].items(), 
                            key=lambda x: x[1], default=('none', 0))[0],
        "frequent_routes": list(recommender.user_habits['frequent_routes'].keys())[:5]
    }

@router.post("/user/{user_id}/clear_habits")
async def clear_user_habits(user_id: str):
    """Clear user's learned habits (reset learning)"""
    import os
    file_path = f"data/user_{user_id}_learning.pkl"
    if os.path.exists(file_path):
        os.remove(file_path)
    return {"message": "User habits cleared", "user_id": user_id}

@router.get("/stations/{mode}")
async def get_stations(mode: str, area: Optional[str] = None):
    """
    Get available stations for a specific transport mode
    """
    import json
    
    try:
        with open('data/stations_algiers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if mode == "all":
            return {
                "bicycle_stations": len(data["bicycle_stations"]),
                "metro_stations": len(data["metro_stations"]),
                "bus_stations": len(data["bus_stations"])
            }
        elif mode == "bicycle":
            stations = data["bicycle_stations"]
            if area:
                stations = [s for s in stations if s.get("area") == area]
            return {"mode": "bicycle", "stations": stations, "count": len(stations)}
        elif mode == "metro":
            return {"mode": "metro", "stations": data["metro_stations"], "count": len(data["metro_stations"])}
        elif mode == "bus":
            return {"mode": "bus", "stations": data["bus_stations"], "count": len(data["bus_stations"])}
        else:
            raise HTTPException(status_code=400, detail="Invalid mode. Use: bicycle, metro, bus, or all")
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Station data not found")

@router.get("/weather/{city}")
async def get_weather_impact(city: str):
    """
    Get weather impact on transport for a city
    """
    # Create a recommender to get current weather
    recommender = TransportRecommender()
    weather = recommender.get_current_weather()
    
    # Impact analysis
    impact = {}
    for mode in ['bicycle', 'metro', 'bus', 'yassir', 'car', 'walk']:
        impact_value = recommender._get_weather_impact(mode, weather)
        if impact_value >= 0.8:
            impact[mode] = "ممتاز"
        elif impact_value >= 0.6:
            impact[mode] = "جيد"
        elif impact_value >= 0.4:
            impact[mode] = "متوسط"
        else:
            impact[mode] = "ضعيف"
    
    return {
        "city": city,
        "weather": weather,
        "impact": impact,
        "recommendations": get_weather_recommendations(weather.get('condition_ar', 'مشمس'))
    }

@router.get("/traffic/{area}")
async def get_traffic_conditions(area: str):
    """
    Get current traffic conditions for an area
    """
    from datetime import datetime
    
    now = datetime.now()
    hour = now.hour
    
    # Simulate traffic levels
    traffic_levels = {
        "الجزائر الوسطى": "very_high" if 7 <= hour <= 10 else "high" if 16 <= hour <= 19 else "medium",
        "باب الوادي": "high" if 8 <= hour <= 11 else "medium",
        "الحراش": "high" if 7 <= hour <= 9 or 17 <= hour <= 19 else "medium",
        "بولوغين": "medium" if 8 <= hour <= 10 else "low"
    }
    
    level = traffic_levels.get(area, "medium")
    
    # Convert to Arabic and get icon
    level_map = {
        "low": {"ar": "خفيف", "icon": "🟢", "delay_min": 5},
        "medium": {"ar": "متوسط", "icon": "🟡", "delay_min": 10},
        "high": {"ar": "ثقيل", "icon": "🟠", "delay_min": 20},
        "very_high": {"ar": "شديد", "icon": "🔴", "delay_min": 30}
    }
    
    traffic_info = level_map.get(level, level_map["medium"])
    
    return {
        "area": area,
        "current_time": now.strftime("%H:%M"),
        "traffic": {
            "level": level,
            "level_ar": traffic_info["ar"],
            "icon": traffic_info["icon"],
            "delay_min": traffic_info["delay_min"],
            "avg_speed_kmh": 40 if level == "low" else 25 if level == "medium" else 15 if level == "high" else 10,
            "updated": now.isoformat()
        },
        "recommendations": get_traffic_recommendations(level, area)
    }

# Helper functions
def get_weather_recommendations(condition: str) -> List[str]:
    """Get weather-based recommendations"""
    if 'مطر' in condition or 'عاصف' in condition:
        return [
            "استخدم المترو أو ياسر لتجنب المطر",
            "تجنب الدراجة والمشي",
            "خذ معطف واق من المطر"
        ]
    elif 'حار' in condition or 'شديد' in condition:
        return [
            "استخدم وسائل نقل مكيفة",
            "اشرب الكثير من الماء",
            "تجنب المشي لمسافات طويلة"
        ]
    else:
        return ["الطقس مناسب لجميع وسائل النقل", "الدراجة خيار جيد اليوم"]

def get_traffic_recommendations(level: str, area: str) -> List[str]:
    """Get traffic-based recommendations"""
    recommendations = []
    
    if level in ["high", "very_high"]:
        recommendations.append(f"تجنب {area} إذا أمكن")
        recommendations.append("استخدم المترو لتجاوز الازدحام")
        recommendations.append("أضف 15-30 دقيقة إضافية لوقت الرحلة")
    
    if area == "الجزائر الوسطى" and level != "low":
        recommendations.append("استخدم الطرق البديلة مثل شارع العربي بن مهيدي")
    
    if not recommendations:
        recommendations.append("حركة المرور طبيعية - استمتع برحلتك")
    
    return recommendations
