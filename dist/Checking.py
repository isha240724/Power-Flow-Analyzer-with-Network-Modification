
from tkinter import Tk, filedialog

root = Tk()
root.withdraw()

raw_file = filedialog.askopenfilename()

with open(raw_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
buses = []
branches = []
generators = []
loads = []
branch_start = None
branch_end = None

for i, line in enumerate(lines):

    if "END OF GENERATOR DATA" in line.upper():
        branch_start = i + 1

    if "END OF BRANCH DATA" in line.upper():
        branch_end = i
        break

import networkx as nx

G = nx.Graph()

# Bus Nodes
for line in lines[2:]:

    if "END OF BUS DATA" in line.upper():
        break

    parts = line.split(",")

    try:
        bus_no = int(parts[0].strip())

        G.add_node(bus_no)
        buses.append(bus_no)
    except:
        pass
print("\n========================")
print("LOAD BUSES")
print("========================")

load_start = None
load_end = None

for i, line in enumerate(lines):

    if "END OF BUS DATA" in line.upper():
        load_start = i + 1

    if "END OF LOAD DATA" in line.upper():
        load_end = i
        break

print("LOAD START =", load_start)
print("LOAD END =", load_end)

for line in lines[load_start:load_end]:

    parts = line.split(",")

    try:
        bus_no = int(parts[0].strip())
        loads.append(bus_no)

    except:
        pass
# Branch Edges
for line in lines[branch_start:branch_end]:

    parts = line.split(",")

    try:
        from_bus = int(parts[0].strip())
        to_bus = int(parts[1].strip())

        G.add_edge(from_bus, to_bus)
        branches.append((from_bus, to_bus))
    except:
        pass

gen_start = None
gen_end = None

for i, line in enumerate(lines):

    if "END OF LOAD DATA" in line.upper():
        gen_start = i + 1

    if "END OF GENERATOR DATA" in line.upper():
        gen_end = i
        break

print("GEN START =", gen_start)
print("GEN END =", gen_end)

print("\nGENERATOR BUSES:\n")

for line in lines[gen_start:gen_end]:

    parts = line.split(",")

    try:
        bus_no = int(parts[0].strip())
        generators.append(bus_no)
        print(bus_no)
    except:
        pass
print("\nSUMMARY")
print("TOTAL BUSES =", len(buses))
print("TOTAL BRANCHES =", len(branches))
print("TOTAL GENERATORS =", len(generators))
print("TOTAL LOADS =", len(loads))
