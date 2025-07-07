import queue
import networkx as nx
import matplotlib.pyplot as plt

def initialize_domains(board):
    domain = []
    for r in range(9):
        row = []
        for c in range(9):
            if board[r][c] == 0:
                row.append({1, 2, 3, 4, 5, 6, 7, 8, 9})
            else:
                row.append({board[r][c]})
        domain.append(row)
    return domain


def define_arcs(board):
    arcs = queue.Queue()
    for row in range(9):
        for col in range(9):
            for j in range(9):
                if j != col:
                    arcs.put(((row, col), (row, j)))
            for i in range(9):
                if i != row:
                    arcs.put(((row, col), (i, col)))
            box_x = col // 3
            box_y = row // 3
            for i in range(box_y * 3, box_y * 3 + 3):
                for j in range(box_x * 3, box_x * 3 + 3):
                    if i != row and j != col:
                        arcs.put(((row, col), (i, j)))
    return arcs


def revise(domaini, domainj):
    revised = False
    to_remove = []
    for i in domaini:
        if not any(i != j for j in domainj):
            to_remove.append(i)
            revised = True
    dom = domaini.copy()
    for i in to_remove:
        dom.remove(i)
    return revised, dom


def neighbours(rowi, coli, rowj, colj):
    neighbours = queue.Queue()
    for j in range(9):
        if j != coli and j != colj:
            neighbours.put(((rowi, coli), (rowi, j)))
    for i in range(9):
        if i != rowi and i != rowj:
            neighbours.put(((rowi, coli), (i, coli)))
    box_x = coli // 3
    box_y = rowi // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if i != rowi and j != coli and i != rowj and j != colj:
                neighbours.put(((rowi, coli), (i, j)))
    return neighbours

def print_subtree(arc_tree, start_node, prefix="", visited=None, is_last=True):
    """
    Print a part of the arc consistency tree starting from a specific node.
    """
    if visited is None:
        visited = set()

    if start_node in visited:
        return
    visited.add(start_node)

    # Build label
    (a, b), (c, d) = start_node
    connector = "+-- " if is_last else "|-- "
    print(prefix + connector + f"(X{a}{b} -> X{c}{d})")

    # Update prefix for children
    new_prefix = prefix + ("    " if is_last else "|   ")
    children = arc_tree.get(start_node, [])
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        print_subtree(arc_tree, child, new_prefix, visited, is_last_child)


def print_filtered_tree(arc_tree, start_node, prefix="", visited=None, is_last=True, filter_var=None):
    """
    Print arcs filtered by a specific variable. Only arcs related to `filter_var` will be printed.
    """
    if visited is None:
        visited = set()

    if start_node in visited:
        return
    visited.add(start_node)

    # If a filter is set and the start_node does not involve the filter variable, skip it
    if filter_var is not None and filter_var not in start_node:
        return

    # Build label
    (a, b), (c, d) = start_node
    connector = "+-- " if is_last else "|-- "
    print(prefix + connector + f"(X{a}{b} -> X{c}{d})")

    # Update prefix for children
    new_prefix = prefix + ("    " if is_last else "|   ")
    children = arc_tree.get(start_node, [])
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        print_filtered_tree(arc_tree, child, new_prefix, visited, is_last_child, filter_var)

def print_arc_tree(arc_tree, arc=None, prefix="", visited=None, is_last=True):
    if visited is None:
        visited = set()

    if arc is None:
        # Find root arcs (those that aren't children of any arc)
        all_children = set(child for children in arc_tree.values() for child in children)
        roots = [a for a in arc_tree if a not in all_children]
        for i, root in enumerate(roots):
            is_last_root = i == len(roots) - 1
            print_arc_tree(arc_tree, root, "", visited, is_last_root)
        return

    if arc in visited:
        return
    visited.add(arc)

    # Build label
    (a, b), (c, d) = arc
    connector = "+-- " if is_last else "|-- "
    print(prefix + connector + f"(X{a}{b} -> X{c}{d})")

    # Update prefix for children
    new_prefix = prefix + ("    " if is_last else "|   ")
    children = arc_tree.get(arc, [])
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        print_arc_tree(arc_tree, child, new_prefix, visited, is_last_child)


def visualize_arc_tree(arc_tree):
    G = nx.DiGraph()  # Directed graph for tree structure

    # Add edges to the graph
    for parent, children in arc_tree.items():
        for child in children:
            (a, b), (c, d) = parent
            (e, f), (g, h) = child
            G.add_edge(f"X{a}{b}", f"X{c}{d}", label=f"({a},{b}) -> ({c},{d})")
    
    # Plot the tree using a spring layout (works for most non-planar graphs)
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Positions for the nodes, using a random seed for reproducibility
    
    # Draw the graph with labels on the edges
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold', arrows=True)
    
    # Draw edge labels (arc labels)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    # Show the plot
    plt.title("Arc Consistency Tree")
    plt.show()



def ac3(board, domain, arcs, filename="log.txt"):
    arc_tree = {}  # Tracks which arc caused others to be added
    revised_any = False  # Track if any revision occurred

    while not arcs.empty():
        with open(filename, "a") as f:
            ((rowi, coli), (rowj, colj)) = arcs.get()
            current_arc = ((rowi, coli), (rowj, colj))

            rev, dom = revise(domain[rowi][coli], domain[rowj][colj])
            if rev:
                revised_any = True
                print(f"Revising arc (X{rowi}{coli}, X{rowj}{colj})")
                f.write(f"Revising arc (X{rowi}{coli}, X{rowj}{colj})\n")
                print(f"Current domain of X{rowi}{coli}: {domain[rowi][coli]}")
                f.write(f"Current domain of X{rowi}{coli}: {domain[rowi][coli]}\n")
                print(f"Domain of X{rowj}{colj}: {domain[rowj][colj]}")
                f.write(f"Domain of X{rowj}{colj}: {domain[rowj][colj]}\n")
                removed = domain[rowi][coli] - dom
                for r in removed:
                    print(f"Removed value {r} from X{rowi}{coli} because no supporting value exists in X{rowj}{colj}")
                    f.write(f"Removed value {r} from X{rowi}{coli} because no supporting value exists in X{rowj}{colj}\n")
                print(f"Updated domain of X{rowi}{coli}: {dom}\n")
                f.write(f"Updated domain of X{rowi}{coli}: {dom}\n\n\n")
                domain[rowi][coli] = dom
                if not domain[rowi][coli]:
                    return False

                neighbour = neighbours(rowi, coli, rowj, colj)
                arc_tree.setdefault(current_arc, [])
                while not neighbour.empty():
                    n = neighbour.get()
                    arcs.put(n)
                    arc_tree[current_arc].append(n)

            else:
                # Still record arc in tree (for completeness, even if it caused no new arcs)
                arc_tree.setdefault(current_arc, [])

        f.close()

    print("\nArc Consistency Tree:")
    if revised_any:
        print_arc_tree(arc_tree)
        visualize_arc_tree(arc_tree)  # Visualize the tree
    else:
        print("No revisions made, tree is empty.")
    return domain
