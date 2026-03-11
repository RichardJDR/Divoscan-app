import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import google.generativeai as genai

# 1. 基础配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 2. 安全读取 Key
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

# 3. 页面样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; }
    .report-card { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 15px; padding: 20px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

hotel_query = st.text_input("", placeholder="输入酒店名称（例如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
    if not FIRECRAWL_API_KEY or not GEMINI_API_KEY:
        st.error("请确保配置了所有 API Keys")
        st.stop()

    if hotel_query:
        with st.spinner(f"DivoScan 正在全球网页中嗅探并分析 {hotel_query}..."):
            try:
                # --- Step 1: Firecrawl 抓取数据 ---
                search_url = "https://api.firecrawl.dev/v1/scrape"
                payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+highlights",
                    "formats": ["markdown"]
                }
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
                response = requests.post(search_url, json=payload, headers=headers)
                raw_data = response.json().get('data', {}).get('markdown', '')[:3000]

                # --- Step 2: Gemini LLM 分析大脑 ---
                prompt = f"""
                你是一个尖锐的酒店测评专家，现在你要分析关于 '{hotel_query}' 的以下原始评价数据：
                ---
                {raw_data}
                ---
                请执行以下任务：
                1. 识别并列出 3 个最严重的“真实度冲突点”（官图 vs 实拍）。
                2. 给该酒店在以下五个维度打分（0-100）：真实度、性价比、硬件、静谧度、服务。
                3. 以“DivoScan 终极建议”结尾。
                请用中文回答，语气要专业、客观、不留情面。
                """
                ai_response = model.generate_content(prompt)
                full_text = ai_response.text

                # --- Step 3: UI 展示 ---
                st.divider()
                c1, c2 = st.columns([1, 1.2])
                
                with c1:
                    # 这里的打分未来可以写逻辑让 AI 输出 JSON 格式，现在先从文本中提取或固定
                    df_radar = pd.DataFrame(dict(
                        r=[80, 45, 90, 40, 85], # 这里后续可优化为 AI 实时分
                        theta=['真实度', '性价比', '硬件', '静谧度', '服务']))
                    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                    fig.update_layout(polar=dict(bgcolor='#1a1c24'), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_container_width=True)

                with c2:
                    st.markdown(f"<div class='report-card'><b>🕵️ AI 侦探实时报告：</b><br><br>{full_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"分析中断: {e}")
