import re
from datetime import datetime
from collections import defaultdict

def analyze_reply_time(lines_in_file):
    """Analyzes response times between participants in a WhatsApp chat."""

    message_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2})?-?\s*(.*?):\s(.*)")
    time_format = "%d/%m/%y, %H:%M"  # 24-hour format

    last_message_time = None
    last_sender = None
    reply_times = defaultdict(list)

    for line in lines_in_file:
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        match = message_pattern.match(decoded_line)

        if match:
            date, time, sender, message = match.groups()
            sender = sender.lstrip("- ").strip()

            if message == "<Media omitted>":
                continue  # Ignore media messages

            # Convert to datetime
            timestamp_str = f"{date}, {time}"
            try:
                timestamp = datetime.strptime(timestamp_str, time_format)
            except ValueError:
                continue  # Skip invalid timestamps

            if last_message_time and last_sender and sender != last_sender:
                response_time = (timestamp - last_message_time).total_seconds()  # in seconds - divide by 60 to convert to minutes
                if response_time < 120 * 60:  # Ignore if response is over 2 hours (optional)
                    reply_times[sender].append((last_message_time, response_time)) # Store timestamp and reply time

            last_message_time = timestamp
            last_sender = sender

    # Calculate stats
    reply_stats = {}
    for person, times in reply_times.items():
        if times:
            response_times = [t[1] for t in times] # Extract just the reply times for stats
            reply_stats[person] = {
                "average_reply_time": sum(response_times) / len(response_times),
                "median_reply_time": sorted(response_times)[len(response_times) // 2],
                "fastest_reply": min(response_times),
                "slowest_reply": max(response_times),
                "times": times, # Store the tuples
            }

    return reply_stats

# def analyze_reply_time(lines_in_file):
#     """Analyzes response times between participants in a WhatsApp chat."""
    
#     message_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2})?-?\s*(.*?):\s(.*)")
#     time_format = "%d/%m/%y, %H:%M"  # 24-hour format

#     last_message_time = None
#     last_sender = None
#     reply_times = defaultdict(list)

#     for line in lines_in_file:
#         decoded_line = line.decode('utf-8', errors='ignore').strip()
#         match = message_pattern.match(decoded_line)
        
#         if match:
#             date, time, sender, message = match.groups()
#             sender = sender.lstrip("- ").strip()

#             if message == "<Media omitted>":  
#                 continue  # Ignore media messages
            
#             # Convert to datetime
#             timestamp_str = f"{date}, {time}"
#             try:
#                 timestamp = datetime.strptime(timestamp_str, time_format)
#             except ValueError:
#                 continue  # Skip invalid timestamps
            
#             if last_message_time and last_sender and sender != last_sender:
#                 response_time = (timestamp - last_message_time).total_seconds()  # in seconds - divide by 60 to convert to minutes
#                 if response_time < 120*60:  # Ignore if response is over 2 hours (optional)
#                     reply_times[sender].append(response_time)

#             last_message_time = timestamp
#             last_sender = sender

#     # Calculate stats
#     reply_stats = {}
#     for person, times in reply_times.items():
#         if times:
#             reply_stats[person] = {
#                 "average_reply_time": sum(times) / len(times),
#                 "median_reply_time": sorted(times)[len(times) // 2],
#                 "fastest_reply": min(times),
#                 "slowest_reply": max(times),
#                 "times": times,
#             }

#     return reply_stats


def analyze_whatsapp(lines_in_file):
    """Analyzes WhatsApp chat text data and extracts useful insights."""
    
    total_messages = len(lines_in_file)
    participants = set()
    messages_per_person = defaultdict(int)
    first_timestamp, last_timestamp = None, None

    # Regex to match a WhatsApp message (Handles both 12h & 24h formats)
    message_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2} (?:AM|PM)?)?-?\s*(.*?):\s(.*)")

    # Regex to detect URLs
    url_pattern = re.compile(r"https?://\S+")

    longest_message = {"participant": None, "message": "", "length": 0}

    for line in lines_in_file:
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        match = message_pattern.match(decoded_line)
        
        if match:
            date, time, sender, message = match.groups()
            participants.add(sender)
            messages_per_person[sender] += 1

            # Skip messages that are just links
            if not url_pattern.fullmatch(message):  
                message_length = len(message)
                if message_length > longest_message["length"]:
                    longest_message = {"participant": sender, "message": message, "length": message_length}

            # Set first & last timestamps
            if first_timestamp is None:
                first_timestamp = f"{date} {time}" if time else date
            last_timestamp = f"{date} {time}" if time else date

    # Identify the most active participant
    most_active_participant = max(messages_per_person, key=messages_per_person.get, default=None)
      
    # Get top 3 frequent chatters
    top_3_frequent_chatters = sorted(messages_per_person.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_frequent_chatters = {chatter: count for chatter, count in top_3_frequent_chatters}

    return {
        "total_messages": total_messages,
        "participants": list(participants),
        "messages_per_person": dict(messages_per_person),
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "most_active_participant": most_active_participant,
        "longest_message": longest_message if longest_message["length"] > 0 else None,
        "reply_time": analyze_reply_time(lines_in_file),
        "top_3_frequent_chatters": top_3_frequent_chatters,
    }
