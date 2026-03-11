import streamlit as st
import time

# 页面配置
st.set_page_config(page_title="DivoScan - AI 住宿侦探", page_icon="🔍", layout="wide")

# 自定义品牌样式
st.markdown("""
<style>
.main { background-color: #0e1117; color: white; }
.divo-title { color: #00ffcc; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 3rem; text-align: center; }
.divo-slogan { color: #39FF14; text-align: center; font-style: italic; margin-bottom: 30px; }
.stMetric { background-color: #1a1c24; border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# 头部：Logo 与 Slogan
st.markdown("<div class='divo-title'>DivoScan.com</div>", unsafe_allow_html=True)
st.markdown("<div class='divo-slogan'>The truth behind the filters. (滤镜背后的住宿真相)</div>", unsafe_allow_html=True)
# 搜索区
hotel_query = st.text_input("", placeholder="输入酒店名称（如：胡志明市艾美酒店）", label_visibility="collapsed")

if st.button("🚀 启动 AI 多维扫描"):
    if hotel_query:
  # 进度条模拟 Agent 协作
        progress_text = "Divo Agent 协作中：正在抓取全网社交媒体与实时噪音数据..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.02)
my_bar.progress(percent_complete + 1, text=progress_text)

        st.divider()

# 结果展示
col1, col2, col3 = st.columns(3)
# 逻辑判定：针对胡志明市艾美酒店的硬核输出
if "艾美" in hotel_query or "Le Meridien" in hotel_query:
with col1:
st.metric("Price-Divo", "隐藏税费预警", delta="⚠️ 15% VAT/Service")
st.write("注意：越南酒店常不含税。")
with col2:
st.metric("Reality-Divo", "噪音指数 78", delta="严重")
st.write("低楼层受西贡河岸摩托车流噪音影响显著。")
with col3:
st.metric("Comfort-Divo", "环境评分 88", delta="稳定")
st.write("西贡河景视角无遮挡，酒廊口碑极佳。")
else:
# 通用模拟
with col1:
st.metric("Price-Divo", "价格波动", delta="监测中")
with col2:
st.metric("Reality-Divo", "真实度扫描", delta="待抓取")
with col3:
st.metric("Comfort-Divo", "硬件评分", delta="待核验")
st.info(f"💡 DivoScan 建议：{hotel_query} 扫描完成。建议选择 15 层以上房间以规避街道噪音。")
else:
st.warning("请输入酒店名字！")

# 页脚
st.caption("© 2026 Divoscan.com | Multi-Agent Intelligence System")
