"""
Batch Request Example - Gets median and mean annual wages for all major 
occupation groups across all states.
"""

import json
import time
import requests
import pandas as pd
from itertools import product
import os

# Load API key
API_KEY = os.getenv('BLS_API_KEY')  # or hardcode for testing
if not API_KEY:
    raise ValueError("Set BLS_API_KEY environment variable")

API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'

# Load series ID codes from JSON
with open('reference/series_id_codes.json', 'r') as f:
    codes = json.load(f)

# Extract codes we need
state_codes = list(codes['area_codes']['S']['state_codes'].keys())
occupation_codes = list(codes['occupation_codes']['major_occupational_groups'].keys())
industry_code = '000000'  # All industries
datatype_codes = ['04', '13']  # Mean and median annual wages

print(f"Generating series IDs...")
print(f"  States: {len(state_codes)}")
print(f"  Occupations: {len(occupation_codes)}")
print(f"  Data types: {len(datatype_codes)}")

# Generate all series ID combinations
series_ids = []
series_metadata = []

for state_code, occ_code, datatype in product(state_codes, occupation_codes, datatype_codes):
    # Construct: OEUS + state_code + industry + occupation + datatype
    series_id = f"OEUS{state_code}{industry_code}{occ_code}{datatype}"
    
    series_ids.append(series_id)
    series_metadata.append({
        'series_id': series_id,
        'state_code': state_code,
        'occupation_code': occ_code,
        'datatype_code': datatype
    })

print(f"Generated {len(series_ids)} series IDs\n")

# Make batched API requests
BATCH_SIZE = 50
all_results = []
total_batches = (len(series_ids) + BATCH_SIZE - 1) // BATCH_SIZE

print("Making API requests...")
for i in range(0, len(series_ids), BATCH_SIZE):
    batch_num = (i // BATCH_SIZE) + 1
    batch = series_ids[i:i + BATCH_SIZE]
    
    print(f"  Batch {batch_num}/{total_batches}: {len(batch)} series")
    
    payload = {
        "seriesid": batch,
        "registrationkey": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'REQUEST_SUCCEEDED':
            all_results.extend(data['Results']['series'])
            print(f"    ✓ Retrieved {len(data['Results']['series'])} series")
        else:
            print(f"    ✗ API Error: {data.get('message', 'Unknown')}")
    
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Request failed: {e}")
    
    # Rate limiting: 0.25 second delay between requests
    if i + BATCH_SIZE < len(series_ids):
        time.sleep(0.25)

print(f"\nTotal series retrieved: {len(all_results)}\n")

# Process results into DataFrame
print("Processing results into DataFrame...")
processed_data = []

for series in all_results:
    series_id = series['seriesID']
    
    # Find metadata for this series
    metadata = next((m for m in series_metadata if m['series_id'] == series_id), None)
    if not metadata:
        continue
    
    # Extract the data point (only one per series for most recent year)
    for data_point in series['data']:
        if data_point['period'] == 'A01':  # Annual data
            processed_data.append({
                'series_id': series_id,
                'state_code': metadata['state_code'],
                'occupation_code': metadata['occupation_code'],
                'datatype_code': metadata['datatype_code'],
                'year': data_point['year'],
                'value': float(data_point['value']) if data_point['value'] != '-' else None
            })

# Create DataFrame
df = pd.DataFrame(processed_data)

# Add human-readable labels
state_names = codes['area_codes']['S']['state_codes']
occupation_names = codes['occupation_codes']['major_occupational_groups']
datatype_names = codes['datatype_codes']

df['state_name'] = df['state_code'].map(state_names)
df['occupation_name'] = df['occupation_code'].map(occupation_names)
df['datatype_name'] = df['datatype_code'].map(datatype_names)

# Pivot to wide format for easier viewing
df_wide = df.pivot_table(
    index=['state_name', 'occupation_name'],
    columns='datatype_name',
    values='value',
    aggfunc='first'
).reset_index()

print(f"Final DataFrame: {len(df_wide)} rows\n")
print(df_wide.head(10))

# Save to CSV
output_file = 'oews_batch_results.csv'
df.to_csv(output_file, index=False)
print(f"\nFull results saved to: {output_file}")