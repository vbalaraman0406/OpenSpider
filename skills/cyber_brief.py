def compile_briefing():
    """Compile cybersecurity briefing from gathered data."""
    briefing = {
        "zero_days": [
            {"cve": "CVE-2026-20131", "severity": "CVSS 10.0", "affected": "Cisco FMC", "patch": "Patch available, actively exploited by Interlock ransomware"},
            {"cve": "CVE-2026-3055", "severity": "CVSS 9.3", "affected": "Citrix NetScaler ADC/Gateway", "patch": "Patch released, exploit in wild"},
            {"cve": "CVE-2026-3909", "severity": "High", "affected": "Google Chrome V8", "patch": "Chrome update 132.0.6834.83"},
            {"cve": "CVE-2026-20944", "severity": "Critical", "affected": "Microsoft Office/Windows", "patch": "March 2026 Patch Tuesday"}
        ],
        "cisa_alerts": [
            {"cve": "CVE-2025-31277", "vendor": "Apple", "added": "2026-03-20", "due": "2026-04-03", "notes": "Multiple CVEs added, patch ASAP"},
            {"cve": "CVE-2026-3909", "vendor": "Google Chromium V8", "added": "2026-03-13", "due": "2026-03-27", "notes": "Zero-day in Chrome, update required"}
        ],
        "banking": [
            {"title": "US banks on high alert for cyberattacks", "date": "2026-03-04", "details": "Iran war escalation prompts increased vigilance, FS-ISAC alerts issued"},
            {"title": "OCC Reports Cyber Activity", "date": "2026-02-25", "details": "OCC highlights vulnerabilities in financial systems, urges patch management"},
            {"title": "1.2 Million Bank Accounts Exposed", "date": "2026-03-03", "details": "French financial systems breach, data leaked, regulators investigating"}
        ],
        "ai_threats": [
            {"topic": "Adversarial AI", "details": "Deepfake attacks targeting banks rise, using AI-generated voices for fraud"},
            {"topic": "LLM Security", "details": "OpenAI GPT-5 vulnerabilities exposed, prompt injection risks increase"},
            {"topic": "AI Governance", "details": "EU AI Act enforcement begins, strict rules for high-risk AI systems"}
        ],
        "senior_items": [
            {"topic": "Ransomware Trends", "details": "Interlock ransomware exploits Cisco zero-day, demands Bitcoin payments"},
            {"topic": "Nation-State Activity", "details": "Iran-linked APT groups target US critical infrastructure, CISA issues alerts"},
            {"topic": "Supply Chain Risks", "details": "Software supply chain attacks increase, focus on third-party vendors"},
            {"topic": "Regulatory Changes", "details": "SEC mandates cyber incident reporting within 72 hours for public companies"}
        ]
    }
    return briefing

def format_message(briefing):
    """Format briefing into WhatsApp-friendly markdown."""
    message = "🔴 *Zero-Day Vulnerabilities*\n"
    for zd in briefing["zero_days"]:
        message += f"• {zd['cve']} ({zd['severity']}): {zd['affected']} - {zd['patch']}\n"
    
    message += "\n🟠 *CISA Alerts*\n"
    for ca in briefing["cisa_alerts"]:
        message += f"• {ca['cve']} ({ca['vendor']}): Added {ca['added']}, due {ca['due']} - {ca['notes']}\n"
    
    message += "\n🏦 *Banking Sector*\n"
    for bank in briefing["banking"]:
        message += f"• {bank['title']} ({bank['date']}): {bank['details']}\n"
    
    message += "\n🤖 *AI Threats*\n"
    for ai in briefing["ai_threats"]:
        message += f"• {ai['topic']}: {ai['details']}\n"
    
    message += "\n📌 *Action Items*\n"
    message += "• Patch all systems for CVE-2026-20131 and CVE-2026-3055 immediately.\n"
    message += "• Review CISA catalog and apply updates for Apple and Google CVEs by due dates.\n"
    message += "• Enhance monitoring for Iran-linked cyber threats on banking networks.\n"
    message += "• Conduct AI security training and audit LLM usage for vulnerabilities.\n"
    message += "• Update incident response plans per new SEC regulations.\n"
    
    return message

if __name__ == "__main__":
    briefing = compile_briefing()
    whatsapp_message = format_message(briefing)
    print(whatsapp_message)