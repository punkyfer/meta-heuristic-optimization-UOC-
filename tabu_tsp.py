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
        self._2_opt_edges = []
        self.moved_edges = []
        self.num_iterations = 0

    def recompute_cost(self, dist_matrix):
        self.cost = 0.0
        for edge in self.edges:
            self.cost += dist_matrix[edge[0].id][edge[1].id]
        return self.cost

    def __str__(self) -> str:
        return f"{self.edges} -> Cost: {self.cost:.2f} ({self.num_iterations} Iterations)" 
    
    def __repr__(self) -> str:
        return str(self.edges)
    
    def has_duplicates(self, nodes):
        route_nodes = []
        for edge in self.edges:
            route_nodes.append(edge[0])
        
        route_nodes.sort()
        original_nodes = nodes.copy()
        original_nodes.sort()

        return route_nodes != original_nodes


def dist(node_1: Node, node_2: Node):
    return math.sqrt((node_1.x - node_2.x)**2 + (node_1.y - node_2.y)**2)

def stochastic_2_opt(route, dist_matrix):
    new_route = Route()
    new_route.edges = route.edges.copy()
    
    e1 = random.randint(0, len(new_route.edges)-2)
    e2 = random.randint(e1+1, len(new_route.edges)-1)

    edge_1 = new_route.edges[e1]
    edge_2 = new_route.edges[e2]

    new_route.edges[e1] = (edge_1[0], edge_2[0])
    new_route.edges[e2] = (edge_1[1], edge_2[1])
    
    edges_between_them = new_route.edges[e1+1:e2]
    edges_between_them.reverse()
    for k in range(len(edges_between_them)):
        edges_between_them[k] = (edges_between_them[k][1], edges_between_them[k][0])
    
    new_route.edges[e1+1:e2] = edges_between_them

    new_route.recompute_cost(dist_matrix)

    new_route._2_opt_edges.append(new_route.edges[e1])
    new_route._2_opt_edges.append(new_route.edges[e2])

    new_route.moved_edges = [new_route.edges[e1]]+edges_between_them+[new_route.edges[e2]]

    return new_route

def generate_new_solution(base_route, best_route, tabu_set, dist_matrix):

    new_route = None

    while new_route is None or is_tabu(new_route, tabu_set):

        new_route = stochastic_2_opt(base_route, dist_matrix)

        if new_route.cost < best_route.cost:
            break
    
    return new_route


def is_tabu(route, tabu_set):
    if len(tabu_set.intersection(route.moved_edges)) == 0:
        return False
    return True


def construct_initial_solution(nodes, dist_matrix):
    random.shuffle(nodes)
    route = Route()
    for i in range(len(nodes)-1):
        route.edges.append((nodes[i], nodes[i+1]))
        route.cost += dist_matrix[nodes[i].id][nodes[i+1].id]

    route.edges.append((nodes[-1], nodes[0]))
    route.cost += dist_matrix[nodes[-1].id][nodes[0].id]
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
        
    new_route.cost = new_route.recompute_cost(dist_matrix)

    return new_route
    

if __name__ == "__main__":

    filename = "berlin52.txt"

    max_iterations = 500
    max_edges_tabu_list = 10
    max_new_sols = 40
    k = 5

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

    base_sol = initial_sol
    best_sol = initial_sol

    credit = 0
    tabu_list = []
    tabu_set = set()

    for i in range(max_iterations):
        best_new_sol = Route()
        best_new_sol.cost = float("inf")
        new_sols = []
        for j in range(max_new_sols):
            new_sol = generate_new_solution(base_sol, best_sol, tabu_set, dist_matrix)
            new_sols.append(new_sol)
            if new_sol.cost < best_new_sol.cost:
                best_new_sol = new_sol

        delta = best_new_sol.cost - base_sol.cost
        if delta <= 0:
            credit = -1 * delta
            base_sol = best_new_sol

            if best_new_sol.cost < best_sol.cost:
                best_sol = best_new_sol
                best_sol.num_iterations = i

                for edge in best_new_sol._2_opt_edges:
                    tabu_list.append(edge)
                    tabu_set.add(edge)

                    if len(tabu_list) > max_edges_tabu_list:
                        try:
                            tabu_set.remove(tabu_list[0])
                        except:
                            pass
                        del tabu_list[0]
        else:
            if delta <= k * credit:
                credit = 0
                base_sol = best_new_sol


    print("Instance Name: "+filename.split(".")[0])
    print("-------------------------------------")
    print("Initial Random solution")
    print(initial_sol)
    print("-------------------------------------")
    print("Tabu Search solution")
    print(best_sol)