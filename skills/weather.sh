#!/bin/bash
echo "=== FLORIDA SPRING TRAINING WEATHER ==="
curl -s --max-time 15 'https://wttr.in/Tampa?format=3'
curl -s --max-time 15 'https://wttr.in/Clearwater?format=3'
curl -s --max-time 15 'https://wttr.in/Fort+Myers?format=3'
curl -s --max-time 15 'https://wttr.in/Jupiter?format=3'
curl -s --max-time 15 'https://wttr.in/Sarasota?format=3'
curl -s --max-time 15 'https://wttr.in/Lakeland?format=3'
curl -s --max-time 15 'https://wttr.in/Bradenton?format=3'
echo "=== ARIZONA SPRING TRAINING WEATHER ==="
curl -s --max-time 15 'https://wttr.in/Tempe?format=3'
curl -s --max-time 15 'https://wttr.in/Goodyear,AZ?format=3'
curl -s --max-time 15 'https://wttr.in/Surprise,AZ?format=3'
curl -s --max-time 15 'https://wttr.in/Peoria,AZ?format=3'
curl -s --max-time 15 'https://wttr.in/Glendale,AZ?format=3'
echo "DONE"
