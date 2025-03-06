import streamlit as st
import pandas as pd
import google.generativeai as genai
import os  # Import the os module
from typing import Generator


st.set_page_config(page_icon="🏋🏽", layout="wide",
                   page_title="Training Plan Assistant")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon("🏋🏽Training Program Assistant🏋🏽")

st.divider()

# --- Helper Functions ---
@st.cache_data()
def load_data(sheet_url):
    csv_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(csv_url)
    return df

def dataframe_to_csv_string(df):
    """Converts a pandas DataFrame to a CSV string."""
    return df.to_csv(index=False)

def generate_response(csv_string, question, api_key, model_name = "gemini-2.0-pro-exp-02-05"):
    """Generates a response from Google AI Studio using the CSV data and question."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)  # Or your preferred model

        # Construct the prompt.  Include the CSV data directly.
        prompt = f"""
        You are a personal training assistant who helps create workouts based on CSV data of available movements. 
        Do not suggest movements outside of the given CSV data unless the instructions from the personal trainer explicitly ask for it.
        Return the program in a table then provide 1-2 sentences explaining the program below the table. Return the table prior to any text.

        Here is the CSV data of movements:
        ```csv
        {csv_string}
        ```

        The program design instructions from the personal trainer are as follows: {question}
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during generation: {e}"  # Return the error message

# --- Main App ---
def main():
    tab1, tab2 = st.tabs(["Generate Training Plan", "Table of Exercises"])
    with tab1:
        
        # 1. Google Sheet URL Input
        sheet_url = st.secrets.get("google_sheet_url")
        api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

        if not api_key:
            st.warning("Error with Google AI Studio API Key.")
            st.stop()
        available_models = [
        "gemini-2.0-pro-exp-02-05",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp"
        ]
        selected_model_name = st.selectbox("Select a Generative Model:", available_models)

        # 3. Load Data (if URL is provided)
        if sheet_url:
            df = load_data(sheet_url)
            # 4. Question Input
            question = st.text_area("Provide Workout Programming Details:",
                                    placeholder="Enter your workout plan generation guidelines...",
                                    height = 150)

            # 5. Generate and Display Response (if question is provided)
            if question:
                csv_string = dataframe_to_csv_string(df)
                with st.spinner("Generating response..."):  # Show a spinner
                    response = generate_response(csv_string, question, api_key, selected_model_name)
                st.write("## Response from Training Assistant")
                st.write(response)
        else:
            st.warning("Error with Google Sheet connection")
            st.stop()

    with tab2:
       st.dataframe(df)
        
if __name__ == "__main__":
    main()

 # --- Sidebar Instructions ---
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("""Provide details for the training assistant to generate a workout plan. \n
**Example**: Create a 6 week program with 3 workouts each week. One workout should use pull movements, one from upper body, two from lower body and one core movement. Day 2 should use push movements,
                    2 for the lower body and and one for the upper body. Day 3 should be a combination of push and pull movements from the upper and lower body with 2 core components.
                    We want to emphasize hypertrophy in this program. Reps should be based on the percentage of one rep max. 
""")
