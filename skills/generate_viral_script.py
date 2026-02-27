import os
import re
import json
from datetime import datetime


def execute(args: dict) -> dict:
    try:
        topic = args.get("topic", "").strip()
        platform = args.get("platform", "TikTok").strip()

        if not topic:
            return {"success": False, "error": "A 'topic' is required."}

        valid_platforms = ["tiktok", "instagram reels", "youtube shorts"]
        if platform.lower() not in valid_platforms:
            return {
                "success": False,
                "error": f"Invalid platform '{platform}'. Choose from: TikTok, Instagram Reels, YouTube Shorts."
            }

        platform_lower = platform.lower()

        # --- Generate Hook Variations ---
        hooks = _generate_hooks(topic, platform_lower)

        # --- Generate Script Body (Visual | Audio two-column) ---
        script_body = _generate_script_body(topic, platform_lower)

        # --- Generate CTA ---
        cta = _generate_cta(topic, platform_lower)

        # --- Generate SEO Data ---
        hashtags, caption = _generate_seo_data(topic, platform_lower)

        # --- Format the full script ---
        formatted_script = _format_script(
            topic, platform, hooks, script_body, cta, hashtags, caption
        )

        # --- Save to file ---
        safe_filename = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
        if not safe_filename:
            safe_filename = "script"
        filename = f"{safe_filename}_script.txt"
        filepath = os.path.abspath(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_script)

        return {
            "success": True,
            "message": f"Viral script for '{topic}' on {platform} has been generated and saved successfully.",
            "file_path": filepath,
            "script_preview": formatted_script[:500] + "..." if len(formatted_script) > 500 else formatted_script
        }

    except Exception as e:
        return {"success": False, "error": f"An error occurred: {str(e)}"}


def _generate_hooks(topic: str, platform: str) -> list:
    """Generate 3 powerful hook variations for the topic."""
    hooks = [
        f"Stop scrolling! You NEED to know this about {topic} before it's too late...",
        f"I can't believe nobody is talking about {topic}... here's what they don't want you to know.",
        f"POV: You just discovered the {topic} secret that changes EVERYTHING 🤯"
    ]

    if platform == "tiktok":
        hooks[0] = f"Wait wait wait... did you know THIS about {topic}?! 😳"
        hooks[2] = f"This {topic} hack is going viral for a reason... let me show you 🔥"
    elif platform == "instagram reels":
        hooks[0] = f"Save this reel! Everything you need to know about {topic} in 60 seconds ⬇️"
        hooks[2] = f"The {topic} guide you've been searching for 👇✨"
    elif platform == "youtube shorts":
        hooks[0] = f"{topic} explained in under 60 seconds — you won't believe #3..."
        hooks[2] = f"Here's why {topic} is breaking the internet right now 🚀"

    return hooks


def _generate_script_body(topic: str, platform: str) -> list:
    """Generate the two-column script body with Visual and Audio cues."""
    script_sections = [
        {
            "timestamp": "0:00 - 0:03",
            "section": "HOOK",
            "visual": f"Creator faces camera with shocked/excited expression. Text overlay: \"{topic.upper()}\" with emoji animation.",
            "audio": f"[Energetic] \"Stop everything — you NEED to hear this about {topic}!\""
        },
        {
            "timestamp": "0:03 - 0:08",
            "section": "CONTEXT",
            "visual": f"Quick cut to B-roll or screen recording related to {topic}. Subtle zoom-in effect. Lower third text: \"Here's the truth...\"",
            "audio": f"[Conversational] \"So here's the deal — most people get {topic} completely wrong. Let me break it down for you.\""
        },
        {
            "timestamp": "0:08 - 0:20",
            "section": "KEY POINT #1",
            "visual": f"Split screen or numbered list graphic. Bold text overlay: \"#1\" with highlight effect. Show relevant imagery for {topic}.",
            "audio": f"[Authoritative] \"First thing — {topic} isn't what you think. The biggest misconception is that it's complicated. It's actually super simple once you understand this one principle.\""
        },
        {
            "timestamp": "0:20 - 0:35",
            "section": "KEY POINT #2",
            "visual": f"Quick transition (swipe/glitch). New angle or demonstration. Text overlay: \"#2 — THIS is the game changer\". Show proof/results related to {topic}.",
            "audio": f"[Building excitement] \"Number two — and this is the one that blew my mind — when you apply {topic} correctly, the results speak for themselves. Look at this...\""
        },
        {
            "timestamp": "0:35 - 0:48",
            "section": "KEY POINT #3 (The Wow Factor)",
            "visual": f"Most dynamic visual moment. Before/after, reaction shot, or dramatic reveal. Animated text: \"🔥 #3 — The Secret 🔥\". Close-up shot for emphasis.",
            "audio": f"[Peak energy] \"But HERE'S the part nobody talks about — the real secret to {topic} is actually hiding in plain sight. Once you see it, you can't unsee it.\""
        },
        {
            "timestamp": "0:48 - 0:55",
            "section": "RECAP / VALUE REINFORCEMENT",
            "visual": f"Quick montage of all 3 points as text overlays. Creator back on camera, confident body language.",
            "audio": f"[Confident wrap-up] \"So remember: {topic} comes down to these three things. Master them and you're ahead of 99% of people.\""
        },
        {
            "timestamp": "0:55 - 1:00",
            "section": "CALL TO ACTION",
            "visual": "Creator points at camera / gestures to follow. Animated subscribe/follow button overlay. End screen with handle.",
            "audio": "[See CTA section below]"
        }
    ]
    return script_sections


def _generate_cta(topic: str, platform: str) -> str:
    """Generate a platform-native call to action."""
    if platform == "tiktok":
        return (
            f"\"Follow for more {topic} tips that actually work! "
            f"Drop a '🔥' in the comments if this helped, and share this with someone who needs to see it! "
            f"Part 2 drops tomorrow — you don't want to miss it.\""
        )
    elif platform == "instagram reels":
        return (
            f"\"Save this reel so you don't lose it! 💾 "
            f"Tag someone who needs to learn about {topic} ASAP. "
            f"Follow @[YOUR_HANDLE] for more content like this, and drop a '💡' in the comments if you learned something new!\""
        )
    elif platform == "youtube shorts":
        return (
            f"\"Smash that subscribe button and hit the bell 🔔 for more {topic} content! "
            f"Leave a comment telling me what topic you want next. "
            f"Like this Short if it helped — it helps more than you know!\""
        )
    return f"\"Follow for more {topic} content!\""


def _generate_seo_data(topic: str, platform: str) -> tuple:
    """Generate hashtags and an optimized caption."""
    topic_tag = re.sub(r'[^\w]', '', topic.title().replace(' ', ''))
    topic_lower_tag = re.sub(r'[^\w]', '', topic.lower().replace(' ', ''))

    base_hashtags = [
        f"#{topic_tag}",
        f"#{topic_lower_tag}tips",
        f"#{topic_lower_tag}101",
        f"#LearnOn{'TikTok' if platform == 'tiktok' else 'Instagram' if platform == 'instagram reels' else 'YouTube'}"
    ]

    if platform == "tiktok":
        platform_hashtags = ["#fyp", "#foryoupage", "#viral", "#tiktoktrending"]
    elif platform == "instagram reels":
        platform_hashtags = ["#reels", "#reelsinstagram", "#explorepage", "#instareels"]
    else:
        platform_hashtags = ["#shorts", "#youtubeshorts", "#trending", "#subscribe"]

    # Combine and limit to 5-8
    all_hashtags = base_hashtags + platform_hashtags
    hashtags = list(dict.fromkeys(all_hashtags))[:8]  # deduplicate, limit to 8

    caption = (
        f"{topic} explained in 60 seconds! 🚀 "
        f"Everything you need to know — watch till the end for the secret most people miss. "
        f"{' '.join(hashtags[:5])}"
    )

    return hashtags, caption


def _format_script(topic, platform, hooks, script_body, cta, hashtags, caption) -> str:
    """Format the complete script as a readable text document."""
    separator = "=" * 70
    sub_separator = "-" * 70
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(separator)
    lines.append(f"  🎬 VIRAL VIDEO SCRIPT — {platform.upper()}")
    lines.append(f"  📌 Topic: {topic}")
    lines.append(f"  ⏱️  Duration: ~60 seconds")
    lines.append(f"  📅 Generated: {timestamp}")
    lines.append(separator)
    lines.append("")

    # --- HOOK VARIATIONS ---
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║                        🪝 HOOK VARIATIONS                           ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")
    for i, hook in enumerate(hooks, 1):
        lines.append(f"  Hook #{i}: {hook}")
        lines.append("")
    lines.append(sub_separator)
    lines.append("")

    # --- SCRIPT BODY ---
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║                    📝 SCRIPT BODY (Visual | Audio)                  ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")

    for section in script_body:
        lines.append(f"  ⏱️  [{section['timestamp']}] — {section['section']}")
        lines.append(f"  {'~' * 60}")
        lines.append(f"  🎥 VISUAL:")
        # Word wrap visual
        visual_lines = _wrap_text(section['visual'], 60)
        for vl in visual_lines:
            lines.append(f"     {vl}")
        lines.append(f"")
        lines.append(f"  🎙️ AUDIO:")
        audio_lines = _wrap_text(section['audio'], 60)
        for al in audio_lines:
            lines.append(f"     {al}")
        lines.append("")
        lines.append(sub_separator)
        lines.append("")

    # --- CALL TO ACTION ---
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║                      📣 CALL TO ACTION (CTA)                       ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")
    cta_lines = _wrap_text(cta, 65)
    for cl in cta_lines:
        lines.append(f"  {cl}")
    lines.append("")
    lines.append(sub_separator)
    lines.append("")

    # --- SEO DATA ---
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║                       🔍 SEO DATA & HASHTAGS                       ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  📌 Hashtags ({len(hashtags)}):")
    lines.append(f"     {' '.join(hashtags)}")
    lines.append("")
    lines.append(f"  ✍️  Optimized Caption:")
    caption_lines = _wrap_text(caption, 65)
    for capl in caption_lines:
        lines.append(f"     {capl}")
    lines.append("")
    lines.append(separator)
    lines.append("")

    # --- PRODUCTION NOTES ---
    lines.append("╔══════════════════════════════════════════════════════════════════════╗")
    lines.append("║                      🎯 PRODUCTION NOTES                           ║")
    lines.append("╚══════════════════════════════════════════════════════════════════════╝")
    lines.append("")
    lines.append("  • Film vertically (9:16 aspect ratio)")
    lines.append("  • Keep text in the safe zone (center 80% of screen)")
    lines.append("  • Use trending audio/sounds when possible")
    lines.append("  • Add captions/subtitles for accessibility")
    lines.append("  • First 3 seconds are CRITICAL — lead with the strongest hook")
    lines.append("  • Post during peak hours for your audience")
    lines.append(f"  • Optimize thumbnail/cover frame for {platform}")
    lines.append("")
    lines.append(separator)
    lines.append(f"  Generated by OpenSpider Script Generator")
    lines.append(separator)

    return "\n".join(lines)


def _wrap_text(text: str, width: int) -> list:
    """Simple word-wrap utility."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= width:
            current_line = f"{current_line} {word}".strip()
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines if lines else [""]
