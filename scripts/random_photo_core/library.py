"""Random photo: library."""
from pathlib import Path
from .schema import BRANCHES, DATA_DIR, FAMILIES, MEDIA, PORTRAIT_KINDS, REGIONS, STYLE_PATH, era_text, nonempty_text, object_rows, read_json, require, string_list, unique_map, validate_card, validate_people, validate_photography_overrides, validate_prop_holders, validate_shot


class Library:
    def __init__(self, data_dir=DATA_DIR, style_path=STYLE_PATH):
        self.data_dir = Path(data_dir)
        data = read_json(style_path)
        self.styles = data.get("styles") if isinstance(data, dict) else None
        require(isinstance(self.styles, list) and len(self.styles) == 620, "Style library must contain exactly 620 entries")
        ids = [style.get("style_id") for style in self.styles if isinstance(style, dict)]
        require(len(ids) == 620 and all(isinstance(x, str) and x for x in ids) and len(set(ids)) == 620, "620 style IDs must be nonempty and unique")
        self._outfits = {}
        self._shared = None
        self._pool_data = None
        self.style_path = Path(style_path)

    def cards(self, name, role, class_id=None):
        cards = read_json(self.data_dir / name)
        require(isinstance(cards, list) and bool(cards), f"{name}: expected nonempty JSON array")
        for card in cards:
            validate_card(card, role, class_id)
        require(len({card['id'] for card in cards}) == len(cards), f"{name}: duplicate card IDs")
        return cards

    def outfits(self, class_id):
        if class_id not in self._outfits:
            paths = sorted(self.data_dir.glob(f"outfits-{class_id}-*.json"))
            require(len(paths) == 1, f"Class {class_id}: expected one outfit file")
            self._outfits[class_id] = self.cards(paths[0].name, "outfit", class_id)
        return self._outfits[class_id]

    def shared(self):
        if self._shared is None:
            self._shared = (self.cards("locations.json", "location"), self.cards("poses.json", "pose"))
        return self._shared

    def find_outfit_class(self, outfit_id):
        found = [class_id for class_id in range(1, 7)
                 if list(self.data_dir.glob(f"outfits-{class_id}-*.json"))
                 and any(card["id"] == outfit_id for card in self.outfits(class_id))]
        require(len(found) <= 1, f"Ambiguous outfit lock: {outfit_id}")
        return found[0] if found else None


class PoolData:
    """Preconnected positive indexes. Sampling never runs physical/semantic graph matching."""
    def __init__(self, library):
        self.library = library
        index = read_json(library.style_path.with_name("style-media-index.json"))
        self.profiles = unique_map(index['styles'], "style_id", "style profiles")
        self.excluded_styles = {row['style_id']: row for row in index.get('excluded_styles', [])}
        require(len(self.excluded_styles) == len(index.get('excluded_styles', [])), "Duplicate excluded style ID")
        require(not set(self.profiles) & set(self.excluded_styles), "Style cannot be both eligible and excluded")
        require(set(self.profiles) | set(self.excluded_styles) == {s["style_id"] for s in library.styles},
                "Eligible and excluded styles must account for the complete source catalog")
        self.original_styles = {s["style_id"]: s for s in library.styles}
        self.primary_pools = {medium: [] for medium in MEDIA}
        self.secondary_recipes = {}
        for style_id, profile in self.profiles.items():
            string_list(profile, "styling_families", FAMILIES, True)
            nonempty_text(profile, ("core_features",), style_id)
            primary = profile.get("primary_recipes")
            require(isinstance(primary, dict) and bool(primary) and set(primary) <= set(MEDIA), f"{style_id}: primary recipes missing")
            require(profile.get("full_catalog_medium") in primary, f"{style_id}: full catalog medium has no recipe")
            for medium, recipe in primary.items():
                require(isinstance(recipe, dict) and recipe.get("region") in REGIONS, f"{style_id}/{medium}: invalid region")
                nonempty_text(recipe, ("prompt",), f"{style_id}/{medium}")
                validate_photography_overrides(recipe, f'{style_id}/{medium}')
                self.primary_pools[medium].append(style_id)
            secondaries = profile.get("secondary_recipes")
            require(isinstance(secondaries, list), f"{style_id}: secondary recipes must be array")
            for recipe in secondaries:
                require(isinstance(recipe, dict) and recipe.get("region") in REGIONS and recipe.get("medium") in MEDIA,
                        f"{style_id}: invalid secondary region/medium")
                nonempty_text(recipe, ("id", "prompt"), style_id)
                string_list(recipe, "host_media", set(MEDIA), True)
                require(recipe["id"] not in self.secondary_recipes, f"Duplicate secondary recipe {recipe['id']}")
                validate_photography_overrides(recipe, recipe["id"])
                self.secondary_recipes[recipe["id"]] = (style_id, recipe)
        require(all(self.primary_pools.values()), "Every medium must have a nonempty primary pool")
        self.style_combinations = unique_map(object_rows(library.style_path.with_name("style-combinations.json"), "combinations"),
                                             "id", "style combinations")
        self.style_links = {}
        for combination in self.style_combinations.values():
            string_list(combination, "styling_families", FAMILIES, True)
            main = combination.get("primary_style_id")
            medium = combination.get("subject_medium")
            secondary = combination.get("secondary_style_id")
            require(main in self.profiles and medium in self.profiles[main]["primary_recipes"], f"{combination['id']}: invalid main recipe")
            require(secondary in self.profiles and secondary != main, f"{combination['id']}: two different style IDs required")
            require(set(combination["styling_families"]) <= set(self.profiles[main]["styling_families"]) & set(self.profiles[secondary]["styling_families"]),
                    f"{combination['id']}: incompatible styling families")
            pair = self.secondary_recipes.get(combination.get("secondary_recipe_id"))
            require(pair is not None and pair[0] == secondary and medium in pair[1]["host_media"],
                    f"{combination['id']}: secondary recipe/host mismatch")
            nonempty_text(combination, ("integration_prompt",), combination["id"])
            self.style_links.setdefault((main, medium), []).append(combination)
        # A valid single style need not have a semantically valid secondary.
        # style_candidates filters the dual branch by actual registered links.
        self.themes = unique_map(object_rows(library.data_dir / "activity-themes.json"), "id", "themes")
        for theme in self.themes.values():
            nonempty_text(theme, ("name", "prompt"), theme["id"])
            require(theme.get("branch") in BRANCHES, f"{theme['id']}: invalid branch")
            if theme["branch"] == "portrait":
                require(theme.get("portrait_kind") in PORTRAIT_KINDS, f"{theme['id']}: invalid portrait kind")
            require(isinstance(theme.get("classes"), list) and bool(theme["classes"])
                    and all(type(c) is int and 1 <= c <= 6 for c in theme["classes"]), f"{theme['id']}: invalid classes")
        self.props = unique_map(object_rows(library.data_dir / "props.json"), "id", "props")
        for prop in self.props.values():
            nonempty_text(prop, ("name", "prompt", "kind"), prop["id"])
        self.activities = unique_map(object_rows(library.data_dir / "activity-combinations.json"), "id", "activities")
        shot_path = library.data_dir / 'shot-options.json'
        shot_definitions = unique_map(object_rows(shot_path), 'id', 'shot definitions') if shot_path.exists() else {}
        for definition in shot_definitions.values():
            validate_shot(definition.get('shot'), definition['id'])
        self.activity_links = {}
        for activity in self.activities.values():
            if 'shot_option_refs' in activity:
                require('shot_options' not in activity, f"{activity['id']}: use inline shots or shot IDs, not both")
                refs = activity.pop('shot_option_refs')
                require(isinstance(refs, list) and bool(refs), f"{activity['id']}: empty shot references")
                for ref in refs:
                    require(isinstance(ref, dict) and isinstance(ref.get('definition'), str)
                            and ref['definition'] in shot_definitions, f"{activity['id']}: unknown shot definition")
                    nonempty_text(ref, ('id',), activity['id'])
                activity['shot_options'] = [dict(shot_definitions[ref['definition']]['shot'], id=ref['id']) for ref in refs]
            nonempty_text(activity, ("position", "prompt"), activity["id"])
            era_text(activity.get('era_context'), activity['id'])
            theme = self.themes.get(activity.get("theme_id"))
            require(theme is not None and activity.get("class_id") in theme["classes"], f"{activity['id']}: invalid theme/class")
            if 'shot' in activity:
                validate_shot(activity['shot'], activity['id'])
            if 'shot_options' in activity:
                require(bool(activity['shot_options']), f"{activity['id']}: empty shot_options")
                require(isinstance(activity['shot_options'], list), f"{activity['id']}: shot_options must be an array")
                require(len({o.get('id') for o in activity['shot_options']}) == len(activity['shot_options']), f"{activity['id']}: duplicate shot option IDs")
                for option in activity['shot_options']:
                    nonempty_text(option, ('id',), activity['id'])
                    validate_shot(option, activity['id'])
            string_list(activity, "outfit_ids", nonempty=True)
            string_list(activity, "media", set(MEDIA), True)
            validate_people(activity.get("people"), activity["id"])
            self.validate_prop_states(activity.get("prop_states"), activity["id"])
            validate_prop_holders(activity['prop_states'], activity['people'], activity['id'])
            for outfit_id in activity["outfit_ids"]:
                for medium in activity["media"]:
                    key = (activity["class_id"], outfit_id, medium, theme["branch"], theme.get("portrait_kind"))
                    self.activity_links.setdefault(key, []).append(activity)

    def validate_prop_states(self, states, label):
        require(isinstance(states, list), f"{label}: prop_states must be array")
        for state in states:
            require(isinstance(state, dict) and state.get("prop_id") in self.props, f"{label}: unknown prop")
            require(type(state.get("count")) is int and state["count"] > 0, f"{label}: invalid prop count")
            nonempty_text(state, ("state", "holder"), label)


def pools(library):
    if library._pool_data is None:
        library._pool_data = PoolData(library)
    return library._pool_data
