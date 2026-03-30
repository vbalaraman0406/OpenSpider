import os
import json
from collections import defaultdict
from datetime import datetime, timedelta

parent = os.path.dirname(os.getcwd())

# Read usage.jsonl
usage_file = os.path.join(parent, 'workspace', 'usage.jsonl')

if not os.path.exists(usage_file):
    print('usage.jsonl NOT FOUND')
else:
    size = os.path.getsize(usage_file)
    print(f'usage.jsonl size: {size} bytes')
    
    entries = []
    with open(usage_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    print(f'Total entries: {len(entries)}')
    
    # Today's date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'Today: {today}')
    
    # Aggregate stats
    total_prompt = 0
    total_comp = 0
    total_tokens = 0
    today_prompt = 0
    today_comp = 0
    today_tokens = 0
    today_requests = 0
    today_cost = 0.0
    total_cost = 0.0
    models = defaultdict(int)
    agents = defaultdict(int)
    daily = defaultdict(lambda: {'prompt': 0, 'comp': 0, 'total': 0, 'requests': 0, 'cost': 0.0})
    
    PRICING = {
        'claude-3-opus-20240229': (15.00, 75.00),
        'claude-3-sonnet-20240229': (3.00, 15.00),
        'claude-3-haiku-20240307': (0.25, 1.25),
        'claude-opus-4-6-thinking': (15.00, 75.00),
        'gpt-4o': (5.00, 15.00),
        'gpt-4-turbo': (10.00, 30.00),
        'gpt-3.5-turbo': (0.50, 1.50),
    }
    
    def calc_cost(model, prompt_t, comp_t):
        pricing = None
        if model in PRICING:
            pricing = PRICING[model]
        else:
            for k, v in PRICING.items():
                if k in model:
                    pricing = v
                    break
        if not pricing:
            return 0.0
        return (prompt_t * pricing[0] / 1_000_000) + (comp_t * pricing[1] / 1_000_000)
    
    for e in entries:
        u = e.get('usage', {})
        pt = u.get('promptTokens', 0)
        ct = u.get('completionTokens', 0)
        tt = u.get('totalTokens', 0)
        model = e.get('model', 'unknown')
        agent = e.get('agentId', 'unknown')
        ts = e.get('timestamp', '')
        date_str = ts[:10] if ts else 'unknown'
        
        cost = calc_cost(model, pt, ct)
        
        total_prompt += pt
        total_comp += ct
        total_tokens += tt
        total_cost += cost
        models[model] += tt
        agents[agent] += tt
        daily[date_str]['prompt'] += pt
        daily[date_str]['comp'] += ct
        daily[date_str]['total'] += tt
        daily[date_str]['requests'] += 1
        daily[date_str]['cost'] += cost
        
        if date_str == today:
            today_prompt += pt
            today_comp += ct
            today_tokens += tt
            today_requests += 1
            today_cost += cost
    
    print(f'\n=== ALL TIME ===')
    print(f'Total Requests: {len(entries)}')
    print(f'Total Prompt Tokens: {total_prompt:,}')
    print(f'Total Completion Tokens: {total_comp:,}')
    print(f'Total Tokens: {total_tokens:,}')
    print(f'Total Cost Est: ${total_cost:.4f}')
    
    print(f'\n=== TODAY ({today}) ===')
    print(f'Requests: {today_requests}')
    print(f'Prompt Tokens: {today_prompt:,}')
    print(f'Completion Tokens: {today_comp:,}')
    print(f'Total Tokens: {today_tokens:,}')
    print(f'Cost Est: ${today_cost:.4f}')
    
    print(f'\n=== MODELS ===')
    for m, t in sorted(models.items(), key=lambda x: -x[1]):
        print(f'  {m}: {t:,} tokens')
    
    print(f'\n=== AGENTS ===')
    for a, t in sorted(agents.items(), key=lambda x: -x[1]):
        print(f'  {a}: {t:,} tokens')
    
    print(f'\n=== LAST 7 DAYS ===')
    sorted_days = sorted(daily.items(), key=lambda x: x[0], reverse=True)[:7]
    for date, d in sorted_days:
        print(f'  {date}: {d["total"]:,} tokens ({d["requests"]} reqs, ${d["cost"]:.4f})')
    
    print(f'\n=== LAST 5 REQUESTS ===')
    for e in entries[-5:]:
        u = e.get('usage', {})
        print(f'  {e.get("timestamp","?")[:19]} | {e.get("model","?")} | agent={e.get("agentId","?")} | prompt={u.get("promptTokens",0):,} comp={u.get("completionTokens",0):,} total={u.get("totalTokens",0):,}')
