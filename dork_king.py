"""
Copyright 2024 ASSlili

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import streamlit as st
import urllib.parse

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="Google Dorking Visualizer",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 核心数据结构 (Query, Description) ---
DORKS = {
    "🕵️‍♂️ 个人隐私与敏感数据": {
        "身份信息 (身份证/学号/工号)": (
            "site:{target} \"身份证\" | \"身份证号\" | \"学号\" | \"工号\" | \"id card\" | \"student id\"",
            "搜索包含敏感身份标识的页面或表格。这类信息常出现在奖学金公示、录取名单或人员统计表中。"
        ),
        "联系方式 (手机/邮箱/通讯录)": (
            "site:{target} \"手机\" | \"手机号\" | \"电话\" | \"邮箱\" | \"通讯录\" | \"contact\" | \"email\" | \"mobile\"",
            "查找暴露的联系方式。Excel 通讯录泄露是社会工程学攻击的主要信息来源。"
        ),
        "居住地址与物流信息": (
            "site:{target} \"地址\" | \"住址\" | \"家庭住址\" | \"配送地址\" | \"收货地址\" | \"address\" | \"location\"",
            "查找包含具体物理地址的信息，可能泄露员工或学生的家庭住址、宿舍号或物流信息。"
        ),
        "账号凭证 (默认/初始密码)": (
            "site:{target} \"默认密码\" | \"初始密码\" | \"default password\" | \"password\" | \"pwd\" | \"change password\"",
            "搜索包含'默认密码'、'初始密码'的通知公告或文档，这是系统弱口令攻击最直接的入口。"
        )
    },
    "🌐 资产发现 (Recon)": {
        "子域名发现 (排除法)": (
            "site:{target} -www -shop -share -ir -mfa",
            "利用减号排除常见子域(如www)，从而发现开发环境(dev)、测试环境(stg)等隐蔽子域名。"
        ),
        "API 接口端点": (
            "site:{target} inurl:api | site:*/rest | site:*/v1 | site:*/v2 | site:*/v3",
            "查找暴露的 RESTful API 接口或版本号目录，通常包含结构化数据。"
        ),
        "高危目录探测": (
            "site:{target} inurl:conf | inurl:env | inurl:cgi | inurl:bin | inurl:etc | inurl:root | inurl:sql | inurl:backup | inurl:admin | inurl:php",
            "搜索 URL 中包含 config, backup, admin 等敏感关键词的页面。"
        ),
        "Github 代码泄露": (
            "site:github.com \"{target}\"",
            "跨域搜索：在 Github 上查找包含目标域名的代码仓库，可能泄露凭证或源码。"
        )
    },
    "💥 报错与调试信息": {
        "服务器报错堆栈": (
            "site:{target} inurl:\"error\" | intitle:\"exception\" | intitle:\"failure\" | intitle:\"server at\" | inurl:exception | \"database error\" | \"SQL syntax\" | \"undefined index\" | \"unhandled exception\" | \"stack trace\"",
            "查找暴露的报错页面，这些页面可能包含物理路径、代码片段或数据库结构信息。"
        ),
        "Apache Server Status": (
            "site:{target} inurl:server-status \"Apache Status\"",
            "查找未关闭的 Apache 服务器状态页，可实时查看服务器负载和访问请求。"
        ),
        "PHP Info 页面": (
            "site:{target} ext:php intitle:phpinfo \"PHP Version\"",
            "查找 phpinfo() 页面，该页面会完整泄露服务器环境配置、模块和路径。"
        )
    },
    "💉 注入与漏洞参数": {
        "SQL 注入参数": (
            "site:{target} inurl:id= | inurl:pid= | inurl:category= | inurl:cat= | inurl:action= | inurl:sid= | inurl:dir= inurl:&",
            "查找 URL 中包含常见数字型参数的页面，这些参数是 SQL 注入的高频测试点。"
        ),
        "XSS 跨站脚本": (
            "site:{target} inurl:q= | inurl:s= | inurl:search= | inurl:query= | inurl:keyword= | inurl:lang= inurl:&",
            "查找包含搜索、查询等字符串输入参数的页面，容易存在反射型 XSS。"
        ),
        "RCE 远程代码执行": (
            "site:{target} inurl:cmd | inurl:exec= | inurl:query= | inurl:code= | inurl:do= | inurl:run= | inurl:read= | inurl:ping= inurl:&",
            "查找包含命令执行语义参数的页面，属于极其危险的漏洞类型。"
        )
    },
    "📂 敏感文件探测": {
        "高危配置文件": (
            "site:{target} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ini | ext:env | ext:json",
            "搜索 xml, ini, conf, env, json 等扩展名，常包含数据库密码或 API Key。"
        ),
        "数据库备份文件": (
            "site:{target} ext:sql | ext:dbf | ext:mdb | ext:db",
            "直接搜索暴露的 SQL 导出文件或数据库文件。"
        ),
        "办公文档 (元数据)": (
            "site:{target} ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:xls | ext:xlsx | ext:csv",
            "搜索公开的办公文档，这些文件的元数据可能泄露作者、软件版本和内部信息。"
        )
    },
    "☁️ 云资产与第三方": {
        "S3 存储桶": (
            "site:s3.amazonaws.com \"{target}\"",
            "搜索 AWS S3 上的公开存储桶，常含有备份数据。"
        ),
        "Pastebin 文本": (
            "site:pastebin.com \"{target}\"",
            "搜索 Pastebin 等粘贴板网站，黑客常在此发布泄露的数据或配置。"
        )
    }
}

# --- 3. 辅助函数 ---

def generate_google_link(query):
    """生成 Google 搜索链接并进行 URL 编码"""
    base_url = "https://www.google.com/search?q="
    encoded_query = urllib.parse.quote(query)
    return base_url + encoded_query

# --- 4. CSS 样式注入 (清爽白卡片风格) ---
st.markdown("""
<style>
    /* 侧边栏样式微调 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #dee2e6;
    }
    
    /* 卡片主容器 */
    .dork-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        text-decoration: none;
    }
    
    /* 悬停效果：轻微上浮 + 阴影 */
    .dork-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #4e8cff;
    }
    
    /* 卡片标题 */
    .dork-title {
        color: #1a1a1a;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* 卡片描述文字 */
    .dork-desc {
        color: #666;
        font-size: 13px;
        line-height: 1.4;
        margin-bottom: 10px;
        flex-grow: 1;
    }
    
    /* 语法预览小字 */
    .dork-code {
        background-color: #f1f3f4;
        color: #5f6368;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 11px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    /* 去除链接下划线 */
    a:hover, a:visited, a:link, a:active {
        text-decoration: none;
    }
    
    /* 底部版权信息样式 */
    .footer-copyright {
        font-size: 12px;
        color: #888;
        text-align: center;
        margin-top: 20px;
        padding-top: 10px;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. 侧边栏导航与输入 ---

with st.sidebar:
    st.title("🔎 Dork Visualizer")
    
    # 导航模式选择
    mode = st.radio("功能模式", ["🚀 在线可视化", "📘 语法深度解析"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # 仅在工具模式下显示输入框
    if mode == "🚀 在线可视化":
        st.write("### 🎯 目标设置")
        
        # 使用 Form 表单，实现“按钮点击后提交”
        with st.form(key='search_form'):
            domain_input = st.text_input(
                "输入目标域名", 
                value=st.session_state.get('target_domain', ''),
                placeholder="例如: edu.cn"
            )
            
            # 提交按钮
            submit_button = st.form_submit_button(label='🔥 立即扫描', use_container_width=True)
            
            if submit_button:
                st.session_state['target_domain'] = domain_input

        st.caption("提示：点击上方按钮生成针对该目标的测试链接。")
        
        if st.button("❌ 清空重置"):
            st.session_state['target_domain'] = ""
            st.rerun()

    # --- 版权声明 (放置于侧边栏底部) ---
    st.markdown("---")
    st.markdown(
        """
        <div class="footer-copyright">
            Designed by <b>ASSlili</b><br>
            Licensed under <b>Apache 2.0</b><br>
            <span style='font-size: 10px;'>Powered by Streamlit & GHDB</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- 6. 主页面逻辑 ---

if mode == "🚀 在线可视化":
    st.header("🚀 Google Hacking 可视化面板")
    st.markdown("快速生成针对特定目标的高级搜索查询链接。")
    st.divider()

    target = st.session_state.get('target_domain', '')

    if not target:
        st.info("👋 **欢迎使用！** 请在左侧侧边栏输入域名并点击 **「立即扫描」** 开始。")
        
        # 空状态下的装饰性展示
        st.markdown("#### 功能概览：")
        cols = st.columns(3)
        for i, cat in enumerate(DORKS.keys()):
            with cols[i % 3]:
                st.markdown(f"✅ **{cat}**")
    else:
        st.success(f"🔍 当前锁定目标: **{target}**")
        
        # 创建标签页
        tabs = st.tabs(list(DORKS.keys()))
        
        for i, (category, items) in enumerate(DORKS.items()):
            with tabs[i]:
                st.markdown(f"#### {category}")
                cols = st.columns(3) # 3列布局
                
                for idx, (label, (template, desc)) in enumerate(items.items()):
                    # 生成链接
                    final_query = template.format(target=target)
                    link = generate_google_link(final_query)
                    
                    # 预览文字（去掉 site:target）
                    code_preview = final_query.replace(f"site:{target}", "").strip()
                    if not code_preview: code_preview = "Whole Site Search"
                    
                    with cols[idx % 3]:
                        st.markdown(
                            f"""
                            <a href="{link}" target="_blank">
                                <div class="dork-card">
                                    <div>
                                        <div class="dork-title">{label}</div>
                                        <div class="dork-desc">{desc}</div>
                                    </div>
                                    <div class="dork-code" title="{final_query}">QUERY: {code_preview}</div>
                                </div>
                            </a>
                            """,
                            unsafe_allow_html=True
                        )

elif mode == "📘 语法深度解析":
    st.header("📘 Google Hacking 语法深度解析")
    st.markdown("本页面详细解释了工具中使用的每一个查询语法的原理和用途。")
    st.divider()

    for category, items in DORKS.items():
        st.subheader(f"📌 {category}")
        
        for label, (template, desc) in items.items():
            # 使用 Expander 折叠详细信息，保持页面整洁
            with st.expander(f"**{label}**"):
                st.markdown(f"**原理解释：**\n{desc}")
                st.markdown("**语法结构：**")
                st.code(template, language="text")
                
                # 拆解解释
                st.markdown("**核心指令拆解：**")
                if "inurl:" in template:
                    st.write("- `inurl:`: 限制搜索结果的 URL 中必须包含特定关键词。")
                if "ext:" in template or "filetype:" in template:
                    st.write("- `ext:` / `filetype:`: 指定搜索特定的文件扩展名。")
                if "site:" in template:
                    st.write("- `site:`: 将搜索范围严格限制在指定域名及其子域名内。")
                if "\"" in template:
                    st.write("- `\"...\"` (双引号): 强制完全匹配，防止 Google 对关键词进行模糊搜索或拆分。")