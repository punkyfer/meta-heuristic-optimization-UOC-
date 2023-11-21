import math
import time

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
        return f"{self.edges} -> Demand:{self.demand:.2f}" 
    
    def __repr__(self) -> str:
        return str(self.edges)


def dist(node_1: Node, node_2: Node):
    return math.sqrt((node_1.x - node_2.x)**2 + (node_1.y - node_2.y)**2)


def compute_savings(node_i:Node, node_j:Node, depot:Node, dist_matrix):
    return dist_matrix[depot.id][node_i.id] + dist_matrix[depot.id][node_j.id] - dist_matrix[node_i.id][node_j.id]


def compute_route_cost(route:Route, dist_matrix):
    cost = 0
    for nodes in route.edges:
        cost += dist_matrix[nodes[0].id][nodes[1].id]
    return cost


def cws_algorithm(instance_name, vehicle_capacity, print_sols=False):
    start = time.time()
    filename = 'data/'+instance_name+'_input_nodes.txt'

    # Load file
    with open(filename) as instance:
        i = 0
        nodes = []
        for line in instance:
            data = [float(x) for x in line.split()]
            node = Node(i, data[0], data[1], data[2])
            nodes.append(node)
            i += 1

    num_nodes = len(nodes)

    # Compute Distance Matrix
    dist_matrix = [[0]*len(nodes) for _ in range(len(nodes))]
    for i, node_1 in enumerate(nodes):
        for j, node_2 in enumerate(nodes):
            if i<j:
                dist_matrix[i][j] = dist(node_1, node_2)
                dist_matrix[j][i] = dist_matrix[i][j]

    depot = nodes[0]

    # Compute Savings List
    savings = []
    for node_i in nodes[1:-1]:
        for node_j in nodes[node_i.id+1:]:
            savings.append((node_i, node_j, compute_savings(node_i, node_j, depot, dist_matrix)))

    savings.sort(key = lambda x: x[2], reverse=True)

    routes = []

    while len(savings) > 0:
        node_i, node_j, _ = savings.pop(0)
        if node_i.route == None and node_j.route == None:
            # Create new route
            if node_i.demand + node_j.demand <= vehicle_capacity:
                route = Route()
                route.edges = [(depot, node_i),(node_i, node_j),(node_j, depot)]
                node_i.route = route
                node_j.route = route
                route.demand = node_i.demand + node_j.demand
                routes.append(route)
        if node_i.route != None and node_i.is_interior == False and node_j.route == None:
            # Add node_j to node_i route
            if node_i.route.demand + node_j.demand <= vehicle_capacity:
                try:
                    node_i.route.edges.remove((node_i, depot))
                except:
                    node_i.route.edges.remove((depot, node_i))
                node_i.is_interior = True
                node_i.route.edges.append((node_i, node_j))
                node_i.route.edges.append((node_j, depot))
                node_i.route.demand += node_j.demand
                node_j.route = node_i.route
        if node_j.route != None and node_j.is_interior == False and node_i.route == None:
            # Add node_i to node_j route
            if node_j.route.demand + node_i.demand <= vehicle_capacity:
                try:
                    node_j.route.edges.remove((node_j, depot))
                except:
                    node_j.route.edges.remove((depot, node_j))
                node_j.is_interior = True
                node_j.route.edges.append((node_j, node_i))
                node_j.route.edges.append((node_i, depot))
                node_j.route.demand += node_i.demand
                node_i.route = node_j.route
        if node_i.route != None and node_i.is_interior == False and node_j.route != None and node_j.is_interior == False and node_i.route != node_j.route:
            # Merge node_i and node_j routes
            if node_i.route.demand + node_j.route.demand <= vehicle_capacity:
                new_route = Route()
                new_route.edges = node_i.route.edges + node_j.route.edges
                try:
                    new_route.edges.remove((node_i, depot))
                except:
                    new_route.edges.remove((depot, node_i))
                try:
                    new_route.edges.remove((node_j, depot))
                except:
                    new_route.edges.remove((depot, node_j))
                
                new_route.edges.append((node_i, node_j))
                new_route.demand = node_i.route.demand + node_j.route.demand
                # Merge routes if cost of merged route is less than the separate routes
                if compute_route_cost(new_route, dist_matrix) <= compute_route_cost(node_i.route, dist_matrix) + compute_route_cost(node_j.route, dist_matrix):
                    routes.remove(node_i.route)
                    routes.remove(node_j.route)
                    routes.append(new_route)
                    node_i.is_interior = True
                    node_j.is_interior = True
                    for nodes in node_i.route.edges:
                        if nodes[0] != depot:
                            nodes[0].route = new_route
                    for nodes in node_j.route.edges:
                        if nodes[0] != depot:
                            nodes[0].route = new_route


    total_cost = 0
    for route in routes:
        total_cost += compute_route_cost(route, dist_matrix)
        if print_sols:
            print(f"{route}, Cost: {compute_route_cost(route, dist_matrix):.2f}")
    
    end = time.time()

    return total_cost, len(routes), num_nodes, end-start

if __name__ == "__main__":
    instances = [
        ('A-n32-k5', 100.0),
        ('A-n38-k5', 100.0),
        ('A-n45-k7', 100.0),
        ('A-n55-k9', 100.0),
        ('A-n60-k9', 100.0),
        ('A-n61-k9', 100.0),
        ('A-n65-k9', 100.0),
        ('A-n80-k10', 100.0),
        ('B-n50-k7', 100.0),
        ('B-n52-k7', 100.0),
        ('B-n57-k9', 100.0),
        ('B-n78-k10', 100.0),
        ('E-n22-k4', 6000.0),
        ('E-n30-k3', 4500.0),
        ('E-n33-k4', 8000.0),
        ('E-n51-k5', 160.0),
        ('E-n76-k7', 220.0),
        ('E-n76-k10', 140.0),
        ('E-n76-k14', 100.0),
        ('F-n45-k4', 2010.0),
        ('F-n72-k4', 30000.0),
        ('F-n135-k7', 2210.0),
        ('M-n101-k10', 200.0),
        ('M-n121-k7', 200.0),
        ('P-n22-k8', 3000.0),
        ('P-n40-k5', 140.0),
        ('P-n50-k10', 100.0),
        ('P-n55-k15', 70.0),
        ('P-n65-k10', 130.0),
        ('P-n70-k10', 135.0),
        ('P-n76-k4', 350.0),
        ('P-n76-k5', 280.0),
        ('P-n101-k4', 400.0),
    ]

    print("Instance,# nodes,vCap,CWS Sol.,# routes, Time (s)")
    for instance in instances:
        total_cost, num_routes, num_nodes, time_taken = cws_algorithm(instance[0], instance[1], False)
        print(f"{instance[0]},{num_nodes},{instance[1]},{total_cost:.2f},{num_routes},{time_taken:.3f}")
