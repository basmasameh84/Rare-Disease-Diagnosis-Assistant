import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import zipfile

# -----------------------------
# Background Color & Button Style
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #66b266, #66ccff); /* Darker green to light blue gradient */
    }
    /* Style for the Diagnose button */
    div.stButton > button:first-child {
        background-color: #4CAF50; 
        color: white;
        border: 2px solid #2E7D32;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #45a049;
        border: 2px solid #1B5E20;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Title & Welcome Message
# -----------------------------
st.markdown(
    """
    <h1 style='text-align: left; color: #333333; font-size: 38px;'>
        🧬 Rare Disease Diagnosis Assistant
    </h1>
    """,
    unsafe_allow_html=True
)

st.write("Welcome! This app helps you identify possible rare diseases based on your symptoms.")
st.write("Please select your symptoms from the list below and click Diagnose.")

# -----------------------------
# Load Dataset from ZIP with Caching
# -----------------------------
@st.cache_data
def load_data():
    with zipfile.ZipFile("Final_Augmented_dataset_Diseases_and_Symptoms.zip", 'r') as zip_ref:
        with zip_ref.open("Final_Augmented_dataset_Diseases_and_Symptoms.csv") as f:
            df = pd.read_csv(f)

    # Find disease column
    disease_col = None
    for col in df.columns:
        if 'disease' in col.lower():
            disease_col = col
            break

    symptom_cols = [col for col in df.columns if col != disease_col] if disease_col else []
    return df, disease_col, symptom_cols

df, disease_column, symptom_columns = load_data()

if df.empty:
    st.error("❌ Dataset is empty or disease column not found.")

# -----------------------------
# User Symptom Selection
# -----------------------------
selected_symptoms = st.multiselect(
    "Select your symptoms:",
    options=symptom_columns
)

# -----------------------------
# Diagnose Button
# -----------------------------
if st.button("Diagnose"):
    if not selected_symptoms:
        st.warning("⚠️ Please select at least one symptom.")
    else:
        mask = df[selected_symptoms].any(axis=1)
        matched_diseases_counts = df.loc[mask, disease_column].value_counts()

        if not matched_diseases_counts.empty:
            top3 = matched_diseases_counts.head(3)

            st.success(f"✅ Most likely disease: {top3.index[0]}")

            st.subheader("Top 3 Predicted Diseases")
            fig, ax = plt.subplots()
            colors = ["#4CAF50", "#2196F3", "#FFC107"]  # Highest -> Green, Middle -> Blue, Lowest -> Yellow
            ax.bar(top3.index, top3.values, color=colors)
            ax.set_ylabel("Matching Count")
            ax.set_xlabel("Disease")
            ax.set_title("Prediction Distribution")
            st.pyplot(fig)
        else:
            st.error("⚠️ No clear match found. Please try selecting different symptoms.")
