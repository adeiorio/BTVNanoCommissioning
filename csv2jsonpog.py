#!/usr/bin/env python3
"""
Convert a CSV of b tag scale factors into a correctionlib JSON (jsonpog) file
with per bin values.

CSV columns expected:
  wp,type,syst,flav,etaMin,etaMax,ptMin,ptMax,discrMin,discrMax,formula

Notes:
  - The script nests by systematic, working_point, flavor, |eta|, pt to match jsonpog fixedWP SF files.
  - Discriminant is ignored, since the CSV has a single [0, 1] bin.
  - Output uses schema_version 2.
  - abseta binning uses flow="error" by default.
  - pt binning flow can be numeric (default is the value of the last pt bin), or the strings "error" or "clamp".

Example:
  python csv2jsonpog.py input.csv out.json \
    --tagger UParTAK4 --era 2024_Summer24 --corr-name UParTAK4_kinfit \
    --version 1 --eta-flow error --pt-flow clamp \
    --meta-file metadata/taggers_Summer24.json --meta-key btagUParTAK4B
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any, Union
from math import isclose


@dataclass(frozen=True)
class Row:
    wp: str
    syst: str
    flavor: int
    etaMin: float
    etaMax: float
    ptMin: float
    ptMax: float
    value: float  # parsed from "formula" column


def parse_csv(path: Path) -> List[Row]:
    rows: List[Row] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        required = [
            "wp",
            "type",
            "syst",
            "flav",
            "etaMin",
            "etaMax",
            "ptMin",
            "ptMax",
            "discrMin",
            "discrMax",
            "formula",
        ]
        missing = [k for k in required if k not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required CSV columns: {missing}")

        for r in reader:
            try:
                value_str = r["formula"].strip().strip('"').strip("'")
                rows.append(
                    Row(
                        wp=r["wp"].strip(),
                        syst=r["syst"].strip(),
                        flavor=int(float(r["flav"])),  # for b-jets expect "5.0"
                        etaMin=float(r["etaMin"]),
                        etaMax=float(r["etaMax"]),
                        ptMin=float(r["ptMin"]),
                        ptMax=float(r["ptMax"]),
                        value=float(value_str),
                    )
                )
            except Exception as e:
                raise RuntimeError(f"Failed to parse row: {r}") from e
    if not rows:
        raise ValueError("No rows parsed from CSV")
    return rows


def unique_sorted_edges(intervals: List[Tuple[float, float]]) -> List[float]:
    edges = set()
    for lo, hi in intervals:
        edges.add(lo)
        edges.add(hi)
    out = sorted(edges)
    return out


def _approx_eq(a: float, b: float, rel=1e-9, abs_=1e-9) -> bool:
    return isclose(a, b, rel_tol=rel, abs_tol=abs_)


def fill_20_30_from_30(
    rows: List[Row],
    nominal_syst: str = "central",
    factor: float = 2.0,
) -> List[Row]:
    """
    For each (wp, flavor, |eta| bin) group:
      if there is a pt bin starting at 30, copy its central value to a new 20–30 bin
      and for every non nominal syst set value = central_30 + factor * (syst_30 - central_30).
      Only add if 20–30 is missing. Leaves existing 20–30 rows untouched.
    """
    # Index rows by a coarse key that does not include pt
    key_eta = lambda r: (r.wp, r.flavor, r.etaMin, r.etaMax)

    groups: Dict[Tuple[str, int, float, float], List[Row]] = defaultdict(list)
    for r in rows:
        groups[key_eta(r)].append(r)

    new_rows: List[Row] = list(rows)  # start with original
    added = 0

    for gkey, group in groups.items():
        # Map (ptMin, ptMax, syst) -> value
        by_bin_syst: Dict[Tuple[float, float, str], float] = {}
        for r in group:
            by_bin_syst[(r.ptMin, r.ptMax, r.syst)] = r.value

        # Find the 30 bin bounds inside this group
        thirty_bins = sorted({(r.ptMin, r.ptMax) for r in group if _approx_eq(r.ptMin, 30.0)})
        if not thirty_bins:
            continue  # nothing to clone from

        # Choose the first 30 bin in sorted order
        pt30_lo, pt30_hi = thirty_bins[0]

        # Central value at 30
        if (pt30_lo, pt30_hi, nominal_syst) not in by_bin_syst:
            continue  # cannot construct deviations without central reference

        v30_central = by_bin_syst[(pt30_lo, pt30_hi, nominal_syst)]

        # Check if 20–30 already exists for this group
        has_20_30 = any(_approx_eq(r.ptMin, 20.0) and _approx_eq(r.ptMax, 30.0) for r in group)
        if has_20_30:
            continue

        # Add nominal 20–30
        wp, flav, etaMin, etaMax = gkey
        new_rows.append(Row(
            wp=wp, syst=nominal_syst, flavor=flav,
            etaMin=etaMin, etaMax=etaMax,
            ptMin=20.0, ptMax=30.0,
            value=v30_central
        ))
        added += 1

        # Add all non nominal systematics, scaled
        syst_names = sorted({r.syst for r in group if r.syst != nominal_syst})
        for sname in syst_names:
            key30 = (pt30_lo, pt30_hi, sname)
            if key30 not in by_bin_syst:
                # if a particular syst does not have a 30 bin, skip it
                continue
            v30_syst = by_bin_syst[key30]
            delta = v30_syst - v30_central
            v20_30_syst = v30_central + factor * delta

            new_rows.append(Row(
                wp=wp, syst=sname, flavor=flav,
                etaMin=etaMin, etaMax=etaMax,
                ptMin=20.0, ptMax=30.0,
                value=v20_30_syst
            ))
            added += 1

    if added:
        print(f"Info, synthesized {added} rows for 20–30 GeV from the 30 GeV bin.")
    return new_rows


def build_pt_binning(rows: List[Row], pt_flow_mode: str, pt_flow_value: float) -> Dict[str, Any]:
    intervals = sorted({(r.ptMin, r.ptMax) for r in rows})
    edges = unique_sorted_edges(intervals)

    vmap: Dict[Tuple[float, float], float] = {}
    for r in rows:
        key = (r.ptMin, r.ptMax)
        if key in vmap and vmap[key] != r.value:
            raise ValueError(f"Duplicate pt bin with different values: {key}")
        vmap[key] = r.value

    content: List[float] = []
    for i in range(len(edges) - 1):
        key = (edges[i], edges[i + 1])
        if key not in vmap:
            raise ValueError(f"Missing value for pt bin {key}")
        content.append(vmap[key])

    # Decide pt flow
    flow: Union[str, float]
    if pt_flow_mode == "last":
        flow = content[-1]
    elif pt_flow_mode == "value":
        flow = float(pt_flow_value)
    elif pt_flow_mode in ("error", "clamp"):
        flow = pt_flow_mode
    else:
        raise ValueError(f"Unknown pt_flow_mode {pt_flow_mode}")

    return {
        "nodetype": "binning",
        "input": "pt",
        "edges": edges,
        "content": content,
        "flow": flow,
    }


def build_eta_binning(rows: List[Row], eta_flow: str, pt_flow_mode: str, pt_flow_value: float) -> Dict[str, Any]:
    eta_intervals = sorted({(r.etaMin, r.etaMax) for r in rows})
    eta_edges = unique_sorted_edges(eta_intervals)

    pt_nodes: List[Dict[str, Any]] = []
    for i in range(len(eta_edges) - 1):
        lo, hi = eta_edges[i], eta_edges[i + 1]
        sub = [r for r in rows if r.etaMin == lo and r.etaMax == hi]
        if not sub:
            raise ValueError(f"No rows found for eta bin {(lo, hi)}")
        pt_nodes.append(build_pt_binning(sub, pt_flow_mode, pt_flow_value))

    return {
        "nodetype": "binning",
        "input": "abseta",
        "edges": eta_edges,
        "content": pt_nodes,
        "flow": eta_flow,
    }


def build_sf_correction(
    rows: List[Row],
    corr_name: str,
    description: str,
    version: int,
    eta_flow: str = "error",
    pt_flow_mode: str = "last",
    pt_flow_value: float = 1.0,
) -> Dict[str, Any]:
    grouped: Dict[Tuple[str, str, int], List[Row]] = defaultdict(list)
    for r in rows:
        grouped[(r.wp, r.syst, r.flavor)].append(r)

    wps = sorted(
        {r.wp for r in rows},
        key=lambda w: ["L", "M", "T", "XT"].index(w) if w in {"L","M","T","XT"} else w,
    )
    systs = sorted({r.syst for r in rows})
    flavors = sorted({r.flavor for r in rows})

    def wp_node_for_syst(syst: str) -> Dict[str, Any]:
        wp_content = []
        for wp in wps:
            flav_content = []
            for flav in flavors:
                key = (wp, syst, flav)
                if key not in grouped:
                    continue
                eta_node = build_eta_binning(grouped[key], eta_flow, pt_flow_mode, pt_flow_value)
                flav_content.append({"key": flav, "value": eta_node})
            if not flav_content:
                continue
            wp_content.append(
                {
                    "key": wp,
                    "value": {
                        "nodetype": "category",
                        "input": "working_point",
                        # This inner node actually needs "flavor", so wrap flavor here
                        "content": [
                            {
                                "key": wp,
                                "value": {
                                    "nodetype": "category",
                                    "input": "flavor",
                                    "content": flav_content,
                                },
                            }
                        ],
                    },
                }
            )
        # The above added an extra "working_point" level with a duplicate key, which is not ideal.
        # Instead, construct correctly: category over working_point, each contains category over flavor.
        # Rebuild correctly:
        proper_wp_content = []
        for wp in wps:
            flav_content = []
            for flav in flavors:
                key = (wp, syst, flav)
                if key not in grouped:
                    continue
                eta_node = build_eta_binning(grouped[key], eta_flow, pt_flow_mode, pt_flow_value)
                flav_content.append({"key": flav, "value": eta_node})
            if not flav_content:
                continue
            proper_wp_content.append(
                {
                    "key": wp,
                    "value": {
                        "nodetype": "category",
                        "input": "flavor",
                        "content": flav_content,
                    },
                }
            )
        return {
            "nodetype": "category",
            "input": "working_point",
            "content": proper_wp_content,
        }

    syst_content = []
    for syst in systs:
        node = wp_node_for_syst(syst)
        if node["content"]:
            syst_content.append({"key": syst, "value": node})

    correction = {
        "name": corr_name,
        "description": description,
        "version": version,
        "inputs": [
            {"name": "systematic", "type": "string"},
            {"name": "working_point", "type": "string", "description": "L/M/T/XT"},
            {
                "name": "flavor",
                "type": "int",
                "description": "hadron flavor definition: 5=b, 4=c, 0=udsg",
            },
            {"name": "abseta", "type": "real"},
            {"name": "pt", "type": "real"},
        ],
        "output": {"name": "weight", "type": "real"},
        "data": {
            "nodetype": "category",
            "input": "systematic",
            "content": syst_content,
        },
    }
    return correction


def build_wp_values_correction(
    tagger: str, desc: str, version: int, values: Dict[str, float]
) -> Dict[str, Any]:
    content = [{"key": k, "value": float(v)} for k, v in values.items()]
    order = ["L", "M", "T", "XT", "XXT"]
    content.sort(key=lambda kv: order.index(kv["key"]) if kv["key"] in order else kv["key"])
    return {
        "name": f"{tagger}_wp_values",
        "description": desc,
        "version": version,
        "inputs": [
            {
                "name": "working_point",
                "type": "string",
                "description": "L/M/T/XT",
            }
        ],
        "output": {
            "name": "wp",
            "type": "real",
            "description": "Working point value of the b jet discriminator",
        },
        "data": {
            "nodetype": "category",
            "input": "working_point",
            "content": content,
        },
    }


def load_wp_values_from_metadata(meta_path: Path, tagger_key: str) -> Dict[str, float]:
    """
    Read thresholds from a metadata JSON like metadata/taggers_Summer24.json

    Expected format:
      {
        "btagUParTAK4B": ["UnifiedParticleTransformer Discriminator", "btagUParTAK4B",
                          0.0246, 0.1272, 0.4648, 0.6298, 0.9739, 1.01]
      }
    The last number is ignored here.
    """
    with meta_path.open() as f:
        payload = json.load(f)
    if tagger_key not in payload:
        raise KeyError(f"Key {tagger_key} not found in {meta_path}")
    arr = payload[tagger_key]
    if not isinstance(arr, list) or len(arr) < 7:
        raise ValueError(
            f"Value for {tagger_key} must be a list with at least 7 elements, got {arr}"
        )
    L, M, T, XT = map(float, arr[2:6])
    return {"L": L, "M": M, "T": T, "XT": XT}


def main():
    ap = argparse.ArgumentParser(
        description="Convert SF CSV to jsonpog correctionlib file with bin based values."
    )
    ap.add_argument("csv", type=Path, help="Input CSV path")
    ap.add_argument("out", type=Path, help="Output JSON path")
    ap.add_argument(
        "--tagger",
        default="UParTAK4",
        help="Tagger name to use in descriptions and WP correction",
    )
    ap.add_argument(
        "--era",
        default="2024_Summer24",
        help="Era label for descriptions, for example 2024_Summer24",
    )
    ap.add_argument(
        "--corr-name",
        default="UParTAK4_Wc",
        help="Name of the scale factor correction to create",
    )
    ap.add_argument("--version", type=int, default=1, help="Correction version")
    ap.add_argument(
        "--eta-flow",
        choices=["error", "clamp"],
        default="error",
        help="Out of range handling for |eta| binning",
    )
    ap.add_argument(
        "--pt-flow",
        choices=["last", "error", "clamp", "value"],
        default="last",
        help="Out of range handling for pt binning. 'last' uses the last bin value. 'value' uses --pt-flow-value.",
    )
    ap.add_argument(
        "--pt-flow-value",
        type=float,
        default=1.0,
        help="Numeric flow value for pt when --pt-flow value is chosen",
    )
    ap.add_argument(
        "--meta-file",
        type=Path,
        default=Path("metadata/taggers_Summer24.json"),
        help="Metadata JSON with WP thresholds",
    )
    ap.add_argument(
        "--meta-key",
        default="btagUParTAK4B",
        help="Key inside metadata JSON to load thresholds from",
    )
    # Backward compatibility with older --flow flag, maps to --eta-flow
    ap.add_argument(
        "--flow",
        choices=["clamp", "error"],
        help="Deprecated, use --eta-flow instead",
    )
    ap.add_argument(
        "--fill-20-30-from-30",
        action="store_true",
        help="If the 20–30 GeV bin is missing, synthesize it from the 30 GeV bin and scale syst deviations.",
    )
    ap.add_argument(
        "--unc-factor",
        type=float,
        default=2.0,
        help="Factor to scale syst deviations for the synthesized 20–30 GeV bin.",
    )
    ap.add_argument(
        "--nominal-syst",
        default="central",
        help="Name of the nominal systematic in the CSV syst column, for example central or nominal.",
    )
    args = ap.parse_args()
    if args.flow:
        args.eta_flow = args.flow

    rows = parse_csv(args.csv)

    if args.fill_20_30_from_30:
        rows = fill_20_30_from_30(
            rows,
            nominal_syst=args.nominal_syst,
            factor=args.unc_factor,
        )

    corr_desc = (
        f"{args.corr_name} scale factors for {args.era}. "
        f"Provided per bin in |eta| and pt, no discriminant dimension."
    )
    sf_correction = build_sf_correction(
        rows=rows,
        corr_name=args.corr_name,
        description=corr_desc,
        version=args.version,
        eta_flow=args.eta_flow,
        pt_flow_mode=args.pt_flow,
        pt_flow_value=args.pt_flow_value,
    )

    top = {
        "schema_version": 2,
        "description": f"Corrections for {args.tagger} in {args.era}.",
        "corrections": [],
    }

    # Load WP values from metadata file if present
    if args.meta_file.exists():
        try:
            wp_vals = load_wp_values_from_metadata(args.meta_file, args.meta_key)
            wp_desc = (
                f"Working point values of the c jet discrimination for {args.tagger} in {args.era}. "
                f"The L M T XT working points correspond to 10, 1, 0.1, 0.05 percent light jet misidentification rates."
            )
            top["corrections"].append(
                build_wp_values_correction(
                    tagger=args.tagger, desc=wp_desc, version=args.version, values=wp_vals
                )
            )
        except Exception as e:
            print(f"Warning, failed to load WP thresholds from {args.meta_file}: {e}")

    top["corrections"].append(sf_correction)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        json.dump(top, f, indent=2, sort_keys=False)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
