"""Random photo: cli."""
import argparse
import json
import sys
from pathlib import Path
from .schema import DATA_DIR, MEDIA, PlanError, REGIONS, STYLE_PATH
from .library import Library
from .sampling import sample
from .reporting import stats, validate


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Read-only random-photo planning. No network, image reads, or generation calls.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--style-library", type=Path, default=STYLE_PATH)
    commands = parser.add_subparsers(dest="command", required=True)
    sample_parser = commands.add_parser("sample", help="Output text plans, never generate images")
    sample_parser.add_argument("--count", type=int, default=1)
    sample_parser.add_argument("--seed", type=int)
    sample_parser.add_argument("--aspect-ratio", help="User-selected W:H; omitted means ask before image generation")
    sample_parser.add_argument("--signature", choices=("auto", "none"), default="auto")
    sample_parser.add_argument("--class-id", "--class-die", dest="class_id", type=int, choices=range(1, 7))
    sample_parser.add_argument("--source", choices=("local", "online", "random"), default="random")
    sample_parser.add_argument("--source-die", type=int, choices=range(1, 7))
    sample_parser.add_argument("--presentation", choices=("scene", "layout", "any"), default="scene")
    sample_parser.add_argument("--medium", choices=(*MEDIA, "random"), default=None)
    for field in ("style", "outfit", "location", "pose"):
        sample_parser.add_argument(f"--{field}-id")
    sample_parser.add_argument("--online-pool", type=Path)
    sample_parser.add_argument("--online-stage", choices=("initial", "resume"), default="resume",
                               help="initial conditions known locks on a supplied pool; resume preserves the earlier draw")
    sample_parser.add_argument("--branch", choices=("random", "themed", "portrait"), default="random")
    sample_parser.add_argument("--portrait-kind", choices=("random", "general", "private"), default="random")
    sample_parser.add_argument("--theme-id")
    sample_parser.add_argument("--activity-id")
    sample_parser.add_argument("--style-mode", choices=("medium", "catalog"), default="medium")
    sample_parser.add_argument("--style-mix", choices=("random", "single", "dual"), default="random")
    sample_parser.add_argument("--secondary-style-id")
    sample_parser.add_argument("--secondary-region", choices=sorted(REGIONS))
    commands.add_parser("validate", help="Validate structure and text compatibility, not media quality")
    commands.add_parser("stats")
    args = parser.parse_args(argv)
    try:
        library = Library(args.data_dir, args.style_library)
        if args.command == "sample":
            kwargs = {key: value for key, value in vars(args).items() if key not in {"command", "data_dir", "style_library"}}
            result = sample(library, **kwargs)
        else:
            result = validate(library) if args.command == "validate" else stats(library)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("valid", True) else 2
    except PlanError as exc:
        print(json.dumps({"error": str(exc), "media_verified": False}, ensure_ascii=False), file=sys.stderr)
        return 2
