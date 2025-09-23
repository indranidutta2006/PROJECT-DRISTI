import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide")

# ========================= # Custom Theme Styling # =========================
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    
    }
    </style>
    <div style="text-align: center;">
        <h2 style="margin-top: -10px; color: #2E86C1;">TEAM SANKET</h2>
    </div>
""", unsafe_allow_html=True)
#st.image("team_banner.png", use_column_width=True)

# ========================= # Sidebar with Logo # =========================
#try:
    #st.sidebar.image("logo.png", width=150)
#except Exception:
    #st.sidebar.markdown("**Project Drishti**")

st.sidebar.title("Navigation")
tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8 = st.tabs(
    ["Upload Excel/CSV", "Dashboard", "Attendance", "Marks", "Assignments", "Fees Status", "Student Details", "About"]
)

# ========================= # Upload Page # =========================
with tab1:
    st.header("Upload Student Data")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx","xls","csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(("xlsx", "xls")):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, index_col=False)

            df.reset_index(drop=True, inplace=True)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]

            # ✅ New required columns
            required_cols = [
                "StudentID", "Attendance", "LastSemMarks", "CurrentSemMarks",
                "BacklogAssignments", "AssignmentSubmission", "FeesDue"
            ]
            missing = [c for c in required_cols if c not in df.columns]

            if missing:
                st.error(f"Missing columns: {missing}. Please upload correct file.")
            else:
                st.session_state["data"] = df
                st.success(f"✅ Loaded file with {df.shape[0]} rows and {df.shape[1]} columns.")
                st.write("Here is a sample of your data:")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error reading file: {e}")

def calculate_risk_scores(df):
    """
    Calculate dropout risk score based on attendance, marks, assignments, and fees.
    """
    risk_scores = []
    risk_labels = []

    for _, row in df.iterrows():
        score = 0

        # Attendance
        if row["Attendance"] < 60:
            score += 2
        elif row["Attendance"] < 75:
            score += 1

        # Marks
        avg_marks = (row["LastSemMarks"] + row["CurrentSemMarks"]) / 2
        if avg_marks < 40:
            score += 2
        elif avg_marks < 50:
            score += 1

        # Assignments
        if row["BacklogAssignments"] > 3:
            score += 2
        elif row["BacklogAssignments"] > 0:
            score += 1

        if row["AssignmentSubmission"] < 50:
            score += 2
        elif row["AssignmentSubmission"] < 75:
            score += 1

        # Fees
        if row["FeesDue"] == 1:
            score += 2

        # Assign label
        if score >= 6:
            risk = "High Risk"
        elif score >= 3:
            risk = "Medium Risk"
        else:
            risk = "Low Risk"

        risk_scores.append(score)
        risk_labels.append(risk)

    df["RiskScore"] = risk_scores
    df["Risk"] = risk_labels

    return df
# ========================= # Dashboard Page # =========================
with tab2:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = calculate_risk_scores(st.session_state["data"])

        st.subheader("📋 Student Risk Scores")
        df_display = df.copy()
        df_display.insert(0, "Sl No", range(1, len(df_display) + 1))

        def highlight_risk(val):
            if val == "High Risk":
                return "background-color: red; color: white;"
            elif val == "Medium Risk":
                return "background-color: yellow; color: black;"
            elif val == "Low Risk":
                return "background-color: lightgreen; color: black;"
            return ""

        st.dataframe(df_display.style.applymap(highlight_risk, subset=["Risk"]), hide_index=True)

        # Risk Distribution + Sorted Table
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Student Dropout Risk Distribution")
            risk_counts = df["Risk"].value_counts()
            fig1, ax1 = plt.subplots()
            colors = ['#90ee90', '#f5d90a', '#ff4b4b']  # red, yellow, green
            labels = [f"{risk} ({count})" for risk, count in risk_counts.items()]
            sizes = risk_counts.values.tolist()

            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                    startangle=90, textprops={'fontsize': 10})
            ax1.axis('equal')
            st.pyplot(fig1)

        with col2:
            st.markdown(
                '<h3 style="color: red; font-weight: bold; font-size: 24px;font-family: Georgia, serif;">'
                'Students Sorted by Risk Level</h3>', 
                unsafe_allow_html=True
            )

            risk_order = {"High Risk": 0, "Medium Risk": 1, "Low Risk": 2}
            sorted_df = df[["StudentID", "Risk", "RiskScore"]].copy()
            sorted_df["RiskOrder"] = sorted_df["Risk"].map(risk_order)
            sorted_df = sorted_df.sort_values(by=["RiskOrder", "RiskScore"], ascending=[True, False])
            sorted_df = sorted_df.drop(columns="RiskOrder").reset_index(drop=True)
            sorted_df.insert(0, "Sl No", range(1, len(sorted_df) + 1))

            # Scrollable table (5 rows visible)
            row_height = 35  # px per row approx
            visible_rows = 5
            table_height = row_height * (visible_rows + 1)
            st.dataframe(sorted_df, height=table_height, hide_index=True)
# ========================= # Attendance Page # =========================
with tab3:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        st.header("📅 Attendance Overview")
        st.bar_chart(df.set_index("StudentID")["Attendance"])

# ========================= # Marks Page # =========================
with tab4:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        st.header("📊 Marks Overview")
        st.line_chart(df.set_index("StudentID")[["LastSemMarks", "CurrentSemMarks"]])

# ========================= # Assignments Page # =========================
with tab5:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        st.header("📝 Assignments Overview")
        st.dataframe(df[["StudentID", "BacklogAssignments", "AssignmentSubmission"]])

# ========================= # Fees Status Page # =========================
with tab6:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()
        st.header("💰 Student Fees Status")

        def highlight_fees(val):
            return "background-color: red; color: white;" if val == 1 else "background-color: lightgreen; color: white;"

        st.dataframe(df[["StudentID", "FeesDue"]].style.applymap(highlight_fees, subset=["FeesDue"]))

# ========================= # Student Details Page # =========================
with tab7:  # Student Tab
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"].copy()

        required_cols = ["StudentID", "Attendance", "LastSemMarks", "CurrentSemMarks", 
                         "BacklogAssignments", "AssignmentSubmission", "FeesDue"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Please upload correct file.")
        else:
            # === Risk Score Calculation (same logic as Dashboard) ===
            df["MarksAvg"] = (df["LastSemMarks"] + df["CurrentSemMarks"]) / 2
            df["AssignmentPenalty"] = df["BacklogAssignments"] * 5
            df["FeesDeduction"] = df["FeesDue"] * 20

            df["RiskScore"] = 100 - (
                0.3 * df["Attendance"] +
                0.3 * df["MarksAvg"] +
                0.2 * df["AssignmentSubmission"] -
                df["AssignmentPenalty"] -
                df["FeesDeduction"]
            )
            df["RiskScore"] = df["RiskScore"].clip(lower=0).round(1)

            def risk_level(score):
                if score >= 75:
                    return "High Risk"
                elif score >= 50:
                    return "Medium Risk"
                else:
                    return "Low Risk"

            df["Risk"] = df["RiskScore"].apply(risk_level)

            # === Student Lookup ===
            st.header("🔍 Individual Student Overview")
            student_id = st.selectbox("Select Student ID", df["StudentID"].unique())

            student = df[df["StudentID"] == student_id].iloc[0]

            st.subheader(f"📌 Student ID: {student_id}")
            st.write(f"**Attendance:** {student['Attendance']}%")
            st.write(f"**Last Sem Marks:** {student['LastSemMarks']}")
            st.write(f"**Current Sem Marks:** {student['CurrentSemMarks']}")
            st.write(f"**Backlog Assignments:** {student['BacklogAssignments']}")
            st.write(f"**Assignments Submitted:** {student['AssignmentSubmission']}%")
            st.write(f"**Fees Due:** {'Yes' if student['FeesDue']==1 else 'No'}")
            st.write(f"**Risk Score:** {student['RiskScore']}")
            st.markdown(f"**Dropout Risk:** "
                        f"<span style='color: {'red' if student['Risk']=='High Risk' else 'orange' if student['Risk']=='Medium Risk' else 'green'}; "
                        f"font-weight: bold;'>{student['Risk']}</span>", unsafe_allow_html=True)
# ========================= # About Page # =========================
with tab8:
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges. It unifies student data and shows real-time **Student at Risk (StAR) scores**. 
    """)
