import os
import time
import streamlit as st
from PIL import Image
from google import genai
from dotenv import load_dotenv

# --- Initialization ---
load_dotenv()

# Securely fetch API Key from .env
api_key = os.getenv("Google API KEY HERE") 
client = genai.Client(api_key=api_key)

@st.cache_data(show_spinner=False)
def get_gemini_response(user_text, _image, engineering_prompt):
    """
    Tries the most advanced 2026 models first. 
    Gemini 3 Flash is the current workhorse for multimodal tasks.
    """
    # Updated 2026 Model Order
    models_to_try = [
        "gemini-3-flash-preview",  # Fastest & most intelligent 2026 model
        "gemini-2.5-flash",        # Reliable high-speed fallback
        "gemini-2.0-flash"         # Legacy fallback (retiring soon)
    ]
    
    # Resize image to save Token Quota (Civil engineering photos are often massive)
    _image.thumbnail((512, 512)) 
    
    for model_name in models_to_try:
        try:
            prompt_parts = [engineering_prompt, _image, user_text]
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_parts
            )
            return response.text
            
        except Exception as e:
            # Handle Quota or Deprecation errors
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if model_name == models_to_try[-1]:
                    return "🛑 ALL MODELS EXHAUSTED: You've reached the daily limit. Please wait until midnight or switch to a paid plan."
                continue # Try the next model
            elif "404" in str(e):
                continue # Model might be deprecated/renamed, try next
            else:
                return f"An error occurred: {str(e)}"

# --- UI Setup ---
st.set_page_config(page_title="Civil Engineering Insight Studio", layout="centered")

st.header("🏗️ Civil Engineering Insight Studio")
st.subheader("Automated Structural Analysis")

# Sidebar Status
with st.sidebar:
    st.success("Connected to Gemini 3 API")
    st.info("Tip: Focus on specific areas like 'Check for corrosion' or 'Analyze joint stability'.")

input_text = st.text_input("Analysis Focus (e.g., 'Check for cracks'):", key="input")
uploaded_file = st.file_uploader("Upload Structure Photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Current Site Photo", use_container_width=True)

submit = st.button("Generate Professional Report")

# Refined Prompt for better 2026 model reasoning
engineering_prompt = """
You are a senior Civil Engineer. Analyze the provided image with high precision:
1. **Structural Classification**: Identify the specific category of structure.
2. **Material Health**: List materials and note any visible signs of wear, stress, or corrosion.
3. **Engineering Logic**: Describe the load-bearing mechanism visible.
4. **Safety Observations**: Highlight any immediate engineering concerns or defects.
Provide this as a professional site inspection report.
"""

if submit:
    if uploaded_file is not None:
        with st.spinner('Accessing Gemini 3 Intelligence...'):
            response = get_gemini_response(input_text, image, engineering_prompt)
            st.divider()
            st.markdown("### 📋 Structural Analysis Report")
            st.write(response)
            
            # Export Option
            st.download_button("Save Report", response, file_name="site_inspection.txt")
    else:

        st.warning("Please upload a site image to begin.")
