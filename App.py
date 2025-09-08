import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gdown
import os

# ——————————————————————————————
# ستايل الصفحة والزرار
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #7fcfbf, #99d6f0);
    }
    div.stButton > button:first-child {
        background-color: #4CAF50; color: white;
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

# العنوان الترحيبي
st.markdown(
    "<h1 style='text-align: left; color: #333333; font-size: 38px;'>🧬 Rare Disease Diagnosis Assistant</h1>",
    unsafe_allow_html=True
)
st.write("Welcome! This app helps you identify possible rare diseases based on your symptoms.")
st.write("Please select your symptoms from the list below and click Diagnose.")

# ——————————————————————————————
# تحميل البيانات باستخدام gdown
@st.cache_data
def load_data():
    file_id = "1-OkKiBHgLibBPKyef_7NAF--1w8eMUio"
    drive_url = f"https://drive.google.com/uc?id={file_id}"
    output_filename = "dataset.csv"

    # لو الملف محمّل من قبل، استخدمه مباشرة
    if not os.path.exists(output_filename):
        try:
            gdown.download(url=drive_url, output=output_filename, quiet=False)
        except Exception as e:
            st.error(f"❌ Failed to download using gdown: {e}")
            return pd.DataFrame(), None, []

    try:
        df = pd.read_csv(output_filename)
    except Exception as e:
        st.error(f"❌ Couldn't read CSV from downloaded file: {e}")
        return pd.DataFrame(), None, []

    disease_col = next((c for c in df.columns if 'disease' in c.lower()), None)
    symptom_cols = [c for c in df.columns if c != disease_col] if disease_col else []
    return df, disease_col, symptom_cols

df, disease_column, symptom_columns = load_data()
if df.empty or disease_column is None:
    st.stop()

# ——————————————————————————————
# اختيار الأعراض
selected_symptoms = st.multiselect("Select your symptoms:", options=symptom_columns)

# ——————————————————————————————
# زر التشخيص ومنطق العرض
if st.button("Diagnose"):
    if not selected_symptoms:
        st.warning("⚠️ Please select at least one symptom.")
    else:
        mask = df[selected_symptoms].any(axis=1)
        matched = df.loc[mask, disease_column].value_counts()

        if not matched.empty:
            top3 = matched.head(3)
            st.success(f"✅ Most likely disease: {top3.index[0]}")
            st.subheader("Top 3 Predicted Diseases")
            fig, ax = plt.subplots()
            colors = ["#4CAF50", "#2196F3", "#FFC107"]
            ax.bar(top3.index, top3.values, color=colors)
            ax.set_ylabel("Matching Count")
            ax.set_xlabel("Disease")
            ax.set_title("Prediction Distribution")
            st.pyplot(fig)
        else:
            st.error("⚠️ No clear match found. Try selecting different symptoms.")

