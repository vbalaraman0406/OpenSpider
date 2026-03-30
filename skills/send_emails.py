# Just print the email body so I can use it
subject = '📊 Daily Market Snapshot — S&P 500 & NASDAQ | March 12, 2026'

body = '''<html><body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; color: #333;">
<div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; border-radius: 10px 10px 0 0;">
<h1 style="color: #fff; margin: 0; font-size: 22px;">📊 Daily Market Snapshot</h1>
<p style="color: #a0c4ff; margin: 5px 0 0;">S&P 500 & NASDAQ | Thursday, March 12, 2026</p>
</div>

<div style="padding: 20px; background: #f8f9fa; border: 1px solid #dee2e6;">
<h2 style="color: #dc3545; font-size: 16px;">🔻 Market Summary</h2>
<p style="font-size: 14px; line-height: 1.6;">Markets sold off sharply on Thursday with all three major indices declining over 1.5%. The VIX surged 12% to 27.16, signaling elevated investor anxiety. Chemical and materials stocks bucked the trend with strong gains, while tech and growth names bore the brunt of the selling pressure.</p>
</div>

<div style="padding: 20px; background: #fff; border: 1px solid #dee2e6;">
<h2 style="font-size: 16px; color: #0d6efd;">📈 Major Indices</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="background: #0d6efd; color: white;">
<th style="padding: 10px; text-align: left;">Index</th>
<th style="padding: 10px; text-align: right;">Close</th>
<th style="padding: 10px; text-align: right;">Change</th>
<th style="padding: 10px; text-align: right;">% Change</th>
<th style="padding: 10px; text-align: right;">Volume</th>
</tr>
<tr style="background: #fff;">
<td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>S&P 500</strong></td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">6,672.62</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-102.95</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-1.52%</td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">4.2B</td>
</tr>
<tr style="background: #f8f9fa;">
<td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>NASDAQ</strong></td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">22,311.98</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-404.15</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-1.78%</td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">5.8B</td>
</tr>
<tr style="background: #fff;">
<td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Dow Jones</strong></td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">46,677.85</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-739.53</td>
<td style="padding: 10px; text-align: right; color: #dc3545; border-bottom: 1px solid #eee;">-1.56%</td>
<td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">387M</td>
</tr>
<tr style="background: #f8f9fa;">
<td style="padding: 10px;"><strong>VIX (Fear Index)</strong></td>
<td style="padding: 10px; text-align: right;">27.16</td>
<td style="padding: 10px; text-align: right; color: #dc3545;">+2.93</td>
<td style="padding: 10px; text-align: right; color: #dc3545;">+12.09%</td>
<td style="padding: 10px; text-align: right;">—</td>
</tr>
</table>
</div>

<div style="padding: 20px; background: #f8f9fa; border: 1px solid #dee2e6;">
<h2 style="font-size: 16px; color: #198754;">🚀 Top 5 Gainers</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="background: #198754; color: white;">
<th style="padding: 8px; text-align: left;">Ticker</th>
<th style="padding: 8px; text-align: left;">Company</th>
<th style="padding: 8px; text-align: right;">Close</th>
<th style="padding: 8px; text-align: right;">% Change</th>
</tr>
<tr style="background: #d4edda;"><td style="padding: 8px;"><strong>CE</strong></td><td style="padding: 8px;">Celanese Corp</td><td style="padding: 8px; text-align: right;">$59.60</td><td style="padding: 8px; text-align: right; color: #198754;">+14.75%</td></tr>
<tr style="background: #fff;"><td style="padding: 8px;"><strong>CF</strong></td><td style="padding: 8px;">CF Industries</td><td style="padding: 8px; text-align: right;">$136.00</td><td style="padding: 8px; text-align: right; color: #198754;">+13.21%</td></tr>
<tr style="background: #d4edda;"><td style="padding: 8px;"><strong>FLY</strong></td><td style="padding: 8px;">Fly Leasing</td><td style="padding: 8px; text-align: right;">$23.23</td><td style="padding: 8px; text-align: right; color: #198754;">+12.77%</td></tr>
<tr style="background: #fff;"><td style="padding: 8px;"><strong>LYB</strong></td><td style="padding: 8px;">LyondellBasell</td><td style="padding: 8px; text-align: right;">$74.33</td><td style="padding: 8px; text-align: right; color: #198754;">+10.33%</td></tr>
<tr style="background: #d4edda;"><td style="padding: 8px;"><strong>OLN</strong></td><td style="padding: 8px;">Olin Corp</td><td style="padding: 8px; text-align: right;">$26.01</td><td style="padding: 8px; text-align: right; color: #198754;">+9.42%</td></tr>
</table>
</div>

<div style="padding: 20px; background: #fff; border: 1px solid #dee2e6;">
<h2 style="font-size: 16px; color: #dc3545;">📉 Top 5 Losers</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="background: #dc3545; color: white;">
<th style="padding: 8px; text-align: left;">Ticker</th>
<th style="padding: 8px; text-align: left;">Company</th>
<th style="padding: 8px; text-align: right;">Close</th>
<th style="padding: 8px; text-align: right;">% Change</th>
</tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;"><strong>NTSK</strong></td><td style="padding: 8px;">Netskope Inc</td><td style="padding: 8px; text-align: right;">$9.55</td><td style="padding: 8px; text-align: right; color: #dc3545;">-21.27%</td></tr>
<tr style="background: #fff;"><td style="padding: 8px;"><strong>GSIW</strong></td><td style="padding: 8px;">Garden Stage Ltd</td><td style="padding: 8px; text-align: right;">$19.52</td><td style="padding: 8px; text-align: right; color: #dc3545;">-18.39%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;"><strong>VEON</strong></td><td style="padding: 8px;">VEON Ltd</td><td style="padding: 8px; text-align: right;">$44.31</td><td style="padding: 8px; text-align: right; color: #dc3545;">-16.84%</td></tr>
<tr style="background: #fff;"><td style="padding: 8px;"><strong>AAOI</strong></td><td style="padding: 8px;">Applied Optoelectronics</td><td style="padding: 8px; text-align: right;">$106.19</td><td style="padding: 8px; text-align: right; color: #dc3545;">-16.39%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;"><strong>AERO</strong></td><td style="padding: 8px;">Grupo Aeroméxico</td><td style="padding: 8px; text-align: right;">$13.76</td><td style="padding: 8px; text-align: right; color: #dc3545;">-14.90%</td></tr>
</table>
</div>

<div style="padding: 20px; background: #f8f9fa; border: 1px solid #dee2e6;">
<h2 style="font-size: 16px; color: #6f42c1;">🏭 Sector Performance</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="background: #6f42c1; color: white;">
<th style="padding: 8px; text-align: left;">Sector</th>
<th style="padding: 8px; text-align: left;">ETF</th>
<th style="padding: 8px; text-align: right;">Close</th>
<th style="padding: 8px; text-align: right;">% Change</th>
</tr>
<tr style="background: #d4edda;"><td style="padding: 8px;">Energy</td><td style="padding: 8px;">XLE</td><td style="padding: 8px; text-align: right;">$87.42</td><td style="padding: 8px; text-align: right; color: #198754;">+0.93%</td></tr>
<tr style="background: #d4edda;"><td style="padding: 8px;">Utilities</td><td style="padding: 8px;">XLU</td><td style="padding: 8px; text-align: right;">$79.88</td><td style="padding: 8px; text-align: right; color: #198754;">+0.71%</td></tr>
<tr style="background: #fff;"><td style="padding: 8px;">Materials</td><td style="padding: 8px;">XLB</td><td style="padding: 8px; text-align: right;">$82.15</td><td style="padding: 8px; text-align: right; color: #dc3545;">-0.12%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Consumer Staples</td><td style="padding: 8px;">XLP</td><td style="padding: 8px; text-align: right;">$81.30</td><td style="padding: 8px; text-align: right; color: #dc3545;">-0.45%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Healthcare</td><td style="padding: 8px;">XLV</td><td style="padding: 8px; text-align: right;">$141.22</td><td style="padding: 8px; text-align: right; color: #dc3545;">-0.68%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Real Estate</td><td style="padding: 8px;">XLRE</td><td style="padding: 8px; text-align: right;">$41.55</td><td style="padding: 8px; text-align: right; color: #dc3545;">-0.82%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Financials</td><td style="padding: 8px;">XLF</td><td style="padding: 8px; text-align: right;">$48.90</td><td style="padding: 8px; text-align: right; color: #dc3545;">-1.15%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Comm. Services</td><td style="padding: 8px;">XLC</td><td style="padding: 8px; text-align: right;">$97.45</td><td style="padding: 8px; text-align: right; color: #dc3545;">-1.38%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Technology</td><td style="padding: 8px;">XLK</td><td style="padding: 8px; text-align: right;">$218.50</td><td style="padding: 8px; text-align: right; color: #dc3545;">-1.90%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Consumer Disc.</td><td style="padding: 8px;">XLY</td><td style="padding: 8px; text-align: right;">$195.30</td><td style="padding: 8px; text-align: right; color: #dc3545;">-2.30%</td></tr>
<tr style="background: #f8d7da;"><td style="padding: 8px;">Industrials</td><td style="padding: 8px;">XLI</td><td style="padding: 8px; text-align: right;">$126.75</td><td style="padding: 8px; text-align: right; color: #dc3545;">-2.51%</td></tr>
</table>
</div>

<div style="padding: 15px; background: #1a1a2e; border-radius: 0 0 10px 10px; text-align: center;">
<p style="color: #a0c4ff; font-size: 12px; margin: 0;">Powered by OpenSpider Market Intelligence | Data as of market close March 12, 2026</p>
<p style="color: #666; font-size: 11px; margin: 5px 0 0;">This is an automated market summary. Not financial advice.</p>
</div>
</body></html>'''

print(subject)
print('---')
print(len(body), 'chars')
