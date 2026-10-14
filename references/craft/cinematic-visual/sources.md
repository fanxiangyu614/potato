# 来源与吸收范围（维护时读取）

2026-09-11 另吸收用户提供的《专业电影分镜脚本生成器》：出处、指纹、吸收映射与冲突处理见 [独立来源记录](storyboard-source.md)。该文件是独立来源，不归入下列 ZY 作品或其授权声明。

- 来源标识：`external-source://zy-cinematic-realism-main.zip`
- 来源作品：造梦师：AI时代电影视觉指南 / DREAM DIRECTOR / zy-cinematic-realism，包内声明 v2.1.0。
- 作者：Copyright (c) 2026 ZY / popopo-99。
- 原仓库：https://github.com/popopo-99/zy-cinematic-realism
- 原授权：CC BY-NC 4.0，https://creativecommons.org/licenses/by-nc/4.0/ 。本目录改编内容保留该署名及非商业授权信息；不改变土豆风暴其他内容的授权。
- 原包 SHA-256：`bc3bdf68e234eaf12bbfbcbd52bdd5fe3edf02dd949990b84e698322252bc8c4`。
- 可用性：本次读取了用户提供的压缩包；原包未随土豆风暴分发，运行本目录不依赖原包路径或网络。仓库与模型网页未在本次吸收中联网核验。
- 改编说明：2026-09-08，根据用户授权重新分类、中文压缩并适配土豆风暴视频／资产流程。以下均为资料方法，不是实测模型性能或成片成功案例。
- 导演扩充：同日按用户进一步要求补齐原包全部 38 位，每位独立中文卡；姓名／别名／创作目标放入二级导演索引，普通画面问题不加载该名单。保留四轴、具体戏剧方法、误读与相近导演区别，仍不采用强制最强或为风格改戏的规则。

## 知识落点

下列原路径均相对于原包内 `zy-cinematic-realism/`，只是来源定位，不是运行时读取路径。

| 本地卡 | 主要原资料 | 本次取舍 |
|---|---|---|
| light-material.md | references/cinematic-principles.md、camera-and-light.md、anti-ai-cleanup.md、cinematography-cards.md | 光源作用范围、材质响应、选择性可读；补充关键动作及资产母版不能被阴影隐藏 |
| director-grammar.md | references/director-routing.md、directors/recommendation-matrix.md | 四轴与区别；删除强制最强、强制改三个观看决策、固定输出块 |
| directors/fincher.md | references/directors/david-fincher.md | 程序证据与四轴，保留误读及与维伦纽瓦的区别 |
| directors/villeneuve.md | references/directors/denis-villeneuve.md | 环境压力与四轴，不用静默替代锁定动作 |
| directors/wong-kar-wai.md | references/directors/wong-kar-wai.md | 混合实景光与空间阻隔，不强加霓虹、烟和爱情故事 |
| directors/koreeda.md | references/directors/hirokazu-koreeda.md | 日常行为与关系，不强制增加人物或流程 |
| narrative-evidence.md | references/cinematic-principles.md、style-cards.md、creative-shuffle.md | 因果环境与微动作；不搬入全部风格库，不强制等待与余波 |
| scene-adaptation.md | references/prompt-compiler.md、continuity-cards.md | 统一场景底稿与必要差异；复用现有记录，增加视频时长／动作／声音保真 |
| revision.md | references/remix.md、result-repair.md、prompt-check.md | 单轴边界、物理后果与结构分流；不承诺文字可以锁定像素 |

## 全量导演来源对应

[导演索引](directors/index.md) 中 38 个条目均有独立正文。上表已列出的四张卡保留原文件名映射：`fincher.md` 对应 `david-fincher.md`，`villeneuve.md` 对应 `denis-villeneuve.md`，`koreeda.md` 对应 `hirokazu-koreeda.md`，`wong-kar-wai.md` 同名。其余 34 张本地 `directors/<文件名>.md` 均逐份改写自原包的 `references/directors/<同一文件名>.md`，不从姓名补写无原文依据的条目。

本地 `directors/index.md` 的姓名与方法摘要根据这些条目的 Identity、Best suited for 与 Core Dramatic Logic 整理；创作目标导航参考原 `recommendation-matrix.md` 并结合各条目交叉归类，是检索组织而非固定推荐排名。新增别名用于定位，不构成另一个导演条目。

未吸收：原模型适配器和能力矩阵、参数默认值、16 风格与 8 摄影卡全文、其余图片示例及原脚本。今后超出这 38 位扩充仍须有实际需求和原文依据，更新索引与本记录，不补空卡，不以原文归纳代替成片验证。

## 2026-09-11 定向补充

再次读取用户所给原包，SHA-256 与上述记录一致。新增内容继续保留 ZY / popopo-99 署名及 CC BY-NC 4.0；中文重组为土豆风暴按需调用卡，不采用原包默认双卡、固定输出块、强制最强导演或优先等待的规则。

- `witness-position.md`：原 `references/cinematography-cards.md` 的 Available-Light Handheld、Wide Environmental Witness、Compressed Nocturnal Observation、Hard Direct Flash、Deep-Focus Spatial Blocking；及 `references/style-cards.md` 的 Peripheral Witness。已有自然光、低照室内和阴天材质方法不重复建卡。
- `environment-blocking.md`：原 `references/style-cards.md` 的 Nocturnal Procedure、Memory in Transit、Weather-Borne Intimacy、Landscape of Duty、Infrastructural Sublime、Ritual Realism、Historical Material Realism；取环境约束行动的判断，不复制固定剧情。
- `director-comparison.md` 与 `examples` 的三张 WebP：原包根目录 `docs/director-style-comparison.md` 与 `docs/images/director-style-comparison/{baseline,david-fincher,wong-kar-wai}.webp`。图像原字节收录，逐图查看后另写可见差异及连续性限制；工作台仅展示两张导演示例，图片数据不进入生成请求。

这次没有新增导演，没有声称完整吸收16风格全文；未导入模型适配器、参数或原脚本，没有进行图片生成或模型效果实测。

## 帅帅导演 v4 定向吸收

- 来源标识：`external-source://shuaishuai-director-system-v4.0.zip`，包内入口为 `shuaishuai-prompt-director/SKILL.md`，自称 SHUAISHUAI Director System v4。
- 原包 SHA-256：`bc9a63491f110ffa751b56cc51b59051a614ef54d7a0070f3a2284c98b0a08d0`。
- 2026-09-21：用户授权按建议补充知识；已读取所给包内入口和参考文档，采用前重新核对下表对应正文。原包不随技能分发，运行不依赖原包路径。
- 证据状态：`candidate / method_extracted`。没有平台生成实验、成片成功证据或独立作者核验；只吸收提示词组织与检查方法，不升级为已验证的平台能力或通用性能定律。
- 署名与授权边界：来源保留包内系统名称；包内未见独立许可证文件，不推定开放许可。此来源独立于前文 ZY 作品，不套用其署名或 CC BY-NC 声明。本次为用户授权的本地方法归纳，不复制整套原文、图标或示例库，不据此声明取得对外分发授权。

原资料路径相对于包内 `shuaishuai-prompt-director/`，仅用于追溯：

| 原资料 | 原位落点 | 增量与边界 |
|---|---|---|
| `references/motion-bible.md` 的 Execution grammar、Speed and rhythm、Transition continuity | [动作句与速度衔接](../action-endpoint-continuity.md#动作句与速度衔接) | 补动作表达顺序与高速段恢复衔接；不填伪精确角度，不删锁定动作，不改一镜到底 |
| `references/motion-bible.md` 的 Anchor system；`references/viral-library.md` 的 Hard Cut checklist | [匹配转场](coverage-and-editing.md#匹配转场的锚点与切点) | 补切点、变化项与不变项；不搬固定锚点数量、十二秒时间线和三段定势模板 |
| `references/camera-bible.md` 的 Movement rules | [空间预演第4节](../spatial-shootability-preflight.md#4-canonical-failure-and-repairs) | 先建立观看方向，再发生依赖该视角的动作；固定机位与有意跟拍滞后不被覆盖 |
| `../../../skills/potato-storm/SKILL.md` 的 Compression；`references/seedance-deploy.md` 的 Compression pass | [提示词压缩检查](../storyboard-review-execution.md#提示词压缩检查) | 按执行信息而非字数裁剪；补独立生成片段不能依赖“同上”的适配边界 |

已有而不重复导入：人物与参考职责锁定、一般动作连续性、按任务取模块、环境因果微动、音乐主导作品的卡点。保留现有[环境叙事](narrative-evidence.md)与音乐设计（历史视频知识，本独立图片包未附该路由）的适用范围，不新增“所有背景都动”或“所有剧情先配音乐”的要求。

未吸收：固定问候、宽泛触发词、另一套模块和专家体系、默认审美排除、平台参数、地点库及十二秒示例库。该次采用时未改变既有受控分镜数值和平台限制；后续授权整改已将通用审美配额改为按需诊断，当前执行以 `controlled-storyboard-standard.md` 为准，平台及项目明确锁仍有效。本次四类文本边界演练仅检查知识采用与锁定项保真，不作为视频效果验证或新成功案例。

## 安爷轻量版定向吸收

- 来源标识：`external-source://安爷skill09.15_V6.19.2_SKILL_真人摄影见证感_阿糕负责_轻量安装版.zip`；包内根目录 `jimeng-seedance-director/`，名称与版本沿用用户提供包的标识。
- 原包 SHA-256：`9991dacb13fd3734dfc46454edff2d4a686d0323f669bdebed79d3c414a385c1`。已读取下表原文并按用户授权本地归纳；运行不依赖原包或外置库。
- 证据状态：`candidate / method_extracted`。没有本地平台生成、成片成功或独立效果验证；源包的个人偏好、朋友成功范本和自述实测不升级为土豆风暴的确认案例。
- 可用范围：仅本次轻量包实际附带内容。其索引引用的 34AI 全文、百大导演、100 组转场全文及外置成功母版未随包提供，不声明已读取或吸收。
- 授权边界：本地方法归纳不等于取得源包对外分发许可；不复制整包、长段原文、图标或案例，也不把既有 ZY 来源授权套用于此来源。

| 原资料（相对包内根目录） | 本地落点 | 方法与适用边界 |
|---|---|---|
| `MODULES/CAMERA_WITNESS_REALISM.md` | [临场响应候选](witness-position.md#临场响应候选) | 事件触发补追、重新构图或焦点恢复；每镜少量合理痕迹，固定机位与静态资产不强加运镜 |
| `MODULES/PERFORMANCE.md`、`MODULES/ACTING_CAUSALITY.md` | [特写微反应候选](../acting-performance.md#特写微反应候选) | 隐藏目标下的泄露与压制，限可读特写，不把肌群流程变成每次必做 |
| `PROJECTS/COUPLE_STORY.md` | [双人关系互动候选](../acting-performance.md#双人关系互动候选) | 双向回应改变下一行动，保留既定关系结局，不复制水族馆剧情或必然亲密收尾 |
| `MODULES/DANCE_DIRECTION.md`、`MODULES/DANCE_CLASSICAL_IN_PLACE.md`、`CAPABILITIES/DANCE.md` | [艺术表演知识卡](../artistic-performance.md) 的舞蹈编排与摄影协作候选 | 支撑与落点可读、技巧和表情景别分工、原地回轴的条件；不搬具体六段舞谱与固定参数 |

摄影与剧情表演知识并入现有卡；按用户归属纠正，舞蹈从镜头语言卡迁至共享艺术表演卡，供跳舞与 MV 复用，原镜头卡只留协作引用。艺术表演卡的任务分流与 MV 复用边界为本地维护补充，不冒充源包原文或已验证效果。入口按问题直达，不另建导演体系、岗位或学习索引条目。未导入全视频默认 BGM、统一 1500 字、个人默认打法、舞台造型、固定时间线或新的平台能力声明；既有版本、声音、分镜与团队规则不变。文本边界检查不等于成片效果验证。

## 独立图片包改编说明

本目录从土豆风暴工艺资料本地整理到独立图片技能，保留来源署名、来源指纹、候选证据状态与上述授权差异。静态图片相关方法按需采用；视频模型、音轨、专家系统、学习索引及项目管理依赖未搬入。来源定位中的原包路径只用于追溯，不是本技能可读取的运行文件。三张WebP保持原字节，未生成或修改示例图。
