# 空间可拍性预演

只在风险镜头进入文案润色前运行。本卡把既有的机位、轴线、动作连续性和发现链规则压缩成一张共享状态表；它不是全片复审，也不是关键词安全锁。简单固定空间、固定机位、单一动作镜头直接跳过。

<!-- spatial-preflight-contract:begin -->
```json
{
  "name": "空间可拍性预演",
  "scope": "risk_shots_only",
  "owner": "main_model",
  "translator": "same_owner",
  "trigger_any": [
    "multiple_people",
    "multiple_spaces",
    "threshold_crossing",
    "facing_change",
    "axis_crossing",
    "occlusion",
    "pov",
    "complex_camera_move",
    "reveal_or_perception_claim"
  ],
  "required_fields": [
    "camera_zone",
    "camera_facing",
    "shot_size",
    "subject_zone",
    "subject_facing",
    "observer",
    "observed_target",
    "audience_evidence",
    "occlusion",
    "transition",
    "next_state"
  ],
  "block_when": [
    "required_state_unknown",
    "camera_cannot_see_claimed_evidence",
    "state_change_has_no_action_or_cut",
    "audience_evidence_missing"
  ],
  "max_passes": 1
}
```
<!-- spatial-preflight-contract:end -->

## 1. 使用方式

主执行者在图片设计时识别空间风险，统一机位、人物朝向、支撑及参考职责；复杂多人关系按任务需要由不同观察路径复核。区分原文明确事实和自行设计的细节，不用未经证实的设置冒充原始事实。

默认一次完整扫查，修复后只重查受影响镜头与衔接；`max_passes: 1` 不限制必要的局部修复和复验。

## 2. State row

```text
shot_id:
camera_zone: 门外 | 门内 | 人物前方 | 人物后方 | 人物侧面 | 明确坐标
camera_facing:
shot_size:
subject_zone:
subject_facing:
observer:
observed_target:
audience_evidence:
occlusion:
transition: 连续动作 | 明确切镜 | 无
next_state:
unresolved_issue: 仅记录仍需解决的具体问题；没有则省略
missing_or_conflict:
```

The words may vary, but the relevant fields must be answerable; use “not applicable” where appropriate rather than inventing an observer for a shot without one. `observer` is the character who knows; `audience_evidence` is what the camera actually proves to viewers. They are not interchangeable. The main model may design unspecified details within user constraints, labeling them as design choices rather than source facts.

## 3. Single feasibility gate

- A close-up cannot also prove wide environmental information unless a visible camera move, reflection, transparent surface, or other named mechanism changes what the audience can see.
- `看到 / 发现 / 注意到` requires the observer, observation position, target, and a shot or sound that gives the audience evidence. Without audience evidence, describe only the character's reaction.
- Moving from outside to inside requires an opening/crossing action or a cut that explicitly re-establishes the new position.
- A sudden facing change requires a turn or a cut. A sudden front-to-back camera relation requires a move, crossing, cut, or newly declared setup.
- A claimed object, person, empty space, or ambush must lie inside the current camera's visible range after occlusion is considered.
- The owner resolves camera position, facing, sightline, occlusion and transition as part of the design. Ask the user only when explicit requirements conflict; unspecified creative choices are for the designer to make.
- An exception is allowed when its physical mechanism is named and visible. The gate judges geometry, not keywords.

## 4. Canonical failure and repairs

### 先建立观看方向，再发生方向相关动作

外部文本方法候选，尚无生成实测；[来源](cinematic-visual/sources.md#帅帅导演-v4-定向吸收)。当某个动作必须从指定侧面看才成立时，把机位转换放在动作前，而不是在同一瞬间同时宣布“绕到正面”和“正面已经看清接触”。

例如从侧后方跟拍转为正面接物：先利用可行路径换到前方并建立人物双手与来物的位置，再发生接物动作；两者共用原时长，不能给换侧凭空加时。一镜到底必须有连续路径，允许切镜时可直接重建前方机位；用户锁定侧后方时不强行改正面，只设计该机位确实可见的证据。世界方向、身体左右与画面左右分别判断。

每个节拍先明确承担观看任务的主运镜，附加运动只在能同时执行且不妨碍读懂动作时保留；这是可读性建议，不另设运镜数量硬指标，不覆盖受控分镜标准或明确的复合运镜要求。主体高速不等于摄影机必须追上，用户要求固定机位、掠过画面或有意跟拍滞后时保留该拍法。

Invalid: `正面特写人物，他推门进屋，看见屋内空荡荡。` A persistent front close-up can show the reaction but cannot simultaneously prove the room behind the camera is empty.

Three-shot repair:

```text
镜头1：从人物后方中景跟随，他推门并跨过门槛。
镜头2：切人物主观广角，空房间完整展开。
镜头3：切回人物面部特写，他停住，目光扫过房间。
```

One-shot repair:

```text
摄影机从人物右后方中景跟随进门，越过门槛后向左绕至侧后方，同时拉广，露出空房间全貌；人物停步转头，摄影机再缓慢推进至侧脸近景。
```

Close-up-only repair:

```text
正面特写人物推门后停住，眼神左右移动，呼吸放轻。
```

The close-up-only version proves only that the character noticed something unusual. A later evidence shot is required before the audience can know the room is empty.

## 5. 应用与修复

由主模型在设计和写作中持续核对目标、用户锁定项和空间状态。发现具体冲突就修对应镜头及衔接，复用已成立的设计；不用重新推演全片，也不把一次表格填写当作已验证画面。

空间类型影响设计时同时执行第7节；不能用“电影感运镜”略过实际退距、路径和遮挡。

## 6. 对话覆盖与关系板取舍

分镜设计或图片生产遇到连续正反打、坐卧高差、前景遮挡，或已报告视线／站位错误时，核对本卡中的机位、体位、朝向与遮挡。触发检查不等于需要图片。先依据叙事选择拍法：交替表达与反应可用正反打；共同动作或距离变化可用同框；用户锁定拍法优先。

检查后采取一个实际动作，不要求输出固定表格：

- **直接继续**：文字能明确空间，或现有参考已经足够。写好所需镜头，不增加关系板。
- **复用已有图**：已有合格关系图覆盖当前体位、轴线与机位需求，沿用其引用与适用范围；位置或轴线变了才检查受影响部分。
- **设计必要关系板**：仍有需要画面比较或验证的具体缺口，且多个计划机位会用到结果。用一句话交代“缺口、现有依据为何不足、各视图验证什么”，再按[可选对话关系板](../dialogue-contact-sheet.md)取模板。若用户明确要求关系板，直接按其规格设计，无需另证明必要性。

只有风险标签却说不出具体缺口时，不增加关系板。只需核对两侧越肩就两格，加双方近景才四格，需要三组角度才六格；用户指定格数优先。人物走位导致关系变化时按状态判断，不用一张“同一时刻”的板代替动作连续性。只要求展示起点和终点、没有计划使用多个正反打机位时，优先状态文字或所需同框镜头，不默认起点一张板、终点再一张板；不能自行假定下游还要正反打，以此制造关系板需求。

仅分析或提示词任务只交对应文字；实际生成须已有图片生产授权且处于数量、预算与锁定项范围内。授权覆盖所需辅助图时直接执行，不另设确认闸；只授权固定成图且没有辅助图额度时，先完成文字修正，不自行增图或挤占交付数量。

关系板生成后实际检查身份、视线、俯仰、体位、前景归属与遮挡。合格才把具体文件／会话引用和适用镜头、状态带回后续图片服务；提示词草稿只能作设计依据，不能标成已验证空间。失败板不传下游，按现有额度处理并只暂停依赖它的镜头；不能以“已做关系板”替代问题已解决。基准换版后复查受影响的下游，不重审全片。

## 7. 场景类型与机位适配

吸收自 [电影分镜来源](cinematic-visual/storyboard-source.md)。先明确可用退距、摄影机及人物路径、门窗与障碍、镜头视野、遮挡和光源安放位置。房间面积只是线索；焦段还受画幅、主体距离和目标景别影响。未知几何写成设计假设，不能装作现场测量。

| 场景 | 必查约束 | 可采用的处理 |
|---|---|---|
| 狭小封闭室内 | 退距、墙角、天花与灯位；环绕是否撞墙 | 门边观察、短距离横移、局部摇移或切换机位 |
| 普通室内 | 家具阻挡、反打背景、窗光方向 | 先定主轴及双人关系，再分解近景与反应 |
| 大型室内 | 空间锚点、空旷背景和收声距离 | 前中后景调度，用移动揭示距离或权力关系 |
| 超大型室内／挑空大厅 | 顶部结构、可用升降高度、远景中的人物辨识 | 先用空间关系交代尺度，升降仍核对通道与落点 |
| 开阔室外 | 地理方向、地平线、日光与移动范围 | 先立空间锚点，再决定远近景和跟随路径 |
| 半封闭／狭窄室外 | 围墙、建筑夹持、横向余量和顶部障碍 | 纵向跟随或端点机位，横移与高位观察须有余量 |
| 特殊封闭空间：车内、楼梯、电梯、隧道等 | 座位、玻璃反射、栏杆遮挡、高低差及退行路径 | 明确机位内外和所在层；分段建立关系，切镜继承位置 |

错误：“三平方米房间内完整绕人一周”，未给出可通行路径。修正：若设定没有该路径，改成门口侧移后切反应；若用户锁定环绕，先明确开放墙体或其他已允许的摄影条件，再判断。不能只凭“三平方米”作绝对禁令，也不能凭生成画面可虚构就让镜头无说明穿墙。
