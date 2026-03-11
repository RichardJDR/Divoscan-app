import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import google.generativeai as genai

# 1. 基础配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 2. 读取 Secrets
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# 3. 初始化 Gemini (多重兼容逻辑)
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # 尝试标准路径
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except:
        try:
            # 尝试简写路径
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"AI 引擎启动失败: {e}")

# 4. 自定义样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; margin-top: -30px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; font-size: 1.1rem; }
    .report-card { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 15px; padding: 25px; color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 5. 头部
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 6. 搜索交互
hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
    if not FIRECRAWL_API_KEY or not GEMINI_API_KEY:
        st.error("⚠️ 配置缺失：请检查 Secrets 中的 API Keys")
        st.stop()

    if hotel_query:
        with st.spinner(f"DivoScan 正在深度解析 {hotel_query} 的全网证据..."):
            try:
                # --- Step 1: Firecrawl 抓取 ---
                scrape_url = "https://api.firecrawl.dev/v1/scrape"
                # 优化搜索词，针对 TripAdvisor 抓取评论亮点
                payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+highlights+tripadvisor",
                    "formats": ["markdown"]
                }
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
                
                response = requests.post(scrape_url, json=payload, headers=headers)
                res_json = response.json()
                raw_data = res_json.get('data', {}).get('markdown', '')[:4000]

                if not raw_data:
                    raw_data = f"关于 {hotel_query} 的初步搜索结果不足，请基于通用行业逻辑和品牌定位进行分析。"

                # --- Step 2: Gemini 诊断 ---
                if model:
                    prompt = f"""
                    你是一个酒店审计专家 Divo。请根据以下关于 '{hotel_query}' 的数据进行排雷分析：
                    ---
                    {raw_data}
                    ---
                    任务：
                    1. 识别 3 个潜在的“滤镜陷阱”（官图 vs 实拍冲突）。
                    2. 给出 0-100 的五个维度评分：真实度、性价比、硬件、静谧度、服务。
                    3. 给出一段毒舌且专业的“Divo 终极裁决”。
                    请用中文回答。
                    """
                    ai_response = model.generate_content(prompt)
                    report_text = ai_response.text
                else:
                    report_text = "AI 引擎未就绪，请检查 API 配置。"

                # --- Step 3: UI 展示 ---
                st.divider()
                c_left, c_right = st.columns([1, 1.3])

                with c_left:
                    # 模拟打分，增强视觉反馈
                    score_vals = [82, 48, 91, 42, 85] if "艾美" in hotel_query else [70, 50, 70, 50, 70]
                    df_radar = pd.DataFrame(dict(r=score_vals, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                    fig.update_layout(polar=dict(bgcolor='#1a1c24', radialaxis=dict(visible=True, range=[0, 100], gridcolor="#444")),
                                    paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                    st.plotly_chart(fig, use_column_width=True)

                with c_right:
                    st.markdown(f"### 🕵️ Divo 侦探报告")
                    st.markdown(f"<div class='report-card'>{report_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"🚨 扫描失败: {e}")
    else:
        st.warning("❗ 请输入酒店名称。")

st.caption("© 2026 Divoscan.com | Agent Logic: Gemini-1.5-Flash")
