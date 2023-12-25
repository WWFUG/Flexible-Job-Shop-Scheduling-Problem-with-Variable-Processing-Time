

import os
import re
import math
import random


def parse(path):
	with open(os.path.join(os.getcwd(), path), "r") as data:
		total_jobs, total_machines, _ = re.findall('\S+', data.readline())
		num_jobs, num_machines, number_max_operations = int(total_jobs), int(total_machines), 1

		id_job = 1
  
		jobOpMachine_to_time = {}
     
		job_to_opnum = [0] * num_jobs

		max_operations = 0
		min_time, max_time = math.inf, 0
		for key, line in enumerate(data):
			if key >= num_jobs:
				break
			# Split data with multiple spaces as separator
			parsed_line = re.findall('\S+', line)
			# print(parsed_line)
			# Current activity's id
			id_activity = 1
			# Current item of the parsed line
			i = 1

			while i < len(parsed_line):
				# Total number of operations for the activity
				number_operations = int(parsed_line[i])
				# print(f"Job: {id_job}")
				# Current activity
				for id_operation in range(1, number_operations + 1):
					machine_id = int(parsed_line[i + 2 * id_operation - 1])
					processing_time = int(parsed_line[i + 2 * id_operation])
					min_time = min(min_time, processing_time)
					max_time = max(max_time, processing_time)
					jobOpMachine_to_time[ (id_job, id_activity, machine_id) ] = processing_time

				i += 1 + 2 * number_operations
				id_activity += 1
	
			max_operations = max(id_activity-1, max_operations)
    
			job_to_opnum[id_job-1] = id_activity-1
   
			id_job += 1

	# print(min_time, max_time)

	# for i in range(1, num_jobs+1):
	# 	for j in range(1, max_operations+1):
	# 		for k in range(1, num_machines+1):
	# 			if not( (i, j, k) in jobOpMachine_to_time): 
	# 				# jobOpMachine_to_time[(i, j, k)] = 10000
	#  				jobOpMachine_to_time[(i, j, k)] = random.randint(min_time, max_time)
     
	# # generate newly filled instances
	# with open(os.path.join(os.getcwd(),path) + ".new", "w") as o_file:
	# 	o_file.write(f"{num_jobs} {num_machines} {1}\n")
	# 	for i in range(num_jobs):
	# 		num_ops = job_to_opnum[i]
	# 		o_file.write(f"{num_ops} ")
	# 		for j in range(num_ops):
	# 			o_file.write(f"{num_machines} ")
	# 			for k in range(num_machines):
	# 				o_file.write(f"{k+1} {jobOpMachine_to_time[ (i+1, j+1, k+1) ]} ")
	# 		o_file.write("\n")
	return  num_jobs, num_machines, number_max_operations, jobOpMachine_to_time, job_to_opnum