import random
import os

# schedule		: a dict with key (job_id, op_id, machine_id) and value (start time)
# jom_to_time	: a dict with key (job_id, op_id, machine_id) and value (processing time)
# num_job		: number of total jobs
# num_machine 	: number of total machines
# filename		: the schedule will be exported as a PNG file with path [output/[filename]] 

def draw_flat_schedule(schedule, jom_to_time, num_job, num_machine, filename):
	import matplotlib.pyplot as plt
	import matplotlib.patches as patches

	# Vertical space between operation
	vertical_space = 1
	# Vertical height of an operation
	vertical_height = 2


	# Dictionary of the operations done, the key correspond to the machine id

	# Define random colors for jobs
	colors = ['#%06X' % random.randint(0, 256 ** 3 - 1) for _ in range( num_job )]

	# Draw
	plt.clf()
	plot = plt.subplot()

	for jom, time in schedule.items():
		j_id, op_id, m_id = jom
		duration = jom_to_time[jom]
		x, y = time, 1 + m_id * (vertical_space + vertical_height)
		plot.add_patch(
				patches.Rectangle(
					(x, y),
					duration - 0.05,
					vertical_height,
					facecolor=colors[j_id - 1]
				)
			)

	plt.yticks([1 + (i + 1) * (vertical_space + vertical_height) + (vertical_height + vertical_space - vertical_space) / 2 
			for i in range(num_machine)], ["machine " + str(i + 1) for i in range(num_machine)])

	plot.autoscale()

	# Display a rectangle with the color and the job's id as the x-axis legend
	handles = []
	for id_job, color in enumerate(colors):
		handles.append(patches.Patch(color=color, label='job ' + str(id_job + 1)))
	plt.legend(handles=handles)

	# Show the schedule order
	plt.show()
	# Saving the scheduler order
	if not (filename is None):
		plt.savefig(os.path.join("output", filename), bbox_inches='tight')