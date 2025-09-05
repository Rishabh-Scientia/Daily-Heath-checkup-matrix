import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import load_prompt
import plotly.express as px
import plotly.graph_objects as go
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate

load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
st.set_page_config(page_title="Daily Health Checkup Matrix", layout="wide")
st.set_page_config(
    page_title="Daily Health Checkup Matrix",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded"
)

# ----CSS Styling ---------
st.markdown("""
<style>
h1, h2, h3, h4 {
}
.stButton>button {
    background-color: #0B5345;
    color: white;
    height: 3em;
    width: 100%;
    border-radius: 10px;
    border: none;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #117A65;
    color: white;
}

.stRadio>div>label>div, .stSelectbox>div>div>div {
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --------- App Title ---------
st.title("🩺 Daily Health Checkup Matrix")
st.markdown(
    "<h4 style='color:#0B5345'>Fill in the following details for a personalized health analysis.</h4>",
    unsafe_allow_html=True
)

# --------- Sidebar ---------
st.sidebar.markdown(f"""
    <h2 style='text-align: center; color: black; font-weight:700'>
          Check Your Health Score Now! 💚
    </h2>
    <hr style='border:1px solid #0B5345'>
""", unsafe_allow_html=True)


st.write("Please fill the following questions for your daily health checkup.")

# ---------------------------
# Collecting Inputs (20 Questions)
# ---------------------------
responses = {}

# 1. Name
responses["Name"] = st.text_input("1. Your Name")

# 2. Age
responses["Age"] = st.number_input("2. Age", min_value=1, max_value=120, step=1)

# 3. Gender
responses["Gender"] = st.radio("3. Gender", ["Male", "Female", "Other"])

# 4. Height
responses["Height (cm)"] = st.slider("4. Height (in cm)", 100, 220, 170)

# 5. Weight
responses["Weight (kg)"] = st.slider("5. Weight (in kg)", 30, 150, 70)

# 6. Sleep hours
responses["Sleep Hours"] = st.slider("6. Average Sleep (hours)", 0, 12, 7)

# 7. Water intake
responses["Water Intake (L)"] = st.slider("7. Daily Water Intake (Liters)", 0, 10, 3)

# 8. Exercise
responses["Exercise"] = st.radio("8. Do you exercise daily?", ["Yes", "No", "Sometimes"])

# 9. Smoking habit
responses["Smoking"] = st.radio("9. Do you smoke?", ["Yes", "No", "Occasionally"])

# 10. Alcohol
responses["Alcohol"] = st.radio("10. Do you consume alcohol?", ["Yes", "No", "Occasionally"])

# 11. Stress level
responses["Stress Level"] = st.slider("11. Stress Level (1 = Low, 10 = High)", 1, 10, 5)

# 12. Diet
responses["Diet"] = st.radio("12. Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Keto", "Other"])

# 13. Fruits & Veggies
responses["FruitsVeg"] = st.slider("13. Daily Servings of Fruits & Vegetables", 0, 10, 3)

# 14. Screen time
responses["Screen Time"] = st.slider("14. Daily Screen Time (hours)", 0, 15, 5)

# 15. Family medical history
responses["Family History"] = st.multiselect(
    "15. Any Family Medical History?",
    ["Diabetes", "Hypertension (High BP)", "Heart Disease", "Asthma", "Cancer", "Obesity", "None"]
)

# 16. Allergies
responses["Allergies"] = st.text_area("16. Do you have any allergies? Describe if there is...")

# 17. Medication
responses["Medication"] = st.multiselect(
    "17. Are you taking any regular medication?",
    ["Blood Pressure", "Diabetes", "Thyroid", "Cholesterol", "Asthma", "Painkillers", "Vitamins/Supplements", "None"]
)

responses["Blood Pressure"] = st.radio("18. Do you have high/low BP?", ["Normal", "High", "Low"])

responses["Sugar"] = st.radio("19. Do you have diabetes?", ["No", "Yes, Type 1", "Yes, Type 2", "Prediabetic"])

responses["Cholesterol"] = st.radio("21. Have you ever had high cholesterol?", ["No", "Yes", "Not sure"])

responses["Activity Type"] = st.radio("22. What kind of physical activity do you do?", ["Walking", "Gym/Workout", "Yoga/Meditation", "Sports", "None"])

responses["Work Type"] = st.radio("23. What best describes your work?", ["Sedentary (desk job)", "Moderately active", "Physically active"])

responses["Mental Health"] = st.slider("24. Mental Health Status (1 = Poor, 10 = Excellent)", 1, 10, 6)

responses["Fast Food"] = st.radio("25. How often do you eat fast food?", ["Rarely", "1-2 times/week", "3-5 times/week", "Daily"])


responses["Caffeine"] = st.radio("26. How many cups of tea/coffee do you drink daily?", ["0", "1-2", "3-5", "More than 5"])

responses["Meal Frequency"] = st.slider(
    "27. How many meals do you have in a day?",
    1, 6, 3
)


responses["Diet Composition"] = st.multiselect(
    "Which types of food are included in your daily diet?",
    [   
        "Roti Dal Normal"
        "Fruits & Vegetables",
        "Whole Grains",
        "Protein (Meat, Eggs, Legumes)",
        "Dairy Products",
        "Fast Food / Junk Food",
        "Sugary Snacks / Drinks",
        "Healthy Fats (Nuts, Olive Oil, etc.)"
    ]
)

responses["Chronic Pain"] = st.radio("28. Do you suffer from chronic pain?", ["No", "Yes (Mild)", "Yes (Severe)"])

responses["Past Illness"] = st.text_area("29. Any past major illness/surgery?")

responses["Temperament"] = st.radio(
    "30. How often do you get angry or lose patience?",
    ["Rarely (Calm)", "Sometimes (Normal)", "Often (Short-tempered)", "Very Often (Easily Irritated)"]
)

responses["Chief Complaint"] = st.text_area(
    "31. What is your main health concern or discomfort today?"
)


# Submit Button

class HealthReport(BaseModel):
    # Core body metrics
    bmi: float = Field(description="Calculated Body Mass Index")
    bmi_category: str = Field(description="BMI Category: Underweight / Normal / Overweight / Obese")


    # Lifestyle & habits
    sleep_score: str = Field(description="Sleep quality e.g., '8/10 - Good'")
    hydration_score: str = Field(description="Hydration adequacy e.g., '6/10 - Average'")
    exercise_score: str = Field(description="Exercise routine e.g., '5/10 - Needs Improvement'")
    stress_score: str = Field(description="Stress level e.g., '7/10 - High'")
    diet_score: str = Field(description="Diet balance e.g., '9/10 - Excellent'")
    screen_time_risk: str = Field(description="Screen time impact e.g., '8/10 - High Risk'")

    # Medical risk areas
    family_history_risk: str = Field(description="Genetic/family risk e.g., '6/10 - Moderate'")
    allergy_risk: str = Field(description="Allergy impact e.g., '3/10 - Mild'")
    medication_risk: str = Field(description="Medication risk e.g., '5/10 - Moderate'")
    blood_pressure_status: str = Field(description="BP status: Normal / High / Low")
    diabetes_risk: str = Field(description="Diabetes risk e.g., '0/10 - None', '8/10 - High'")
    cholesterol_risk: str = Field(description="Cholesterol risk e.g., '7/10 - High'")
    heart_health_score: str = Field(description="Heart health e.g., '6/10 - Average'")
    immunity_score: str = Field(description="Immunity strength e.g., '8/10 - Strong'")

    # Lifestyle/environment extras
    caffeine_score: str = Field(description="Caffeine intake e.g., '4/10 - Acceptable'")
    sunlight_score: str = Field(description="Sunlight exposure e.g., '7/10 - Adequate'")
    chronic_pain_score: str = Field(description="Chronic pain level e.g., '2/10 - Low'")
    mental_health_score: str = Field(description="Mental health wellbeing e.g., '9/10 - Excellent'")
    fast_food_score: str = Field(description="Fast food consumption e.g., '6/10 - Frequent'")

    # Overall analysis
    lifestyle_score: str = Field(description="Lifestyle wellness rating e.g., '7/10 - Balanced'")
    improvement_plan: str = Field(description="3–5 key short steps for health improvement")
    # Risk & overall
    risk_score: str = Field(description="Overall health risk score out of 10 with label, e.g., '7/10 - Moderate risk'")
    final_report: str = Field(description="One line health summary")
    Heath_number: float = Field(description="give overall score of helth after analysis of all parameters, '60/100'")

parser = PydanticOutputParser(pydantic_object=HealthReport)
#------Prompt templat----00
template = """
You are a professional health advisor AI.
You will receive a dictionary of health responses from a user.

The dictionary: {user_responses}

Your tasks:
1. Calculate BMI = Weight(kg) / (Height(m))^2  
2. Classify BMI into categories.  
3. Analyze sleep, hydration, exercise, stress, diet, screen time, family history, allergies, medication, BP, and diabetes risks.  
4. Provide detailed remarks for each health aspect.  
5. Suggest cures and improvement steps.  
6. Give a final summary in one line.  

Return ONLY a JSON object strictly in this format:
{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["user_responses"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
#---------New Prompt Template-01-------
analysis_template = PromptTemplate(
    template="""
You are a health analysis expert.  
You will receive structured patient responses.  
Your task is to calculate and return a JSON object with health analysis scores across multiple criteria.

### Rules:
- Always give numeric scores out of 10 first, followed by a label (e.g., "7/10 - Moderate").
- Use only the fields listed below.
- Do not add extra fields.
- Ensure clarity, concise descriptions, and medical accuracy.

### Fields Required:
# Core body metrics
- bmi: float
- bmi_category: str

# Lifestyle & habits
- sleep_score: str
- hydration_score: str
- exercise_score: str
- stress_score: str
- diet_score: str
- screen_time_risk: str

# Medical risk areas
- family_history_risk: str
- allergy_risk: str
- medication_risk: str
- blood_pressure_status: str
- diabetes_risk: str
- cholesterol_risk: str
- heart_health_score: str
- immunity_score: str

# Lifestyle/environment extras
- caffeine_score: str
- sunlight_score: str
- chronic_pain_score: str
- mental_health_score: str
- fast_food_score: str

# Overall analysis
- lifestyle_score: str
- improvement_plan: str
- risk_score: str
- final_report: str

### Patient Responses:
{analysed_responses}

### Your Output (Valid JSON only):
""",
    input_variables=["analysed_responses"]
)
#---------New Prompt Template-02-------
template2 = """
You are a professional health advisor AI.

You will receive a dictionary of a person's health scores as input:

{health_scores}

Your tasks:
1. Analyze each score and understand the overall health condition.
2. Generate a **well-written summary** of the person's health.
3. Suggest **3-5 improvement steps**.
4. Provide **diet recommendations** better diet list to improve if needed.
5. Provide **physical activity/exercise recommendations**. list to improve if needed.
6. Provide additional **lifestyle tips** for better overall health.

Return ONly in heading than point forms in short form each task only 2, 3 point in point wise of one or two lines length form  etc.:
"""
prompt2 = PromptTemplate(
    template=template2,
    input_variables=["health_scores"]
)


# SUBMIT BUTTON 
if st.button("Generate Health Report"):
    st.subheader("📊 User Responses")
    df_user = pd.DataFrame(list(responses.items()), columns=["Question", "Answer"])
    st.dataframe(df_user, height=400)

    _input = prompt.format_prompt(user_responses=responses)
    with st.spinner(" ## Analyzing health report with AI..."):
        raw_output = model.invoke(_input.to_string())
        try:
            report = parser.parse(raw_output.content)
            report_dict = report.dict()
            analysis_scores = report_dict
        except Exception as e:
            st.error(f"Parsing error: {e}")
            st.stop()

    # Health Score Sidebar
    if report_dict["Heath_number"] >= 80:
        color = "green"
        status = "Excellent"
    elif report_dict["Heath_number"] >= 60:
        color = "orange"
        status = "Good"
    else:
        color = "red"
        status = "Poor"
    st.sidebar.success("✅ Health Report Generated Successfully!")
    st.sidebar.markdown(f"""
    <h1 style='text-align: center; color: {color}; font-size: 40px; font-weight:700'>
    Your Score: {report_dict["Heath_number"]}/100 ({status})
    </h1>
    """, unsafe_allow_html=True)

    st.subheader("🧾 AI Health Analysis")
    df_report = pd.DataFrame(list(report_dict.items()), columns=["Parameter", "Analysis"])
    st.dataframe(df_report, height=500)

    def extract_score(value: str) -> int:
        try:
            return int(value.split("/")[0])
        except:
            return 0

    scores = {k: extract_score(v) for k, v in analysis_scores.items()}

    # Lifestyle & Habits
    df1 = pd.DataFrame({
        "Criteria": ["Sleep", "Exercise", "Diet", "Stress"],
        "Score": [scores["sleep_score"], scores["exercise_score"], scores["diet_score"], scores["stress_score"]]
    })
    fig1 = px.bar(df1, x="Criteria", y="Score", text="Score", color="Score",
                  color_continuous_scale=px.colors.sequential.Teal, title="Lifestyle & Habits")
    st.plotly_chart(fig1, use_container_width=True)

    # Medical Risk
    df2 = pd.DataFrame({
        "Criteria": ["Diabetes", "Cholesterol", "Heart Health"],
        "Score": [scores["diabetes_risk"], scores["cholesterol_risk"], scores["heart_health_score"]]
    })
    fig2 = px.pie(df2, names="Criteria", values="Score", title="Medical Risk Distribution",
                  color_discrete_sequence=px.colors.sequential.Agsunset)
    st.plotly_chart(fig2, use_container_width=True)

    # Mental & Immunity
    df3 = pd.DataFrame({
        "Criteria": ["Mental Health", "Immunity", "Stress"],
        "Score": [scores["mental_health_score"], scores["immunity_score"], scores["stress_score"]]
    })
    fig3 = px.line(df3, x="Criteria", y="Score", markers=True, title="Mental & Immunity Trends",
                   line_shape='spline', color_discrete_sequence=['purple'])
    st.plotly_chart(fig3, use_container_width=True)

    # Overall Health
    df4 = pd.DataFrame({
        "Criteria": ["Lifestyle Score", "Overall Risk"],
        "Score": [scores["lifestyle_score"], scores["risk_score"]]
    })
    fig4 = px.bar(df4, x="Criteria", y="Score", text="Score", color="Score",
                  color_continuous_scale=px.colors.sequential.Magenta, title="Overall Health Summary")
    st.plotly_chart(fig4, use_container_width=True)

    # Health Suggestions
    with st.spinner("Collecting Data for Better Analysis..."):
        st.subheader("💡 Health Suggestions & Recommendations")
        llm_input = prompt2.format(health_scores=analysis_scores)
        response2 = model.invoke(llm_input)
        st.markdown(response2.content)
