import os

print("CURRENT FOLDER =", os.getcwd())
print("FILES =", os.listdir())
print("MAIN FILE STARTED")
from tkinter import Tk, filedialog
import sys
from parser import parse_raw
from network_builder import build_graph
from sld_drawer import draw_sld
import sld_drawer
print("SLD FILE =", sld_drawer.__file__)
from networkx.algorithms.community import greedy_modularity_communities
if len(sys.argv) > 1:

    raw_file = sys.argv[1]

else:

    root = Tk()
    root.withdraw()

    raw_file = filedialog.askopenfilename(
        title="Select RAW File",
        filetypes=[("RAW Files","*.raw *.RAW")]
    )

with open(raw_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

data = parse_raw(lines)

slack_bus = None

for bus in data.buses:

    if data.bus_types[bus] == 3:

        slack_bus = bus

        break

print("SLACK BUS =", slack_bus)





    
G = build_graph(data)

print("\nSUMMARY")
print("TOTAL BUSES =", len(data.buses))
print("TOTAL BRANCHES =", len(data.branches))
print("TOTAL GENERATORS =", len(data.generators))
print("TOTAL LOADS =", len(data.loads))
print("TOTAL TRANSFORMERS =", len(data.transformers))
print("\nGRAPH")
print("NODES =", G.number_of_nodes())
print("EDGES =", G.number_of_edges())
print("\nFIRST 10 BUS NAMES\n")

for bus_no, bus_name in list(data.bus_names.items())[:10]:
    print(bus_no, "=", bus_name)

print("\nAREA STATISTICS\n")

from networkx.algorithms.community import greedy_modularity_communities

communities = list(greedy_modularity_communities(G))

for i, community in enumerate(communities):

    print(f"AREA {i+1} : {len(community)} BUSES")

    print(
        "BUSES =",
        sorted(list(community))
    )

    print()
print("\nINTER AREA LINKS\n")

node_to_area = {}

for area_no, community in enumerate(communities, start=1):

    for node in community:
        node_to_area[node] = area_no

links = {}

for u, v in G.edges():

    area_u = node_to_area[u]
    area_v = node_to_area[v]

    if area_u != area_v:

        pair = tuple(sorted((area_u, area_v)))

        links[pair] = links.get(pair, 0) + 1

for pair, count in sorted(links.items()):

    print(
        f"AREA {pair[0]} ↔ AREA {pair[1]} : {count} Links"
   )
# INTER AREA LINKS wala code
print("\nTOTAL GENERATORS =", len(data.generators))
print("TOTAL LOADS =", len(data.loads))
print("TOTAL TRANSFORMERS =", len(data.transformers))

print("\nLAST 10 GENERATORS")
print(data.generators[-10:])

print("\nLAST 10 LOADS")
print(data.loads[-10:])

print(type(data.generators[0]))
print(data.generators[:5])

print("\nFIRST 5 BRANCHES")
for b in data.branches[:5]:
    print(b)

print("\nGENERATORS")
for g in data.generators[:10]:
    print(g)

print("\nLOADS")
for l in data.loads[:10]:
    print(l)

print("\nTRANSFORMERS")
for t in data.transformers[:5]:
    print(t)

import os

json_file = os.path.splitext(raw_file)[0] + "_nr_results.json"

draw_sld(
    G,
    data.generators,
    data.loads,
    data.transformers,
    slack_bus,
    json_file
)
