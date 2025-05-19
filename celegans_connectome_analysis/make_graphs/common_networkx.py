# Builds networkx graph given existing checked_graph.gpickle and observational
# data from data/observed_func/*.csv (run process_timescales.py)
# run python celegans_connectome_analysis/make_graphs/common_networkx.py

# Requirements: data/data_derivatives/checked_graph.gpickle, data/observed_func/*.csv
# Output: data/data_derivatives/stx_fx_time.gpickle containing the graph with observational data

import networkx as nx
import numpy as np
import csv
import pandas as pd
from pathlib import Path
import pickle 

with open('data/data_derivatives/checked_graph.gpickle', 'rb') as f:
    G = pickle.load(f)
csv_dir = Path("data/observed_func")

for csv_path in csv_dir.glob("*.csv"):
    label = csv_path.stem
    df = pd.read_csv(csv_path)

    # optional: capture the shared time vector once
    time_vector = df["time"].values

    for neuron in df.columns:
        if neuron == "time":
            continue

        if neuron not in G:
            G.add_node(neuron)
            print(f"[+] Added missing node '{neuron}' from {csv_path.name}")

        ts_dict = G.nodes[neuron].get("timeseries", {})
        ts_dict[label] = df[neuron].values
        G.nodes[neuron]["timeseries"] = ts_dict

with open('data/data_derivatives/stx_fx_time.gpickle', 'wb') as f:
    pickle.dump(G, f)
    
for node in sorted(G.nodes):
    print(node)

