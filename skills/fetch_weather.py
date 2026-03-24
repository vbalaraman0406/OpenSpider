import os
import re
import json

def fetch_html():
    """Fetch HTML from NWS Vancouver forecast page using os.popen and curl."""
    url = 'https://forecast.weather.gov/MapClick.php?CityName=Vancouver&state=WA&site=PQR&textField1=45.6280&textField2=-122.6739'
    cmd = f"curl -s -H 'User-Agent: Mozilla/5.0' '{url}'"
    try:
        with os.popen(cmd) as stream:
            html = stream.read()
        if html:
            return html
        else:
            return "Curl returned empty output"
    except Exception as e:
        return f"Error fetching HTML: {e}"

def extract_forecast(html):
    """Extract 5-day forecast data using regex patterns."""
    forecast = []
    # Pattern for tombstone containers (each day)
    tombstone_pattern = r'<div class="tombstone-container">(.*?)</div>'
    tombstones = re.findall(tombstone_pattern, html, re.DOTALL)
    for i, stone in enumerate(tombstones[:5]):  # First 5 days
        day_match = re.search(r'<p class="period-name">(.*?)</p>', stone, re.DOTALL)
        day = re.sub(r'<[^>]+>', '', day_match.group(1)).strip() if day_match else "N/A"
        
        high_match = re.search(r'<p class="temp temp-high">(.*?)</p>', stone, re.DOTALL)
        high = re.sub(r'<[^>]+>', '', high_match.group(1)).strip() if high_match else "N/A"
        
        low_match = re.search(r'<p class="temp temp-low">(.*?)</p>', stone, re.DOTALL)
        low = re.sub(r'<[^>]+>', '', low_match.group(1)).strip() if low_match else "N/A"
        
        cond_match = re.search(r'<p class="short-desc">(.*?)</p>', stone, re.DOTALL)
        conditions = re.sub(r'<[^>]+>', '', cond_match.group(1)).strip() if cond_match else "N/A"
        
        forecast.append({
            "Day": day,
            "High (F)": high,
            "Low (F)": low,
            "Conditions": conditions,
            "Precipitation %": "N/A",  # Will update from detailed forecast
            "Wind": "N/A"
        })
    
    # Extract precipitation and wind from detailed forecast section
    detailed_pattern = r'<div id="detailed-forecast-body">(.*?)</div>'
    detailed_match = re.search(detailed_pattern, html, re.DOTALL)
    if detailed_match:
        detailed_html = detailed_match.group(1)
        row_pattern = r'<div class="row-forecast">(.*?)</div>'
        rows = re.findall(row_pattern, detailed_html, re.DOTALL)
        for i, row in enumerate(rows[:5]):
            row_text = re.sub(r'<[^>]+>', ' ', row).strip()
            precip_match = re.search(r'(\d+)%', row_text)
            wind_match = re.search(r'Wind.*?(\d+ to \d+ mph|\d+ mph)', row_text, re.IGNORECASE)
            if i < len(forecast):
                if precip_match:
                    forecast[i]["Precipitation %"] = f"{precip_match.group(1)}%"
                if wind_match:
                    forecast[i]["Wind"] = wind_match.group(1)
    
    return forecast

def extract_alerts(html):
    """Extract active weather alerts."""
    alert_pattern = r'<div class="alert-headline">(.*?)</div>'
    alert_match = re.search(alert_pattern, html, re.DOTALL)
    if alert_match:
        alert_text = re.sub(r'<[^>]+>', '', alert_match.group(1)).strip()
        return [alert_text]
    return ["No active alerts"]

def main():
    html = fetch_html()
    if html.startswith("Error") or html.startswith("Curl"):
        print(json.dumps({"error": html}))
        return
    
    forecast = extract_forecast(html)
    alerts = extract_alerts(html)
    
    # Build markdown table
    markdown_table = "| Day | High (F) | Low (F) | Conditions | Precipitation % | Wind |\n"
    markdown_table += "|-----|----------|---------|------------|-----------------|------|\n"
    for day in forecast:
        markdown_table += f"| {day['Day']} | {day['High (F)']} | {day['Low (F)']} | {day['Conditions']} | {day['Precipitation %']} | {day['Wind']} |\n"
    
    alerts_text = "\n".join(alerts)
    
    result = {
        "markdown_table": markdown_table,
        "alerts": alerts_text,
        "forecast": forecast
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()