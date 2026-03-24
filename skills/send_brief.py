import json

email_html = """
<html>
<head>
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
.container { max-width: 700px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.header { background: linear-gradient(135deg, #1a237e, #283593); color: white; padding: 30px; text-align: center; }
.header h1 { margin: 0; font-size: 28px; }
.header p { margin: 5px 0 0; opacity: 0.85; font-size: 14px; }
.section { padding: 20px 25px; border-bottom: 1px solid #eee; }
.section h2 { color: #1a237e; font-size: 20px; margin-top: 0; border-left: 4px solid #1a237e; padding-left: 12px; }
table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }
th { background: #1a237e; color: white; padding: 10px 8px; text-align: left; font-size: 12px; }
td { padding: 8px; border-bottom: 1px solid #eee; }
tr:nth-child(even) { background: #f8f9fa; }
.hot { color: #d32f2f; font-weight: bold; }
.cold { color: #1565c0; font-weight: bold; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; margin: 2px; }
.tag-green { background: #e8f5e9; color: #2e7d32; }
.tag-red { background: #ffebee; color: #c62828; }
.tag-orange { background: #fff3e0; color: #e65100; }
.tag-blue { background: #e3f2fd; color: #1565c0; }
.footer { padding: 15px 25px; text-align: center; color: #999; font-size: 11px; background: #f8f9fa; }
ul { padding-left: 20px; }
li { margin-bottom: 8px; line-height: 1.5; }
.alert-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 15px; margin: 10px 0; border-radius: 4px; }
.injury-box { background: #ffebee; border-left: 4px solid #d32f2f; padding: 12px 15px; margin: 10px 0; border-radius: 4px; }
</style>
</head>
<body>
<div class="container">

<div class="header">
<h1>⚾ Fantasy Baseball Morning Brief</h1>
<p>Thursday, March 19, 2026 | Spring Training Edition</p>
<p style="font-size:12px; opacity:0.7;">Powered by OpenSpider Fantasy Ops | Market Makers League</p>
</div>

<!-- SECTION 1: ROSTER NEWS -->
<div class="section">
<h2>📋 Roster News & Transactions</h2>
<p>Key roster moves and transactions shaping the 2026 fantasy landscape:</p>
<ul>
<li><strong>Gerrit Cole (SP, NYY)</strong> — <span class="tag tag-green">RETURNING</span> Progressing well in spring training after missing significant time. Expected to be in the Opening Day rotation. Fantasy managers should feel confident drafting him as a top-15 SP.</li>
<li><strong>Zack Wheeler (SP, PHI)</strong> — <span class="tag tag-green">RETURNING</span> Working his way back and expected to rejoin the Phillies rotation early in the season. Andrew Painter filling his spot until return.</li>
<li><strong>Corbin Carroll (OF, ARI)</strong> — <span class="tag tag-green">HEALTHY</span> Fully recovered from hamate bone surgery. Looking sharp in spring training and poised for a bounce-back season. Buy-low window closing.</li>
<li><strong>Francisco Lindor (SS, NYM)</strong> — <span class="tag tag-green">HEALTHY</span> Back from hamate bone injury and looking like his usual self. Draft with confidence as a top-5 SS.</li>
<li><strong>Anthony Volpe (SS, NYY)</strong> — <span class="tag tag-red">IL</span> Starting the season on the Injured List with a shoulder labrum issue. Significant concern — avoid drafting until timeline is clearer.</li>
<li><strong>Pablo López (SP, MIN)</strong> — <span class="tag tag-red">OUT FOR SEASON</span> Underwent Tommy John surgery. Do not draft. Complete loss for 2026 fantasy purposes.</li>
<li><strong>Yu Darvish (SP, SD)</strong> — <span class="tag tag-red">OUT FOR 2026</span> Will miss the entire 2026 season. Remove from all draft boards.</li>
<li><strong>Logan Evans (SP)</strong> — <span class="tag tag-red">OUT FOR 2026</span> Also expected to miss the full season.</li>
<li><strong>Jordan Westburg (3B/SS, BAL)</strong> — <span class="tag tag-orange">MONITOR</span> UCL concerns being monitored. Could impact his availability — draft with caution and have a backup plan.</li>
<li><strong>Seiya Suzuki (OF, CHC)</strong> — <span class="tag tag-orange">MONITOR</span> Could miss time early in the season. Keep an eye on spring training updates before finalizing draft position.</li>
<li><strong>José Berríos (SP, TOR)</strong> — <span class="tag tag-orange">MONITOR</span> Expected to miss at least one start. Minor concern but worth noting for early-season streaming decisions.</li>
</ul>
</div>

<!-- SECTION 2: INJURY REPORTS -->
<div class="section">
<h2>🏥 Injury Report — Fantasy Impact</h2>
<div class="injury-box">
<strong>🚨 HIGH IMPACT INJURIES</strong>
</div>
<table>
<tr><th>Player</th><th>Team</th><th>Pos</th><th>Injury</th><th>Status</th><th>Fantasy Impact</th></tr>
<tr><td><strong>Anthony Volpe</strong></td><td>NYY</td><td>SS</td><td>Shoulder Labrum</td><td><span class="tag tag-red">IL</span></td><td>Avoid in drafts. No clear return timeline. Significant downgrade.</td></tr>
<tr><td><strong>Pablo López</strong></td><td>MIN</td><td>SP</td><td>Tommy John Surgery</td><td><span class="tag tag-red">OUT</span></td><td>Complete season loss. Do not draft under any circumstances.</td></tr>
<tr><td><strong>Yu Darvish</strong></td><td>SD</td><td>SP</td><td>Undisclosed</td><td><span class="tag tag-red">OUT</span></td><td>Out for 2026. Remove from all boards.</td></tr>
<tr><td><strong>Spencer Strider</strong></td><td>ATL</td><td>SP</td><td>Velocity Concerns</td><td><span class="tag tag-orange">WATCH</span></td><td>10% decrease in high-velocity fastball usage. Risky at current ADP.</td></tr>
<tr><td><strong>Jordan Westburg</strong></td><td>BAL</td><td>3B/SS</td><td>UCL Issue</td><td><span class="tag tag-orange">WATCH</span></td><td>Monitor closely. Could require surgery if it worsens.</td></tr>
<tr><td><strong>Seiya Suzuki</strong></td><td>CHC</td><td>OF</td><td>Undisclosed</td><td><span class="tag tag-orange">DTD</span></td><td>May miss early-season games. Slight ADP discount warranted.</td></tr>
<tr><td><strong>Luis Robert Jr.</strong></td><td>NYM</td><td>OF</td><td>Injury History</td><td><span class="tag tag-orange">RISK</span></td><td>Traded to Mets but injury concerns persist. High bust potential at ADP.</td></tr>
<tr><td><strong>Gerrit Cole</strong></td><td>NYY</td><td>SP</td><td>Returning</td><td><span class="tag tag-green">GO</span></td><td>On track for Opening Day. Draft as SP1 with confidence.</td></tr>
<tr><td><strong>Zack Wheeler</strong></td><td>PHI</td><td>SP</td><td>Returning</td><td><span class="tag tag-green">GO</span></td><td>Will miss early starts but expected back by mid-April.</td></tr>
</table>
</div>

<!-- SECTION 3: WAIVER WIRE -->
<div class="section">
<h2>🔥 Top 10 Waiver Wire Pickups — Week 1</h2>
<p>These players are widely available and could provide immediate fantasy value. Act fast before your leaguemates catch on!</p>
<table>
<tr><th>#</th><th>Player</th><th>Team</th><th>Pos</th><th>Own%</th><th>Why Add?</th></tr>
<tr><td>1</td><td><strong>Matt McLain</strong></td><td>CIN</td><td>SS/2B</td><td>~55%</td><td>🔥 Scorching hot spring training. ADP rising rapidly. Elite power-speed combo when healthy. Could be a top-5 SS if he stays on the field.</td></tr>
<tr><td>2</td><td><strong>JJ Wetherholt</strong></td><td>STL</td><td>2B/3B</td><td>~30%</td><td>Hitting .300 with 1.000 OPS in spring. Expected to contend for starting role. 15/20 power-speed upside. Must-add in all formats.</td></tr>
<tr><td>3</td><td><strong>Kevin McGonigle</strong></td><td>DET</td><td>SS</td><td>~15%</td><td>Top prospect getting called up. Expected to make Opening Day roster. High-contact bat with developing power.</td></tr>
<tr><td>4</td><td><strong>Daylen Lile</strong></td><td>—</td><td>OF</td><td>~10%</td><td>Exciting prospect with plus speed and improving bat. Stash in deeper leagues for potential mid-season impact.</td></tr>
<tr><td>5</td><td><strong>Kirby Yates</strong></td><td>—</td><td>RP</td><td>~40%</td><td>Elite closer who could rack up saves early. If he's available, grab him immediately for ratio and saves help.</td></tr>
<tr><td>6</td><td><strong>Caleb Durbin</strong></td><td>—</td><td>2B/OF</td><td>~20%</td><td>Speed demon who could contribute 30+ steals. Excellent late-round value in roto and categories leagues.</td></tr>
<tr><td>7</td><td><strong>Trey Yesavage</strong></td><td>TOR</td><td>SP</td><td>~8%</td><td>Prospect with rising stock. Could slot into Toronto's rotation with Berríos missing time. Streaming upside.</td></tr>
<tr><td>8</td><td><strong>Andrew Painter</strong></td><td>PHI</td><td>SP</td><td>~25%</td><td>Filling Wheeler's rotation spot. Has ace-level stuff. Deep sleeper SP who could emerge as a top-30 arm.</td></tr>
<tr><td>9</td><td><strong>Andrés Giménez</strong></td><td>TOR</td><td>2B/SS</td><td>~45%</td><td>Traded to Toronto. AL East sleeper with 20/20 potential. Undervalued at current ADP after trade.</td></tr>
<tr><td>10</td><td><strong>Colton Cowser</strong></td><td>BAL</td><td>OF</td><td>~35%</td><td>Breakout candidate in Baltimore's potent lineup. Power-speed combo with excellent plate discipline.</td></tr>
</table>
<div class="alert-box">
<strong>💡 Deep Sleepers:</strong> Connelly Early (SP, BOS) — impressive spring training performance. George Klassen (SP, LAA) — plus power stuff, could emerge by midseason. Chandler Simpson (OF, TB) — outlier speed for SB-needy teams. Justin Crawford (OF, PHI) — strong spring, could make Opening Day roster.
</div>
</div>

<!-- SECTION 4: MATCHUP PREVIEWS -->
<div class="section">
<h2>📊 Today's Key Matchup Previews — March 19</h2>
<p><em>Spring Training games continue today. Here are the key matchups and pitchers to watch:</em></p>

<table>
<tr><th>Matchup</th><th>Starting Pitchers</th><th>Fantasy Notes</th></tr>
<tr><td><strong>TB vs PHI</strong></td><td>Drew Rasmussen (TB) vs TBD (PHI)</td><td>Rasmussen returning from injury — monitor his pitch count and velocity. Could be a streaming option early in the season if healthy.</td></tr>
<tr><td><strong>HOU vs MIA</strong></td><td>TBD vs TBD</td><td>Spring Breakout showcase game. Watch for prospect performances from both sides. Astros lineup always dangerous.</td></tr>
<tr><td><strong>BOS vs TBD</strong></td><td>Brayan Bello (BOS)</td><td>Bello is a breakout candidate for 2026. Monitor his spring outings closely — he's being drafted as a mid-tier SP2.</td></tr>
<tr><td><strong>Various ST Games</strong></td><td>Trevor Rogers</td><td>Rogers looking to bounce back. If he shows improved command, he could be a late-round SP target.</td></tr>
</table>

<h3>🎯 Top Pitchers to Target for 2026 (Consensus Rankings)</h3>
<table>
<tr><th>Rank</th><th>Pitcher</th><th>Team</th><th>Notes</th></tr>
<tr><td>1</td><td><strong>Tarik Skubal</strong></td><td>DET</td><td>Consensus #1 SP. Elite strikeout upside with improved command. Draft as your ace.</td></tr>
<tr><td>2</td><td><strong>Paul Skenes</strong></td><td>PIT</td><td>Sophomore sensation. Electric stuff with ace ceiling. Top-3 SP lock.</td></tr>
<tr><td>3</td><td><strong>Garrett Crochet</strong></td><td>BOS</td><td>Moved to Boston's rotation. Dominant stuff with high K upside. SP1 potential.</td></tr>
<tr><td>4</td><td><strong>Yoshinobu Yamamoto</strong></td><td>LAD</td><td>Year 2 adjustment expected to be smoother. Elite pitch mix and command.</td></tr>
<tr><td>5</td><td><strong>Gerrit Cole</strong></td><td>NYY</td><td>Returning healthy. When right, he's a top-3 pitcher in baseball.</td></tr>
</table>
</div>

<!-- SECTION 5: TRENDING PLAYERS -->
<div class="section">
<h2>📈 Trending Players — Hot & Cold</h2>

<h3 class="hot">🔥 WHO'S HOT — Spring Training Risers</h3>
<table>
<tr><th>Player</th><th>Team</th><th>Pos</th><th>Spring Stats</th><th>Why They're Rising</th></tr>
<tr><td><strong>Matt McLain</strong></td><td>CIN</td><td>SS/2B</td><td>Scorching</td><td>ADP skyrocketing. Looks fully healthy and is mashing the ball. Could be a league-winner if he stays on the field all season.</td></tr>
<tr><td><strong>Curtis Mead</strong></td><td>TB</td><td>3B/2B</td><td>Leading hitter</td><td>One of the top spring training hitters. Power is translating. Could lock down an everyday role.</td></tr>
<tr><td><strong>Josh Lowe</strong></td><td>TB</td><td>OF</td><td>Hot bat</td><td>Showing improved power and consistency. 20/30 upside makes him a steal at current ADP.</td></tr>
<tr><td><strong>Rhys Hoskins</strong></td><td>—</td><td>1B</td><td>6 HR (leads ST)</td><td>Leading all of spring training in home runs. Power is back in a big way. Late-round 1B value.</td></tr>
<tr><td><strong>Samuel Basallo</strong></td><td>BAL</td><td>C</td><td>Hot spring</td><td>21-year-old Orioles prospect with elite bat speed. Could be the next great fantasy catcher if he earns the starting job.</td></tr>
<tr><td><strong>Connelly Early</strong></td><td>BOS</td><td>SP</td><td>Impressive</td><td>Red Sox prospect turning heads with dominant spring outings. Deep-league stash with upside.</td></tr>
<tr><td><strong>JJ Wetherholt</strong></td><td>STL</td><td>2B/3B</td><td>.300/1.000 OPS</td><td>Cardinals prospect looking like a future star. Add now before ownership spikes.</td></tr>
</table>

<h3 class="cold">❄️ WHO'S COLD — Caution Flags</h3>
<table>
<tr><th>Player</th><th>Team</th><th>Pos</th><th>Concern</th><th>Fantasy Advice</th></tr>
<tr><td><strong>Spencer Strider</strong></td><td>ATL</td><td>SP</td><td>Velocity down 10%</td><td>High-velocity fastball usage dropping significantly. At his ADP, the risk may outweigh the reward. Consider fading.</td></tr>
<tr><td><strong>Luis Robert Jr.</strong></td><td>NYM</td><td>OF</td><td>Injury history</td><td>Traded to Mets but can't stay healthy. High draft cost + injury risk = potential bust. Draft with extreme caution.</td></tr>
<tr><td><strong>Cal Raleigh</strong></td><td>SEA</td><td>C</td><td>Regression risk</td><td>ADP of 13.4 is too rich. Fatigue and regression concerns make him a risky pick at that price point.</td></tr>
<tr><td><strong>Pablo López</strong></td><td>MIN</td><td>SP</td><td>Tommy John</td><td>Season over before it started. Complete avoid.</td></tr>
<tr><td><strong>Anthony Volpe</strong></td><td>NYY</td><td>SS</td><td>Shoulder labrum</td><td>Starting on IL with no clear timeline. His ADP should crater — do not draft at pre-injury price.</td></tr>
</table>
</div>

<!-- SECTION 6: QUICK HITS -->
<div class="section">
<h2>⚡ Quick Hits & Draft Tips</h2>
<ul>
<li><strong>Prospect Call-Ups to Watch:</strong> Kevin McGonigle (DET), JJ Wetherholt (STL), Trey Yesavage (TOR), Justin Crawford (PHI), Samuel Basallo (BAL)</li>
<li><strong>Buy Low:</strong> Corbin Carroll (ARI) — fully healthy from hamate surgery, ADP still depressed from 2025 struggles. Elite upside.</li>
<li><strong>Sell High:</strong> Cal Raleigh (SEA) — if someone offers top-50 value, take it. Regression is coming.</li>
<li><strong>Streaming SP Strategy:</strong> Target Andrew Painter (PHI) and Trey Yesavage (TOR) early in the season while Wheeler and Berríos are out.</li>
<li><strong>Saves Strategy:</strong> Kirby Yates is being undervalued. Closers are scarce — lock one down early.</li>
<li><strong>Stolen Base Targets:</strong> Caleb Durbin and Chandler Simpson are elite speed options available in late rounds.</li>
</ul>
</div>

<div class="footer">
<p>⚾ Fantasy Baseball Morning Brief | March 19, 2026</p>
<p>Compiled by OpenSpider Fantasy Ops Manager | Sources: RotoBaller, FantasyPros, ESPN, Yahoo Sports, MLB.com, Razzball, Sports Illustrated, Baseball Savant</p>
<p>Market Makers League (Manager: Uncle Freddy) | Team ID #34277</p>
<p style="font-size:10px; color:#bbb;">This is an automated fantasy baseball intelligence brief. Data sourced from publicly available spring training reports and fantasy analysis.</p>
</div>

</div>
</body>
</html>
"""

print("EMAIL_HTML_READY")
print(f"Length: {len(email_html)} characters")
