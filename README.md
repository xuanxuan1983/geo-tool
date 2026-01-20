# Product-GEO-Content – AI-Powered GEO Content Generation Tool

> **产品标识**: `product-geo-content`
> **版本**: v1.0.0
> **更新日期**: 2026-01-20

## Overview
**Product-GEO-Content** 是一个完整的GEO（生成式引擎优化）内容生成和测试工具，专为医美行业设计。通过AI自动化生成D→B→C→A全流程内容，并集成Notion/飞书平台进行项目管理。

A lightweight **Streamlit** web interface that wraps the existing GEO pipeline (`run_full_pipeline.py`, `ai_pressure_test_multi.py`, `generate_comparison_report.py`).

- **Roles**: Admin (full access) / Team Member (run pipeline, view results).
- **核心能力**:
  - ✅ **AI内容生成**: D→B→C→A全流程自动化
  - ✅ **智能参数提取**: 自动从D矩阵提取关键词和问题
  - ✅ **多引擎压力测试**: DeepSeek/ChatGPT多引擎AI压力测试
  - ✅ **平台集成**: Notion/飞书双平台项目管理
  - ✅ **数据库关联**: Relation实现项目与执行记录关联
  - ✅ **PPT自动生成**: 一键生成演示文稿
- **Features**:
  - One‑click D→B→C→A execution.
  - Multi‑engine AI pressure testing.
  - Before/After comparison reports.
  - Secure password‑based login (hashes stored in `.env`).
  - Dockerized deployment (Dockerfile + `docker‑compose.yml`).

## Quick Start (Local)
```bash
# 1. Clone repo
git clone https://github.com/xuanxuan1983/geo-tool.git
cd geo-tool  # product-geo-content

# 2. Create a virtual env & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure platform integration (Notion/Feishu)
#    Edit config/platform_config.yaml with your credentials

# 4. Set passwords (replace placeholders in .env)
#   Generate SHA‑256 hash:
#   python -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
#   Paste the hash into ADMIN_PASSWORD_HASH / MEMBER_PASSWORD_HASH

# 5. Run the app
streamlit run scripts/app.py
```
Open `http://localhost:8501` in a browser.

## Docker Deployment
```bash
# Build and run the container
docker compose up --build -d
```
The app will be reachable at `http://localhost:8501`. The `output/` directory is mounted as a volume, so all generated files persist on the host.

## Environment Variables (`.env`)
| Variable | Purpose |
|----------|---------|
| ADMIN_PASSWORD_HASH | SHA‑256 hash of the admin password |
| MEMBER_PASSWORD_HASH | SHA‑256 hash of the member password |
| DEEPSEEK_API_KEY | Your DeepSeek API key (already in `config.py`) |
| OPENAI_API_KEY | API key for ChatGPT (optional) |

## File Structure
```
product-geo-content/
├─ scripts/
│   ├─ app.py                              # Streamlit UI
│   ├─ auth.py                             # Login & role handling
│   ├─ wrapper.py                          # Pipeline wrapper functions
│   ├─ run_full_pipeline.py                # D→B→C→A pipeline
│   ├─ ai_pressure_test_multi.py           # AI pressure testing
│   ├─ generate_comparison_report.py       # Comparison reports
│   ├─ platform_adapter.py                 # Platform abstract interfaces
│   ├─ notion_adapter.py                   # Notion integration
│   ├─ feishu_adapter.py                   # Feishu integration
│   ├─ platform_integration_manager.py     # Platform manager
│   ├─ cleanup_auto.py                     # Auto cleanup script
│   └─ cleanup_test_data.py                # Interactive cleanup
├─ config/
│   └─ platform_config.yaml                # Platform configuration
├─ docs/
│   └─ notion_relation_setup.md            # Notion setup guide
├─ output/                                 # Generated client files
├─ input/                                  # Input JSON files
├─ .env                                    # Secrets (do NOT commit)
├─ .gitignore
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## Next Steps
- Replace the placeholder password hashes in `.env`.
- Configure Notion or Feishu credentials in `config/platform_config.yaml`.
- (Optional) Add Feishu OAuth in `auth.py`.
- Customize branding: replace the DMY logo path in `app.py`.

---

## Product Information

### 产品标识
- **Product ID**: `product-geo-content`
- **产品名称**: GEO智能内容生成工具
- **行业**: 医美/医疗美容
- **版本**: v1.0.0
- **更新日期**: 2026-01-20

### 技术栈
- **前端**: Streamlit
- **AI引擎**: DeepSeek, OpenAI GPT
- **平台集成**: Notion API, Feishu/Lark API
- **语言**: Python 3.9+
- **部署**: Docker, Docker Compose

### GitHub仓库
- **仓库地址**: https://github.com/xuanxuan1983/geo-tool.git
- **分支**: main
- **许可**: Private

### 联系方式
如有问题或建议，请通过GitHub Issues提交。

---
*Product-GEO-Content - AI-Powered Content Generation for Medical Aesthetics*
