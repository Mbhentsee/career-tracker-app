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

df_path = "data/applications.csv"

# Try loading existing applications
try:
    df = pd.read_csv(df_path)

    # Format date column if needed
    if 'Application Date' in df.columns:
        df['Application Date'] = pd.to_datetime(df['Application Date']).dt.date

    st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.warning("⚠️ No applications yet. Add some using the form above.")


st.header("📊 Application Insights")

try:
    df = pd.read_csv("data/applications.csv")

    # Format date column
    df['Application Date'] = pd.to_datetime(df['Application Date'])

    st.subheader("1. Applications by Status")
    status_counts = df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    st.bar_chart(data=status_counts, x='Status', y='Count')

    st.subheader("2. Applications Over Time")
    time_series = df.groupby(df['Application Date'].dt.to_period("W")).size()
    time_series.index = time_series.index.astype(str)  # Convert Period to string for display
    st.line_chart(time_series)

except FileNotFoundError:
    st.warning("📉 No data to visualize yet. Submit some applications first.")
