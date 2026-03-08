import fastf1
import inspect

# Check telemetry columns from docstring
from fastf1.core import Telemetry
doc = Telemetry.__doc__
print('=== Telemetry Docstring ===')
print(doc[:2000] if doc else 'No docstring')

# Check Lap (singular) class
print('\n=== Lap (singular) properties ===')
from fastf1.core import Lap
for name in sorted(dir(Lap)):
    if not name.startswith('_') and not callable(getattr(Lap, name, None)):
        print(f'  {name}')

# Check available data columns for laps
print('\n=== Laps Docstring (first 1500 chars) ===')
from fastf1.core import Laps
doc2 = Laps.__doc__
print(doc2[:1500] if doc2 else 'No docstring')

# Check event schedule for 2025
print('\n=== 2025 Event Schedule (first 3 events) ===')
schedule = fastf1.get_event_schedule(2025)
print(schedule.columns.tolist())
print(schedule[['EventName', 'Country', 'EventDate']].head(3).to_string())

# Check get_session signature
print('\n=== get_session signature ===')
print(inspect.signature(fastf1.get_session))
print(fastf1.get_session.__doc__[:500] if fastf1.get_session.__doc__ else 'No doc')
