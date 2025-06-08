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

st.header("📋 All Applications")

# 🔽 Paste filter block here
try:
    df = pd.read_csv("data/applications.csv")
    df['Application Date'] = pd.to_datetime(df['Application Date'])

    # Filter: Status
    statuses = df['Status'].unique().tolist()
    selected_status = st.multiselect("Filter by Status", options=statuses, default=statuses)

    # Filter: Date Range
    min_date = df['Application Date'].min().date()
    max_date = df['Application Date'].max().date()
    date_range = st.date_input("Filter by Date Range", value=(min_date, max_date))

    # Apply filters
    filtered_df = df[
        (df['Status'].isin(selected_status)) &
        (df['Application Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
    ]

    st.success(f"🎯 Showing {len(filtered_df)} filtered application(s)")
    st.dataframe(filtered_df, use_container_width=True)

except FileNotFoundError:
    st.warning("⚠️ No application data available yet.")


df_path = "data/applications.csv"

import os

csv_path = "data/applications.csv"

# Step 1: Ensure the folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Step 2: Load data safely
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    # Create empty DataFrame with correct structure
    df = pd.DataFrame(columns=["Company Name", "Position", "Application Date", "Status", "Notes"])

# Step 3: Convert date column (only if not empty)
if not df.empty:
    df['Application Date'] = pd.to_datetime(df['Application Date'], errors='coerce')

    st.dataframe(df, use_container_width=True)

st.warning("⚠️ No applications yet. Add some using the form above.")


st.header("📊 Application Insights")

try:
    df = pd.read_csv("data/applications.csv")

    # Format date column
    df['Application Date'] = pd.to_datetime(df['Application Date'])

    st.subheader("1. Applications by Status")
    status_counts = filtered_df['Status'].value_counts()
    status_counts.columns = ['Status', 'Count']
    st.bar_chart(data=status_counts, x='Status', y='Count')

    st.subheader("2. Applications Over Time")
    time_series = df.groupby(df['Application Date'].dt.to_period("W")).size()
    time_series.index = time_series.index.astype(str)  # Convert Period to string for display
    st.line_chart(time_series)

except FileNotFoundError:
    st.warning("📉 No data to visualize yet. Submit some applications first.")

