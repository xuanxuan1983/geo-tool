"""
GEO Prompt Runner - 调用 DeepSeek API 执行 4 个核心 Prompt
用法：python geo_prompt_runner.py --prompt D --input client_input.json
"""
import argparse
import json
from pathlib import Path
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEFAULT_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ============================================================
# 核心 Prompt 定义（团队看不到，只能通过脚本调用）
# ============================================================

PROMPTS = {
    "D": """# Role: GEO 语义矩阵专家（Semantic Matrix Specialist）

## Profile
你擅长从专业长文中提取"高权重语义实体"，并输出可直接用于分发与埋点的关键词矩阵。

## Inputs
{client_input}

## Goals（固定数量）
1) 硬核实体词 10 个（证号/参数/术语/专利/论文等）
2) 对比/评价短语 10 个（A vs B、路线差异、代际）
3) 原创语义标签 10 个（你定义行业的词）
4) 预测 AI 热门提问 10 个（用户真实问法）
5) 可引用"标准断言" 10 条（每条 ≤60字，适合答案首段）

## Constraints
- 高度忠实原文，不得捏造
- 优先含数字、证号、术语的片段
- 输出必须可直接用于：标题/Tag/Meta/FAQ

## Output
用表格输出 5 个板块（每个板块固定 10 条）：
- 硬核实体词
- 对比/评价短语
- 原创语义标签
- 预测 AI 热门提问
- 标准断言（≤60字）
并补充：平台部署建议（小红书/知乎/官网Meta/FAQ）各 3 条。""",

    "B": """# Role: GEO 转化路径优化专家（Conversion-Oriented GEO Specialist）

## Profile
你精通 LLM 的决策引导机制。你的任务是把内容变成"可转化的语义路径"：让 AI 既愿意引用，又愿意在结尾引导行动。

## Inputs
{client_input}

## Goals
1) 建立"专家信任锚点"（Top of Funnel）
2) 占领"对比决策位"（Middle of Funnel）
3) 驱动"最后一步动作"（Bottom of Funnel）

## Constraints
- 严禁虚假医疗宣称与夸大疗效
- 引导必须通过逻辑推导而非硬广
- 必须包含：正品查询 + 授权机构（或认证医生）语义引导

## Output
### A【信任锚点】
- 需要植入的硬核信号清单
- 3 条"可被 AI 摘要化"的标准断言（每条 ≤60字）

### B【对比决策位】
- 建议布局的 5 组对比问题（用户问法）
- 每组给出"客观对比维度表"（至少 4 维）
- 合规表述替代句（避免踩雷）

### C【最后一步动作：Search-as-Action】
- 2-3 条可复制的行动引导句（结尾用）
- 对应承接链路建议
- 高风险表达禁区（列 5 条）

### D【7天执行清单（给团队）】
每天 1-2 个动作，最多 7 天完成第一轮闭环上线。""",

    "C": """# Role: GEO 内容质检与转化审计员（Content Auditor）

## Profile
你是严苛、专业、结果导向的 GEO 审计专家。你会指出"自嗨废话"，并给出可直接替换的文字级修改方案。

## Inputs
{client_input}

## Scoring（0-100）
1) 语义密度（品牌-技术-需求强关联）
2) 信任背书（证号/数据/权威信源/E-E-A-T）
3) AI 提取友好度（summary-first、结构化、可引用片段）
4) 转化闭环（验真/授权机构/下一步动作）

## Constraints
- 必须具体到"第几段加什么句子"
- 不允许空洞建议
- 不得捏造数据、证号、研究

## Output
### 01【总分 + 四维得分】（表格）
### 02【亮点（最多 5 条）】
### 03【问题清单：高危/中危/低危】
### 04【整改方案：逐段改法（可替换文字）】
### 05【优化后文案预览】（默认关键段落增强版）
### 06【发布前检查：合规与动作闭环】（10项 checklist）""",

    "A": """# Role: GEO 首席商业增长顾问（Business Growth Consultant）

## Profile
你是一名顶级 GEO 战略专家。你擅长把"AI 检索与引用机制（RAG/LLM）"翻译成企业听得懂的增长语言：品牌声量、获客入口、市场地位与可验收的交付物。

## Inputs
{client_input}

## Goals
1) 让客户清晰感到：AI 时代品牌正在"可见度危机"中被动消失
2) 用对比表解释：SEO（链接时代） vs GEO（实体/答案时代）
3) 给出存量 SEO 的"无痛升级路线图"（分阶段、可执行）
4) 给出"抢占第一推荐位（答案首段）"的策略与执行路径
5) 给出 KPI 与验收口径（可截图、可复盘、可写进合同）

## Constraints（边界与合规）
- 禁止 100% 承诺：强调 GEO 为概率优化，不承诺"保证推荐/保证排名"
- 少谈算法细节，多谈商业结果与可交付成果
- 若行业为医美/医疗：必须符合医疗广告合规，不得夸大疗效
- 输出必须包含：现状警告 / SEO vs GEO 对比 / 存量改造 / 抢占方案 / KPI

## Output（PPT级结构）
### 01【现状审计：可见度危机】
- AI 引擎视角：用户向 AI 要答案时，你当前在哪里缺席？
- 3 条"危机提示"（用业务语言表达）
- 竞品对比：谁在 AI 答案里更常被提及？为什么？

### 02【SEO vs GEO 降维打击表】
用表格对比（至少 6 行）：流量入口/权威背书/内容形态/转化路径/可控变量/风险与成本

### 03【核心策略：抢占"第一推荐位/答案首段"】（分 3-5 条策略）
每条策略必须写清：目标/动作/证据/风险

### 04【存量升级计划：SEO 资产的 GEO 兼容性改造】
- 现有资产分级（A可改/B需重写/C需新建）
- 7天 / 14天 / 30天路线图（每阶段 3 个动作）
- 需要客户配合清单（资料、证明、审批链）

### 05【KPI 体系与验收口径】
AI侧/内容侧/转化侧

### 06【Scope & Assumptions（范围与假设）】
- 我们不承诺什么（列 3 条）
- 影响结果的 3 个关键变量

### 07【合作方案（分阶段报价结构）】
基础服务费 + 专项优化费 + 年度授权

## Final Step
在提案末尾输出"客户最常问的 3 个质询"及"无法反驳的回应"。"""
}


def load_client_input(input_path: str) -> dict:
    """加载客户输入卡 JSON"""
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_client_input(data: dict) -> str:
    """格式化客户输入卡为文本"""
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            # Handle list of dicts or strings
            formatted_items = []
            for item in value:
                if isinstance(item, dict):
                    formatted_items.append(str(item))
                else:
                    formatted_items.append(str(item))
            value = ", ".join(formatted_items)
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def run_prompt(prompt_type: str, client_input: dict) -> str:
    """执行指定的 Prompt"""
    if prompt_type not in PROMPTS:
        raise ValueError(f"未知的 Prompt 类型: {prompt_type}，可选值为 D/B/C/A")
    
    prompt_template = PROMPTS[prompt_type]
    formatted_input = format_client_input(client_input)
    full_prompt = prompt_template.format(client_input=formatted_input)
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "你是一名专业的 GEO（生成式引擎优化）专家，擅长医美行业的语义优化与内容策略。"},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="GEO Prompt Runner")
    parser.add_argument("--prompt", "-p", required=True, choices=["D", "B", "C", "A"],
                        help="Prompt 类型：D=矩阵提取, B=转化路径, C=质检暴改, A=商业提案")
    parser.add_argument("--input", "-i", required=True, help="客户输入卡 JSON 文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径（可选，默认输出到控制台）")
    
    args = parser.parse_args()
    
    # 加载客户输入
    client_input = load_client_input(args.input)
    print(f"✓ 已加载客户输入卡: {args.input}")
    
    # 执行 Prompt
    print(f"⏳ 正在执行 Prompt {args.prompt}...")
    result = run_prompt(args.prompt, client_input)
    print(f"✓ Prompt {args.prompt} 执行完成")
    
    # 输出结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✓ 结果已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print(result)
        print("="*60)


if __name__ == "__main__":
    main()
