import streamlit as st
import pandas as pd
import joblib
import time
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk

# --- CSS Styling ---
st.markdown("""
    <style>
    section[data-testid="stSidebar"] .css-1v0mbdj, section[data-testid="stSidebar"] .css-1cpxqw2 {
        font-size: 22px !important;
        font-weight: bold;
        color: #f72585;
        transition: 0.3s;
    }
    section[data-testid="stSidebar"] .css-1cpxqw2:hover {
        color: #7209b7 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #12002e, #3c096c, #9d4edd);
        color: white;
        padding: 10px;
        border-right: 2px solid #f72585;
    }
    .stApp {
        background: linear-gradient(to bottom right, #03071e, #370617);
        color: white;
    }
    h1 ,h2, h3 {
        color: #f72585 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load model and features ---
model = joblib.load("salary_prediction_model_v2.pkl")
model_features = joblib.load("model_features_v2.pkl")

job_titles = sorted([col.replace("Job Title_", "") for col in model_features if col.startswith("Job Title_")])
job_states = sorted([col.replace("job_state_", "") for col in model_features if col.startswith("job_state_")])

# --- Sidebar Navigation ---
st.set_page_config(page_title="Salary Predictor", layout="wide")
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🔮 Predict Salary", "📈 Salary Growth", "📍 Salary by State"])

# 🏠 --- HOME PAGE ---
if page == "🏠 Home":
    st.markdown("""
    <h1 style='color:#ff4bff;'>🎓 Welcome to the Salary Prediction App</h1>
    <p style='font-size:18px;'>This web app uses machine learning to estimate your salary based on job details, skills, and company profile. It also forecasts your salary over time based on annual growth!</p>
    
    <h3 style='color:#ffaaff;'>✨ Features:</h3>
    <ul style='font-size:16px;'>
        <li>🎯 Real-time salary prediction using ML</li>
        <li>🧠 Inputs like job title, location, and tools</li>
        <li>📍 Tailored results by job type and company rating</li>
        <li>📈 Forecast your salary growth over years</li>
    </ul>
    """, unsafe_allow_html=True)

# 🔮 --- SALARY PREDICTION PAGE ---
elif page == "🔮 Predict Salary":
    st.markdown("""
    <div style='background:linear-gradient(to right, #2e003e, #3c096c); padding:20px; border-radius:15px;'>
        <h1 style='color:#ffb3ec; margin:0;'>💼 Predict Your Salary</h1>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 Enter Job Details")

    job_title = st.selectbox("Select Job Title", job_titles)
    job_state = st.selectbox("Select Job Location", job_states)
    rating = st.slider("Company Rating", 0.0, 5.0, 3.5, 0.1)
    age = st.slider("Company Age", 0, 150, 10)
    python = st.checkbox("Python")
    r = st.checkbox("R")
    spark = st.checkbox("Spark")
    aws = st.checkbox("AWS")
    excel = st.checkbox("Excel")

    input_data = {
        'Rating': rating,
        'age': age,
        'python_yn': int(python),
        'R_yn': int(r),
        'spark': int(spark),
        'aws': int(aws),
        'excel': int(excel),
    }

    for feature in model_features:
        if feature.startswith("Job Title_"):
            input_data[feature] = 1 if feature == f"Job Title_{job_title}" else 0
        elif feature.startswith("job_state_"):
            input_data[feature] = 1 if feature == f"job_state_{job_state}" else 0

    for feat in model_features:
        if feat not in input_data:
            input_data[feat] = 0

    input_df = pd.DataFrame([input_data])

    if st.button("🎯 Predict Salary"):
        with st.spinner("Calculating prediction..."):
            time.sleep(1)
            pred = model.predict(input_df)[0]
        st.success(f"💰 Estimated Salary: **${pred:,.2f}**")

# 📈 --- SALARY GROWTH PAGE ---
elif page == "📈 Salary Growth":
    st.markdown("""
        <div style='background:linear-gradient(to right, #0f2027, #2c5364); padding:20px; border-radius:15px;'>
            <h1 style='color:#00ffcc; margin:0;'>📈 Project Your Salary Growth</h1>
        </div>
    """, unsafe_allow_html=True)

    years = st.slider("Select Number of Years to Project", 1, 10, 5)
    base_salary = st.number_input("Enter Current Predicted Salary ($)", min_value=0.0, value=100.0)
    growth_rate = st.slider("Expected Annual Growth Rate (%)", 1.0, 20.0, 5.0)

    future_salaries = [round(base_salary * ((1 + growth_rate / 100) ** i), 2) for i in range(years + 1)]
    df_growth = pd.DataFrame({
        "Year": list(range(years + 1)),
        "Salary": future_salaries
    })

    # 🎨 Plotly Line Chart with style
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_growth["Year"],
        y=df_growth["Salary"],
        mode='lines+markers',
        line=dict(color='#ff4bff', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        name="Projected Salary"
    ))

    fig.update_layout(
        plot_bgcolor="#0f001a",
        paper_bgcolor="#0f001a",
        font=dict(color="#ffffff", size=14),
        xaxis_title="Year",
        yaxis_title="Salary ($)",
        title_font_color="#00ffcc",
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.success("✅ Growth projection complete!")

# 🗺️ --- SALARY BY STATE MAP ---
elif page == "📍 Salary by State":
    st.markdown("""
        <div style='background:linear-gradient(to right, #2c003e, #3c096c); padding:20px; border-radius:15px;'>
            <h1 style='color:#ffb3ec; margin:0;'>🗺️ Average Salary by U.S. State</h1>
        </div>
    """, unsafe_allow_html=True)

    # Sample data — replace with actual values if available
    state_salary_df = pd.DataFrame({
        'state': ['CA', 'TX', 'NY', 'IL', 'FL'],
        'salary': [130000, 110000, 125000, 100000, 105000]
    })

    fig = px.choropleth(
        state_salary_df,
        locations='state',
        locationmode='USA-states',
        color='salary',
        scope='usa',
        color_continuous_scale='Purples',
        labels={'salary': 'Average Salary'},
        title='📍 Average Salary by State'
    )

    fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='#0f001a',
        plot_bgcolor='#0f001a',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)
