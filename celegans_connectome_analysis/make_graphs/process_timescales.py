#!/usr/bin/env python3
import subprocess
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO

# DANDI set ID
DANDISET = "DANDI:000776/0.241009.1509"

BASE_DIR = Path("/storage2/projects/celegans")
BASE_DIR.mkdir(parents=True, exist_ok=True)


def list_nwb_assets():
    """
    Returns all asset paths under the dandiset that end in .nwb.
    """
    cmd = ["dandi", "ls", "-r", "-f", "json", DANDISET]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("ERROR listing assets:", proc.stderr, file=sys.stderr)
        sys.exit(1)

    try:
        assets = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON from dandi ls:", e, file=sys.stderr)
        sys.exit(1)

    return [a["path"] for a in assets if a["path"].endswith(".nwb")]

def download_asset(rel_path: str) -> bool:
    """
    Downloads the one .nwb asset at `rel_path` into BASE_DIR
    """
    dandiset_id = DANDISET.split(":")[1].split("/")[0]
    version = DANDISET.split("/")[1]
    url = f"dandi://DANDI/{dandiset_id}@{version}/{rel_path}"
    cmd = [
        "dandi",
        "download",
        url,
        "--output-dir",
        str(BASE_DIR),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[ERROR] downloading {rel_path}:", proc.stderr, file=sys.stderr)
        return False
    return True


def process_nwb(nwb_path: Path):
    print(f"  → opening {nwb_path.name}")

    with NWBHDF5IO(str(nwb_path), 'r') as io:
        nwb = io.read()

        mods = list(nwb.processing.keys())
        print(f"     modules:", mods)
        if 'CalciumActivity' not in mods:
            print("     [SKIP] no CalciumActivity module")
            return

        ints = list(nwb.processing['CalciumActivity'].data_interfaces.keys())
        print(f"     interfaces:", ints)

        chosen = None
        for key in ints:
            if 'ResponseSeries' in key:
                chosen = key
                break
        if chosen is None and 'SignalRawFluor' in ints:
            chosen = 'SignalRawFluor'
        if chosen is None:
            print("     [SKIP] no suitable interface found")
            return

        print(f"     using interface: {chosen}")
        rcs = nwb.processing['CalciumActivity'].data_interfaces[chosen]

        if not hasattr(rcs, 'rois'):
            print("     [SKIP] interface has no .rois")
            return

        try:
            idxs   = rcs.rois.data[:]                   
            labels = rcs.rois.table['ID_labels'][:] 
            names  = labels[idxs]             
            data   = rcs.data[:]            
            times  = rcs.timestamps[:]          
        except Exception as e:
            print(f"     [ERROR] reading datasets: {e}")
            return

    # filter out empty‐string labels
    keep  = [i for i, nm in enumerate(names) if nm != ""]
    names = names[keep]
    data  = data[:, keep]

    output_dir = Path("data/observed_func")
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data, columns=names)
    df.insert(0, 'time', times)
    out_csv = output_dir / f"{nwb_path.stem}.csv"
    df.to_csv(out_csv, index=False)
    print(f"     ✓ wrote {out_csv.name} to {output_dir}")

def main():
    assets = list_nwb_assets()
    if not assets:
        print("No .nwb files found.", file=sys.stderr)
        sys.exit(1)

    for rel in assets:
        print(f"[Asset] {rel}")

        if not download_asset(rel):
            continue

        basename = Path(rel).name
        candidates = list(BASE_DIR.glob(f"{basename}*"))
        local_nwb = next((p for p in candidates if p.suffix == ".nwb"), None)
        if local_nwb is None:
            print(f"[WARN] no completed .nwb for {basename}, saw:", candidates, file=sys.stderr)
            continue

        try:
            process_nwb(local_nwb)
        except Exception as e:
            print(f"[ERROR] processing {basename}: {e}", file=sys.stderr)
        else:
            local_nwb.unlink()
            print(f"    → deleted {basename}\n")


if __name__ == "__main__":
    main()
