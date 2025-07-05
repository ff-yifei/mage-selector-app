import streamlit as st
from PIL import Image
import os
import glob
from collections import defaultdict

st.set_page_config(layout="wide", page_title="多级目录图片展示系统")
st.title("📂 多级目录图片展示系统")



# 路径配置
BASE_DIR = "images"
UMAP_DIR = os.path.join(BASE_DIR, "images")
VIOLIN_DIR = os.path.join(BASE_DIR, "VlnPlot")

# 创建目录结构（如果不存在）
def create_dirs():
    for path in [UMAP_DIR, VIOLIN_DIR]:
        if not os.path.exists(path):
            os.makedirs(path)

# 递归获取目录结构
def get_directory_structure(rootdir):
    dir_structure = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = dir_structure
        for folder in folders:
            parent = parent.setdefault(folder, {})
        parent.update(subdir)
    return dir_structure

# 递归获取所有图片文件
@st.cache_data(ttl=300)
def get_all_image_files(directory):
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
    return image_files

# 从路径中提取基因名称
def extract_gene_name(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    # 尝试从文件名中提取基因名称（去掉后缀）
    return filename.split("_")[0] if "_" in filename else filename

# 显示目录树
def display_directory_tree(tree, path=""):
    for key, value in tree.items():
        full_path = os.path.join(path, key)
        if isinstance(value, dict):  # 文件夹
            with st.expander(f"📁 {key}", expanded=False):
                display_directory_tree(value, full_path)
        else:  # 文件
            st.markdown(f'<div class="file-item">{key}</div>', unsafe_allow_html=True)

# 创建基因到文件路径的映射
def create_gene_map(files):
    gene_map = defaultdict(list)
    for file in files:
        gene = extract_gene_name(file)
        gene_map[gene].append(file)
    return gene_map

# 确保目录存在
create_dirs()

# 获取所有图片文件
umap_files = get_all_image_files(UMAP_DIR)
violin_files = get_all_image_files(VIOLIN_DIR)

# 创建基因映射
umap_gene_map = create_gene_map(umap_files)
violin_gene_map = create_gene_map(violin_files)

# 获取基因列表
umap_genes = sorted(umap_gene_map.keys())
violin_genes = sorted(violin_gene_map.keys())

# 获取目录结构
umap_structure = get_directory_structure(UMAP_DIR)
violin_structure = get_directory_structure(VIOLIN_DIR)

# 侧边栏
with st.sidebar:
    st.markdown("## 🗂️ 目录浏览器")
    
    tab1, tab2 = st.tabs(["UMAP 结构", "Violin 结构"])
    
    with tab1:
        st.subheader("UMAP 目录结构")
        if umap_structure:
            display_directory_tree(umap_structure, UMAP_DIR)
        else:
            st.info("UMAP 目录为空")
    
    with tab2:
        st.subheader("Violin 目录结构")
        if violin_structure:
            display_directory_tree(violin_structure, VIOLIN_DIR)
        else:
            st.info("Violin 目录为空")
    
    st.markdown("---")
    st.markdown("## 🔧 控制面板")
    
    # UMAP 部分
    st.markdown("### UMAP 图")
    umap_gene = st.selectbox("选择基因 (UMAP)", umap_genes, index=0 if umap_genes else None)
    
    # Violin 部分
    st.markdown("### Violin 图")
    violin_gene = st.selectbox("选择基因 (Violin)", violin_genes, index=0 if violin_genes else None)
    
    # 刷新按钮
    if st.button("刷新图片列表", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 系统信息")
    st.info(f"UMAP 图片数量: {len(umap_files)}")
    st.info(f"Violin 图片数量: {len(violin_files)}")
    st.info(f"UMAP 基因数量: {len(umap_genes)}")
    st.info(f"Violin 基因数量: {len(violin_genes)}")

# 主内容区
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("UMAP 图预览")
    if umap_gene and umap_gene in umap_gene_map:
        files = umap_gene_map[umap_gene]
        
        if len(files) > 1:
            tabs = st.tabs([os.path.basename(os.path.dirname(f)) or "根目录" for f in files])
            for tab, file in zip(tabs, files):
                with tab:
                    st.markdown(f'<div class="selected-path">{file}</div>', unsafe_allow_html=True)
                    st.image(Image.open(file), use_container_width=True)
        else:
            st.markdown(f'<div class="selected-path">{files[0]}</div>', unsafe_allow_html=True)
            st.image(Image.open(files[0]), use_container_width=True)
    elif umap_genes:
        st.info("请从左侧选择基因")
    else:
        st.warning("UMAP 目录中没有图片")

with col2:
    st.subheader("Violin 图预览")
    if violin_gene and violin_gene in violin_gene_map:
        files = violin_gene_map[violin_gene]
        
        if len(files) > 1:
            tabs = st.tabs([os.path.basename(os.path.dirname(f)) or "根目录" for f in files])
            for tab, file in zip(tabs, files):
                with tab:
                    st.markdown(f'<div class="selected-path">{file}</div>', unsafe_allow_html=True)
                    st.image(Image.open(file), use_container_width=True)
        else:
            st.markdown(f'<div class="selected-path">{files[0]}</div>', unsafe_allow_html=True)
            st.image(Image.open(files[0]), use_container_width=True)
    elif violin_genes:
        st.info("请从左侧选择基因")
    else:
        st.warning("Violin 目录中没有图片")
        
