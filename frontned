import streamlit as st
import base64

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_header_and_css(bg_file, logo_file):
    bg_base64 = get_base64(bg_file)
    logo_base64 = get_base64(logo_file)
    st.markdown(
        f"""
        <style>
        body {{
            background-image: url('data:image/png;base64,{bg_base64}');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }}
        .app-header {{
            background: rgba(255,255,255,0.85);
            padding: 1.5rem 2rem 1rem 2rem;
            border-radius: 0 0 1.5rem 1.5rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.07);
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .app-logo {{
            width: 48px; height: 48px;
            background: url('data:image/png;base64,{logo_base64}') no-repeat center center;
            background-size: contain;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
        }}
        .app-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #3a3a3a;
            letter-spacing: 1px;
        }}
        .premium-badge {{
            background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
            color: #fff;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.3rem 0.8rem;
            margin-left: 1rem;
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: flex; align-items: center;
            gap: 0.5rem;
        }}
        .footer {{
            margin-top: 3rem;
            color: #888;
            font-size: 0.95rem;
            text-align: center;
        }}
        section[data-testid="stFileUploader"] > div {{
            min-width: 400px;
            max-width: 600px;
            min-height: 180px;
            padding: 2.5rem 1.5rem;
            font-size: 1.25rem;
            border-radius: 1.2rem;
            margin: 0 auto 2rem auto;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        section[data-testid="stFileUploader"] label {{
            font-size: 1.2rem;
        }}
        </style>
        <div class="app-header">
            <div class="app-logo"></div>
            <div class="app-title">Lumera</div>
            <div class="premium-badge">⚡ Unlock Pro: Up to 20x Faster Processing & Advanced AI Features</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h3 style='font-family:Montserrat, sans-serif; color:#3a3a3a;'>Create a panorama from your video</h3>", unsafe_allow_html=True)

def render_footer():
    st.markdown(
        "<div class='footer'>This application is for demonstration purposes only.</div>",
        unsafe_allow_html=True
    ) 
