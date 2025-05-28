# Builds base graph from functional and structural data 
# python celegans_connectome_analysis/make_graphs/build_checked_graph.py


# Requirements: data/*.xlsx files containing functional and structural data.
# Output: data/data_derivatives/checked_graph.gpickle containing the graph containing data from the functional and structural data.

import networkx as nx
import pandas as pd
from pathlib import Path
from celegans_connectome_analysis.get_nx import get_adult_c_elegans_nx, get_fxnl_nx
import pickle 


G_fx = get_fxnl_nx()
G_stx = get_adult_c_elegans_nx()

fx_nodes = set(G_fx.nodes())
stx_nodes = set(G_stx.nodes())

def combined_graph(stx, fx):
    G = nx.DiGraph()
    transfer_info(G, fx, 'fx_weight')
    transfer_info(G, stx, 'stx_weight')
    for u, v in G.edges():
        if 'fx_weight' not in G[u][v]:
            G[u][v]['fx_weight'] = 0
            G[u][v]['has_fx'] = False
        else:
            G[u][v]['has_fx'] = True
        if 'stx_weight' not in G[u][v]:
            G[u][v]['stx_weight'] = 0
            G[u][v]['has_stx'] = False
        else:
            G[u][v]['has_stx'] = True
    return G

def transfer_info(G: nx.DiGraph, source: nx.DiGraph, weight_label: str):
    for node in source.nodes():
        if node not in G.nodes():
            G.add_node(node)
        
        G.nodes[node]['neuron type'] = source.nodes[node]['neuron type']
        # add out edge information
        for target, infos in source[node].items():
            if not G.has_edge(node, target):
                G.add_edge(node, target)
            renamed_infos = {weight_label: infos['weight']}
            G[node][target].update(renamed_infos)
            
G = combined_graph(G_stx, G_fx)
with open('data/data_derivatives/checked_graph.gpickle', 'wb') as f:
    pickle.dump(G, f)

###############################
# run to check if built 
###############################
# with open('data/data_derivatives/checked_graph.gpickle', 'rb') as f:
#     G = pickle.load(f)
    
# print(G.number_of_nodes())
# print(G.number_of_edges())
# print(G.nodes['ADFL'])