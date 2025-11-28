# Dork King Simulator
# 🔎 Google Dorking Visualizer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
![Author](https://img.shields.io/badge/Author-ASSlili-orange)

一个基于 Python Streamlit 构建的轻量级、可视化 Google Hacking (Dorking) 工具。
旨在帮助渗透测试人员、安全研究员及 Bug Bounty 猎人快速生成针对特定目标的高级搜索查询链接，高效发现资产与潜在漏洞。

## ✨ 功能特性

* **可视化操作**：告别复杂的命令行，通过直观的 Web 界面输入域名即可一键生成查询。
* **六大核心模块**：
    * 🕵️‍♂️ **隐私与敏感数据**：检测身份证、手机号、通讯录、默认密码等 PII 泄露。
    * 🌐 **资产发现 (Recon)**：子域名挖掘、API 接口探测、Github 代码泄露。
    * 💥 **报错与调试**：查找暴露的堆栈报错、PHPInfo、Apache Server Status。
    * 💉 **漏洞参数挖掘**：针对 SQL 注入、XSS、RCE、SSRF 的参数模式搜索。
    * 📂 **敏感文件探测**：配置文件、数据库备份、Office 文档元数据。
    * ☁️ **云资产与第三方**：S3 存储桶、Pastebin 泄露检测。
* **双模式切换**：
    * 🚀 **在线可视化**：快速生成测试链接。
    * 📘 **语法深度解析**：详细解释每条 Dork 的原理与用途，适合教学与查阅。
* **清爽 UI**：基于 Streamlit 的现代化卡片式设计，操作流畅。

## 🚀 快速开始

### 1. 环境要求

确保你的电脑上安装了 Python 3.8 或更高版本。

### 2. 安装依赖

pip install -r requirements.txt

## 使用方法
1. 在项目目录下运行以下命令启动应用
```bash
streamlit run dork_king.py
```
2. 在浏览器中打开显示的本地URL（通常是 http://localhost:8501）
3. 在侧边栏输入目标域名（例如：example.com）
4. 点击各分类下的按钮生成对应的Google Dork查询链接
5. 点击链接在新标签页中查看搜索结果

## 免责声明
本工具仅用于安全测试与教育目的。使用本工具进行任何未经授权的扫描或攻击行为均属非法，使用者需自行承担相关法律责任。