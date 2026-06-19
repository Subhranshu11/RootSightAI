import streamlit as st
from streamlit.components.v1 import html
import os
from groq import Groq

from scripts.query_engine import (
    analyze_incident,
    add_incident_to_knowledgebase,
    metadata
)

from scripts.dynamic_ingest import (
    build_dynamic_repository
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="RootSight AI",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# LOGIN SESSION
# -----------------------------------

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

TEAM_CORP_KEY = "VectorMinds"
PASSWORD = "$RG11"

if not st.session_state["authenticated"]:

    st.markdown("""
    <style>
    
    /* -----------------------------------
    HIDE STREAMLIT ELEMENTS
    ----------------------------------- */
    
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
    
    /* -----------------------------------
    FULL PAGE
    ----------------------------------- */
    
    html, body, .stApp{
        height:100vh;
        margin:0;
        padding:0;
    }
    
    .stApp{
        background: white;
    }
    
    .block-container{
        width:100%;
        height:100vh;
        padding:0 !important;
        margin:0 !important;
    }
    
    /* -----------------------------------
    SPLIT SCREEN LAYOUT
    ----------------------------------- */
    
    [data-testid="stHorizontalBlock"]{
        width:100%;
        min-height:100vh;
        align-items:center !important;
    }
    
    [data-testid="column"]{
        min-height:100vh;
    }
    
    [data-testid="column"]:first-child{
        display:flex;
        justify-content:center;
        align-items:center;
    }
    
    [data-testid="column"]:nth-child(2){
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
    }
    
    /* -----------------------------------
    WELCOME TEXT
    ----------------------------------- */
    
    .welcome-title{
        font-size:64px;
        font-weight:700;
        color: #ff6200;
    
        margin-bottom:0px;   /* was 40px */
        line-height:1;
    }
    
    .welcome-subtitle{
        font-size:17px;
        color:#9CA3AF;
    
        margin-top:0px;
        margin-bottom:30px;
    }
    
    /* -----------------------------------
    INPUTS
    ----------------------------------- */
    
    /* Outer Streamlit container */
    
    .stTextInput > div > div{
        background:white !important;
        border:none !important;
        box-shadow:none !important;
        border-radius:30px !important;
    }
    
    /* Actual input */
    
    div[data-testid="stTextInput"] input{
        background:#fcf5f0 !important;
        color:black !important;
    
        border:none !important;
        outline:none !important;
        box-shadow:none !important;
    
        border-radius:30px !important;
        height:58px !important;
    
        padding-left:22px !important;
    
        font-size:16px !important;
    }
    
    /* Focus state */
    
    div[data-testid="stTextInput"] input:focus{
        border:none !important;
        outline:none !important;
        box-shadow:none !important;
    }
    /* Username / Password Labels */

    label[data-testid="stWidgetLabel"]{
        color:black !important;
        font-size:15px !important;
        font-weight:500 !important;
    }
    /* -----------------------------------
    PASSWORD BOX
    ----------------------------------- */
    
    div[data-testid="stTextInput"]{
        border:none !important;
        
        box-shadow:none !important;
    }
    
    /* -----------------------------------
    BUTTON
    ----------------------------------- */
    /* Remember Me checkbox */

    div[data-testid="stCheckbox"] label{
        color:black !important;
        font-size:14px !important;
    }
    div[data-testid="stCheckbox"] p{
        color:black !important;
    }
    div[data-testid="stButton"] button{
        width:100%;
        border-radius:30px !important;
    
        height:58px !important;
    
        font-size:18px !important;
        font-weight:600 !important;
    
        background:#FF6200 !important;
        color:white !important;
    
        border:none !important;
    }
    
    div[data-testid="stButton"] button:hover{
        background:#e45700 !important;
    }
    /* RIGHT SIDE LOGIN PANEL */
    
    [data-testid="column"]:nth-child(2){
        padding-left:80px !important;
        padding-right:120px !important;
        box-sizing:border-box;
    }
    /* -----------------------------------
    IMAGE
    ----------------------------------- */
    
    img{
        display:block;
        margin:auto;
    }
    /* LOGO */

    [data-testid="column"]:nth-child(2) img{
        max-width:500px !important;
        margin-left:40px !important;
    }
    
    /* LOGIN PANEL */
    
    [data-testid="column"]:nth-child(3){
        padding-right:80px !important;
    }
    
    /* TITLE */
    
    .welcome-title{
        font-size:64px;
        font-weight:700;
        color:#ff6200;
        margin-bottom:0px;
    }
    /* Kill Streamlit input wrapper */
    
    div[data-baseweb="input"]{
        border:none !important;
        background:#fcf5f0 !important;
        box-shadow:none !important;
        border-radius:30px !important;
    }
    
    div[data-baseweb="input"] > div{
        border:none !important;
        background:#fcf5f0 !important;
        box-shadow:none !important;
        border-radius:30px !important;
    }
    
    /* Password field wrapper */
    
    div[data-baseweb="base-input"]{
        border:none !important;
        background:#fcf5f0 !important;
        box-shadow:none !important;
    }
    
    /* Remove white focus ring */
    
    
    </style>
    """, unsafe_allow_html=True)

    col0, col1, col2, col3 = st.columns([0.15, 1, 0.9, 0.15])

    with col1:
        st.image(
            "assets/ai_tree.png",
            width=600
        )
    
    with col2:
        st.markdown("""
        <div class="welcome-title">
            Welcome!
        </div>
        <div class="welcome-subtitle">
            Enterprise Operational Intelligence Platform
        </div>
        """, unsafe_allow_html=True)
    
        team_key = st.text_input(
            "Username",
            placeholder="Enter your username...",
            key="team_key"
        )
    
        password = st.text_input(
            "Password",
            placeholder="*****",
            type="password",
            key="password"
        )
        
        remember_me = st.checkbox(
            "Remember Me",
            value=True
        )
        
        login_clicked = st.button(
            "Get Set RootSight!",
            use_container_width=True
        )

        if login_clicked:

            if (
                team_key == TEAM_CORP_KEY
                and
                password == PASSWORD
            ):

                st.session_state["authenticated"] = True
                st.rerun()

            else:

                st.error(
                    "Invalid credentials"
                )
        st.caption(
            "RootSight AI v1.3 | VectorMinds"
        )
    st.stop()

# -----------------------------------
# ADAPTIVE CSS (STREAMLIT LIGHT/DARK)
# -----------------------------------

st.markdown("""
<style>

/* -----------------------------------
THEME VARIABLES
----------------------------------- */

:root {
    --resolve-color: #003B70;
}

/* Dark Theme */

@media (prefers-color-scheme: dark) {

    :root {
        --resolve-color: #4DA3FF;
    }

}

/* -----------------------------------
MAIN APP
----------------------------------- */

.stApp {
    font-family: "Segoe UI", sans-serif;
}

/* -----------------------------------
SIDEBAR
----------------------------------- */

section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.15);
}

/* Center the image in the sidebar */

[data-testid="stSidebar"] img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* -----------------------------------
TEXT AREA
----------------------------------- */

textarea {
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 15px !important;
}

/* -----------------------------------
BUTTONS
----------------------------------- */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3rem;
    font-weight: 600;
    background-color: #FF6200;
    color: white;
    border: none;
    transition: 0.3s;
}
div[data-testid="stButton"] button:hover{
        background:#e45700 !important;
    }

/* -----------------------------------
MAIN HEADER
----------------------------------- */

.main-header {
    font-size: 50px;
    font-weight: 700;
    margin-bottom: 0;
}

/* -----------------------------------
SUB HEADER
----------------------------------- */

.sub-header {
    color: inherit;
    opacity: 0.75;
    margin-top: 0px;
    margin-bottom: 30px;
    font-size: 16px;
}

/* -----------------------------------
WORKSPACE CARD
----------------------------------- */

.workspace-card {
    padding: 0px;
    border: none;
    background: transparent;
}

/* -----------------------------------
RCA OUTPUT
----------------------------------- */

.rca-box {
    padding: 24px;
    border-radius: 18px;
    border-left: 5px solid #FF6200;
    border-top: 1px solid rgba(128,128,128,0.15);
    border-right: 1px solid rgba(128,128,128,0.15);
    border-bottom: 1px solid rgba(128,128,128,0.15);
    line-height: 1.8;
    font-size: 15px;
    margin-top: 10px;
}

/* -----------------------------------
SECTION TITLE
----------------------------------- */

.section-title {
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 10px;
}

/* -----------------------------------
FOOTER
----------------------------------- */

.footer-text {
    text-align: center;
    opacity: 0.7;
    margin-top: 40px;
    font-size: 13px;
}

/* -----------------------------------
STATUS CARDS
----------------------------------- */

.status-card{
    border:1px solid rgba(128,128,128,0.15);
    border-radius:18px;
    padding:22px;

    text-align:center;

    background-color:rgba(255,255,255,0.02);

    transition:all 0.25s ease;
}

.status-card:hover{
    transform:translateY(-2px);
    border-color:#FF6200;
}

.status-label{
    font-size:13px;
    opacity:0.7;
    margin-bottom:10px;
    font-weight:500;
}

.status-value{
    font-size:30px;
    font-weight:700;
    color:#FF6200;
}

.status-live{
    font-size:22px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:

    st.markdown(
        """
        <div style='text-align:center;'>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1,4,1])

    with col2:
        st.image("assets/ai_tree.png", width=290)

    st.markdown(
        """
        <div style='text-align:center; margin-top:0px;'>
            <div style='font-size:14px; opacity:0.75; margin-top:0px; color:#5B6575;'>
                Enterprise Operational Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Enterprise Knowledge Workspace")

    uploaded_files = st.file_uploader(
        "Upload Knowledge Sources",
        type=[
            "csv",
            "xlsx",
            "json",
            "pdf",
            "docx",
            "pptx",
            "txt",
            "md",
            "log",
            "xml"
        ],
        accept_multiple_files=True
    )
    # -----------------------------------
    # SAVE UPLOADED FILES
    # -----------------------------------

    UPLOAD_FOLDER = "dynamic_workspace"

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    uploaded_count = 0

    if uploaded_files:

        for uploaded_file in uploaded_files:

            save_path = os.path.join(
                UPLOAD_FOLDER,
                uploaded_file.name
            )

            with open(save_path, "wb") as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            uploaded_count += 1


        try:

            build_dynamic_repository()
            import pickle

            with open(
                "dynamic_vectorstore/dynamic_metadata.pkl",
                "rb"
            ) as f:
        
                dynamic_chunks = pickle.load(f)
        
            st.session_state["dynamic_kb_active"] = True
        
            st.session_state["dynamic_chunk_count"] = len(
                dynamic_chunks
            )
            st.markdown(
                f"""
                <div style="
                    padding:12px;
                    border-radius:12px;
                    border-left:4px solid #FF6200;
                    background-color:rgba(255,98,0,0.08);
                    margin-top:10px;
                ">
                    <b>Enterprise Knowledge Source Activated</b><br>
                    {uploaded_count} document(s) indexed and available for RCA analysis
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception:

            st.error(
                "Knowledge workspace initialization failed."
            )

    st.divider()

    st.markdown("### Workspace")

    st.markdown("""
- Historical Correlation
- Operational Runbooks
- Enterprise Incident Memory
- RCA Knowledge Retrieval
""")

    st.divider()

    st.markdown("### Supported Operations")

    st.markdown("""
- SQL Alerts
- Oracle Incidents
- SAP BI Issues
- Azure Pipeline Issues
- Power BI Issues
""")

    st.divider()

    st.markdown(
        """
        <div style="
            text-align:center;
            opacity:0.75;
            font-size:15px;
            margin-top:10px;
            margin-bottom:10px;
        ">
            Team Name
            <br>
            <span style="
                color:#FF6200;
                font-weight:600;
                font-size:20px;
            ">
                🧠Vector Minds
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    if st.button(
        "Logout",
        use_container_width=True
    ):
    
        st.session_state["authenticated"] = False
    
        st.session_state.pop(
            "dynamic_kb_active",
            None
        )
    
        st.session_state.pop(
            "dynamic_chunk_count",
            None
        )
    
        st.rerun()
        
# -----------------------------------
# HEADER
# -----------------------------------

st.markdown("""
<div class="main-header">

<span style="color:#FF6200;">
    RootSight AI
</span>

</div>

<div class="sub-header">
Enterprise Operational Intelligence & RCA Workspace
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# HEALTH CHECKS
# -----------------------------------

# AI Engine Status

try:

    # Prefer the Streamlit secret, fall back to environment variable, and handle missing keys gracefully
    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    test_client = Groq(
        api_key=api_key
    )

    # Only attempt an API call if we have an API key
    if api_key:
        test_client.models.list()
        ai_status = "🟢 Active"
    else:
        ai_status = "🔴 Offline"

except Exception:

    ai_status = "🔴 Offline"

# -----------------------------------
# DYNAMIC STATUS CHECKS
# -----------------------------------

# AI Engine Status

try:
    ai_status = (
        "🟢 Active"
        if (st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY"))
        else "🔴 Offline"
    )
except:
    ai_status = "🟢 Active"

# -----------------------------------
# OPERATIONAL STATUS BAR
# -----------------------------------

knowledge_chunks = len(metadata)

if st.session_state.get("dynamic_kb_active", False):
    knowledge_chunks = st.session_state.get(
        "dynamic_chunk_count",
        len(metadata)
    )
    

documents_loaded = (
    len(os.listdir("dynamic_workspace"))
    if os.path.exists("dynamic_workspace")
    else 0
)

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:

    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">
            Context Articles
        </div>
        <div class="status-value">
            {knowledge_chunks}
        </div>
    </div>
    """,
    unsafe_allow_html=True)
with status_col2:

    st.markdown("""
    <div class="status-card">
        <div class="status-label">
            Knowledge Route
        </div>
        <div class="status-value">
            🟢 LIVE
        </div>
    </div>
    """,
    unsafe_allow_html=True)

with status_col3:
    st.markdown(f"""
    <div class="status-card">
        <div class="status-label">
            AI Engine
        </div>
        <div class="status-value">
            {ai_status}
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------
# INPUT SECTION
# -----------------------------------

st.markdown("""
<div class="section-title">
Enterprise Incident Input
</div>
""", unsafe_allow_html=True)

user_input = st.text_area(
    label="Incident Description",
    label_visibility="collapsed",
    height=180,
    key="incident_input",
    placeholder="""
Example:

SAP BI Launchpad not opening.
SQL Developer is not working.

"""
)

# -----------------------------------
# ENTER KEY SUBMISSION
# -----------------------------------

enter_pressed = html(
    """
    <script>

    const doc = window.parent.document;

    const textarea = doc.querySelector('textarea');

    textarea.addEventListener('keydown', function(event) {

        if (event.key === 'Enter' && !event.shiftKey) {

            event.preventDefault();

            const buttons = doc.querySelectorAll('button');

            buttons.forEach(btn => {

                if (btn.innerText.includes('RootSight Analyze')) {
                    btn.click();
                }

            });

        }

    });

    </script>
    """,
    height=0
)

analyze_clicked = st.button(
    "RootSight Analyze",
    use_container_width=True
)

# -----------------------------------
# INCIDENT ANALYSIS
# -----------------------------------

if analyze_clicked:

    if not user_input.strip():

        st.warning(
            "Please enter enterprise incident details."
        )

    else:

        with st.spinner(
            "Analyzing enterprise operational incident..."
        ):

            try:

                # -----------------------------------
                # ANALYZE INCIDENT
                # -----------------------------------

                retrieved_context = []

                result = analyze_incident(
                    user_input,
                    return_context=True
                )

                response = result["response"]
                import re

                display_response = response

                knowledge_source_display = (
                    "Uploaded Enterprise Documents"
                    if uploaded_files
                    else
                    "Historical Knowledge Base"
                )

                #display_response = re.sub(
                #    r"## Severity.*?(?=##|$)",
                #    "",
                #    display_response,
                #    flags=re.DOTALL
                #)

                display_response = re.sub(
                    r"## Affected Components.*?(?=##|$)",
                    "",
                    display_response,
                    flags=re.DOTALL
                )

                display_response = re.sub(
                    r"## Operational Insight.*?(?=##|$)",
                    "",
                    display_response,
                    flags=re.DOTALL
                )

                display_response = display_response.strip()

                retrieved_context = result.get(
                    "context",
                    []
                )

                # -----------------------------------
                # SCOPE RESTRICTION CHECK
                # -----------------------------------

                if "Scope Restriction Notice" in response:

                    st.warning(
                        "Query outside enterprise operational scope."
                    )

                    st.markdown(response)

                    st.stop()

                # -----------------------------------
                # DETECT SEVERITY
                # -----------------------------------
                
                #severity = "Medium"

                #if "Critical" in response:
                #    severity = "Critical"

                #elif "High" in response:
                #    severity = "High"

                #elif "Low" in response:
                #    severity = "Low"
                
                # -----------------------------------
                # HEADER
                # -----------------------------------

                st.markdown("## Incident Analysis")

                #st.caption(
                #    f"Incident ID: {incident_id}"
                #)

                # -----------------------------------
                # SEVERITY
                # -----------------------------------

                #if severity == "Critical":

                #    st.error(
                #        f"Severity Level: {severity}"
                #    )

                #elif severity == "High":

                #    st.warning(
                #        f"Severity Level: {severity}"
                #    )

                #elif severity == "Medium":

                #    st.info(
                #        f"Severity Level: {severity}"
                #    )

                #else:

                #    st.success(
                #        f"Severity Level: {severity}"
                #    )
                
                # -----------------------------------
                # KNOWLEDGE SOURCE
                # -----------------------------------

                st.success(
                    f"Knowledge Source: {knowledge_source_display}"
                )
                # -----------------------------------
                # RCA OUTPUT
                # -----------------------------------

                st.markdown(
                    f"""
<div class="rca-box">

{display_response}

</div>
""",
                    unsafe_allow_html=True
                )

                # -----------------------------------
                # ENTERPRISE CONTEXT VIEWER
                # -----------------------------------

                with st.expander(
                    "Retrieved Enterprise Context"
                ):

                    st.caption(
                        "Semantic operational knowledge retrieved from enterprise vector database"
                    )

                    if retrieved_context:

                        for i, chunk in enumerate(retrieved_context):

                            st.markdown(
                                f"### Context Chunk {i + 1}"
                            )

                            cleaned_chunk = chunk.replace(
                                "**",
                                ""
                            )

                            cleaned_chunk = cleaned_chunk.replace(
                                "severity: Low",
                                "severity: LOW"
                            )

                            cleaned_chunk = cleaned_chunk.replace(
                                "severity: Medium",
                                "severity: MEDIUM"
                            )

                            cleaned_chunk = cleaned_chunk.replace(
                                "severity: High",
                                "severity: HIGH"
                            )

                            cleaned_chunk = cleaned_chunk.replace(
                                "severity: Critical",
                                "severity: CRITICAL"
                            )

                            st.code(
                                cleaned_chunk[:2500],
                                language="yaml"
                            )

                    else:

                        st.info(
                            "No enterprise context retrieved."
                        )

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

# -----------------------------------
# FOOTER
# -----------------------------------

st.markdown("""
<div class="footer-text">
AI-Powered Enterprise Operational Intelligence Platform
</div>
""", unsafe_allow_html=True)
