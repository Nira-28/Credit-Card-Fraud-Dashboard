import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Config ---
st.set_page_config(page_title=" Fraud Dashboard", layout="wide")

# --- Load Dataset ---
@st.cache_data
def load_data():
    return pd.read_csv("creditcard.csv")

data = load_data()
data['Hour'] = (data['Time'] // 3600) % 24

st.title(" Credit Card Fraud Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

hour_range = st.sidebar.slider("Select Hour Range (0-23)", 0, 23, (0,23))
time_range = st.sidebar.slider(
    "Select Time Range (seconds since first transaction)", 
    int(data['Time'].min()), int(data['Time'].max()), 
    (int(data['Time'].min()), int(data['Time'].max()))
)
amount_range = st.sidebar.slider(
    "Select Transaction Amount Range ($)", 
    float(data['Amount'].min()), float(data['Amount'].max()), 
    (float(data['Amount'].min()), float(data['Amount'].max()))
)

# --- Apply Filters ---
filtered_data = data[
    (data['Hour'] >= hour_range[0]) & (data['Hour'] <= hour_range[1]) &
    (data['Time'] >= time_range[0]) & (data['Time'] <= time_range[1]) &
    (data['Amount'] >= amount_range[0]) & (data['Amount'] <= amount_range[1])
]
filtered_fraud = filtered_data[filtered_data['Class'] == 1]

# --- Fraud Alert Panel ---
st.subheader(" Fraud Alerts")
if not filtered_fraud.empty:
    # Peak fraud hour
    peak_hour = filtered_fraud['Hour'].value_counts().idxmax()
    peak_hour_count = filtered_fraud['Hour'].value_counts().max()
    
    # Top transaction amount
    top_amount = filtered_fraud['Amount'].max()
    
    st.markdown(f"**Peak Fraud Hour:** {peak_hour}:00 with **{peak_hour_count}** fraudulent transactions")
    st.markdown(f"**Highest Fraudulent Transaction Amount:** ${top_amount:,.2f}")
    
    # --- Top 5 Fraud Hours & Amounts ---
    st.subheader(" Top 5 Fraud Hours & Amounts")
    
    top_hours = filtered_fraud['Hour'].value_counts().head(5).reset_index()
    top_hours.columns = ['Hour', 'Fraud Count']
    
    top_amounts = filtered_fraud.sort_values(by='Amount', ascending=False).head(5)[['Amount', 'Time']]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 5 Fraud Hours**")
        st.table(top_hours)
    with col2:
        st.markdown("**Top 5 Fraudulent Transactions by Amount**")
        st.table(top_amounts)
else:
    st.markdown("No fraudulent transactions in the selected filters ")

# --- Tabs for Charts ---
tab1, tab2 = st.tabs(["Hourly Analysis", "Time & Amount Trends"])

with tab1:
    st.header(" Hourly Analysis")
    col1, col2 = st.columns(2)
    
    # Fraud Count by Hour
    with col1:
        st.subheader("Fraud Count by Hour")
        fraud_by_hour = filtered_fraud['Hour'].value_counts().sort_index()
        fig1, ax1 = plt.subplots(figsize=(8,5))
        sns.barplot(x=fraud_by_hour.index, y=fraud_by_hour.values, palette="Reds", ax=ax1)
        ax1.set_xlabel("Hour of Day")
        ax1.set_ylabel("Number of Fraudulent Transactions")
        st.pyplot(fig1)
    
    # Fraud Rate by Hour
    with col2:
        st.subheader("Fraud Rate (%) by Hour")
        transactions_by_hour = filtered_data.groupby('Hour')['Class'].count()
        fraud_rate = (fraud_by_hour / transactions_by_hour) * 100
        fig2, ax2 = plt.subplots(figsize=(8,5))
        sns.lineplot(x=fraud_rate.index, y=fraud_rate.values, marker="o", color="red", ax=ax2)
        ax2.set_xlabel("Hour of Day")
        ax2.set_ylabel("Fraud Percentage (%)")
        ax2.grid(True)
        st.pyplot(fig2)

with tab2:
    st.header(" Time &  Amount Trends")
    col3, col4 = st.columns(2)
    
    # Fraud Trend Over Time
    with col3:
        st.subheader("Fraud Trend Over Time")
        fig3, ax3 = plt.subplots(figsize=(8,5))
        sns.histplot(filtered_fraud['Time'], bins=100, color="red", alpha=0.7, kde=False, ax=ax3)
        ax3.set_xlabel("Time (seconds)")
        ax3.set_ylabel("Number of Fraudulent Transactions")
        st.pyplot(fig3)
    
    # Fraud Trend by Amount
    with col4:
        st.subheader("Fraud Trend by Amount")
        fig4, ax4 = plt.subplots(figsize=(8,5))
        sns.histplot(filtered_fraud['Amount'], bins=50, color="red", alpha=0.7, kde=False, ax=ax4)
        ax4.set_xlabel("Transaction Amount ($)")
        ax4.set_ylabel("Number of Fraudulent Transactions")
        st.pyplot(fig4)
