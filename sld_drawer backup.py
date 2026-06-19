import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

def draw_sld(G):

    plt.figure(figsize=(15,10))

    pos = nx.kamada_kawai_layout(G)

    # -------------------------
    # AREA DETECTION
    # -------------------------
    communities = list(greedy_modularity_communities(G))

    colors = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "cyan",
        "yellow",
        "magenta"
    ]

    node_colors = {}

    for i, community in enumerate(communities):

        color = colors[i % len(colors)]

        for node in community:
            node_colors[node] = color

    # -------------------------
    # DRAW EDGES
    # -------------------------
    for u, v in G.edges():

        if node_colors[u] == node_colors[v]:

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color=node_colors[u],
                width=2
            )

        else:

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color="black",
                style="dashed",
                width=2
            )

    # -------------------------
    # DRAW NODES
    # -------------------------
    for node in G.nodes():

        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=[node],
            node_color=node_colors[node],
            node_size=250
        )

    # -------------------------
    # LABELS
    # -------------------------
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8
    )

    plt.title("Area Wise Power Network")

    plt.axis("off")
    plt.show()
