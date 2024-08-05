import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Set up the Firefox options
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # Update this with your actual path to Firefox
options.headless = False  # Set to True if you want to run headless
service = Service(r'C:\Windows\System\geckodriver.exe')  # Update this with your actual path to geckodriver

# Start the WebDriver
driver = webdriver.Firefox(service=service, options=options)

# Open Microsoft Teams
driver.get('https://teams.microsoft.com')

# Wait for the user to log in manually
time.sleep(60)

# Set the log file path
log_file_path = 'chat_log.txt'

# Function to save messages to a log file
def save_messages_to_log(messages):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        for msg in messages:
            log_file.write(f"Author: {msg['author']}, Timestamp: {msg['timestamp']}, Content: {msg['content']}\n")

# Function to extract chat messages
def extract_chat_messages():
    messages = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='message-wrapper']")
    chat_data = []

    for message in messages:
        try:
            author = message.find_element(By.CSS_SELECTOR, "div[data-tid='message-author-name']").text
            timestamp = message.find_element(By.CSS_SELECTOR, "time").get_attribute('datetime')
            content = message.find_element(By.CSS_SELECTOR, "div[id^='content']").text
            chat_data.append({
                'author': author,
                'timestamp': timestamp,
                'content': content
            })
        except Exception as e:
            print(f"Error: {e}")

    return chat_data

# Function to keep track of seen messages
def get_seen_message_ids():
    if not os.path.exists(log_file_path):
        return set()
    
    with open(log_file_path, 'r', encoding='utf-8') as log_file:
        lines = log_file.readlines()
    
    seen_ids = set()
    for line in lines:
        parts = line.split(', ')
        if len(parts) > 1 and 'Timestamp' in parts[1]:
            try:
                timestamp = parts[1].split(': ')[1].strip()
                seen_ids.add(timestamp)
            except IndexError:
                continue  # Skip lines that do not have the expected format
    
    return seen_ids

# Main loop to check for new messages and save them to the log file
seen_message_ids = get_seen_message_ids()

while True:
    new_messages = extract_chat_messages()
    new_messages_to_log = []
    
    for msg in new_messages:
        if msg['timestamp'] not in seen_message_ids:
            new_messages_to_log.append(msg)
            seen_message_ids.add(msg['timestamp'])
    
    if new_messages_to_log:
        save_messages_to_log(new_messages_to_log)
        print(f"Saved {len(new_messages_to_log)} new messages to log.")
    
    # Wait before checking for new messages again
    time.sleep(10)
