import streamlit as st
from PIL import Image
import os

st.title("图片选择展示网站")

# 左侧参数选择
feature1 = st.sidebar.selectbox("选择 Gene", ["ACTA2","CD3D", "CD3E","CD4","CD8A", "CD14","CD68","CD79A","CLEC10A","COL1A1","CSF3R","DCN","FAP","FOXP3","IGHG1","IGKC","JCHAIN","KRT8","KRT18","KRT19","NKG7","TPSB2","VWF","EPCAM"])
submit = st.sidebar.button("提交")

# 显示图片
if submit:
    image_path = f"images/{feature1}.png"
    if os.path.exists(image_path):
        st.image(Image.open(image_path), caption=f"{feature1}", use_column_width=True)
    else:
        st.warning("找不到对应的图片，请确认参数组合和文件名是否一致。")

