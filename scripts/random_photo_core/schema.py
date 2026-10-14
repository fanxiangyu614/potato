"""Random photo: schema."""
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


DATA_DIR = ROOT / "references" / "random-photo-data"


STYLE_PATH = ROOT / "references" / "style_library.json"


MEDIA = ("真人", "2D", "3D", "CG")


FAMILIES = {"fresh", "romantic", "elegant", "street", "stage", "athletic", "martial", "futuristic", "classical", "dark", "playful", "fantasy"}


ERAS = {"modern", "fantasy", "historical", "future"}


STANCES = {"stand", "walk", "sit", "kneel", "dynamic"}


SUPPORTS = {"standing_floor", "chair", "bench", "bed", "steps", "wall", "rail", "table", "pool_edge", "mirror"}


KINDS = {"original_design", "legacy_text", "web_visual_distilled", "hybrid", "mixed_adaptation"}


BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".mov", ".glb", ".gltf", ".obj", ".fbx", ".blend", ".safetensors"}


ASSET_KEYS = {"image_path", "image_file", "asset_path", "reference_image", "reference_images", "model_path", "video_path"}


REGIONS = {"subject", "background", "outfit_surface", "prop", "format", "light", "overall"}


BRANCHES = {"themed", "portrait"}


PORTRAIT_KINDS = {"general", "private"}


class PlanError(ValueError):
    pass


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise PlanError(f"Cannot read JSON {path}: {exc}") from exc


def require(condition, message):
    if not condition:
        raise PlanError(message)


def string_list(card, key, allowed=None, nonempty=False):
    value = card.get(key)
    require(isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value), f"{card.get('id')}: {key} must be a string list")
    require(not nonempty or bool(value), f"{card.get('id')}: {key} cannot be empty")
    require(len(value) == len(set(value)), f"{card.get('id')}: duplicate {key}")
    require(allowed is None or set(value) <= allowed, f"{card.get('id')}: unknown {key}")


def validate_card(card, role, expected_class=None, online=False):
    require(isinstance(card, dict), f"{role}: card must be an object")
    for key in ("id", "name", "prompt"):
        require(isinstance(card.get(key), str) and card[key].strip(), f"{role}: missing {key}")
    require(not ASSET_KEYS.intersection(card), f"{card['id']}: asset dependencies are forbidden")
    string_list(card, "media", set(MEDIA), True)
    provenance = card.get("provenance")
    require(isinstance(provenance, dict) and provenance.get("kind") in KINDS, f"{card['id']}: invalid provenance")
    string_list({"id": card["id"], "source_ids": provenance.get("source_ids")}, "source_ids", nonempty=True)
    if online:
        require(provenance["kind"] == "web_visual_distilled", f"{card['id']}: online card must have web_visual_distilled provenance")
    if role == "outfit":
        string_list(card, "styling_families", FAMILIES, True)
        require(type(card.get("class_id")) is int and 1 <= card["class_id"] <= 6, f"{card['id']}: invalid class_id")
        require(expected_class is None or card["class_id"] == expected_class, f"{card['id']}: class does not match filename")
        require(isinstance(card.get("subtype"), str) and card["subtype"].strip(), f"{card['id']}: missing subtype")
        string_list(card, "recognition_points", nonempty=True)
        require(3 <= len(card["recognition_points"]) <= 5, f"{card['id']}: need 3-5 recognition points")
        string_list(card, "era", ERAS, True)
        string_list(card, "mobility", STANCES, True)
        string_list(card, "props")
        if card["class_id"] == 1:
            for key in ("character", "work", "costume_version", "official_status"):
                require(isinstance(card.get(key), str) and card[key].strip(), f"{card['id']}: COS missing {key}")
    elif role == "location":
        string_list(card, "eras", ERAS, True)
        string_list(card, "supports", SUPPORTS, True)
        string_list(card, "props")
        classes = card.get("allowed_classes")
        require(isinstance(classes, list) and bool(classes) and all(type(x) is int and 1 <= x <= 6 for x in classes), f"{card['id']}: invalid allowed_classes")
        require(len(classes) == len(set(classes)), f"{card['id']}: duplicate allowed_classes")
    else:
        require(card.get("stance") in STANCES, f"{card['id']}: invalid stance")
        string_list(card, "requires_support", SUPPORTS, True)
        string_list(card, "requires_props")


def validate_shot(shot, label):
    require(isinstance(shot, dict), f"{label}: shot must be an object")
    nonempty_text(shot, ('moment', 'camera_position', 'framing', 'viewing_target'), label)


def normalize_aspect_ratio(value):
    if value is None:
        return None
    require(isinstance(value, str) and re.fullmatch(r'[1-9]\d*\s*[:：]\s*[1-9]\d*', value.strip()),
            'aspect_ratio must be positive integers W:H, for example 16:9, 9:16 or 1:1')
    return ':'.join(str(int(part.strip())) for part in value.strip().replace('：', ':').split(':'))


def object_rows(path, key=None):
    data = read_json(path)
    rows = data.get(key) if key is not None and isinstance(data, dict) else data
    require(isinstance(rows, list) and bool(rows), f"{path.name}: expected nonempty array {key or ''}")
    return rows


def unique_map(rows, key, label):
    require(all(isinstance(row, dict) and isinstance(row.get(key), str) and row[key].strip() for row in rows),
            f"{label}: missing {key}")
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), f"{label}: duplicate {key}")
    return result


def nonempty_text(obj, fields, label):
    require(all(isinstance(obj.get(field), str) and obj[field].strip() for field in fields),
            f"{label}: missing text in {', '.join(fields)}")


def era_text(context, label):
    if isinstance(context, str):
        require(bool(context.strip()), f'{label}: empty era_context')
        return context
    require(isinstance(context, dict), f'{label}: era_context must be text or structured context')
    fields = ('story_era', 'environment_character', 'shoot_context')
    nonempty_text(context, fields, label)
    return '；'.join(f'{name}：{context[field]}' for name, field in zip(('故事年代', '环境风貌', '取景情境'), fields))


def validate_people(people, label):
    require(isinstance(people, dict) and people.get("main") == 1, f"{label}: exactly one main person required")
    require(type(people.get("supporting")) is int and 0 <= people["supporting"] <= 2,
            f"{label}: supporting count must be 0-2")
    nonempty_text(people, ("relationship",), label)


def validate_prop_holders(states, people, label):
    holders = {'main', 'environment'} | {f'supporting_{i + 1}' for i in range(people['supporting'])}
    occupied = set()
    for state in states:
        require(state['holder'] in holders, f"{label}: prop holder has no corresponding person/place")
        if state['holder'] == 'environment' or state.get('hand') not in {'left', 'right', 'both'}:
            continue
        hands = ('left', 'right') if state['hand'] == 'both' else (state['hand'],)
        for hand in hands:
            slot = (state['holder'], hand)
            require(slot not in occupied, f"{label}: multiple props occupy the same hand")
            occupied.add(slot)


def validate_execution(outfit, location, pose, activity, medium=None):
    label = activity['id']
    require(outfit['class_id'] in location['allowed_classes'], f'{label}: location class mismatch')
    require(pose['stance'] in outfit['mobility'], f'{label}: pose mobility mismatch')
    require(bool(set(pose['requires_support']) & set(location['supports'])), f'{label}: unsupported stance')
    provided = set(location['props']) | set(outfit['props']) | {s['prop']['kind'] for s in activity['prop_states']}
    require(set(pose['requires_props']) <= provided, f'{label}: missing required props')
    if medium is not None:
        require(all(medium in card['media'] for card in (outfit, location, pose)), f'{label}: medium mismatch')
    validate_prop_holders(activity['prop_states'], activity['people'], label)


def validate_photography_overrides(recipe, label):
    overrides = recipe.get('photography_overrides', {})
    require(isinstance(overrides, dict) and set(overrides) <= {'light', 'material', 'grain', 'color', 'skin', 'hair'},
            f'{label}: invalid photography override fields')
    require(all(isinstance(value, str) and value.strip() for value in overrides.values()),
            f'{label}: photography overrides need visible effects')
