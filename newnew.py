import streamlit as st
from PIL import Image
import os
import base64
import requests
from io import BytesIO, StringIO
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="GitHub 基因图片智能定位系统")
st.title("🧬 GitHub 基因图片智能定位系统")

# 自定义CSS样式
st.markdown("""
<style>
    .github-card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid #6f42c1;
    }
    .path-info {
        background-color: #e9f7fe;
        padding: 12px;
        border-radius: 5px;
        margin: 15px 0;
        font-family: monospace;
    }
    .github-indicator {
        display: inline-flex;
        align-items: center;
        background-color: #e0f2fe;
        padding: 5px 10px;
        border-radius: 15px;
        margin-right: 8px;
        margin-bottom: 8px;
        font-size: 0.9em;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        border-radius: 5px 5px 0 0 !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e9f7fe !important;
    }
    .warning-box {
        background-color: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 15px 0;
        border-radius: 0 4px 4px 0;
    }
    .gene-list-item {
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .gene-list-item:hover {
        background-color: #e9f7fe;
    }
    .gene-list-item.selected {
        background-color: #6f42c1;
        color: white;
        font-weight: bold;
    }
    .search-section {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .image-preview {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        background-color: #ffffff;
    }
    @media (max-width: 768px) {
        .gene-grid {
            grid-template-columns: repeat(3, 1fr) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 配置参数
REPO_OWNER = "ff-yifei"                # GitHub用户名或组织名
REPO_NAME = "mage-selector-app"        # 仓库名称
BRANCH = "main"                        # 分支名称
UMAP_CONFIG_PATH = "images-mapping.csv"  # UMAP CSV文件路径
VIOLIN_CONFIG_PATH = "mapping-violin.csv"  # Violin CSV文件路径
CSV_DELIMITER = "/"                    # CSV分隔符
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "your-github-token")  # 从secrets获取token

# 获取GitHub API头信息
def get_github_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN and GITHUB_TOKEN != "your-github-token":
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

# 获取GitHub文件内容
@st.cache_data(ttl=600, show_spinner="正在从GitHub加载数据...")
def get_github_file_content(path):
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref={BRANCH}"
    try:
        response = requests.get(api_url, headers=get_github_headers())
        response.raise_for_status()
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    except requests.exceptions.HTTPError as e:
        st.error(f"GitHub API错误 ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        st.error(f"无法从GitHub获取文件: {str(e)}")
    return ""

# 获取GitHub目录结构
@st.cache_data(ttl=600)
def get_github_directory_structure(path):
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref={BRANCH}"
    try:
        response = requests.get(api_url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"无法获取目录结构: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        st.error(f"获取目录结构时出错: {str(e)}")
    return []

# 从CSV内容解析基因路径信息
def parse_gene_paths_from_csv(csv_content, gene_col="gene", path_col="image_path"):
    gene_paths = {}
    
    try:
        # 使用pandas解析CSV
        df = pd.read_csv(StringIO(csv_content), sep=CSV_DELIMITER)
        
        # 识别列
        if gene_col in df.columns:
            gene_col_name = gene_col
        else:
            gene_col_name = df.columns[0]
            
        if path_col in df.columns:
            path_col_name = path_col
        else:
            path_col_name = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        # 创建基因路径字典
        for _, row in df.iterrows():
            gene = str(row[gene_col_name]).strip()
            path = str(row[path_col_name]).strip()
            if gene and path:
                gene_paths[gene] = path
                
        return gene_paths
    
    except Exception as e:
        st.error(f"解析CSV文件时出错: {str(e)}")
        return {}

# 从GitHub获取基因路径信息
def get_gene_paths_from_github(config_path, gene_col="gene", path_col="image_path"):
    content = get_github_file_content(config_path)
    if content:
        gene_paths = parse_gene_paths_from_csv(content, gene_col, path_col)
        if gene_paths:
            return gene_paths
        else:
            st.error(f"基因路径文件 '{config_path}' 格式不正确或未找到有效数据。")
    else:
        st.error(f"无法从路径 '{config_path}' 加载基因路径文件")
    return {}

# 获取GitHub原始文件URL
def get_github_raw_url(path):
    return f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{path}"

# 获取基因列表
def get_gene_list(gene_paths):
    return sorted(gene_paths.keys())

# 显示基因列表
def display_gene_list(genes, selected_gene, section_id):
    st.markdown(f'<div class="gene-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">', unsafe_allow_html=True)
    
    for gene in genes:
        class_name = "selected" if gene == selected_gene else ""
        st.markdown(
            f'<div class="gene-list-item {class_name}" onclick="selectGene_{section_id}(\'{gene}\')">{gene}</div>', 
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# 获取GitHub图片
def get_github_image(gene_path):
    try:
        img_url = get_github_raw_url(gene_path)
        response = requests.get(img_url, headers=get_github_headers(), stream=True)
        response.raise_for_status()
        
        img_data = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            img_data.write(chunk)
        img_data.seek(0)
        
        return Image.open(img_data)
    except requests.exceptions.HTTPError as e:
        st.error(f"图片加载错误 ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        st.error(f"加载图片时出错: {str(e)}")
    
    return None

# 显示图片预览
def display_image_preview(gene, gene_path, image_type):
    with st.container():
        st.markdown(f"""
        <div class='github-card'>
            <h3>{gene} {image_type}图片信息</h3>
            <p>图片路径: <code>{gene_path}</code></p>
            <p>完整URL: <a href="{get_github_raw_url(gene_path)}" target="_blank">{get_github_raw_url(gene_path)}</a></p>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        with st.spinner(f"正在加载{image_type}图片..."):
            image = get_github_image(gene_path)
        
        if image:
            st.image(image, caption=f"{gene} {image_type}图片", use_column_width=True)
        else:
            st.warning(f"无法加载{image_type}图片，请检查路径是否正确")
            
            # 尝试显示目录内容
            dir_path = os.path.dirname(gene_path)
            if dir_path:
                st.info(f"尝试显示目录内容: {dir_path}")
                try:
                    dir_content = get_github_directory_structure(dir_path)
                    
                    if dir_content and isinstance(dir_content, list):
                        st.write("目录内容:")
                        for item in dir_content:
                            st.write(f"- {item['name']} ({item['type']})")
                    else:
                        st.write("无法获取目录内容")
                except:
                    st.write("获取目录内容时出错")
    except Exception as e:
        st.error(f"加载{image_type}图片时出错: {str(e)}")

# 显示路径分析信息
def display_path_analysis(gene_path, genes, image_type):
    st.subheader(f"{image_type}图片详细信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 路径分析")
        st.code(f"文件名: {os.path.basename(gene_path)}")
        st.code(f"目录: {os.path.dirname(gene_path)}")
        st.code(f"扩展名: {os.path.splitext(gene_path)[1]}")
        
        # 检查文件是否存在
        try:
            response = requests.head(get_github_raw_url(gene_path), headers=get_github_headers())
            exists = response.status_code == 200
            st.code(f"文件状态: {'✅ 存在' if exists else '❌ 不存在'}")
            if not exists:
                st.warning("文件在指定路径不存在，请检查基因路径配置")
        except:
            st.code("文件状态: ❓未知")
    
    with col2:
        st.markdown("### GitHub API信息")
        st.code(f"仓库: {REPO_OWNER}/{REPO_NAME}")
        st.code(f"分支: {BRANCH}")
        st.code(f"配置文件: {UMAP_CONFIG_PATH if image_type == 'UMAP' else VIOLIN_CONFIG_PATH}")
        st.code(f"基因数量: {len(genes)}")

# 主应用程序逻辑
def main():
    # 加载基因路径信息
    with st.spinner("正在加载基因数据..."):
        umap_gene_paths = get_gene_paths_from_github(UMAP_CONFIG_PATH, gene_col="gene", path_col="umap_path")
        violin_gene_paths = get_gene_paths_from_github(VIOLIN_CONFIG_PATH, gene_col="gene", path_col="violin_path")
    
    umap_genes = get_gene_list(umap_gene_paths) if umap_gene_paths else []
    violin_genes = get_gene_list(violin_gene_paths) if violin_gene_paths else []
    
    # 侧边栏 - 分为上下两部分
    with st.sidebar:
        # 上半部分：UMAP搜索
        st.markdown("## 🔍 UMAP 图片搜索")
        st.markdown("根据基因名称搜索UMAP图片")
        
        # UMAP基因搜索
        umap_search_term = st.text_input("搜索基因 (UMAP)", "", key="umap_gene_search")
        
        # 过滤UMAP基因列表
        filtered_umap_genes = [g for g in umap_genes if not umap_search_term or umap_search_term.lower() in g.lower()]
        
        # 选择UMAP基因
        if filtered_umap_genes:
            selected_umap_gene = st.selectbox(
                "选择基因 (UMAP)",
                filtered_umap_genes,
                index=0,
                key="umap_gene_selector"
            )
        else:
            selected_umap_gene = None
            st.warning("没有匹配的基因")
        
        st.markdown("---")
        
        # 下半部分：Violin搜索
        st.markdown("## 📊 Violin 图片搜索")
        st.markdown("根据基因名称搜索Violin图片")
        
        # Violin基因搜索
        violin_search_term = st.text_input("搜索基因 (Violin)", "", key="violin_gene_search")
        
        # 过滤Violin基因列表
        filtered_violin_genes = [g for g in violin_genes if not violin_search_term or violin_search_term.lower() in g.lower()]
        
        # 选择Violin基因
        if filtered_violin_genes:
            selected_violin_gene = st.selectbox(
                "选择基因 (Violin)",
                filtered_violin_genes,
                index=0,
                key="violin_gene_selector"
            )
        else:
            selected_violin_gene = None
            st.warning("没有匹配的基因")
        
        st.markdown("---")
        
        # 控制面板
        st.markdown("## ⚙️ 控制面板")
        show_details = st.checkbox("显示详细信息", True)
        
        # 刷新按钮
        if st.button("刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 主内容区
    col1, col2 = st.columns(2)
    
    # UMAP图片显示
    with col1:
        st.subheader("UMAP 图片预览")
        if selected_umap_gene and umap_gene_paths:
            gene_path = umap_gene_paths.get(selected_umap_gene)
            if gene_path:
                display_image_preview(selected_umap_gene, gene_path, "UMAP")
                
                if show_details:
                    display_path_analysis(gene_path, umap_genes, "UMAP")
            else:
                st.error(f"找不到 {selected_umap_gene} 的UMAP图片路径")
        else:
            st.info("请在左侧选择基因以显示UMAP图片")
            
            # 显示UMAP基因列表
            if umap_genes:
                st.subheader("可用UMAP基因")
                display_gene_list(umap_genes, selected_umap_gene if 'selected_umap_gene' in locals() else None, "umap")
    
    # Violin图片显示
    with col2:
        st.subheader("Violin 图片预览")
        if selected_violin_gene and violin_gene_paths:
            gene_path = violin_gene_paths.get(selected_violin_gene)
            if gene_path:
                display_image_preview(selected_violin_gene, gene_path, "Violin")
                
                if show_details:
                    display_path_analysis(gene_path, violin_genes, "Violin")
            else:
                st.error(f"找不到 {selected_violin_gene} 的Violin图片路径")
        else:
            st.info("请在左侧选择基因以显示Violin图片")
            
            # 显示Violin基因列表
            if violin_genes:
                st.subheader("可用Violin基因")
                display_gene_list(violin_genes, selected_violin_gene if 'selected_violin_gene' in locals() else None, "violin")
    
    # 添加JavaScript函数处理基因点击
    st.markdown("""
    <script>
    function selectGene_umap(gene) {
        // 更新UMAP基因选择器
        const selectBox = window.parent.document.querySelector('select[aria-label="选择基因 (UMAP)"]');
        if (selectBox) {
            selectBox.value = gene;
            const event = new Event('change');
            selectBox.dispatchEvent(event);
        }
        
        // 滚动到顶部
        window.parent.scrollTo(0, 0);
    }
    
    function selectGene_violin(gene) {
        // 更新Violin基因选择器
        const selectBox = window.parent.document.querySelector('select[aria-label="选择基因 (Violin)"]');
        if (selectBox) {
            selectBox.value = gene;
            const event = new Event('change');
            selectBox.dispatchEvent(event);
        }
        
        // 滚动到顶部
        window.parent.scrollTo(0, 0);
    }
    </script>
    """, unsafe_allow_html=True)

# 运行主应用程序
if __name__ == "__main__":
    main()
