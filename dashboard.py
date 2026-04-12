import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GitGuard Analytics", layout="wide")

st.title("🛡️ GitGuard Team Analytics Dashboard")
st.markdown("Monitor commit quality, standard compliance, and team sentiment in real-time.")

LOG_FILE = "commit_logs.csv"

if os.path.exists(LOG_FILE):
    df = pd.read_csv(LOG_FILE)
    
    if not df.empty:
        # Top Metrics Row
        col1, col2, col3 = st.columns(3)
        total_commits = len(df)
        accepted = len(df[df["Status"] == "Accepted"])
        compliance_rate = (accepted / total_commits) * 100

        col1.metric("Total Commits Monitored", total_commits)
        col2.metric("Compliance Rate", f"{compliance_rate:.1f}%")
        col3.metric("Avg Sentiment Score", f"{df['Sentiment_Score'].mean():.2f}")

        st.divider()

        # Split layout for charts and data
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("Commit Status Breakdown")
            status_counts = df["Status"].value_counts()
            st.bar_chart(status_counts, color=["#ff4b4b" if "Rejected" in status_counts.index else "#00cc96"])

        with right_col:
            st.subheader("Common Rejection Reasons")
            rejections = df[df["Status"] == "Rejected"]
            if not rejections.empty:
                st.dataframe(rejections["Reason"].value_counts().reset_index(), use_container_width=True)
            else:
                st.success("No rejected commits yet! Great job team.")

        st.divider()
        st.subheader("Recent Commit Activity")
        st.dataframe(df.tail(10).iloc[::-1], use_container_width=True) # Show last 10, newest first
    else:
        st.info("Log file is empty. Make a commit to see data!")
else:
    st.warning("No commit logs found yet. Try making a commit in your terminal!")