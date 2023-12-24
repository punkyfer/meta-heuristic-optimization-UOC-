import math
import time
import operator
import networkx as nx
import matplotlib.pyplot as plt
import glob

class Node:
    def __init__(self, id, x, y, demand):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.route = None
        self.is_interior = False
        
    def __str__(self) -> str:
        return str(self.id)
    
    def __repr__(self) -> str:
        return str(self.id)
    

class Route:
    def __init__(self):
        self.edges = []
        self.demand = 0.0

    def __str__(self) -> str:
        return f"{self.edges} -> Demand: {self.demand:.2f}" 
    
    def __repr__(self) -> str:
        return str(self.edges)


def dist(node_1: Node, node_2: Node):
    return math.sqrt((node_1.x - node_2.x)**2 + (node_1.y - node_2.y)**2)


def compute_efficiency(node_i:Node, node_j:Node, start:Node, finish:Node, alpha, dist_matrix):
    savings = dist_matrix[start.id][node_i.id] + dist_matrix[finish.id][node_j.id] - dist_matrix[node_i.id][node_j.id]
    reward = node_i.demand + node_j.demand
    return alpha * savings + (1-alpha) * reward


def compute_route_cost(route:Route, dist_matrix):
    cost = 0
    for nodes in route.edges:
        cost += dist_matrix[nodes[0].id][nodes[1].id]
    return cost

def pjs_top_algorithm(fileName, alpha, plot_graph=False, print_sols = False):

    start_time = time.time()

    # Load file
    with open(fileName) as instance:
        i = -3
        nodes = []
        for line in instance:
            if i == -3: pass
            elif i == -2: fleetSize = int( line.split(";")[1] )
            elif i == -1: routeMaxCost = float( line.split(";")[1] )
            else:
                data = [float(x) for x in line.split(";")]
                aNode = Node(i, data[0], data[1], data[2])
                nodes.append(aNode)
            i += 1

    num_nodes = len(nodes)

    # Compute Distance Matrix
    dist_matrix = [[0]*len(nodes) for _ in range(len(nodes))]
    for i, node_1 in enumerate(nodes):
        for j, node_2 in enumerate(nodes):
            if i<j:
                dist_matrix[i][j] = dist(node_1, node_2)
                dist_matrix[j][i] = dist_matrix[i][j]

    start = nodes[0]
    finish = nodes[-1]

    # Compute Savings List
    savings = []
    for node_i in nodes[1:-2]:
        for node_j in nodes[node_i.id+1:-1]:
            savings.append((node_i, node_j, compute_efficiency(node_i, node_j, start, finish, alpha, dist_matrix)))

    savings.sort(key = lambda x: x[2], reverse=True)

    routes = []

    while len(savings) > 0:
        node_i, node_j, _ = savings.pop(0)
        if node_i.route == None and node_j.route == None:
            # Create new route
            if dist_matrix[start.id][node_i.id] + dist_matrix[node_i.id][node_j.id] + dist_matrix[node_j.id][finish.id] <= routeMaxCost:
                route = Route()
                route.edges = [(start, node_i),(node_i, node_j),(node_j, finish)]
                node_i.route = route
                node_j.route = route
                route.demand = node_i.demand + node_j.demand
                routes.append(route)
        if node_i.route != None and node_i.is_interior == False and node_j.route == None:
            # Add node_j to node_i route
            add_to_route = False
            try:
                if compute_route_cost(node_i.route, dist_matrix) - dist_matrix[node_i.id][finish.id] + dist_matrix[node_i.id][node_j.id] + dist_matrix[node_j.id][finish.id] <= routeMaxCost:
                    node_i.route.edges.remove((node_i, finish))
                    node_i.route.edges.append((node_i, node_j))
                    node_i.route.edges.append((node_j, finish))
                    add_to_route = True
            except:
                if compute_route_cost(node_i.route, dist_matrix) - dist_matrix[start.id][node_i.id] + dist_matrix[node_j.id][node_i.id] + dist_matrix[start.id][node_j.id] <= routeMaxCost:
                    node_i.route.edges.remove((start, node_i))
                    node_i.route.edges.append((node_j, node_i))
                    node_i.route.edges.append((start, node_j))
                    add_to_route = True
            if add_to_route:
                node_i.is_interior = True
                node_i.route.demand += node_j.demand
                node_j.route = node_i.route
        if node_j.route != None and node_j.is_interior == False and node_i.route == None:
            # Add node_i to node_j route
            add_to_route = False
            try:
                if compute_route_cost(node_j.route, dist_matrix) - dist_matrix[node_j.id][finish.id] + dist_matrix[node_j.id][node_i.id] + dist_matrix[node_i.id][finish.id] <= routeMaxCost:
                    node_j.route.edges.remove((node_j, finish))
                    node_j.route.edges.append((node_j, node_i))
                    node_j.route.edges.append((node_i, finish))
                    add_to_route = True
            except:
                if compute_route_cost(node_j.route, dist_matrix) - dist_matrix[start.id][node_j.id] + dist_matrix[node_i.id][node_j.id] + dist_matrix[start.id][node_i.id] <= routeMaxCost:
                    node_j.route.edges.remove((start, node_j))
                    node_j.route.edges.append((node_i, node_j))
                    node_j.route.edges.append((start, node_i))
                    add_to_route = True
            if add_to_route:
                node_j.is_interior = True
                node_j.route.demand += node_i.demand
                node_i.route = node_j.route
        if node_i.route != None and node_i.is_interior == False and node_j.route != None and node_j.is_interior == False and node_i.route != node_j.route:
            # Merge node_i and node_j routes
            if compute_route_cost(node_i.route, dist_matrix) + compute_route_cost(node_j.route, dist_matrix) <= routeMaxCost:
                new_route = Route()
                new_route.edges = node_i.route.edges + node_j.route.edges
                try:
                    new_route.edges.remove((node_i, finish))
                except:
                    new_route.edges.remove((start, node_i))
                try:
                    new_route.edges.remove((node_j, finish))
                except:
                    new_route.edges.remove((start, node_j))
                
                new_route.edges.append((node_i, node_j))
                new_route.demand = node_i.route.demand + node_j.route.demand
                # Merge routes
                if compute_route_cost(new_route, dist_matrix) <= routeMaxCost:
                    routes.remove(node_i.route)
                    routes.remove(node_j.route)
                    routes.append(new_route)
                    node_i.is_interior = True
                    node_j.is_interior = True
                    for nodes in node_i.route.edges:
                        if nodes[0] != start:
                            nodes[0].route = new_route
                    for nodes in node_j.route.edges:
                        if nodes[0] != start:
                            nodes[0].route = new_route


    routes.sort(key = operator.attrgetter("demand"), reverse=True)
    total_cost = 0
    max_route_cost = 0
    total_route_cost = 0
    for route in routes[:fleetSize]:
        total_cost += route.demand
        route_cost = compute_route_cost(route, dist_matrix)
        total_route_cost += route_cost
        if route_cost > max_route_cost:
            max_route_cost = route_cost
        if print_sols:
            print(f"{route}, Cost: {compute_route_cost(route, dist_matrix):.2f}")

    end_time = time.time()

    if plot_graph:
        G = nx.Graph()
        G.add_node(start.id, coord=(start.x, start.y))
        for route in routes[:fleetSize]:
            for edge in route.edges:
                G.add_edge(edge[0].id, edge[1].id)
                G.add_node(edge[1].id, coord = (edge[1].x, edge[1].y))
        coord = nx.get_node_attributes(G, "coord")
        nx.draw_networkx(G, coord, node_color="pink")
        plt.savefig(plot_graph, dpi=300, bbox_inches='tight')
    return total_cost, num_nodes, fleetSize, routeMaxCost, max_route_cost, total_route_cost, end_time-start_time

if __name__ == "__main__":
    alpha_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

    fileNames = [f for f in glob.glob('data/p*.txt')]
    fileNames = ["data/p4.4.l.txt", "data/p3.3.l.txt", "data/p5.4.q.txt"]

    image_name = fileNames[1].split("/")[1].replace(".", "_")[:-4]
    print("Instance Name: p5.4.q")
    print("-------------------------------------")
    pjs_top_algorithm(fileNames[2], 0.7, False, True)
    print("")
    # "pjs_top_"+instance.replace(".","_")
    print("Instance,alpha,# nodes,fleetSize,routeMaxCost,maxRouteCostFound,totalRouteCostFound, PJS Sol.,Time (s)")
    for fileName in fileNames:
        for alpha in alpha_values:
            total_cost, num_nodes, fleetSize, routeMaxCost, max_route_cost, total_route_cost, time_taken = pjs_top_algorithm(fileName, alpha, False, False)
            print(f"{fileName[5:-4]},{alpha},{num_nodes},{fleetSize},{routeMaxCost:.2f},{max_route_cost:.2f},{total_route_cost:.2f},{total_cost:.2f},{time_taken:.3f}")
