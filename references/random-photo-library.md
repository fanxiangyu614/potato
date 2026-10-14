# 随机拍照：文字库与网络建库

## 边界

本地妆造、场地／地点与姿势只存文字JSON卡、标签、出处和规则；不存源图、缩略图、视频、模型、图片base64或本机图片路径。用户当次身份图和最终生成图片属于任务输入／交付物，不属于本地库。

建库时可以联网看图片；本地正常运行直接使用已整理文字，来源链接供追溯。COS造型不熟悉或服装依据不足时补找服装图；无可用生图入口时提供当轮服装参考与提示词。两种情况执行[补找服装参考](random-photo-online.md#补找服装参考与无模型交付)，图片不入文字库。

## 从热门图片提炼

按六类及亚型检索近期街拍／舞台、漫展COS、成人时装、生活／旅行写真、古风拍摄等。近期趋势优先近30–90天；经典造型可保留较早来源和拍摄年份。无需强迫所有风格追热点。

实际查看图片后记录可见衣装结构、配色、妆容、发型/发色、饰品、道具、空间及支撑、身体关系和视线；名称与图注辅助身份或地理核实，不替代视觉。不可见的鞋、背面、面料材质、年代或场地不得假装看见。

保存独立妆造、场地、姿势和道具文字卡，并在建库阶段连接已成立的活动套组；同图可支持多类卡，但不是多个独立热度样本。裁切、转载与同款换色去重；不能让一个平台、名人、作品或单一服装占满某类别。观察中不保存人物长相／身份特征，不改变用户人物身份。

区分四种来源：`original_design`原创、`legacy_text`现有文字扩展、`web_visual_distilled`实际图像提炼、`hybrid`可见结构＋原创改编。`hybrid`与活动层的`mixed_adaptation`另写改编说明，指出可见依据和原创扩展；不称改编后的每套都是网上热门。

`provenance.jsonl`每行一条文字来源：`id,kind,url,title,published_at,collected_at,image_seen,image_locator,observations,popularity`。无网页的原创／旧文来源用`kind`和说明，不伪造URL。

热度分层记录：可见点赞／收藏／转发／评论等数据（带采集日期）；多个独立报道；可信编辑精选；近期发现；普通灵感。页面总流量、活动总人数和文章评论不能冒充某张图片互动。没有计数就保存null，注明“编辑精选／热点场景报道；未核实单图人气”。来源正文与公开指标可以保存有限摘要，不能搬运整篇文字或完整图库。

验证顺序：可见观察→文字转译→实质去重→服装／世界观／支撑／道具语义核对→结构与兼容检查→入库。图像无法查看的来源只能标待核实，不入`web_visual_distilled`。禁止先写卡后将搜索结果随机挂作证据。

## JSON字段

六个`outfits-1-cos.json`至`outfits-6-classical.json`及`locations.json`、`poses.json`均为数组；全部有唯一`id`、`name`、完整中文`prompt`、`media:[真人,2D,3D,CG]`及`provenance:{kind,source_ids}`。

- 妆造正文把服装、妆容、发型/发色及饰品写成与人物和活动协调的一套设计，不单独随机妆容，不记录来源模特的骨相身份。妆容写必要的眉眼唇色与光泽效果，淡妆同样具体；未看清处标原创补充。旧卡缺项按[当前妆造编排](random-photo.md#身份与完整妆造)在当次补齐，不增加来源外观锁定。字段：`class_id,subtype,styling_families,recognition_points`3–5项、`era`可多选modern/fantasy/historical/future、`mobility`从stand/walk/sit/kneel/dynamic选择、`props`实际自带物件。COS另有`character,work,costume_version,official_status`，未查官方原画不冒充官方还原。
- 场地：`eras,supports,props,allowed_classes`，正文说明空间、落脚面、可坐／可倚支撑及光源。可见地点才写地理名；不确定以场地类型表达。支撑词为standing_floor/chair/bench/bed/steps/wall/rail/table/pool_edge/mirror，标签必须与正文实际一致。
- 姿势：`stance,requires_support,requires_props`，正文说明重心、手脚、物件握持、视线与可读构图；支撑列表任一满足，道具列表全部满足。标签不能反过来创造正文没有的物件或身体能力。

`python -B -X utf8 scripts/random_photo.py validate`验证字段、620风格唯一ID、卡ID、禁止素材和每妆造的有效下游组合。它不证明源图真的看过、服装精确官方还原或实际成图好看；这些由实际观察和作品检查负责。

首版目标200妆造＋90场地＋120姿势，网络提炼卡作为实质增量逐批加入。扩到1,020独立卡需继续收集与审阅真实来源，不靠排列组合、换色或虚报数量完成。每次扩库分别报告原创、旧文字、图像提炼和改编数量，保留检查范围。

## 活动与风格索引

妆造用`theme_ids`连接活动，用非空`styling_families`连接相容风格；词表见随机拍照正文，按具体衣装赋值，不按类别统一复制。`activity-themes.json`包含id/name/prompt/branch/classes，写真另有portrait_kind；`props.json`保存id/name/prompt/kind/provenance。`activity-combinations.json`的每条完整路径包含id/class_id/outfit_ids/theme_id/media/location_id/position/pose_id/prop_states/people/prompt/era_context。本地套组以非空`shot_option_refs`保存镜头绑定，每项含原镜头`id`和共享`definition`。`shot-options.json`只合并完全相同的moment/camera_position/framing/viewing_target正文；加载后还原为`shot_options`，保留各活动的ID、次数和顺序。外部文字池仍可直接提供非空`shot_options`，不能同时提供两种形式；围绕同一物理动作提供不同相机高度、方向、景别和时机，不能用三个近义词伪装三种拍法。网络可先提供单个shot；两者都有时从shot_options抽取并写入本张shot。

`era_context`推荐 `{story_era,environment_character,shoot_context}`三段非空文字；兼容旧完整文字。现代人物在古建取景可通过已核对的套组成立，不用简单年代交集替代语义判断。

道具状态包含prop_id/count/state/holder及适用时hand。holder用main/supporting_1/supporting_2/environment；数量为正整数，手部left/right/both与腰间、头戴、桌上、架上状态分开。两件手持物不能重复占同一手；桌/架/地面物件归environment，正文交代实际支撑。姿势所需道具由衣装、现场或活动套组提供。镜像只随真正的镜面现场出现。

每套妆造在其启用媒介都必须有主题、通用写真和私房写真路径；所有正式场地与姿势连接实际活动。共享套组使用outfit_ids引用，不复制全排列。用户锁定件无连接时报缺口，不能在运行时遍历任意三卡再让模型排查。

原 `style_library.json`保留620正文。邻近的 `style-media-index.json`以`styles`保存人物适用项，以`excluded_styles`保存移出项ID、名称与理由；两者互斥且合计覆盖原库，移出项没有主副风格运行配方。人物适用项记录styling_families、core_features、primary_recipes、secondary_recipes及full_catalog_medium；主recipe包含明确region、prompt与visual_effect（实际可见的风格表现），副recipe另有区域medium/host_media。仅有明确例外的摄影recipe登记`photography_overrides`，值为需替换的light/material/grain/color/skin/hair可见目标，不允许覆盖身份与焦点。默认内置入口使用逐区域解析结果；其他模型仍按各自适配。新增风格时人工判断实际语义，运行时不以关键词猜例外。region为subject/background/outfit_surface/prop/format/light/overall：outfit_surface只指主角衣装表面，独立布样或陈列件用prop。`style-combinations.json`保存两个不同ID、主体媒介、副recipe引用、主副气质交集styling_families与integration_prompt。

分类依据原DNA及用途，原绘制/工艺结构在登记区域保留。主风格可由环境或版式承担；不可只改配色就声称原意保留。默认主池等概率，副组合在选中主风格之后条件抽取；统计分别报告登记与实际可达范围。

衣装/场地有`style_affinities`时，其值为经过内容核对的具体风格ID。风格中`required_outfit_affinity`或`required_location_affinity`要求实际卡存在该连接；气质交集不能替代它。风格限定的服装和场地各有原创配套文字卡，从已有主题和实际支撑连接活动。网络候选只有看见相应衣装结构或空间特征后才登记同样的连接，不为通过抽样随意填ID。新增动作使用状态由活动给出，衣装卡仅定义服装和配套物件，不另指挥手部。

新增或修订风格先按完整配方判断其具象前提，再登记衣装/场地亲和或场景标签；仅画法/材质语言才能跨场地复用。主副风格都检查前提，副配方不能借媒介融合引入新衣装/地点/道具；无正向依据不连边。场地标签从卡片实际空间登记，池边不是水下。机位不可分离的风格用`shot_requirements`登记，抽样后须完成定制镜头。文字结构验证不代替这一步语义判断。

实际数量由`stats`读取，分别报告独立妆造、场地、姿势、活动路径、镜头选项和风格组合；新增加的原创动作/机位注明文字设计，不挂网络热度。文字结构、实际观察、语义复核和媒体结果分别验收。

风格正文若包含不可移走的空间题材，用`required_scene_tags`连接场地的`scene_tags`，至少一项匹配；例如海岸、沙漠、太空设施、夜间演出空间。标签必须对应实际空间，不能为匹配风格把卧室标成海岸。具体场所用`required_location_affinity`，空间类型用`required_scene_tags`；明确衣装和场地题材由主风格承担，副风格选择可在同一空间成立的绘制、材料或光色语言。

## 脚本维护边界

`scripts/random_photo.py`保留原CLI与Python导入入口。`random_photo_core/`按职责组织：`schema.py`为字段和常量，`library.py`负责加载与索引，`sampling.py`负责骰子/锁定/条件抽样，`online.py`解析已观察候选，`brief.py`形成底稿和逐区域摄影目标，`reporting.py`负责结构验证及统计，`cli.py`处理命令参数。模块不会联网、检测模型或提交生图。

修改模块位置不改变随机维度、种子、候选顺序与权重；规则变更单独说明。数据和代码校验不能证明最终提示词已整合或成图通过。独立打包需包含整个`random_photo_core/`及`shot-options.json`，不能只复制入口脚本。
