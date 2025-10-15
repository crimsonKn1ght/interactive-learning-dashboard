# pages/career_coach.py
import io
import time
import streamlit as st
from app.services.auth_manager import save_target_profile, load_target_profile
from app.services.resume_parser import parse_and_save_text
from app.agents.orchestrator import run_agentic_pipeline
 
 
# ============================================================================
# AUTHENTICATION CHECK
# ============================================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/login.py")
 
 
# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    div.stButton > button:first-child,
    div.stFormSubmitButton > button:first-child {
        background-color: #1c7ed6;
        color: white;
        border: none;
        border-radius: 6px;
        height: 2.8em;
        font-weight: 500;
    }
    div.stButton > button:first-child:hover,
    div.stFormSubmitButton > button:first-child:hover {
        background-color: #1864ab;
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
 
 
# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown("### User Profile")
    st.write(f"**Username:** {st.session_state.username}")
    st.divider()
   
    if st.button("Logout", width='stretch'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
 
 
# ============================================================================
# PAGE HEADER
# ============================================================================
st.title("Career Goals & Target Profile")
st.caption("Define your target role, skills, and upload your resume for personalized analysis")
st.divider()
 
 
# ============================================================================
# LOAD TARGET PROFILE FROM DATABASE
# ============================================================================
profile = load_target_profile(st.session_state.username)
 
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0
 
 
# ============================================================================
# STATIC OPTIONS CONFIGURATION
# ============================================================================
ALL_ROLES = [
    "Select Target Role",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Engineer",
    "AI Researcher",   # change JSON key from ML Researcher → AI Researcher
    "Software Developer",
    "Full Stack Developer",
    "Product Manager",
    "DevOps Engineer",
    "Cloud Architect",  # add this to JSON
    "Cybersecurity Specialist",  # add this to JSON
    "BI Developer",
    "Prompt Engineer / GenAI Specialist"  # add this to JSON
]
 
 
# Structured taxonomy of skills
SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "R", "Java", "C++", "JavaScript", "SQL", "Scala"
    ],
    "Machine Learning & AI": [
        "Machine Learning", "Deep Learning", "Natural Language Processing (NLP)",
        "Generative AI", "Computer Vision", "Reinforcement Learning",
        "Feature Engineering", "Model Deployment", "MLOps"
    ],
    "Data Engineering": [
        "ETL", "Data Pipelines", "Apache Spark", "Kafka",
        "Hadoop", "Data Warehousing", "Data Wrangling"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP",
        "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"
    ],
    "Data Visualization & BI": [
        "Power BI", "Tableau", "Excel", "Matplotlib", "Seaborn", "Plotly", "Dash"
    ],
    "Frameworks & Libraries": [
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras",
        "Pandas", "NumPy", "OpenCV", "NLTK", "Hugging Face Transformers"
    ],
    "Software Development": [
        "React", "Node.js", "Flask", "Django", "Git", "APIs", "Agile Methodology"
    ],
    "Other Technical Skills": [
        "Statistics", "Data Analysis", "Big Data", "Prompt Engineering",
        "Cybersecurity", "System Design"
    ]
}
 
# Flatten taxonomy with category prefix for UI
FLATTENED_SKILLS = []
for category, skills in SKILL_TAXONOMY.items():
    FLATTENED_SKILLS.extend([f"{category}: {skill}" for skill in skills])
 
# Role → Skills map aligned to taxonomy
ROLE_SKILLS_MAP = {
    "Data Analyst": [
        "Programming Languages: SQL", "Programming Languages: Python",
        "Data Visualization & BI: Power BI", "Data Visualization & BI: Tableau",
        "Data Visualization & BI: Excel", "Other Technical Skills: Statistics"
    ],
    "Data Scientist": [
        "Programming Languages: Python", "Machine Learning & AI: Machine Learning",
        "Machine Learning & AI: Deep Learning", "Machine Learning & AI: Natural Language Processing (NLP)",
        "Machine Learning & AI: Feature Engineering", "Frameworks & Libraries: Scikit-learn",
        "Frameworks & Libraries: Pandas", "Frameworks & Libraries: NumPy"
    ],
    "Machine Learning Engineer": [
        "Programming Languages: Python", "Machine Learning & AI: Deep Learning",
        "Frameworks & Libraries: TensorFlow", "Frameworks & Libraries: PyTorch",
        "Machine Learning & AI: MLOps", "Machine Learning & AI: Model Deployment",
        "Cloud & DevOps: AWS", "Cloud & DevOps: Azure", "Cloud & DevOps: GCP",
        "Cloud & DevOps: Docker", "Cloud & DevOps: Kubernetes", "Cloud & DevOps: CI/CD"
    ],
    "Data Engineer": [
        "Programming Languages: SQL", "Programming Languages: Python",
        "Data Engineering: ETL", "Data Engineering: Data Pipelines",
        "Data Engineering: Apache Spark", "Data Engineering: Kafka",
        "Cloud & DevOps: AWS", "Cloud & DevOps: Docker", "Cloud & DevOps: Kubernetes"
    ],
    "AI Researcher": [
        "Programming Languages: Python", "Machine Learning & AI: Deep Learning",
        "Machine Learning & AI: Generative AI", "Machine Learning & AI: Natural Language Processing (NLP)",
        "Frameworks & Libraries: PyTorch", "Machine Learning & AI: Computer Vision",
        "Machine Learning & AI: Reinforcement Learning", "Other Technical Skills: Statistics"
    ],
    "Software Developer": [
        "Programming Languages: Python", "Programming Languages: JavaScript",
        "Software Development: React", "Software Development: Node.js",
        "Software Development: Git", "Software Development: APIs",
        "Software Development: Agile Methodology"
    ],
    "Full Stack Developer": [
        "Programming Languages: JavaScript", "Programming Languages: Python",
        "Software Development: React", "Software Development: Node.js",
        "Software Development: Django", "Software Development: Flask",
        "Programming Languages: SQL", "Software Development: Git"
    ],
    "Prompt Engineer / GenAI Specialist": [
        "Other Technical Skills: Prompt Engineering", "Machine Learning & AI: Generative AI",
        "Machine Learning & AI: Natural Language Processing (NLP)", "Programming Languages: Python",
        "Frameworks & Libraries: Hugging Face Transformers"
    ],
    "Select Target Role": FLATTENED_SKILLS
}
 
LEARNING_MODES = ["Self-paced", "Mentor-led", "Bootcamp", "Hybrid"]
TIMEFRAMES = ["3 months", "6 months", "1 year", "Flexible"]
 
 
# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def normalize_skill(skill: str) -> str:
    return skill.strip()
 
 
def merge_skill_lists(*skill_lists):
    merged = set()
    for skill_list in skill_lists:
        if skill_list:
            merged.update(skill_list)
    return sorted(merged)
 
 
# ============================================================================
# PREPARE SKILL OPTIONS WITH STORED CUSTOM SKILLS
# ============================================================================
stored_current_skills = profile.get("current_skills", [])
stored_target_skills = profile.get("target_skills", [])
 
custom_current_skills = [s for s in stored_current_skills if s not in FLATTENED_SKILLS]
custom_target_skills = [s for s in stored_target_skills if s not in FLATTENED_SKILLS]
 
all_current_skills = merge_skill_lists(FLATTENED_SKILLS, custom_current_skills)
all_target_skills = merge_skill_lists(
    ROLE_SKILLS_MAP.get(profile.get("target_role", "Select Target Role"), FLATTENED_SKILLS),
    custom_target_skills
)
 
 
# ============================================================================
# SET DEFAULT VALUES FROM DATABASE
# ============================================================================
default_target_role = profile.get("target_role", "Select Target Role")
default_motivation = profile.get("motivation", "")
default_learning_mode = profile.get("learning_mode", "Self-paced")
default_timeframe = profile.get("timeframe", "6 months")
default_custom_timeframe = profile.get("custom_timeframe_months", "")
 
role_index = ALL_ROLES.index(default_target_role) if default_target_role in ALL_ROLES else 0
learning_index = LEARNING_MODES.index(default_learning_mode) if default_learning_mode in LEARNING_MODES else 0
 
timeframe_option = "Flexible" if default_timeframe == "Flexible" else default_timeframe
timeframe_index = TIMEFRAMES.index(timeframe_option) if timeframe_option in TIMEFRAMES else 1
 
 
# ============================================================================
# MAIN CAREER GOALS FORM
# ============================================================================
form_key = f"career_goals_form_{st.session_state.form_key_counter}"
 
with st.form(form_key, clear_on_submit=False):
    col_left, col_right = st.columns(2)
   
    # ========== LEFT COLUMN: Career Direction ==========
    with col_left:
        st.subheader("Career Direction")
        target_role = st.selectbox("Target Role", ALL_ROLES, index=role_index)
        motivation = st.text_area("Career Motivation", value=default_motivation, height=150)
        st.markdown("### Learning Preferences")
        learning_mode = st.selectbox("Preferred Learning Mode", LEARNING_MODES, index=learning_index)
        selected_timeframe_option = st.selectbox("Expected Timeframe", TIMEFRAMES, index=timeframe_index)
        if selected_timeframe_option == "Flexible":
            custom_timeframe_months = st.number_input(
                "Specify timeframe (months)", min_value=1, max_value=60,
                value=int(default_custom_timeframe) if default_custom_timeframe else 12
            )
            final_timeframe = "Flexible"
        else:
            final_timeframe = selected_timeframe_option
            custom_timeframe_months = None
   
    # ========== RIGHT COLUMN: Skills Assessment ==========
    with col_right:
        st.subheader("Skills Assessment")
        st.markdown("**Current Skills**")
        selected_current_skills = st.multiselect(
            "Select your current skills",
            all_current_skills,
            default=stored_current_skills,
            label_visibility="collapsed"
        )
        new_current_skill = st.text_input("Add custom current skill", key="new_current_skill")
        st.markdown("---")
        st.markdown("**Target Skills to Learn**")
        role_specific_skills = ROLE_SKILLS_MAP.get(target_role, FLATTENED_SKILLS)
        all_target_skills_for_role = merge_skill_lists(role_specific_skills, custom_target_skills)
        selected_target_skills = st.multiselect(
            "Skills to learn or improve",
            all_target_skills_for_role,
            default=stored_target_skills,
            label_visibility="collapsed"
        )
        new_target_skill = st.text_input("Add custom target skill", key="new_target_skill")
   
    # Resume upload section
    st.divider()
    st.subheader("Upload Resume")
    uploaded_resume = st.file_uploader("Select Resume File", type=["pdf", "docx"], label_visibility="collapsed")
    if uploaded_resume is None and profile.get("resume_filename"):
        st.info(f"Using previously uploaded: **{profile.get('resume_filename')}**")
   
    has_resume = uploaded_resume or profile.get("resume_parsed_text")
    button_text = "Generate Skill Analysis" if has_resume else "Save Career Goals"
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        submitted = st.form_submit_button(button_text, width='stretch')
 
 
# ============================================================================
# FORM SUBMISSION HANDLER
# ============================================================================
if submitted:
   
    # Handle custom skill addition
    if new_current_skill.strip() or new_target_skill.strip():
       
        # Load existing profile to merge with
        existing_profile = load_target_profile(st.session_state.username)
       
        # Start with existing data
        updated_profile = {
            "target_role": existing_profile.get("target_role"),
            "motivation": existing_profile.get("motivation"),
            "current_skills": existing_profile.get("current_skills", []).copy(),
            "target_skills": existing_profile.get("target_skills", []).copy(),
            "learning_mode": existing_profile.get("learning_mode"),
            "timeframe": existing_profile.get("timeframe"),
            "custom_timeframe_months": existing_profile.get("custom_timeframe_months"),
            "resume_parsed_text": existing_profile.get("resume_parsed_text"),
            "resume_filename": existing_profile.get("resume_filename"),
            "analysis_output": existing_profile.get("analysis_output")
        }
       
        # Add new current skill
        if new_current_skill.strip():
            normalized_current = normalize_skill(new_current_skill)
            if normalized_current not in updated_profile["current_skills"]:
                updated_profile["current_skills"].append(normalized_current)
       
        # Add new target skill
        if new_target_skill.strip():
            normalized_target = normalize_skill(new_target_skill)
            if normalized_target not in updated_profile["target_skills"]:
                updated_profile["target_skills"].append(normalized_target)
       
        # Save complete profile
        success, message = save_target_profile(st.session_state.username, updated_profile)
       
        if success:
            st.success("Custom skills added successfully!")
            st.session_state.form_key_counter += 1
            time.sleep(0.5)
            st.rerun()
        else:
            st.error(f"Failed to add custom skills: {message}")
   
    # Handle main form submission
    elif target_role != "Select Target Role":
       
        # Parse resume if newly uploaded
        resume_parsed_text = profile.get("resume_parsed_text")
        resume_filename = profile.get("resume_filename")
       
        if uploaded_resume is not None:
            try:
                # Parse resume and save text
                txt_path = parse_and_save_text(uploaded_resume)
               
                # Read parsed text
                with open(txt_path, 'r', encoding='utf-8') as f:
                    resume_parsed_text = f.read()
               
                resume_filename = uploaded_resume.name
                st.success(f"Resume parsed: {resume_filename}")
               
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                resume_parsed_text = None
                resume_filename = None
       
        # Prepare complete profile data
        updated_profile = {
            "target_role": target_role,
            "motivation": motivation,
            "current_skills": selected_current_skills,
            "target_skills": selected_target_skills,
            "learning_mode": learning_mode,
            "timeframe": final_timeframe,
            "custom_timeframe_months": custom_timeframe_months,
            "resume_parsed_text": resume_parsed_text,
            "resume_filename": resume_filename,
            "analysis_output": profile.get("analysis_output")  # Preserve existing analysis
        }
       
        # Save to database
        success, message = save_target_profile(st.session_state.username, updated_profile)
       
        if not success:
            st.error(f"Failed to save profile: {message}")
        else:
            # If resume exists, run AI analysis
            if resume_parsed_text:
                try:
                    status_placeholder = st.empty()
                   
                    analysis_steps = [
                        "Analyzing your profile...",
                        "Analyzing your skills...",
                        "Generating personalized roadmap..."
                    ]
                   
                    for step in analysis_steps:
                        status_placeholder.info(step)
                        time.sleep(5)
                   
                    # Prepare pipeline input
                    pipeline_input = {
                        "role": profile.get("current_role", ""),  # ✅ current role from profile
                        "target_role": target_role,
                        "current_skills": selected_current_skills,
                        "target_skills": selected_target_skills,
                        "experience": profile.get("experience", "N/A"),  # ✅ ensure experience is passed
                        "learning_mode": learning_mode,
                        "motivation": motivation,
                        "timeframe": final_timeframe,
                    }
                                       
                    # Run AI analysis pipeline
                    resume_path_for_pipeline = txt_path if uploaded_resume else "data/text.txt"
 
                    # If no new upload but we have saved text, write it back to file
                    if not uploaded_resume and profile.get("resume_parsed_text"):
                        with open(resume_path_for_pipeline, "w", encoding="utf-8") as f:
                            f.write(profile["resume_parsed_text"])
 
                    context = run_agentic_pipeline(
                        pipeline_input,
                        resume_text_path=resume_path_for_pipeline,
                        use_cache=False,
                        force_refresh=True
                    )
 
 
                   
                    # Save analysis output to profile
                    updated_profile["analysis_output"] = context
                    save_target_profile(st.session_state.username, updated_profile)
                   
                    # Store analysis results in session
                    st.session_state.analysis = context
                   
                    # Redirect to dashboard
                    st.switch_page("pages/analysis_dashboard.py")
               
                except Exception as e:
                    st.error("Error analyzing resume")
                    st.exception(e)
           
            else:
                st.success("Career goals saved successfully!")
                st.info("Upload your resume anytime to generate personalized skill analysis")
   
    else:
        st.warning("Please select a target role before proceeding")
 
