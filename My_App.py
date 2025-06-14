import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Career Tracker", layout="wide")
st.header("📝 Add New Application")

# Ensure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

df_path = "data/applications.csv"

# Load data
try:
    df = pd.read_csv(df_path)
    df['Application Date'] = pd.to_datetime(df['Application Date'], errors='coerce')
except FileNotFoundError:
    df = pd.DataFrame(columns=["Job Title", "Company", "Application Date", "Status", "Job Link", "Location", "Notes"])

# --- Form Section ---
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
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(df_path, index=False)
        st.success("✅ Application added successfully!")

# --- Filters ---
st.subheader("📋 All Applications")

if not df.empty:
    statuses = df['Status'].unique().tolist()
    selected_status = st.multiselect("Filter by Status", options=statuses, default=statuses)

    min_date = df['Application Date'].min().date()
    max_date = df['Application Date'].max().date()
    date_range = st.date_input("Filter by Date Range", value=(min_date, max_date))

    filtered_df = df[
        (df['Status'].isin(selected_status)) &
        (df['Application Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
    ]

    # Search
    search_query = st.text_input("🔍 Search company name")
    if search_query:
        filtered_df = filtered_df[filtered_df['Company'].str.contains(search_query, case=False)]

    # Sort
    sort_order = st.selectbox("Sort applications by:", ["Newest first", "Oldest first"])
    if sort_order == "Newest first":
        filtered_df = filtered_df.sort_values(by="Application Date", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="Application Date", ascending=True)

    st.success(f"🎯 Showing {len(filtered_df)} filtered application(s)")
    st.dataframe(filtered_df, use_container_width=True)

    # Summary
    st.subheader("📈 Application Summary")
    total_apps = len(filtered_df)
    interviews = (filtered_df['Status'] == 'Interview').sum()
    offers = (filtered_df['Status'] == 'Offer').sum()
    rejections = (filtered_df['Status'] == 'Rejected').sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", total_apps)
    col2.metric("Interviews", interviews)
    col3.metric("Offers", offers)
    col4.metric("Rejections", rejections)

    # Visualizations
    st.header("📊 Application Insights")

    st.subheader("1. Applications by Status")
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    st.bar_chart(data=status_counts, x='Status', y='Count')

    st.subheader("2. Applications Over Time")
    time_series = filtered_df.groupby(filtered_df['Application Date'].dt.to_period("W")).size()
    time_series.index = time_series.index.astype(str)
    st.line_chart(time_series)

    st.subheader("🧁 Status Distribution (Pie Chart)")
    fig, ax = plt.subplots()
    ax.pie(status_counts['Count'], labels=status_counts['Status'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.warning("⚠️ No application data available yet.")
