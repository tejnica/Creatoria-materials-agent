# Creatoria Materials Agent

An agent for searching and analyzing engineering materials with parameterized search capabilities and n8n integration.

## Features

- 🔍 Material search by keywords and parameters
- 📊 Parameterized search with range and unit support
- 🌐 Search in scientific databases (Google Scholar, arXiv)
- 🔄 n8n integration for automation
- 📝 Automatic material property extraction
- 🏷️ Automatic material categorization
- 🔄 Unit conversion
- 📈 Result reliability assessment

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/creatoria-materials-agent.git
cd creatoria-materials-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # for Linux/Mac
venv\Scripts\activate     # for Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install ChromeDriver:
```bash
# Windows (using chocolatey)
choco install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Mac
brew install chromedriver
```

5. Configure settings:
- Copy `config.example.json` to `config.json`
- Fill in required API keys and settings

### Cloud Deployment

#### Heroku

1. Create a Heroku app:
```bash
heroku create your-app-name
```

2. Configure environment variables:
```bash
heroku config:set ACI_API_KEY=your_api_key
```

3. Deploy the application:
```bash
git push heroku main
```

#### Docker

1. Build the image:
```bash
docker build -t creatoria-materials-agent .
```

2. Run the container:
```bash
docker run -p 8000:8000 creatoria-materials-agent
```

## Running

### Local Run

```bash
python run_agent.py
```

The server will be available at: `http://localhost:8000`

### Health Check

```bash
curl http://localhost:8000/health
```

## Project Structure

```
creatoria-materials-agent/
├── creatoria-agent.py     # Main agent code
├── parameter_parser.py    # Parameter query parser
├── web_search.py         # Web search module
├── run_agent.py          # FastAPI server
├── config.json           # Configuration
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker configuration
├── Procfile             # Heroku configuration
└── examples/            # Usage examples
```

## Configuration

### Configuration (config.json)

```json
{
    "materials_project": "YOUR_API_KEY",
    "aci": {
        "api_key": "YOUR_ACI_API_KEY",
        "endpoint": "https://api.aci.dev",
        "agent_id": "pubchem-agent"
    },
    "web_search": {
        "enabled": true,
        "sources": {
            "google_scholar": true,
            "arxiv": true,
            "sciencedirect": true,
            "nature": true,
            "springer": true,
            "general_web": true
        }
    }
}
```

### n8n Integration

1. Create a new workflow in n8n
2. Add HTTP Request node
3. Configure:
   - Method: POST
   - URL: http://your-server:8000/materials-webhook
   - Body: JSON
   ```json
   {
     "parameters": "pressure drop ≤ 200 kPa\ninlet temperature 25–40 °C\nmass ≤ 1.5 kg\ncost ≤ 50"
   }
   ```

## Usage

### Parameter Search

```python
import requests

response = requests.post(
    "http://localhost:8000/materials-webhook",
    json={
        "parameters": """
        pressure drop ≤ 200 kPa
        inlet temperature 25–40 °C
        mass ≤ 1.5 kg
        cost ≤ 50
        """
    }
)

print(response.json())
```

### Keyword Search

```python
response = requests.post(
    "http://localhost:8000/materials-webhook",
    json={
        "query": "graphene",
        "category": "nanomaterials"
    }
)
```

### Supported Parameters

- Pressure (pressure)
- Temperature (temperature)
- Mass (mass)
- Cost (cost)
- Length (length)
- Density (density)
- Thermal conductivity (thermal_conductivity)
- Electrical conductivity (electrical_conductivity)
- Strength (strength)
- Hardness (hardness)

### Supported Operators

- ≤ (less than or equal)
- ≥ (greater than or equal)
- < (less than)
- > (greater than)
- = (equal)
- – (range)

## Logging

Logs are saved to `agent.log` and contain information about:
- Server startup and shutdown
- Request processing
- Errors and warnings
- Search results

## Development

### Adding New Sources

1. Create a new method in `web_search.py`
2. Add the source to configuration
3. Update result processing

### Adding New Parameters

1. Add parameter to `parameter_parser.py`
2. Update unit conversion tables
3. Add processing to `creatoria-agent.py`

## License

MIT

## Authors

- Eduard Tsunsky (Cunskis)
- edsolntsev@gmail.com

## Support

Create an issue in the repository for:
- Bug reports
- Feature requests
- Usage questions 
