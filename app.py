import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# 1. 网页基础配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 2. 读取安全配置
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# 3. 智能模型获取 (基于之前的成功探测逻辑)
@st.cache_resource
def get_verified_model(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            models = res.json().get('models', [])
            # 优先匹配 2.5 或 1.5 的 Flash 模型
            for m in models:
                if 'flash' in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m['name']
            if models: return models[0]['name']
    except:
        return None
    return None

verified_model_path = get_verified_model(GEMINI_API_KEY)

# 4. 自定义品牌 UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; margin-top: -30px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; font-size: 1.1rem; }
    .report-card { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 15px; padding: 25px; color: #e0e0e0; line-height: 1.6; }
    .stButton>button { width: 100%; background-color: #00ffcc; color: black; font-weight: bold; border-radius: 10px; border: none; height: 3rem; }
    .stButton>button:hover { background-color: #39FF14; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 5. 头部区域
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 6. 侧边栏状态灯
with st.sidebar:
    st.header("🕵️ 系统核心状态")
    if verified_model_path:
        st.success(f"AI 引擎已挂载: \n{verified_model_path.split('/')[-1]}")
    else:
        st.error("AI 引擎连接失败")
    st.divider()
    st.caption("DivoScan v1.0.0-Gold")

# 7. 主交互逻辑
hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（例如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
    if not FIRECRAWL_API_KEY or not GEMINI_API_KEY:
        st.error("配置错误：请在 Secrets 中检查 API Key。")
        st.stop()

    if hotel_query:
        with st.spinner(f"DivoScan 正在全球联网嗅探并深度分析 {hotel_query}..."):
            try:
                # --- Step 1: Firecrawl 数据抓取 ---
                scrape_url = "https://api.firecrawl.dev/v1/scrape"
                payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+highlights+tripadvisor",
                    "formats": ["markdown"]
                }
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
                scrape_res = requests.post(scrape_url, json=payload, headers=headers)
                raw_data = scrape_res.json().get('data', {}).get('markdown', '')[:4000]

                # --- Step 2: Gemini 专家大脑诊断 ---
                gemini_endpoint = f"https://generativelanguage.googleapis.com/v1beta/{verified_model_path}:generateContent?key={GEMINI_API_KEY}"
                
                prompt = f"""
                你是一个尖锐、毒辣且极其专业的酒店审计专家 Divo。
                请根据以下关于 '{hotel_query}' 的实时抓取数据进行深度排雷：
                ---
                {raw_data}
                ---
                任务：
                1. 第一行务必仅输出 5 个由逗号分隔的数字，代表该酒店的：真实度,性价比,硬件,静谧度,服务 (0-100)。
                2. 随后列出 3 个核心“滤镜陷阱”。
                3. 以一句话“Divo 终极裁决”结尾。
                要求：语气专业冷酷。用中文回答。
                """
                
                gemini_res = requests.post(gemini_endpoint, json={"contents": [{"parts": [{"text": prompt}]}]})
                
                if gemini_res.status_code == 200:
                    full_text = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    # 尝试解析 AI 返回的分数
                    try:
                        lines = full_text.strip().split('\n')
                        scores = [int(s.strip()) for s in lines[0].split(',')]
                        report_content = "\n".join(lines[1:])
                    except:
                        scores = [70, 70, 70, 70, 70]
                        report_content = full_text

                    # --- Step 3: UI 视觉化展示 ---
                    st.divider()
                    col_left, col_right = st.columns([1, 1.3])

                    with col_left:
                        df_radar = pd.DataFrame(dict(
                            r=scores,
                            theta=['真实度','性价比','硬件','静谧度','服务']))
                        
                        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                        fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                        fig.update_layout(
                            polar=dict(bgcolor='#1a1c24', radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")),
                            paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col_right:
                        st.markdown(f"### 🕵️ Divo 侦探现场报告")
                        st.markdown(f"<div class='report-card'>{report_content}</div>", unsafe_allow_html=True)
                else:
                    st.error(f"AI 调用失败: {gemini_res.text}")

            except Exception as e:
                st.error(f"🚨 扫描链路异常: {e}")
    else:
        st.warning("❗ 请输入想要扫描的酒店名称。")

# 8. 页脚
st.caption("© 2026 Divoscan.com | Powered by Firecrawl & Gemini-Flash-Next")
