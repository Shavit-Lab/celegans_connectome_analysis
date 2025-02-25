# get the directory of this file
import os
from pathlib import Path 
import networkx as nx
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
project_path = Path(dir_path).parent
# get the directory of the project


def get_adult_c_elegans_nx():
    path_syncounts = project_path / 'data' / '41586_2021_3778_MOESM4_ESM.xlsx'

    # read in the data
    df = pd.read_excel(path_syncounts, sheet_name="Dataset8", header=2)
    # remove first row
    df = df.iloc[1:]
    # remove the first column
    df = df.iloc[:,1:]

    #name the first column "neuron type"
    df.columns = ["neuron type"] + list(df.columns[1:])
    # name the second column "neuron name"
    df = df.rename(columns={df.columns[1]: "neuron name"})

    # if neuron type is nan, copy the previous neuron type
    df["neuron type"] = df["neuron type"].fillna(method='ffill')

    # check that the neuron names are unique
    row_names = df["neuron name"]
    col_names = df.columns[2:]
    assert row_names.nunique() == len(row_names)
    assert col_names.nunique() == len(col_names)

    # for neuron type, map Sensory to Sens.
    df["neuron type"] = df["neuron type"].str.replace("Sensory", "Sens.")
    df["neuron type"] = df["neuron type"].str.replace("Motor", "Mot.")
    df["neuron type"] = df["neuron type"].str.replace("Inter", "Inter.")
    df["neuron type"] = df["neuron type"].str.replace("Modulatory", "Mod.")
    df["neuron type"] = df["neuron type"].str.replace("Motor", "Mot.")



    G = nx.DiGraph()

    # add edges
    for i, row in df.iterrows():
        # iterate through the entries of row
        post = row["neuron name"]
        for pre, val in row.items():
            if pre not in ["neuron type", "neuron name"] and val > 0:
                G.add_edge(pre, post, weight=val)
        


    # add neuron types
    for i, row in df.iterrows():
        neuron_name = row["neuron name"]
        neuron_type = row["neuron type"]
        # if neuron name is not in the graph, add it
        if neuron_name not in G.nodes:
            G.add_node(neuron_name)
        G.nodes[neuron_name]["neuron type"] = neuron_type

    return G
        


def get_fxnl_nx():
    path_stim = project_path / 'data' / '41586_2023_6683_MOESM5_ESM.xlsx'

    # read in the data
    df = pd.read_excel(path_stim, sheet_name="Figure2a, df_over_f")
    df_q = pd.read_excel(path_stim, sheet_name="Figure2a, alpha=(1 - q_val)")

    # set entries in df to 0 if the corresponding entry in df_q is less than 0.5
    # iterate through row and column indices
    for i in range(df.shape[0]):
        for j in range(1,df.shape[1]):
            if df_q.iloc[i,j] < 0.5:
                df.iloc[i,j] = 0

    df = df.transpose()
    df.columns = df.iloc[0]
    df = df.reset_index()
    df = df.drop([0])
    df = df.rename(columns={df.columns[0]: "neuron name"})

    # check that the neuron names are unique
    row_names = df["neuron name"]
    col_names = df.columns[1:]
    assert row_names.nunique() == len(row_names)
    assert col_names.nunique() == len(col_names)
    # assert that the neuron names are the same
    assert (row_names == col_names).all()

    # set the diagonal to 0
    for i in range(df.shape[0]):
        df.iloc[i,i+1] = 0

    # get the row number of the neuron name URYVR
    row_number = df[df["neuron name"] == "URYVR"].index[0]
    # get the row number of the neuron name SIBVR
    row_number2 = df[df["neuron name"] == "SIBVR"].index[0]


    # make a new column called "neuron type". If the index is less than row_number, set the value to "sensory". If the index is greater than row_number, set the value to "interneuron"
    df["neuron type"] = "Motor"
    df.loc[:row_number2, "neuron type"] = "Inter"
    df.loc[:row_number, "neuron type"] = "Sensory"


    # for neuron type, map Sensory to Sens.
    df["neuron type"] = df["neuron type"].str.replace("Sensory", "Sens.")
    df["neuron type"] = df["neuron type"].str.replace("Motor", "Mot.")
    df["neuron type"] = df["neuron type"].str.replace("Inter", "Inter.")
    df["neuron type"] = df["neuron type"].str.replace("Modulatory", "Mod.")
    df["neuron type"] = df["neuron type"].str.replace("Motor", "Mot.")



    G = nx.DiGraph()

    # add edges
    for i, row in df.iterrows():
        # iterate through the entries of row
        post = row["neuron name"]
        for pre, val in row.items():
            if pre not in ["neuron type", "neuron name"] and val > 0:
                G.add_edge(pre, post, weight=val)
        


    # add neuron types
    for i, row in df.iterrows():
        neuron_name = row["neuron name"]
        neuron_type = row["neuron type"]
        # if neuron name is not in the graph, add it
        if neuron_name not in G.nodes:
            G.add_node(neuron_name)
        G.nodes[neuron_name]["neuron type"] = neuron_type

    return G
        
