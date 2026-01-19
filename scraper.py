# scraper.py
# RemoteOK Job Scraper - mentorship/portfolio-ready
# Features:
# - Fetches real jobs from JSON feed
# - Filters by multiple keywords
# - Saves versioned CSV
# - Optional email alerts for new jobs

import requests
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Step 1: Fetch jobs from RemoteOK JSON

def fetch_jobs_json():
    url = "https://remoteok.com/remote-jobs.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        jobs = response.json()
        return jobs
    except requests.exceptions.RequestException as e:
        print("Error fetching JSON feed:", e)
        return []


# Step 2: Parse jobs & filter by keywords

def parse_jobs(jobs, keywords=None):
    if keywords is None:
        keywords = ["Python", "Django", "Flask", "ML", "Machine Learning", "AI"]

    job_list = []

    # Skip first element (metadata)
    for job in jobs[1:]:
        title = job.get("position")
        company = job.get("company", "N/A")
        location = job.get("location", "Remote")
        link = "https://remoteok.com" + job.get("url", "")

        if title:
            # Debug: print job titles being processed
            print("Found job title:", title)

            if any(k.lower() in title.lower() for k in keywords):
                job_list.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "job_link": link
                })

    return job_list

# Step 3: Save jobs to CSV

def save_to_csv(job_list):
    if not job_list:
        print("No jobs found with the specified keywords.")
        return None

    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"jobs_{today}.csv"

    df = pd.DataFrame(job_list)
    df.to_csv(filename, index=False)
    print(f"Saved {len(job_list)} jobs to {filename}")
    return filename


# Step 4: Send email alert 

def send_email_alert(filename, sender_email, sender_password, recipient_email):
    """
    Send an email alert with the CSV file attached or summary of jobs.
    """
    # Read CSV content
    df = pd.read_csv(filename)
    job_summary = df.to_string(index=False)

    # Create email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "New Python Jobs Alert"

    # Body of email
    body = f"Hi,\n\nHere are the latest Python/ML/AI jobs:\n\n{job_summary}\n\nRegards,\nJob Scraper Bot"
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print("Error sending email:", e)

# Step 5: Main function

def main():
    print("Fetching jobs from RemoteOK JSON feed...")
    jobs_json = fetch_jobs_json()
    if not jobs_json:
        print("Failed to fetch jobs.")
        return

    print("Parsing jobs with keywords: Python, Django, Flask, ML, AI...")
    filtered_jobs = parse_jobs(jobs_json)

    csv_file = save_to_csv(filtered_jobs)

    # Optional: send email if you want
    send_email = False  # set True to send email
    if send_email and csv_file:
        # Fill your email credentials
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"
        recipient_email = "recipient_email@gmail.com"
        send_email_alert(csv_file, sender_email, sender_password, recipient_email)

if __name__ == "__main__":
    main()
