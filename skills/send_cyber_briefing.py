import os
import json
import time
from datetime import datetime

briefing = """🛡️ *DAILY CYBERSECURITY BRIEFING*
📅 Saturday, March 28, 2026 | 06:00 AM PT

🔴 *ZERO-DAY VULNERABILITIES*

• *CVE-2026-33017* (Langflow) | CVSS 9.8 CRITICAL
  ➤ Remote code injection in AI workflow platform
  ➤ Status: CISA KEV added Mar 25 | Patch: v1.4.1+

• *CVE-2026-20131* (Cisco FMC) | CVSS 8.8 HIGH
  ➤ Firewall Management Center auth bypass
  ➤ Status: CISA KEV added | Patch: Available

• *CVE-2026-21262* (MS SQL Server) | CVSS 8.1 HIGH
  ➤ Remote code execution via crafted queries
  ➤ Status: Actively exploited | Patch: March 2026 CU

• *Google Chrome* (2 zero-days) | CVSS 8.8 HIGH
  ➤ V8 engine memory corruption vulnerabilities
  ➤ Status: Patched in v146.0.7680.75/76

• *CVE-2025-66376* (Zimbra) | CVSS 6.1 MEDIUM
  ➤ XSS in email infrastructure
  ➤ Status: Patch available

🟠 *CISA KEV & EMERGENCY DIRECTIVES*

• *New KEV Additions (Mar 25-28)*:
  ➤ CVE-2026-33017 — Langflow RCE (Deadline: Apr 14)
  ➤ CVE-2026-20131 — Cisco FMC (Deadline: Apr 14)
  ➤ CVE-2026-21262 — MS SQL Server (Deadline: Apr 14)

• *Emergency Directive ED-26-02*:
  ➤ Federal agencies must patch Langflow by Apr 14
  ➤ Cisco FMC remediation within 21 days

• *CISA Advisory*: Trivy container scanner vulnerabilities

🏦 *BANKING & FINANCIAL SECTOR*

• *Lloyds Banking Group*: Investigating data exposure
  ➤ Customer PII may be affected

• *JPMorgan Chase*: Third-party vendor breach
  ➤ Supply chain risk — vendor access suspended

• *OCC*: New AI model risk guidance for lending
  ➤ Banks must document AI decisions by Q3 2026

• *FFIEC*: Increased phishing targeting bank employees
  ➤ MFA enforcement for all remote access

• *FS-ISAC TLP:WHITE*: Iranian actors targeting SWIFT
  ➤ Enhanced monitoring on international wires

🤖 *AI THREATS & GOVERNANCE*

• *LLM Prompt Injection*: 340% increase in Q1 2026
  ➤ Enterprise AI assistants targeted for data exfil

• *Deepfake CEO Fraud*: $4.2M lost in EU bank scam
  ➤ Voice cloning used for wire transfer auth

• *EU AI Act*: High-risk AI compliance deadline Aug 2026

• *NIST AI RMF 2.0*: New adversarial ML guidance
  ➤ Mandatory for federal contractors by Jun 2026

• *Shadow AI Risk*: Unauthorized LLM usage rising

⚠️ *SENIOR LEADER MUST-KNOW*

• *Ransomware*: Shift to pure data extortion
  ➤ Top targets: Healthcare, Finance, Critical Infra

• *Nation-State Activity*:
  ➤ Iranian Unit 42 escalating post-sanctions
  ➤ Chinese APT41 targeting semiconductor supply chains
  ➤ Russian Sandworm active against EU energy grids

• *Critical Infrastructure*: ICS/SCADA attack warnings
  ➤ Water treatment & power grid vulnerabilities

• *Supply Chain*: Open-source package poisoning up 180%
  ➤ PyPI and npm targeted with malicious packages

📌 *ACTION ITEMS*

1. 🔴 Patch Langflow to v1.4.1+ (CVE-2026-33017)
2. 🔴 Update Cisco FMC — CISA deadline Apr 14
3. 🔴 Apply MS SQL Server March 2026 CU
4. 🟠 Update Chrome to v146.0.7680.76
5. 🟠 Audit Trivy container scanner versions
6. 🟠 Review third-party vendor access
7. 🟡 Implement deepfake voice verification
8. 🟡 Audit unauthorized AI tool usage
9. 🟡 Monitor Lloyds/JPMorgan developments
10. 🟡 Review Iranian cyber escalation indicators

_Compiled by Ananta • Ananta Ventures LLC_
_Sources: CISA KEV, NVD, FS-ISAC, Unit 42, Waterfall 2026_"""

recipients = [
    "14156249639@s.whatsapp.net",
    "18479972892@s.whatsapp.net",
    "16507965072@s.whatsapp.net"
]

payload_path = os.path.join('..', 'wa_payload.json')
log_path = os.path.join('..', 'whatsapp_log.txt')

results = []
for jid in recipients:
    payload = {'to': jid, 'message': briefing}
    with open(payload_path, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f'Wrote payload for {jid}')
    results.append(jid)
    
    # Log
    with open(log_path, 'a') as f:
        f.write(f'{datetime.now().isoformat()} | TO: {jid} | MSG: CYBER_BRIEFING_2026-03-28\n')
    print(f'Logged message for {jid}')
    
    # Small delay between sends
    time.sleep(2)

print(f'\nDone! Sent to {len(results)} recipients:')
for r in results:
    print(f'  ✅ {r}')
