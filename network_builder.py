import networkx as nx

def build_graph(data):

    G = nx.Graph()

    # Bus nodes
    for bus in data.buses:

        G.add_node(
            bus,
            voltage=data.bus_voltage.get(bus, "N/A"),
            angle=data.bus_angle.get(bus, "N/A")
        )
    # Branch edges
    for from_bus, to_bus, r, x in data.branches:

        G.add_edge(
            from_bus,
            to_bus,
            edge_type="branch",
            r=r,
            x=x
        )
    # Transformer edges
    for from_bus, to_bus in data.transformers:
        G.add_edge(
            from_bus,
            to_bus,
            edge_type="transformer"
        )
    return G
