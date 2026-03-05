import json

with open('/Users/vbalaraman/OpenSpider/nws_forecast.json') as f:
    data = json.load(f)

periods = data['properties']['periods']

# Group into days
days = {}
for p in periods[:14]:
    name = p['name']
    temp = p['temperature']
    sf = p['shortForecast']
    pop = p.get('probabilityOfPrecipitation', {})
    pv = pop.get('value', None) if pop else None
    ps = str(pv) + '%' if pv is not None else '0%'
    ws = p['windSpeed']
    wd = p['windDirection']
    is_night = p['isDaytime'] == False
    print(f'{name}|{temp}|{sf}|{ps}|{ws} {wd}|{"night" if is_night else "day"}')
