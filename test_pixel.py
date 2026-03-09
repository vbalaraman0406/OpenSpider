# test_pixel.py

import json

# This simulates what Ananta (Manager) does when delegating to Pixel (Canva Expert)
print("🧠 [Ananta] Delegating task to Pixel (Canva Expert)...")
print("   Task: Create a social media graphic with the quote 'Always aim high'")

from skills.canva_list_templates import list_templates
from skills.canva_generate_image import generate_image

print("\n🎨 [Pixel] Received task! Let's see what templates are available...")
templates_json = json.loads(list_templates())
print("   Templates found!")

# Assume Pixel picks the Instagram post template
chosen_template_id = "temp_InstagramPost_1"

print(f"\n🎨 [Pixel] Generating image using template: {chosen_template_id}...")

text_vars = {
    "quote_text": "Always aim high", 
    "author_name": "OpenSpider"
}
image_vars = {
    "background_image": "https://example.com/mountain.jpg"
}

result_json = generate_image(chosen_template_id, text_vars, image_vars)

print("\n✅ [Pixel] Finished task. Handing result back to Ananta.")
print(result_json)
