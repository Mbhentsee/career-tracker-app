import streamlit as st
import pandas as pd

st.set_page_config(page_title="Career Tracker", layout="wide")

st.header("📝 Add New Application")

with st.form(key='application_form'):
    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Job Title")
        company = st.text_input("Company")
        application_date = st.date_input("Application Date")
    
    with col2:
        status = st.selectbox("Application Status", ["Applied", "Interview", "Offer", "Rejected", "No Response"])
        job_link = st.text_input("Job Link (optional)")
        location = st.text_input("Location (City, Country)")

    notes = st.text_area("Additional Notes")

    submitted = st.form_submit_button("➕ Add Application")

    if submitted:
        new_entry = {
            "Job Title": job_title,
            "Company": company,
            "Application Date": application_date.strftime("%Y-%m-%d"),
            "Status": status,
            "Job Link": job_link,
            "Location": location,
            "Notes": notes
        }

        # Load or create CSV file
        df_path = "data/applications.csv"
        try:
            df = pd.read_csv(df_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=new_entry.keys())

        # Append new entry
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(df_path, index=False)
        st.success("✅ Application added successfully!")


# Placeholder sections
st.header("📝 Add New Application")
st.text("Form goes here...")

st.header("📋 View Applications")
st.text("Data table goes here...")

st.header("📈 Insights")
st.text("Charts go here...")


