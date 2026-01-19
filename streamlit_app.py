# final_streamlit_app.py
# Polished RemoteOK Job Scraper with Streamlit
# Features:
# - Interactive keyword input
# - Table numbered from 1
# - CSV download
# - Email alert option
# - Graphs: jobs per company & location
# - Latest jobs on top
# - Fix: missing locations default to "Remote"

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt

# -------------------------
# Fetch jobs from RemoteOK JSON
# -------------------------
@st.cache_data
def fetch_jobs_json():
    url = "https://remoteok.com/remote-jobs.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        jobs = response.json()
        return jobs
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching jobs: {e}")
        return []

# -------------------------
# Parse & filter jobs
# -------------------------
def parse_jobs(jobs, keywords):
    job_list = []
    for job in jobs[1:]:  # skip metadata
        title = job.get("position")
        company = job.get("company") or "N/A"
        location = job.get("location") or "Remote"  # FIX: replace None with "Remote"
        link = "https://remoteok.com" + job.get("url", "")

        if title and any(k.lower() in title.lower() for k in keywords):
            job_list.append({
                "title": title,
                "company": company,
                "location": location,
                "job_link": link
            })
    # Latest jobs on top
    return job_list[::-1]

# -------------------------
# Email alert function
# -------------------------
def send_email_alert(df, sender_email, sender_password, recipient_email):
    job_summary = df.to_string(index=False)
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "New Python Jobs Alert"
    body = f"Hi,\n\nHere are the latest jobs:\n\n{job_summary}\n\nRegards,\nJob Scraper Bot"
    message.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        st.success(f"Email sent to {recipient_email}")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="RemoteOK Job Scraper", layout="wide")
st.title("💼 RemoteOK Job Scraper")
st.write("Scrape Python, Django, Flask, ML, AI remote jobs from RemoteOK!")

# Keyword input
keywords_input = st.text_input("Enter keywords (comma-separated):", "Python,Django,Flask,ML,AI")
keywords = [k.strip() for k in keywords_input.split(",")]

# Button to fetch jobs
if st.button("Fetch Jobs"):
    st.info("Fetching jobs...")
    jobs_json = fetch_jobs_json()
    if jobs_json:
        filtered_jobs = parse_jobs(jobs_json, keywords)
        if filtered_jobs:
            df = pd.DataFrame(filtered_jobs)

            # Add numbering starting from 1
            df.index = df.index + 1
            df.index.name = "No."

            st.success(f"Found {len(df)} jobs!")
            st.dataframe(df)

            # CSV download
            csv_file_name = f"jobs_{datetime.today().strftime('%Y-%m-%d')}.csv"
            csv = df.to_csv(index=True).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv, file_name=csv_file_name, mime="text/csv")

            # Optional email alert
            send_email = st.checkbox("Send Email Alert")
            if send_email:
                st.subheader("Email Settings")
                sender_email = st.text_input("Sender Email")
                sender_password = st.text_input("App Password", type="password")
                recipient_email = st.text_input("Recipient Email")
                if st.button("Send Email"):
                    send_email_alert(df, sender_email, sender_password, recipient_email)

            # -------------------------
            # Graphs
            # -------------------------
            st.subheader("📊 Jobs by Company")
            company_counts = df['company'].value_counts().head(10)
            fig1, ax1 = plt.subplots()
            company_counts.plot(kind='barh', ax=ax1, color='skyblue')
            ax1.invert_yaxis()
            ax1.set_xlabel("Number of Jobs")
            ax1.set_ylabel("Company")
            st.pyplot(fig1)

            st.subheader("📊 Jobs by Location")
            location_counts = df['location'].value_counts().head(10)
            fig2, ax2 = plt.subplots()
            location_counts.plot(kind='barh', ax=ax2, color='salmon')
            ax2.invert_yaxis()
            ax2.set_xlabel("Number of Jobs")
            ax2.set_ylabel("Location")
            st.pyplot(fig2)

        else:
            st.warning("No jobs found with the specified keywords.")
    else:
        st.error("Failed to fetch jobs.")
