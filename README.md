# 🚇 Algiers Transport AI

An AI-powered multimodal transport recommendation system for Algiers, Algeria. Suggests optimal routes using bicycles, metro, bus, Yassir, and private cars with real-time scoring.

## 🌟 Features

- **AI-Powered Recommendations**: Weighted scoring based on time, cost, comfort, and environment
- **Multi-Modal Integration**: Bicycle, Metro, Bus, Yassir, Car
- **Real-Time Factors**: Traffic, weather, time of day considerations
- **Bicycle System**: Station recommendations with points-based payment
- **Arabic/English Support**: Localized for Algiers users
- **RESTful API**: Easy integration with web/mobile apps

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Git

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/algiers-transport-ai.git
cd algiers-transport-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 5. Test with client
python terminal_client.py