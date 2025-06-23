import networkx as nx
import pickle
import os
import pandas as pd
import numpy as np
import csv
from itertools import combinations
from typing import List, Tuple

DATA_PATH = 'data/data_derivatives/obs_func.gpickle'
SAVE_PATH = 'data/data_derivatives/spike_correlations.csv'

def spike_mask(
    x: np.ndarray,
    win_baseline: int = 40,
    z_thresh: float = 1.3,
    refractory_s: int = 0,
    dtype=bool,
) -> np.ndarray:
    """
    Detect spike events in a 1 Hz calcium trace.

    Parameters
    ----------
    x : np.ndarray
        1-D trace, one sample = one second.
    win_baseline : int
        Window (seconds) for running baseline / noise estimate.
        60 s ≈ one minute works well for stable recordings.
    z_thresh : float
        A sample is a spike if       (x - baseline) / sigma  > z_thresh
    refractory_s : int
        Minimum number of seconds between successive spikes.
    dtype : numpy dtype
        Output mask type (np.uint8, bool, etc.).

    Returns
    -------
    mask : np.ndarray
        Binary mask, shape (len(x),), 1 where a spike is detected.
    """
    x = np.asarray(x, dtype=float)
    N = len(x)
    mask = np.zeros(N, dtype=dtype)

    if N == 0:
        return mask

    pad = win_baseline // 2
    padded = np.pad(x, (pad, pad), mode="edge")
    #    rolling median baseline
    baseline = np.empty(N)
    for i in range(N):
        w = padded[i : i + win_baseline]
        baseline[i] = np.median(w)

    sigma = np.empty(N)
    for i in range(N):
        w = padded[i : i + win_baseline]
        sigma[i] = np.median(np.abs(w - np.median(w))) / 0.6745 + 1e-9 

    z = (x - baseline) / sigma
    cand = np.where(z > z_thresh)[0]         

    if cand.size == 0:
        return mask

    keep = [cand[0]]
    for idx in cand[1:]:
        if idx - keep[-1] >= refractory_s:
            keep.append(idx)

    mask[np.array(keep)] = 1
    return mask

def write_spike_correlations(triplet: Tuple[str, str, str], obs_func: nx.DiGraph, writer: csv.writer):
    n1, n2, n3 = triplet
    # grab timeseries results for each neuron
    n1_data = obs_func.nodes[n1].get('timeseries', {})
    n2_data = obs_func.nodes[n2].get('timeseries', {})
    n3_data = obs_func.nodes[n3].get('timeseries', {})
    
    common_keys = set(n1_data.keys()) & set(n2_data.keys()) & set(n3_data.keys())
    
    if not common_keys:
        print(f"No common keys for {triplet}")
        return
    
    for key in common_keys:
        # get the timeseries data for each neuron  
        n1_spikes = spike_mask(n1_data[key])
        n2_spikes = spike_mask(n2_data[key])
        n3_spikes = spike_mask(n3_data[key])

        orderings = [(n1_spikes, n2_spikes, n3_spikes, '->n3'),
                     (n1_spikes, n3_spikes, n2_spikes, '->n2'),
                     (n2_spikes, n3_spikes, n1_spikes, '->n1')]
        
        for a, b, c, direction in orderings:
            and_corr = np.corrcoef(a & b, c)[0,1]
            or_corr = np.corrcoef(a | b, c)[0,1]
            and_notb_corr = np.corrcoef(a & ~b, c)[0,1]
            and_nota_corr = np.corrcoef(~a & b, c)[0,1]
            not_not_corr = np.corrcoef(~a & ~b, c)[0,1]
            a_corr = np.corrcoef(a, c)[0,1]
            b_corr = np.corrcoef(b, c)[0,1]
            writer.writerow([n1, n2, n3, direction, and_corr, or_corr, and_notb_corr, and_nota_corr, not_not_corr, a_corr, b_corr])
            print(f"n1: {n1}, n2: {n2}, n3: {n3}, direction: {direction}, and_corr: {and_corr}, or_corr: {or_corr}, and_notb_corr: {and_notb_corr}, and_nota_corr: {and_nota_corr}, not_not_corr: {not_not_corr}, a_corr: {a_corr}, b_corr: {b_corr}")
            

if __name__ == "__main__":
    with open(DATA_PATH, 'rb') as f:
        obs_func: nx.DiGraph = pickle.load(f)

    all_neurons = list(obs_func.nodes)
    all_triplets = combinations(all_neurons, 3)
    
    with open(SAVE_PATH, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['n1', 'n2', 'n3', 'direction', 'and_corr', 'or_corr', 'and_notb_corr', 'and_nota_corr', 'not_not_corr', 'a_corr', 'b_corr'])
        for triplet in all_triplets:
            write_spike_correlations(triplet, obs_func, writer)
            
        print(f"Saved to {SAVE_PATH}")





