#!/usr/bin/env python3
"""
Terminal Client for Algiers Transport
ONLY accepts valid area names from the data
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "al_engine"))
from ai_engine.recommendation_engine import TransportRecommender

def print_colored(text, color_code):
    """Print colored text in terminal"""
    print(f"\033[{color_code}m{text}\033[0m")

def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print_colored("🇩🇿  ALGIERS TRANSPORT AI SYSTEM", "1;34")
    print_colored("🚇  Smart Route Recommendations", "1;36")
    print("="*70)

def print_area_suggestions(recommender):
    """Print available area suggestions"""
    areas = recommender.get_available_areas()
    
    print("\n" + "-"*70)
    print_colored("📍  AVAILABLE AREAS IN ALGIERS:", "1;33")
    print("-"*70)
    
    print("\n  English Name          Arabic Name")
    print("  ────────────────────  ───────────────────")
    
    for area in areas:
        eng = area.get("english", "")
        ar = area.get("arabic", "")
        print(f"  • {eng:<20} {ar}")
    
    print(f"\n  💡  You can use either English or Arabic names")
    print("  ❌  Other locations will be rejected")

def print_option(option, index):
    """Print a transport option in a nice format"""
    colors = {
        'metro': '1;35',    # Purple
        'bus': '1;33',      # Yellow
        'bicycle': '1;32',  # Green
        'walk': '1;36',     # Cyan
        'error': '1;31'     # Red for errors
    }
    
    emoji = {
        'metro': '🚇',
        'bus': '🚌',
        'bicycle': '🚴',
        'walk': '👣',
        'error': '❌'
    }
    
    color = colors.get(option.get('mode', ''), '1;37')
    symbol = emoji.get(option.get('mode', ''), '📍')
    
    print(f"\n{'━'*70}")
    print_colored(f"{symbol}  OPTION {index + 1}: {option.get('name', 'ERROR').upper()}", color)
    print(f"{'━'*70}")
    
    if 'error' in option:
        print(f"  {option['error']}")
        return
    
    # Main info
    print(f"  ⏱️  Duration: {option['duration']} minutes")
    print(f"  💰  Cost: {option['cost']} DZD")
    print(f"  🌿  Emissions: {option['emissions']:.2f} kg CO2")
    print(f"  ⭐  Score: {option['score']:.1f}/100")
    
    # Description
    print(f"\n  📝  {option['description']}")
    
    # Details
    print(f"\n  📊  Details:")
    for key, value in option['details'].items():
        print(f"     • {key}: {value}")

def get_valid_area_input(prompt, recommender):
    """Get valid area input from user"""
    while True:
        area = input(prompt).strip()
        
        if not area:
            print_colored("  ❌  Please enter a location", "1;31")
            continue
        
        if area.lower() in ['exit', 'quit', 'q']:
            return None
        
        if recommender.is_valid_area(area):
            return area
        else:
            print_colored(f"  ❌  '{area}' is not a valid area in Algiers", "1;31")
            print_colored("  💡  Type 'areas' to see available areas, or 'exit' to quit", "1;33")
            
            if input("  Show available areas? (y/n): ").lower() == 'y':
                print_area_suggestions(recommender)
            
            print()

def main():
    """Main function"""
    print_header()
    
    # Initialize the recommender
    print_colored("\n📂  Loading Algiers transport data...", "1;36")
    try:
        recommender = TransportRecommender("data/algiers_transport.json")
        print_colored("✅  Data loaded successfully!", "1;32")
    except Exception as e:
        print_colored(f"❌  Error: {e}", "1;31")
        print("\nPlease make sure 'data/algiers_transport.json' exists")
        print("Current directory:", os.getcwd())
        return
    
    # Get city info
    city_info = recommender.get_city_info()
    print(f"\n🏙️  City: {city_info.get('city', 'Algiers')}")
    print(f"👥  Population: {city_info.get('population', 4000000):,}")
    print(f"📏  Area: {city_info.get('area_sqkm', 363)} km²")
    
    print_area_suggestions(recommender)
    
    print("\n" + "="*70)
    print_colored("📍  ENTER YOUR JOURNEY", "1;34")
    print("="*70)
    
    while True:
        try:
            print("\n" + "-"*70)
            print_colored("  Type 'areas' to see available areas, 'exit' to quit", "1;33")
            print("-"*70)
            
            # Get valid start location
            start = get_valid_area_input("\n  Start location: ", recommender)
            if start is None:
                print_colored("\n👋  Goodbye! Safe travels!", "1;33")
                break
            
            # Get valid end location
            end = get_valid_area_input("  End location: ", recommender)
            if end is None:
                print_colored("\n👋  Goodbye! Safe travels!", "1;33")
                break
            
            # Get recommendations
            print_colored(f"\n🔍  Finding routes from {start} to {end}...", "1;36")
            
            recommendations = recommender.get_recommendations(start, end)
            
            if not recommendations:
                print_colored("❌  No transport options found for this route.", "1;31")
                continue
            
            # Check if first recommendation is an error
            if 'error' in recommendations[0]:
                print_option(recommendations[0], 0)
                continue
            
            # Show results
            print("\n" + "⭐"*70)
            print_colored("  🎯  RECOMMENDED ROUTES", "1;32;47")
            print("⭐"*70)
            
            for i, option in enumerate(recommendations[:3]):  # Show top 3
                print_option(option, i)
            
            # Show summary if we have valid options
            valid_options = [opt for opt in recommendations if 'error' not in opt]
            if len(valid_options) > 1:
                print("\n" + "="*70)
                print_colored("  📈  COMPARISON", "1;34")
                print("="*70)
                
                best = valid_options[0]
                second = valid_options[1] if len(valid_options) > 1 else best
                
                print(f"\n  🥇  Best option: {best['name']} ({best['score']:.1f}/100)")
                print(f"  🥈  Second best: {second['name']} ({second['score']:.1f}/100)")
                
                # Show comparison
                advantages = []
                if second['cost'] < best['cost']:
                    savings = best['cost'] - second['cost']
                    advantages.append(f"💰  Saves {savings} DZD")
                
                if second['duration'] < best['duration']:
                    time_saved = best['duration'] - second['duration']
                    advantages.append(f"⏱️  {time_saved} minutes faster")
                
                if second['emissions'] < best['emissions']:
                    co2_saved = best['emissions'] - second['emissions']
                    advantages.append(f"🌿  {co2_saved:.2f} kg less CO₂")
                
                if advantages:
                    print(f"\n  ✅  Advantages of 2nd option:")
                    for adv in advantages:
                        print(f"      {adv}")
            
            # Show transport statistics
            print("\n" + "="*70)
            print_colored("  📊  ALGIERS TRANSPORT STATISTICS", "1;36")
            print("="*70)
            
            transport_stats = recommender.get_transport_stats()
            
            metro = transport_stats.get('metro', {})
            if metro:
                print(f"\n  🚇  {metro.get('system_name', 'Metro')}:")
                print(f"       • {metro.get('total_stations', 14)} stations")
                print(f"       • {metro.get('daily_ridership', 350000):,} daily riders")
                print(f"       • Operating: {metro.get('operating_hours', '05:00-23:00')}")
            
            bus = transport_stats.get('bus_network', {})
            if bus:
                print(f"  🚌  Bus Network:")
                print(f"       • {bus.get('total_lines', 120)} lines")
                print(f"       • {bus.get('daily_ridership', 500000):,} daily riders")
            
            bike = transport_stats.get('bicycle_sharing', {})
            if bike:
                print(f"  🚴  Bike Sharing:")
                print(f"       • {bike.get('total_stations', 25)} stations")
                print(f"       • {bike.get('total_bikes', 500)} bikes available")
            
            # Ask to continue
            print("\n" + "-"*70)
            choice = input("  🔄  Find another route? (Y/n): ").strip().lower()
            if choice in ['n', 'no']:
                print_colored("\n👋  Thank you for using Algiers Transport System!", "1;32")
                break
            
            # Clear for next search
            print("\n" * 2)
            
        except KeyboardInterrupt:
            print_colored("\n\n👋  Goodbye! Safe travels in Algiers!", "1;33")
            break
        except Exception as e:
            print_colored(f"\n❌  Error: {e}", "1;31")
            print("  Please try again...")
            continue

if __name__ == "__main__":
    main()