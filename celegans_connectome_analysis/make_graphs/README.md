Run in following order:

Run from celegans_connectome_analysis:

installation requirements:
```txt
dandi==0.63.1
networkx==3.1
numpy==1.24.4
pandas=2.0.3
pynwb==2.8.3
```

More detailed requirements are in .requirements.txt, but the above should cover most if not all essential requirements.

To build graphs:
```bash
python celegans_connectome_analysis/celegans_connectome_analysis/make_graphs/build_checked_graph.py
python celegans_connectome_analysis/celegans_connectome_analysis/make_graphs/process_timescales.py
python celegans_connectome_analysis/celegans_connectome_analysis/make_graphs/common_networkx.py
```





