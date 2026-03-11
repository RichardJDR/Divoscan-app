import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 基础页面配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🕵️", layout="wide")

# 2. 读取双 Key (请确保在 Streamlit Cloud 的 Secrets 中配置)
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入品牌视觉样式 (极致黑客绿风格)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; padding-top: 20px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.1rem; margin-bottom: 30px; }
    .stMetric { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.6; }
    /* 侧边栏样式优化 */
    [data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2937; }
    .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 10px; }
    .online { background-color: #39FF14; box-shadow: 0 0 8px #39FF14; }
    .offline { background-color: #ff4b4b; box-shadow: 0 0 8px #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 4. 侧边栏：精简双 Key 指示灯
with st.sidebar:
    st.markdown("<h2 style='color:#00ffcc;'>🛰️ 核心引擎状态</h2>", unsafe_allow_html=True)
    
    # 探测器状态
    if FIRECRAWL_API_KEY:
        st
