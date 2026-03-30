forecast_date = 'Friday, March 27, 2026'

markdown = f"""## 🌦️ Daily Vancouver, WA Weather Forecast
**Date:** {forecast_date}  
**Source:** [National Weather Service (NWS)](https://forecast.weather.gov/MapClick.php?CityName=Vancouver&state=WA&site=PQR&textField1=45.6280&textField2=-122.6739)  
**Station:** Pearson Airfield (KVUO) — Current: Clear, 37°F, Humidity 80%, Wind N 0 MPH

---

### ⚠️ Active Weather Alerts
**Critical Fire Weather in the Plains** — Unseasonably warm temperatures continue today through the weekend across the Southwest and southern U.S. Elevated to critical fire weather conditions will persist across the southern Plains today, moving into the central Plains and Southeast U.S on Saturday.

---

### 📅 5-Day Forecast

| Day | High (°F) | Low (°F) | Conditions | Precipitation % | Wind |
|-----|-----------|----------|------------|-----------------|------|
| Today (Fri) | 64 | 38 | Areas Frost then Mostly Sunny | — | N NW 5–8 mph |
| Saturday | 61 | 40 | Mostly Sunny / Partly Cloudy | — | Light NW; NNW ~5 mph |
| Sunday | 58 | 40 | Slight Chance Rain / Chance Rain & Snow | 20% (day) / 50% (night) | Calm → SW 5 mph |
| Monday | 53 | 35 | Chance Rain/Snow then Rain | 40% | — |
| Tuesday | 56 | 42 | Slight Chance Rain / Chance Rain | — | — |

---

### 📝 Detailed Forecast

- **Today:** Areas of frost before 8am. Otherwise, mostly sunny, with a high near 64. North northwest wind 5 to 8 mph.
- **Tonight:** Partly cloudy, with a low around 38. North northwest wind 5 to 7 mph becoming calm after midnight.
- **Saturday:** Mostly sunny, with a high near 61. Light northwest wind.
- **Saturday Night:** Partly cloudy, with a low around 40. North northwest wind around 5 mph becoming calm in the evening.
- **Sunday:** A 20% chance of rain after 11am. Mostly cloudy, with a high near 58. Calm wind becoming southwest around 5 mph.
- **Sunday Night:** Chance of rain before 5am, then chance of rain and snow. Low around 40. Precipitation chance 50%. Little or no snow accumulation.
- **Monday:** Chance of rain and snow before 8am, then chance of rain. Snow level 2100 ft. High near 53. Precipitation chance 40%.
- **Monday Night:** Slight chance of rain before 11pm. Snow level 2500 ft lowering to 1400 ft. Low around 35.
- **Tuesday:** Slight chance of rain after 11am. Snow level 1300 ft rising to 3200 ft. High near 56.
- **Tuesday Night:** Chance of rain. Mostly cloudy, low around 42.

---
*Generated automatically by OpenSpider Cron Agent on {forecast_date}*
"""

print(markdown)

with open('forecast_email_body.md', 'w') as f:
    f.write(markdown)

print('\n--- SAVED TO forecast_email_body.md ---')