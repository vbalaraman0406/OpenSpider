import json

def generate_sea_lax_flights():
    flights = [
        {
            "airline": "Alaska Airlines",
            "departure_time": "08:00 AM",
            "arrival_time": "10:30 AM",
            "stops": 0,
            "cabin_class": "Business",
            "price": 720
        },
        {
            "airline": "Alaska Airlines",
            "departure_time": "09:00 AM",
            "arrival_time": "11:45 AM",
            "stops": 0,
            "cabin_class": "Premium Economy",
            "price": 680
        },
        {
            "airline": "Frontier Airlines",
            "departure_time": "07:30 AM",
            "arrival_time": "10:15 AM",
            "stops": 0,
            "cabin_class": "Premium Economy",
            "price": 560
        },
        {
            "airline": "Frontier Airlines",
            "departure_time": "02:00 PM",
            "arrival_time": "04:45 PM",
            "stops": 0,
            "cabin_class": "Business",
            "price": 600
        },
        {
            "airline": "Delta Air Lines",
            "departure_time": "10:00 AM",
            "arrival_time": "12:30 PM",
            "stops": 0,
            "cabin_class": "Business",
            "price": 880
        },
        {
            "airline": "Delta Air Lines",
            "departure_time": "01:00 PM",
            "arrival_time": "03:45 PM",
            "stops": 1,
            "cabin_class": "Premium Economy",
            "price": 790
        },
        {
            "airline": "American Airlines",
            "departure_time": "06:00 AM",
            "arrival_time": "08:45 AM",
            "stops": 0,
            "cabin_class": "First Class",
            "price": 650
        },
        {
            "airline": "American Airlines",
            "departure_time": "03:00 PM",
            "arrival_time": "05:30 PM",
            "stops": 0,
            "cabin_class": "Business",
            "price": 680
        }
    ]
    return flights

if __name__ == '__main__':
    sea_lax_flights = generate_sea_lax_flights()
    print(json.dumps(sea_lax_flights, indent=2))
