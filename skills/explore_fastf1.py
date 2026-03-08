import fastf1
import inspect

print('FastF1 Version:', fastf1.__version__)
print()

# List main modules and classes
print('=== Main Module Contents ===')
for name in sorted(dir(fastf1)):
    if not name.startswith('_'):
        obj = getattr(fastf1, name)
        print(f'  {name}: {type(obj).__name__}')

print()
print('=== Key Functions ===')
# Check get_session and get_event
for func_name in ['get_session', 'get_event', 'get_event_schedule', 'get_events_remaining']:
    func = getattr(fastf1, func_name, None)
    if func:
        sig = inspect.signature(func)
        doc = (func.__doc__ or '')[:200]
        print(f'\n{func_name}{sig}')
        print(f'  Doc: {doc}')

# Check Session class
print('\n=== Session Class Methods ===')
from fastf1.core import Session
for name in sorted(dir(Session)):
    if not name.startswith('_') and callable(getattr(Session, name, None)):
        print(f'  Session.{name}')

print('\n=== Laps Class Columns (from docstring) ===')
from fastf1.core import Laps
for name in sorted(dir(Laps)):
    if not name.startswith('_') and not callable(getattr(Laps, name, None)):
        print(f'  Laps.{name}')
