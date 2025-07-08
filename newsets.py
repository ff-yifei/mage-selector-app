import streamlit as st
from PIL import Image
import os
import base64
import requests
from io import BytesIO, StringIO
import re
import csv
import pandas as pd

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
    @media (max-width: 768px) {
        .gene-grid {
            grid-template-columns: repeat(3, 1fr) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 从环境变量获取GitHub仓库配置
REPO_OWNER = st.secrets.get("REPO_OWNER", "ff-yifei")
REPO_NAME = st.secrets.get("REPO_NAME", "mage-selector-app")
BRANCH = st.secrets.get("BRANCH", "main")
CONFIG_PATH = st.secrets.get("CONFIG_PATH", "gene_paths.csv")
CSV_DELIMITER = st.secrets.get("CSV_DELIMITER", " ")
HAS_HEADER = st.secrets.get("HAS_HEADER", "true").lower() == "true"
GENE_COLUMN = st.secrets.get("GENE_COLUMN", "Gene")
PATH_COLUMN = st.secrets.get("PATH_COLUMN", "image_path")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")




# 获取GitHub API头信息
def get_github_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    return headers

# 获取GitHub文件内容
@st.cache_data(ttl=600, show_spinner="正在从GitHub加载数据...")
def get_github_file_content(path):
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}"
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
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={branch}"
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
def parse_gene_paths_from_csv(mapping.csv):
    gene_paths = {}
    
    # 使用StringIO将字符串转换为类文件对象
    csv_data = StringIO(mapping.csv)
    
    try:
        # 尝试使用pandas解析CSV
        try:
            df = pd.read_csv(
                mapping.csv, 
                sep=csv_delimiter,
                header=0 if has_header else None
            )
            
            # 尝试通过列名或索引识别列
            if isinstance(gene_column, str) and gene_column in df.columns:
                gene_col = gene_column
            elif isinstance(gene_column, int) and gene_column < len(df.columns):
                gene_col = df.columns[gene_column]
            else:
                gene_col = df.columns[0]  # 默认第一列
                
            if isinstance(path_column, str) and path_column in df.columns:
                path_col = path_column
            elif isinstance(path_column, int) and path_column < len(df.columns):
                path_col = df.columns[path_column]
            else:
                path_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]  # 默认第二列
            
            # 创建基因路径字典
            for _, row in df.iterrows():
                gene = str(row[gene_col]).strip()
                path = str(row[path_col]).strip()
                if gene and path:
                    gene_paths[gene] = path
                    
            return gene_paths
        except Exception as e:
            st.warning(f"Pandas解析失败: {str(e)}，尝试使用CSV模块")
        
        # 重置StringIO对象
        csv_data.seek(0)
        
        # 使用csv模块作为备选方案
        reader = csv.reader(csv_data, delimiter=csv_delimiter)
        rows = list(reader)
        
        # 处理标题行
        if has_header and rows:
            header = rows[0]
            rows = rows[1:]
            
            # 识别列索引
            if isinstance(gene_column, str) and gene_column in header:
                gene_idx = header.index(gene_column)
            else:
                gene_idx = 0
                
            if isinstance(path_column, str) and path_column in header:
                path_idx = header.index(path_column)
            else:
                path_idx = 1 if len(header) > 1 else 0
        else:
            gene_idx = 0
            path_idx = 1 if len(rows[0]) > 1 else 0 if rows else None
        
        # 处理数据行
        for row in rows:
            if len(row) > max(gene_idx, path_idx):
                gene = str(row[gene_idx]).strip()
                path = str(row[path_idx]).strip()
                if gene and path:
                    gene_paths[gene] = path
        
        return gene_paths
    
    except Exception as e:
        st.error(f"解析CSV文件时出错: {str(e)}")
        return {}

# 从GitHub获取基因路径信息
def get_gene_paths_from_github():
    content = get_github_file_content(config_path)
    if content:
        gene_paths = parse_gene_paths_from_csv(content)
        if gene_paths:
            return gene_paths
        else:
            st.error("基因路径文件格式不正确或未找到有效数据。")
    else:
        st.error(f"无法从路径 '{config_path}' 加载基因路径文件")
    return {}

# 获取GitHub原始文件URL
def get_github_raw_url(path):
    return f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{path}"

# 获取基因列表
def get_gene_list(gene_paths):
    return sorted(gene_paths.keys())

# 显示基因列表
def display_gene_list(genes, selected_gene):
    st.markdown(f'<div class="gene-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">', unsafe_allow_html=True)
    
    for gene in genes:
        class_name = "selected" if gene == selected_gene else ""
        st.markdown(
            f'<div class="gene-list-item {class_name}" onclick="selectGene(\'{gene}\')">{gene}</div>', 
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# 获取GitHub图片
def get_github_image(gene_path):
    try:
        # 尝试直接获取图片
        img_url = get_github_raw_url(gene_path)
        response = requests.get(img_url, headers=get_github_headers(), stream=True)
        response.raise_for_status()
        
        # 对于大文件，使用分块读取
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

# 主应用
def main():
    # 显示配置信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 当前配置")
    st.sidebar.info(f"仓库: {repo_owner}/{repo_name}")
    st.sidebar.info(f"分支: {branch}")
    st.sidebar.info(f"基础路径: {base_path}")
    st.sidebar.info(f"配置文件: {config_path}")
    st.sidebar.info(f"分隔符: '{csv_delimiter}'")
    st.sidebar.info(f"标题行: {'是' if has_header else '否'}")
    
    # 加载基因路径信息
    with st.spinner("正在加载基因数据..."):
        gene_paths = get_gene_paths_from_github()
    
    if not gene_paths:
        st.error("未找到基因路径信息！请检查配置。")
        return
    
    genes = get_gene_list(gene_paths)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"## 🧬 基因选择 ({len(genes)})")
        
        # 基因搜索
        search_term = st.text_input("搜索基因", "", key="gene_search")
        
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
                with st.spinner("正在加载图片..."):
                    # 尝试获取图片
                    image = get_github_image(gene_path)
                
                if image:
                    st.image(image, caption=f"{selected_gene} 图片", use_container_width=True)
                else:
                    st.warning("无法加载图片，请检查路径是否正确")
                    
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
                    response = requests.head(get_github_raw_url(gene_path), headers=get_github_headers())
                    exists = response.status_code == 200
                    st.code(f"文件状态: {'✅ 存在' if exists else '❌ 不存在'}")
                    if not exists:
                        st.warning("文件在指定路径不存在，请检查基因路径配置")
                except:
                    st.code("文件状态: ❓未知")
            
            with col2:
                st.markdown("### GitHub API信息")
                st.code(f"仓库: {repo_owner}/{repo_name}")
                st.code(f"分支: {branch}")
                st.code(f"配置文件: {config_path}")
                st.code(f"基因数量: {len(genes)}")
                st.code(f"CSV分隔符: '{csv_delimiter}'")
                st.code(f"标题行: {'是' if has_header else '否'}")
    
    # 所有基因列表
    st.subheader(f"所有可用基因 ({len(genes)})")
    display_gene_list(genes, selected_gene)
    
    # 添加JavaScript函数处理基因点击
    st.markdown("""
    <script>
    function selectGene(gene) {
        // 更新基因选择器
        const selectBox = window.parent.document.querySelector('select[aria-label="选择基因"]');
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

# 运行应用
if __name__ == "__main__":
    main()


    
  
