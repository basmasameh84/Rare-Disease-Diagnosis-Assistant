import streamlit as st
import pandas as pd
import gdown
import os
import traceback
import logging
import time

# إعداد اللوجينج
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

try:
    logging.info("🚀 App started successfully")

    # ——————————————————————————————
    # ستايل الصفحة + أنيميشن
    st.markdown(
        """
        <style>
        /* خلفية متحركة */
        .stApp {
            background: linear-gradient(270deg, #7fcfbf, #99d6f0, #7fcfbf);
            background-size: 600% 600%;
            animation: gradientMove 15s ease infinite;
        }
        @keyframes gradientMove {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* زرار */
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
        .stStatus {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

    # ——————————————————————————————
    # العنوان
    st.markdown(
        "<h1 style='text-align: left; color: #333333; font-size: 38px;'>🧬 Rare Disease Diagnosis Assistant</h1>",
        unsafe_allow_html=True
    )
    st.write("Welcome! This app helps you identify possible rare diseases based on your symptoms.")
    st.write("Please select your symptoms from the list below and click Diagnose.")

    # ——————————————————————————————
    # تحميل البيانات
    def load_data():
        file_id = "1-OkKiBHgLibBPKyef_7NAF--1w8eMUio"
        drive_url = f"https://drive.google.com/uc?id={file_id}"
        raw_file = "dataset.csv"
        reduced_file = "dataset_reduced.csv"

        if os.path.exists(reduced_file):
            df = pd.read_csv(reduced_file)
        else:
            if not os.path.exists(raw_file):
                gdown.download(url=drive_url, output=raw_file, quiet=True)

            chunks = pd.read_csv(raw_file, chunksize=50000, low_memory=False)
            df = pd.concat(chunks, ignore_index=True)

            if len(df) > 100000:
                df = df.sample(n=100000, random_state=42).reset_index(drop=True)
                df.to_csv(reduced_file, index=False)

        disease_col = next((c for c in df.columns if 'disease' in c.lower()), None)
        symptom_cols = [c for c in df.columns if c != disease_col] if disease_col else []

        return df, disease_col, symptom_cols

    # ——————————————————————————————
    # كاش
    if "data_loaded" not in st.session_state:
        with st.spinner("⏳ Please wait..."):
            df, disease_column, symptom_columns = load_data()
            st.session_state["df"] = df
            st.session_state["disease_column"] = disease_column
            st.session_state["symptom_columns"] = symptom_columns
            st.session_state["data_loaded"] = True
    else:
        df = st.session_state["df"]
        disease_column = st.session_state["disease_column"]
        symptom_columns = st.session_state["symptom_columns"]

    if df.empty or disease_column is None:
        st.stop()

    # ——————————————————————————————
    # اختيار الأعراض
    selected_symptoms = st.multiselect("Select your symptoms:", options=symptom_columns)

    # ——————————————————————————————
    # زر التشخيص
    if st.button("Diagnose"):
        if not selected_symptoms:
            st.warning("⚠️ Please select at least one symptom.")
        else:
            mask = df[selected_symptoms].any(axis=1)
            matched = df.loc[mask, disease_column].value_counts()

            if not matched.empty:
                top_disease = matched.index[0]

                # نصوص متغيرة قبل النتيجة
                steps = [
                    "🔎 Analyzing symptoms...",
                    "🧠 Matching with rare diseases...",
                    "📊 Preparing most likely diagnosis..."
                ]
                placeholder = st.empty()
                for step in steps:
                    placeholder.markdown(f"<h4 style='text-align:center; color:#004d40;'>{step}</h4>", unsafe_allow_html=True)
                    time.sleep(1.5)
                placeholder.empty()

                # عرض الكارت
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #e0f7fa, #b2dfdb);
                        padding: 30px;
                        border-radius: 20px;
                        text-align: center;
                        box-shadow: 0px 6px 15px rgba(0,0,0,0.1);
                        margin-top: 25px;
                        animation: fadeIn 1.5s;
                    ">
                        <h2 style="color:#004d40; margin-bottom:10px;">🩺 Most Likely Diagnosis</h2>
                        <h1 style="color:#00796b; font-size:36px; margin:0; font-weight:bold;">
                            {top_disease}
                        </h1>
                        <hr style="margin:20px auto; border:1px solid #80cbc4; width:60%;">
                        <p style="color:#004d40; font-size:16px; margin-top:10px;">
                            *This is the most probable diagnosis based on your selected symptoms.*
                        </p>
                    </div>

                    <style>
                    @keyframes fadeIn {{
                        from {{opacity: 0; transform: translateY(20px);}}
                        to {{opacity: 1; transform: translateY(0);}}
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("⚠️ No clear match found. Try selecting different symptoms.")

except Exception as e:
    st.error("❌ Unexpected error happened. Please check logs.")
    st.text(traceback.format_exc())
