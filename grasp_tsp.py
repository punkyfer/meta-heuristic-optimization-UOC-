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

def dist(node_1: Node, node_2: Node):
    return math.sqrt((node_1.x - node_2.x)**2 + (node_1.y - node_2.y)**2)

def get_greedy_random_solution(original_nodes, dist_matrix):
    nodes = original_nodes.copy()
    route = Route()
    starting_node = nodes.pop(random.randint(0, len(nodes)-1))

    while len(nodes) > 0:
        elements_distance = []
        max_distance = 0
        for node in nodes:
            node_distance = dist_matrix[starting_node.id][node.id]
            elements_distance.append((node, node_distance))
            if node_distance > max_distance:
                max_distance = node_distance

        # Pure Greedy
        # elements_distance.sort(key = lambda x: x[1], reverse=False)
        # random_node = elements_distance[0][0]
        
        # Greedy Random
        possible_nodes = []
        probabilities = []
        for elem in elements_distance:
            possible_nodes.append(elem[0])
            probabilities.append(1-(elem[1]/(max_distance+1)))

        if probabilities == [0.0]:
            random_node = nodes[0]
        else:
            random_node = random.choices(possible_nodes, weights = probabilities, k=1)[0]

        route.edges.append((starting_node, random_node))
        route.cost += dist_matrix[starting_node.id][random_node.id]
        nodes.remove(random_node)
        starting_node = random_node

    route.edges.append((route.edges[-1][1], route.edges[0][0]))
    return route

def local_search_2_opt(route, dist_matrix, max_iters = 1000):
    num_iters = 0
    best_route = Route()
    best_route.edges = route.edges
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
        else:
            break
    return best_route


    

if __name__ == "__main__":

    filename = "berlin52.txt"

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

    greedy_sol = get_greedy_random_solution(nodes, dist_matrix)
    local_search_solution = local_search_2_opt(greedy_sol, dist_matrix)

    best_sol = local_search_solution

    for i in range(1000):
        greedy_sol = get_greedy_random_solution(nodes, dist_matrix)
        local_search_solution = local_search_2_opt(greedy_sol, dist_matrix)
        if local_search_solution.cost < best_sol.cost:
            best_sol = local_search_solution

    print("Greedy solution")
    print(greedy_sol)
    print("-------------------------------------")
    print("Local Search 2-OPT solution")
    print(best_sol)