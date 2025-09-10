import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gdown
import os
import traceback
import logging

# إعداد اللوجينج
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   # يكتب في ملف
        logging.StreamHandler()           # يطبع في الـ console
    ]
)

try:
    logging.info("🚀 App started successfully")

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
        /* إخفاء صندوق Running */
        .stStatus {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ——————————————————————————————
    # العنوان الترحيبي
    st.markdown(
        "<h1 style='text-align: left; color: #333333; font-size: 38px;'>🧬 Rare Disease Diagnosis Assistant</h1>",
        unsafe_allow_html=True
    )
    st.write("Welcome! This app helps you identify possible rare diseases based on your symptoms.")
    st.write("Please select your symptoms from the list below and click Diagnose.")

    # ——————————————————————————————
    # تحميل البيانات
    def load_data():
        logging.info("📥 Starting to load data...")
        file_id = "1-OkKiBHgLibBPKyef_7NAF--1w8eMUio"
        drive_url = f"https://drive.google.com/uc?id={file_id}"
        output_filename = "dataset.csv"

        if not os.path.exists(output_filename):
            logging.info("⬇️ Downloading dataset from Google Drive...")
            gdown.download(url=drive_url, output=output_filename, quiet=True)
        else:
            logging.info("✅ Dataset already exists locally.")

        chunks = pd.read_csv(output_filename, chunksize=50000, low_memory=False)
        df = pd.concat(chunks, ignore_index=True)
        logging.info(f"✅ Data loaded successfully! Rows: {len(df)}, Columns: {len(df.columns)}")

        disease_col = next((c for c in df.columns if 'disease' in c.lower()), None)
        if disease_col:
            logging.info(f"🩺 Found disease column: {disease_col}")
        else:
            logging.warning("⚠️ No disease column found!")

        symptom_cols = [c for c in df.columns if c != disease_col] if disease_col else []
        logging.info(f"📝 Number of symptom columns: {len(symptom_cols)}")

        return df, disease_col, symptom_cols

    # ——————————————————————————————
    # كاش يدوي بالـ session_state
    if "data_loaded" not in st.session_state:
        with st.spinner("⏳ Please wait..."):
            logging.info("⏳ Loading dataset for the first time...")
            df, disease_column, symptom_columns = load_data()
            st.session_state["df"] = df
            st.session_state["disease_column"] = disease_column
            st.session_state["symptom_columns"] = symptom_columns
            st.session_state["data_loaded"] = True
            logging.info("✅ Dataset cached in session_state")
    else:
        df = st.session_state["df"]
        disease_column = st.session_state["disease_column"]
        symptom_columns = st.session_state["symptom_columns"]
        logging.info("♻️ Loaded dataset from session_state")

    if df.empty or disease_column is None:
        logging.error("❌ Dataframe empty or no disease column found, stopping app.")
        st.stop()

    # ——————————————————————————————
    # اختيار الأعراض
    selected_symptoms = st.multiselect("Select your symptoms:", options=symptom_columns)

    # ——————————————————————————————
    # زر التشخيص ومنطق العرض
    if st.button("Diagnose"):
        if not selected_symptoms:
            st.warning("⚠️ Please select at least one symptom.")
            logging.warning("⚠️ Diagnose clicked without selecting symptoms")
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
                logging.info(f"✅ Prediction done. Top disease: {top3.index[0]}")
            else:
                st.error("⚠️ No clear match found. Try selecting different symptoms.")
                logging.warning("⚠️ No match found for selected symptoms.")

except Exception as e:
    logging.exception("💥 Unexpected error happened!")
    st.error("❌ Unexpected error happened. Please check logs.")
    st.text(traceback.format_exc())

