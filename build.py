#!/usr/bin/env python3
"""
IronStats Brasil - Build Script
Reads CSVs from data/ folder, generates the complete HTML site.
Usage: python3 build.py
"""
import csv, json, os, re, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'races.json')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'docs')
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'template.html')

def parse_time(t):
    if not t or t == '--': return None
    p = t.replace('--', ':').split(':')
    try:
        if len(p) == 3: return int(p[0])*3600 + int(p[1])*60 + int(p[2])
        if len(p) == 2: return int(p[0])*60 + int(p[1])
    except: pass
    return None

def process_csv(filepath):
    athletes = []
    with open(filepath, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r.get('Finish', '') != 'FIN': continue
            nm = r.get('Name', '')
            parts = nm.split(' ', 1)
            short = f"{parts[0][0]}. {parts[1]}" if len(parts) > 1 else nm
            athletes.append([
                short,
                (r.get('Country', '') or '')[:3],
                (r.get('Gender', '') or ' ')[0],
                r.get('Division', ''),
                int(r.get('Age Group Rank', 0) or 0),
                parse_time(r.get('Overall Time', '')),
                parse_time(r.get('Swim Time', '')),
                parse_time(r.get('Bike Time', '')),
                parse_time(r.get('Run Time', '')),
                parse_time(r.get('Transition 1 Time', '')),
                parse_time(r.get('Transition 2 Time', '')),
            ])
    athletes.sort(key=lambda x: x[5] if x[5] else 999999)
    return athletes

def discover_races():
    """Scan data/ for CSVs and match with races.json config"""
    config = json.load(open(CONFIG_FILE, encoding='utf-8'))
    
    csvs = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    output = {"m": {}, "d": {}}
    weather = {}
    course_info = {}
    series = {}
    
    for filename in sorted(csvs):
        # Parse: ironman703{city}{year}-results.csv
        match = re.match(r'ironman703(\w+?)(\d{4})-results\.csv', filename)
        if not match:
            print(f"  Skipping {filename} (unrecognized format)")
            continue
        
        city_key = match.group(1)  # e.g. "sopaulo", "riodejaneiro"
        year = int(match.group(2))
        
        if city_key not in config['races']:
            print(f"  Warning: {city_key} not in races.json, skipping {filename}")
            continue
        
        race_cfg = config['races'][city_key]
        # Map city keys to 2-letter codes
        code_map = {"sopaulo": "sp", "riodejaneiro": "rj", "florianopolis": "fl",
                     "brasilia": "bs", "aracaju": "ar", "curitiba": "ct",
                     "buenosaires": "ba", "puntadeleste": "pe", "fortaleza": "fo",
                     "maceio": "mc", "ecuador": "ec", "cartagena": "cg",
                     "bariloche": "bl", "sanjuan": "sj", "valdivia": "vd", "peru": "pr"}
        code = code_map.get(city_key, city_key[:2])
        rid = code + str(year)[2:]  # e.g. "sp22", "rj25"
        
        # Process CSV
        filepath = os.path.join(DATA_DIR, filename)
        athletes = process_csv(filepath)
        print(f"  {rid}: {len(athletes)} finishers from {filename}")
        
        # Store data
        output["m"][rid] = {
            "n": race_cfg["name"],
            "c": race_cfg["city"],
            "y": year,
            "sk": race_cfg["swimKm"],
            "bk": race_cfg["bikeKm"],
            "rk": race_cfg["runKm"]
        }
        output["d"][rid] = athletes
        
        # Weather
        yr_str = str(year)
        if yr_str in race_cfg.get("editions", {}):
            weather[rid] = race_cfg["editions"][yr_str]
        
        # Course info (use 2-letter code as key)
        if race_cfg.get("course"):
            course_info[code] = race_cfg["course"]
        
        # Series grouping
        city_name = race_cfg["city"]
        if city_name not in series:
            series[city_name] = []
        series[city_name].append(rid)
    
    return output, weather, course_info, series

def build():
    print("IronStats Brasil - Building site...")
    
    data, weather, course_info, series = discover_races()
    
    if not data["d"]:
        print("ERROR: No race data found. Check data/ folder and races.json")
        sys.exit(1)
    
    total = sum(len(v) for v in data["d"].values())
    print(f"  Total: {len(data['d'])} editions, {total} results")
    
    # Read HTML template
    template = open(TEMPLATE_FILE, encoding='utf-8').read()
    
    # Inject data
    data_js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    weather_js = json.dumps(weather, ensure_ascii=False, separators=(',', ':'))
    course_js = json.dumps(course_info, ensure_ascii=False, separators=(',', ':'))
    series_js = json.dumps(series, ensure_ascii=False, separators=(',', ':'))
    
    html = template.replace('/*DATA_PLACEHOLDER*/', data_js)
    html = html.replace('/*WEATHER_PLACEHOLDER*/', weather_js)
    html = html.replace('/*COURSE_PLACEHOLDER*/', course_js)
    html = html.replace('/*SERIES_PLACEHOLDER*/', series_js)
    
    # Write output
    os.makedirs(OUT_DIR, exist_ok=True)
    outpath = os.path.join(OUT_DIR, 'index.html')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  Output: {outpath} ({len(html)//1024}KB)")
    print("  Done!")

if __name__ == '__main__':
    build()
