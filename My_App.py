import streamlit as st
import pandas as pd
import os 

st.set_page_config(page_title="Career Tracker", layout="wide")
st.header("📝 Add New Application")

df_path = "data/applications.csv"

# Ensure the 'data' directory exists
os.makedirs(os.path.dirname(df_path), exist_ok=True)

# Load data
try:
    df = pd.read_csv(df_path)
    if 'Application Date' in df.columns:
        # Convert 'Application Date' to datetime objects, coercing errors
        df['Application Date'] = pd.to_datetime(df['Application Date'], errors='coerce')
    else:
        df['Application Date'] = pd.NaT # Initialize if column doesn't exist
except FileNotFoundError:
    # Create an empty DataFrame if the file doesn't exist
    df = pd.DataFrame(columns=["Job Title", "Company", "Application Date", "Status", "Job Link", "Location", "Notes"])
    # Ensure 'Application Date' is of datetime type for an empty DataFrame
    df['Application Date'] = pd.to_datetime(df['Application Date'])


# --- Form Section ---
with st.form(key='application_form'):
    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Job Title", help="e.g., Software Engineer")
        company = st.text_input("Company", help="e.g., Google")
        application_date = st.date_input("Application Date", help="Select the date you applied.")

    with col2:
        status = st.selectbox("Application Status", ["Applied", "Interview", "Offer", "Rejected", "No Response"],
                              help="Current status of your application.")
        job_link = st.text_input("Job Link (optional)", help="Direct link to the job posting.")
        location = st.text_input("Location (City, Country)", help="e.g., New York, USA")

    notes = st.text_area("Additional Notes", help="Any specific details, contacts, or follow-ups.")
    submitted = st.form_submit_button("➕ Add Application")

    if submitted:
        # Create a new entry, converting application_date to a pandas Timestamp (datetime object)
        new_entry = {
            "Job Title": job_title,
            "Company": company,
            "Application Date": pd.to_datetime(application_date), # Store as datetime object
            "Status": status,
            "Job Link": job_link,
            "Location": location,
            "Notes": notes
        }
        # Concatenate the new entry to the DataFrame
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        # Save the updated DataFrame back to CSV
        df.to_csv(df_path, index=False)
        st.success("✅ Application added successfully!")
        # Rerun the app to clear the form and update filters/display
        st.rerun() # --- CHANGED from st.experimental_rerun() to st.rerun() ---

# ------------------- FILTERS ----------------------
# Check if df is not empty AND 'Application Date' column exists AND it contains at least one non-NaT value
if not df.empty and 'Application Date' in df.columns and df['Application Date'].notna().any():
    # Convert min/max dates to Python date objects for st.date_input
    min_date = df['Application Date'].min().date()
    max_date = df['Application Date'].max().date()
    
    # Handle cases where min_date might be greater than max_date (e.g., due to data issues)
    if min_date > max_date:
        min_date = max_date # Or set to a default sensible value

    date_range = st.date_input("📅 Filter by Date Range", value=(min_date, max_date))

    # Ensure date_range always has two elements
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
    else:
        # If only one date is selected (e.g., during interaction), set range to that single date
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[0])


    selected_status = st.multiselect("🎯 Filter by Status", 
                                     options=df['Status'].unique(), 
                                     default=list(df['Status'].unique()),
                                     help="Select application statuses to display.")

    filtered_df = df[
        (df['Status'].isin(selected_status)) &
        (df['Application Date'].between(start_date, end_date))
    ]
else:
    st.info("ℹ️ No applications with valid dates yet. Add an application to enable date filtering.")
    filtered_df = df.copy() # Ensure filtered_df is defined even if no dates

# ------------------- SEARCH & SORT ----------------------
search_query = st.text_input("🔍 Search company name", help="Type to search for companies (case-insensitive).")
if search_query:
    filtered_df = filtered_df[filtered_df['Company'].str.contains(search_query, case=False, na=False)]

sort_order = st.selectbox("Sort applications by:", ["Newest first", "Oldest first"],
                          help="Choose the sorting order for application dates.")
if 'Application Date' in filtered_df.columns:
    if sort_order == "Newest first":
        filtered_df = filtered_df.sort_values(by="Application Date", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="Application Date", ascending=True)

# ------------------- DISPLAY ----------------------
st.success(f"🎯 Showing {len(filtered_df)} filtered application(s)")
st.dataframe(filtered_df, use_container_width=True)

# ------------------- SUMMARY METRICS ----------------------
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

# ------------------- VISUALIZATIONS ----------------------
st.header("📊 Application Insights")

if not filtered_df.empty and 'Status' in filtered_df.columns:
    st.subheader("1. Applications by Status")
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    st.bar_chart(data=status_counts, x='Status', y='Count')

if not filtered_df.empty and 'Application Date' in filtered_df.columns and filtered_df['Application Date'].notna().any():
    st.subheader("2. Applications Over Time")
    # Ensure 'Application Date' is datetime before resampling
    time_series = filtered_df.dropna(subset=['Application Date']).groupby(
        filtered_df['Application Date'].dt.to_period("W")
    ).size()
    time_series.index = time_series.index.astype(str) # Convert PeriodIndex to string for plotting
    st.line_chart(time_series)
else:
    st.info("No applications with valid dates to display 'Applications Over Time' chart.")

if not filtered_df.empty:
    st.subheader("🧁 Status Distribution (Pie Chart)")
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    # Check if there's enough data for a meaningful pie chart
    if status_counts['Count'].sum() > 0:
        fig, ax = plt.subplots(figsize=(6, 6)) # Added figsize for better appearance
        ax.pie(status_counts['Count'], labels=status_counts['Status'], autopct='%1.1f%%', startangle=90,
               wedgeprops={'edgecolor': 'black'}) # Added edgecolor for better separation
        ax.axis('equal') # Ensures pie chart is circular
        st.pyplot(fig)
    else:
        st.info("Not enough data to display pie chart.")
else:
    st.info("No data available to display pie chart.")
