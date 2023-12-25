from abc_scheduler import *
from visualizer import draw_flat_schedule
from parse import parse
import sys
import timeit
import warnings
import statistics


warnings.simplefilter('ignore', RuntimeWarning)

path = sys.argv[1]
num_jobs, num_machines, number_max_operations, jobOpMachine_to_time, job_to_opnum = parse(path)
# exit(1)
print(f"Running Benchmark {path}...")
print("Scheduler launched with the following parameters:")
print('\t', num_jobs, "jobs")
print('\t', num_machines, "machine(s)")
# print("\n")


time_delta = float(sys.argv[2]) # processing time variation

start = timeit.default_timer()

# use_abc = True
filename = "schedule.png"
avg_makespan = 0.0
num_iter = 1
makespan_list = []
for _ in range(num_iter):
    s = AbcScheduler(jobOpMachine_to_time, job_to_opnum, num_machines, num_jobs)
    s.optimize(1000, 500)
    # s.dynamic_optimize(100, 20, time_delta)
    # draw_flat_schedule(s.best_schedule, jobOpMachine_to_time, num_jobs, num_machines, filename)
    avg_makespan += s.best_makespan
    makespan_list.append(s.best_makespan)
    # print(f"Makespan {s.best_makespan}")

# avg_makespan /= num_iter 

print(f"Avg Makespan = { statistics.mean(makespan_list) }")
print(f"Standard Deviation = { statistics.stdev(makespan_list) }")

stop = timeit.default_timer()
print("Finished in " + str(stop - start) + " seconds.")

# del s
# del temp_jobs_list, temp_machines_list