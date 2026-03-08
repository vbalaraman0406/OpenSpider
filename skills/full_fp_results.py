import requests

headers = {'User-Agent': 'Mozilla/5.0'}

session_keys = {'FP1': 9686, 'FP2': 9687}

# Get driver mapping from FP1 session
resp = requests.get('https://api.openf1.org/v1/drivers?session_key=9686', headers=headers, timeout=10)
drivers = {}
if resp.status_code == 200:
    for d in resp.json():
        drivers[d.get('driver_number')] = {'name': d.get('full_name','?'), 'team': d.get('team_name','?')}

for session_name, skey in session_keys.items():
    print(f'\n=== {session_name} RESULTS (2025 Australian GP) ===')
    resp = requests.get(f'https://api.openf1.org/v1/laps?session_key={skey}', headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        best = {}
        lap_counts = {}
        for lap in data:
            dn = lap.get('driver_number')
            dur = lap.get('lap_duration')
            ln = lap.get('lap_number', 0)
            if dn not in lap_counts or ln > lap_counts[dn]:
                lap_counts[dn] = ln
            if dur and (dn not in best or dur < best[dn]):
                best[dn] = dur
        sorted_best = sorted(best.items(), key=lambda x: x[1])
        leader_time = sorted_best[0][1] if sorted_best else 0
        print(f'Pos | Driver | Team | Best Lap | Gap | Laps')
        print(f'--- | ------ | ---- | -------- | --- | ----')
        for i, (dn, dur) in enumerate(sorted_best):
            mins = int(dur // 60)
            secs = dur - mins * 60
            time_str = f'{mins}:{secs:06.3f}'
            gap = dur - leader_time
            gap_str = f'+{gap:.3f}' if gap > 0 else 'LEADER'
            d = drivers.get(dn, {'name': f'#{dn}', 'team': '?'})
            laps = lap_counts.get(dn, '?')
            print(f'P{i+1} | {d["name"]} | {d["team"]} | {time_str} | {gap_str} | {laps}')
