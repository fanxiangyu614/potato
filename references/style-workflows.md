# 风格探索、随机拍照与头像三视图

## Overview

Use this skill to turn a subject into reusable AIGC prompt variants using rare sub-style tags rather than broad labels such as minimalism, Bauhaus, or cyberpunk.

The bundled library lives at `style_library.json`. Load it only when the user asks for specific style lookup, filtering, auditing, or manual curation. For normal prompt generation, run `../scripts/explore_styles.py`.

The library is keyword-first. Some 2026-05 entries were distilled from public Midjourney SREF style-reference galleries and documentation, but this skill does not store SREF codes and should not output `--sref` parameters unless the user explicitly changes the goal.

Final prompt variants should be written in Chinese by default. English prompt tokens remain in the style metadata for lookup and manual conversion, but the user-facing prompt text should use Chinese style names, Chinese visual DNA, and Chinese anti-drift constraints.

## Scope and completion

审阅或维护 Skill 时只处理规则。根据用户目标直接选择模式、风格数量和组合；主题已明确时不要求先选择菜单。缺少不可推定的主题或明确约束冲突才澄清，普通偏好用合理默认值继续。

提示词请求交付筛选后的可用提示词即完成；要求出图时继续调用可用图像工具，不能停在风格建议或询问“要不要生成”。编辑任务必须使用对应参考图，缺少引用时请求补充；工具不可用时说明具体缺口并交付已完成部分。生成次数与预算遵守用户要求及图像执行 Skill 的边界。

与内部脏图修复、仿 MJ8.2 优化模块或视频制作联用时，本模块只提供用户要求的视觉方向，服从最终交付物的语言、篇幅、身份与连续性约束；不额外生成探索报告、多个版本或第二套图片。库内风格和脚本输出均为候选素材，不得覆盖用户给定内容。

## 参考图质量与执行复盘

涉及参考图生成、连续画面、画质返工或指定后期处理时，按需读取 [图片制作错误复盘与防错规则](storyboard-image-quality.md)，核对参考使用、画质、内容一致性和实际验收。维护技能时只沉淀通用错误与防错措施；具体项目的提示词、剧情、人物、镜头清单及参数留在项目文件中，不写进技能。

## 头像三视图入口

用户要求“头像三视图”“大头三视图”“面部三视图”，或基于人物参考图制作正面、45°、90°侧面头像时，读取 [头像三视图规则与提示词](head-three-views.md)。此模式优先于通用风格探索，不自动抽取库内风格或套用 COS 规则。默认先制作三张证件照式视图，由用户确认相似度后再制作透明背景纯面部三视图；已明确确认参考版本或指定仅做某阶段时按当前要求执行。维护、导入知识时只更新技能，不启动出图。

## 随机拍照入口

「随机拍照」「随机写真」「随机风格＋人物妆造」执行 [随机拍照](random-photo.md)。旧「COS拍照／COS随机拍照」锁第1类，来源仍独立掷骰。该工作流调用 `random_photo.py`；骰子、默认媒介、场景/版式池与全库模式统一以[随机拍照规则](random-photo.md#媒介池与双风格)为准，不使用下方十种摄影预设代替主池。

用户要求生成就完成实际图片；只写提示词就交文字。仅维护玩法不启动生图；用户锁定项优先，未要求选择菜单时直接按合理默认执行。

下方 `explore_styles.py --mode cos` 是保留的十种兼容摄影风格**显式预设**，仅用户要求摄影兼容小池建议时使用；不作为随机拍照默认，不把十种预设冒充620全库。其他普通风格探索继续按下文执行。

## Default Workflow

1. Identify the subject and output goal.
   - Product or packaging: prefer `product`.
   - Character, avatar, IP, portrait: prefer `character`.
   - Real-person COS style candidates: use `cos`; the role, costume, location, composition and pose must already be part of the subject.
   - Poster, cover, social visual: prefer `poster`.
   - Narrative scene: prefer `scene`.
   - Same subject with multiple surfaces: prefer `material-series`.
   - Fast exploration: use `minimal`.

2. 多方向探索优先运行脚本；单个方向的细化可直接复用已选风格，不重新随机抽取。示例数量 8 不是最低配额，用户数量优先，未指定时默认 3 个候选：

```bash
python3 scripts/explore_styles.py "SUBJECT" --mode minimal --count 8 --freshness high
```

3. Review generated style IDs and remove combinations that conflict with the subject, platform, or brand. Rewrite candidate text before delivery: library motifs must not delete required accessories, replace readable text with pseudo-text, or clear a required background. If the script fails, inspect the error and use the library directly when feasible; do not make script success a delivery gate.

4. If the user asks for a more targeted direction, use `--style-family`:
   - `film`: cinematic genres and light color
   - `fashion`: editorial styling and subculture looks
   - `product`: toy/product/material presentation
   - `photography`: photographic tone and media defects
   - `illustration`: drawing, manga, animation, and picture-book media
   - `graphic`: posters, packaging, catalogs, and print layouts
   - `craft`: regional craft, folk pattern, and historical media
   - `digital`: UI, game, old software, and screen media
   - `space`: architectural and scene atmosphere
   - `material`: surface and tactile material variants

5. 默认交付风格名和可直接使用的提示词；选择理由最多简述一句。分析维度、变量槽位和复用模板仅在用户要求或确实有助于后续复用时提供，不为简单请求固定输出六部分。

## Combination Rules

普通风格探索使用一个主风格及至多一个适配层；随机拍照则按已登记的主副风格组合与区域正文执行。 The script supplies subject and style candidates; it does not add a photographic quality or capture preset. For the default built-in photographic entrypoint, compose the final prompt with [默认生图摄影规则](default-image-photography.md); for COS, use [完整 COS 规则](cos-random-photo.md). Other models and non-photographic tasks keep their own requirements.

Do not stack too many strong style anchors. If the subject is fragile, such as a logo, facial identity, product silhouette, or readable packaging, prioritize recognizability over novelty.

## Script Usage

Run examples from this cabin folder (`..`), not the hub skill root. Prefer `python -B` on Windows, or invoke the script by its actual absolute path from any directory. Bash examples are illustrative; use the current shell's syntax, not Bash heredocs in PowerShell. Do not install another runtime merely to match an example command.

```bash
python3 scripts/explore_styles.py "ceramic cat perfume bottle" --mode product --count 6 --seed 42
python3 scripts/explore_styles.py "martial arts heroine" --mode character --count 5
python3 scripts/explore_styles.py "AI knowledge base app icon" --mode poster --count 8 --format json
python3 scripts/explore_styles.py "retro cafe mascot" --style-id S008 --count 4
python3 scripts/explore_styles.py "fashion portrait" --mode character --style-family fashion --freshness high --count 8
python3 scripts/explore_styles.py "blind box toy" --mode product --style-family product --freshness high --count 8
python3 scripts/explore_styles.py "蒂法，漫展会场，半身抓拍，整理手套，微笑" --mode cos --count 3 --seed 42
```

Useful options:

- `--mode`: `minimal`, `product`, `character`, `cos`, `poster`, `scene`, `material-series`. `cos` 只产生兼容真人 COS 摄影且不替换角色、服装、地点和动作的候选。
- `--count`: number of prompt variants.
- `--seed`: reproducible random seed.
- `--style-id`: force a base style by library ID, then vary supporting layers.
- `--format`: `markdown` or `json`.
- `--freshness`: `normal` or `high`; `high` biases toward newer, lower-frequency, visually specific entries.
- `--style-family`: narrow the base style pool to a concrete family such as `film`, `fashion`, `product`, `photography`, `illustration`, `graphic`, `craft`, `digital`, `space`, or `material`.
- `--allow-space-change`: only use when the user explicitly wants a new location. `scene` preserves the location written in the subject by default.
- `--avoid-generic` / `--no-avoid-generic`: generic suppression is on by default; turn it off only when you need broader styles.

## Manual Library Lookup

Use `style_library.json` when you need to:

- inspect all 620 entries
- search by Chinese style name, English prompt token, category, subject suitability, or failure mode
- select styles manually for a themed series
- quote style metadata such as `容易翻车` or `补救提示`

For quick shell lookup:

```bash
python3 - <<'PY'
import json
p='references/style_library.json'
data=json.load(open(p, encoding='utf-8'))
for s in data['styles']:
    if 'giallo' in s.get('English prompt tokens','').lower() or '铅黄' in s.get('中文风格名',''):
        print(s['style_id'], s['中文风格名'], s['视觉DNA / 关键词'], s['English prompt tokens'])
PY
```

## Output Standards

Keep prompts specific, visual, and generation-ready. The final prompt should be Chinese. Use English prompt tokens only as metadata or when the user explicitly asks for an English version.

Prefer precise sub-style phrases such as `sun-faded folk horror poster photography`, `chrome Y2K fashion editorial`, `pastel ceramic toy photography`, or `overexposed tropical VHS travelogue`. Avoid relying on isolated generic words such as cinematic, surreal, retro, futuristic, cyberpunk, minimalism, or aesthetic.

按实际主体选择必要的防偏移约束，不机械附加与任务无关的禁忌：保留身份与可识别结构，避免意外文字、符号和形体错误。用户指定极简风时不写“避免现代极简”。

产品保持可识别；只有任务需要时才采用干净背景，不删除指定场景或道具。人物保持已给姿势和配饰；1–2 个配饰仅适用于未限定的新角色设计。海报保留用户提供的可读文字与排版要求；只有明确制作占位版时才使用伪文字，不主动破坏标题或长文案。
