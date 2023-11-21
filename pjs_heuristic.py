import networkx as nx
import math
import operator
import time
import matplotlib.pyplot as plt

class Node:
    def __init__(self, ID, x, y, demand):
        self.ID = ID
        self.x = x
        self.y = y
        self.demand = demand
        self.inRoute = None
        self.isInterior = False
        self.dnEdge = None
        self.ndEdge = None
        self.isLinkedToStart = False
        self.isLinkedToFinish = False

class Edge:
    def __init__(self, origin, end):
        self.origin = origin
        self.end = end
        self.cost = 0.0
        self.savings = 0.0
        self.invEdge = None
        self.efficiency = 0.0

class Route:
    def __init__(self):
        self.cost = 0.0
        self.edges = []
        self.demand = 0.0

    def reverse(self):
        size = len(self.edges)
        for i in range(size):
            edge = self.edges[i]
            invEdge = edge.invEdge
            self.edges.remove(edge)
            self.edges.insert(0, invEdge)

class Solution:
    
    last_ID = -1

    def __init__(self):
        Solution.last_ID += 1
        self.ID = Solution.last_ID
        self.routes = []
        self.cost = 0.0
        self.demand = 0.0



alpha = 0.7

instanceName = 'p5.3.q'

fileName = 'data/' + instanceName + '.txt'

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

startTime = time.time()

start = nodes[0]
finish = nodes[-1]

for node in nodes[1:-1]:
    snEdge = Edge(start, node)
    nfEdge = Edge(node, finish)

    snEdge.cost = math.sqrt((node.x - start.x)**2 + (node.y - start.y)**2)
    nfEdge.cost = math.sqrt((node.x - finish.x)**2 + (node.y - finish.y)**2)

    node.dnEdge = snEdge
    node.ndEdge = nfEdge

efficiencyList = []
for i in range(1, len(nodes)-2):
    iNode = nodes[i]
    for j in range(i+1, len(nodes)-1):
        jNode = nodes[j]
        ijEdge = Edge(iNode, jNode)
        jiEdge = Edge(jNode, iNode)
        ijEdge.invEdge = jiEdge
        jiEdge.invEdge = ijEdge

        ijEdge.cost = math.sqrt((jNode.x - iNode.x)**2 + (jNode.y - iNode.y)**2)
        jiEdge.cost = ijEdge.cost

        ijSavings = iNode.ndEdge.cost + jNode.dnEdge.cost - ijEdge.cost
        edgeReward = iNode.demand + jNode.demand
        ijEdge.savings = ijSavings
        ijEdge.efficiency = alpha * ijSavings + (1-alpha) * edgeReward
        jiSavings = jNode.ndEdge.cost + iNode.dnEdge.cost - jiEdge.cost
        jiEdge.savings = jiSavings
        jiEdge.efficiency = alpha * jiSavings + (1-alpha) * edgeReward

        efficiencyList.append(ijEdge)
        efficiencyList.append(jiEdge)

efficiencyList.sort(key = operator.attrgetter("efficiency"), reverse=True)

sol = Solution()
for node in nodes[1:-1]:
    snEdge = node.dnEdge
    nfEdge = node.ndEdge
    snfRoute = Route()
    snfRoute.edges.append(snEdge)
    snfRoute.demand += node.demand
    snfRoute.cost += snEdge.cost
    snfRoute.edges.append(nfEdge)
    snfRoute.cost += nfEdge.cost
    node.inRoute = snfRoute
    node.isLinkedToStart = True
    node.isLinkedToFinish = True
    sol.routes.append(snfRoute)
    sol.cost += snfRoute.cost
    sol.demand += snfRoute.demand

def checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge):
    if iRoute == jRoute: return False
    if iNode.isLinkedToFinish == False or jNode.isLinkedToStart == False: return False
    if routeMaxCost < iRoute.cost + jRoute.cost - ijEdge.savings: return False
    return True

while len(efficiencyList) > 0:
    index = 0
    ijEdge = efficiencyList.pop(index)

    iNode = ijEdge.origin
    jNode = ijEdge.end

    iRoute = iNode.inRoute
    jRoute = jNode.inRoute

    isMergeFeasible = checkMergingConditions(iNode, jNode, iRoute, jRoute, ijEdge)

    if isMergeFeasible == True:
        jiEdge = ijEdge.invEdge
        if jiEdge in efficiencyList: efficiencyList.remove(jiEdge)

        iEdge = iRoute.edges[-1]
        iRoute.edges.remove(iEdge)
        iRoute.cost -= iEdge.cost

        iNode.isLinkedToFinish = False

        jEdge = jRoute.edges[0]
        jRoute.edges.remove(jEdge)
        jRoute.cost -= jEdge.cost

        jNode.isLinkedToStart = False

        iRoute.edges.append(ijEdge)
        iRoute.cost += ijEdge.cost
        iRoute.demand += jNode.demand
        jNode.inRoute = iRoute

        for edge in jRoute.edges:
            iRoute.edges.append(edge)
            iRoute.cost += edge.cost
            iRoute.demand += edge.end.demand
            edge.end.inRoute = iRoute
        
        sol.cost -= ijEdge.savings
        sol.routes.remove(jRoute)

sol.routes.sort(key = operator.attrgetter("demand"), reverse=True)
for route in sol.routes[fleetSize:]:
    sol.demand -= route.demand
    sol.cost -= route.cost
    sol.routes.remove(route)

endTime = time.time()

print("Instance: ", instanceName)
print("Reward obtained with PJS heuristic sol =", "{:.{}f}".format(sol.demand, 2))
print("Computational time:","{:.{}f}".format(endTime - startTime, 2), "sec.")
for route in sol.routes:
    s = str(0)
    for edge in route.edges:
        s = s + "-" + str(edge.end.ID)
    print("Route: "+s+" || Reward = " + "{:{}f}".format(route.demand, 2) + " || Cost / Time = "+"{:{}f}".format(route.cost, 2))

G = nx.Graph()
G.add_node(start.ID, coord=(start.x, start.y))
for route in sol.routes:
    for edge in route.edges:
        G.add_edge(edge.origin.ID, edge.end.ID)
        G.add_node(edge.end.ID, coord = (edge.end.x, edge.end.y))
coord = nx.get_node_attributes(G, "coord")
nx.draw_networkx(G, coord, node_color="pink")
plt.savefig('plotgraph.png', dpi=300, bbox_inches='tight')