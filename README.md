# BLS OEWS API Tutorial

Guide to using the [Bureau of Labor Statistics (BLS) Public Data API](https://www.bls.gov/developers/home.htm) to access data from the [Occupational Employment and Wage Statistics (OEWS) survey](https://www.bls.gov/oes/).

## About

This tutorial was developed by the Bloomberg Center for Government Excellence (GovEx) Research & Analytics team. When possible, we automate data collection through the BLS API rather than downloading Data Tables. Since [BLS series ID construction](https://www.bls.gov/help/hlpforma.htm) is complex and OEWS specific examples are not included in the official API documentation, we created this tutorial to help others query OEWS data with Python.

## OEWS Series ID Format

Querying the API requires constructing series IDs that specify exactly which data you want. Each OEWS series ID encodes the geographic area, occupation, industry, and employment or wage measure you're requesting.

### Series ID Structure

OEWS series IDs follow this 25-character format:

```
OE + U + areatype_code(1) + area_code(7) + industry_code(6) + occupation_code(6) + datatype_code(2)
```

| Component | Position | Length | Example Value | Description |
|-----------|----------|--------|-------|-------------|
| Survey | 1-2 | 2 | `OE` | Survey (always `OE`) |
| Seasonal | 3 | 1 | `U` | Not seasonally adjusted (always `U`) |
| Area Type | 4 | 1 | `M` | `M` (metro), `S` (state), `N` (national) |
| Area Code | 5-11 | 7 | `0011260` | Geographic identifier (CBSA codes, State FIPS) |
| Industry | 12-17 | 6 | `000000` | Industry classification (NAICS) |
| Occupation | 18-23 | 6 | `000000` | Occupation classification (SOC) |
| Data Type | 24-25 | 2 | `13` | Employment or Wage measure (`01`-`17`) |

**Complete code definitions:** [reference/series_id_codes.json](reference/series_id_codes.json)

**Example Series IDs:** 
- `OEUN000000000000000000001`: Total employment for all occupations across all industries in the United States
- `OEUS280000000000025201113`: Annual median wage for elementary school teachers in Mississippi
- `OEUM001910000000029124204`: Annual mean wage for orthopedic surgeons in Dallas-Fort Worth, TX

### API Limitations

- **Year coverage:** API provides only the most recent year. For historical data, use [OEWS Data Tables](https://www.bls.gov/oes/tables.htm)
- **Rate limits:** 500 requests/day, 50 series per request (API v2 with registration). For large-scale data collection, remember to batch requests in groups of 50 with delays between requests to respect rate limits.

## Quick Start

### Prerequisites
- Python 3.9+
- BLS API key (register at https://data.bls.gov/registrationEngine/)

### Installation

```bash
# Clone the repository
git clone https://github.com/govex/bls-oews-api-tutorial.git
cd bls-oews-api-tutorial

# # Create and activate virtual environment (if needed)
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Add your API key to .env file (if preferred)
echo "BLS_API_KEY=your_key_here" > .env
```

### Basic Example

```python
import requests

API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
API_KEY = 'your_api_key_here' # Or use your .env file

# Request median wage for all occupations in Atlanta MSA
series_id = 'OEUM001126000000000000013'

payload = {
    "seriesid": [series_id],
    "registrationkey": API_KEY
}

response = requests.post(API_URL, json=payload)
data = response.json()

if data['status'] == 'REQUEST_SUCCEEDED':
    value = data['Results']['series'][0]['data'][0]['value']
    print(f"Requested value: ${value}\n")
else:
    print(f"API Error: {data.get('message', 'Unknown error')}\n")

print("Full API response:")
data
```

### Batch Request Example

For querying multiple series efficiently, see [examples/batch_request.py](examples/batch_request.py). This example demonstrates querying median and mean annual wages for all major occupations across all US states.
```bash
python examples/batch_request.py
```

## Additional Resources

- [OEWS Overview](https://www.bls.gov/oes/)
- [OEWS Data Files](https://download.bls.gov/pub/time.series/oe/)
- [OEWS Technical Documentation](https://download.bls.gov/pub/time.series/oe/oe.txt)
- [OEWS Profiles Definitions](https://www.bls.gov/help/def/oesprofiles.htm)
- [BLS API Documentation](https://www.bls.gov/developers/api_signature_v2.htm)
- [Standard Occupational Classification (SOC)](https://www.bls.gov/soc/)
- [North American Industry Classification System (NAICS)](https://www.bls.gov/bls/naics.htm)

## Contributing

Contributions and suggestions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Authors

Developed by the Bloomberg Center for Government Excellence (GovEx) Research & Analytics team.
