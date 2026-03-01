import requests
from duckduckgo_search import DDGS
import json
import re

results_all = []

queries = [
    'best bathroom remodel contractor Vancouver WA 98662 reviews',
    'bathroom tile contractor Vancouver WA Google reviews rating',
    'vanity installation contractor Vancouver WA rated',
    'bathroom renovation company Vancouver Washington reviews 2024 2025',
    'site:houzz.com bathroom remodel Vancouver WA',
    'bathroom contractor Vancouver WA 4.5 stars',
    'top rated bathroom remodeler Clark County WA'
]

for q in queries:
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(q, max_results=8))
            for r in res:
                results_all.append({
                    'title': r.get('title',''),
                    'body': r.get('body',''),
                    'href': r.get('href','')
                })
    except Exception as e:
        print(f'Error on query [{q}]: {e}')

# Deduplicate by href
seen = set()
unique = []
for r in results_all:
    if r['href'] not in seen:
        seen.add(r['href'])
        unique.append(r)

print(f'Total unique results: {len(unique)}')
for r in unique:
    print(f"TITLE: {r['title']}")
    print(f"BODY: {r['body'][:200]}")
    print(f"URL: {r['href']}")
    print('---')
