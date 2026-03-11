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

# 初始化 Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # 使用兼容性最好的模型名称
    model = genai.GenerativeModel('gemini-1.5-flash') 

# ... (中间的样式代码保持不变) ...

if st.button("🚀 启动 AI 多维扫描"):
    if not FIRECRAWL_API_KEY or not GEMINI_API_KEY:
        st.error("请确保在 Secrets 中配置了 FIRECRAWL_API_KEY 和 GEMINI_API_KEY")
        st.stop()

    if hotel_query:
        with st.spinner(f"DivoScan 正在深度解析 {hotel_query} 的全网证据..."):
            try:
                # --- Step 1: Firecrawl 抓取 ---
                search_url = "https://api.firecrawl.dev/v1/scrape"
                payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+tripadvisor",
                    "formats": ["markdown"]
                }
                headers = {"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"}
                response = requests.post(search_url, json=payload, headers=headers)
                
                # 容错处理
                res_json = response.json()
                raw_data = res_json.get('data', {}).get('markdown', '')[:4000]

                if not raw_data:
                    st.warning("未能抓取到实时数据，正尝试备用分析路径...")
                    raw_data = f"关于 {hotel_query} 的通用网络信息"

                # --- Step 2: Gemini 诊断 ---
                prompt = f"""
                你是一个尖锐的酒店测评专家 Divo。请分析以下关于 '{hotel_query}' 的数据：
                ---
                {raw_data}
                ---
                任务：
                1. 识别 3 个潜在的“差评陷阱”。
                2. 给出 0-100 的五个维度评分：真实度、性价比、硬件、静谧度、服务。
                3. 给出一个“毒舌”总结。
                请用中文回答。
                """
                ai_response = model.generate_content(prompt)
                
                # --- Step 3: 展示 ---
                st.divider()
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    # 模拟雷达图，后期可根据 ai_response 提取数字
                    df_radar = pd.DataFrame(dict(
                        r=[78, 52, 88, 45, 80],
                        theta=['真实度', '性价比', '硬件', '静谧度', '服务']))
                    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                    fig.update_layout(polar=dict(bgcolor='#1a1c24'), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                    st.plotly_chart(fig, use_column_width=True)
                with c2:
                    st.markdown(f"### 🕵️ AI 侦探报告\n{ai_response.text}")

            except Exception as e:
                st.error(f"分析失败，原因: {e}")
