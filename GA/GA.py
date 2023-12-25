#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 10:29:28 2023

@author: liuchuxuan
"""
import numpy as np
import random
from gurobipy import *
import pandas as pd
import csv
import plotly.express as px
import copy
import time
import random
import numpy as np
import os
import json

# inputs
result = []

for o in [1,7,13]:
    file_name = str(o) + "a.fjs"
    orig_path = "/Users/liuchuxuan/Desktop/testing_data/"
    file_path =  orig_path + file_name 
    data = open(file_path, "r")
    machine_num = parse(file_path)[1]
    job_num = parse(file_path)[0]
    processing_time_value = parse(file_path)[3]
    operations_num = parse(file_path)[4]
    rows = 0
    for i in range(len(operations_num)):
        rows = rows + operations_num[i]
    cols = machine_num
    data = pd.DataFrame(index=range(rows), columns=range(cols))
    delta_data = pd.DataFrame(index=range(rows), columns=range(cols))
    delta_time = []
    processing_time = []
    count = 0
    for i in range(job_num):
        processing_time_single = data[count:count + operations_num[i]]
        delta_time_single = delta_data[count:count + operations_num[i]]
        count = count + operations_num[i]
        processing_time.append(processing_time_single)
        delta_time.append(delta_time_single)
        
    
    for i in range(job_num):
        for j in range(operations_num[i]):
            for w in range(machine_num):
                processing_time[i].iat[j,w] = processing_time_value[i+1,j+1,w+1]
                delta_time[i].iat[j,w] = random.uniform(-0.2, 0.2) *  processing_time_value[i+1,j+1,w+1]
    for i in range(job_num):
        delta_time[i] = processing_time[i] + delta_time[i]
    
    JS = []
    for i in range(len(operations_num)):
        for j in range(operations_num[i]):
            JS.append(i + 1)
    random.shuffle(JS)
    
    MA = []  
    for i in range(len(operations_num)):
        MA_single = []
        for j in range(operations_num[i]):
            MA_single.append(1)
        MA.append(MA_single)
    MA = assign_optimal_machine(MA,processing_time)

    final_results = dynamic_processing_time(MA,JS,processing_time,machine_num)
    result.append(final_results[0])
    

def parse(path):
	with open(os.path.join(os.getcwd(), path), "r") as data:
		total_jobs, total_machines, _ = re.findall('\S+', data.readline())
		num_jobs, num_machines, number_max_operations = int(total_jobs), int(total_machines), []

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
    
    

OS = JS
def cal_makespan(MA, OS, processing_time, machine_num):
    new_MA = []
    for m in MA: new_MA.append(m)
    num_machines = machine_num
    num_jobs = len(MA)
    schedule = {}
    machine_cur_time = [0] * num_machines
    job_cur_time = [0] * num_jobs
    job_op_id = [0] * num_jobs
    job_start_id = []
    cur_id = 0
    for o_list in MA:
        num = len(o_list)
        job_start_id.append(cur_id)
        cur_id += num

    OS_concrete = []
    op_begin = [] 
    op_end   = [] 

    for j_id in OS:
        o_id = job_op_id[j_id-1]
        m_id = new_MA[j_id-1][o_id]
        p_time = processing_time[j_id - 1].iat[o_id - 1, m_id - 1]
        if machine_cur_time[m_id-1] < job_cur_time[j_id-1]:
            schedule[(j_id, o_id, m_id)] = job_cur_time[j_id-1]
            op_begin.append( job_cur_time[j_id-1] )
            machine_cur_time[m_id-1] = job_cur_time[j_id-1] + p_time
            op_end.append( job_cur_time[j_id-1] + p_time )
        else:
            schedule[(j_id, o_id, m_id)] = machine_cur_time[m_id-1]
            op_begin.append( machine_cur_time[m_id-1] )
            machine_cur_time[m_id-1] += p_time
            op_end.append( machine_cur_time[m_id-1] + p_time )
        job_cur_time[j_id-1] = machine_cur_time[m_id-1]
        job_op_id[j_id-1] += 1

        OS_concrete.append( [j_id,  job_op_id[j_id-1] ] )

    makespan = max(job_cur_time)
    # print(f"Makespan: {makespan}")
    return makespan, op_begin, op_end, machine_cur_time, OS_concrete

  

def assign_optimal_machine(MA,processing_time):
    for i in range(len(MA)):
        for j in range(len(MA[i])):
           inner_processing_time = list(processing_time[i].iloc[j])
           machine_assigned = inner_processing_time.index(min(inner_processing_time))
           MA[i][j] = machine_assigned + 1
    return MA



def GA_for_JS(MA,JS,processing_time):
    randon_JS = []
    random_sample_makespan = []
    time_limit = 0.5
    start_time = time.time()
    for i in range(1):
        random.shuffle(JS)
        adding_js = copy.deepcopy(JS)
        randon_JS.append(adding_js)
        random_sample_makespan.append(cal_makespan(MA,JS,processing_time,machine_num)[0])
        
    random_ga = []
    for i in range(len(randon_JS)):
        random_ga.append([randon_JS[i],random_sample_makespan[i]])
    
    
    for w in range(3):
        percentage_rep = []
        percentage = []
        for i in range(len(random_sample_makespan)):
            a = 1/random_sample_makespan[i]
            b = 1/sum(random_sample_makespan)
            percentage_rep.append(a/b)
        for i in range(len(random_sample_makespan)):
            percentage.append(round(percentage_rep[i]/sum(percentage_rep),4))
        fitvalue = np.cumsum(percentage)
        random_1 = random.random()    
        random_2 = random.random()
        position_1 = -1
        position_2 = -1
        for i in range(len(fitvalue)):
            if random_1 <= fitvalue[i]:
                position_1 = i
                break
        for i in range(len(fitvalue)):
            if random_2 <= fitvalue[i]:
                position_2 = i
                break
        
        c = 5
        parent_sequence_1 = randon_JS[position_1]
        p1_part1 = parent_sequence_1[0:c]
        p1_part2 = parent_sequence_1[c:]
        parent_sequence_2 = randon_JS[position_2]
        p2_part1 = parent_sequence_2[0:c]
        p2_part2 = parent_sequence_2[c:]
        
        operations_num = []
        for i in range(len(MA)):
            operations_num.append(len(MA[i]))
        count = [0] * len(MA)
        #child1
        child1 = copy.deepcopy(p1_part1)
        for i in range(len(p1_part1)):
            count[child1[i] - 1] = count[child1[i] - 1] + 1
        for i in range(len(parent_sequence_1)):
            if (count[parent_sequence_1[i] - 1] < operations_num[parent_sequence_1[i] - 1]):
                child1.append(parent_sequence_1[i])
                count[parent_sequence_1[i] - 1] = count[parent_sequence_1[i] - 1] + 1
        #child2
        count = [0] * len(MA)
        child2 = copy.deepcopy(p2_part1)
        for i in range(len(p2_part1)):
            count[child2[i] - 1] = count[child2[i] - 1] + 1
        for i in range(len(parent_sequence_2)):
            if (count[parent_sequence_2[i] - 1] < operations_num[parent_sequence_2[i] - 1]):
                child2.append(parent_sequence_2[i])
                count[parent_sequence_2[i] - 1] = count[parent_sequence_2[i] - 1] + 1
        
        
        child1_obj = cal_makespan(MA,child1,processing_time,machine_num)[0]
        child2_obj = cal_makespan(MA,child2,processing_time,machine_num)[0]
        random_ga.append([child1,child1_obj])
        random_ga.append([child2,child2_obj])
        
        sorted_random_ga = list()
        sorted_random_ga_index = sorted(range(len(random_ga)),key=lambda i: random_ga[i][1])
        for i in range(len(sorted_random_ga_index)):
            sorted_random_ga.append(random_ga[sorted_random_ga_index[i]])
        sorted_random_ga.pop()
        sorted_random_ga.pop()
        random_ga = sorted_random_ga
        randon_JS = [i[0] for i in sorted_random_ga]
        random_sample_makespan = [i[1] for i in sorted_random_ga]
    optimal_makespan = random_sample_makespan[0]
    optimal_sequence = randon_JS[0]
    return optimal_makespan,optimal_sequence


def MA_local_search(MA,JS,processing_time):
    for i in range(len(MA)):
        MA_single_search = [[copy.deepcopy(MA),copy.deepcopy(cal_makespan(MA,JS,processing_time,machine_num)[0])]]
        for r in range(len(MA[i])):
            initial_MA = copy.deepcopy(MA[i][r])
            for j in range(machine_num):
                if (initial_MA != j + 1):
                    MA[i][r] = j + 1
                    MA_single_search.append([copy.deepcopy(MA),copy.deepcopy(cal_makespan(MA,JS,processing_time,machine_num)[0])])
                local_search_sort_index = sorted(range(len(MA_single_search)),
                                        key=lambda i: (MA_single_search[i][1]))
            MA = copy.deepcopy(MA_single_search[local_search_sort_index[0]][0])
            optimal_MA_obj = MA_single_search[local_search_sort_index[0]][1]
    return optimal_MA_obj,MA





result = []
for i in range(20):
    static_result = MA_local_search(MA,GA_for_JS(MA,JS,processing_time)[1],processing_time)
    result.append(static_result[0])
    
avg(result)


def dynamic_processing_time(MA,JS,processing_time,machine_num):
    JS = GA_for_JS(MA,JS,processing_time)[1]
    optimal_obj = MA_local_search(MA,GA_for_JS(MA,JS,processing_time)[1],processing_time)[0]
    MA = MA_local_search(MA,GA_for_JS(MA,JS,processing_time)[1],processing_time)[1]
    JS_after_GA_concrete = cal_makespan(MA,JS,processing_time,machine_num)[4]
    operation_start_time = cal_makespan(MA,JS,processing_time,machine_num)[1]
    for i in range(optimal_obj):
        for j in range(len(operation_start_time)):
            if (i == operation_start_time[j]):
                job_num = JS_after_GA_concrete[j][0]
                operation_num = JS_after_GA_concrete[j][1]
                machine_num_t = MA[job_num - 1][operation_num - 1]
                processing_time[job_num - 1].iat[operation_num - 1,machine_num_t - 1] =  delta_time[job_num - 1].iat[operation_num - 1,machine_num_t - 1]
                JS = GA_for_JS(MA,JS,processing_time)[1]
                optimal_obj = MA_local_search(MA,GA_for_JS(MA,JS,processing_time)[1],processing_time)[0]
                MA = MA_local_search(MA,GA_for_JS(MA,JS,processing_time)[1],processing_time)[1]
                JS_after_GA_concrete = cal_makespan(MA,JS,processing_time,machine_num)[4]
                operation_start_time = cal_makespan(MA,JS,processing_time,machine_num)[1]
                break
    return optimal_obj, JS, MA
        
final_results = dynamic_processing_time(MA,JS,processing_time,machine_num)
final_results[0]
final_results[1]
final_results[2]


    
    
    









