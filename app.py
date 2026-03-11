import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 页面配置
st.set_page_config(
    page_title="DivoScan - AI 住宿侦探", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 注入极致黑客视觉样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.8rem; text-align: center; padding-top: 60px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; }
    .stButton>button { width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; border: none; height: 3.5rem; border-radius: 8px; font-size: 1.2rem; }
    .stButton>button:hover { background-color: #39FF14; box-shadow: 0 0 20px #39FF14; }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #333; height: 3.5rem; font-size: 1.1rem; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. 品牌头部
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 4. 搜索区域
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（如：新加坡金沙酒店）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度扫描")

# 5. 核心逻辑：解决 NotFound 与 429 的双重保护
def get_ai_response(query):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        return "ERROR: Missing API Key", None
    
    genai.configure(api_key=api_key)
    
    # 尝试模型列表：从最新到最稳
    # 注意：这里去掉了 models/ 前缀，由 SDK 自动处理
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']
    
    prompt = f"你是一个毒舌酒店专家Reality-Divo。针对酒店'{query}'，给出审计报告。格式：真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字。请犀利点评。"
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt)
            return response.text, m_name
        except Exception as e:
            error_msg = str(e).lower()
            # 如果是找不到模型或额度限制，尝试下一个
            if "notfound" in error_msg or "404" in error_msg or "429" in error_msg:
                continue
            else:
                return f"ERROR: {str(e)}", None
    return "所有审计接口均暂时离线，请稍后再试。", None

# 6. 页面渲染
if scan_clicked:
    if hotel_query:
        with st.status("Divo Agents 正在解码真相...", expanded=True) as status:
            full_report, final_model = get_ai_response(hotel_query)
            
            if full_report and not full_report.startswith("ERROR"):
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [60, 60, 60, 60, 60]
                
                status.update(label=f"扫描完毕 (驱动: {final_model})", state="complete", expanded=False)
                
                st.divider()
                col_left, col_right = st.columns([1, 1.3])
                with col_left:
                    df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.3)', line_color='#39FF14', line_width=4)
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ffcc', polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor='#333'), angularaxis=dict(gridcolor='#333')), height=450)
                    st.plotly_chart(fig, use_container_width=True)
                with col_right:
                    st.markdown(f"### 🕵️ 现场审计报告: {hotel_query}")
                    st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            else:
                st.error(full_report)
    else:
        st.warning("🕵️ 请输入酒店名称。")

st.markdown("<br><br><div style='text-align:center; color:#4b5563; font-size:0.9rem;'>© 2026 Divoscan.com</div>", unsafe_allow_html=True)
