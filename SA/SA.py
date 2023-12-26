import random as rand
import numpy as np
import math
import pandas as pd
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from tqdm import tqdm
from statistics import mean 
import timeit
import os
import re

def parse(path):
	with open(os.path.join(os.getcwd(), path), "r") as data:
		total_jobs, total_machines, _ = re.findall('\S+', data.readline())
		num_jobs, num_machines, number_max_operations = int(total_jobs), int(total_machines), 1
		id_job = 1
		jobOpMachine_to_time = {}
		job_to_opnum = [0] * num_jobs
		max_operations = 0
		for key, line in enumerate(data):
			if key >= num_jobs:
				break
			# Split data with multiple spaces as separator
			parsed_line = re.findall('\S+', line)
			# Current activity's id
			id_activity = 1
			# Current item of the parsed line
			i = 1
			while i < len(parsed_line):
				# Total number of operations for the activity
				number_operations = int(parsed_line[i])
				# Current activity
				for id_operation in range(1, number_operations + 1):
					machine_id = int(parsed_line[i + 2 * id_operation - 1])
					processing_time = int(parsed_line[i + 2 * id_operation])
					jobOpMachine_to_time[ (id_job, id_activity, machine_id) ] = processing_time
				i += 1 + 2 * number_operations
				id_activity += 1
			max_operations = max(id_activity-1, max_operations)
			job_to_opnum[id_job-1] = id_activity-1
			id_job += 1
	for i in range(1, num_jobs+1):
		for j in range(1, max_operations+1):
			for k in range(1, num_machines+1):
				if not( (i, j, k) in jobOpMachine_to_time):
					jobOpMachine_to_time[(i, j, k)] = 10000
	# print(jobOpMachine_to_time)
	return  num_jobs, num_machines, number_max_operations, jobOpMachine_to_time, job_to_opnum

class SA_Scheduling(object):
    def __init__(self, num_machines, num_jobs, num_operations, processing_times, delta=0.1):
        self.num_machines = num_machines
        self.num_jobs = num_jobs
        self.num_operations = num_operations
        self.processing_times = copy.deepcopy(processing_times)
        self.delta = delta
        self.var_processing_times = copy.deepcopy(processing_times)
        self.MA = []
        self.OS = []
        self.makespan = 0
        self.schedule = {}

        self.machine_start_jo = [[] for _ in range(num_machines)]
        self.job_finished_op = [0] * num_jobs
        self.best_schedule = {}
    
    def init_MA(self):
        self.MA = []
        machine_workload = [0] * self.num_machines
        for j_id in range(self.num_jobs):
            num_op = self.num_operations[j_id]
            for o_id in range(num_op):
                best_m_id, min_p_time = 0, 10000
                for m_id in range(self.num_machines):
                    p_time = self.var_processing_times[(j_id+1, o_id+1, m_id+1)]
                    if machine_workload[m_id] + p_time < min_p_time:  # Find the machine with minimum workload for this operation
                        best_m_id = m_id
                        min_p_time = machine_workload[m_id] + p_time
                machine_workload[best_m_id] += min_p_time
                self.MA.append(best_m_id)
        self.MA = self.revise_MA(self.MA)
        # print(f"Init MA: {self.MA}")
    
    def init_OS(self):
        self.OS = []
        for j_id in range(self.num_jobs):
            num_op = self.num_operations[j_id]
            for _ in range(num_op):
                self.OS.append(j_id)
        rand.shuffle(self.OS)
        self.OS = self.revise_OS(self.OS)
        # print(f"Init OS: {self.OS}")
    
    def simulated_annealing_OS(self, temperature=600, min_temperature=0.1, cooling_rate=0.95, iterations=40):
        current_OS = copy.deepcopy(self.OS)
        best_OS = copy.deepcopy(current_OS)
        # print("Initial makespan {}".format(self.evaluation(self.MA, best_OS)))
        while True:
            if temperature <= min_temperature:
                break
            for _ in range(iterations):
                neighbor_OS = copy.deepcopy(current_OS)
                swap_indices = rand.sample(range(sum(self.num_operations)), 2)
                neighbor_OS[swap_indices[0]], neighbor_OS[swap_indices[1]] = neighbor_OS[swap_indices[1]], neighbor_OS[swap_indices[0]]
                neighbor_OS = self.revise_OS(neighbor_OS)
                diff_makespan = self.evaluation(self.MA, neighbor_OS) - self.evaluation(self.MA, current_OS)
                if diff_makespan < 0 or rand.uniform(0, 1) < math.exp(-diff_makespan / temperature):
                    current_OS = copy.deepcopy(neighbor_OS)
                    if self.evaluation(self.MA, current_OS) < self.evaluation(self.MA, best_OS):
                        best_OS = copy.deepcopy(current_OS)
                        # print("Update best makespan : {}".format(self.evaluation(self.MA, best_OS)))
            temperature *= cooling_rate
        self.OS = copy.deepcopy(best_OS)
    
    def optimize_MA(self):
        best_makespan = self.evaluation(self.MA, self.OS)
        # print("Initial makespan {}".format(best_makespan))
        for i in range(sum(self.num_operations)):
            for m_id in range(self.num_machines):
                if m_id == self.MA[i]:
                    continue
                orig_m_id = self.MA[i]
                self.MA[i] = m_id
                self.MA = self.revise_MA(self.MA)
                new_makespan = self.evaluation(self.MA, self.OS)
                if new_makespan < best_makespan:
                    best_makespan = new_makespan
                    # print("Update best makespan : {}".format(best_makespan))
                else:
                    self.MA[i] = orig_m_id
    
    def revise_MA(self, MA):
        job_start_id = []
        cur_id = 0
        for num in self.num_operations:
            job_start_id.append(cur_id)
            cur_id += num
        for m_id, jo_list in enumerate(self.machine_start_jo):
            for jo in jo_list:
                j_id, o_id = jo
                MA[job_start_id[j_id] + o_id] = m_id
        return MA
    
    def revise_OS(self, OS):
        prefix_OS = []
        # print(self.machine_start_jo)
        for m_id, jo_list in enumerate(self.machine_start_jo):
            for jo in jo_list:
                j_id, o_id = jo
                prefix_OS.append(j_id)
        for j_id, finished_count in enumerate(self.job_finished_op):
            for _ in range(finished_count):
                OS.remove(j_id)
        OS = prefix_OS + OS
        return OS
    
    def evaluation(self, MA, OS):
        self.schedule = {}
        machine_cur_time = [0] * self.num_machines
        job_cur_time = [0] * self.num_jobs
        job_op_id = [0] * self.num_jobs
        job_start_id = []
        cur_id = 0
        for num in self.num_operations:
            job_start_id.append(cur_id)
            cur_id += num
        for j_id in OS:
            o_id = job_op_id[j_id]
            m_id = MA[job_start_id[j_id] + o_id]
            p_time = self.var_processing_times[(j_id+1, o_id+1, m_id+1)]
            if machine_cur_time[m_id] < job_cur_time[j_id]:
                self.schedule[(j_id+1, o_id+1, m_id+1)] = job_cur_time[j_id]
                machine_cur_time[m_id] = job_cur_time[j_id] + p_time
            else:
                self.schedule[(j_id+1, o_id+1, m_id+1)] = machine_cur_time[m_id]
                machine_cur_time[m_id] += p_time
            job_cur_time[j_id] = machine_cur_time[m_id]
            job_op_id[j_id] += 1     
        makespan = max(job_cur_time)
        # print(f"Makespan: {makespan}")
        return makespan

    def adjust_val(self):
        self.MA = [val + 1 for val in self.MA]
        self.OS = [val + 1 for val in self.OS]

    def gantt_chart(self, schedule):
        vertical_space = 1
        vertical_height = 2
        colors = ['#%06X' % rand.randint(0, 256 ** 3 - 1) for _ in range(self.num_jobs)]
        plt.clf()
        plot = plt.subplot()
        for jom, time in schedule.items():
            j_id, o_id, m_id = jom
            p_time = self.var_processing_times[(j_id, o_id, m_id)]
            x, y = time, 1 + m_id * (vertical_space + vertical_height)
            plot.add_patch(patches.Rectangle((x, y), p_time - 0.05, vertical_height, facecolor=colors[j_id - 1]))
        plt.yticks([1 + (i + 1) * (vertical_space + vertical_height) + (vertical_height + vertical_space - vertical_space) / 2 
                    for i in range(self.num_machines)], ["machine " + str(i + 1) for i in range(self.num_machines)])
        plot.autoscale()
        handles = []
        for j_id, color in enumerate(colors):
            handles.append(patches.Patch(color=color, label='job ' + str(j_id + 1)))
        plt.legend(handles=handles)
        plt.show()
        # plt.savefig(os.path.join("output", filename), bbox_inches='tight')
    
    def pipeline(self):
        self.init_MA()
        self.init_OS()
        self.simulated_annealing_OS()
        self.optimize_MA()
        self.makespan = self.evaluation(self.MA, self.OS)
        self.adjust_val()
    
    def optimize(self):
        self.init_MA()
        self.init_OS()
        self.simulated_annealing_OS()
        self.optimize_MA()
        self.makespan = self.evaluation(self.MA, self.OS)

    def dynamic_scheduling(self):
        self.optimize()
        job_done = [False] * self.num_jobs
        while True:
            for jom, start_time in self.best_schedule.items():
                self.schedule.pop(jom)
            checkpoint = min(self.schedule.values())
            for jom, start_time in self.schedule.items():
                j_id, o_id, m_id = jom
                if start_time == checkpoint:
                    # print(self.best_schedule)
                    self.best_schedule[jom] = start_time
                    self.machine_start_jo[m_id-1].append((j_id-1, o_id-1))
                    self.job_finished_op[j_id-1] += 1
                    if self.job_finished_op[j_id-1] == self.num_operations[j_id-1]:
                        job_done[j_id-1] = True
            if all(job_done):
                print("Finish dynamic scheduling!")
                break    
            for jom, time in self.processing_times.items():
                self.var_processing_times[jom] = rand.uniform((1-self.delta) * time, (1+self.delta) * time)
            self.optimize()
        self.makespan = self.evaluation(self.MA, self.OS)
        self.adjust_val()
    
    def dynamic_scheduling_ver2(self):
        self.optimize()
        MAX_SPAN = 3
        job_done = [False] * self.num_jobs
        for t in tqdm(range(MAX_SPAN)):
            for jom, start_time in self.schedule.items():
                j_id, o_id, m_id = jom
                if start_time == t:
                    # print(self.best_schedule)
                    self.best_schedule[jom] = start_time
                    self.machine_start_jo[m_id-1].append((j_id-1, o_id-1))
                    self.job_finished_op[j_id-1] += 1
                    if self.job_finished_op[j_id-1] == self.num_operations[j_id-1]:
                        job_done[j_id-1] = True
            if all(job_done):
                print("Finish dynamic scheduling!")
                break    
            for jom, time in self.processing_times.items():
                self.var_processing_times[jom] = rand.uniform((1-self.delta) * time, (1+self.delta) * time)
            self.optimize()
        self.makespan = self.evaluation(self.MA, self.OS)
        self.adjust_val()

file_path = f''
num_jobs, num_machines, number_max_operations, processing_times, num_operations = parse(file_path)

makespan_list = []
time_list = []
iteration = 20
for _ in tqdm(range(iteration)):
    start_time = timeit.default_timer()
    scheduler = SA_Scheduling(num_machines, num_jobs, num_operations, processing_times)
    scheduler.optimize()
    end_time = timeit.default_timer()
    makespan_list.append(scheduler.makespan)
    time_list.append(end_time - start_time)
print(f"Mean makespan: {mean(makespan_list)}")
print(f"Mean running time: {mean(time_list)}")