import os
import json
import re


def execute(args: dict) -> dict:
    try:
        topic = args.get("topic", "")
        platform = args.get("platform", "TikTok")

        if not topic:
            return {"success": False, "error": "A topic is required."}

        platform = platform.strip()
        valid_platforms = ["tiktok", "instagram reels", "youtube shorts"]
        if platform.lower() not in valid_platforms:
            return {
                "success": False,
                "error": f"Invalid platform '{platform}'. Choose from: TikTok, Instagram Reels, or YouTube Shorts."
            }

        # Platform-specific CTAs and hashtag styles
        platform_lower = platform.lower()
        if platform_lower == "tiktok":
            cta = "Save this for later and follow for more! Drop a comment if you want Part 2! 👇"
            platform_hashtag = "#TikTok #ForYouPage #FYP"
        elif platform_lower == "instagram reels":
            cta = "Save this reel and share it with someone who needs to see this! Link in bio for more 🔗"
            platform_hashtag = "#Reels #InstagramReels #Explore"
        else:  # youtube shorts
            cta = "Subscribe and hit the bell so you never miss a short! Like this video if it helped you! 🔔"
            platform_hashtag = "#Shorts #YouTubeShorts #Subscribe"

        # Generate hashtags
        topic_words = re.sub(r'[^\w\s]', '', topic).split()
        topic_tag = "".join(w.capitalize() for w in topic_words)
        hashtags = [
            f"#{topic_tag}",
            f"#{topic_words[0].capitalize()}Tips" if topic_words else "#Tips",
            "#LearnOn" + platform.replace(" ", ""),
            "#Viral",
            "#MustWatch",
        ]
        hashtags_str = " ".join(hashtags) + " " + platform_hashtag

        caption = f"You NEED to know this about {topic}. Watch till the end! 🔥"

        # Build the script
        script = f"""{'='*70}
SOCIAL MEDIA VIDEO SCRIPT
{'='*70}
Topic    : {topic}
Platform : {platform}
Duration : ~60 seconds
{'='*70}

{'─'*70}
SECTION 1: HOOK VARIATIONS (Pick one to open the video)
{'─'*70}

HOOK #1 — Curiosity Gap:
"Most people have NO idea about this {topic} secret… and it's costing
them big time."

HOOK #2 — Controversial Statement:
"Everything you've been told about {topic} is WRONG. Here's the truth
nobody wants you to know."

HOOK #3 — Relatable Problem:
"If you've ever struggled with {topic}, stop scrolling — this is
going to change everything for you."

{'─'*70}
SECTION 2: MAIN SCRIPT (Two-Column Format)
{'─'*70}

Timestamp | VISUAL                                  | AUDIO (Voiceover / Dialogue)
----------|------------------------------------------|---------------------------------------------
0:00-0:03 | Close-up of presenter's face, fast zoom  | [Deliver chosen HOOK — see above]
          | in. Text overlay: "WAIT FOR IT…"         |
          | SFX: Dramatic whoosh sound               |
----------|------------------------------------------|---------------------------------------------
0:03-0:10 | Cut to B-roll relevant to {topic}.       | "Here's the thing — {topic} is something
          | Kinetic text overlay highlighting key     |  most people completely overlook. But once
          | words. Camera: slow push-in.             |  you understand this, you'll never look at
          |                                          |  it the same way again."
----------|------------------------------------------|---------------------------------------------
0:10-0:20 | Split screen: LEFT shows the common      | "See, most people do it like THIS —"
          | mistake / wrong approach. RIGHT shows    |  [gesture left] "— but what you SHOULD be
          | the correct approach. Animated arrows    |  doing is THIS." [gesture right]
          | and circles drawing viewer attention.    |  "And here's exactly why…"
          | SFX: Error buzzer (left), Ding (right)  |
----------|------------------------------------------|---------------------------------------------
0:20-0:35 | Presenter on camera with energetic       | "Step one: [Key insight #1 about {topic}].
          | delivery. Text overlay bullets appear    |  This alone will put you ahead of 90% of
          | one-by-one as each point is made.        |  people. Step two: [Key insight #2 about
          | B-roll intercuts every 3-4 seconds to    |  {topic}]. This is the part nobody talks
          | maintain visual pace.                    |  about. And step three: [Key insight #3
          | SFX: Subtle pop sound on each bullet.   |  about {topic}]. This is the game-changer."
----------|------------------------------------------|---------------------------------------------
0:35-0:48 | Quick montage of results / proof /       | "When you put all three together, the
          | transformation related to {topic}.       |  results speak for themselves. People who
          | Before-and-after style if applicable.    |  figured this out are already seeing
          | Dynamic transitions (swipe, glitch).     |  massive results with {topic}."
          | Upbeat background music builds.          |
----------|------------------------------------------|---------------------------------------------
0:48-0:55 | Presenter back on camera, leaning in     | "But here's the part that's going to blow
          | for emphasis. Text overlay:              |  your mind — there's actually a bonus tip
          | "BONUS TIP 🤯"                           |  that ties everything together. [Deliver
          | SFX: Mind-blown sound effect             |  bonus insight about {topic}]."
----------|------------------------------------------|---------------------------------------------
0:55-1:00 | Presenter points at camera. CTA text     | "{cta}"
          | overlay appears with animation.           |
          | End screen / logo.                       |
          | SFX: Notification bell sound             |

{'─'*70}
SECTION 3: CALL TO ACTION
{'─'*70}

{cta}

{'─'*70}
SECTION 4: SEO DATA
{'─'*70}

Hashtags:
{hashtags_str}

Optimized Caption:
{caption}

{'='*70}
PRODUCTION NOTES:
- Keep energy HIGH throughout. Pace should feel urgent.
- Use jump cuts every 2-4 seconds to maintain attention.
- Background music: Trending audio on {platform} if possible.
- Text overlays should be large, bold, and centered for mobile viewing.
- Film vertically (9:16 aspect ratio).
{'='*70}
"""

        # Create a safe filename from the topic
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
        safe_topic = re.sub(r'[\s]+', '_', safe_topic)
        filename = f"{safe_topic}_video_script.txt"

        # Determine save directory (user's home directory / Documents if available)
        home_dir = os.path.expanduser("~")
        documents_dir = os.path.join(home_dir, "Documents")
        if os.path.isdir(documents_dir):
            save_dir = documents_dir
        else:
            save_dir = home_dir

        filepath = os.path.join(save_dir, filename)

        # Write the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(script)

        return {
            "success": True,
            "message": f"Video script for '{topic}' on {platform} has been successfully generated and saved.",
            "file_path": filepath,
            "summary": {
                "topic": topic,
                "platform": platform,
                "hooks_provided": 3,
                "script_duration": "~60 seconds",
                "hashtags": hashtags_str,
                "caption": caption,
                "cta": cta
            }
        }

    except PermissionError as e:
        return {"success": False, "error": f"Permission denied when writing file: {str(e)}"}
    except OSError as e:
        return {"success": False, "error": f"OS error occurred: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}