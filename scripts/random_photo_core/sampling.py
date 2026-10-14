"""Random photo: sampling."""
import hashlib
import random
import secrets
from .schema import BRANCHES, MEDIA, PORTRAIT_KINDS, REGIONS, normalize_aspect_ratio, require
from .library import pools
from .online import load_online_pool, online_activity
from .brief import finalize_brief, style_view


def rng(seed, index, dimension):
    digest = hashlib.sha256(f"{seed}:{index}:{dimension}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def context_fits(profile, outfit=None, location=None):
    scene_tags = profile.get('required_scene_tags')
    if scene_tags and location is not None and not set(scene_tags) & set(location.get('scene_tags', [])):
        return False
    for role, card in (('outfit', outfit), ('location', location)):
        required = profile.get('required_' + role + '_affinity')
        if required and card is not None and required not in card.get('style_affinities', []):
            return False
    return True


def matching_style_links(data, main, medium, secondary_style_id=None, secondary_region=None, families=None, outfit=None, location=None):
    links = data.style_links.get((main, medium), [])
    return [c for c in links
            if context_fits(data.profiles[c['secondary_style_id']], outfit, location)
            and (secondary_style_id is None or c['secondary_style_id'] == secondary_style_id)
            and (secondary_region is None or data.secondary_recipes[c['secondary_recipe_id']][1]['region'] == secondary_region)
            and (not families or set(families) & set(c['styling_families']))
            and (not families or set(families) & set(data.profiles[c['secondary_style_id']]['styling_families']))]


def style_candidates(data, medium, mode, main_lock, mix, secondary_lock, region, presentation, families=None, outfit=None, location=None):
    candidates = []
    for sid in ([main_lock] if main_lock in data.primary_pools[medium] else [] if main_lock else data.primary_pools[medium]):
        profile = data.profiles[sid]
        if not context_fits(profile, outfit, location):
            continue
        if main_lock and sid != main_lock:
            continue
        if mode == 'catalog' and profile['full_catalog_medium'] != medium:
            continue
        recipe = profile['primary_recipes'][medium]
        if not main_lock and mode != 'catalog' and presentation != 'any':
            if (recipe['region'] == 'format') != (presentation == 'layout'):
                continue
        if families and not set(families) & set(profile['styling_families']):
            continue
        if mix == 'dual' and not matching_style_links(data, sid, medium, secondary_lock, region, families, outfit, location):
            continue
        candidates.append(sid)
    return candidates


def style_context(data, seed, index, medium, mode, main_lock, mix, secondary_lock, region, presentation):
    require(mode in {'medium', 'catalog'}, 'style_mode must be medium or catalog')
    require(mix in {'random', 'single', 'dual'}, 'invalid style_mix')
    require(presentation in {'scene', 'layout', 'any'}, 'invalid presentation')
    require(medium is None or medium in (*MEDIA, 'random'), 'invalid medium')
    require(mode != 'catalog' or medium is None, 'catalog mode and explicit medium lock conflict')
    for locked in (main_lock, secondary_lock):
        if locked in data.excluded_styles:
            require(False, f"Style {locked} is excluded from random-photo: {data.excluded_styles[locked]['reason']}")
    require(main_lock is None or main_lock in data.profiles, f'Unknown style lock: {main_lock}')
    require(secondary_lock is None or secondary_lock in data.profiles, f'Unknown secondary style lock: {secondary_lock}')
    require(region is None or region in REGIONS, 'invalid secondary region')
    require(mix != 'single' or secondary_lock is None and region is None, 'single style conflicts with secondary locks')
    eligible_mixes = ['single', 'dual']
    if mix == 'random' and main_lock and not secondary_lock and not region:
        eligible_media = [medium] if medium in MEDIA else MEDIA
        eligible_mixes = [branch for branch in eligible_mixes if any(
            style_candidates(data, m, mode, main_lock, branch, None, None, presentation)
            for m in eligible_media)]
        require(bool(eligible_mixes), 'No registered style branch matches the explicit locks')
    selected_mix = ('dual' if secondary_lock or region else
                    ('dual' if rng(seed,index,'style_mix').randrange(100)<20 else 'single')) if mix=='random' else mix
    if mix == 'random' and len(eligible_mixes) == 1:
        selected_mix = eligible_mixes[0]
    counts = {m: len(style_candidates(data,m,mode,main_lock,selected_mix,secondary_lock,region,presentation)) for m in MEDIA}
    if medium in MEDIA:
        selected = medium
        probability = 'locked'
    else:
        eligible = [m for m in MEDIA if counts[m]]
        require(bool(eligible), 'No registered medium/style combination matches the explicit locks')
        weights = [counts[m] if mode=='catalog' else 1 for m in eligible]
        dimension = 'catalog_medium' if mode=='catalog' else 'medium'
        selected = rng(seed,index,dimension).choices(eligible,weights=weights,k=1)[0]
        probability = f'{weights[eligible.index(selected)]}/{sum(weights)} within eligible media'
    require(counts[selected]>0, f'No registered styles for {selected} and current locks')
    return {'medium': selected, 'medium_probability': probability, 'style_mix': selected_mix,
            'style_mix_probability': ('1/1 within explicitly locked style/medium branches' if mix == 'random' and len(eligible_mixes) == 1
                                      else 'locked' if mix != 'random' or secondary_lock or region else 'single 80%; dual 20%'),
            'style_mode': mode, 'presentation': presentation, 'style_status': 'awaiting_outfit',
            'primary_style_probability': 'pending outfit compatibility'}


def select_styles(data, seed, index, medium, style_mode, style_id, style_mix, secondary_style_id, secondary_region,
                  presentation='scene', families=None, context=None, outfit=None, location=None):
    context = context or style_context(data,seed,index,medium,style_mode,style_id,style_mix,secondary_style_id,secondary_region,presentation)
    selected_medium, mix = context['medium'], context['style_mix']
    candidates=style_candidates(data,selected_medium,style_mode,style_id,mix,secondary_style_id,secondary_region,presentation,families,outfit,location)
    require(bool(candidates),'No compatible style for the chosen styling, medium and locks')
    main=rng(seed,index,'style').choice(candidates)
    profile=data.profiles[main]; recipe=profile['primary_recipes'][selected_medium]
    style=style_view(data.original_styles[main])
    style.update(region=recipe['region'],prompt=recipe['prompt'],region_medium=recipe.get('region_medium',selected_medium),
                 visual_effect=recipe.get('visual_effect',profile['core_features']))
    if profile.get('shot_requirements'):
        style['shot_requirements'] = dict(profile['shot_requirements'])
    if recipe.get('photography_overrides'):
        style['photography_overrides'] = dict(recipe['photography_overrides'])
    result=dict(context, style=style, style_status='selected',
                primary_style_probability='locked' if style_id else f'1/{len(candidates)} within selected medium/styling/locks')
    if mix=='dual':
        links=matching_style_links(data,main,selected_medium,secondary_style_id,secondary_region,families,outfit,location)
        combination=rng(seed,index,'secondary_style').choice(links)
        secondary_id, secondary_recipe=data.secondary_recipes[combination['secondary_recipe_id']]
        second=style_view(data.original_styles[secondary_id])
        second.update(region=secondary_recipe['region'],medium=secondary_recipe['medium'],prompt=secondary_recipe['prompt'],recipe_id=secondary_recipe['id'])
        if data.profiles[secondary_id].get('shot_requirements'):
            second['shot_requirements'] = dict(data.profiles[secondary_id]['shot_requirements'])
        if secondary_recipe.get('photography_overrides'):
            second['photography_overrides'] = dict(secondary_recipe['photography_overrides'])
        result.update(secondary_style=second,style_combination=combination,secondary_style_probability=f'1/{len(links)} within compatible links')
    return result


def select_shot(activity, seed, index):
    activity=dict(activity)
    options=activity.get('shot_options',[])
    if options:
        shot=rng(seed,index,'shot').choice(options)
        activity.update(shot=dict(shot),shot_id=shot['id'])
    elif activity.get('shot'):
        activity['shot_id']=activity['shot'].get('id',activity['id']+'-fixed')
    return activity


def resolve_locks(library, data, pool, online_semantics, class_id, outfit_id, theme_id,
                  activity_id, branch, portrait_kind, online_stage):
    local_lock_class = library.find_outfit_class(outfit_id) if outfit_id else None
    online_lock_classes = {p["outfit"]["class_id"] for p in pool if p["outfit"]["id"] == outfit_id} if pool is not None and outfit_id else set()
    require(len(online_lock_classes) <= 1, f"Ambiguous online outfit lock: {outfit_id}")
    online_lock_class = next(iter(online_lock_classes), None)
    require(local_lock_class is None or online_lock_class is None or local_lock_class == online_lock_class,
            f"Local and online class metadata conflict for outfit lock: {outfit_id}")
    lock_class = local_lock_class if local_lock_class is not None else (online_lock_class if online_stage == 'initial' else None)
    if class_id is not None and online_lock_class is not None:
        require(class_id == online_lock_class, 'class_id and observed outfit class conflict; original draw was kept')
    require(class_id is None or lock_class is None or class_id == lock_class,
            f"class_id and outfit_id locks conflict: class {class_id}, outfit {outfit_id} belongs to class {lock_class}")
    theme_lock = data.themes.get(theme_id) if theme_id else None
    if theme_id and theme_lock is None and pool:
        theme_lock = next((theme for theme, _ in online_semantics.values() if theme['id'] == theme_id), None)
    require(theme_id is None or theme_lock is not None, f"Unknown theme lock: {theme_id}")
    activity_lock = data.activities.get(activity_id) if activity_id else None
    online_activity_locks = [(item, *online_semantics[item['id']]) for item in pool or []
                             if online_semantics[item['id']][1]['id'] == activity_id] if activity_id else []
    if online_activity_locks:
        item, activity_theme, observed_activity = online_activity_locks[0]
        signatures = {(entry['outfit']['class_id'], theme['id'], theme['branch'], theme.get('portrait_kind'))
                      for entry, theme, _ in online_activity_locks}
        require(len(signatures) == 1, f'Ambiguous online activity lock: {activity_id}')
        if activity_lock:
            require(activity_lock['class_id'] == item['outfit']['class_id']
                    and activity_lock['theme_id'] == activity_theme['id'], 'Local/online activity lock metadata conflict')
        activity_lock = dict(observed_activity, class_id=item['outfit']['class_id'], theme_id=activity_theme['id'])
    else:
        activity_theme = data.themes[activity_lock['theme_id']] if activity_lock else None
    require(activity_id is None or activity_lock is not None, f'Unknown activity lock: {activity_id}')
    if activity_lock:
        require(theme_id is None or theme_id == activity_lock['theme_id'], 'activity and theme locks conflict')
        require(class_id is None or class_id == activity_lock['class_id'], 'activity and class locks conflict')
        require(lock_class is None or lock_class == activity_lock['class_id'], 'activity and outfit locks conflict')
        lock_class = activity_lock['class_id']
        theme_lock = activity_theme
    if theme_lock:
        require(branch == 'random' or branch == theme_lock['branch'], 'branch and theme locks conflict')
        require(portrait_kind == 'random' or portrait_kind == theme_lock.get('portrait_kind'), 'portrait_kind and theme locks conflict')
    return lock_class, theme_lock, online_lock_class, local_lock_class


def select_local_activity(library, data, seed, index, selected_class, selected_medium,
                          selected_branch, selected_kind, style_fits, outfit_id,
                          theme_id, activity_id, location_id, pose_id):
    locations, poses = library.shared()
    location_map = {card['id']: card for card in locations}
    pose_map = {card['id']: card for card in poses}
    options = []
    for outfit in library.outfits(selected_class):
        if (outfit_id is not None and outfit['id'] != outfit_id) or not style_fits(outfit):
            continue
        links = data.activity_links.get((selected_class, outfit['id'], selected_medium, selected_branch, selected_kind), [])
        matches = [a for a in links if style_fits(outfit, location_map[a['location_id']]) and (theme_id is None or a['theme_id'] == theme_id)
                   and (activity_id is None or a['id'] == activity_id)
                   and (location_id is None or a['location_id'] == location_id)
                   and (pose_id is None or a['pose_id'] == pose_id)]
        if matches:
            options.append((outfit, matches))
    require(bool(options), f"No preconnected local combination for class {selected_class}/{selected_branch}/{selected_kind}/{selected_medium}; locks were not changed")
    outfit, matches = rng(seed, index, 'outfit').choice(options)
    themes = list(dict.fromkeys(a['theme_id'] for a in matches))
    selected_theme = rng(seed, index, 'theme').choice(themes)
    selected = rng(seed, index, 'activity').choice([a for a in matches if a['theme_id'] == selected_theme])
    require(selected['location_id'] in location_map and selected['pose_id'] in pose_map, f"{selected['id']}: missing location/pose reference")
    activity = dict(selected, prop_states=[dict(state, prop=data.props[state['prop_id']]) for state in selected['prop_states']])
    return dict(status='text_plan_ready', outfit=outfit, location=location_map[selected['location_id']],
                pose=pose_map[selected['pose_id']], theme=data.themes[selected_theme], activity=activity)



def sample(library, count=1, seed=None, class_id=None, source="random", source_die=None,
           medium=None, style_id=None, outfit_id=None, location_id=None, pose_id=None, online_pool=None,
           branch="random", portrait_kind="random", theme_id=None, activity_id=None,
           style_mode="medium", style_mix="random", secondary_style_id=None, secondary_region=None,
           aspect_ratio=None, signature="auto", online_stage="resume", presentation="scene"):
    aspect_ratio = normalize_aspect_ratio(aspect_ratio)
    require(signature in ('auto', 'none'), 'signature must be auto or none')
    require(type(count) is int and 1 <= count <= 10000, "count must be between 1 and 10000")
    require(class_id is None or type(class_id) is int and 1 <= class_id <= 6, "class_id must be 1-6")
    require(source in {"random", "local", "online"}, "invalid source")
    require(source_die is None or type(source_die) is int and 1 <= source_die <= 6, "source_die must be 1-6")
    require(branch in (*BRANCHES, 'random'), 'invalid branch')
    require(portrait_kind in (*PORTRAIT_KINDS, 'random'), 'invalid portrait_kind')
    require(branch != 'themed' or portrait_kind == 'random', 'themed branch conflicts with portrait_kind lock')
    if source_die is not None and source != "random":
        require(source == ("local" if source_die <= 4 else "online"), "source and source_die locks conflict")
    require(online_stage in ('initial', 'resume'), 'online_stage must be initial or resume')
    data = pools(library)
    pool = load_online_pool(online_pool) if online_pool is not None else None
    online_semantics = {item['id']: online_activity(item, data) for item in pool} if pool else {}
    lock_class, theme_lock, online_lock_class, local_lock_class = resolve_locks(
        library, data, pool, online_semantics, class_id, outfit_id, theme_id,
        activity_id, branch, portrait_kind, online_stage)
    seed = secrets.randbits(128) if seed is None else seed
    plans = []
    for index in range(count):
        die = source_die if source_die is not None else (rng(seed, index, "source").randint(1, 6) if source == "random" else None)
        selected_source = source if source != "random" else ("local" if die <= 4 else "online")
        style_fields = style_context(data, seed, index, medium, style_mode, style_id, style_mix, secondary_style_id, secondary_region, presentation)
        selected_medium = style_fields['medium']
        style_fit_cache = {}
        def style_fits(outfit, location=None):
            key = (tuple(outfit['styling_families']), tuple(outfit.get('style_affinities', [])),
                   tuple(location.get('style_affinities', [])) if location else None,
                   tuple(location.get('scene_tags', [])) if location else None)
            if key not in style_fit_cache:
                style_fit_cache[key] = bool(style_candidates(data, selected_medium, style_mode, style_id, style_fields['style_mix'],
                                        secondary_style_id, secondary_region, presentation, outfit['styling_families'], outfit, location))
            return style_fit_cache[key]

        allowed_classes = theme_lock.get('classes', list(range(1, 7))) if theme_lock else list(range(1, 7))
        constrained = any(value is not None for value in (outfit_id, location_id, pose_id, theme_id, activity_id, style_id, secondary_style_id, secondary_region))
        local_candidates = None
        initial_online_candidates = None
        if selected_source == 'local' and constrained:
            local_outfits = {o['id']: o for c in allowed_classes for o in library.outfits(c)}
            local_locations = {l['id']: l for l in library.shared()[0]}
            local_candidates = [a for a in data.activities.values() if selected_medium in a['media']
                                and any(oid in local_outfits and (outfit_id is None or oid == outfit_id) and style_fits(local_outfits[oid],local_locations[a['location_id']]) for oid in a['outfit_ids'])
                                and (outfit_id is None or outfit_id in a['outfit_ids'])
                                and (location_id is None or a['location_id'] == location_id)
                                and (pose_id is None or a['pose_id'] == pose_id)
                                and (theme_id is None or a['theme_id'] == theme_id)
                                and (activity_id is None or a['id'] == activity_id)
                                and (branch == 'random' or data.themes[a['theme_id']]['branch'] == branch)
                                and (portrait_kind == 'random' or data.themes[a['theme_id']].get('portrait_kind') == portrait_kind)]
            eligible = {a['class_id'] for a in local_candidates}
            allowed_classes = [c for c in allowed_classes if c in eligible]
            require(bool(allowed_classes), 'No preconnected local combination matches the explicit locks')
        if selected_source == 'online' and pool is not None and online_stage == 'initial' and constrained:
            initial_online_candidates = [p for p in pool
                if style_fits(p['outfit'], p['location']) and all(selected_medium in p[role]['media'] for role in ('outfit', 'location', 'pose'))
                and all(lock is None or p[role]['id'] == lock for role, lock in (('outfit', outfit_id), ('location', location_id), ('pose', pose_id)))
                and (theme_id is None or online_semantics[p['id']][0]['id'] == theme_id)
                and (activity_id is None or online_semantics[p['id']][1]['id'] == activity_id)
                and (branch == 'random' or online_semantics[p['id']][0]['branch'] == branch)
                and (portrait_kind == 'random' or online_semantics[p['id']][0].get('portrait_kind') == portrait_kind)]
            eligible = {p['outfit']['class_id'] for p in initial_online_candidates}
            allowed_classes = [c for c in allowed_classes if c in eligible]
            require(bool(allowed_classes), 'No viewed online combination matches the initial locks')
        class_die = rng(seed, index, 'class').choice(allowed_classes) if class_id is None and lock_class is None else None
        selected_class = class_id or lock_class or class_die
        require(selected_class in allowed_classes, 'class/outfit and theme locks conflict')
        selected_branch = (theme_lock['branch'] if theme_lock else ('portrait' if portrait_kind != 'random' else
                           ('portrait' if rng(seed, index, 'branch').randrange(100) < 20 else 'themed'))) if branch == 'random' else branch
        selected_kind = None
        branch_probability = ('fixed by theme/activity lock' if theme_lock else
                              'fixed portrait kind' if portrait_kind != 'random' else
                              'fixed themed branch' if branch == 'themed' else
                              'general 50%, private 50% within locked portrait' if branch == 'portrait' else
                              'themed 80%, portrait/general 10%, portrait/private 10%')
        if selected_branch == 'portrait':
            selected_kind = theme_lock.get('portrait_kind') if theme_lock else (rng(seed, index, 'portrait_kind').choice(('general', 'private')) if portrait_kind == 'random' else portrait_kind)
        if (local_candidates is not None or initial_online_candidates is not None) and theme_lock is None:
            candidate_themes = ([data.themes[a['theme_id']] for a in local_candidates if a['class_id'] == selected_class]
                                if local_candidates is not None else
                                [online_semantics[p['id']][0] for p in initial_online_candidates if p['outfit']['class_id'] == selected_class])
            available = {(t['branch'], t.get('portrait_kind')) for t in candidate_themes}
            allowed = [(b, k, weight) for b, k, weight in [('themed', None, 80), ('portrait', 'general', 10), ('portrait', 'private', 10)]
                       if (b, k) in available and (branch == 'random' or b == branch)
                       and (portrait_kind == 'random' or k == portrait_kind)]
            require(bool(allowed), 'No activity for class and explicit branch/pose/location locks')
            if len(allowed) < (3 if branch == 'random' and portrait_kind == 'random' else 2 if branch == 'portrait' and portrait_kind == 'random' else 1):
                selected_branch, selected_kind, _ = rng(seed, index, 'conditioned_branch').choices(allowed, weights=[a[2] for a in allowed], k=1)[0]
                branch_probability = 'conditional weights: ' + ', '.join(f'{b}/{k or "none"}={w}' for b, k, w in allowed)
        plan = {"index": index + 1, "class_id": selected_class, "class_die": class_die,
                "class_probability": 'locked' if class_die is None else f'1/{len(allowed_classes)} within eligible classes',
                "activity_branch_probability": branch_probability,
                "source": selected_source, "source_die": die, "branch": selected_branch, "portrait_kind": selected_kind,
                **style_fields, "locks": {"class_id": class_id, "source": source, "source_die": source_die,
                "medium": medium, "style_id": style_id, "outfit_id": outfit_id, "location_id": location_id,
                "pose_id": pose_id, "branch": branch, "portrait_kind": portrait_kind, "theme_id": theme_id,
                "activity_id": activity_id, "style_mode": style_mode, "style_mix": style_mix,
                "aspect_ratio": aspect_ratio, "signature": signature, "online_stage": online_stage, "presentation": presentation,
                "secondary_style_id": secondary_style_id, "secondary_region": secondary_region}}
        if selected_source == 'online':
            target_themes = [t for t in data.themes.values() if selected_class in t['classes']
                             and t['branch'] == selected_branch and t.get('portrait_kind') == selected_kind]
            if initial_online_candidates is not None:
                target_themes = list({online_semantics[p['id']][0]['id']: online_semantics[p['id']][0]
                    for p in initial_online_candidates if p['outfit']['class_id'] == selected_class
                    and online_semantics[p['id']][0]['branch'] == selected_branch
                    and online_semantics[p['id']][0].get('portrait_kind') == selected_kind}.values())
            require(theme_lock is not None or bool(target_themes), 'No registered target theme for the online branch')
            target_theme = theme_lock or rng(seed, index, 'theme').choice(target_themes)
            plan['target_theme'] = target_theme
            if pool is None:
                plan.update(status='needs_online_references', required_reference_roles=['outfit', 'location', 'pose'],
                            online_pool_contract={'version': 2, 'container': 'JSON array',
                            'entry_fields': ['id', 'outfit', 'location', 'pose', 'theme', 'activity', 'provenance'],
                            'branch': selected_branch, 'portrait_kind': selected_kind, 'theme_id': target_theme['id']})
                if local_lock_class is not None:
                    plan['outfit_lock_origin'] = 'local_text_class_metadata_only'
                    plan['online_reference_status'] = 'pending_matching_viewed_candidate_for_locked_id'
            else:
                require(outfit_id is None or online_lock_class is not None,
                        f"Locked outfit {outfit_id} is absent from the viewed online pool; a local text card cannot substitute for online references")
                candidates = [p for p in pool if p['outfit']['class_id'] == selected_class and style_fits(p['outfit'], p['location'])
                              and all(selected_medium in p[role]['media'] for role in ('outfit', 'location', 'pose'))
                              and online_semantics[p['id']][0]['branch'] == selected_branch
                              and online_semantics[p['id']][0].get('portrait_kind') == selected_kind
                              and online_semantics[p['id']][0]['id'] == target_theme['id']
                              and (activity_id is None or online_semantics[p['id']][1]['id'] == activity_id)
                              and all(lock is None or p[role]['id'] == lock for role, lock in (('outfit', outfit_id), ('location', location_id), ('pose', pose_id)))]
                require(bool(candidates), f"No viewed online combination for class {selected_class}/{selected_branch}/{selected_kind}/{selected_medium} and locks")
                selected = rng(seed, index, 'online_candidate').choice(candidates)
                theme, activity = online_semantics[selected['id']]
                plan.update(status='text_plan_ready', candidate_id=selected['id'],
                            **{role: selected[role] for role in ('outfit', 'location', 'pose')},
                            theme=theme, activity=activity, reference_provenance=selected['provenance'])
        else:
            plan.update(select_local_activity(library, data, seed, index, selected_class, selected_medium,
                        selected_branch, selected_kind, style_fits, outfit_id,
                        theme_id, activity_id, location_id, pose_id))
        if plan['status'] == 'text_plan_ready':
            plan.update(select_styles(data,seed,index,medium,style_mode,style_id,style_mix,secondary_style_id,secondary_region,
                                      presentation,plan['outfit']['styling_families'],style_fields,plan['outfit'],plan['location']))
            plan['activity']=select_shot(plan['activity'],seed,index)
            finalize_brief(plan, aspect_ratio, signature)
        plan['aspect_ratio'] = aspect_ratio
        plan['requires_shot_plan'] = not bool(plan.get('activity', {}).get('shot')) or bool(plan.get('shot_requirements'))
        plan['brief_ready'] = (plan['status'] == 'text_plan_ready' and aspect_ratio is not None
                                        and not plan['requires_shot_plan'])
        plans.append(plan)
    return {'schema_version': 3, 'seed': seed, 'plans': plans,
            'requires_aspect_ratio': aspect_ratio is None,
            'aspect_ratio_question': '这次用16:9、9:16，还是其他比例？' if aspect_ratio is None else None,
            'media_verified': False}
