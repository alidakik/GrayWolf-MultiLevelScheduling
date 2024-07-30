import numpy as np
import random
import matplotlib.pyplot as plt

# a class to represent a process with attributes like ID,
# arrival time, remaining time, and priority.
class Process:
    def __init__(self, id, arrival_time, remaining_time, priority):
        self.id = id
        self.priority = priority
        self.remaining_time = remaining_time
        self.arrival_time = arrival_time

    def __str__(self):
        return f'Process {self.id} - Priority: {self.priority} - Remaining Time: {self.remaining_time} - Arrival Time: {self.arrival_time}'


# Parameters for the simulation
num_wolves = 5
num_queues = 5 
max_iter = 15
lower_bound = 1   
upper_bound = 100  

# generate the a random position to a single wolve
# and make sure that the position sum don't accross the upper_bound
# the upper bound the processor scheduling time 
# thats mean that we are scheduling the processor for upper_bound time
def random_position(size, lower_bound, upper_bound):

    random_ints = np.random.randint(lower_bound, upper_bound, size)
    
    # Adjust the sum to match the upper bound
    current_sum = np.sum(random_ints)
    while current_sum != upper_bound:
        if current_sum < upper_bound:
            # Randomly add to elements until the sum is the upper bound
            indices_to_add = np.random.choice(size, (upper_bound - current_sum), replace=True)
            for i in indices_to_add:
                if random_ints[i] < upper_bound - 1:
                    random_ints[i] += 1
                    current_sum += 1
        else:
            # Randomly subtract from elements until the sum is the upper bound
            indices_to_subtract = np.random.choice(size, (current_sum - upper_bound), replace=True)
            for i in indices_to_subtract:
                if random_ints[i] > lower_bound:
                    random_ints[i] -= 1
                    current_sum -= 1
    
    return np.array(random_ints)



# initialize the positions of the wolves based on the random_position function
def init_posistions(num_wolves, num_queues, lower_bound, upper_bound):
    positions = []
    for i in range(num_wolves):
        array = random_position(num_queues, lower_bound, upper_bound)
        positions.append(array)
        
    return np.array(positions)


# normilize a position so its some don't accross the upper bound
def normilize_position(values,upper_bound):
    current_sum = sum(values)
    required_total = upper_bound
    difference = required_total - current_sum
    
    num_items = len(values)
    
    addition_per_item = difference // num_items
    remainder = difference % num_items
    
    
    adjusted_values = [x + addition_per_item for x in values]
    
    for i in range(int(remainder)):
        adjusted_values[i] += (1 if difference > 0 else -1)

    return adjusted_values




# this function calculate the fitness of a specific position
# the fitness is calculated based on the waiting time of the processes
# and the priority of the process
def fitness_function(num_queues, processes,position):
    score = 0
    for i in range(1,num_queues+1):
        queue_processes = processes[i]
        
        waiting_time = 0
        queue_score = 0
        porsition_temp = position[i-1]
        task_flag = 0
        for j in range(len(queue_processes)):

            # for each processes in queue check if the queue still have time to run the process
            # and the process has been arrived and lastlu the process still have time to run
            if porsition_temp - queue_processes[j].remaining_time > 0 \
                and queue_processes[j].arrival_time <= waiting_time \
                and queue_processes[j].remaining_time > 0:
                    
                #queue_processes[i].remaining_time = 0
                queue_score += waiting_time - queue_processes[j].arrival_time
                waiting_time += queue_processes[j].remaining_time
                porsition_temp -= queue_processes[j].remaining_time
                
            else:
                task_flag=1
                break
        # apply the score for the queue
        if queue_score == 0 and task_flag:
            score += 15*(num_queues-i+1)
        score += queue_score*(num_queues-i+1) 
        
    return score


# the main funtion for the grey wolf optimization
# the function will return the best score and the best position
def GWO(max_iter, num_wolves, num_queues, processes):
    fitness_history = []
    
    
    # initialize the pack of wolves
    alpha_pos = np.zeros(num_queues)
    beta_pos = np.zeros(num_queues)
    delta_pos = np.zeros(num_queues)
    alpha_score = float('inf')
    beta_score = float('inf')
    delta_score = float('inf')
        
    positions = init_posistions(num_wolves, num_queues, lower_bound, upper_bound)
    #positions = np.random.uniform(low=lower_bound, high=upper_bound, size=(num_wolves, num_queues))



    for iteration in range(max_iter):
        for i in range(num_wolves):
            # calculate the fitness of the current position
            fitness = fitness_function(num_queues, processes, positions[i])
            
            # update the alpha, beta, and delta positions
            if fitness < alpha_score:
                if beta_score == float('inf'):
                    beta_pos = alpha_pos
                    beta_score = alpha_score
                    if delta_score == float('inf'):
                        delta_score = beta_score
                        delta_pos = beta_pos
                alpha_score = fitness
                alpha_pos = positions[i]
                
            if fitness > alpha_score and fitness < beta_score:
                if delta_score == float('inf'):
                    delta_score = beta_score
                    delta_pos = beta_pos
                beta_score = fitness
                beta_pos = positions[i]
            
            if fitness > alpha_score and fitness > beta_score and fitness < delta_score:
                delta_score = fitness
                delta_pos = positions[i]
        
        
        # update the positions of the wolves
        a = 2 - iteration * (2 / max_iter) # a is the linearly dicreasing value from 2 to 0
        
        # update the positions of the wolves based on the alpha, beta, and delta positions
        # run the equation for each wolf
        for i in range(num_wolves):
        
            r1 = random.random()
            r2 = random.random()
            
            A1 = 2 * a * r1 - a
            C1 = 2 * r2
            
            D_alpha = abs(C1 * alpha_pos - positions[i])
            X1 = abs(alpha_pos - A1 * D_alpha)
            
            r1 = random.random()
            r2 = random.random()
            
            A2 = 2 * a * r1 - a
            C2 = 2 * r2
            
            D_beta = abs(C2 * beta_pos - positions[i])
            X2 = abs(beta_pos - A2 * D_beta)
            
            r1 = random.random()
            r2 = random.random()
            
            A3 = 2 * a * r1 - a
            C3 = 2 * r2
            
            D_delta = abs(C3 * delta_pos - positions[i])
            X3 = abs(delta_pos - A3 * D_delta)
            
            positions[i] = normilize_position((X1 + X2 + X3) / 3,upper_bound)
            
        print(f'Iteration {iteration} - Best fitness: {alpha_score}')
        fitness_history.append(alpha_score)
    return alpha_score, alpha_pos, fitness_history



# input processes
# define processes 
process1 = Process(id=1, arrival_time=0, remaining_time=10, priority=1)
process2 = Process(id=2, arrival_time=0, remaining_time=5, priority=2)
process3 = Process(id=3, arrival_time=0, remaining_time=2, priority=3)
process4 = Process(id=4, arrival_time=0, remaining_time=4, priority=4)
process5 = Process(id=5, arrival_time=0, remaining_time=6, priority=5)
process6 = Process(id=6, arrival_time=0, remaining_time=8, priority=1)
process7 = Process(id=7, arrival_time=2, remaining_time=3, priority=1)
process8 = Process(id=8, arrival_time=2, remaining_time=6, priority=2)
process9 = Process(id=9, arrival_time=1, remaining_time=2, priority=3)
process10 = Process(id=10, arrival_time=1, remaining_time=4, priority=4)
process11 = Process(id=11, arrival_time=2, remaining_time=6, priority=5)
process12 = Process(id=12, arrival_time=3, remaining_time=8, priority=1)
process13 = Process(id=13, arrival_time=2, remaining_time=3, priority=2)


processes_list = [process1, process2, process3, process4,
                  process5, process6, process7, process8,
                  process9, process10, process11, process12, process13]
processes = {}

for i in range(1, num_queues+1):
    processes[i] = [process for process in processes_list if process.priority == i]
    processes[i] = sorted(processes[i], key=lambda x: x.arrival_time)
    


# run the algorith    
alpha_score, alpha_position, fitness_history = GWO(max_iter, num_wolves, num_queues, processes)

# plot the programming langauge
plt.figure(figsize=(10, 5))
plt.plot(fitness_history, label='Fitness over Iterations')
plt.xlabel('Iteration')
plt.ylabel('Fitness')
plt.title('Fitness over Iterations for GWO')
plt.legend()
plt.grid(True)
plt.show()
