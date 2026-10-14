"""Random photo: brief."""
from .schema import era_text


def style_view(style):
    # Do not compile recovery phrases, example prompts, or quality slogans.
    keys = {"style_id": "style_id", "中文风格名": "name", "类别": "category", "视觉DNA / 关键词": "visual_dna", "材质/色彩/光线": "light_color"}
    return {target: style[key] for key, target in keys.items() if key in style}


def photography_scope(plan):
    # A primary backdrop and a secondary painted panel are separate layers,
    # even when both recipes call their region "background".
    styles = [('primary', plan['style'], plan['style']['region_medium'])]
    if 'secondary_style' in plan:
        styles.append(('secondary', plan['secondary_style'], plan['secondary_style']['medium']))
    separate_background = any(style['region'] == 'background' for _, style, _ in styles)
    layers = [
        {'id': 'subject', 'region': 'subject', 'medium': plan['medium'], 'label': '人物摄影层' if plan['medium'] == '真人' else '人物艺术层'},
        {'id': 'environment', 'region': 'environment', 'medium': plan['medium'],
         'label': '现场落点与动作支撑（不含单列风格区域）' if separate_background else '现场环境（不含单列风格区域）'},
    ]
    region_names = {'background': '背景', 'prop': '陈列物', 'format': '版式',
                    'outfit_surface': '衣装表面', 'light': '光线', 'overall': '整体风格', 'subject': '人物风格'}
    for role, style, medium in styles:
        if style['region'] in ('subject', 'overall', 'light') and medium == plan['medium']:
            continue  # These describe the existing subject/environment, not a new layer.
        layers.append({'id': f"{role}:{style['region']}", 'region': style['region'], 'medium': medium,
                       'style_id': style['style_id'],
                       'label': f"{'主' if role == 'primary' else '副'}风格{style['style_id']}的{region_names[style['region']]}"})
    regions = [layer['id'] for layer in layers if layer['medium'] == '真人']
    return {'layers': layers, 'regions': regions,
            'excluded_art_regions': [layer['id'] for layer in layers if layer['medium'] != '真人'],
            'rule_reference': 'references/default-image-photography.md' if regions else None,
            'apply_only_for': 'confirmed GPT built-in photographic image entry; not an unknown host default'}


def signature_plan(plan, policy):
    if plan['class_id'] != 1 or policy == 'none':
        return {'enabled': False, 'reason': 'user disabled' if policy == 'none' else 'non-COS class'}
    name = plan['outfit']['character'].strip()
    english = plan['outfit'].get('character_english', '').strip()
    label = name + (' · ' + english if english and english not in name else '')
    return {'enabled': True, 'text': label, 'position': 'lower-left',
            'prompt': f'左下角小面积原创手写艺术署名“{label}”，与角色气质相符，不遮挡人物，不做官方Logo；除此之外不添加无关文字。'}


def photography_targets(plan):
    """Resolve defaults for photographic layers before model-specific composition."""
    scope = plan['photography_scope']
    if not scope['regions']:
        return None
    defaults = {'light': '主光只照到指定区域；无额外填充，主体背光面与邻近环境合为连贯深黑，最深处无纹理；强光可过曝，不同时恢复两端细节',
                'material': '大形与材质各自反射成立，次要纹理合并',
                'grain': '摄影区域细小单色颗粒轻微可感，黑位不抬灰',
                'color': '黑位扎实，亮部保留颜色，不全局蒙灰或褪色'}
    per_region = {region: dict(defaults) for region in scope['regions']}
    if 'subject' in per_region:
        per_region['subject'].update(identity='先核对身份与比例', focus='脸可见且达到可辨尺度时对焦近眼；背影或极远景对焦本张动作/空间观看重点，不强求不可见五官',
                                    skin='偏哑光宽缓受光，暗侧面颈随遮挡沉下去，脸可见且达到可辨尺度时保留主要五官；不全脸补亮，不以油亮或毛孔证明真实', hair='头发以少量完整发束和连续轮廓为主，省去外围飞丝、逆光细亮线及内部沟纹；暗发束合并为无细节色块')
    applied = []
    styles = [('primary', plan['style'])]
    if 'secondary_style' in plan:
        styles.append(('secondary', plan['secondary_style']))
    for role, style in styles:
        overrides = style.get('photography_overrides', {})
        medium = style.get('region_medium', style.get('medium'))
        if not overrides or medium != '真人':
            continue
        if style['region'] in ('overall', 'light'):
            regions = [r for r in ('subject', 'environment') if r in per_region]
        elif style['region'] == 'subject':
            regions = ['subject'] if 'subject' in per_region else []
        else:
            regions = [f"{role}:{style['region']}"] if f"{role}:{style['region']}" in per_region else []
        for region in regions:
            changes = {key: value for key, value in overrides.items() if key in per_region[region]}
            per_region[region].update(changes)
            if changes:
                applied.append({'style_id': style['style_id'], 'region': region, 'replacements': changes})
    # Common goals are safe for every photographic region; regional goals are authoritative.
    first = next(iter(per_region.values()))
    common = {key: value for key, value in first.items()
              if all(target.get(key) == value for target in per_region.values())}
    return {'rule_reference': 'references/default-image-photography.md', 'regions': scope['regions'],
            'excluded_art_regions': scope['excluded_art_regions'], 'targets': common,
            'region_targets': per_region, 'style_overrides': applied,
            'apply_only_for': scope['apply_only_for']}


def compile_prompt(plan):
    # Compile a creative brief; the executor resolves styling and shot design.
    # The structured prop states below are authoritative; author-generated
    # summaries after this marker repeat the same fields and need not be sent twice.
    activity_prompt = plan['activity']['prompt'].split(' 道具套组：', 1)[0]
    text = [f"主体采用{plan['medium']}表达，一位成年主角；身份参考只保留可辨认的脸型、五官比例和用户明确锁定的特征；妆容、发型、发色与饰品按本次角色衣装和活动成套设计，不自动继承身份图妆发。",
            "参考职责：服装图仅提供衣装结构、配色、识别饰物与选用道具外形；其他模特整张穿衣照只供观察，不直接上传。动作、场景、构图与画风按下方方案，提交前按随机拍照规则核对实际附件与职责。",
            f"妆造：{plan['outfit']['prompt']}", f"活动：{plan['theme']['prompt']}",
            f"现场：{plan['location']['prompt']}", f"具体位置：{plan['activity']['position']}",
            f"动作：{plan['pose']['prompt']}", f"组合关系：{activity_prompt}",
            f"情境：{era_text(plan['activity']['era_context'], plan['activity']['id'])}", f"人物关系：{plan['activity']['people']['relationship']}"]
    for state in plan['activity']['prop_states']:
        text.append(f"道具：{state['prop']['prompt']}；数量{state['count']}；持有者{state['holder']}；状态{state['state']}"
                    + (f"；位置/手部{state['hand']}" if state.get('hand') else ""))
    if plan.get('aspect_ratio'):
        text.insert(0, f"画幅比例：{plan['aspect_ratio']}，按此比例构图。")
    if plan['activity'].get('shot'):
        shot = plan['activity']['shot']
        text.append(f"拍摄套组：时机{shot['moment']}；机位{shot['camera_position']}；景别{shot['framing']}；观看重点{shot['viewing_target']}。")
    if plan['signature']['enabled']:
        text.append(plan['signature']['prompt'])
    text.append(f"主风格作用于{plan['style']['region']}：{plan['style']['prompt']}")
    if plan['style_mix'] == 'dual':
        secondary = plan['secondary_style']
        text.append(f"副风格作用于{secondary['region']}，采用{secondary['medium']}：{secondary['prompt']}")
        text.append(f"融合方式：{plan['style_combination']['integration_prompt']}")
    scope = photography_scope(plan)
    digital = [layer['id'] for layer in scope['layers'] if layer['medium'] in ('3D', 'CG')]
    if digital:
        text.append('渲染风格：UE5 render style，仅作用于3D/CG区域（' + '、'.join(digital) + '）；保留所选风格DNA，不覆盖真人或2D区域。')
    return '\n'.join(text)


def finalize_brief(plan, aspect_ratio, signature):
    plan['aspect_ratio'] = aspect_ratio
    plan['signature'] = signature_plan(plan, signature)
    plan['creative_intent'] = {
        'identity': '用户原始身份参考的脸型及五官比例；妆发按本次衣装活动设计',
        'styling_families': plan['outfit']['styling_families'],
        'outfit': plan['outfit']['id'], 'activity': plan['activity']['id'],
        'shot': plan['activity'].get('shot'),
        'primary_effect': plan['style']['visual_effect'],
        'integration': plan.get('style_combination', {}).get('integration_prompt'),
        'stage': 'complete lighting and styling during prompt composition; compare final image to this intent'}
    plan['shot_requirements'] = [
        {'style_id': style['style_id'], **style['shot_requirements']}
        for style in (plan['style'], plan.get('secondary_style', {})) if style.get('shot_requirements')]
    plan['compatibility_review'] = {
        'status': 'required_before_submission',
        'dimensions': ['人物与服饰', '服饰与动作道具', '场景与活动支撑', '主副风格与既有内容', '镜头与风格'],
        'instruction': '逐项按原文核对并完成最终编排；任一硬冲突未解决不可提交。保持用户锁定，不能用气质标签或平均分抵消。参见random-photo.md搭配成立后才可提交'}
    plan['prompt_text'] = compile_prompt(plan)
    plan['rendering_intent'] = {
        'detail': '脸可见且达到可辨尺度时保留主要结构；头发成组、轮廓连贯，减少外围碎发、细亮线与暗部纹理；其他信息服从观看重点',
        'light': '指定受光与连贯暗区，阴影允许隐去次要结构；不以局部提亮恢复每个表面，不叠加全域清晰度或HDR式细节',
        'medium': '真人按摄影目标；2D用色面和笔触合并，3D用大体块和宽缓反射，CG用数字笔触与合成明暗；不把艺术人物强制改摄影',
        'scope': '随机人物创作的构图与信息取舍目标；不移植默认模型专用参数。明确风格可改变影调，不自动增加碎发或抬亮所有阴影'}
    plan['delivery_requirements'] = {
        'review': '实际看图并与原始身份及本张目标对照，指出具体区域问题',
        'repair': '有影响使用的偏差时，在最终回复直接给每张完整可复制修复提示词、建议模型与参考顺序；不能只存文件或只说可以修',
        'authorization': '建议不等于修图授权，不自动增加付费生成'}
    plan['composition_policy'] = {
        'variation': '对照本批/当前对话已交付画面的动作轮廓、机位方向高度、景别与人物占比，按random-photo.md编排明显差异；不改变骰点与显式锁定',
        'revision': '定制动作时同步更新最终动作、活动关系、镜头与creative_intent，保留抽样底稿及来源事实',
        'scale': '巨构场地读取references/megastructure-scenes.md，选择建筑主导、人景叙事或人物主导，不统一缩小人物',
        'sampling': '底稿允许重复；差异设计发生在最终编排，不宣称独立等概率无重复'}
    plan['prompt_stage'] = 'creative_brief'
    plan['requires_prompt_composition'] = True
    plan['photography_scope'] = photography_scope(plan)
    plan['digital_rendering'] = {
        'style': 'UE5 render style',
        'regions': [layer['id'] for layer in plan['photography_scope']['layers'] if layer['medium'] in ('3D', 'CG')],
        'meaning': '区域渲染风格意图，不宣称实际引擎；用户明确指定优先'}
    plan['built_in_photography_targets'] = photography_targets(plan)
    plan['visual_checks'] = {'identity': '脸可见且可辨时，与原始身份参考对照脸型、眼距/眼形、鼻唇比例及自然表情；否则核对可见轮廓和衣装并注明无法验证五官身份，不改原构图',
                             'reference_scope': '对照已选方案，检查服装参考是否越界带入来源模特的姿势、场景、构图或画风',
                             'styling': '按实际可见范围核对妆容、发型/发色与人物、衣装和活动协调，不因身份参考自动锁定原妆发，不强求远景五官',
                             'lighting': '同一画面的光源、受光/遮挡、暗区和风格区域共同成立',
                             'focus': '脸可见且达到可辨尺度时近眼平面主要结构可辨；背影/极远景检查动作和空间焦点，不以五官不可见判错' if plan['medium'] == '真人' else '按主体媒介核对观看重点',
                             'main_style': plan['style']['visual_effect'],
                             'signature': plan['signature'], 'shot': plan['activity'].get('shot'),
                             'photography': '逐区域对照 built_in_photography_targets.region_targets；已替换项不再按旧默认验收' if plan['built_in_photography_targets'] else None}

