import json

def navigate_yahoo_fantasy():
    return json.dumps({"action": "browse_web", "command": "navigate", "url": "https://baseball.fantasysports.yahoo.com/"})

if __name__ == "__main__":
    print(navigate_yahoo_fantasy())