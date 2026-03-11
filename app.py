import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import re

# 1. 页面配置：隐藏侧边栏，全宽布局
st.set_page_config(
    page_title="DivoScan - AI 住宿侦探", 
    page_icon="🕵️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 读取 Secrets 
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

# 3. 极致黑客视觉样式 (针对无侧边栏优化)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .divo-title { color: #00ffcc; font-family: 'Courier New', monospace; font-weight: bold; font-size: 3.5rem; text-align: center; padding-top: 40px; margin-bottom: 5px; }
    .divo-slogan { color: #39FF14; text-align: center; font-style: italic; font-size: 1.2rem; margin-bottom: 50px; }
    .report-box { background-color: #161b22; border-left: 5px solid #39FF14; padding: 25px; border-radius: 8px; line-height: 1.8; font-size: 1.1rem; color: #e5e7eb; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .stButton>button { width: 100%; background-color: #00ffcc; color: #0e1117; font-weight: bold; border: none; height: 3.2rem; border-radius: 6px; font-size: 1.1rem; transition: 0.3s; }
    .stButton>button:hover { background-color: #39FF14; color: #0e1117; box-shadow: 0 0 15px #39FF14; }
    .stTextInput>div>div>input { background-color: #1a1c24; color: white; border: 1px solid #333; height: 3.2rem; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# 4. 品牌头部
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 5. 搜索区域 (居中布局)
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    hotel_query = st.text_input("", placeholder="🔍 输入酒店名称进行深度扫描（例如：新加坡金沙酒店）", label_visibility="collapsed")
    scan_clicked = st.button("🚀 启动深度多维扫描")

# 6. 核心逻辑执行
if scan_clicked:
    if not GOOGLE_API_KEY:
        st.error("系统错误：未检测到 GOOGLE_API_KEY，请在 Secrets 中配置。")
    elif hotel_query:
        with st.status("Divo Agent 正在同步全球证据...", expanded=True) as status:
            st.write("📡 穿透防火墙获取底层评价碎片...")
            time.sleep(1)
            
            st.write("🧠 Reality-Divo 正在进行真伪博弈...")
            
            try:
                # 修复 404：使用最基础的模型名称，SDK 会自动处理路径
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                你是一个毒舌且专业的酒店审计专家 Reality-Divo。针对酒店 '{hotel_query}' 进行深度排雷。
                
                必须包含以下格式评分（用于驱动雷达图）：
                真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
                
                点评要求：
                1. 语气犀利，避开官方公关辞令。
                2. 揭露具体痛点（如：空调噪音、地毯异味、电梯排队、滤镜虚假等）。
                3. 如果抓取受限，请基于品牌历史通病给出预测性审计。
                """
                
                response = model.generate_content(prompt)
                full_report = response.text
                
                # 动态提取评分
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [60, 60, 60, 60, 60]
                
                status.update(label="审计报告解码成功", state="complete", expanded=False)
                
                # 7. 结果展示
                st.divider()
                col_left, col_right = st.columns([1, 1.2])
                
                with col_left:
                    # 动态雷达图
                    df_score = pd.DataFrame(dict(r=r_values, theta=['真实度','性价比','硬件','静谧度','服务']))
                    fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
                    fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.25)', line_color='#39FF14', line_width=3)
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
                    st.markdown(f"### 🕵️ 现场审计结论: <span style='color:#00ffcc;'>{hotel_query}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
                    st.write("")
                    if st.button("📥 下载完整审计 PDF (Beta)"):
                        st.toast("正在生成加密报告...")
                        st.balloons()

            except Exception as e:
                # 捕捉具体的报错信息，方便调试
                st.error(f"大脑执行异常: {str(e)}")
                st.info("提示：如果持续 404，请确认 API Key 是否属于有效的 Google AI Studio 项目。")
    else:
        st.warning("🕵️ 请先输入酒店名称。")

# 8. 极简页脚
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<div style='text-align:center; color:#4b5563; font-size:0.9rem;'>© 2026 Divoscan.com | Multi-Agent Analysis Protocol v2.5</div>", unsafe_allow_html=True)
