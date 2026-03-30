import subprocess
import json

topics = [
    'Dolphins Broncos trade Waddle Achane NFL March 2026',
    'Dune Part Three movie 2026',
    'NATO news March 2026',
    'SOFI stock news March 2026',
    'Ali Larijani Iran March 2026',
    'Tulsi Gabbard news March 2026',
    'Spider-Man Black Cat Marvel 2026',
    'SaveActTaxesVoting bill 2026',
    'St Patricks Day 2026 trending'
]

for topic in topics:
    print(f'\n=== {topic} ===')
    # Just print the topic - we'll use browse_web instead
    print(f'Need to search: {topic}')

print('\nDone listing topics to search')
