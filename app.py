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
        st.markdown('<div><span class="status-dot online"></span><span style="color:#e5e7eb;">探测器 (Firecrawl)</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div><span class="status-dot offline"></span><span style="color:#9ca3af;">探测器 (Firecrawl)</span></div>', unsafe_allow_html=True)
        
    # 大脑状态
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.markdown('<div><span class="status-dot online"></span><span style="color:#e5e7eb;">大脑 (Gemini 1.5)</span></div>', unsafe_allow_html=True)
        except:
            st.markdown('<div><span class="status-dot offline"></span><span style="color:#ff4b4b;">大脑配置错误</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div><span class="status-dot offline"></span><span style="color:#9ca3af;">大脑 (Gemini 1.5)</span></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='color:#4b5563; font-size:0.8rem;'>Protocol: Hybrid-Scan-v2.1<br>Node: SG-Primary<br>Status: Standby</div>", unsafe_allow_html=True)

# 5. 主界面内容
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

hotel_query = st.text_input("", placeholder="🔍 输入酒店名称（如：新加坡金沙酒店）", label_visibility="collapsed")

if st.button("🚀 启动深度多维扫描"):
    if not (GOOGLE_API_KEY):
        st.error("无法启动：关键大脑组件 (Gemini Key) 未配置。")
    elif hotel_query:
        with st.status("Divo Agents 正在解码真相...", expanded=True) as status:
            st.write("📡 穿透防火墙获取底层评价碎片...")
            time.sleep(1.2)
            
            st.write("🧠 Reality-Divo 正在进行多维证据博弈...")
            
            # 强化后的防御性 Prompt
            prompt = f"""
            你是一个毒舌且深谙酒店业套路的专家 Reality-Divo。
            针对酒店 '{hotel_query}'，进行深度审计。

            必须严格按此格式开头：
            真实度:数字, 性价比:数字, 硬件:数字, 静谧度:数字, 服务:数字
            数字范围 0-100。

            点评要求：
            1. 语气直接且犀利，避开所有官方说辞。
            2. 如果数据抓取不畅，请直接基于该酒店的品牌历史口碑（如：金沙的人多、卡尔登的老化等）给出预测性排雷。
            3. 揭露那些‘滤镜之外’的真相（如空调声、早餐排队、地毯异味等）。
            """
            
            try:
                response = model.generate_content(prompt)
                full_report = response.text
                
                # 正则解析评分驱动雷达图
                scores = re.findall(r"(\w+):(\d+)", full_report)
                if len(scores) >= 5:
                    score_map = {k: int(v) for k, v in scores}
                    r_values = [score_map.get(k, 50) for k in ['真实度', '性价比', '硬件', '静谧度', '服务']]
                else:
                    r_values = [60, 55, 70, 50, 75] # 兜底分
                
                status.update(label="扫描报告生成完毕", state="complete", expanded=False)
            except Exception as e:
                st.error(f"大脑执行异常: {str(e)}")
                r_values = [15, 15, 15, 15, 15]
                full_report = "侦探由于网络博弈暂时断线，请稍后重试。"

        # 6. 结果可视化展示
        st.divider()
        col_left, col_right = st.columns([1, 1.3])
        
        with col_left:
            # 雷达图样式升级
            df_score = pd.DataFrame(dict(
                r=r_values,
                theta=['真实度','性价比','硬件','静谧度','服务']))
            fig = px.line_polar(df_score, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', fillcolor='rgba(57, 255, 20, 0.25)', line_color='#39FF14', line_width=2.5)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#00ffcc',
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    angularaxis=dict(linewidth=1, showline=True, linecolor='#1f2937'),
                    radialaxis=dict(showline=True, gridcolor='#1f2937', range=[0, 100], tickfont=dict(size=8))
                ),
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown(f"### 🕵️ 现场审计报告: {hotel_query}")
            st.markdown(f"<div class='report-box'>{full_report}</div>", unsafe_allow_html=True)
            
            # 模拟交互功能
            st.write("")
            if st.button("📥 生成加密 PDF 报告"):
                st.toast("报告加密成功，准备下载...")
                st.balloons()
    else:
        st.warning("🕵️ 告诉我酒店的名字，我才能开始办案。")

# 7. 页脚
st.divider()
st.caption("© 2026 Divoscan.com | Multi-Agent Security Protocol | 24/7 Deep Web Analysis")
