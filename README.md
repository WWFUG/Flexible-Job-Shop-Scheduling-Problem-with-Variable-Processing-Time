# Flexible Job Shop Scheduling Problem with Variable Processing Time

## Abstract

In real scheduling problems, unexpected changes may occur frequently such as changes in task features. These changes cause deviation from primary scheduling. 
In our report,  three heuristic models, inspired from Artificial Bee Colony algorithm, Genetic algorithm and Simulated Annealing algorithm are proposed for a dynamic flexible job-shop scheduling (DFJSP) problem. This problem consists of n jobs that should be processed by m machines and the processing time of jobs deviates from estimated times. The objective is near-optimal scheduling after any change in tasks in order to minimize the maximal completion time (Makespan). In the proposed model, first, scheduling is done according to the estimated processing times and then re-scheduling is performed after determining the exact ones considering machine set-up. In order to evaluate the performance of the proposed models, some numerical experiments are designed in small, medium and large sizes in different levels of changes in processing times and statistical results illustrate the efficiency of the proposed algorithms.	

## Introduction and Problem Settings

In a flexible job scheduling problem (FJSP), there are multiple stages and multiple machines. In this optimization problem, each job consists of some related operations, thus we need to consider two sub-problems: machine assignment and operation sequence problem. Machine assignment problem allocates an operation to one of the available machines. Operation sequence problem determines the order of all operations on machines considering their relations in order to obtain a feasible and optimal solution.

Below is a simple example of our FJSP problem, there are four jobs, job1 has 3 operations, job 2 has 2 operations, job 3 has 3 operations, job 4 has 2 operations. There are 5 machines. We have two sequence: MA (machine assignment) and JS (job sequence). For instance, in Figure 1, the above sequence represents the machine assignment of each operations, the below represents the job sequence. In figure 2, the Gantt chart is used to show the result of the example.


![image](https://hackmd.io/_uploads/r10hMMDDa.png)


<!-- ![image](https://hackmd.io/_uploads/H1qiMzPwT.png) -->


<!-- ![image](https://hackmd.io/_uploads/rJNvpS8DT.png)
*Figure 1.*

![image](https://hackmd.io/_uploads/H16AprUvp.png)
*Figure 2.* -->


In real world problems, the processing time of each operations may be changed due to the nature of the production process, machine set-up, etc. In order to prepare the production planning for the total process, we have to consider the estimated times and update the actual times after machine’s setting. Thus, we let the processing time vary in a range with respect to the current processing time. The variation of processing time may be positive or negative. For instance, if the magnitude of change is 0.25, then the processing time after variation equals the current processing time + Δ,  Δ =r processing time, where r~U(-0.25,0.25).

## Mathematical Model

<!-- ![image](https://hackmd.io/_uploads/Hk4VAHLw6.png) -->
![image](https://hackmd.io/_uploads/ryYKfGDD6.png)


<!-- ![image](https://hackmd.io/_uploads/SymvRSUDp.png) -->

![image](https://hackmd.io/_uploads/SyatRS8vT.png)


## Algorithms

### Overview

Figure 3 is the overview of the algorithm, it is a time discrete algorithm. First, we generate the initial MA and OS sequence. For MA sequence, we assign the operations to the machine which has the minimum processing time. Besides, the OS sequence is generated randomly.Then, we do the initial scheduling, we use metaheuristic algorithms to improve the OS sequence. After getting the operations sequence, we will adjust the MA sequence with local search algorithm. In each iteration, we need to examine whether the time spot is the beginning time of any operations. If it is true, we should update the processing time and reschedule the remaining operations and their machine assignment. We will do this process iteratively until the end of makespan. (The makespan will also change in each iteration.)


<center>
    <img src="https://hackmd.io/_uploads/ByqxJ8ID6.png"
         width="650" 
         height="500">
    <figcaption>Figure 3.</figcaption>
</center>

<!-- ![image](https://hackmd.io/_uploads/ByqxJ8ID6.png)
<figcaption>Figure 3.</figcaption> -->


### Metaheuristics

 - ABC (Artificial Bee Colony)\
The Artificial Bee Colony (ABC) algorithm is an optimization technique inspired by the foraging behavior of honey bees. This innovative approach parallels the quest for food sources with the exploration of the solution space in a problem. The quality of a food source directly corresponds to the objective value of a solution, setting the stage for the algorithm's operation. The process begins with the initialization of a bee population and the positioning of food sources, laying down the configuration and the initial solution.
The ABC algorithm unfolds iteratively, with each cycle comprising three distinct phases. Firstly, the employed bees engage in a greedy search. They explore new positions, tactically combining pairs of current positions, much like bees seeking out promising food sources. This phase symbolizes a focused search within the vicinity of known solutions.
Following this, the onlooker bees come into play. Their role is pivotal; they assess the fitness value of the solutions found by the employed bees and, based on a randomly generated threshold, also engage in a greedy search. This search, too, involves pairing current positions, mirroring the way bees select the most promising food sources based on certain cues.
Lastly, the scout bees address stagnation – a situation where certain solutions, analogous to "old food sources," fail to improve despite repeated attempts. In these cases, scout bees discard these unproductive solutions and introduce new, randomly generated ones. This phase is crucial for maintaining diversity in the solution space and preventing the algorithm from getting trapped in local optima.
Overall, the ABC algorithm's design reflects the efficient and dynamic foraging strategies of bees, turning it into a powerful tool for tackling complex optimization problems.\
We use the following settings: Maximum iteration time = 50, Initial Population=1000.


 - GA (Genetic Algorithm)\
The initial population of the genetic algorithm consists of 30 different operations sequence, all of them are generated randomly. The MA sequence is generated by the initialization rule. We calculate the makespan of all these 30 instances. The probability of picking an instance from the population is
<center>
    <img src="https://hackmd.io/_uploads/SkQ31UUwp.png"
         width="500" 
         height="70">
</center>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;which ensures the sequence with a little makespan has a higher probability to be chosen. 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In each iteration, we perform crossover by picking two parents from the population pool 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;according to the above probability. We randomly select a point c with a value between c 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;and total number of operations − c and generate two children correspondingly. The first 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;child is a job sequence with the first c jobs identical to the first parent. On the other hand, 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;the second child is a job sequence with the first c jobs identical to the second parent. The 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;remaining jobs are then ordered by the relative order of the first parent. The following 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;figure is an example of the children generation process.
<center>
    <img src="https://hackmd.io/_uploads/HkgygIUDT.png"
         width="500" 
         height="100">
</center>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For each child, we again evaluate the job sequence by the identical processes described 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;in the previous paragraph, including searching for the best neighboring assignment. We 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;then substitute the child for the worst job order in the population pool if the child has a 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;better objective value.
After a predetermined number of iterations, which we set to be 30 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;in our implementation, we terminate the algorithm. Finally, we propose the best solution in 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;the population pool as the final solution of our heuristic algorithm.


 - SA (Simulated Anealing)\
Simulated Annealing (SA) is an optimization technique inspired by the metallurgical process of annealing, where materials are heated and then slowly cooled to alter their physical properties. This algorithm cleverly applies the principles of thermodynamics to the realm of optimization problems, where it seeks to find the best possible solution in a large search space.
The core concept of Simulated Annealing is the analogy of heating a material to a high temperature, which increases the atoms' energy and enables them to move freely. In optimization terms, this corresponds to exploring a wide range of possible solutions, even accepting those that are worse than the current solution, to avoid getting trapped in local optima. As the temperature 'cools down,' the algorithm becomes more selective, accepting fewer inferior solutions, akin to atoms settling into a more stable structure.
This cooling process is controlled by a parameter known as the "temperature," which systematically decreases over time according to a predefined schedule. High temperatures at the beginning allow the algorithm to explore a broad range of solutions, including sub-optimal ones. As the temperature decreases, the search gradually focuses on areas of the solution space with higher quality solutions.
A key feature of Simulated Annealing is its ability to probabilistically accept solutions that are worse than the current one. This characteristic helps in jumping out of local optima, a common problem in many optimization algorithms. The probability of accepting worse solutions diminishes as the temperature lowers, guiding the algorithm towards convergence on a global optimum, or at least a near-optimal solution.\
The procedure for SA-based scheduling is shown in Figure 4. We use the following settings: Initial Temperature = 600, Minimum Temperature = 0.1, Cooling Rate = 0.95, Iteration time = 40.
<!-- ![image](https://hackmd.io/_uploads/By8FLLIw6.png) -->
<center>
    <img src="https://hackmd.io/_uploads/By8FLLIw6.png"
         width="450" 
         height="600">
    <figcaption>Figure 4.</figcaption>
</center>



 - Local Search\
We find that some of the operations can be processed on more than one machine. Therefore, we check all the combinations for current partial sequence and find the optimal assignment based on the minimum makespan of partial sequence.

 - Dynamic Scheduling\
We start from 0 to the end of makespan, in each iteration, we check whether the time spot is the beginning time of any operation. If it is true, we update the processing time (processing time = processing time + Δ), beginning and finishing time of each operation and the makespan. Figure 5 is an example of the update process.

<center>
    <img src="https://hackmd.io/_uploads/BkDsgUIw6.png"
         width="700" >
    <figcaption>Figure 5.</figcaption>
</center>

In each iteration, we also fix the partial OS and MA sequence before time t and do the metaheuristic and local search for the remaining sequence. Figure 6 demonstrates how we fix the partial sequence. For MA sequence, we assign the operations in the partial sequence to the determined machines. For OS sequence, we advance the operations in the partial sequence to the front of OS sequence and the remaining operations are then ordered by the relative sequence generated by the rescheduling process.
<center>
    <img src="https://hackmd.io/_uploads/BkBTg8LPT.png"
         width="700" >
    <figcaption>Figure 6.</figcaption>
</center>
<!-- ![image](https://hackmd.io/_uploads/BkBTg8LPT.png)
*Figure 6.* -->


## Results

### Toy Example
- Size: 4 jobs 5 machines, Δ=0.1 * processing time
    - GA: 
        - MA = [[4, 5, 4], [1, 5, 5], [3, 5, 5, 5], [4, 5]]
        - OS = [3, 2, 2, 1, 1, 4, 3, 4, 2, 3, 1, 3]
        - Min makespan = 17
    - ABC
        - MA = [[4, 2, 1], [3, 5, 1], [4, 2, 3, 4], [1, 5]]
        - Best OS = [1, 1, 1, 3, 3, 4, 2, 3, 4, 3, 2, 2]
        - Min makespan = 14
    - SA
        - MA = [[4, 2, 1], [1, 5, 1], [4, 2, 3, 2], [1, 5]]
        - JS = [1, 1, 1, 2, 3, 4, 2, 3, 4, 3, 3, 2]
        - Min makespan = 16
<!-- ![image](https://hackmd.io/_uploads/H1dzH8Iv6.png) -->
<center>
    <img src="https://hackmd.io/_uploads/H1dzH8Iv6.png"
         width="600" 
         height="400">
</center>

### Larger Examples
- Size
    - 10 jobs 5 machines (01a)
    - 15 jobs 8 machines (07a)
    - 20 jobs 10 machines (13a)
- Variation of processing time
    - Δ= (+/-) 0.1/0.2/0.3/0.4/0.5 * processing time
    - [0,0.1], [0.1,0.2], [0.2,0.3], [0.3,0.4], [0.4,0.5]
<!-- ![image](https://hackmd.io/_uploads/SJKdr8ID6.png) -->
<!-- ![image](https://hackmd.io/_uploads/r1K0BLLwT.png) -->
<center>
    <img src="https://hackmd.io/_uploads/SJKdr8ID6.png"
         width="600" 
         height="350">
</center>
<center>
    <img src="https://hackmd.io/_uploads/r1K0BLLwT.png"
         width="600" 
         height="400">
</center>


### Sensitivity Analysis
- The line chart representation of sensitivity analysis based on the variation of processing time

<center>
    <img src="https://hackmd.io/_uploads/Skx3BIIvT.png"
         width="550">
</center>


## Conclusion and Future Work

- Our preliminary results demonstrated that:
    - ABC is empirically more promising than SA and GA
    - As the uncertainty (delta/variation) increases, the scheduling results become more unstable as expected

- For future work, we would like to expand in the following directions:
    - Potential heuristics for speeding up the time to convergence
    - More comprehensive experiments on a larger dataset


## Reference
1. Melissa Shahgholi Zadeh, Yalda Katebi & Ali Doniavi (2019) "A heuristic model for dynamic flexible job shop scheduling problem considering variable processing times", International Journal of Production Research, 57:10, 3020-3035
