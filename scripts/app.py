# app.py – Streamlit front‑end for GEO Tool

import streamlit as st
st.set_page_config(page_title="GEO Tool", layout="wide", page_icon="🧭")
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env vars
load_dotenv()

PRIMARY_COLOR = os.getenv("PRIMARY_COLOR", "#3B82F6")
DEFAULT_DARK_MODE = os.getenv("DARK_MODE_DEFAULT", "true").lower() == "true"
from auth import check_credentials, get_user_role
from feishu_oauth import get_auth_url, feishu_login_flow
# Lazy loaded imports: wrapper, ppt_generator, canva_uploader, screenshot_automation

# -------------------------------------------------------------------
# Helper: list generated files for a client
# -------------------------------------------------------------------
def list_client_files(client_folder: Path):
    files = []
    for f in client_folder.iterdir():
        if f.is_file() and f.suffix in {".md", ".json", ".png", ".jpg", ".pptx"}:
            files.append(f)
    return files



if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = None
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = DEFAULT_DARK_MODE

if not st.session_state.authenticated:
    st.title("🔐 GEO Tool – 登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    # Feishu login link
    feishu_url = get_auth_url()
    st.markdown(f"[🌟 使用飞书登录]({feishu_url})", unsafe_allow_html=True)
    if st.button("登录"):
        role = check_credentials(username, password)
        if role:
            st.session_state.authenticated = True
            st.session_state.role = role
            st.session_state.username = username
            st.success(f"登录成功，角色：{role}")
        else:
            st.error("用户名或密码错误")
    # Handle Feishu redirect after auth
    query_params = st.query_params
    if "code" in query_params:
        feishu_role = feishu_login_flow(query_params)
        if feishu_role:
            st.session_state.authenticated = True
            st.session_state.role = feishu_role
            st.session_state.username = "feishu_user"
            st.success(f"飞书登录成功，角色：{feishu_role}")
        else:
            st.error("飞书登录失败，请重试")
    st.stop()

# -------------------------------------------------------------------
# Main UI – sidebar navigation
# -------------------------------------------------------------------
st.sidebar.title("🌐 GEO Tool")
# Apply dark mode CSS
if st.session_state.dark_mode:
    st.markdown(f"""
    <style>
    .stApp {{background-color: #111; color: #eee;}}
    .stButton>button {{background-color: {PRIMARY_COLOR}; color: white;}}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <style>
    .stApp {{background-color: #fff; color: #000;}}
    .stButton>button {{background-color: {PRIMARY_COLOR}; color: white;}}
    </style>
    """, unsafe_allow_html=True)

page = st.sidebar.radio("页面", ["仪表盘", "🚀 新建项目", "压力测试", "对比报告", "设置"])

# ---------------------------------------------------------------
# 1️⃣ Dashboard – show recent clients & files
# ---------------------------------------------------------------
if page == "仪表盘":
    st.header("📊 仪表盘")
    output_root = Path(__file__).parent.parent / "output"
    output_root.mkdir(parents=True, exist_ok=True)  # Create if not exists
    clients = [p.name for p in output_root.iterdir() if p.is_dir()]
    st.subheader("已生成的客户文件夹")

    if not clients:
        st.info("暂无数据，请先去【运行流水线】")
    else:
        for client in clients:
            with st.expander(f"📂 {client} (点击查看文件)", expanded=False):
                folder_path = output_root / client
                
                # Management Actions
                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button("🗑️ 删除此客户", key=f"del_{client}"):
                        import shutil
                        try:
                            shutil.rmtree(folder_path)
                            st.success(f"已删除 {client}！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败: {e}")

                # List Files
                files = list_client_files(folder_path)
                if not files:
                    st.warning("文件夹为空")
                else:
                    for f in files:
                        st.markdown(f"**📄 {f.name}**")
                        col_view, col_dl = st.columns([1, 1])
                        
                        # Preview Content for Markdown/JSON
                        if f.suffix in [".md", ".json", ".txt"]:
                            with col_view:
                                if st.checkbox(f"👀 预览", key=f"view_{client}_{f.name}"):
                                    content = f.read_text(encoding="utf-8")
                                    if f.suffix == ".json":
                                        st.code(content, language="json")
                                    else:
                                        st.markdown(content)
                        
                        # Download Button
                        with col_dl:
                            with open(f, "rb") as fh:
                                st.download_button(
                                    label="📥 下载",
                                    data=fh,
                                    file_name=f.name,
                                    key=f"db_dash_{client}_{f.name}"
                                )
                        st.divider()
    st.info("💡 提示：这里可以管理生成的结果文件夹。")

# ---------------------------------------------------------------
# 1.5️⃣ Create Client Input - Form
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# 1.5️⃣ New Project - One Stop Shop
# ---------------------------------------------------------------
elif page == "🚀 新建项目":
    st.header("🚀 开始新项目")
    
    with st.form("client_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("客户名称 (Client Name)", "示例品牌")
            c_type = st.selectbox("业务类型 (Business Type)", ["上游品牌", "下游机构", "医生个人IP"], index=0)
        with col2:
            c_product = st.text_input("核心产品 (Core Product)", "重组胶原蛋白植入剂")
            c_goal = st.text_input("商业目标 (Goal)", "获客")
            
        st.subheader("硬性锚点 (Hard Anchors)")
        st.caption("每行一个，例如专利号、核心技术、注册证号")
        c_anchors_text = st.text_area("锚点列表", "注册证号：XXXXXXXXXX\n核心技术：EDC/NHS 交联技术\n成分参数：III型重组胶原蛋白\n专利号：CNXXXXXXX")
        
        st.subheader("竞品信息 (Competitors)")
        st.caption("格式：竞品名称 | 关键词 (每行一个)")
        c_competitors_text = st.text_area("竞品列表", "竞品A | 玻尿酸\n竞品B | 动物源胶原蛋白\n竞品C | 自体脂肪")
        
        st.subheader("现有资产 (Existing Assets)")
        st.caption("每行一个 URL")
        c_assets_text = st.text_area("资产列表", "https://example.com")
        
        st.subheader("合规红线 (Compliance Redlines)")
        st.caption("每行一个")
        c_redlines_text = st.text_area("红线列表", "不能出现100%有效\n不能与药品做疗效对比\n不能使用患者证言")
        

            
        # Buttons
        st.caption("👇 点击下方按钮，自动保存配置并运行流水线，无需手动上传下载。")
        run_submitted = st.form_submit_button("🚀 保存并立即开始运行 (Save & Run)")
        

        
    if run_submitted:
         # Construct JSON logic
         # Parse inputs
        anchors = [line.strip() for line in c_anchors_text.split('\n') if line.strip()]
        assets = [line.strip() for line in c_assets_text.split('\n') if line.strip()]
        redlines = [line.strip() for line in c_redlines_text.split('\n') if line.strip()]
        
        competitors = []
        for line in c_competitors_text.split('\n'):
            if '|' in line:
                parts = line.split('|')
                competitors.append({"name": parts[0].strip(), "key_phrase": parts[1].strip()})
            elif line.strip():
                competitors.append({"name": line.strip(), "key_phrase": "无"})
        
        import json
        data = {
            "client_name": c_name,
            "business_type": c_type,
            "core_product": c_product,
            "hard_anchors": anchors,
            "competitors": competitors,
            "existing_assets": assets,
            "goal": c_goal,
            "compliance_redlines": redlines
        }
        json_str = json.dumps(data, indent=4, ensure_ascii=False)

        st.write("---")
        st.info(f"正在保存配置并启动流水线 (Output: output/{c_name}) ...")
        
        # Save to file
        client_folder = (Path(__file__).parent.parent / "output" / c_name).resolve()
        client_folder.mkdir(parents=True, exist_ok=True)
        input_path = client_folder / f"{c_name}.json"
        input_path.write_text(json_str, encoding='utf-8')
        
        # Run Pipeline
        with st.spinner("🚀 正在执行 D→B→C→A 全自动流水线 (耗时约 1-2 分钟)..."):
            from wrapper import run_pipeline
            from ppt_generator import generate_ppt
            run_pipeline(str(c_name), str(input_path.resolve()))
            # Generate PPT
            generate_ppt(str(c_name), str(client_folder))
        
        st.success("🎉 执行完成！结果如下：")
        
        # Show results directly (Copied from Dashboard logic)
        files = list_client_files(client_folder)
        for f in files:
            with st.expander(f"📄 {f.name} (点击预览)", expanded=False):
                col_dl, col_action = st.columns([1, 1])
                with col_dl:
                    with open(f, "rb") as fh:
                        st.download_button(label="📥 下载", data=fh, file_name=f.name, key=f"dl_new_{f.name}")
                with col_action:
                    if f.suffix == ".pptx":
                        if st.button(f"📤 发送到 Canva", key=f"canva_new_{f.name}"):
                            from canva_uploader import upload_to_canva
                            with st.spinner("正在上传..."):
                                res = upload_to_canva(str(f))
                                if res.get("success"):
                                    st.success(res.get("message"))
                                    st.markdown(f"[🎨 打开 Canva]({res.get('design_url')})", unsafe_allow_html=True)
                                else:
                                    st.error(res.get("error"))
                
                # Preview content
                if f.suffix in [".md", ".json", ".txt"]:
                    content = f.read_text(encoding="utf-8")
                    if f.suffix == ".json":
                        st.code(content, language="json")
                    else:
                        st.markdown(content)

# ---------------------------------------------------------------
# 2️⃣ Run Pipeline – D→B→C→A
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# 3️⃣ Pressure Test – multi‑engine
# ---------------------------------------------------------------
elif page == "压力测试":
    st.header("🔎 AI 压力测试")
    client_name = st.selectbox("选择客户", [d.name for d in (Path(__file__).parent.parent / "output").iterdir() if d.is_dir()])
    engines = st.multiselect("选择 AI 引擎", ["deepseek", "chatgpt"], default=["deepseek"])
    if st.button("开始压力测试"):
        client_folder = Path(__file__).parent.parent / "output" / client_name
        with st.spinner("正在以多角色发起攻击..."):
            from wrapper import run_pressure_test
            # Use user-selected engines
            res = run_pressure_test(client_folder.name, str(client_folder), engines)
            st.success(f"测试完成！报告已生成: {res}")
            with open(res, "r") as f:
                st.markdown(f.read())

# ---------------------------------------------------------------
# 4️⃣ Comparison Report – before/after
# ---------------------------------------------------------------
elif page == "对比报告":
    st.header("📈 前后对比报告")
    client_name = st.selectbox("选择客户", [d.name for d in (Path(__file__).parent.parent / "output").iterdir() if d.is_dir()], key="cmp_client")
    client_folder = Path(__file__).parent.parent / "output" / client_name
    json_files = [f.name for f in client_folder.iterdir() if f.is_file() and f.suffix == ".json"]
    if not json_files:
        st.warning("该客户暂无 JSON 测试文件。")
    else:
        before_file = st.selectbox("选择前测 JSON", json_files, key="before_file")
        after_file = st.selectbox("选择后测 JSON", json_files, key="after_file")
        if st.button("开始对比"):
            if before_file == after_file:
                st.error("请选择不同的前后文件进行对比。")
            else:
                p_before = client_folder / before_file
                p_after = client_folder / after_file
                with st.spinner("正在进行语义差异分析..."):
                    from wrapper import generate_comparison_report
                    res = generate_comparison_report(str(p_before), str(p_after), client_name)
                    st.success("对比报告生成完成！")
                    with open(res, "r") as f:
                        st.markdown(f.read())

# ---------------------------------------------------------------
# 5️⃣ Settings – show (admin only) env vars
# ---------------------------------------------------------------
elif page == "设置":
    st.header("⚙️ 设置")
    if st.session_state.role != "admin":
        st.warning("仅管理员可查看设置")
    else:
        st.subheader("环境变量（仅展示）")
        from dotenv import dotenv_values
        env = dotenv_values()
        for k, v in env.items():
            st.text_input(k, v, disabled=True)
            
        st.subheader("🤖 自动化截图")
        st.info("此功能将启动后台浏览器截取当前应用的所有页面截图。")
        auto_user = st.text_input("自动化登录用户名", value="admin")
        auto_pass = st.text_input("自动化登录密码", type="password")
        if st.button("开始截图"):
             with st.spinner("正在后台截取页面 (可能需要几十秒)..."):
                 try:
                     from screenshot_automation import capture_screenshots
                     out_path = Path(__file__).parent.parent / "output" / "screenshots"
                     res = capture_screenshots(str(out_path), auto_user, auto_pass)
                     st.success(f"截图完成！保存在: {res}")
                     for img in Path(res).iterdir():
                         if img.suffix == ".png":
                             st.image(str(img), caption=img.name, width=300)
                 except Exception as e:
                     st.error(f"截图失败: {e}")
                     st.warning("如果是第一次运行，请尝试在终端执行: playwright install")

# End of app.py
