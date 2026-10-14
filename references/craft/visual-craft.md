# Visual craft

Load this card when locking style, writing identity, planning assets, or generating a requested image. Do not load it to decorate a text-only outline.

图片制作先核对实际身份、衣装与空间参考的职责及可用范围；只补当前画面真正缺失的依据。多个视角保持同一门窗、家具、尺度与光源；只有用户已授权且确有用途时才制作辅助图，不凭完整平面图或四向图模板增加数量。

实际生成分镜图时，以导演意图、已定导演风格与镜头惯性、剧本和该镜提示词为依据，先采用镜头语言知识落实观看位置、景别、构图、调度、光影和前后关联；不为凑图拆镜，不用“电影感”标签代替设计。执行本技能的 [逐张制作与六项验收](../storyboard-image-quality.md)：按该卡验收与处理，不在本卡另设调用或修复次数。内置知识不足时可定向联网查证，不覆盖用户锁定项。

设计写实电影画面的光源与材质、导演风格、环境叙事，或处理场景转码与受控修复时，从 [共享电影画面索引](cinematic-visual/index.md) 只取当前所需卡片。保留本卡的风格 ID 与资产职责；共享知识不增加另一套资产或强制输出表。

## Reuse the approved visual direction

Reuse the approved style. Only when missing information would materially change the result, clarify the relevant choice below; do not repeat questions already answered:

1. What world? reality / fantasy / past / future
2. What should the audience feel? immersion / warmth / spectacle / artifice
3. What should the image resemble? film / animation / illustration / dream

| ID | Look | Look cues (select and translate for the current scene) | Privacy |
|----|------|---------------------------------------------------|---------|
| A1 | cinematic photoreal | Physically grounded witness position, source-based light, differentiated materials, scene-appropriate exposure and depth of field | medium-high |
| A2 | documentary | Available light and observed behavior; handheld only when the requested camera permits it | medium |
| A3 | vintage film | Period-appropriate capture and color; grain, light leaks and vignette only when requested or supported by the chosen medium | medium |
| B1 | 3D animation | `3D animated scene, Pixar Disney quality, soft global illumination, stylized rendering, subsurface scattering` | none |
| B2 | anime | `Anime style frame, Japanese animation quality, cel shading, clean linework, vibrant flat colors` | none |
| B3 | 2D hand-drawn | `Hand-drawn animation frame, watercolor texture, soft brush strokes, paper grain` | none |
| C1 | concept art | `Cinematic concept art, matte painting quality, atmospheric perspective, painterly brushwork` | none |
| C2 | ink / guofeng | `Chinese ink painting style, sumi-e brush strokes, ink wash gradient, rice paper texture, negative space` | none |
| C3 | cyberpunk | `Cyberpunk scene, neon lights, cyan and magenta color scheme, rain-slick reflections, high contrast` | none |
| C4 | stop motion | `Stop motion animation, claymation texture, miniature set, handmade quality, tilt-shift` | none |
| D1 | film noir | `Film noir frame, black and white, high contrast chiaroscuro, venetian blind shadows` | none |
| D2 | graphic novel | `Graphic novel panel, bold black outlines, pop art color palette, halftone dot shading` | none |
| D3 | surreal | `Surreal dreamscape, soft focus, ethereal glow, floating elements, pastel gradient colors` | none |

Keep one primary look; add secondary cues only when requested and compatible with the scene. If the chosen style cannot be delivered, report the actual limitation and keep the approved style; changing to concept art or another style requires the user's decision.

For A1/A2/A3, the style ID is a continuity label, not a mandatory keyword suffix or prefix. Translate the relevant look into the current camera, source light and material decisions; do not automatically add camera brands, anamorphic lenses, shallow focus, handheld shake or grain. Use “film still” only for a static story image, not as the default wording for moving video. User-fixed camera, readable asset geometry, actions and explicit aesthetic choices prevail.

Do not dump this table into every reply. Use the locked ID only.

## Identity lock: form, color, material

For each recurring character, write one compact lock and reuse it. Do not synonym-rewrite it shot to shot.

- Form: user-locked face shape, facial proportions, height and body proportion; hair silhouette only when explicitly locked.
- Color: locked identity features plus the selected styling; hair, makeup and garment colors follow this task rather than inheriting the identity photo by default.
- Material: skin reflectance, hair finish, fabric finish, metal finish.

Texture quality comes from material language, not from a catalog of 100 palettes:

- skin: matte / sheen / oily / velvet; skin texture follows the chosen model and photographic treatment; do not add pores as a universal quality requirement
- hair: silk, coarse, mist, wet
- cloth: satin, linen, leather, cotton
- forbid: plastic skin, waxy hair, paper-thin fabric, extra fingers, chibi proportions unless requested

Wardrobe may change. Keep the user-locked face, proportions and recognition anchors. Hair, makeup and wardrobe remain adjustable unless explicitly locked.

## Character sheet format

用户已有明确版式时以其为准；本卡的可选人设板示例采用一张 16:9 横图、三个区域：

- 左侧：同一人物正脸大头像，完整呈现面部和发型。
- 中间：正面无头身体，展示颈部以下的服装、手、道具及双脚；头部确实不画，颈部为干净展示截面，不是把头顶推到画布外，也不是缩放或裁切整个身体。
- 最右侧：有头的完整背面人物，显示后脑、背部服装与双脚。
- 正反身体使用相同人物比例、肩胯尺度及脚底基线；中间因无头而较低，不把无头身体拉高到背面头顶。服装、道具与身份保持一致，背景干净。
- 不自动增加侧面、3/4 身体或第四格。文字标签按任务需要添加。

Hero Bust is a separate job: 3/4 chest-up identity still when that reference has an actual image task. Do not replace the turnaround with it, and do not require it when the user only asked for a sheet.

When generating a character sheet, use the format above and [图片资产协作](../asset-handoff.md) for the requested image job; apply this project's style ID and identity lock. Do not let image production change occupancy, wardrobe count, or story facts.

## Generate only the requested job

| Job | Make it when | Do not make it when |
|-----|--------------|---------------------|
| identity-sheet | recurring face must stay stable | one-off extra in a wide shot |
| hero-bust | a requested close identity reference is necessary | user only needs a turnaround |
| wardrobe | clothes actually change | the requested batch uses one look |
| location-master | geography must stay stable | the scene never returns |
| location-angle | a specific camera side is needed | a master already covers it |
| hero-prop | the object gets a close-up or changes state | it is set dressing |
| last-frame | the next shot must inherit a proven image | user did not ask to generate frames |

Never generate six location views, a 360 turn, or a photography board because a template exists. Never chain first frames for every shot unless the user asked.

## Image calls

图片调用、重试及干净参考服从当前用户授权、实际模型入口和本技能的[图片质量规则](../storyboard-image-quality.md)。本卡不新增调用或修复额度。人物图检查实际在场关系，不能因当前构图看不到同伴就改写其在场事实。

**用户可以否决一切**: style ID, prefix, identity lock, sheet layout, or any generation.
