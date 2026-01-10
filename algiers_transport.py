#!/usr/bin/env python3
import math
import heapq
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
import webbrowser
import requests

# ============================================================================
# COMPLETE ALGIERS TRANSPORT DATA
# ============================================================================

class AlgiersData:
    
    @staticmethod
    def get_data():
      
        return {
            "metadata": {
                "city": "Algiers",
                "country": "Algeria",
                "population": 4000000,
                "area_sqkm": 363,
                "last_updated": "2024-01-15"
            },
            
            "areas": [
                {"id": 1, "name": "City Center", "arabic_name": "الجزائر الوسطى", "type": "commercial",
                 "coordinates": {"lat": 36.7763, "lng": 3.0587},
                 "transport": ["metro", "bus", "bicycle", "walk", "tram"],
                 "attractions": ["Casbah", "Great Mosque", "National Museum"]},
                
                {"id": 2, "name": "El Harrach", "arabic_name": "الحراش", "type": "residential",
                 "coordinates": {"lat": 36.7200, "lng": 3.1300},
                 "transport": ["metro", "tram", "bus", "bicycle"],
                 "attractions": ["Botanical Garden", "Zoo", "Olympic Stadium"]},
                
                {"id": 3, "name": "Bab El Oued", "arabic_name": "باب الوادي", "type": "historic",
                 "coordinates": {"lat": 36.7896, "lng": 3.0572},
                 "transport": ["bus", "walk"],
                 "attractions": ["Martyr's Square", "Old Port"]},
                
                {"id": 4, "name": "Kouba", "arabic_name": "القبة", "type": "residential",
                 "coordinates": {"lat": 36.7333, "lng": 3.0833},
                 "transport": ["bus", "bicycle", "walk"],
                 "attractions": ["University District", "Local Markets"]},
                
                {"id": 5, "name": "El Biar", "arabic_name": "البيار", "type": "residential",
                 "coordinates": {"lat": 36.7667, "lng": 3.0333},
                 "transport": ["bus", "walk"],
                 "attractions": ["Diplomatic Quarter", "Parks"]},
                
                {"id": 6, "name": "Hydra", "arabic_name": "حيدرة", "type": "residential",
                 "coordinates": {"lat": 36.7500, "lng": 3.0333},
                 "transport": ["bus", "walk"],
                 "attractions": ["Upscale Residences", "Shopping"]}
            ],
            
            "transport_modes": {
                "metro": {
                    "name": "Algiers Metro",
                    "emoji": "🚇",
                    "color": "#FF0000",
                    "speed_kmh": 40,
                    "cost_per_km": 5,
                    "base_cost": 50,
                    "emissions_kg_per_km": 0.05,
                    "comfort": 0.8,
                    "reliability": 0.9,
                    "description": "Fast underground metro system"
                },
                "bus": {
                    "name": "City Bus",
                    "emoji": "🚌",
                    "color": "#0000FF",
                    "speed_kmh": 20,
                    "cost_per_km": 2,
                    "base_cost": 30,
                    "emissions_kg_per_km": 0.15,
                    "comfort": 0.5,
                    "reliability": 0.7,
                    "description": "Extensive bus network"
                },
                "bicycle": {
                    "name": "Bike Sharing",
                    "emoji": "🚴",
                    "color": "#00FF00",
                    "speed_kmh": 15,
                    "cost_per_km": 3,
                    "base_cost": 50,
                    "emissions_kg_per_km": 0,
                    "comfort": 0.6,
                    "reliability": 0.8,
                    "description": "Shared bicycle system"
                },
                "walk": {
                    "name": "Walking",
                    "emoji": "👣",
                    "color": "#00FFFF",
                    "speed_kmh": 5,
                    "cost_per_km": 0,
                    "base_cost": 0,
                    "emissions_kg_per_km": 0,
                    "comfort": 0.7,
                    "reliability": 1.0,
                    "description": "On foot"
                },
                "tram": {
                    "name": "Tramway",
                    "emoji": "🚊",
                    "color": "#FFFF00",
                    "speed_kmh": 25,
                    "cost_per_km": 4,
                    "base_cost": 40,
                    "emissions_kg_per_km": 0.04,
                    "comfort": 0.7,
                    "reliability": 0.85,
                    "description": "Electric tram system"
                }
            },
            
            "distance_matrix": {
                "City Center": {
                    "El Harrach": 8.5,
                    "Bab El Oued": 2.0,
                    "Kouba": 5.5,
                    "El Biar": 3.0,
                    "Hydra": 4.0
                },
                "El Harrach": {
                    "City Center": 8.5,
                    "Bab El Oued": 10.0,
                    "Kouba": 7.0,
                    "El Biar": 9.0,
                    "Hydra": 8.0
                },
                "Bab El Oued": {
                    "City Center": 2.0,
                    "El Harrach": 10.0,
                    "Kouba": 4.0,
                    "El Biar": 3.5,
                    "Hydra": 3.0
                },
                "Kouba": {
                    "City Center": 5.5,
                    "El Harrach": 7.0,
                    "Bab El Oued": 4.0,
                    "El Biar": 2.5,
                    "Hydra": 2.0
                }
            }
        }

# ============================================================================
# WEATHER SERVICE
# ============================================================================

class WeatherService:
    """Weather service for Algiers"""
    
    def __init__(self):
        self.api_key = "3a773fc067b71064a7eb7cf4452a0289"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self) -> Dict[str, Any]:
        """Get current weather in Algiers"""
        try:
            params = {
                "q": "Algiers,DZ",
                "appid": self.api_key,
                "units": "metric",
                "lang": "en"
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                return self._parse_weather(response.json())
        except:
            pass
        
        return self._get_mock_weather()
    
    def _parse_weather(self, data: Dict) -> Dict[str, Any]:
        """Parse weather data"""
        return {
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"] * 3.6,
            "icon": data["weather"][0]["icon"]
        }
    
    def _get_mock_weather(self) -> Dict[str, Any]:
        """Get mock weather"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            temp = 22
            condition = "Sunny"
        elif 12 <= hour < 18:
            temp = 26
            condition = "Partly Cloudy"
        elif 18 <= hour < 24:
            temp = 20
            condition = "Clear"
        else:
            temp = 18
            condition = "Clear"
        
        return {
            "temperature": temp,
            "feels_like": temp + 2,
            "humidity": 65,
            "description": condition,
            "wind_speed": 12.5,
            "icon": "01d"
        }
    
    def get_weather_impact(self, weather: Dict, mode: str) -> float:
        """Calculate weather impact factor"""
        temp = weather["temperature"]
        condition = weather["description"].lower()
        
        impact = 1.0
        
        # Temperature impact
        if mode in ["bicycle", "walk"]:
            if temp > 35:
                impact *= 0.4
            elif temp > 30:
                impact *= 0.7
            elif 20 <= temp <= 25:
                impact *= 1.2
        
        # Rain impact
        if "rain" in condition:
            if mode in ["bicycle", "walk"]:
                impact *= 0.3
        
        return max(0.5, min(1.5, impact))

# ============================================================================
# SHORTEST PATH ALGORITHM
# ============================================================================

class TransportGraph:
    """Graph for finding shortest paths"""
    
    def __init__(self, data: Dict):
        self.data = data
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Dict[str, List[Tuple[str, float, str]]]:
        """Build transport graph"""
        graph = {}
        data = self.data
        
        for area in data["areas"]:
            area_name = area["name"]
            graph[area_name] = []
            
            for other_area in data["areas"]:
                other_name = other_area["name"]
                if area_name == other_name:
                    continue
                
                # Get distance
                distance = self._get_distance(area_name, other_name)
                if distance == 0:
                    continue
                
                # Find common transport
                area_modes = set(area.get("transport", []))
                other_modes = set(other_area.get("transport", []))
                common_modes = area_modes.intersection(other_modes)
                
                for mode in common_modes:
                    if mode in data["transport_modes"]:
                        speed = data["transport_modes"][mode]["speed_kmh"]
                        time = (distance / speed) * 60
                        
                        # Add waiting time
                        if mode in ["metro", "bus", "tram"]:
                            time += 5
                        
                        graph[area_name].append((other_name, time, mode))
        
        return graph
    
    def _get_distance(self, start: str, end: str) -> float:
        """Get distance between areas"""
        distances = self.data["distance_matrix"]
        
        if start in distances and end in distances[start]:
            return distances[start][end]
        if end in distances and start in distances[end]:
            return distances[end][start]
        
        # Try to find coordinates
        start_coords = None
        end_coords = None
        
        for area in self.data["areas"]:
            if area["name"] == start:
                start_coords = area.get("coordinates")
            if area["name"] == end:
                end_coords = area.get("coordinates")
        
        if start_coords and end_coords:
            return self._calculate_distance(start_coords, end_coords)
        
        return 5.0
    
    def _calculate_distance(self, coord1: Dict, coord2: Dict) -> float:
        """Calculate distance between coordinates"""
        lat1, lon1 = coord1["lat"], coord1["lng"]
        lat2, lon2 = coord2["lat"], coord2["lng"]
        
        # Simple approximation
        dlat = (lat2 - lat1) * 111.32
        dlon = (lon2 - lon1) * 111.32 * math.cos(math.radians((lat1 + lat2) / 2))
        
        return math.sqrt(dlat**2 + dlon**2)
    
    def dijkstra(self, start: str, end: str) -> Tuple[List[str], float, List[str]]:
        """Dijkstra's shortest path algorithm"""
        if start not in self.graph or end not in self.graph:
            return [], float('inf'), []
        
        pq = [(0, start, [], [])]
        visited = set()
        
        while pq:
            current_time, current_node, path, modes = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            new_path = path + [current_node]
            
            if current_node == end:
                return new_path, current_time, modes
            
            for neighbor, time_cost, mode in self.graph[current_node]:
                if neighbor not in visited:
                    new_modes = modes + [mode]
                    heapq.heappush(pq, (current_time + time_cost, neighbor, new_path, new_modes))
        
        return [], float('inf'), []
    
    def find_paths(self, start: str, end: str, max_paths: int = 5) -> List[Dict[str, Any]]:
        """Find multiple paths"""
        paths = []
        
        # Get shortest path
        path, time, modes = self.dijkstra(start, end)
        if path:
            paths.append({
                "path": path,
                "total_time": time,
                "modes": modes
            })
        
        return paths

# ============================================================================
# SMART RECOMMENDATION ENGINE
# ============================================================================

class SmartRecommendationEngine:
    """Smart engine that automatically finds best for each criteria"""
    
    def __init__(self, data: Dict, weather_service: WeatherService):
        self.data = data
        self.weather_service = weather_service
        self.graph = TransportGraph(data)
    
    def get_all_recommendations(self, start: str, end: str) -> Dict[str, Dict[str, Any]]:
        """Get best recommendations for ALL criteria automatically"""
        if not self._is_valid_area(start) or not self._is_valid_area(end):
            return {}
        
        weather = self.weather_service.get_weather()
        all_paths = self.graph.find_paths(start, end, max_paths=10)
        
        if not all_paths:
            return {}
        
        # Evaluate all paths with all criteria
        all_recommendations = []
        for path_info in all_paths:
            for criteria in ["fastest", "cheapest", "greenest", "balanced"]:
                rec = self._evaluate_path(path_info, weather, criteria)
                if rec:
                    all_recommendations.append(rec)
        
        # Find best for each category
        results = {}
        
        # 1. FASTEST (lowest time)
        fastest = min(all_recommendations, key=lambda x: x["metrics"]["total_time"])
        results["fastest"] = {
            "recommendation": fastest,
            "title": "🚀 FASTEST ROUTE",
            "subtitle": f"Time: {fastest['metrics']['total_time']} min",
            "icon": "🏎️"
        }
        
        # 2. CHEAPEST (lowest cost)
        cheapest = min(all_recommendations, key=lambda x: x["metrics"]["total_cost"])
        results["cheapest"] = {
            "recommendation": cheapest,
            "title": "💰 CHEAPEST ROUTE",
            "subtitle": f"Cost: {cheapest['metrics']['total_cost']} DZD",
            "icon": "💰"
        }
        
        # 3. GREENEST (lowest emissions)
        greenest = min(all_recommendations, key=lambda x: x["metrics"]["total_emissions"])
        results["greenest"] = {
            "recommendation": greenest,
            "title": "🌿 GREENEST ROUTE",
            "subtitle": f"Emissions: {greenest['metrics']['total_emissions']} kg CO₂",
            "icon": "🌿"
        }
        
        # 4. BEST COMFORT (highest comfort)
        most_comfortable = max(all_recommendations, key=lambda x: x["metrics"]["comfort"])
        results["comfort"] = {
            "recommendation": most_comfortable,
            "title": "🛋️ MOST COMFORTABLE",
            "subtitle": f"Comfort: {most_comfortable['metrics']['comfort']:.1f}/1.0",
            "icon": "🛋️"
        }
        
        # 5. BEST OVERALL (highest balanced score)
        balanced_recs = [r for r in all_recommendations if r["criteria"] == "balanced"]
        if balanced_recs:
            best_overall = max(balanced_recs, key=lambda x: x["score"])
            results["best"] = {
                "recommendation": best_overall,
                "title": "🏆 BEST OVERALL",
                "subtitle": f"AI Score: {best_overall['score']}/100",
                "icon": "🏆"
            }
        
        # 6. SMART CHOICE (best combination of speed and price)
        smart_choices = []
        for rec in all_recommendations:
            # Calculate value score (time vs cost balance)
            time_norm = 1 - (rec["metrics"]["total_time"] / 120)  # Normalize to 0-1
            cost_norm = 1 - (rec["metrics"]["total_cost"] / 500)  # Normalize to 0-1
            value_score = (time_norm * 0.6) + (cost_norm * 0.4)  # Weighted
            smart_choices.append((rec, value_score))
        
        if smart_choices:
            smart_choice = max(smart_choices, key=lambda x: x[1])[0]
            results["smart"] = {
                "recommendation": smart_choice,
                "title": "🤖 SMART CHOICE",
                "subtitle": "Best balance of speed and price",
                "icon": "🤖"
            }
        
        return results
    
    def _is_valid_area(self, area_name: str) -> bool:
        """Check if area is valid"""
        for area in self.data["areas"]:
            if area["name"].lower() == area_name.lower():
                return True
            if area.get("arabic_name", "").lower() == area_name.lower():
                return True
        return False
    
    def _evaluate_path(self, path_info: Dict, weather: Dict, criteria: str) -> Optional[Dict[str, Any]]:
        """Evaluate a path"""
        path = path_info["path"]
        modes = path_info["modes"]
        base_time = path_info["total_time"]
        
        if not path or len(path) < 2:
            return None
        
        # Calculate metrics
        metrics = self._calculate_metrics(path, modes, base_time, weather)
        
        # Calculate score based on criteria
        score = self._calculate_score(metrics, criteria)
        
        return {
            "path": path,
            "modes": modes,
            "metrics": metrics,
            "score": round(score, 1),
            "criteria": criteria,
            "weather": weather
        }
    
    def _calculate_metrics(self, path: List[str], modes: List[str], base_time: float, weather: Dict) -> Dict[str, Any]:
        """Calculate path metrics"""
        total_distance = 0
        total_cost = 0
        total_emissions = 0
        avg_comfort = 0
        
        # Calculate for each segment
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            mode = modes[i] if i < len(modes) else "walk"
            
            # Get distance
            distance = self._get_distance(start, end)
            total_distance += distance
            
            # Get mode data
            mode_data = self.data["transport_modes"].get(mode, {})
            
            # Cost
            cost = mode_data.get("base_cost", 0) + (distance * mode_data.get("cost_per_km", 0))
            total_cost += cost
            
            # Emissions
            emissions = distance * mode_data.get("emissions_kg_per_km", 0)
            total_emissions += emissions
            
            # Comfort
            comfort = mode_data.get("comfort", 0.5)
            avg_comfort += comfort
        
        # Averages
        if len(path) > 1:
            avg_comfort /= (len(path) - 1)
        
        # Apply weather impact
        weather_factor = self.weather_service.get_weather_impact(weather, modes[0] if modes else "walk")
        adjusted_time = base_time * weather_factor
        
        return {
            "total_time": round(adjusted_time, 1),
            "total_distance": round(total_distance, 1),
            "total_cost": round(total_cost),
            "total_emissions": round(total_emissions, 2),
            "comfort": round(avg_comfort, 2),
            "weather_factor": round(weather_factor, 2)
        }
    
    def _get_distance(self, start: str, end: str) -> float:
        """Get distance between areas"""
        distances = self.data["distance_matrix"]
        
        if start in distances and end in distances[start]:
            return distances[start][end]
        if end in distances and start in distances[end]:
            return distances[end][start]
        
        return 5.0
    
    def _calculate_score(self, metrics: Dict, criteria: str) -> float:
        """Calculate score based on criteria"""
        if criteria == "fastest":
            # Score based on time (lower time = higher score)
            time_score = 100 - (metrics["total_time"] * 2)
            cost_penalty = metrics["total_cost"] * 0.1
            return max(0, time_score - cost_penalty)
        
        elif criteria == "cheapest":
            # Score based on cost (lower cost = higher score)
            cost_score = 100 - (metrics["total_cost"] * 0.4)
            time_penalty = metrics["total_time"] * 0.5
            return max(0, cost_score - time_penalty)
        
        elif criteria == "greenest":
            # Score based on emissions (lower emissions = higher score)
            emission_score = 100 - (metrics["total_emissions"] * 20)
            comfort_bonus = metrics["comfort"] * 10
            return max(0, emission_score + comfort_bonus)
        
        else:  # balanced
            # Balanced score considering all factors
            time_score = 1 - min(metrics["total_time"] / 120, 1)
            cost_score = 1 - min(metrics["total_cost"] / 500, 1)
            emission_score = 1 - min(metrics["total_emissions"] / 5, 1)
            comfort_score = metrics["comfort"]
            
            weighted_score = (
                time_score * 0.3 +
                cost_score * 0.3 +
                emission_score * 0.2 +
                comfort_score * 0.2
            )
            
            return max(0, min(100, weighted_score * 100))
    
    def get_google_maps_url(self, start: str, end: str, mode: str = "transit") -> str:
        """Generate Google Maps URL"""
        start_coords = None
        end_coords = None
        
        for area in self.data["areas"]:
            if area["name"].lower() == start.lower():
                start_coords = area["coordinates"]
            if area["name"].lower() == end.lower():
                end_coords = area["coordinates"]
        
        if not start_coords or not end_coords:
            return ""
        
        # Create URL
        url = f"https://www.google.com/maps/dir/"
        url += f"{start_coords['lat']},{start_coords['lng']}/"
        url += f"{end_coords['lat']},{end_coords['lng']}/"
        
        # Add travel mode
        if mode == "walking":
            url += "data=!4m2!4m1!3e2"
        elif mode == "bicycling":
            url += "data=!4m2!4m1!3e1"
        elif mode == "transit":
            url += "data=!4m2!4m1!3e3"
        else:
            url += "data=!4m2!4m1!3e0"
        
        return url

# ============================================================================
# IMPROVED TERMINAL INTERFACE
# ============================================================================

class SmartTerminalInterface:
    """Smart terminal that shows best options automatically"""
    
    def __init__(self):
        self.data = AlgiersData.get_data()
        self.weather_service = WeatherService()
        self.recommender = SmartRecommendationEngine(self.data, self.weather_service)
        self.colors = {
            "red": "1;31",
            "green": "1;32",
            "yellow": "1;33",
            "blue": "1;34",
            "purple": "1;35",
            "cyan": "1;36",
            "white": "1;37"
        }
    
    def print_color(self, text: str, color: str = "white"):
        """Print colored text"""
        code = self.colors.get(color, "1;37")
        print(f"\033[{code}m{text}\033[0m")
    
    def print_header(self):
        """Print header"""
        print("\n" + "="*80)
        self.print_color("🇩🇿  ALGIERS SMART TRANSPORT AI", "blue")
        self.print_color("🤖  Automatically finds BEST routes for you", "cyan")
        print("="*80)
    
    def print_areas(self):
        """Print available areas"""
        areas = self.data["areas"]
        
        print("\n" + "-"*80)
        self.print_color("📍  AVAILABLE AREAS IN ALGIERS:", "yellow")
        print("-"*80)
        
        print("\n  English Name          Arabic Name           Transport Available")
        print("  ────────────────────  ───────────────────  ───────────────────")
        
        for area in areas:
            eng = area["name"]
            ar = area.get("arabic_name", "")
            transport = ", ".join(area.get("transport", []))
            print(f"  • {eng:<20} {ar:<20} {transport}")
    
    def print_weather(self, weather: Dict):
        """Print weather"""
        print("\n" + "-"*80)
        self.print_color("🌤️  CURRENT WEATHER IN ALGIERS:", "cyan")
        print("-"*80)
        
        temp = weather["temperature"]
        condition = weather["description"]
        
        if "rain" in condition.lower():
            icon = "🌧️"
        elif "cloud" in condition.lower():
            icon = "☁️"
        else:
            icon = "☀️"
        
        print(f"\n  {icon}  {condition}")
        print(f"  🌡️  Temperature: {temp}°C (Feels like: {weather['feels_like']}°C)")
        print(f"  💧  Humidity: {weather['humidity']}%")
        print(f"  💨  Wind: {weather['wind_speed']:.1f} km/h")
        
        # Weather advice
        if "rain" in condition.lower():
            self.print_color("  ⚠️  Rainy weather - Metro/Bus recommended", "yellow")
        elif temp > 30:
            self.print_color("  ⚠️  Hot weather - Air-conditioned transport recommended", "yellow")
        elif temp < 15:
            self.print_color("  ⚠️  Cool weather - Consider warmer transport options", "yellow")
    
    def print_recommendation_card(self, rec_data: Dict, category: str):
        """Print a recommendation card"""
        rec = rec_data["recommendation"]
        title = rec_data["title"]
        subtitle = rec_data["subtitle"]
        icon = rec_data["icon"]
        
        path = rec["path"]
        modes = rec["modes"]
        metrics = rec["metrics"]
        score = rec["score"]
        
        # Mode emojis
        mode_emojis = {
            "metro": "🚇",
            "bus": "🚌",
            "bicycle": "🚴",
            "walk": "👣",
            "tram": "🚊"
        }
        
        # Color based on category
        color_map = {
            "fastest": "blue",
            "cheapest": "green",
            "greenest": "cyan",
            "comfort": "purple",
            "best": "yellow",
            "smart": "white"
        }
        color = color_map.get(category, "white")
        
        print(f"\n{'━'*80}")
        self.print_color(f"{icon}  {title}", color)
        self.print_color(f"   {subtitle}", color)
        print(f"{'━'*80}")
        
        # Key metrics
        print(f"\n  📊  KEY METRICS:")
        print(f"     ⏱️  Time: {metrics['total_time']} minutes")
        print(f"     💰  Cost: {metrics['total_cost']} DZD")
        print(f"     🌿  Emissions: {metrics['total_emissions']} kg CO₂")
        print(f"     🛋️  Comfort: {metrics['comfort']:.1f}/1.0")
        print(f"     ⭐  AI Score: {score}/100")
        
        # Route summary
        print(f"\n  🗺️  ROUTE: {path[0]} → {path[-1]}")
        print(f"     Distance: {metrics['total_distance']} km")
        print(f"     Segments: {len(path)-1}")
        
        # Transport modes with emojis
        if modes:
            mode_display = []
            for mode in modes:
                emoji = mode_emojis.get(mode, "📍")
                mode_name = self.data["transport_modes"].get(mode, {}).get("name", mode)
                mode_display.append(f"{emoji} {mode_name}")
            print(f"\n  🚦  TRANSPORT: {' → '.join(mode_display)}")
        
        # Weather impact
        if metrics['weather_factor'] < 0.8:
            self.print_color(f"  ⚠️  Weather impact: Reduced efficiency ({metrics['weather_factor']})", "yellow")
        elif metrics['weather_factor'] > 1.1:
            self.print_color(f"  ✅  Weather impact: Enhanced efficiency ({metrics['weather_factor']})", "green")
        
        # Google Maps option
        print(f"\n  🗺️  Type '{category}' to open this route in Google Maps")
    
    def print_comparison_table(self, results: Dict[str, Dict]):
        """Print comparison table of all options"""
        print("\n" + "="*80)
        self.print_color("📊  COMPARISON TABLE", "purple")
        print("="*80)
        
        print("\n  Category      Time(min)  Cost(DZD)  Emissions(kg)  Comfort  Score")
        print("  ───────────  ─────────  ─────────  ─────────────  ───────  ─────")
        
        categories = ["fastest", "cheapest", "greenest", "comfort", "best", "smart"]
        
        for cat in categories:
            if cat in results:
                rec = results[cat]["recommendation"]
                metrics = rec["metrics"]
                
                icon = results[cat]["icon"]
                time = f"{metrics['total_time']:>6.1f}"
                cost = f"{metrics['total_cost']:>8}"
                emissions = f"{metrics['total_emissions']:>11.2f}"
                comfort = f"{metrics['comfort']:>7.1f}"
                score = f"{rec['score']:>5.1f}"
                
                print(f"  {icon} {cat:<10} {time}  {cost}  {emissions}  {comfort}  {score}")
        
        print(f"\n  💡  Legend: 🏎️=Fastest  💰=Cheapest  🌿=Greenest  🛋️=Comfort  🏆=Best  🤖=Smart")
    
    def get_area(self, prompt: str) -> Optional[str]:
        """Get valid area input"""
        while True:
            area = input(f"\n  {prompt}: ").strip()
            
            if not area:
                self.print_color("  ❌  Please enter a location", "red")
                continue
            
            if area.lower() in ["exit", "quit", "q"]:
                return None
            
            if area.lower() == "areas":
                self.print_areas()
                continue
            
            # Check if valid
            valid = False
            correct_name = area
            for a in self.data["areas"]:
                if a["name"].lower() == area.lower():
                    valid = True
                    correct_name = a["name"]
                    break
                elif a.get("arabic_name", "").lower() == area.lower():
                    valid = True
                    correct_name = a["name"]
                    break
            
            if valid:
                return correct_name
            else:
                self.print_color(f"  ❌  '{area}' not found", "red")
                self.print_color("  💡  Type 'areas' to see available areas", "yellow")
    
    def open_google_maps(self, start: str, end: str, mode: str = "transit"):
        """Open Google Maps"""
        url = self.recommender.get_google_maps_url(start, end, mode)
        
        if not url:
            self.print_color("  ❌  Could not generate URL", "red")
            return
        
        self.print_color("\n  🌐  Opening Google Maps...", "cyan")
        
        try:
            webbrowser.open(url)
            self.print_color("  ✅  Google Maps opened in browser", "green")
        except:
            self.print_color("  ⚠️  Could not open browser", "yellow")
            print(f"  🔗  URL: {url}")
    
    def run(self):
        """Main application loop"""
        self.print_header()
        
        # Print city info
        metadata = self.data["metadata"]
        print(f"\n🏙️  City: {metadata['city']}")
        print(f"👥  Population: {metadata['population']:,}")
        print(f"📏  Area: {metadata['area_sqkm']} km²")
        
        self.print_areas()
        
        while True:
            try:
                print("\n" + "="*80)
                self.print_color("📍  ENTER YOUR JOURNEY", "blue")
                print("="*80)
                
                # Get start location
                start = self.get_area("Start location")
                if start is None:
                    self.print_color("\n👋  Goodbye! Safe travels!", "green")
                    break
                
                # Get end location
                end = self.get_area("End location")
                if end is None:
                    self.print_color("\n👋  Goodbye! Safe travels!", "green")
                    break
                
                if start.lower() == end.lower():
                    self.print_color("  ⚠️  Start and end are the same!", "yellow")
                    continue
                
                # Get weather
                weather = self.weather_service.get_weather()
                self.print_weather(weather)
                
                # Get ALL recommendations automatically
                self.print_color(f"\n🤖  Finding BEST routes from {start} to {end}...", "cyan")
                print("   (Analyzing fastest, cheapest, greenest, most comfortable, and best overall)")
                
                results = self.recommender.get_all_recommendations(start, end)
                
                if not results:
                    self.print_color("  ❌  No routes found for this journey", "red")
                    continue
                
                # Show all recommendations
                print("\n" + "⭐"*80)
                self.print_color("  🎯  BEST ROUTES FOR YOUR JOURNEY", "green")
                print("⭐"*80)
                
                # Show each recommendation
                categories = ["fastest", "cheapest", "greenest", "comfort", "best", "smart"]
                
                for category in categories:
                    if category in results:
                        self.print_recommendation_card(results[category], category)
                
                # Show comparison table
                self.print_comparison_table(results)
                
                # Google Maps integration
                print("\n" + "-"*80)
                self.print_color("  🗺️  OPEN IN GOOGLE MAPS", "cyan")
                print("-"*80)
                
                print("\n  Choose a route to open in Google Maps:")
                print("    fastest  - Open fastest route")
                print("    cheapest - Open cheapest route")
                print("    greenest - Open greenest route")
                print("    best     - Open best overall route")
                print("    smart    - Open smart choice route")
                print("    all      - Open all routes")
                print("    skip     - Skip Google Maps")
                
                while True:
                    choice = input("\n  Your choice: ").strip().lower()
                    
                    if choice in ["exit", "quit"]:
                        self.print_color("\n👋  Goodbye!", "green")
                        return
                    
                    if choice == "skip":
                        break
                    
                    if choice == "all":
                        # Open all routes
                        for cat in ["fastest", "cheapest", "greenest", "best"]:
                            if cat in results:
                                self.open_google_maps(start, end, "transit")
                        break
                    
                    if choice in results:
                        self.open_google_maps(start, end, "transit")
                        break
                    
                    if choice in ["fastest", "cheapest", "greenest", "best", "smart"]:
                        self.print_color(f"  ℹ️  No {choice} route available", "yellow")
                    else:
                        self.print_color("  ❌  Invalid choice", "red")
                        print("  Valid choices: fastest, cheapest, greenest, best, smart, all, skip")
                
                # Continue or exit
                print("\n" + "-"*80)
                again = input("  🔄  Find another route? (Y/n): ").strip().lower()
                
                if again in ["n", "no"]:
                    self.print_color("\n👋  Thank you for using Algiers Transport AI!", "green")
                    break
                
                # Clear for next search
                print("\n" * 3)
                
            except KeyboardInterrupt:
                self.print_color("\n\n👋  Goodbye! Come back soon!", "green")
                break
            except Exception as e:
                self.print_color(f"\n❌  Error: {str(e)}", "red")
                print("  Please try again...")
                continue

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting Algiers Smart Transport AI...")
    
    # Check for internet
    try:
        import requests
        import webbrowser
    except ImportError:
        print("❌ Error: Missing required libraries")
        print("   Install: pip install requests")
        exit(1)
    
    # Run application
    try:
        app = SmartTerminalInterface()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋  Goodbye!")
    except Exception as e:
        print(f"\n❌  Fatal error: {e}")
