import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# 1. 基础配置
st.set_page_config(page_title="DivoScan Debugger", page_icon="🕵️", layout="wide")

# 2. 读取 Secrets
FIRECRAWL_API_KEY = st.secrets.get("FIRECRAWL_API_KEY")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# --- 核心诊断函数 ---
def test_gemini_api():
    """测试 Gemini API 连通性并返回详细错误"""
    if not GEMINI_API_KEY:
        return "Missing Key", "请在 Secrets 中配置 GEMINI_API_KEY"
    
    # 尝试两个最可能的端点
    models_to_test = ["gemini-1.5-flash", "gemini-1.5-pro"]
    errors = []
    
    for model_name in models_to_test:
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "say hi"}]}]}
        
        try:
            res = requests.post(test_url, json=payload, timeout=10)
            if res.status_code == 200:
                return "Success", model_name
            else:
                errors.append(f"{model_name}: {res.status_code} - {res.text}")
        except Exception as e:
            errors.append(f"{model_name} Connection Error: {str(e)}")
            
    return "Failed", "\n".join(errors)

# 3. 侧边栏：实时状态监控
with st.sidebar:
    st.header("⚙️ 系统自检")
    status, detail = test_gemini_api()
    if status == "Success":
        st.success(f"API 状态: 正常\n当前模型: {detail}")
    else:
        st.error(f"API 状态: 异常")
        st.code(detail)
    
    show_debug = st.checkbox("显示原始数据(Debug Mode)")

# 4. 主界面样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3rem; text-align: center; }
    .report-card { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 12px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
hotel_query = st.text_input("", placeholder="🔍 输入酒店名开始排雷", label_visibility="collapsed")

if st.button("🚀 启动深度扫描"):
    if status != "Success":
        st.error("无法启动：API 连通性测试未通过，请查看左侧 Debug 信息。")
    elif hotel_query:
        with st.spinner("Divo Agent 正在执行跨协议嗅探..."):
            try:
                # --- Step 1: Firecrawl 抓取 ---
                scrape_url = "https://api.firecrawl.dev/v1/scrape"
                scrape_payload = {
                    "url": f"https://www.google.com/search?q={hotel_query}+reviews+tripadvisor",
                    "formats": ["markdown"]
                }
                scrape_res = requests.post(scrape_url, json=scrape_payload, headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"})
                raw_data = scrape_res.json().get('data', {}).get('markdown', '')[:3000]

                # --- Step 2: Gemini 分析 ---
                # 使用测试成功的模型
                final_model = detail if status == "Success" else "gemini-1.5-flash"
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{final_model}:generateContent?key={GEMINI_API_KEY}"
                
                prompt = f"分析 {hotel_query} 的评价：\n{raw_data}\n\n请用毒舌风格列出3个避雷点，并给5维评分。用中文。"
                gemini_res = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt}]}]})
                
                if show_debug:
                    st.write("--- DEBUG DATA ---")
                    st.json(gemini_res.json())

                if gemini_res.status_code == 200:
                    report = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    st.divider()
                    c1, c2 = st.columns([1, 1.5])
                    with c1:
                        # 雷达图逻辑
                        df = pd.DataFrame(dict(r=[80, 50, 85, 45, 75], theta=['真实度','性价比','硬件','静谧度','服务']))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_traces(fill='toself', fillcolor='rgba(0, 255, 204, 0.3)', line_color='#00ffcc')
                        fig.update_layout(polar=dict(bgcolor='#1a1c24'), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.markdown(f"<div class='report-card'><b>🕵️ Divo 报告：</b><br><br>{report}</div>", unsafe_allow_html=True)
                else:
                    st.error(f"AI 分析出错: {gemini_res.text}")

            except Exception as e:
                st.error(f"链路崩溃: {e}")

st.caption("© 2026 Divoscan.com | Hybrid Analysis Engine")
