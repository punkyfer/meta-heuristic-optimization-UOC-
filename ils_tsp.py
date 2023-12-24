import math
import random

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        
    def __str__(self) -> str:
        return str(self.id)
    
    def __repr__(self) -> str:
        return str(self.id)
    
    def __lt__(self, other):
        return self.id < other.id
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash((self.id, self.x, self.y))
    
class Route:
    def __init__(self):
        self.edges = []
        self.cost = 0.0

    def recompute_cost(self, dist_matrix):
        self.cost = 0.0
        for edge in self.edges:
            self.cost += dist_matrix[edge[0].id][edge[1].id]
        return self.cost

    def __str__(self) -> str:
        return f"{self.edges} -> Cost: {self.cost:.2f}" 
    
    def __repr__(self) -> str:
        return str(self.edges)
    
    def has_duplicates(self, nodes):
        route_nodes = []
        for edge in self.edges:
            route_nodes.append(edge[0])
        route_nodes.append(self.edges[-1][1])

        route_nodes.sort()
        original_nodes = nodes.copy()
        original_nodes.sort()

        return route_nodes != original_nodes


def dist(node_1: Node, node_2: Node):
    return math.sqrt((node_1.x - node_2.x)**2 + (node_1.y - node_2.y)**2)

def local_search_2_opt(route, dist_matrix, max_iters = 50):
    num_iters = 0
    best_route = Route()
    best_route.edges = route.edges.copy()
    best_route.cost = route.cost
    while num_iters < max_iters:
        num_iters += 1
        x = 0
        y = 0
        while x < len(route.edges):
            while y < len(route.edges):
                edge_1 = route.edges[x]
                edge_2 = route.edges[y]
                if edge_1 != edge_2 and edge_1[1] != edge_2[0]:
                    # Swap routes
                    new_route = Route()
                    new_route.edges = route.edges.copy()
                    new_route.edges[x] = (edge_1[0], edge_2[0])
                    new_route.edges[y] = (edge_1[1], edge_2[1])
                    
                    # Reverse edges between them
                    edges_between_them = new_route.edges[x+1:y]
                    edges_between_them.reverse()
                    for k in range(len(edges_between_them)):
                        edges_between_them[k] = (edges_between_them[k][1], edges_between_them[k][0])
                    new_route.edges[x+1:y] = edges_between_them

                    # Recompute costs
                    if new_route.recompute_cost(dist_matrix) < route.cost:
                        route = new_route 
                y += 1
            x += 1
        if route.cost < best_route.cost:
            best_route = Route()
            best_route.edges = route.edges.copy()
            best_route.cost = route.cost
            num_iters = 0
        else:
            break
    return best_route

def construct_initial_solution(nodes, dist_matrix):
    random.shuffle(nodes)
    route = Route()
    for i in range(len(nodes)-1):
        route.edges.append((nodes[i], nodes[i+1]))
        route.cost += dist_matrix[nodes[i].id][nodes[i+1].id]
    return route

def perturbation(route, dist_matrix, random_segments=4):

    new_route = Route()
    new_route.edges = route.edges.copy()

    start_index = random.randint(0, len(new_route.edges)-(1+random_segments))

    nodes = set()
    for i in range(random_segments):
        nodes.add(new_route.edges[start_index+i][0])
        nodes.add(new_route.edges[start_index+i][1])
    
    new_nodes = list(nodes)

    random.shuffle(new_nodes)

    for i in range(len(new_nodes)-1):
        new_route.edges[start_index+i] = (new_nodes[i], new_nodes[i+1])

    if start_index > 0:
        new_route.edges[start_index-1] = (new_route.edges[start_index-1][0], new_nodes[0])

    if start_index+random_segments < len(new_route.edges):
        new_route.edges[start_index+random_segments] = (new_nodes[-1], new_route.edges[start_index+random_segments][1])
        
    new_route.recompute_cost(dist_matrix)

    return new_route
    

if __name__ == "__main__":

    filename = "berlin52.txt"

    max_iterations = 10000
    max_no_improve_iterations = 1000

    # Load file
    with open(filename) as instance:
        nodes = []
        for line in instance:
            data = [x for x in line.split()]
            node = Node(int(data[0])-1, float(data[1]), float(data[2]))
            nodes.append(node)

    # Compute Distance Matrix
    dist_matrix = [[0]*len(nodes) for _ in range(len(nodes))]
    for i, node_1 in enumerate(nodes):
        for j, node_2 in enumerate(nodes):
            if i<j:
                dist_matrix[i][j] = dist(node_1, node_2)
                dist_matrix[j][i] = dist_matrix[i][j]

    initial_sol = construct_initial_solution(nodes, dist_matrix)
    local_search_solution = local_search_2_opt(initial_sol, dist_matrix, max_no_improve_iterations)

    best_sol = local_search_solution

    for i in range(max_iterations):
        new_sol = perturbation(best_sol, dist_matrix, 4)
        new_sol = local_search_2_opt(new_sol, dist_matrix, max_no_improve_iterations)
        if new_sol.cost < best_sol.cost:
            best_sol = new_sol
        
    print("Instance Name: "+filename.split(".")[0])
    print("-------------------------------------")
    print("Initial Random solution")
    print(initial_sol)
    print("-------------------------------------")
    print("ILS solution")
    print(best_sol)