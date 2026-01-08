#!/usr/bin/env python3
"""
Configuration for Algiers Transport AI
"""

import os
from datetime import time

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Transport Mode Constants
TRANSPORT_MODES = {
    "bicycle": {"emissions": 0, "min_speed": 10, "max_speed": 20},
    "metro": {"emissions": 5, "min_speed": 30, "max_speed": 60},
    "bus": {"emissions": 15, "min_speed": 15, "max_speed": 40},
    "yassir": {"emissions": 120, "min_speed": 20, "max_speed": 50},
    "car": {"emissions": 150, "min_speed": 20, "max_speed": 60},
    "walk": {"emissions": 0, "min_speed": 4, "max_speed": 6}
}

# Algiers Specific Constants
ALGIERS_AREAS = [
    "الجزائر الوسطى", "باب الوادي", "القصبة", "بولوغين",
    "الحراش", "الدويرة", "بئر مراد رايس", "بني مسوس",
    "القبة", "الشراقة", "الحمامات", "المرادية"
]

# Traffic Patterns in Algiers
TRAFFIC_PEAK_HOURS = {
    "weekday_morning": {"start": time(7, 0), "end": time(9, 30)},
    "weekday_evening": {"start": time(16, 30), "end": time(19, 0)},
    "friday_prayer": {"start": time(11, 30), "end": time(13, 30)},
    "sunday_evening": {"start": time(17, 0), "end": time(20, 0)}  # Family returns
}

# Pricing (in DZD)
PRICING = {
    "bicycle": {
        "hourly": 50,
        "daily": 300,
        "weekly": 1500,
        "monthly": 5000
    },
    "metro": {"single": 50, "daily": 100, "weekly": 500},
    "bus": {"single": 30, "daily": 120, "weekly": 600},
    "yassir": {
        "base_fare": 150,
        "per_km": 60,
        "per_minute": 5
    }
}