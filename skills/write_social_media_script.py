import json
import os


def execute(args: dict) -> dict:
 try:
 topic = args.get("topic", "general topic")
 platform = args.get("platform", "TikTok")
 output_file = args.get("output_file", "script_output.txt")

 # Normalize platform
 platform = platform.strip()
 if platform.lower() not in ["tiktok", "reels", "shorts"]:
 platform = "TikTok"

 # Generate 3 hook variations
 hooks = [
 f"Hook 1 (Question): \"Did you know this about {topic}? Most people have no idea...\"",
 f"Hook 2 (Bold Statement): \"Stop scrolling — this {topic} hack will change everything.\"",
 f"Hook 3 (Curiosity Gap): \"I tried {topic} for 30 days and here's what happened…\""
 ]

 # Two-column A/V script sections
 script_sections = [
 {
 "section": "INTRO (0-3s)",
 "visual": f"Close-up of creator looking surprised / shocked face. Text overlay: \"{topic.upper()}\" with emoji.",
 "audio": f"\"You NEED to know this about {topic}…\" (energetic, fast-paced tone)"
 },
 {
 "section": "PROBLEM / CONTEXT (3-8s)",
 "visual": f"B-roll or screen recording related to {topic}. Quick cuts, zoom-ins for emphasis.",
 "audio": f"\"Most people get {topic} completely wrong. Here's what's actually going on…\""
 },
 {
 "section": "MAIN CONTENT / VALUE (8-20s)",
 "visual": f"Step-by-step demonstration or talking head with text overlays highlighting key points about {topic}. Use arrows, highlights, or annotations.",
 "audio": f"\"First, [key point 1 about {topic}]. Second, [key point 2]. And the most important thing — [key point 3].\""
 },
 {
 "section": "RESULTS / PROOF (20-25s)",
 "visual": f"Before/after comparison, screenshots, or data visuals related to {topic}.",
 "audio": f"\"And look at the difference — this is what happens when you actually understand {topic}.\""
 },
 {
 "section": "CTA / OUTRO (25-30s)",
 "visual": f"Creator pointing at camera. On-screen text: \"Follow for more {topic} tips!\" with subscribe/follow animation.",
 "audio": f"\"Follow for more {topic} tips, and drop a comment if you want part 2!\""
 }
 ]

 # Generate SEO hashtags (5-8)
 topic_slug = topic.lower().replace(" ", "")
 topic_slug_camel = topic.title().replace(" ", "")
 seo_tags = [
 f"#{topic_slug}",
 f"#{topic_slug_camel}Tips",
 f"#{platform.lower()}",
 f"#viral",
 f"#{topic_slug}hack",
 f"#learnon{platform.lower()}",
 f"#{topic_slug}101",
 f"#contentcreator"
 ]

 # Build the formatted script string
 lines = []
 lines.append("=" * 60)
 lines.append(f"  SOCIAL MEDIA VIDEO SCRIPT")
 lines.append(f"  Platform: {platform}")
 lines.append(f"  Topic: {topic}")
 lines.append("=" * 60)
 lines.append("")

 # Hooks section
 lines.append("-" * 40)
 lines.append("HOOK VARIATIONS")
 lines.append("-" * 40)
 for hook in hooks:
 lines.append(f"  {hook}")
 lines.append("")

 # A/V Script section
 lines.append("-" * 40)
 lines.append("A/V SCRIPT (Two-Column Format)")
 lines.append("-" * 40)
 for section in script_sections:
 lines.append(f"")
 lines.append(f"[{section['section']}]")
 lines.append(f"  Visual: {section['visual']}")
 lines.append(f"  Audio:  {section['audio']}")
 lines.append("")

 # CTA section
 lines.append("-" * 40)
 lines.append("CALL TO ACTION")
 lines.append("-" * 40)
 lines.append(f"  1. \"Follow for more {topic} content!\"")
 lines.append(f"  2. \"Comment '{topic.upper()}' to get the full guide!\"")
 lines.append(f"  3. \"Share this with someone who needs to hear this!\"")
 lines.append("")

 # SEO Tags section
 lines.append("-" * 40)
 lines.append("SEO HASHTAGS")
 lines.append("-" * 40)
 lines.append(f"  {' '.join(seo_tags)}")
 lines.append("")
 lines.append("=" * 60)
 lines.append("END OF SCRIPT")
 lines.append("=" * 60)

 script_content = "\n".join(lines)

 # Write to file
 filepath = os.path.abspath(output_file)
 with open(filepath, "w", encoding="utf-8") as f:
 f.write(script_content)

 return {
 "success": True,
 "filepath": filepath
 }

 except Exception as e:
 return {
 "success": False,
 "error": str(e)
 }
