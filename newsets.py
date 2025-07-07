import streamlit as st
from PIL import Image
import os
import base64
import json
import requests
from io import BytesIO
import re

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
    }
    .gene-list-item:hover {
        background-color: #e9f7fe;
    }
    .gene-list-item.selected {
        background-color: #6f42c1;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# GitHub 配置
GITHUB_REPO_OWNER = "your-github-username"
GITHUB_REPO_NAME = "your-repository-name"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")  # 从Streamlit secrets获取

# 基础路径
BASE_PATH = "data/images"

# 获取GitHub API头信息
def get_github_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

# 获取GitHub文件内容
@st.cache_data(ttl=600)  # 缓存10分钟
def get_github_file_content(path):
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{path}?ref={GITHUB_BRANCH}"
    try:
        response = requests.get(api_url, headers=get_github_headers())
        response.raise_for_status()
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    except Exception as e:
        st.error(f"无法从GitHub获取文件: {str(e)}")
        return ""

# 获取GitHub目录结构
@st.cache_data(ttl=600)
def get_github_directory_structure(path):
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{path}?ref={GITHUB_BRANCH}"
    try:
        response = requests.get(api_url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"无法从GitHub获取目录结构: {str(e)}")
        return []

# 从GitHub文件解析基因路径信息
def parse_gene_paths_from_github(file_content):
    gene_paths = {}
    
    # 尝试解析为JSON
    try:
        data = json.loads(file_content)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    
    # 尝试解析为键值对格式
    pattern = re.compile(r'^([^:]+):\s*(.+)$', re.MULTILINE)
    matches = pattern.findall(file_content)
    
    if matches:
        for gene, path in matches:
            gene_paths[gene.strip()] = path.strip()
    
    return gene_paths

# 从GitHub获取基因路径信息
def get_gene_paths_from_github():
    # 尝试可能的文件路径
    possible_paths = [
        "gene_paths.json",
        "data/gene_paths.txt",
        "config/gene_paths.cfg",
        "gene_data/paths.json"
    ]
    
    for path in possible_paths:
        content = get_github_file_content(path)
        if content:
            gene_paths = parse_gene_paths_from_github(content)
            if gene_paths:
                return gene_paths
    
    return {}

# 获取GitHub原始文件URL
def get_github_raw_url(path):
    return f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/{GITHUB_BRANCH}/{path}"

# 获取基因列表
def get_gene_list(gene_paths):
    return sorted(gene_paths.keys())

# 显示基因列表
def display_gene_list(genes, selected_gene):
    cols = 5
    rows = (len(genes) + cols - 1) // cols
    
    for i in range(rows):
        with st.container():
            col_list = st.columns(cols)
            for j in range(cols):
                idx = i * cols + j
                if idx < len(genes):
                    gene = genes[idx]
                    col = col_list[j]
                    
                    class_name = "selected" if gene == selected_gene else ""
                    col.markdown(
                        f'<div class="gene-list-item {class_name}" onclick="selectGene(\'{gene}\')">{gene}</div>', 
                        unsafe_allow_html=True
                    )

# 获取GitHub图片
def get_github_image(gene_path):
    try:
        # 尝试直接获取图片
        img_url = get_github_raw_url(gene_path)
        response = requests.get(img_url, stream=True)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except:
        # 尝试获取文件内容
        content = get_github_file_content(gene_path)
        if content:
            try:
                # 尝试从base64解码
                return Image.open(BytesIO(base64.b64decode(content)))
            except:
                pass
    return None

# 主应用
def main():
    # 加载基因路径信息
    gene_paths = get_gene_paths_from_github()
    
    if not gene_paths:
        st.error("未找到基因路径信息文件！请确保GitHub仓库中存在以下文件之一：")
        st.info("- gene_paths.json")
        st.info("- data/gene_paths.txt")
        st.info("- config/gene_paths.cfg")
        st.info("- gene_data/paths.json")
        return
    
    genes = get_gene_list(gene_paths)
    
    # 侧边栏
    with st.sidebar:
        st.markdown(f"## 🧬 基因选择 ({len(genes)})")
        
        # 基因搜索
        search_term = st.text_input("搜索基因", "")
        
        # 过滤基因列表
        filtered_genes = [g for g in genes if not search_term or search_term.lower() in g.lower()]
        
        # 选择基因
        if filtered_genes:
            selected_gene = st.selectbox(
                "选择基因",
                filtered_genes,
                index=0,
                key="gene_selector"
            )
        else:
            selected_gene = None
            st.warning("没有匹配的基因")
        
        st.markdown("---")
        st.markdown("## 🔧 控制面板")
        
        # 显示选项
        show_details = st.checkbox("显示详细信息", True)
        show_image = st.checkbox("显示图片", True)
        
        # 刷新按钮
        if st.button("刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 仓库信息")
        st.info(f"仓库: {GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")
        st.info(f"分支: {GITHUB_BRANCH}")
        st.info(f"基因数量: {len(genes)}")

    # 主内容区
    if selected_gene:
        gene_path = gene_paths.get(selected_gene)
        
        if not gene_path:
            st.error(f"找不到 {selected_gene} 的图片路径")
            return
            
        # 显示基因信息卡片
        with st.container():
            st.markdown(f"""
            <div class='github-card'>
                <h3>{selected_gene} 基因信息</h3>
                <p>图片路径: <code>{gene_path}</code></p>
                <p>完整URL: <a href="{get_github_raw_url(gene_path)}" target="_blank">{get_github_raw_url(gene_path)}</a></p>
            </div>
            """, unsafe_allow_html=True)
        
        # 显示图片
        if show_image:
            st.subheader("图片预览")
            
            try:
                # 尝试获取图片
                image = get_github_image(gene_path)
                
                if image:
                    st.image(image, caption=f"{selected_gene} 图片", use_container_width=True)
                else:
                    st.warning("无法加载图片，请检查路径是否正确")
                    
                    # 尝试显示目录内容
                    st.info("尝试显示路径内容:")
                    dir_path = os.path.dirname(gene_path)
                    dir_content = get_github_directory_structure(dir_path)
                    
                    if dir_content and isinstance(dir_content, list):
                        st.write(f"目录内容: {dir_path}")
                        for item in dir_content:
                            st.write(f"- {item['name']} ({item['type']})")
                    else:
                        st.write("无法获取目录内容")
            except Exception as e:
                st.error(f"加载图片时出错: {str(e)}")
        
        # 显示详细信息
        if show_details:
            st.subheader("详细信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 路径分析")
                st.code(f"文件名: {os.path.basename(gene_path)}")
                st.code(f"目录: {os.path.dirname(gene_path)}")
                st.code(f"扩展名: {os.path.splitext(gene_path)[1]}")
                
                # 检查文件是否存在
                try:
                    response = requests.head(get_github_raw_url(gene_path))
                    exists = response.status_code == 200
                    st.code(f"文件状态: {'存在' if exists else '不存在'}")
                except:
                    st.code("文件状态: 未知")
            
            with col2:
                st.markdown("### GitHub API信息")
                st.code(f"仓库: {GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")
                st.code(f"分支: {GITHUB_BRANCH}")
                st.code(f"最后更新: 从缓存获取")
    
    # 所有基因列表
    st.subheader("所有可用基因")
    display_gene_list(genes, selected_gene)
    
    # 添加JavaScript函数处理基因点击
    st.markdown("""
    <script>
    function selectGene(gene) {
        window.parent.document.querySelectorAll('.gene-list-item').forEach(el => {
            el.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // 设置选择框的值
        const selectBox = window.parent.document.querySelector('select[aria-label="选择基因"]');
        selectBox.value = gene;
        
        // 触发变更事件
        const event = new Event('change');
        selectBox.dispatchEvent(event);
    }
    </script>
    """, unsafe_allow_html=True)

# 运行应用
if __name__ == "__main__":
    main()
