"""Stable Python API for random-photo plans."""
from .schema import ROOT, DATA_DIR, STYLE_PATH, MEDIA, FAMILIES, ERAS, STANCES, SUPPORTS, KINDS, BINARY_SUFFIXES, ASSET_KEYS, REGIONS, BRANCHES, PORTRAIT_KINDS, PlanError, read_json, require, string_list, validate_card, validate_shot, normalize_aspect_ratio, object_rows, unique_map, nonempty_text, era_text, validate_people, validate_prop_holders, validate_execution, validate_photography_overrides
from .library import Library, PoolData, pools
from .online import load_online_pool, online_activity
from .brief import style_view, photography_scope, signature_plan, photography_targets, compile_prompt, finalize_brief
from .sampling import rng, context_fits, matching_style_links, style_candidates, style_context, select_styles, select_shot, resolve_locks, select_local_activity, sample
from .reporting import validate, stats
from .cli import main

__all__ = ['ROOT', 'DATA_DIR', 'STYLE_PATH', 'MEDIA', 'FAMILIES', 'ERAS', 'STANCES', 'SUPPORTS', 'KINDS', 'BINARY_SUFFIXES', 'ASSET_KEYS', 'REGIONS', 'BRANCHES', 'PORTRAIT_KINDS', 'PlanError', 'read_json', 'require', 'string_list', 'validate_card', 'validate_shot', 'normalize_aspect_ratio', 'object_rows', 'unique_map', 'nonempty_text', 'era_text', 'validate_people', 'validate_prop_holders', 'validate_execution', 'validate_photography_overrides', 'Library', 'PoolData', 'pools', 'load_online_pool', 'online_activity', 'style_view', 'photography_scope', 'signature_plan', 'photography_targets', 'compile_prompt', 'finalize_brief', 'rng', 'context_fits', 'matching_style_links', 'style_candidates', 'style_context', 'select_styles', 'select_shot', 'resolve_locks', 'select_local_activity', 'sample', 'validate', 'stats', 'main']
