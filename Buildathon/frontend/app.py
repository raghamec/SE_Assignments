import streamlit as st
import requests
import base64
import os

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="உழவுத்தளம் - வேளாண் சேவை", 
    page_icon="🌾", 
    layout="wide"
)

# Function to load local image from root folder and convert to Base64
def get_base64_image(file_prefix="Farmer_Img_3"):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        file_path = os.path.join(root_dir, file_prefix + ext)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if ext == ".png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
    return None

bg_data_uri = get_base64_image("Farmer_Img_3")

bg_style = f"""
    .stApp {{
        background: linear-gradient(rgba(10, 40, 15, 0.60), rgba(20, 55, 25, 0.65)), 
                    url("{bg_data_uri}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}
""" if bg_data_uri else """
    .stApp {{
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
    }}
"""

st.markdown(f"""
<style>
    {bg_style}
    
    /* Make Streamlit header transparent */
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}

    /* Green-themed sidebar */
    [data-testid="stSidebar"] {{
        background-color: #008704 !important;
        border-right: 2px solid #a5d6a7;
    }}
    
    [data-testid="stSidebarContent"] {{
        color: #ffffff;
        background-color: #008704;
    }}

    /* --- EXPANDER STYLING (Deep Forest Green Header & Soft Mint Body) --- */
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        background-color: #f1f8e9 !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
        background-color: #1b5e20 !important;
        color: #ffeb3b !important;
        font-weight: 800 !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid #81c784;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{
        background-color: #144a18 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] summary svg {{
        fill: #ffeb3b !important;
        color: #ffeb3b !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {{
        background-color: #f1f8e9 !important;
        color: #1b5e20 !important;
        padding: 12px !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] p,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] label {{
        color: #1b5e20 !important;
        font-weight: 600 !important;
    }}

    /* --- FILE UPLOADER DROPZONE & BUTTON STYLING --- */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background-color: #e8f5e9 !important;
        border: 2px dashed #2e7d32 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        transition: all 0.2s ease-in-out;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {{
        background-color: #dcf2de !important;
        border-color: #1b5e20 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] div,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: #1b5e20 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {{
        fill: #2e7d32 !important;
        color: #2e7d32 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
        background-color: #2e7d32 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 6px 14px !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {{
        background-color: #1b5e20 !important;
        color: #ffeb3b !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {{
        background-color: #ffffff !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 6px !important;
        color: #1b5e20 !important;
        padding: 4px 8px !important;
    }}
    
    /* FIXED CENTERED HEADER SECTION */
    .fixed-header {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: linear-gradient(rgba(15, 45, 20, 0.94), rgba(15, 45, 20, 0.88));
        backdrop-filter: blur(8px);
        padding: 12px 20px 10px 20px;
        border-bottom: 2px solid #81c784;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        text-align: center;
    }}

    /* TOP RIGHT WEATHER BOX */
    .weather-box {{
        position: absolute;
        top: 35px;
        right: 25px;
        background: rgba(255, 255, 255, 0.96);
        border: 2px solid #2e7d32;
        border-radius: 10px;
        padding: 8px 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.35);
        width: 300px;
        text-align: left;
        z-index: 1000;
    }}
    .weather-title {{
        color: #1b5e20;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 3px;
        border-bottom: 1px solid #c8e6c9;
        padding-bottom: 2px;
    }}
    .weather-info {{
        color: #2e7d32;
        font-size: 0.8rem;
        font-weight: 700;
        line-height: 1.8;
    }}

    .main-title {{
        color: #ffeb3b;
        font-weight: 900;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.95);
        margin: 0 auto;
        font-size: 1.9rem;
        letter-spacing: 0.5px;
    }}
    
    .subtitle {{
        color: #e8f5e9;
        text-align: center;
        font-size: 1rem;
        font-weight: 700;
        text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.9);
        margin: 2px auto 6px auto;
    }}
    
    .thirukural-box {{
        background-color: rgba(255, 255, 255, 0.96);
        border-left: 5px solid #2e7d32;
        border-right: 5px solid #2e7d32;
        padding: 5px 15px;
        border-radius: 8px;
        text-align: center;
        max-width: 680px;
        margin: 0 auto;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }}
    
    .thirukural-text {{
        color: #1b5e20;
        font-size: 0.85rem;
        font-style: italic;
        font-weight: 700;
        margin: 0;
    }}
    
    .block-container {{
        padding-top: 165px !important;
        padding-bottom: 110px !important;
    }}

    .chat-scroll-container {{
        max-height: calc(100vh - 320px);
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 10px;
    }}

    /* --- CLEAR BUTTON ("நீக்குக") STYLING --- */
    .main .stButton > button {{
        background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%) !important;
        color: #ffffff !important;
        border: 2px solid #ffeb3b !important;
        border-radius: 20px !important;
        padding: 6px 18px !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;
        transition: all 0.2s ease-in-out !important;
        float: right !important;
    }}
    .main .stButton > button:hover {{
        background: linear-gradient(135deg, #8e0000 0%, #b71c1c 100%) !important;
        color: #ffeb3b !important;
        transform: translateY(-2px) !important;
    }}
    
    /* --- DISTINCT THEME COLORS FOR USER & AI CHAT BUBBLES --- */
    [data-testid="stChatMessage"] {{
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22) !important;
    }}

    /* User Chat Bubble */
    [data-testid="stChatMessage"]:nth-of-type(odd) {{
        background: linear-gradient(135deg, #fffde7 0%, #fff9c4 100%) !important;
        border: 2px solid #fbc02d !important;
        border-left: 6px solid #f57f17 !important;
    }}
    [data-testid="stChatMessage"]:nth-of-type(odd) p,
    [data-testid="stChatMessage"]:nth-of-type(odd) div {{
        color: #3e2723 !important;
        font-weight: 600;
    }}

    /* AI Assistant Chat Bubble */
    [data-testid="stChatMessage"]:nth-of-type(even) {{
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%) !important;
        border: 2px solid #66bb6a !important;
        border-left: 6px solid #1b5e20 !important;
    }}
    [data-testid="stChatMessage"]:nth-of-type(even) p,
    [data-testid="stChatMessage"]:nth-of-type(even) li {{
        color: #1b5e20 !important;
    }}

    /* Avatar badge styling inside chat messages */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {{
        background-color: #ffffff !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }}

    /* --- BOTTOM CHAT INPUT BOX STYLING --- */
    [data-testid="stBottom"] > div {{
        background-color: rgba(15, 45, 20, 0.90) !important;
        backdrop-filter: blur(8px);
        border-top: 2px solid #81c784;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }}

    [data-testid="stChatInput"] {{
        background-color: #f1f8e9 !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: #1b5e20 !important;
        font-weight: 600 !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: #4e7a51 !important;
    }}

    [data-testid="stChatInput"] button {{
        color: #1b5e20 !important;
    }}
    [data-testid="stChatInput"] button:hover {{
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }}
</style>

<!-- Fixed Centered Header Section with Top-Right Weather Widget -->
<div class="fixed-header">
    <div class="weather-box">
        <div class="weather-title">🌤️ தமிழ்நாடு வானிலை</div>
        <div class="weather-info">
            🌡️ வெப்பநிலை: 31°C<br>
            🌧️ மழை வாய்ப்பு: மிதமானது (30%)<br>
            🌀 புயல் எச்சரிக்கை: இல்லை
        </div>
    </div>
    <h1 class="main-title" style="text-align: center; color: #ffeb3b;">🌾 உழவுத்தளம் </h1>
    <p class="subtitle">அரசு வேளாண் திட்டங்கள் உங்கள் கையில்... மானியமும் பயன்களும் இனி உங்கள் வயலில்...!</p>
    <div class="thirukural-box">
        <p class="thirukural-text">"உழுதுண்டு வாழ்வாரே வாழ்வார்மற் றெல்லாம் <br> தொழுதுண்டு பின்செல் பவர்" — திருவள்ளுவர்</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Sidebar with Expandable/Collapsible Upload Section
with st.sidebar:
    st.markdown("### ⚙️ கூட்டுச்சேகரம் பகுதி (Crowd-Sourcing)")
    
    with st.expander("📂 PDF ஆவணங்களைப் பதிவேற்றுக", expanded=True):
        st.write("விவசாய திட்டங்கள் குறித்த கையேடுகள் பகிரவும்.")
        
        uploaded_files = st.file_uploader(
            "PDF கோப்புகளைத் தேர்ந்தெடுக்கவும்", type=["pdf"], accept_multiple_files=True
        )
        
        if uploaded_files:
            current_file_names = {f.name for f in uploaded_files}
            
            if current_file_names != st.session_state.processed_files:
                with st.spinner("🌿 ஆவணங்கள் பகுப்பாய்வு செய்யப்பட்டு அட்டவணைப்படுத்தப்படுகின்றன..."):
                    files_payload = [
                        ("files", (file.name, file.getvalue(), "application/pdf"))
                        for file in uploaded_files
                    ]
                    response = requests.post(f"{BACKEND_URL}/upload", files=files_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"🌱 {data['message']} ({data['chunks_indexed']} பகுதிகள் சேமிக்கப்பட்டன)")
                        st.session_state.processed_files = current_file_names
                    else:
                        st.error(f"⚠️ பிழை: {response.text}")
                        
    st.markdown("---")
    st.markdown("**💡 குறிப்பு:** ஆங்கிலம், தமிழ் அல்லது Tanglish மொழிகளில் கேள்விகளைக் கேட்கலாம். பதில்கள் **தமிழில்** மட்டுமே வழங்கப்படும்!")

# Define Farmer & AI Avatars
USER_AVATAR = "👨‍🌾"
AI_AVATAR = "🌾"

# Scrollable Chat Container Wrapper Start
st.markdown('<div class="chat-scroll-container">', unsafe_allow_html=True)

# Display Chat History with Custom Avatars (Source section completely removed)
for msg in st.session_state.messages:
    avatar_icon = USER_AVATAR if msg["role"] == "user" else AI_AVATAR
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# Scrollable Chat Container Wrapper End
st.markdown('</div>', unsafe_allow_html=True)

# Right-Aligned "நீக்குக" (Clear Chat) Button above the Chat Input
_, clear_col = st.columns([5, 1])
with clear_col:
    if st.button("🗑️ நீக்குக", key="clear_chat_btn", help="உரையாடலை அழித்து புதிதாகத் தொடங்கவும்"):
        st.session_state.messages = []
        st.rerun()

# Chat Input in Tamil
if prompt := st.chat_input("அரசு திட்டங்கல் பற்றி இங்கே கேட்கவும்.. (குறிப்பு: ஆங்கிலம், தமிழ் அல்லது Tanglish மொழிகளில் கேள்விகளைக் கேட்கலாம்)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AI_AVATAR):
        with st.spinner("🔍 விவசாய ஆவணங்களைத் தேடுகிறது..."):
            res = requests.post(f"{BACKEND_URL}/ask", json={"question": prompt})
            if res.status_code == 200:
                data = res.json()
                answer = data["answer"]
                
                st.markdown(answer)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })
                st.rerun()
            else:
                st.error("⚠️ சேவையகத்துடன் (Backend) இணைப்பதில் தோல்வி.")