import fastf1
from fastf1.core import Telemetry, Laps, Lap

# Get telemetry channels - focused extraction
doc = Telemetry.__doc__
# Find the channel descriptions
lines = doc.split('\n')
for i, line in enumerate(lines):
    if 'Speed' in line or 'Brake' in line or 'Position' in line or 'DRS' in line or 'Source' in line or 'Distance' in line or 'X' in line or 'Y' in line or 'Z' in line or 'Status' in line or 'Time' in line or 'Date' in line or 'SessionTime' in line:
        print(line.strip())

print('\n=== Laps DataFrame Columns ===')
doc2 = Laps.__doc__
if doc2:
    lines2 = doc2.split('\n')
    in_cols = False
    for line in lines2:
        stripped = line.strip()
        if 'column' in stripped.lower() or in_cols:
            in_cols = True
            print(stripped)
            if stripped == '' and in_cols:
                break

# Get 2025 schedule
print('\n=== 2025 Australian GP ===')
schedule = fastf1.get_event_schedule(2025)
aus = schedule[schedule['EventName'].str.contains('Australia', case=False)]
print(aus[['RoundNumber', 'EventName', 'Country', 'EventDate']].to_string())

# Show session identifiers
print('\n=== Session Identifiers ===')
print('Valid identifiers: FP1, FP2, FP3, Q, SQ, SS, S, R, Sprint')
print('Or: Practice 1, Practice 2, Practice 3, Qualifying, Sprint, Race')

# Rate limits info
print('\n=== Rate Limiting ===')
print('FastF1 uses Ergast API (deprecated) and new F1 API')
print('Cache is critical to avoid repeated API calls')
print('Default cache location:', fastf1.Cache._get_cache_path() if hasattr(fastf1.Cache, '_get_cache_path') else 'see logs')
