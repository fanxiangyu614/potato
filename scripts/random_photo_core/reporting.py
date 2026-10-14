"""Random photo: reporting."""
from .schema import BINARY_SUFFIXES, MEDIA, PlanError, require
from .library import pools


def validate(library):
    errors, counts = [], {}
    for path in library.data_dir.rglob('*'):
        if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
            errors.append(f'Binary/visual asset forbidden in text library: {path.name}')
    try:
        data = pools(library)
        locations, poses = library.shared()
        location_map = {c['id']: c for c in locations}
        pose_map = {c['id']: c for c in poses}
        outfits = {c['id']: c for class_id in range(1, 7) for c in library.outfits(class_id)}
        all_ids = list(location_map) + list(pose_map) + list(outfits) + list(data.themes) + list(data.props) + list(data.activities)
        require(len(all_ids) == len(set(all_ids)), 'Card IDs must be unique across library roles')
        for activity in data.activities.values():
            label = activity['id']
            require(activity.get('location_id') in location_map and activity.get('pose_id') in pose_map, f'{label}: missing location/pose')
            location, pose = location_map[activity['location_id']], pose_map[activity['pose_id']]
            require(activity['class_id'] in location['allowed_classes'], f'{label}: location class mismatch')
            require(bool(set(pose['requires_support']) & set(location['supports'])), f'{label}: unsupported stance')
            provided = set(location['props']) | {data.props[s['prop_id']]['kind'] for s in activity['prop_states']}
            for outfit_id in activity['outfit_ids']:
                require(outfit_id in outfits and outfits[outfit_id]['class_id'] == activity['class_id'], f'{label}: outfit/class reference mismatch')
                outfit = outfits[outfit_id]
                require(pose['stance'] in outfit['mobility'], f'{label}/{outfit_id}: pose mobility mismatch')
                require(set(pose['requires_props']) <= provided | set(outfit['props']), f'{label}/{outfit_id}: missing required props')
                require(set(activity['media']) <= set(outfit['media']) & set(location['media']) & set(pose['media']), f'{label}: medium mismatch')
                if 'theme_ids' in outfit:
                    require(activity['theme_id'] in outfit['theme_ids'], f'{label}: theme not linked by outfit')
        for outfit in outfits.values():
            for medium in outfit['media']:
                for branch, kind in [('themed', None), ('portrait', 'general'), ('portrait', 'private')]:
                    if not data.activity_links.get((outfit['class_id'], outfit['id'], medium, branch, kind)):
                        errors.append(f"{outfit['id']}/{medium}/{branch}/{kind}: missing complete activity path")
        counts['shot_options'] = sum(len(a.get('shot_options', [])) for a in data.activities.values())
        counts.update(styles=len(library.styles), eligible_styles=len(data.profiles), excluded_styles=len(data.excluded_styles), outfits=len(outfits), locations=len(locations), poses=len(poses),
                      themes=len(data.themes), props=len(data.props), activities=len(data.activities), style_combinations=len(data.style_combinations))
        for class_id in range(1, 7):
            counts[f'class_{class_id}'] = len(library.outfits(class_id))
        usage = {role: {a[f'{role}_id'] for a in data.activities.values()} for role in ('location', 'pose')}
        counts['unlinked_locations'] = len(set(location_map) - usage['location'])
        counts['unlinked_poses'] = len(set(pose_map) - usage['pose'])
    except PlanError as exc:
        errors.append(str(exc))
    return {'valid': not errors, 'errors': errors, 'counts': counts, 'media_verified': False}


def stats(library):
    result = validate(library)
    if result['valid']:
        data = pools(library)
        media_counts = {}
        for medium in MEDIA:
            reachable = {c['secondary_recipe_id'] for c in data.style_combinations.values() if c['subject_medium'] == medium}
            background = {data.secondary_recipes[r][0] for r in reachable if data.secondary_recipes[r][1]['region'] == 'background'}
            other = {data.secondary_recipes[r][0] for r in reachable if data.secondary_recipes[r][1]['region'] != 'background'}
            primary = set(data.primary_pools[medium])
            media_counts[medium] = {'primary': len(primary), 'scene_primary': sum(data.profiles[s]['primary_recipes'][medium]['region'] != 'format' for s in primary),
                                    'layout_primary': sum(data.profiles[s]['primary_recipes'][medium]['region'] == 'format' for s in primary), 'background_secondary': len(background),
                                    'other_secondary': len(other), 'unique': len(primary | background | other)}
        result['style_media_counts'] = media_counts
        result['cross_medium_primary_styles'] = sum(len(p['primary_recipes']) > 1 for p in data.profiles.values())
    result['sampling'] = {'class_probability': '1/6 each when unlocked', 'source_probability': 'local 2/3 (dice 1-4), online 1/3 (dice 5-6)',
                          'branch_probability': 'themed 80%, portrait 20%', 'portrait_kind_probability': 'general 50%, private 50% within portrait',
                          'style_mix_probability': 'single 80%, dual 20%; independent of activity branch',
                          'style_probability': 'uniform within compatible medium/styling pool; catalog uses registered-medium weights then compatible styles',
                          'default_medium': 'random: four equal media before explicit constraints', 'network_calls': 0, 'generation_calls': 0}
    return result
