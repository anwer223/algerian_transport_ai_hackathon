#!/usr/bin/env python3
"""
Algiers Transport AI Recommendation Engine
"""

import json
import heapq
from datetime import datetime, time
from typing import List, Dict, Any
import math
import os

class TransportRecommender:
    
    
    def __init__(self, transport_data: dict, preference: str = "balanced", user_id: str = None):
       
        self.transport_data = transport_data
        self.preference = preference
        
        # Define scoring weights for each preference
        self.scoring_weights = {
            'fastest': {'time': 0.6, 'cost': 0.1, 'comfort': 0.1, 'green': 0.1, 'availability': 0.1},
            'cheapest': {'time': 0.1, 'cost': 0.6, 'comfort': 0.1, 'green': 0.1, 'availability': 0.1},
            'greenest': {'time': 0.2, 'cost': 0.2, 'comfort': 0.1, 'green': 0.4, 'availability': 0.1},
            'comfort': {'time': 0.2, 'cost': 0.2, 'comfort': 0.5, 'green': 0.05, 'availability': 0.05},
            'balanced': {'time': 0.3, 'cost': 0.3, 'comfort': 0.2, 'green': 0.1, 'availability': 0.1}
        }
        
    def get_metro_info(self) -> Dict[str, Any]:
        """Get metro information from data"""
        return self.transport_data.get("transport_systems", {}).get("metro", {})
    
    def get_tram_info(self) -> Dict[str, Any]:
        """Get tram information from data"""
        return self.transport_data.get("transport_systems", {}).get("tram", {})
    
    def get_bicycle_info(self) -> Dict[str, Any]:
        """Get bicycle sharing information from data"""
        return self.transport_data.get("transport_systems", {}).get("bicycle_sharing", {})
    
    def get_bus_info(self) -> Dict[str, Any]:
        """Get bus network information from data"""
        return self.transport_data.get("transport_systems", {}).get("bus_network", {})
    
    def get_areas(self) -> List[Dict[str, Any]]:
        """Get detailed area information from data"""
        return self.transport_data.get("areas_detailed", [])
    
    def get_distance_matrix(self) -> Dict[str, Any]:
        """Get distance matrix from data"""
        return self.transport_data.get("distance_matrix", {})
    
    def get_traffic_hotspots(self) -> List[Dict[str, Any]]:
        """Get traffic hotspots from data"""
        return self.transport_data.get("traffic_hotspots", [])
    
    def get_transport_statistics(self) -> Dict[str, Any]:
        """Get transport statistics from data"""
        return self.transport_data.get("transport_statistics", {})
    
    def _get_area_by_name(self, area_name: str) -> Dict[str, Any]:
        """Find area information by name (Arabic or French)"""
        for area in self.get_areas():
            if area_name in [area.get("name", {}).get("ar"), area.get("name", {}).get("fr")]:
                return area
        return {}
    
    def _estimate_distance(self, start_area: str, end_area: str) -> float:
        """Estimate distance between areas using distance_matrix"""
        distance_matrix = self.get_distance_matrix()
        
        # Try direct lookup
        if start_area in distance_matrix and end_area in distance_matrix[start_area]:
            return distance_matrix[start_area][end_area].get("distance_km", 5.0)
        
        # Try reverse lookup
        if end_area in distance_matrix and start_area in distance_matrix[end_area]:
            return distance_matrix[end_area][start_area].get("distance_km", 5.0)
        
        # Default distance based on areas
        area_start = self._get_area_by_name(start_area)
        area_end = self._get_area_by_name(end_area)
        
        if area_start and area_end:
            # Estimate based on city scale
            return 8.0  # Default for medium distance in Algiers
        
        return 5.0  # Default fallback
    
    def _get_traffic_multiplier(self, area_name: str, hour: int) -> float:
        """Get traffic multiplier for area at specific hour"""
        area = self._get_area_by_name(area_name)
        if not area:
            return 1.0
        
        traffic_patterns = area.get("traffic_patterns", {})
        morning_peak = traffic_patterns.get("morning_peak", "07:00-09:00")
        evening_peak = traffic_patterns.get("evening_peak", "16:00-18:00")
        
        # Check if hour is in peak time
        def is_in_peak(peak_str: str, hour: int) -> bool:
            if not peak_str or "-" not in peak_str:
                return False
            try:
                start, end = peak_str.split("-")
                start_hour = int(start.split(":")[0])
                end_hour = int(end.split(":")[0])
                return start_hour <= hour <= end_hour
            except:
                return False
        
        if is_in_peak(morning_peak, hour) or is_in_peak(evening_peak, hour):
            congestion = traffic_patterns.get("congestion_level", "medium")
            if congestion == "عالية جداً" or congestion == "شديد":
                return 1.8
            elif congestion == "ثقيل":
                return 1.5
            elif congestion == "متوسطة":
                return 1.3
        
        return 1.0
    
    def get_all_options(self, start: str, end: str, departure_time: str) -> List[Dict[str, Any]]:
        """
        Generate all possible transport options between two areas
        """
        all_options = []
        
        try:
            hour = int(departure_time.split(':')[0])
        except:
            hour = 8
        
        distance = self._estimate_distance(start, end)
        
        # 1. Metro options
        metro_options = self._generate_metro_options(start, end, distance, hour)
        all_options.extend(metro_options)
        
        # 2. Tram options
        tram_options = self._generate_tram_options(start, end, distance, hour)
        all_options.extend(tram_options)
        
        # 3. Bicycle options
        bicycle_options = self._generate_bicycle_options(start, end, distance, hour)
        all_options.extend(bicycle_options)
        
        # 4. Bus options
        bus_options = self._generate_bus_options(start, end, distance, hour)
        all_options.extend(bus_options)
        
        # 5. Walk option (for short distances)
        if distance <= 3:
            walk_options = self._generate_walk_options(start, end, distance, hour)
            all_options.extend(walk_options)
        
        # 6. Multi-modal options
        multimodal_options = self._generate_multimodal_options(start, end, distance, hour)
        all_options.extend(multimodal_options)
        
        return all_options
    
    def _generate_metro_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        """Generate metro route options"""
        options = []
        metro_info = self.get_metro_info()
        
        if not metro_info:
            return options
        
        line_1 = metro_info.get("line_1", {})
        stations = line_1.get("stations", [])
        
        # Check if areas have metro access
        start_has_metro = self._area_has_metro_access(start)
        end_has_metro = self._area_has_metro_access(end)
        
        if start_has_metro and end_has_metro:
            # Calculate base duration
            base_duration = distance * 1.2  # 1.2 minutes per km for metro
            frequency = line_1.get("frequency", {})
            
            # Add waiting time based on frequency
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                wait_time = 5  # Peak frequency
            else:
                wait_time = 10  # Off-peak frequency
            
            total_duration = base_duration + wait_time
            
            metro_option = {
                'mode': 'metro',
                'id': f'METRO_{start[:3]}_{end[:3]}',
                'description': f'🚇 مترو الجزائر - {line_1.get("line_number", "الخط 1")}',
                'duration_minutes': int(total_duration),
                'cost_dzd': 50,  # Fixed metro fare from data
                'emissions_kg': 0.05 * distance,
                'comfort_score': 0.8,
                'availability_score': 0.9,
                'details': {
                    'line': line_1.get("line_number", "الخط 1"),
                    'frequency': f'كل {wait_time} دقائق',
                    'crowding': 'عالية في ساعات الذروة' if 7 <= hour <= 9 or 16 <= hour <= 19 else 'متوسطة',
                    'stations_count': len(stations),
                    'rolling_stock': line_1.get("rolling_stock", "ألستوم")
                }
            }
            options.append(metro_option)
        
        return options
    
    def _generate_tram_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        options = []
        tram_info = self.get_tram_info()
        
        if not tram_info:
            return options
        
        line_t1 = tram_info.get("line_t1", {})
        
        # Check if areas are along tram line
        if self._area_near_tram(start) and self._area_near_tram(end):
            base_duration = distance * 1.5  # 1.5 minutes per km for tram
            
            # Add waiting time
            if 7 <= hour <= 9 or 16 <= hour <= 19:
                wait_time = 6
            else:
                wait_time = 12
            
            total_duration = base_duration + wait_time
            
            tram_option = {
                'mode': 'tram',
                'id': f'TRAM_{start[:3]}_{end[:3]}',
                'description': f'🚊 ترامواي الجزائر - {line_t1.get("line_number", "T1")}',
                'duration_minutes': int(total_duration),
                'cost_dzd': 40,  # Slightly cheaper than metro
                'emissions_kg': 0.04 * distance,
                'comfort_score': 0.7,
                'availability_score': 0.85,
                'details': {
                    'line': line_t1.get("line_number", "T1"),
                    'length_km': line_t1.get("length_km", 23.2),
                    'stations_count': line_t1.get("stations_count", 38),
                    'electric': tram_info.get("electric", True)
                }
            }
            options.append(tram_option)
        
        return options
    
    def _generate_bicycle_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        """Generate bicycle route options"""
        options = []
        bike_info = self.get_bicycle_info()
        
        if not bike_info or distance > 10:  # Not practical for long distances
            return options
        
        # Check if areas have bike stations
        start_has_bike = self._area_has_bike_station(start)
        end_has_bike = self._area_has_bike_station(end)
        
        if start_has_bike and end_has_bike:
            base_duration = distance * 4  # 4 minutes per km for bicycle
            
            # Adjust for traffic
            traffic_multiplier = self._get_traffic_multiplier(start, hour)
            total_duration = base_duration * traffic_multiplier
            
            # Get pricing from data
            pricing = bike_info.get("pricing", {})
            hourly_rate = pricing.get("hourly_rate", 50)
            estimated_cost = (distance / 15) * hourly_rate  # Assume 15 km/h average
            
            bike_option = {
                'mode': 'bicycle',
                'id': f'BIKE_{start[:3]}_{end[:3]}',
                'description': '🚴 نظام مشاركة الدراجات في الجزائر',
                'duration_minutes': int(total_duration),
                'cost_dzd': max(50, int(estimated_cost)),  # Minimum 50 DZD
                'emissions_kg': 0,
                'comfort_score': 0.6,
                'availability_score': 0.7,
                'details': {
                    'system': bike_info.get("system_name", {}).get("ar", "نظام مشاركة الدراجات"),
                    'operator': bike_info.get("operator", "بلدية الجزائر"),
                    'stations_count': bike_info.get("total_stations", 25),
                    'total_bikes': bike_info.get("total_bikes", 500),
                    'technology': bike_info.get("technology", "ذكي - تطبيق وهواتف")
                },
                'recommended_pack': self._recommend_bicycle_pack(distance)
            }
            options.append(bike_option)
        
        return options
    
    def _generate_bus_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        """Generate bus route options"""
        options = []
        bus_info = self.get_bus_info()
        
        if not bus_info:
            return options
        
        base_duration = distance * 3  # 3 minutes per km for bus
        
        # Adjust for traffic
        traffic_multiplier = max(
            self._get_traffic_multiplier(start, hour),
            self._get_traffic_multiplier(end, hour)
        )
        total_duration = base_duration * traffic_multiplier
        
        bus_option = {
            'mode': 'bus',
            'id': f'BUS_{start[:3]}_{end[:3]}',
            'description': f'🚌 شبكة الحافلات - {bus_info.get("total_lines", 120)} خط',
            'duration_minutes': int(total_duration),
            'cost_dzd': 30,  # Standard bus fare
            'emissions_kg': 0.15 * distance,
            'comfort_score': 0.5,
            'availability_score': 0.8,
            'details': {
                'total_lines': bus_info.get("total_lines", 120),
                'daily_ridership': f"{bus_info.get('daily_ridership', 500000):,}",
                'operators': bus_info.get("operators", ["ETUSA", "مؤسسات محلية"]),
                'ac_available': 'محدود'  # From data
            }
        }
        options.append(bus_option)
        
        return options
    
    def _generate_walk_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        """Generate walking options for short distances"""
        options = []
        
        if distance <= 3:  # Up to 3 km
            base_duration = distance * 15  # 15 minutes per km
            
            # Check infrastructure score for walking
            area = self._get_area_by_name(start)
            walk_score = 0.7  # Default
            if area:
                infra_score = area.get("infrastructure_score", {})
                walk_score = infra_score.get("pedestrian_friendly", 7) / 10
            
            walk_option = {
                'mode': 'walk',
                'id': f'WALK_{start[:3]}_{end[:3]}',
                'description': '👣 المشي',
                'duration_minutes': int(base_duration),
                'cost_dzd': 0,
                'emissions_kg': 0,
                'comfort_score': walk_score,
                'availability_score': 1.0,
                'details': {
                    'distance_km': f"{distance:.1f}",
                    'calories_burned': int(distance * 80),
                    'health_benefit': '30 دقيقة من التمارين',
                    'best_for': 'المسافات القصيرة، الصحة، توفير المال'
                }
            }
            options.append(walk_option)
        
        return options
    
    def _generate_multimodal_options(self, start: str, end: str, distance: float, hour: int) -> List[Dict[str, Any]]:
        """Generate multi-modal transport options"""
        options = []
        
        # Metro + Walk combination
        if distance > 3 and distance <= 15:
            metro_duration = distance * 1.2 * 0.7  # 70% by metro
            walk_duration = distance * 15 * 0.3  # 30% walking
            total_duration = metro_duration + walk_duration + 5  # +5 min transfer
            
            multimodal_option = {
                'mode': 'multimodal',
                'id': f'MULTI_{start[:3]}_{end[:3]}',
                'description': '🚇 + 👣 مترو + مشي',
                'duration_minutes': int(total_duration),
                'cost_dzd': 50,  # Metro fare only
                'emissions_kg': 0.05 * distance * 0.7,
                'comfort_score': 0.6,
                'availability_score': 0.8,
                'details': {
                    'combination': ['مترو للمسافة الرئيسية', 'مشي للمسافة الأخيرة'],
                    'transfer_time': '5 دقائق',
                    'best_for': 'تجنب الازدحام، مسافات متوسطة',
                    'total_distance': f"{distance:.1f} كم"
                }
            }
            options.append(multimodal_option)
        
        # Bus + Metro combination for longer distances
        if distance > 10:
            bus_duration = distance * 3 * 0.4
            metro_duration = distance * 1.2 * 0.6
            total_duration = bus_duration + metro_duration + 10  # +10 min transfer
            
            multimodal_option2 = {
                'mode': 'multimodal',
                'id': f'MULTI2_{start[:3]}_{end[:3]}',
                'description': '🚌 + 🚇 حافلة + مترو',
                'duration_minutes': int(total_duration),
                'cost_dzd': 80,  # Bus + Metro
                'emissions_kg': 0.15 * distance * 0.4 + 0.05 * distance * 0.6,
                'comfort_score': 0.5,
                'availability_score': 0.9,
                'details': {
                    'combination': ['حافلة إلى محطة المترو', 'مترو إلى قرب الوجهة'],
                    'transfer_time': '10 دقائق',
                    'best_for': 'المسافات الطويلة، توفير التكلفة',
                    'cost_saving': 'أقل من التكسي'
                }
            }
            options.append(multimodal_option2)
        
        return options
    
    def _area_has_metro_access(self, area_name: str) -> bool:
        """Check if area has metro access"""
        area = self._get_area_by_name(area_name)
        if area:
            transport_access = area.get("transport_access", {})
            metro_stations = transport_access.get("metro_stations", 0)
            return metro_stations > 0
        
        # Check hardcoded areas from data
        if area_name in ["الجزائر الوسطى", "Centre-ville d'Alger"]:
            return True
        if area_name in ["الحراش", "El Harrach"]:
            return True
        
        return False
    
    def _area_near_tram(self, area_name: str) -> bool:
        """Check if area is near tram line"""
        area = self._get_area_by_name(area_name)
        if area:
            transport_access = area.get("transport_access", {})
            tram_stations = transport_access.get("tram_stations", 0)
            return tram_stations > 0
        
        return False
    
    def _area_has_bike_station(self, area_name: str) -> bool:
        """Check if area has bicycle sharing station"""
        area = self._get_area_by_name(area_name)
        if area:
            transport_access = area.get("transport_access", {})
            bicycle_stations = transport_access.get("bicycle_stations", 0)
            return bicycle_stations > 0
        
        return False
    
    def _recommend_bicycle_pack(self, distance: float) -> Dict[str, Any]:
        """Recommend optimal bicycle pack based on distance"""
        bike_info = self.get_bicycle_info()
        pricing = bike_info.get("pricing", {})
        
        # Estimate usage time (assuming 15 km/h average)
        hours = distance / 15
        
        if hours <= 1:
            return {
                'type': 'hourly',
                'cost': pricing.get("hourly_rate", 50),
                'recommended': 'مناسب للرحلات القصيرة'
            }
        elif hours <= 8:
            return {
                'type': 'daily',
                'cost': pricing.get("daily_rate", 300),
                'recommended': 'أفضل ليوم كامل'
            }
        else:
            return {
                'type': 'monthly',
                'cost': pricing.get("monthly_rate", 5000),
                'recommended': 'مثالي للمستخدمين المنتظمين'
            }
    
    def score_option(self, option: Dict[str, Any]) -> float:
        """
        Calculate AI score for a transport option (0-100)
        Higher score = better recommendation
        """
        weights = self.scoring_weights.get(self.preference, self.scoring_weights['balanced'])
        
        # Normalize factors to 0-1 scale
        # Time: shorter = better
        max_time = 120
        time_score = 1.0 - min(option['duration_minutes'] / max_time, 1.0)
        
        # Cost: cheaper = better
        max_cost = 1000
        cost_score = 1.0 - min(option['cost_dzd'] / max_cost, 1.0)
        
        # Comfort: from option
        comfort_score = option.get('comfort_score', 0.5)
        
        # Green: lower emissions = better
        max_emissions = 2.0
        green_score = 1.0 - min(option['emissions_kg'] / max_emissions, 1.0)
        
        # Availability: from option
        availability_score = option.get('availability_score', 0.8)
        
        # Calculate weighted score
        weighted_score = (
            weights['time'] * time_score +
            weights['cost'] * cost_score +
            weights['comfort'] * comfort_score +
            weights['green'] * green_score +
            weights['availability'] * availability_score
        )
        
        # Convert to 0-100 scale
        return round(weighted_score * 100, 1)
    
    def get_top_recommendations(self, start: str, end: str, departure_time: str, 
                               top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Get top N transport recommendations with AI scores
        """
        # Get all possible options
        all_options = self.get_all_options(start, end, departure_time)
        
        if not all_options:
            # Fallback option if no specific options found
            distance = self._estimate_distance(start, end)
            base_duration = distance * 2.5
            fallback_option = {
                'mode': 'estimated',
                'id': f'EST_{start[:3]}_{end[:3]}',
                'description': f'🚗 تقدير عام من {start} إلى {end}',
                'duration_minutes': int(base_duration),
                'cost_dzd': int(distance * 50),
                'emissions_kg': distance * 0.15,
                'comfort_score': 0.7,
                'availability_score': 0.8,
                'details': {
                    'distance': f"{distance:.1f} كم",
                    'recommendation': 'استخدم الحافلات أو التكسي',
                    'note': 'لا توجد معلومات مفصلة لهذا المسار'
                }
            }
            all_options.append(fallback_option)
        
        # Score each option
        for option in all_options:
            option['ai_score'] = self.score_option(option)
            option['explanation'] = self._generate_explanation(option)
        
        # Sort by AI score (descending)
        all_options.sort(key=lambda x: x['ai_score'], reverse=True)
        
        # Get top recommendations
        return all_options[:top_n]
    
    def _generate_explanation(self, option: Dict[str, Any]) -> str:
        """Generate human-readable explanation for AI choice"""
        score = option['ai_score']
        mode = option['mode']
        
        explanations = {
            'metro': f"🚇 المترو (نتيجة الذكاء الاصطناعي: {score}/100) - سريع وموثوق. يتجنب الازدحام المروري تماماً.",
            'tram': f"🚊 الترامواي (نتيجة الذكاء الاصطناعي: {score}/100) - صديق للبيئة مع تغطية واسعة.",
            'bicycle': f"🚴 الدراجة (نتيجة الذكاء الاصطناعي: {score}/100) - صديقة للبيئة وصحية. ممتازة للمسافات القصيرة والمتوسطة.",
            'bus': f"🚌 الحافلة (نتيجة الذكاء الاصطناعي: {score}/100) - اقتصادية مع تغطية واسعة. الأفضل للمسافرين بميزانية محدودة.",
            'walk': f"👣 المشي (نتيجة الذكاء الاصطناعي: {score}/100) - مجاني، صحي، وصفر انبعاثات.",
            'multimodal': f"🔄 متعدد الوسائط (نتيجة الذكاء الاصطناعي: {score}/100) - أفضل ما في العالمين: السرعة + الاقتصادية.",
            'estimated': f"📍 تقدير (نتيجة الذكاء الاصطناعي: {score}/100) - خيار عام بناءً على المسافة."
        }
        
        base = explanations.get(mode, f"هذا الخيار حصل على {score}/100 من الذكاء الاصطناعي.")
        
        # Add cost savings
        if option['cost_dzd'] < 100:
            base += " 💰 قيمة ممتازة!"
        
        if option['emissions_kg'] < 0.1:
            base += " 🌿 خيار صديق للبيئة!"
        
        # Add time comparison
        if option['duration_minutes'] < 30:
            base += " ⏱️ خيار سريع!"
        
        return base
