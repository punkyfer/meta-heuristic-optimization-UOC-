
import operator
import time

class Job:
    def __init__(self, id, processing_times, total_processing_time):
        self.id = id
        self.processing_times = processing_times
        self.total_processing_time = total_processing_time

class Solution:

    last_id = -1

    def __init__(self, num_jobs, num_machines):
        Solution.last_id += 1
        self.id = Solution.last_id
        self.num_jobs = num_jobs
        self.num_machines = num_machines
        self.jobs = []
        self.makespan = 0.0

    def compute_makespan(self):
        num_rows = self.num_jobs
        num_cols = self.num_machines
        times = [[0 for j in range(num_cols)] for i in range(num_rows)]
        for column in range(num_cols):
            for row in range(num_rows):
                if column == 0 and row == 0:
                    times[0][0] = self.jobs[0].processing_times[0]
                elif column == 0:
                    times[row][0] = times[row -1][0] + self.jobs[row].processing_times[0]
                elif row == 0:
                    times[0][column] = times[0][column-1] + self.jobs[0].processing_times[column]
                else:
                    max_time = max(times[row-1][column], times[row][column-1])
                    times[row][column] = max_time + self.jobs[row].processing_times[column]
        return times[num_rows-1][num_cols-1]
    
def compute_e_matrix(sol, k):
    num_rows = k
    num_cols = sol.num_machines
    e = [[0 for j in range(num_cols)] for i in range(num_rows)]
    for i in range(k):
        for j in range(sol.num_machines):
            if i == 0 and j == 0: e[i][j] = sol.jobs[i].processing_times[j]
            elif j == 0: e[i][j] = e[i-1][j] + sol.jobs[i].processing_times[j]
            elif i == 0: e[i][j] = e[i][j-1] + sol.jobs[i].processing_times[j]
            else:
                max_time = max(e[i-1][j], e[i][j-1])
                e[i][j] = max_time + sol.jobs[i].processing_times[j]
    return e

def compute_q_matrix(sol, k):
    num_rows = k+1
    num_cols = sol.num_machines
    q = [[0 for j in range(num_cols)] for i in range(num_rows)]
    for i in range(k, -1, -1):
        for j in range(sol.num_machines-1, -1, -1):
            if i == k: 
                q[k][j] = 0
            elif i == k-1 and j == sol.num_machines-1:
                q[i][j] = sol.jobs[i].processing_times[j]
            elif j == sol.num_machines-1:
                q[i][j] = q[i+1][j] + sol.jobs[i].processing_times[j]
            elif i == k - 1:
                q[i][j] = q[i][j+1] + sol.jobs[i].processing_times[j]
            else:
                max_time = max(q[i+1][j], q[i][j+1])
                q[i][j] = max_time + sol.jobs[i].processing_times[j]
    return q

def compute_f_matrix(sol, k, e):
    num_rows = k+1
    num_cols = sol.num_machines
    f = [[0 for j in range(num_cols)] for i in range(num_rows)]
    for i in range(k+1):
        for j in range(sol.num_machines):
            if i == 0 and j == 0:
                f[i][j] = sol.jobs[k].processing_times[0]
            elif j == 0:
                f[i][j] = e[i-1][j] + sol.jobs[k].processing_times[j]
            elif i == 0:
                f[i][j] = f[i][j-1] + sol.jobs[k].processing_times[j]
            else:
                max_time = max(e[i-1][j], f[i][j-1])
                f[i][j] = max_time + sol.jobs[k].processing_times[j]
    return f

    
def improve_by_shifting_job_to_left(sol, k):
    best_position = k
    min_makespan = float("inf")
    e_matrix = compute_e_matrix(sol, k)
    q_matrix = compute_q_matrix(sol, k)
    f_matrix = compute_f_matrix(sol, k, e_matrix)

    for i in range(k, -1, -1):
        max_sum = 0.0
        for j in range(sol.num_machines):
            new_sum = f_matrix[i][j] + q_matrix[i][j]
            if new_sum > max_sum: 
                max_sum = new_sum
        new_makespan = max_sum

        if new_makespan <= min_makespan:
            min_makespan = new_makespan
            best_position = i

    if best_position < k:
        aux_job = sol.jobs[k]
        for i in range(k, best_position, -1):
            sol.jobs[i] = sol.jobs[i-1]
        sol.jobs[best_position] = aux_job

    if k == sol.num_jobs - 1:
        sol.makespan = min_makespan

    return sol

        

if __name__ == "__main__":

    instance_name = "tai117_500_20"
    #instance_name = "tai109_200_20"
    #instance_name = "tai084_100_20"
    #instance_name = "tai044_50_10"

    file_name = "pfsp_data/"+instance_name+"_inputs.txt"

    with open(file_name) as instance:
        i = -3
        jobs = []
        for line in instance:
            if i == -3: pass
            elif i == -2:
                num_jobs = int(line.split()[0])
                num_machines = int(line.split()[1])
            elif i == -1: pass
            else:
                data = [float(x) for x in line.split("\t")]
                total_processing_time = sum(data)
                job = Job(i, data, total_processing_time)
                jobs.append(job)
            i += 1

    t_start = time.time()

    jobs.sort(key = operator.attrgetter('total_processing_time'), reverse=True)
    sol = Solution(num_jobs, num_machines)
    index = 0 # Greedy
    sol.jobs.append(jobs[index])

    for i in range(1, num_jobs):
        index = i
        sol.jobs.append(jobs[index])
        sol = improve_by_shifting_job_to_left(sol, i)

    t_end = time.time()

    print("Instance: "+instance_name+" with "+str(num_jobs)+" jobs and "+str(num_machines)+" machines")
    print("NEH makespan with Taillard acceleration =", "{:.{}f}".format(sol.makespan, 2))
    print("NEH verification with traditional method:", "{:.{}f}".format(sol.compute_makespan(), 2))
    print("Computational time:", "{:.{}f}".format(t_end-t_start, 1), "sec.")
    permutation = "( "
    for job in jobs:
        permutation = permutation + str(job.id) + " "
    permutation = permutation + ")"
    print("Sol:", permutation)
