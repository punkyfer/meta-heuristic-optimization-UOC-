import time
import random

def basin_function_1(x):
    a = 0.5
    h = 2
    k = -5
    return sum([a*((x_i-h)**2)+k for x_i in x])


def basin_function_2(x):
    return sum([x_i**2 for x_i in x])


def random_search(basin_function, searchSpace, problemSize, maxIterations = 100000):
    bestCost = float("inf")
    bestSol = [0, 0]
    num_iters = 0
    while num_iters < maxIterations:
        num_iters += 1
        x = [random.uniform(searchSpace[0], searchSpace[1]) for i in range(problemSize)]
        cost = basin_function(x)
        if cost < bestCost:
            bestCost = cost
            bestSol = x
    return bestCost, bestSol


if __name__ == "__main__":
    print("Random Search Algorithm")
    print("---------------------------------------------------------")
    print("Basin Function: f(x) = sum(a(x_i - h)² + k) for i=1,...,n")
    searchSpace = [-5, 5]
    problemSize = 2
    start = time.time()
    cost, sol = random_search(basin_function_1, searchSpace, problemSize)
    end = time.time()
    print(f"Cost = {cost} \nSolution = {sol} \nTime taken = {end-start}")
    print("---------------------------------------------------------")
    print("Basin Function: f(x) = sum(x_i²) for i=1,...,n")
    searchSpace = [-5, 5]
    problemSize = 2
    start = time.time()
    cost, sol = random_search(basin_function_2, searchSpace, problemSize)
    end = time.time()
    print(f"Cost = {cost} \nSolution = {sol} \nTime taken = {end-start}")