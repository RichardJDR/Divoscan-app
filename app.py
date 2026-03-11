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

# 2. 读取配置
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入视觉样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.8rem; text-align: center; padding-top: 50px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    .stButton>button { width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; border: none; height: 3.5rem; border-radius: 8px; font-size: 1.2rem; transition: 0.3s; }
    .stButton>button:hover { background-color: #39FF14; box-shadow: 0 0 20px #39FF14; transform: translateY(-2px); }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #333; height: 3.5rem; font-size: 1.1rem; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 4. 品牌头部
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 5. 搜索区域
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（如：新加坡金沙酒店 / 上海宝格丽）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度扫描")

# 6. 核心逻辑：自动降级机制
def generate_audit(query):
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 备选模型列表
    model_list = ['gemini-2.0-flash', 'gemini-1.5-flash']
    
    prompt = f"""
    你是一个毒舌且专业的酒店审计专家 Reality-Divo。
    针对酒店 '{query}'，请给出犀利的排雷报告。
    必须严格按此格式开头评分：
    真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
    """
    
    for model_name in model_list:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, model_name
        except Exception as e:
            if "429" in str(e):
                continue # 如果额度超限，尝试下一个模型
            else:
                raise e # 其它错误抛出
    return None, None

# 7. 页面渲染逻辑
if scan_clicked:
    if not GOOGLE_API_KEY:
        st.error("密钥缺失：请在 Secrets 中填入 GOOGLE_API_KEY。")
    elif hotel_query:
        with st.status("Divo Agents 正在联合办案...", expanded=True) as status:
            st.write("📡 探测器正在采集碎片...")
            
            full_report, active_model = generate_audit(hotel_query)
            
            if full_report:
                # 解析评分驱动雷达图
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [70, 60, 80, 55, 75]
                
                status.update(label=f"审计完成 (引擎: {active_model})", state="complete", expanded=False)
                
                st.divider()
                col_left, col_right = st.columns([1, 1.3])
                with col_left:
                    df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.3)', line_color='#39FF14', line_width=4)
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ffcc', polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor='#333'), angularaxis=dict(gridcolor='#333', tickfont=dict(size=14))), height=450)
                    st.plotly_chart(fig, use_container_width=True)

                with col_right:
                    st.markdown(f"### 🕵️ 现场审计报告: <span style='color:#00ffcc;'>{hotel_query}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            else:
                st.error("🕵️ 侦探社今日额度已耗尽，请稍后再试或更换 API Key。")
    else:
        st.warning("🕵️ 请输入酒店名称。")

# 8. 页脚
st.markdown("<br><br><br><div style='text-align:center; color:#4b5563; font-size:0.9rem;'>© 2026 Divoscan.com | Multi-Agent Analysis Protocol v2.8</div>", unsafe_allow_html=True)
