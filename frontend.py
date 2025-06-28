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
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400;500&display=swap');
        html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
            background: url('data:image/png;base64,{bg_base64}') no-repeat center center fixed !important;
            background-size: cover !important;
            background-color: #e0eafc !important;
            color: #185a9d !important;
        }}
        body {{
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }}
        .app-header {{
            background: rgba(255,255,255,0.92);
            padding: 2rem 2.5rem 1.5rem 2.5rem;
            border-radius: 0 0 2rem 2rem;
            box-shadow: 0 6px 32px rgba(0,0,0,0.09);
            display: flex;
            align-items: center;
            gap: 1.5rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
        }}
        .app-logo {{
            width: 60px; height: 60px;
            background: url('data:image/png;base64,{logo_base64}') no-repeat center center;
            background-size: contain;
            border-radius: 16px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 12px rgba(67,206,162,0.12);
        }}
        .app-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #185a9d;
            letter-spacing: 1.5px;
            margin-bottom: 0.2rem;
        }}
        .premium-badge {{
            background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
            color: #fff;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.4rem 1.1rem;
            margin-left: 1.2rem;
            font-size: 1.08rem;
            box-shadow: 0 2px 10px rgba(24,90,157,0.10);
            display: flex; align-items: center;
            gap: 0.7rem;
        }}
        .tech-stack-line-box {{
            background: linear-gradient(90deg, #e0eafc 0%, #185a9d 100%);
            color: #fff;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.4rem 1.1rem;
            margin-top: 0.7rem;
            margin-left: 0;
            font-size: 1.08rem;
            box-shadow: 0 2px 10px rgba(24,90,157,0.10);
            display: flex; align-items: center;
            gap: 0.7rem;
            letter-spacing: 0.2px;
        }}
        .footer {{
            margin-top: 3.5rem;
            color: #888;
            font-size: 1.05rem;
            text-align: center;
            font-family: 'Roboto', sans-serif;
        }}
        section[data-testid="stFileUploader"] > div {{
            min-width: 350px;
            max-width: 520px;
            min-height: 170px;
            padding: 2.2rem 1.2rem;
            font-size: 1.18rem;
            border-radius: 1.1rem;
            margin: 0 auto 2.2rem auto;
            box-shadow: 0 2px 14px rgba(24,90,157,0.08);
            background: rgba(255,255,255,0.97);
            border: 1.5px solid #e0eafc;
        }}
        section[data-testid="stFileUploader"] label {{
            font-size: 1.15rem;
            color: #185a9d;
            font-weight: 500;
        }}
        @media (max-width: 700px) {{
            .app-header {{
                flex-direction: column;
                align-items: flex-start;
                padding: 1.2rem 1rem 1rem 1rem;
            }}
            .app-title {{
                font-size: 2rem;
            }}
            .premium-badge {{
                font-size: 0.98rem;
                padding: 0.3rem 0.7rem;
            }}
        }}
        span[data-testid="stFileUploaderFilename"] {
            color: #fff !important;
            font-weight: 600;
            font-size: 1.1rem;
        }
        </style>
        <div class="app-header">
            <div class="app-logo"></div>
            <div>
                <div class="app-title">Lumera</div>
                <div class="tech-stack-line-box">🛠️ The full version is powered by OpenCV, COLMAP, PyTorch (RAFT), and Azure Cloud for professional-grade video stitching and 3D reconstruction.</div>
            </div>
            <div class="premium-badge">⚡ Unlock Pro: Up to 20x Faster Processing & Advanced AI Features</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h3 style='font-family:Montserrat, sans-serif; color:#fff; margin-bottom:1.5rem;'>Create a panorama from your video</h3>", unsafe_allow_html=True)

def render_footer():
    st.markdown(
        "<div class='footer'>This application is for demonstration purposes only.<br>Powered by Bilal Albezreh & Yaman Albezreh &middot; 2025</div>",
        unsafe_allow_html=True
    )
