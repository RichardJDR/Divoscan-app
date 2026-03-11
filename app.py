import streamlit as st
import time

# 1. 页面配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 2. 自定义品牌样式
st.markdown("""
<style>
.main { background-color: #0e1117; color: white; }
.divo-title { color: #00ffcc; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 3rem; text-align: center; }
.divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; }
.stMetric { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. 头部：Logo 与 Slogan
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)

# 4. 搜索区
hotel_query = st.text_input("", placeholder="输入酒店名称（如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
if hotel_query:
# 进度条模拟 Agent 协作
progress_text = "Divo Agent 协作中：正在抓取全网数据并分析真实隔音与视野..."
my_bar = st.progress(0, text=progress_text)

for percent_complete in range(100):
time.sleep(0.02)
my_bar.progress(percent_complete + 1, text=progress_text)

st.divider()

# 结果展示
col1, col2, col3 = st.columns(3)

# 核心判定逻辑
if "艾美" in hotel_query or "Saigon" in hotel_query:
with col1:
st.metric("Price-Divo", "隐藏税费预警", delta="⚠️ 15% VAT/Service")
st.write("越南当地预订常不含税。")
with col2:
st.metric("Reality-Divo", "噪音指数 78", delta="严重")
st.write("低楼层受摩托车流影响，建议选 15 层以上。")
with col3:
st.metric("Comfort-Divo", "环境评分 88", delta="稳定")
st.write("西贡河景无遮挡，行政酒廊好评。")
else:
with col1:
st.metric("Price-Divo", "监测中", delta="Waiting")
with col2:
st.metric("Reality-Divo", "扫描中", delta="Waiting")
with col3:
st.metric("Comfort-Divo", "核验中", delta="Waiting")

st.info(f"💡 DivoScan 建议：{hotel_query} 扫描完成。")
else:
st.warning("请输入酒店名字！")

# 5. 页脚
st.caption("© 2026 Divoscan.com | Multi-Agent Intelligence System")
