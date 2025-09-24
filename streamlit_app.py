import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import base64
from io import BytesIO

# ========================= # Page Config # =========================
st.set_page_config(page_title="Project Drishti", layout="wide")

# ========================= # Banner =========================
IMG_PATH = "assets/team_banner.png"

def display_banner():
    try:
        image = Image.open(IMG_PATH)
        max_width = 100
        aspect_ratio = image.height / image.width
        new_height = int(max_width * aspect_ratio)
        image = image.resize((max_width, new_height))

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{img_str}" width="{max_width}" height="{new_height}" style="margin-right: 15px;">
                <h2 style="color: #0a3a5e; margin: 0;font-family:Georgia, serif;">PROJECT DRISHTI</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.markdown(
            "<h2 style='text-align: center; color: #0a3a5e;font-family:Georgia, serif;'>PROJECT DRISHT</h2>",
            unsafe_allow_html=True
        )

display_banner()


# ========================= # Sidebar =========================
#st.sidebar.title("Navigation")
tabs = st.tabs(
    ["Upload Excel/CSV", "Dashboard", "Attendance", "Marks", "Assignments", "Fees Status", "Student Details", "About"]
)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = tabs

# ========================= # Upload Page =========================
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
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error reading file: {e}")


# ========================= # Risk Score Function =========================
def calculate_risk_scores(df):
    star_scores = []
    risk_labels = []

    for _, row in df.iterrows():
        # New StAR Score formula
        star_score = round(
            ((100 - row["Attendance"]) * 0.6)
            + (max(0, row["LastSemMarks"] - row["CurrentSemMarks"]) * 0.8)
            + (row["BacklogAssignments"] * 15)
            + ((100 - row["AssignmentSubmission"]) * 0.3)
            + (10 if row["FeesDue"] == 1 else 0)
        )

        # Ensure score always between 1 and 100
        star_score = np.clip(star_score, 1, 100)
        star_scores.append(star_score)

        # Risk label mapping
        if star_score >= 75:
            risk = "High Risk"
        elif star_score >= 50:
            risk = "Medium Risk"
        else:
            risk = "Low Risk"
        risk_labels.append(risk)

    df["StARScore"] = star_scores
    df["Risk"] = risk_labels
    return df
# ========================= # Dashboard =========================
with tab2:
    st.title("🏫 Project Drishti – Student Success Early Warning System")
    st.markdown("Helping educators move from **reactive** to **proactive** mentoring")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = calculate_risk_scores(st.session_state["data"])
        st.subheader("📋 Student StAR Scores")
        df_display = df.copy()
        df_display.insert(0, "Sl No", range(1, len(df_display) + 1))

        def highlight_risk(val):
            if val == "High Risk": return "background-color: red; color: white;"
            elif val == "Medium Risk": return "background-color: yellow; color: black;"
            elif val == "Low Risk": return "background-color: lightgreen; color: black;"
            return ""

        st.dataframe(df_display.style.applymap(highlight_risk, subset=["Risk"]), hide_index=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Student Dropout Risk Distribution")
            risk_counts = df["Risk"].value_counts()
            fig, ax = plt.subplots()
            colors = ['#ffb4b', '#f5d90a','#90ee90']  # Low, Medium, High
            ax.pie(
                risk_counts.values,
                labels=[f"{r} ({c})" for r, c in zip(risk_counts.index, risk_counts.values)],
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10}
            )
            ax.axis('equal')
            st.pyplot(fig)

        with col2:
            st.markdown(
                '<h3 style="color:red;font-weight:bold;font-size:24px;font-family:Georgia, serif;">'
                'Students Sorted by StAR Score</h3>', unsafe_allow_html=True)
            sorted_df = df.sort_values(by=["StARScore"], ascending=False).reset_index(drop=True)
            sorted_df.insert(0, "Sl No", range(1, len(sorted_df) + 1))
            st.dataframe(sorted_df, height=210, hide_index=True)

# ========================= # Attendance =========================
with tab3:
    st.header("📅 Attendance Overview")
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"]
        st.bar_chart(df.set_index("StudentID")["Attendance"])

# ========================= # Marks =========================
with tab4:
    st.header("📊 Marks Overview")
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"]
        st.line_chart(df.set_index("StudentID")[["LastSemMarks","CurrentSemMarks"]])

# ========================= # Assignments =========================
with tab5:
    st.header("📝 Assignments Overview")
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"]
        st.dataframe(df[["StudentID","BacklogAssignments","AssignmentSubmission"]])

# ========================= # Fees =========================
with tab6:
    st.header("💰 Student Fees Status")
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        df = st.session_state["data"]
        def highlight_fees(val):
            return "background-color:red;color:white;" if val==1 else "background-color:lightgreen;color:white;"
        st.dataframe(df[["StudentID","FeesDue"]].style.applymap(highlight_fees, subset=["FeesDue"]))

# ========================= # Student Details =========================
with tab7:
    st.header("🔍 Individual Student Overview")
    if "data" not in st.session_state:
        st.warning("⚠️ Please upload student data first.")
    else:
        # Calculate risk scores
        df = calculate_risk_scores(st.session_state["data"])
        
        # Student selector
        student_id = st.selectbox("Select Student ID", df["StudentID"].unique())
        student = df[df["StudentID"] == student_id].iloc[0]

        # Show student details
        st.write("**Attendance:** {}%".format(student['Attendance']))
        st.write("**Last Sem Marks:** {}".format(student['LastSemMarks']))
        st.write("**Current Sem Marks:** {}".format(student['CurrentSemMarks']))
        st.write("**Backlog Assignments:** {}".format(student['BacklogAssignments']))
        st.write("**Assignments Submitted:** {}%".format(student['AssignmentSubmission']))
        st.write("**Fees Due:** {}".format("Yes" if student['FeesDue'] == 1 else "No"))

        # StAR Score and Risk
        star_score = student["StARScore"]
        risk = student["Risk"]

        st.write("**StAR Score:** {}".format(star_score))

        st.markdown(
            "**Dropout Risk:** <span style='color:{}; font-weight:bold'>{}</span>".format(
                "red" if risk.lower().startswith("high") else "orange" if risk.lower().startswith("medium") else "green",
                risk
            ),
            unsafe_allow_html=True
        )

        # ✅ Recommended Actions (now forced to show with <br>)
        if risk.lower().startswith("high"):
            st.markdown(
                "**Recommended Actions:**<br>"
                "1. Schedule Meeting with <b>{}</b>.<br>"
                "2. Contact Guardians.".format(student['StudentID']),
                unsafe_allow_html=True
            )
        elif risk.lower().startswith("medium"):
            st.markdown(
                "**Recommended Actions:**<br>"
                "1. Arrange Counseling Session for <b>{}</b>.<br>"
                "2. Monitor Progress Weekly.".format(student['StudentID']),
                unsafe_allow_html=True
            )
        else:  # Low Risk
            st.markdown(
                "**Recommended Actions:**<br>"
                "1. Encourage <b>{}</b> to keep up the good work.<br>"
                "2. Monitor Monthly.".format(student['StudentID']),
                unsafe_allow_html=True
            )
            
# ========================= # About =========================
with tab8:
    st.header("ℹ️ About Project Drishti")
    st.markdown("""
    **Drishti** is an early warning system for schools/colleges. It unifies student data and shows real-time **Student at Risk (StAR) scores**.
    """)
