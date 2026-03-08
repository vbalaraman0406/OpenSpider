import os

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 20px; }
  .container { max-width: 680px; margin: 0 auto; background: #16213e; border-radius: 12px; padding: 30px; }
  h1 { color: #e94560; text-align: center; font-size: 24px; }
  h2 { color: #0f3460; background: #e94560; display: inline-block; padding: 4px 14px; border-radius: 6px; font-size: 16px; color: #fff; }
  h3 { color: #e94560; border-bottom: 1px solid #333; padding-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0 20px 0; font-size: 14px; }
  th { background: #0f3460; color: #fff; padding: 8px 10px; text-align: left; }
  td { padding: 7px 10px; border-bottom: 1px solid #2a2a4a; }
  tr:hover td { background: #1a1a3e; }
  .turbo { color: #ff6b6b; font-weight: bold; }
  .good { color: #51cf66; }
  .warn { color: #fcc419; }
  .bad { color: #ff6b6b; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
  .badge-green { background: #2b8a3e; color: #fff; }
  .badge-yellow { background: #e67700; color: #fff; }
  .badge-red { background: #c92a2a; color: #fff; }
  .section { margin: 20px 0; }
  .footer { text-align: center; font-size: 12px; color: #666; margin-top: 30px; }
  .highlight-box { background: #0f3460; border-left: 4px solid #e94560; padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 16px 0; }
</style>
</head>
<body>
<div class="container">

<h1>\U0001f3ce\ufe0f F1 Fantasy Team Update</h1>
<p style="text-align:center; font-size:18px; color:#aaa;">Australian Grand Prix 2026 &bull; Albert Park Circuit, Melbourne &bull; March 8, 2026</p>

<div class="highlight-box">
  <strong>\u26a0\ufe0f Status:</strong> Race Day &mdash; Fantasy team is <strong>LOCKED</strong>. This is a post-race analysis for record-keeping and future optimization.
</div>

<h2>\U0001f4ca FP1 Results (Top 5)</h2>
<table>
  <tr><th>Pos</th><th>Driver</th><th>Team</th><th>Time</th><th>Gap</th></tr>
  <tr><td>1</td><td><strong>Charles Leclerc</strong></td><td>Ferrari</td><td>1:20.267</td><td>&mdash;</td></tr>
  <tr><td>2</td><td><strong>Lewis Hamilton</strong></td><td>Ferrari</td><td>&mdash;</td><td>+0.469s</td></tr>
  <tr><td>3</td><td>Max Verstappen</td><td>Red Bull</td><td>&mdash;</td><td>~+0.7s</td></tr>
  <tr><td>4</td><td>Isack Hadjar</td><td>Red Bull</td><td>&mdash;</td><td>~+0.9s</td></tr>
  <tr><td>5</td><td>Oscar Piastri</td><td>McLaren</td><td>&mdash;</td><td>~+1.0s</td></tr>
</table>
<p><span class="good">\u2705 Ferrari 1-2</span> &mdash; Leclerc dominant, Hamilton strong. Red Bull competitive with Hadjar P4.</p>

<h2>\U0001f4ca FP2 Results (Top 5)</h2>
<table>
  <tr><th>Pos</th><th>Driver</th><th>Team</th><th>Time</th><th>Gap</th></tr>
  <tr><td>1</td><td><strong class="turbo">Oscar Piastri \U0001f525 TURBO</strong></td><td>McLaren</td><td>1:19.729</td><td>&mdash;</td></tr>
  <tr><td>2</td><td>Kimi Antonelli</td><td>Mercedes</td><td>&mdash;</td><td>+0.214s</td></tr>
  <tr><td>3</td><td>George Russell</td><td>Mercedes</td><td>&mdash;</td><td>+0.320s</td></tr>
  <tr><td>4</td><td>Lewis Hamilton</td><td>Ferrari</td><td>&mdash;</td><td>+0.321s</td></tr>
  <tr><td>5</td><td>Charles Leclerc</td><td>Ferrari</td><td>&mdash;</td><td>~+0.5s</td></tr>
</table>
<p><span class="good">\u2705 Piastri fastest overall</span> &mdash; McLaren-Mercedes package excelling. Mercedes 2-3 shows strong race pace.</p>

<h2>\U0001f3c1 Race Result</h2>
<div class="highlight-box">
  <strong>\U0001f3c6 Winner: George Russell (Mercedes)</strong><br>
  Mercedes showed dominant race pace after strong FP2 showing.
</div>

<h2>\U0001f4cb Current Fantasy Team Analysis</h2>
<table>
  <tr><th>Role</th><th>Pick</th><th>Price</th><th>Practice Form</th><th>Verdict</th></tr>
  <tr>
    <td><span class="turbo">TURBO</span></td>
    <td><strong>Oscar Piastri</strong></td>
    <td>$25.5M</td>
    <td><span class="badge badge-green">FP2 P1</span> &mdash; 1:19.729, fastest overall</td>
    <td class="good">\u2705 Excellent pick</td>
  </tr>
  <tr>
    <td>Driver</td>
    <td>Isack Hadjar</td>
    <td>$15.1M</td>
    <td><span class="badge badge-green">FP1 P4</span> &mdash; Strong Red Bull pace</td>
    <td class="good">\u2705 Solid</td>
  </tr>
  <tr>
    <td>Driver</td>
    <td>Carlos Sainz</td>
    <td>$11.8M</td>
    <td><span class="badge badge-yellow">Not in top 5</span> &mdash; Williams midfield</td>
    <td class="warn">\u26a0\ufe0f Monitor</td>
  </tr>
  <tr>
    <td>Driver</td>
    <td>Oliver Bearman</td>
    <td>$7.4M</td>
    <td><span class="badge badge-yellow">Data limited</span> &mdash; Budget pick</td>
    <td class="warn">\u26a0\ufe0f Budget filler</td>
  </tr>
  <tr>
    <td>Driver</td>
    <td>Sergio Perez</td>
    <td>$6.0M</td>
    <td><span class="badge badge-red">Not visible</span> &mdash; Red Bull #2 struggles</td>
    <td class="bad">\u274c Weakest link</td>
  </tr>
  <tr>
    <td>Constructor</td>
    <td><strong>Ferrari</strong></td>
    <td>$23.3M</td>
    <td><span class="badge badge-green">FP1 1-2</span>, Hamilton P4 FP2</td>
    <td class="good">\u2705 Both cars in points likely</td>
  </tr>
  <tr>
    <td>Constructor</td>
    <td>Aston Martin</td>
    <td>$10.3M</td>
    <td><span class="badge badge-red">FP1 woes</span> &mdash; Poor practice form</td>
    <td class="bad">\u274c Risky pick</td>
  </tr>
</table>
<p><strong>Budget remaining:</strong> $0.6M</p>

<h2>\U0001f525 Turbo Driver: Oscar Piastri</h2>
<div class="highlight-box">
  <strong>Why Piastri?</strong><br>
  \u2022 <strong>Fastest in FP2</strong> with 1:19.729 &mdash; 0.214s clear of P2<br>
  \u2022 McLaren-Mercedes package showing excellent single-lap and race pace<br>
  \u2022 High qualifying position expected &rarr; strong points haul<br>
  \u2022 Turbo doubles all points &mdash; a podium finish = massive score<br>
  <strong>Verdict:</strong> <span class="good">CONFIRMED \u2705</span> &mdash; Piastri remains the optimal Turbo selection.
</div>

<h2>\u26a0\ufe0f Key Risks &amp; Watch List</h2>
<table>
  <tr><th>Risk</th><th>Impact</th><th>Action for Chinese GP</th></tr>
  <tr>
    <td><span class="bad">Aston Martin poor form</span></td>
    <td>Constructor unlikely to score both-cars bonus (+10 pts lost)</td>
    <td>Swap to <strong>Mercedes ($24.5M?)</strong> or <strong>McLaren</strong> if budget allows</td>
  </tr>
  <tr>
    <td><span class="warn">Perez invisible in practice</span></td>
    <td>$6.0M wasted if outside points</td>
    <td>Consider <strong>Antonelli</strong> or another rising driver</td>
  </tr>
  <tr>
    <td><span class="warn">Sainz midfield with Williams</span></td>
    <td>$11.8M may underperform vs. price</td>
    <td>Monitor Williams development; consider <strong>Russell</strong> if funds free up</td>
  </tr>
  <tr>
    <td><span class="good">Mercedes surge</span></td>
    <td>Russell WON the race; Antonelli P2 FP2</td>
    <td>Strong candidate for constructor swap from Aston Martin</td>
  </tr>
</table>

<h2>\U0001f52e Recommendations for Chinese GP (March 22)</h2>
<div class="highlight-box">
  <strong>Priority swaps to evaluate:</strong><br>
  1. <strong>Aston Martin \u2192 Mercedes/McLaren</strong> (constructor) &mdash; if budget permits after price changes<br>
  2. <strong>Perez \u2192 Antonelli or budget alternative</strong> &mdash; Mercedes pace is real<br>
  3. <strong>Keep Piastri TURBO</strong> &mdash; McLaren looks like a title contender<br>
  4. <strong>Keep Ferrari constructor</strong> &mdash; Leclerc + Hamilton is a reliable points machine<br>
  <br>
  \U0001f4c5 Next optimization window: <strong>March 19-20, 2026</strong> (FP1/FP2 for Chinese GP)
</div>

<div class="footer">
  <p>Generated by OpenSpider F1 Fantasy Optimizer &bull; Data from FP1 &amp; FP2 sessions &bull; March 8, 2026</p>
</div>

</div>
</body>
</html>"""

wa_content = """🏎️ F1 FANTASY TEAM UPDATE
Australian Grand Prix 2026
Albert Park Circuit, Melbourne | March 8, 2026

⚠️ STATUS: Race Day — Team is LOCKED
This is a post-race analysis.

🏆 RACE WINNER: George Russell (Mercedes)

📊 FP1 TOP 5:
1. Charles Leclerc (Ferrari) — 1:20.267
2. Lewis Hamilton (Ferrari) — +0.469s
3. Max Verstappen (Red Bull)
4. Isack Hadjar (Red Bull)
5. Oscar Piastri (McLaren)
→ Ferrari 1-2, dominant pace

📊 FP2 TOP 5:
1. Oscar Piastri (McLaren) — 1:19.729 🔥
2. Kimi Antonelli (Mercedes) — +0.214s
3. George Russell (Mercedes) — +0.320s
4. Lewis Hamilton (Ferrari) — +0.321s
5. Charles Leclerc (Ferrari)
→ Piastri fastest overall, Mercedes strong

📋 CURRENT TEAM:
🔥 TURBO: Oscar Piastri ($25.5M) ✅ FP2 P1
• Isack Hadjar ($15.1M) ✅ FP1 P4
• Carlos Sainz ($11.8M) ⚠️ Midfield
• Oliver Bearman ($7.4M) ⚠️ Budget pick
• Sergio Perez ($6.0M) ❌ Invisible
🏗️ Ferrari ($23.3M) ✅ FP1 1-2
🏗️ Aston Martin ($10.3M) ❌ Poor practice
Budget: $0.6M remaining

🔥 TURBO PICK: Oscar Piastri
→ Fastest in FP2, 0.214s clear
→ McLaren-Mercedes package excelling
→ High qualifying = big Turbo points
✅ CONFIRMED as optimal Turbo

⚠️ KEY RISKS:
• Aston Martin had woes in FP1 — swap candidate
• Perez not in top results — weakest link
• Mercedes surging (Russell won!)

🔮 CHINESE GP RECOMMENDATIONS (Mar 22):
1. Swap Aston Martin → Mercedes constructor
2. Swap Perez → Antonelli if budget allows
3. Keep Piastri TURBO
4. Keep Ferrari constructor

📅 Next optimization: March 19-20

— OpenSpider F1 Fantasy Optimizer"""

os.makedirs('workspace', exist_ok=True)

with open('workspace/f1_fantasy_update.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open('workspace/f1_fantasy_update_wa.txt', 'w', encoding='utf-8') as f:
    f.write(wa_content)

print('Files written successfully:')
print('  - workspace/f1_fantasy_update.html')
print('  - workspace/f1_fantasy_update_wa.txt')