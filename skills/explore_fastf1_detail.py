import fastf1
import inspect

# Explore Session.load signature
from fastf1.core import Session
load_doc = Session.load.__doc__
print('=== Session.load() docstring ===')
print(load_doc[:1500] if load_doc else 'No docstring')

print('\n=== Session Properties ===')
for name in sorted(dir(Session)):
    if not name.startswith('_') and not callable(getattr(Session, name, None)):
        print(f'  {name}')

# Explore Telemetry class
print('\n=== Telemetry Class ===')
from fastf1.core import Telemetry
for name in sorted(dir(Telemetry)):
    if not name.startswith('_') and callable(getattr(Telemetry, name, None)):
        print(f'  Telemetry.{name}')

# Check Laps methods
print('\n=== Laps Methods ===')
from fastf1.core import Laps
for name in sorted(dir(Laps)):
    if not name.startswith('_') and callable(getattr(Laps, name, None)):
        obj = getattr(Laps, name)
        if hasattr(obj, '__doc__') and obj.__doc__ and 'lap' in (obj.__doc__ or '').lower()[:100]:
            print(f'  Laps.{name}: {obj.__doc__[:100].strip()}')
        elif name in ['pick_driver', 'pick_drivers', 'pick_fastest', 'pick_quicklaps', 'pick_team', 'pick_teams', 'pick_wo_box', 'pick_track_status', 'pick_accurate', 'get_car_data', 'get_pos_data', 'get_telemetry', 'get_weather_data']:
            sig = inspect.signature(obj) if callable(obj) else ''
            print(f'  Laps.{name}{sig}')

# Check cache setup
print('\n=== Cache ===')
print(type(fastf1.Cache))
for name in dir(fastf1.Cache):
    if not name.startswith('_'):
        print(f'  Cache.{name}')
