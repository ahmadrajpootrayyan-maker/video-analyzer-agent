import streamlit as st
import os
from dotenv import load_dotenv
import video_processor
import ai_analyst

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="VisionAI - Multimodal Video Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Apply custom font */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Title Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }
    
    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Glassmorphic Metrics */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.3);
    }
    
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #a855f7;
        margin-bottom: 4px;
    }
    
    .metric-lbl {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Custom button styling */
    div.stButton > button {
        background: linear-gradient(135deg, #a855f7 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.25) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45) !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Chat history message styling */
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    
    /* Frame gallery border design */
    .frame-container {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
        background: rgba(15, 23, 42, 0.4);
        padding: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .frame-container:hover {
        border-color: #a855f7;
        transform: scale(1.02);
    }
    
    .frame-cap {
        margin-top: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "frames" not in st.session_state:
    st.session_state.frames = None
if "analysis_output" not in st.session_state:
    st.session_state.analysis_output = None
if "analysis_mode" not in st.session_state:
    st.session_state.analysis_mode = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "report"

# Sidebar Content
with st.sidebar:
    st.markdown("### 🎬 VisionAI Settings")
    st.markdown("---")
    
    # Model configuration
    model_name = st.selectbox(
        "🧠 AI Model",
        ["gemini-2.5-flash", "gemini-1.5-flash"],
        index=0,
        help="Select the Gemini model to use. Gemini 2.5 Flash is highly recommended for speed and detail."
    )
    
    # API Key Handling
    env_key = os.environ.get("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        value=env_key,
        type="password",
        help="If not provided, falls back to the GEMINI_API_KEY environment variable."
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Video Settings")
    
    # Frame extraction rate
    interval_seconds = st.slider(
        "⏱️ Frame Extraction Rate",
        min_value=0.5,
        max_value=10.0,
        value=3.0,
        step=0.5,
        help="How frequently (in seconds) to extract a frame from the video."
    )
    
    # Max image width for upload
    max_frame_width = st.slider(
        "📏 Frame Target Width (px)",
        min_value=200,
        max_value=1280,
        value=640,
        step=40,
        help="Resize frames to this width before sending to AI to optimize speed and API costs."
    )
    
    st.markdown("---")
    st.markdown("### 🔍 Analysis Settings")
    
    analysis_mode = st.selectbox(
        "📋 Analysis Mode",
        [
            "Summary & Timeline",
            "Sports Commentator",
            "Sports Coach",
            "Safety & Security Audit"
        ],
        index=0,
        help="Choose the perspective for AI analysis."
    )
    
    # Video File Upload
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "📤 Upload Video Clip",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="Supports mp4, mov, avi, webm, mkv."
    )

# Header Section
st.markdown("<div class='title-gradient'>VisionAI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>Next-generation video intelligence analyzer, commentator, coach, and security inspector powered by Gemini multimodal AI.</div>", unsafe_allow_html=True)

# Handle file change and session cleanup
if uploaded_file is not None:
    if st.session_state.uploaded_file_name != uploaded_file.name:
        # File changed, clean up previous file
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            try:
                os.remove(st.session_state.video_path)
            except Exception:
                pass
        
        # Reset session states
        st.session_state.video_path = None
        st.session_state.frames = None
        st.session_state.analysis_output = None
        st.session_state.analysis_mode = None
        st.session_state.chat_history = []
        st.session_state.uploaded_file_name = uploaded_file.name

# Main Layout
if uploaded_file is None:
    # Landing page state
    st.info("💡 Please upload a video clip in the sidebar to get started!")
    
    # Decorative Cards explaining capabilities
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-val'>🔍</div>
            <div class='metric-lbl'>Detailed Summaries</div>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 10px;'>Generates chronological breakdowns and semantic timelines of events.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-val'>🎙️</div>
            <div class='metric-lbl'>Sports Commentator</div>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 10px;'>Turns play-by-play video frames into an energetic, vocal broadcasting script.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-val'>🏋️</div>
            <div class='metric-lbl'>Athletic Coach</div>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 10px;'>Critiques body mechanics, athletic posture, form errors, and suggests drills.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-val'>🛡️</div>
            <div class='metric-lbl'>Safety Audit</div>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 10px;'>Inspects environments for physical hazards, safety violations, and security risks.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # Save file if not already saved
    if st.session_state.video_path is None:
        with st.spinner("Saving video file to disk..."):
            st.session_state.video_path = video_processor.save_uploaded_file(uploaded_file)
            
    # Track setting changes to auto-re-extract if needed
    if "last_interval" not in st.session_state:
        st.session_state.last_interval = None
    if "last_max_width" not in st.session_state:
        st.session_state.last_max_width = None

    if (st.session_state.frames is None 
        or st.session_state.last_interval != interval_seconds 
        or st.session_state.last_max_width != max_frame_width):
        
        with st.spinner("Extracting frames for AI analysis..."):
            st.session_state.frames = video_processor.extract_frames(
                st.session_state.video_path,
                interval_seconds=interval_seconds,
                max_width=max_frame_width
            )
            st.session_state.last_interval = interval_seconds
            st.session_state.last_max_width = max_frame_width
            # If settings changed and frames re-extracted, reset chat history to prevent context mismatch
            st.session_state.chat_history = []
            
    # Gather video info
    video_info = video_processor.get_video_info(st.session_state.video_path)
    
    # Main column split: Video player & gallery on left, active workspace on right
    left_col, right_col = st.columns([1, 1.2])
    
    with left_col:
        st.subheader("🎥 Video Preview")
        st.video(uploaded_file)
        
        # Display Video Metadata Metrics in Glassmorphic Cards
        if "error" not in video_info:
            dur = video_info["duration"]
            res = f"{video_info['width']}x{video_info['height']}"
            fps = f"{video_info['fps']:.1f} FPS"
            
            st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-card'>
                    <div class='metric-val'>{dur:.1f}s</div>
                    <div class='metric-lbl'>Duration</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-val'>{res}</div>
                    <div class='metric-lbl'>Resolution</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-val'>{fps}</div>
                    <div class='metric-lbl'>Frame Rate</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show calculate estimated frame count
            est_frames = len(st.session_state.frames) if st.session_state.frames else 0
            st.markdown(f"ℹ️ *Extracted **{est_frames} frames** (every {interval_seconds}s) ready for analysis.*")
            
            # Integrated Frame Gallery inside an expander
            st.markdown("---")
            with st.expander("🖼️ View Extracted Frame Gallery", expanded=False):
                if st.session_state.frames:
                    grid_cols = st.columns(3)
                    for idx, frame in enumerate(st.session_state.frames):
                        col_idx = idx % 3
                        with grid_cols[col_idx]:
                            st.image(frame["image"], use_container_width=True)
                            st.markdown(f"<div style='text-align:center; font-size:0.8rem; font-weight:600; margin-bottom:10px;'>⏱️ {frame['timestamp_str']}</div>", unsafe_allow_html=True)
                else:
                    st.info("No frames extracted.")
        else:
            st.error(f"Error reading video metadata: {video_info['error']}")

    with right_col:
        # Toggle Buttons for Active Workspace Mode
        st.markdown("<div style='font-size:1.1rem; font-weight:600; margin-bottom:10px; color:#a855f7;'>🛠️ Select Workspace Tool</div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            report_active = st.session_state.active_tab == "report"
            btn_label = "📊 Report Generator" + (" ✅" if report_active else "")
            if st.button(btn_label, key="btn_report_toggle", use_container_width=True):
                st.session_state.active_tab = "report"
                st.rerun()
        with col_btn2:
            chat_active = st.session_state.active_tab == "chat"
            btn_label = "💬 Chatbot" + (" ✅" if chat_active else "")
            if st.button(btn_label, key="btn_chat_toggle", use_container_width=True):
                st.session_state.active_tab = "chat"
                st.rerun()
        
        st.markdown("<hr style='margin: 10px 0 20px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
        
        if st.session_state.active_tab == "report":
            st.subheader("📋 Video Intelligence Report")
            # Action Button
            analyze_btn = st.button("🚀 Run Video Analysis Report", use_container_width=True)
            
            if analyze_btn:
                try:
                    if not api_key_input:
                        st.error("🔑 Please enter a Gemini API Key in the sidebar to run the analysis.")
                    else:
                        # Initialize client
                        client = ai_analyst.get_client(api_key_input)
                        
                        with st.status("Analyzing Video...", expanded=True) as status:
                            status.write(f"🧠 Sending {len(st.session_state.frames)} frames to Gemini ({model_name}) for **{analysis_mode}**...")
                            analysis_result = ai_analyst.analyze_video(
                                client,
                                model_name,
                                st.session_state.frames,
                                analysis_mode
                            )
                            st.session_state.analysis_output = analysis_result
                            st.session_state.analysis_mode = analysis_mode
                            
                            status.update(label="✨ Analysis Complete!", state="complete")
                            st.toast("Video analysis report generated!", icon="🎉")
                        
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    
            if st.session_state.analysis_output:
                st.subheader(f"📊 {st.session_state.analysis_mode} Report")
                st.markdown(st.session_state.analysis_output)
                
                st.markdown("---")
                # Download Report Button
                report_data = st.session_state.analysis_output
                st.download_button(
                    label="📥 Download Report (Markdown)",
                    data=report_data,
                    file_name=f"vision_ai_report_{st.session_state.active_tab.replace(' ', '_').lower()}.md",
                    mime="text/markdown"
                )
            else:
                st.info("💡 Click the **Run Video Analysis Report** button above to generate a structured intelligence report! Or toggle the **Chatbot** button above to ask questions immediately.")
                
        else: # st.session_state.active_tab == "chat"
            st.subheader("💬 Chat with Video")
            st.write("Ask specific questions about details in the video frames. The AI will inspect all sampled frames chronologically to answer.")
            
            # Action buttons / suggestions
            st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 5px; font-weight: 500;'>💡 Try these suggested questions:</p>", unsafe_allow_html=True)
            s_col1, s_col2, s_col3 = st.columns(3)
            suggested_prompt = None
            with s_col1:
                if st.button("📝 Describe video", key="sug_desc", use_container_width=True):
                    suggested_prompt = "Describe the video timeline and main events in detail."
            with s_col2:
                if st.button("⚠️ Any hazards?", key="sug_safety", use_container_width=True):
                    suggested_prompt = "Inspect the video. Are there any safety violations or physical hazards?"
            with s_col3:
                if st.button("⚡ Analyze action", key="sug_action", use_container_width=True):
                    suggested_prompt = "Analyze the primary activity/action in this video. What are the key moments?"
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Clear chat button
            if len(st.session_state.chat_history) > 0:
                st.markdown("---")
                if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()

            # Chat input
            prompt = st.chat_input("Ask about details in the video (e.g. 'What is the color of the jacket?', 'Where is this located?')")
            
            # If a suggestion button was clicked, use it as prompt
            if suggested_prompt:
                prompt = suggested_prompt
                
            if prompt:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Verify API key
                if not api_key_input:
                    st.error("🔑 Please enter a Gemini API Key in the sidebar to chat with the video.")
                else:
                    # Get response
                    with st.spinner("Thinking..."):
                        try:
                            client = ai_analyst.get_client(api_key_input)
                            response = ai_analyst.chat_with_video(
                                client,
                                model_name,
                                st.session_state.frames,
                                st.session_state.chat_history[:-1], # pass previous history
                                prompt
                            )
                            # Add assistant response to history
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chat failed: {str(e)}")

