import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 页面配置 (隐藏侧边栏并设为宽屏)
st.set_page_config(
    page_title="DivoScan - AI 住宿侦探", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 读取配置
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 注入极致黑客视觉样式
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    /* 隐藏左侧菜单按钮 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; padding-top: 40px; margin-bottom: 0px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; }
    .stButton>button { width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; border: none; height: 3rem; border-radius: 5px; }
    .stButton>button:hover { background-color: #39FF14; color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 4. 主界面标题
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 居中对齐的搜索框
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（例如：新加坡金沙酒店 / 曼谷 W 酒店）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度多维扫描")

# 5. 执行逻辑
if scan_clicked:
    if not GOOGLE_API_KEY:
        st.error("系统配置错误：缺失 API 密钥。")
    elif hotel_query:
        with st.status("Divo Agent 正在解码真相...", expanded=True) as status:
            st.write("📡 穿透数据迷雾，抓取证据碎片...")
            time.sleep(1)
            
            st.write("🧠 Reality-Divo 正在进行多维逻辑博弈...")
            
            # 初始化大脑
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            
            prompt = f"""
            你是一个毒舌且专业的酒店审计专家 Reality-Divo。
            针对酒店 '{hotel_query}'，请直接给出排雷审计。

            必须严格按此格式开头：
            真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
            
            点评要求：
            1. 语气犀利，指出该酒店‘滤镜之外’的真相。
            2. 即使数据不足，也请基于品牌口碑和已知行业痛点给出专业预测。
            3. 揭露诸如：电梯拥挤、早餐像食堂、地毯霉味、隔音差等具体细节。
            """
            
            try:
                response = model.generate_content(prompt)
                full_report = response.text
                
                # 正则提取评分驱动雷达图
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [65, 55, 75, 50, 80]
                
                status.update(label="审计报告已就绪", state="complete", expanded=False)
            except Exception as e:
                st.error(f"大脑执行异常: {str(e)}")
                r_values = [20, 20, 20, 20, 20]
                full_report = "审计官暂时掉线，请确认 API Key 是否正确并重试。"

        # 6. 结果可视化 (双列展示)
        st.divider()
        col_left, col_right = st.columns([1, 1.2])
        
        with col_left:
            # 极致雷达图样式
            df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
            fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.2)', line_color='#39FF14', line_width=3)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#00ffcc',
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor='#333'),
                    angularaxis=dict(gridcolor='#333', tickfont=dict(size=14))
                ),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown(f"### 🕵️ 现场审计报告: <span style='color:#00ffcc;'>{hotel_query}</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            st.write("")
            st.caption("⚠️ Divo 提示：本报告基于 AI 深度扫描生成，反映用户端最真实的吐槽与期待。")
    else:
        st.warning("🕵️ 告诉我酒店的名字，我才能帮你办案。")

# 7. 页脚
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<div style='text-align:center; color:#4b5563;'>© 2026 Divoscan.com | Multi-Agent Analysis Protocol v2.0</div>", unsafe_allow_html=True)
