import matplotlib.pyplot as plt
import networkx as nx
import json
   
try:
    with open("line_loss.json", "r") as f:
        line_loss = json.load(f)
except:
    line_loss = {}    
from networkx.algorithms.community import greedy_modularity_communities

def draw_sld(G, generators, loads, transformers, slack_bus, json_file):
    line_loss_file = json_file.replace(
        "_nr_results.json",
        "_line_loss.json"
    )

    try:
        with open(line_loss_file, "r") as f:
            line_loss = json.load(f)
    except:
        line_loss = {}    
    try:
        with open(json_file, "r") as f:
            nr_data = json.load(f)

        print("JSON Loaded Successfully")
        print("Total Keys =", len(nr_data))

    except Exception as e:

        print("JSON ERROR =", e)

        nr_data = {}  

    print("JSON FILE =", json_file)
    print("JSON KEYS =", list(nr_data.keys())[:10])
    print("JSON FILE =", json_file)
    global popup_box
    popup_box = None
    plt.figure(figsize=(50,30))
    generator_buses = set(generators)
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

    # Fixed area locations
    centers = [
        (-3000,  2500),   # AREA 1
        ( 3000,  2500),   # AREA 2

        (-3300,  6500),   # AREA 3
        ( 3300,  6500),   # AREA 4

        (-3000, -750),   # AREA 5
        ( 3000, -750),   # AREA 6

        (-3300, -3200),   # AREA 7
        ( 3300, -3200)    # AREA 8
    ]

    pos = {}
    node_colors = {}

    for area_id, community in enumerate(communities):

        subG = G.subgraph(list(community))

        local_pos = nx.kamada_kawai_layout(subG)

        cx, cy = centers[area_id % len(centers)]

        color = colors[area_id % len(colors)]

        for node in community:

            x, y = local_pos[node]

            if area_id == 1:      # Blue
                scale = 1400

            elif area_id == 3:   # Orange
                scale = 1400

            elif area_id == 0:   # Red
                scale = 1400

            else:
                scale = 1400
            pos[node] = (
                x * scale + cx,
                y * scale + cy
            )
##            node_colors[node] = color
            

       # plt.text(
        #    cx - 220,
         #   cy,
         #   f"AREA {area_id + 1}",
          #  fontsize=18,
           # fontweight="bold",
           # bbox=dict(
             #   facecolor="white",
               # edgecolor="black"
          #  )
        #)
    # ==========================
    # BUS TYPE COLORS
    # ==========================

    

    node_colors = {}

    for node in G.nodes():

        if node == slack_bus:

            node_colors[node] = "gold"

        elif node in generators and node in loads:

            node_colors[node] = "purple"

        elif node in generators:

            node_colors[node] = "green"

        elif node in loads:

            node_colors[node] = "red"

        else:

            node_colors[node] = "deepskyblue"
    # Draw edges
    # Draw edges
    for u, v in G.edges():

        if node_colors[u] == node_colors[v]:

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color=node_colors[u],
                width=1
            )

        else:

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color="black",
                style="dashed",
                width=1
            )
    # Reactance Labels (Only first 10 lines)

    edge_labels = {}

    count = 0

    for u, v, attr in G.edges(data=True):

        if "x" in attr:

            edge_labels[(u, v)] = f"{attr['x']:.3f}"

            count += 1

            if count >= 10:
                break

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=6
    )
        # Draw nodes
    node_sizes = []

    for node in G.nodes():

        if node == slack_bus:
            node_sizes.append(500)

        elif node in generators:
            node_sizes.append(350)

        elif node in loads:
            node_sizes.append(250)

        else:
            node_sizes.append(180)    
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=[node_colors[n] for n in G.nodes()],
        node_size=node_sizes
    )

##    # Transformer marker
##    for u, v, attr in G.edges(data=True):
##
##        if attr.get("edge_type") == "transformer":
##
##            x1, y1 = pos[u]
##            x2, y2 = pos[v]
##
##            plt.text(
##                (x1 + x2) / 2,
##                (y1 + y2) / 2,
##                "T",
##                fontsize=10,
##                color="black",
##                fontweight="bold"
##            )

    # Bus labels
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8,
        font_color="white"
    )
##    # Generator Symbols

##    for bus in generators:
##
##        if bus in pos:
##
##            x, y = pos[bus]
##
##            plt.text(
##                x + 120,
##                y + 120,
##                "G",
##                fontsize=10,
##                fontweight="bold",
##                color="black"
##            )
    plt.title("Area Wise Power Network")

        # ==============================
    # NETWORK DASHBOARD
    # ==============================

    area_info = ""

    for i, community in enumerate(communities):

        area_info += (
            f"Area {i+1} : {len(community)} Buses\n"
        )

    summary_text = (
        f"NETWORK SUMMARY\n"
        f"================\n\n"
        f"Total Buses : {len(G.nodes())}\n"
        f"Total Generators : {len(generators)}\n"
        f"Total Loads : {len(loads)}\n"
        f"Total Branches : {len(G.edges())}\n"
        f"Total Transformers : {len(transformers)}\n\n"
        f"AREA SUMMARY\n"
        f"------------\n"
        f"{area_info}"
        f"\n"
        f"BUS COLOR LEGEND\n"
        f"----------------\n"
        f"Green  : Generator Bus\n"
        f"Red    : Load Bus\n"
        f"Purple : Gen + Load Bus\n"
        f"Yellow : Slack Bus\n"
        f"Blue   : Normal Bus\n"
        )

    plt.gcf().text(
        0.82,      # Right Side
        0.90,      # Top
        summary_text,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(
            facecolor="lightyellow",
            edgecolor="black",
            boxstyle="round,pad=0.5"
        )
    )
        
    plt.axis("off")

    plt.margins(0.20)

    plt.subplots_adjust(
        left=0.05,
        right=0.95,
        top=0.95,
        bottom=0.05
    )
    def onclick(event):
        global popup_box

        # Double click = close popup

        if event.dblclick:

            try:
                popup_box.remove()
                popup_box = None
                plt.draw()
            except:
                pass

            return
        if event.xdata is None or event.ydata is None:
            return

        click_x = event.xdata
        click_y = event.ydata

        nearest_bus = None
        min_dist = float("inf")

        for bus, (x, y) in pos.items():

            dist = ((click_x - x)**2 + (click_y - y)**2)**0.5

            if dist < min_dist:
                min_dist = dist
                nearest_bus = bus

        if min_dist > 300:
            return

        bus = nearest_bus
        # ===========================
# RIGHT CLICK NR POPUP
# ===========================

        if event.button == 3:
            print("Clicked Bus =", bus)
            print("Lookup Key =", str(int(bus)))
            print("Available =", str(int(bus)) in nr_data)
            data = nr_data.get(str(int(bus)))
            print("Data =", data)
            if data:

                info = f"NR RESULTS\n\n"

                info += f"Bus : {bus}\n"

                info += f"Type : {data['type']}\n\n"

                info += f"Voltage : {data['V']:.5f} pu\n"

                info += f"Angle : {data['angle']:.5f} deg\n\n"

                info += f"P Injection : {data['Pinj']:.4f} MW\n"

                info += f"Q Injection : {data['Qinj']:.4f} MVAR\n\n"

                info += f"P Spec : {data['Pspec']:.4f} MW\n"

                info += f"Q Spec : {data['Qspec']:.4f} MVAR\n\n"

                info += f"dP : {data['dP']:.6f}\n"

                info += f"dQ : {data['dQ']:.6f}"
                info += "\n\nCONNECTED LINE LOSSES\n"
                info += "-----------------------\n"

                for nbr in G.neighbors(bus):

                    key1 = f"{int(bus)}-{int(nbr)}"
                    key2 = f"{int(nbr)}-{int(bus)}"
                    print("BUS =", bus)
                    print("KEY1 =", key1)
                    print("KEY2 =", key2)
                    if key1 in line_loss:

                        info += (
                            f"{key1} : "
                            f"{line_loss[key1]['PLOSS']:.4f} MW\n"
                        )

                    elif key2 in line_loss:

                        info += (
                            f"{key2} : "
                            f"{line_loss[key2]['PLOSS']:.4f} MW\n"
                        )
                
            else:

                info = "NR DATA NOT FOUND"

            try:
                if popup_box is not None:
                    popup_box.remove()
            except:
                pass

            popup_box = plt.annotate(
                info,
                (click_x, click_y),
                xytext=(80,80),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    fc="lightgreen",
                    ec="darkgreen",
                    lw=2
                ),
                fontsize=7
            )

            plt.draw()

            return

   
        info = f"BUS {bus}\n\n"

        vm = G.nodes[bus].get("voltage", 1.0)
        va = G.nodes[bus].get("angle", 0.0)

        info += f"Voltage : {vm:.5f} pu\n"
        info += f"Angle : {va:.4f} deg\n\n"

        info += f"Generator : {'Yes' if bus in generators else 'No'}\n"
        info += f"Load : {'Yes' if bus in loads else 'No'}\n"
        info += f"Connected Lines : {G.degree(bus)}\n\n"

        info += "CONNECTED BRANCHES\n"
        info += "------------------\n"

        try:
            popup_box.remove()
        except:
            pass

        for nbr in G.neighbors(bus):

            edge = G.get_edge_data(bus, nbr)

            info += f"\n{bus} -> {nbr}\n"

            if "r" in edge:
                info += f"R = {edge['r']:.4f}\n"

            if "x" in edge:
                info += f"X = {edge['x']:.4f}\n"
        # Popup position adjustment

        if click_x > 2500:

            offset = (-250, -80)

        elif click_y > 2000:

            offset = (80, -300)

        else:

            offset = (80, 80)
        popup_box = plt.annotate(
            info,
            (click_x, click_y),
            xytext=offset,
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.5",
                fc="lightblue",
                ec="navy",
                lw=2,
                alpha=0.95
            ),
            fontsize=6
        )

        plt.draw()

               
    fig = plt.gcf()

    fig.canvas.mpl_connect(
        "button_press_event",
        onclick
    )
    plt.show()

