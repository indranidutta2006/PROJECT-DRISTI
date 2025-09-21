import streamlit as st
import pandas as pd
import numpy as np

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide")

# ========================= # Custom Theme Styling # =========================
st.markdown("""
    <style>
    /* Whole page background */
    .reportview-container {
        background-color: #f4f8fb;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #002b5c; /* Dark blue */
        color: white;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: white !important;
    }

    /* Main headers */
    h1, h2, h3 {
        color: #002b5c;
    }

    /* Dataframe table font */
    .stDataFrame {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ========================= # Sidebar with Logo # =========================
try:
    st.sidebar.image("logo.png", width=150)  # Upload this file to repo root
except Exception:
    st.sidebar.markdown("**Project Drishti**")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Upload Data", "About"])

# ========================= # Title # =========================
st.title("🏫 Project Drishti – Student Success Early Warning System")
st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

# ========================= # Upload Page # =========================
if page == "Upload Data":
    st.header("Upload Student Data")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(("xlsx","xls")):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)

            st.success(f"✅ Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
            st.write("Here is a sample of your data:")
            st.dataframe(df.head())
            st.session_state["data"] = df

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ========================= # Dashboard Page # =========================
elif page == "Dashboard":
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first from the sidebar.")
    else:
        df = st.session_state["data"].copy()

        required_cols = ["StudentID", "Attendance", "Marks", "FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # === Risk Score Calculation ===
            df["FeesDeduction"] = df["FeesDue"] * 20
            df["RiskScore"] = 100 - (0.4*df["Attendance"] + 0.4*df["Marks"] + df["FeesDeduction"])
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            # === Assign Risk Levels ===
            def risk_level(score):
                if score >= 75:
                    return "High Risk"
                elif score >= 50:
                    return "Medium Risk"
                else:
                    return "Low Risk"

            df["Risk"] = df["RiskScore"].apply(risk_level)

            # === Color-coded Dataframe ===
            def highlight_risk(val):
                if val == "High Risk":
                    return "background-color: red; color: white;"
                elif val == "Medium Risk":
                    return "background-color: orange; color: black;"
                elif val == "Low Risk":
                    return "background-color: lightgreen; color: black;"
                return ""

            st.subheader("📋 Student Risk Scores")
            st.dataframe(df.style.applymap(highlight_risk, subset=["Risk"]))

            # === Risk Distribution Chart ===
            st.subheader("📊 Risk Distribution")
            risk_counts = df["Risk"].value_counts()
            st.bar_chart(risk_counts)

            # === Detailed View on Click ===
            student_id = st.selectbox("Select Student to View Details", df["StudentID"])

            if student_id:
                student_data = df[df["StudentID"] == student_id].iloc[0]

                # Plot Risk Score in a half-circle gauge
                #fig, ax = plt.subplots(figsize=(5, 3))
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 1)
                ax.barh(0, student_data["RiskScore"], color="red", height=0.3, align="center")
                ax.text(student_data["RiskScore"] - 5, 0, f'{student_data["RiskScore"]}%', fontsize=14, color='white', ha='center', va='center')

                ax.set_yticks([])
                ax.set_xticks([0, 50, 100])
                ax.set_xticklabels([0, 50, 100], fontsize=10)
                ax.set_title(f"Student {student_id} Risk Score", fontsize=16)
                st.pyplot(fig)

                # Academic Performance and Attendance Line Chart
                st.subheader(f"📈 Academic Performance and Attendance for Student {student_id}")
                st.line_chart({
                    "Marks": df[df["StudentID"] == student_id]["Marks"],
                    "Attendance": df[df["StudentID"] == student_id]["Attendance"]
                })

                # Fees Due Table
                st.subheader(f"💰 Fees Due for Student {student_id}")
                st.table(pd.DataFrame({
                    "StudentID": [student_id],
                    "Fees Due": [student_data["FeesDue"]]
                }))

                # Recommended Actions Table
                st.subheader(f"📝 Recommended Actions for Student {student_id}")
                recommended_actions = pd.DataFrame({
                    "Action": ["Monitor Attendance", "Review Marks Progress", "Follow up on Fees Payment"],
                    "Urgency": ["High", "Medium", "High"]
                })
                st.table(recommended_actions)

# ========================= # About Page # =========================
elif page == "About":
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges. It unifies student data and shows real-time **Student at Risk (StAR) scores**. 
    ### Features
    - **High Risk** students = 🔴 Red
    - **Medium Risk** students = 🟠 Orange
    - **Low Risk** students = 🟢 Green
    - Upload Excel/CSV files directly
    - Easy, intuitive portal look
    """)
