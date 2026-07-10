import os
from google import genai
from google.genai import types

def get_client(api_key=None):
    """
    Initializes and returns the Google GenAI Client.
    Uses the provided key or falls back to environmental GEMINI_API_KEY.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is missing. Please provide it in the sidebar or set the GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=key)

def analyze_video(client, model_name, frames, mode):
    """
    Analyzes the video frames based on the selected mode.
    """
    if not frames:
        return "No frames extracted to analyze."

    # Define prompts based on mode
    prompts = {
        "Summary & Timeline": {
            "system_instruction": "You are a professional video producer and chronological analyst. Summarize the video and create a detailed timeline.",
            "task": (
                "Analyze the provided video frames. Provide a comprehensive report containing:\n"
                "1. **Executive Summary**: A concise, premium description of what the video shows, its overall theme, setting, and flow.\n"
                "2. **Detailed Chronological Timeline**: Break down the action frame by frame (or at notable intervals) using the timestamps. Describe what occurs in each frame.\n"
                "3. **Key Visual Elements**: List important objects, colors, characters, text overlay, or lighting styles observed.\n"
                "Write in a professional, clear, and engaging tone."
            )
        },
        "Sports Commentator": {
            "system_instruction": "You are an energetic, legendary sports broadcaster. Provide high-octane, dramatic, and engaging play-by-play commentary.",
            "task": (
                "Imagine you are broadcasting this clip live on television. Analyze the sequence of frames and write an exciting play-by-play script:\n"
                "- Use an energetic, enthusiastic, and descriptive sportscasting style.\n"
                "- Include timestamps in brackets next to your commentary (e.g. `[00:03] - ...`) to sync with the video action.\n"
                "- Add emotion and sound markers in italics (e.g., *[Crowd cheers wildy]*, *[Gasp from the commentators]*, *[Buzzer sounds]*).\n"
                "- Conclude with a memorable final recap call (e.g., 'What an unbelievable display of skill!')."
            )
        },
        "Sports Coach": {
            "system_instruction": "You are an elite athletic coach and biomechanical analyst. Evaluate posture, technique, and form, and offer improvement advice.",
            "task": (
                "Analyze the athletic movement in the video frames. Provide a detailed coaching analysis:\n"
                "1. **Phase Breakdown**: Analyze the motion phases (e.g., Setup/Start, Acceleration/Execution, Follow-through/Finish).\n"
                "2. **Technique & Form Critique**: Assess the subject's form. Highlight correct body angles, footwork, posture, and point out any mechanical errors, inefficiencies, or safety issues (e.g., rounding the back, improper knee tracking, head position).\n"
                "3. **Actionable Recommendations**: Give specific drills, postural cues, or muscle activation exercises to help them correct their form.\n"
                "Be constructive, encouraging, and highly detailed."
            )
        },
        "Safety & Security Audit": {
            "system_instruction": "You are an expert safety inspector and security analyst. Audit the video for compliance, hazards, and suspicious activities.",
            "task": (
                "Examine the video sequence carefully for safety and security purposes. Provide an audit report containing:\n"
                "1. **Environment & Activity Overview**: Describe the scene and what the subjects are doing.\n"
                "2. **Safety Violations & Physical Hazards**: Identify any unsafe acts, lack of PPE (hard hats, safety glasses, gloves), ergonomic issues, or physical hazards (slipping, machine risks, electrical hazards).\n"
                "3. **Security Analysis**: Evaluate if there are any suspicious behaviors, unauthorized access, or anomalies.\n"
                "4. **Risk Level Rating**: Assign a risk rating (Low, Medium, High) with rationale.\n"
                "5. **Preventative Recommendations**: Actionable items to mitigate risks."
            )
        }
    }
    
    config = prompts.get(mode)
    if not config:
        raise ValueError(f"Unknown analysis mode: {mode}")
        
    # Build contents list with sequence of frames
    contents = [
        f"System Instruction: {config['system_instruction']}\n\n"
        "Here are the chronological frames extracted from the video. Please review them and answer the task below.\n"
    ]
    
    for idx, f in enumerate(frames):
        contents.append(f"\n--- Frame {idx+1} (Timestamp: {f['timestamp_str']}) ---")
        contents.append(f["image"])
        
    contents.append(f"\n\nTask: {config['task']}")
    
    # Generate content
    response = client.models.generate_content(
        model=model_name,
        contents=contents
    )
    
    return response.text

def chat_with_video(client, model_name, frames, chat_history, new_question):
    """
    Answers a question about the video, utilizing the frames and previous chat history.
    """
    contents = [
        "You are an AI Video Assistant. You are here to answer questions about the video that the user has uploaded.\n"
        "Below are the chronological frames of the video, each labeled with its timestamp.\n"
        "Use these frames to answer the user's questions as accurately and specifically as possible. If the video does not show what the user asks, politely explain that it is not visible in the frames.\n"
    ]
    
    for idx, f in enumerate(frames):
        contents.append(f"\n--- Frame {idx+1} (Timestamp: {f['timestamp_str']}) ---")
        contents.append(f["image"])
        
    contents.append("\n\nHere is the conversation history so far:")
    for msg in chat_history:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        contents.append(f"\n{role_label}: {msg['content']}")
        
    contents.append(f"\nUser: {new_question}")
    contents.append("\nAssistant: ")
    
    response = client.models.generate_content(
        model=model_name,
        contents=contents
    )
    
    return response.text
