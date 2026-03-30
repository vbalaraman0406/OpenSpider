import json
import datetime
from bs4 import BeautifulSoup

def run_script():
    url = "https://factbase.app/t/donald-trump/truth-social"
    
    # 1. Navigate to the URL and read content
    print(f"Navigating to {url}")
    response = browse_web(command="navigate", url=url)
    if response['success']:
        print("Successfully navigated. Reading content...")
        content_response = browse_web(command="read_content")
        if content_response['success']:
            html_content = content_response['content']
            print("Content read. Parsing...")
        else:
            print(f"Failed to read content: {content_response.get('error', 'Unknown error')}")
            return {"status": "error", "message": f"Failed to read content: {content_response.get('error', 'Unknown error')}"}
    else:
        print(f"Failed to navigate: {response.get('error', 'Unknown error')}")
        return {"status": "error", "message": f"Failed to navigate: {response.get('error', 'Unknown error')}"}

    soup = BeautifulSoup(html_content, 'html.parser')
    posts = []

    # 2. Parse the webpage content to extract posts
    post_elements = soup.find_all('div', class_='post-item') 

    for post_element in post_elements:
        timestamp_str = post_element.find('span', class_='post-timestamp').text.strip() if post_element.find('span', class_='post-timestamp') else 'N/A'
        
        content_div = post_element.find('div', class_='post-content')
        full_content = content_div.get_text(separator=' ', strip=True) if content_div else 'No content found'
        
        topic_summary = full_content.split('.')[0] if '.' in full_content else ' '.join(full_content.split(' ')[0:10]) + '...'

        posts.append({
            'timestamp_str': timestamp_str,
            'topic_summary': topic_summary,
            'full_content': full_content,
            'element': post_element # Keep element to extract datetime later
        })

    # 3. Calculate the time 30 minutes prior to the current system time
    # Current system time: Friday, March 27, 2026 at 09:57 AM PDT.
    # PDT is UTC-7. So 09:57 AM PDT is 16:57 UTC.
    current_time_utc = datetime.datetime(2026, 3, 27, 16, 57, 0, tzinfo=datetime.timezone.utc)
    time_30_minutes_ago_utc = current_time_utc - datetime.timedelta(minutes=30)

    new_posts = []
    # 4. Filter the extracted posts
    for post in posts:
        post_element = post['element']
        time_tag = post_element.find('time')
        if time_tag and 'datetime' in time_tag.attrs:
            post_datetime_str = time_tag['datetime'] # e.g., '2026-03-27T09:50:00-07:00'
            try:
                # Parse the ISO format string with timezone information
                post_time = datetime.datetime.fromisoformat(post_datetime_str).astimezone(datetime.timezone.utc)
                if post_time > time_30_minutes_ago_utc:
                    new_posts.append(post)
            except ValueError as e:
                print(f"Error parsing ISO timestamp '{post_datetime_str}': {e}. Skipping post for time filter.")
                continue
        else:
            print(f"Warning: Could not find ISO datetime for post: {post['timestamp_str']}. Skipping for time filter.")
            continue

    # 5. If one or more new posts are found
    if new_posts:
        whatsapp_message_parts = ["New Truth Social Posts from Donald Trump:"]
        for post in new_posts:
            whatsapp_message_parts.append(f"\n---\nTimestamp: {post['timestamp_str']}\nTopic: {post['topic_summary']}\nContent: {post['full_content']}")
        
        whatsapp_message = "\n".join(whatsapp_message_parts)
        
        recipients = [
            "14156249639@s.whatsapp.net",
            "16507965072@s.whatsapp.net",
            "120363423852747118@g.us" # Stock Market Discussions group
        ]
        
        print(f"Found {len(new_posts)} new posts. Sending WhatsApp message to {', '.join(recipients)}...")
        send_results = []
        for recipient in recipients:
            send_response = send_whatsapp(to=recipient, message=whatsapp_message)
            send_results.append({"recipient": recipient, "status": send_response['status'], "message": send_response.get('message', '')})
        
        return {"status": "success", "message": "WhatsApp messages sent.", "sent_to": recipients, "send_results": send_results}
    else:
        print("No new posts found within the last 30 minutes.")
        return {"status": "success", "message": "No new posts found."}
