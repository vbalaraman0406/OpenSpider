import os
import json
import re


def execute(args: dict) -> dict:
    try:
        topic = args.get("topic", "").strip()
        platform = args.get("platform", "TikTok").strip()

        if not topic:
            return {"success": False, "error": "A topic is required."}

        valid_platforms = ["tiktok", "instagram reels", "youtube shorts"]
        if platform.lower() not in valid_platforms:
            return {
                "success": False,
                "error": f"Invalid platform '{platform}'. Choose from: TikTok, Instagram Reels, YouTube Shorts."
            }

        # Platform-specific CTA suggestions
        cta_map = {
            "tiktok": "Follow for more and save this for later! Drop a comment if you agree 👇",
            "instagram reels": "Save this reel for later 🔖, share it with a friend, and follow for more! Link in bio for details.",
            "youtube shorts": "Subscribe and hit the bell 🔔 so you never miss a short! Like this video if it helped you."
        }

        cta = cta_map[platform.lower()]

        # Generate the script content
        script_content = generate_script(topic, platform, cta)

        # Create a safe filename from the topic
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
        safe_topic = re.sub(r'[\s]+', '_', safe_topic)
        filename = f"{safe_topic}_script.txt"

        # Determine save path (user's home directory / Documents if available, else current dir)
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.isdir(documents_path):
            save_dir = documents_path
        else:
            save_dir = os.getcwd()

        filepath = os.path.join(save_dir, filename)

        # Write the script to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(script_content)

        return {
            "success": True,
            "message": f"Script for '{topic}' on {platform} has been successfully generated and saved.",
            "file_path": filepath,
            "script_preview": script_content[:500] + "..." if len(script_content) > 500 else script_content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_script(topic: str, platform: str, cta: str) -> str:
    # Generate hashtags based on topic
    topic_words = topic.lower().split()
    base_hashtags = [f"#{word}" for word in topic_words if len(word) > 2]
    platform_hashtags_map = {
        "tiktok": ["#fyp", "#foryoupage", "#viral", "#tiktok"],
        "instagram reels": ["#reels", "#reelsinstagram", "#explorepage", "#trending"],
        "youtube shorts": ["#shorts", "#youtubeshorts", "#viral", "#trending"]
    }
    platform_tags = platform_hashtags_map.get(platform.lower(), ["#viral", "#trending"])
    
    combined_topic_tag = "#" + "".join([w.capitalize() for w in topic_words])
    all_hashtags = list(dict.fromkeys([combined_topic_tag] + base_hashtags + platform_tags))
    hashtags = all_hashtags[:8]
    hashtags_str = " ".join(hashtags)

    # Build the formatted script
    script = f"""
================================================================================
        🎬 60-SECOND VIDEO SCRIPT — {platform.upper()}
================================================================================
📌 TOPIC: {topic}
📱 PLATFORM: {platform}
================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪝 SECTION 1: HOOK VARIATIONS (Choose one — first 3 seconds are CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔥 HOOK 1 — Curiosity Gap:
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ "Nobody talks about this one thing about {topic}... and it changes     │
  │ everything."                                                           │
  │                                                                        │
  │ [VISUAL: Extreme close-up of face, eyes wide. Quick zoom-in effect.    │
  │  Bold text overlay: "WAIT FOR IT..." with suspenseful sound effect]    │
  └──────────────────────────────────────────────────────────────────────────┘

  💥 HOOK 2 — Controversial / Bold Statement:
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ "Everything you've been told about {topic} is WRONG. Here's the truth."│
  │                                                                        │
  │ [VISUAL: Creator staring at camera, shaking head. Red X graphic pops   │
  │  on screen. Dramatic bass drop sound effect]                           │
  └──────────────────────────────────────────────────────────────────────────┘

  😩 HOOK 3 — Relatable Problem:
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ "If you've ever struggled with {topic}, this is literally the video    │
  │ you've been waiting for."                                              │
  │                                                                        │
  │ [VISUAL: POV-style shot showing frustration. Quick montage of common   │
  │  pain points. Text overlay: "THIS IS FOR YOU 👇" with whoosh SFX]     │
  └──────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 SECTION 2: MAIN SCRIPT BODY (Two-Column Format)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────┬────────────────────────────────────────┐
│          📹 VISUAL                  │           🎙️ AUDIO / VOICEOVER        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:00–0:03 — THE HOOK             │                                        │
│                                     │                                        │
│ - Camera: Tight close-up on face    │ [Chosen hook from above]               │
│ - Text overlay: Teaser text in      │                                        │
│   bold, large font                  │ Speak fast, high energy, lean into     │
│ - SFX: Attention-grabbing sound     │ the camera.                            │
│   (notification ding, bass drop)    │                                        │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:03–0:12 — THE CONTEXT          │                                        │
│                                     │                                        │
│ - Camera: Medium shot, casual       │ "So here's the deal with {topic}.      │
│   setting (desk, kitchen, outdoors) │ Most people approach it completely      │
│ - B-roll: Quick cuts of relevant    │ the wrong way. They think it's about   │
│   imagery related to {topic}        │ [common misconception], but it's       │
│ - Text overlay: Key stat or fact    │ actually about [real insight]. Let me   │
│   in contrasting color              │ break it down for you in under a       │
│ - Subtle background music starts    │ minute."                               │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:12–0:30 — THE VALUE (Core)     │                                        │
│                                     │                                        │
│ - Camera: Switch between close-up   │ "Step one — [First key point about     │
│   and medium shot for dynamism      │ {topic}]. This is the foundation       │
│ - On-screen: Numbered list          │ most people skip.                      │
│   appearing one by one (1, 2, 3)    │                                        │
│ - B-roll: Relevant demonstration    │ Step two — [Second key point about     │
│   or example footage                │ {topic}]. This is where the magic      │
│ - SFX: Subtle 'pop' sound as each   │ happens. Pay attention here.           │
│   point appears                     │                                        │
│ - Text overlays highlighting key    │ Step three — [Third key point about    │
│   words from the dialogue           │ {topic}]. And THIS is the one nobody   │
│                                     │ talks about."                          │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:30–0:45 — THE PROOF/STORY      │                                        │
│                                     │                                        │
│ - Camera: Close-up, more intimate   │ "I personally discovered this when     │
│   and personal feel                 │ [brief personal anecdote or case       │
│ - B-roll: Before/after visuals,     │ study related to {topic}]. The         │
│   results screenshots, or           │ results were insane — [describe        │
│   testimonial-style footage         │ specific outcome]. And I'm not the     │
│ - Text overlay: "Real results" or   │ only one. Thousands of people are      │
│   "Before → After"                  │ already doing this."                   │
│ - SFX: Success/achievement sound    │                                        │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:45–0:55 — THE PAYOFF           │                                        │
│                                     │                                        │
│ - Camera: Pull back to medium shot, │ "So if you're serious about {topic},   │
│   confident posture                 │ stop overthinking it and start with    │
│ - On-screen: Summary graphic with   │ these three steps today. Literally     │
│   all 3 points listed               │ today. Not tomorrow, not next week.    │
│ - B-roll: Aspirational/success      │ The difference between people who      │
│   imagery                           │ succeed and those who don't? Action."  │
│ - Music builds to crescendo         │                                        │
│                                     │                                        │
├─────────────────────────────────────┼────────────────────────────────────────┤
│                                     │                                        │
│ ⏱️ 0:55–1:00 — CTA                  │                                        │
│                                     │                                        │
│ - Camera: Close-up, direct eye      │ "{cta}"                                │
│   contact with lens                 │                                        │
│ - Text overlay: CTA text animated   │ [Speak with conviction and warmth.     │
│   in with arrow pointing to         │  Smile at the end.]                    │
│   follow/save button                │                                        │
│ - SFX: Notification/click sound     │                                        │
│ - End screen with logo/handle       │                                        │
│                                     │                                        │
└─────────────────────────────────────┴────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📣 SECTION 3: CALL TO ACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Platform: {platform}
  CTA: {cta}

  💡 Pro Tips:
  - Deliver the CTA while the value is still fresh in the viewer's mind
  - Use a native gesture (point at save button, tap screen) to reinforce
  - Keep energy HIGH through the final second — don't trail off

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SECTION 4: SEO & OPTIMIZATION DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📝 Optimized Caption:
  "This changes EVERYTHING about {topic} 🤯 Most people get this wrong —
  here are the 3 steps that actually work. Save this before it gets buried!
  👇 Drop a 🔥 if you needed this."

  # Hashtags:
  {hashtags_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PRODUCTION NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📱 Aspect Ratio: 9:16 (vertical)
  ⏱️ Total Duration: 60 seconds max
  🎵 Music: Trending audio on {platform} (upbeat, motivational)
  ✂️ Editing Style: Fast cuts every 2-3 seconds to maintain attention
  🗣️ Speaking Pace: ~160-180 words per minute (energetic but clear)
  📝 Subtitles: Add burned-in captions — 80%+ of viewers watch on mute
  🎨 Color Grading: Warm, high contrast for maximum thumb-stopping power

================================================================================
              Generated by Social Media Script Tool | {platform}
================================================================================
"""
    return script.strip()
