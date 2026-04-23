#!/usr/bin/env python3
"""
Copy a captured config tree to a new location and replace site-identity
values with stable placeholders, so the copy can be committed to a
fixtures repo and cleanly diffed against genconfig test-harness output.

Replaces these values:
  - Every password from <site-config>/passwords.yml         -> <PASSWORD:key>
  - Site knobs from <site-config>/defaults.yml or globals.yml
    (the SITE_VALUE_KEYS list below)                        -> <SITE:suffix>
  - Host identity pulled from --facts at known paths
    (FACT_KEYS below)                                       -> <SITE:suffix>

Both operator runs (over a real snapshot) and conftest runs (over a
fresh test render) invoke this script. Same contract, matching
placeholders, so `diff -r` cancels credential and identity lines.

Inputs are read-only. The destination directory must not exist.

Usage:
    anonymize-snapshot.py \\
        --site-config /path/to/site-config \\
        --facts /path/to/host-facts.json \\
        SRC_DIR DST_DIR
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import yaml


# --- Contract ---------------------------------------------------------------
# Extend these as new noise categories emerge. Both sides of any diff must
# use the same list for placeholders to cancel.

# Keys to read from defaults.yml / globals.yml.
# key in yaml  ->  suffix used in <SITE:suffix> placeholder
SITE_VALUE_KEYS = {
    "kolla_internal_vip_address": "internal_vip",
    "kolla_external_vip_address": "external_vip",
    "openstack_region_name":      "region",
}

# Dotted paths to read from ansible_facts.
FACT_KEYS = {
    "ansible_default_ipv4.address": "host_ip",
    "ansible_hostname":             "hostname",
    "ansible_fqdn":                 "fqdn",
}


def flatten_passwords(obj, prefix=""):
    """Flatten nested password YAML into {dotted_key: string_value}."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            out.update(flatten_passwords(v, key))
    elif isinstance(obj, str) and obj.strip():
        out[prefix] = obj
    return out


def load_facts(path):
    """Load a facts file. Accepts JSON (ansible -m setup --tree output) or
    YAML (our test host_vars). Auto-unwraps a top-level 'ansible_facts' key.
    """
    text = path.read_text()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = yaml.safe_load(text) or {}
    if isinstance(data, dict) and "ansible_facts" in data:
        data = data["ansible_facts"]
    return data or {}


def get_dotted(obj, path):
    """Walk a dotted path; return None if any segment is missing."""
    cur = obj
    for seg in path.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    return cur


def build_substitutions(site_config, facts_path):
    """Return {value: placeholder} dict. `value` is the literal string to
    find in file contents; `placeholder` is what it gets replaced with."""
    subs = {}

    pw_file = site_config / "passwords.yml"
    if pw_file.exists():
        for key, val in flatten_passwords(yaml.safe_load(pw_file.read_text()) or {}).items():
            subs.setdefault(val, f"<PASSWORD:{key}>")

    for fname in ("defaults.yml", "globals.yml"):
        path = site_config / fname
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text()) or {}
        for key, suffix in SITE_VALUE_KEYS.items():
            v = data.get(key)
            if isinstance(v, str) and v.strip():
                subs.setdefault(v, f"<SITE:{suffix}>")

    facts = load_facts(facts_path)
    for dotted, suffix in FACT_KEYS.items():
        v = get_dotted(facts, dotted)
        if isinstance(v, str) and v.strip():
            subs.setdefault(v, f"<SITE:{suffix}>")

    return subs


def copy_and_scrub(src, dst, subs):
    # Copy first (shutil.copytree requires dst to not exist — our caller
    # validated this).
    shutil.copytree(src, dst)

    # Longest value first so short values can't partial-match inside longer
    # ones (e.g., a 4-char password inside a 200-char SSH key).
    items = sorted(subs.items(), key=lambda kv: -len(kv[0]))

    scanned = changed = 0
    for root, _, files in os.walk(dst):
        for f in files:
            path = os.path.join(root, f)
            scanned += 1
            try:
                with open(path, encoding="utf-8") as fp:
                    content = fp.read()
            except (UnicodeDecodeError, OSError):
                continue  # binary files, symlinks, etc.
            new = content
            for val, placeholder in items:
                if val in new:
                    new = new.replace(val, placeholder)
            if new != content:
                with open(path, "w", encoding="utf-8") as fp:
                    fp.write(new)
                changed += 1
    return scanned, changed


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--site-config", required=True, type=Path,
                    help="directory containing defaults.yml/globals.yml/passwords.yml")
    ap.add_argument("--facts", required=True, type=Path,
                    help="ansible facts for the captured host (JSON from "
                         "`ansible -m setup --tree` or YAML host_vars)")
    ap.add_argument("src", type=Path, help="source tree (read-only)")
    ap.add_argument("dst", type=Path, help="output tree (must not exist)")
    args = ap.parse_args()

    if not args.site_config.is_dir():
        sys.exit(f"--site-config directory not found: {args.site_config}")
    if not args.facts.exists():
        sys.exit(f"--facts file not found: {args.facts}")
    if not args.src.is_dir():
        sys.exit(f"src directory not found: {args.src}")
    if args.dst.exists():
        sys.exit(f"dst already exists (refusing to overwrite): {args.dst}")

    subs = build_substitutions(args.site_config, args.facts)
    if not subs:
        sys.exit("no substitutions found; nothing to anonymize")

    scanned, changed = copy_and_scrub(args.src, args.dst, subs)
    print(f"anonymize-snapshot: scanned {scanned} files, rewrote {changed} "
          f"with {len(subs)} substitutions -> {args.dst}")


if __name__ == "__main__":
    main()
