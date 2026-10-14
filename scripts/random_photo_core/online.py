"""Random photo: online."""
from urllib.parse import urlparse
from .schema import BRANCHES, PORTRAIT_KINDS, era_text, nonempty_text, read_json, require, validate_card, validate_execution, validate_people, validate_shot


def load_online_pool(path):
    pool = read_json(path)
    require(isinstance(pool, list) and bool(pool), "Online pool must be a nonempty JSON array")
    ids = set()
    for item in pool:
        require(isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"].strip(), "Online candidate missing id")
        require(item["id"] not in ids, "Duplicate online candidate ID")
        ids.add(item["id"])
        for role in ("outfit", "location", "pose"):
            validate_card(item.get(role), role, online=True)
        p = item.get("provenance", {})
        require(isinstance(p, dict) and p.get("kind") == "web_visual_distilled" and p.get("image_seen") is True, f"{item['id']}: online image must have been actually viewed")
        urls = p.get("source_urls")
        require(isinstance(urls, list) and bool(urls) and all(isinstance(url, str) and urlparse(url).scheme in {"http", "https"} and urlparse(url).netloc for url in urls), f"{item['id']}: missing real source URLs")
        require(isinstance(p.get("observed_at"), str) and bool(p["observed_at"].strip()), f"{item['id']}: missing observed_at")
        roles = p.get("reference_roles")
        require(isinstance(roles, list) and {"outfit", "location", "pose"} <= set(roles), f"{item['id']}: missing reference responsibilities")
        if "observations" in p:
            require(isinstance(p["observations"], list) and bool(p["observations"]) and all(isinstance(x, str) and x.strip() for x in p["observations"]), f"{item['id']}: observations must be nonempty text observations")
        if "image_locator" in p:
            require(isinstance(p["image_locator"], str) and p["image_locator"].strip(), f"{item['id']}: image_locator must be text")
    return pool


def online_activity(item, data):
    # V2 entries carry observed activity semantics as well as the paired cards.
    theme = item.get("theme")
    require(isinstance(theme, dict) and theme.get("branch") in BRANCHES, f"{item['id']}: online pool needs an observed theme/branch")
    nonempty_text(theme, ("id", "name", "prompt"), item['id'])
    if theme['branch'] == 'portrait':
        require(theme.get('portrait_kind') in PORTRAIT_KINDS, f"{item['id']}: online portrait_kind missing")
    activity = item.get('activity')
    require(isinstance(activity, dict), f"{item['id']}: online activity missing")
    nonempty_text(activity, ('position', 'prompt'), item['id'])
    era_text(activity.get('era_context'), item['id'])
    validate_people(activity.get('people'), item['id'])
    states = activity.get('prop_states')
    require(isinstance(states, list), f"{item['id']}: online prop_states missing")
    enriched = []
    for state in states:
        require(isinstance(state, dict), f"{item['id']}: invalid prop state")
        prop = state.get('prop') or data.props.get(state.get('prop_id'))
        require(isinstance(prop, dict), f"{item['id']}: online prop needs definition")
        nonempty_text(prop, ('name', 'prompt', 'kind'), item['id'])
        require(type(state.get('count')) is int and state['count'] > 0, f"{item['id']}: prop count invalid")
        nonempty_text(state, ('holder', 'state'), item['id'])
        enriched.append(dict(state, prop=prop))
    activity = dict(activity, id=activity.get('id', item['id']), prop_states=enriched)
    if 'shot' in activity:
        validate_shot(activity['shot'], item['id'])
    for option in activity.get('shot_options', []):
        nonempty_text(option, ('id',), item['id'])
        validate_shot(option, item['id'])
    validate_execution(item['outfit'], item['location'], item['pose'], activity)
    return theme, activity
