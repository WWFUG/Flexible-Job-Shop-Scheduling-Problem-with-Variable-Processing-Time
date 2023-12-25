
import numpy as np
# import pprint as pp
import random as rand
import queue
import math
    
# TODO define the evaluation function passed to fn_eval
# set the function value of infeasible solution to infinity
# Encode the FJSP problem to the Machine Assignment (MA) vector and Operation Assignment (OS) vector



class AbcScheduler(object):
    def __init__(self, jobOpMachine_to_time, job_to_opnum, num_machine, num_job):
        self.var_jom_to_time = jobOpMachine_to_time
        self.jom_to_time    = jobOpMachine_to_time
        self.num_machine    = num_machine
        self.num_job        = num_job
        self.job_to_opnum   = job_to_opnum
        self.job_MA_start   = [0] * self.num_job
        
        self.machine_to_started_jop = [[] for _ in range(num_machine)]
        self.job_to_unprocessed_op = [1] * self.num_job 
        self.incre_best_schedule = {}
        
        self.MA_len         = 0
        id = 1
        for entry in job_to_opnum:
            self.MA_len += entry
            if id == len(job_to_opnum) - 1: continue
            self.job_MA_start[id] = self.MA_len
            id += 1
        
        self.npopulation    = None
        self.nruns          = None
        self.trials_limit   = None
        self.fn_lb          = None
        self.fn_ub          = None

        self.employed_bees  = None
        self.onlooker_bees  = None
        
        self.MA             = [0] * self.MA_len
        self.OS             = [0] * self.MA_len
        
        # food sources
        self.food_MA        = None      # currently only Apply ABC on OS
        self.food_OS        = None
        self.food_makespan  = None
        self.food_trials    = None
        self.tmp_op_to_time = None

        
        self.best_makespan  = math.inf
        self.best_schedule  = None
        self.best_OS        = None
        self.best_MA        = None
        
        
    def initAbc (self, npop, nrs, tlimit=50, ebp=0.5):

        self.npopulation    = npop
        self.nruns          = nrs
        self.trials_limit   = tlimit

        self.employed_bees  = round(npop * ebp)
        self.onlooker_bees  = npop - self.employed_bees
        
        self.food_MA        = [ self.create_initMA() for _ in range(self.employed_bees) ]
        self.food_OS        = [ self.create_randOS() for _ in range(self.employed_bees) ]
        self.food_makespan  = [ 0 ] * self.employed_bees
        self.food_trials    = [ 0 ] * self.employed_bees
        
        # generate initial MA
        self.GMPT_MA()

        for i, OS in enumerate(self.food_OS):

            makespan = self.eval_OS(OS) 
            # print("Decoded {} {}".format( i, makespan)  )
            self.food_makespan[i] = makespan
            if makespan < self.best_makespan:
                self.best_makespan = makespan
                self.best_schedule = self.tmp_op_to_time
                self.best_OS       = OS
                self.best_MA       = self.MA
        
    def optimize(self, npop, nrs):
        nrs = 1
        for _ in range(1):
            self.optimize_OS(npop, nrs)
            self.optimize_MA()
            # print("Best OS {}".format(self.best_OS))
            # print("Best MA {}".format(self.best_MA))
    
    def dynamic_optimize(self, npop, nrs, delta):
        self.optimize(npop, nrs)
        MAX_SPAN = 10000
        job_done = [False] * self.num_job
        for cur_t in range(0, MAX_SPAN):
            new_start_job = False
            for jom, start_time in self.best_schedule.items():
                # include started operation
                job, op, machine = jom
                if start_time == cur_t:
                    new_start_job = True
                    self.incre_best_schedule[jom] = start_time
                    self.machine_to_started_jop[ machine-1 ].append( jom[:-1] )
                    self.job_to_unprocessed_op[ job-1 ] += 1
                    if self.job_to_unprocessed_op[ job-1 ] > self.job_to_opnum[ job-1 ]:
                        job_done[job-1] = True
                        
            if len( set(job_done) ) == 1 and job_done[0]:
                break
            
            # update jom_to_time
            if new_start_job:
                for jom, time in self.jom_to_time.items():
                    if jom not in self.incre_best_schedule:
                        self.var_jom_to_time[jom] = int(rand.uniform( (1-delta)*time , (1+delta)*time ))
                self.optimize(npop, nrs)
    
    # TODO using critical operations as a heuristic
    def optimize_MA(self):
        cnt = 0
        percent = 1
        # print("Initial makespan {}".format(self.best_makespan))
        for i in range(self.MA_len):
            self.MA = self.best_MA
            for m_id in range(1, self.num_machine+1):
                if m_id == self.MA[i]: continue
                orig_mid = self.MA[i]
                self.MA[i] = m_id
                self.MA = self.incor_proc_jop_MA(self.MA)
                new_makespan = self.eval_OS(self.best_OS)
                if new_makespan < self.best_makespan:
                    self.best_MA = self.MA
                    self.best_schedule = self.tmp_op_to_time
                    self.best_makespan = new_makespan
                    # print("Update best makespan : {}".format(self.best_makespan))
                    # print("MA: {}".format(self.best_MA))
                else:
                    self.MA[i] = orig_mid
    
    def optimize_OS(self, npop, nrs):
        self.initAbc(npop, nrs)
        for _ in range(1, self.nruns+1):
            self.employed_bees_stage()
            self.onlooker_bees_stage()
            self.scout_bees_stage()
            
        best_pos = self.food_makespan.index(min(self.food_makespan))
        val = self.eval_OS( self.food_OS[best_pos] )
        assert(val == min(self.food_makespan))
        self.best_schedule = self.tmp_op_to_time
        self.best_OS = self.food_OS[best_pos]
        self.best_MA = self.MA
                
        
    def employed_bees_stage(self):
        pop = self.employed_bees
        for i in range(pop):
            k = rand.randint(0, pop - 1)
            while k == i:
                k = rand.randint(0, pop - 1)
            new_OS = self.gen_newOS(i, k)
            new_makespan = self.eval_OS(new_OS)
            if new_makespan < self.food_makespan[i]:
                self.food_makespan[i] = new_makespan
                self.food_OS[i] = new_OS
            else:
                self.food_trials[i] += 1

    def onlooker_bees_stage(self):
        pop = self.onlooker_bees
        mean_makespan = sum(self.food_makespan) / len(self.food_makespan)
        prob = [math.exp(-self.food_makespan[i] / mean_makespan) for i in range(pop)]
        for i in range(pop):
            ind = self.roulette_selection(prob)
            k = rand.randint(0, pop - 1)
            while k == ind:
                k = rand.randint(0, pop - 1)
            new_OS = self.gen_newOS(i, k)
            new_makespan = self.eval_OS(new_OS)
            if new_makespan < self.food_makespan[i]:
                self.food_makespan[i] = new_makespan
                self.food_OS[i] = new_OS
            else:
                self.food_trials[i] += 1
    
    def scout_bees_stage(self):
        pop = self.employed_bees
        for i in range(pop):
            if self.food_trials[i] >= self.trials_limit:
                self.food_OS[i] = self.create_randOS()
                self.food_makespan[i] = self.eval_OS(self.food_OS[i])
                self.food_trials[i] = 0


    # generate new OS using OS i with neighbor k
    def gen_newOS(self, i, k):
        phi = [rand.random() for _ in range(self.num_job) ]
        denometer = (self.fitness(self.food_makespan[i]) + self.fitness(self.food_makespan[k]))
        R = [ self.fitness(self.food_makespan[i])/denometer, self.fitness(self.food_makespan[k])/denometer   ]
        t = self.roulette_selection(R)
        prob_thr = R[t-1]
        new_OS = [0] * self.MA_len
        OS_i, OS_k = self.food_OS[i], self.food_OS[k]    
    
        copy = [False] * self.num_job
        # determine which job should remain the same
        for j_id in range(1, self.num_job+1):
            if phi[j_id-1] <= prob_thr:
                copy[j_id-1] = True
        
        # update using OS_k
        for i, j_id in enumerate(OS_k):
            if copy[j_id-1]:
                new_OS[i] = j_id
        
        # update using OS_i
        for i, j_id in enumerate(new_OS):
            if j_id != 0: continue
            if not copy[ OS_i[i]-1 ]:
                new_OS[i] = OS_i[i]

        job_op_num = [0] * self.num_job
        insert_pos = []
        # SUMIF
        for i, j_id in enumerate(new_OS):
            if j_id == 0: 
                insert_pos.append(i)
            else:
                job_op_num[j_id-1] += 1
        
        for i in range(len(job_op_num)):
            job_op_num[i] = (self.job_to_opnum[i] - job_op_num[i])
            
        insert_jid = []
        for i in range(len(job_op_num)):
            if job_op_num[i] == 0: continue
            for _ in range( job_op_num[i] ):
                insert_jid .append(i+1)

        # randomly fill in empty positions
        rand.shuffle(insert_jid)
        for i, id in enumerate(insert_pos):
            new_OS[id] = insert_jid[i]
        
        return self.incor_proc_jop_OS(new_OS)

            
    # TODO cross over operation
    
    def GMPT_MA(self):
        machine_WL = [0] * self.num_machine
        ma_entry_id = 0
        for job_id in range(1, self.num_job+1):
            num_op = self.job_to_opnum[job_id-1]
            # for each operation
            for op in range(1, num_op+1):
                min_mid, min_dur = 0, math.inf
                # search for machine with minimum processing time
                for m_id in range(1, self.num_machine+1):
                    duration = self.var_jom_to_time[(job_id, op, m_id)]
                    if machine_WL[m_id-1] + duration < min_dur:
                        min_mid, min_dur = m_id, machine_WL[m_id-1] + duration
                machine_WL[min_mid-1] += min_dur 
                self.MA[ma_entry_id] = min_mid
                
                ma_entry_id += 1
        # FIXME considering processed job op
        self.MA = self.incor_proc_jop_MA(self.MA)
        
        # print("Init MA: {}".format(self.MA))
                  
    
    def create_initMA(self):
        pass
    
    def create_randOS(self):
        init_OS = [0] * self.MA_len
        id_OS  = 0
        for job_id in range(1, self.num_job+1):
            num_op = self.job_to_opnum[job_id-1]
            # for each operation
            for _ in range(num_op):
                init_OS[id_OS] = job_id
                id_OS += 1
        rand.shuffle(init_OS)
        # FIXME considering processed job op
        init_OS = self.incor_proc_jop_OS(init_OS)
        return init_OS
        
    # use self.MA to evaluate OS
    # def eval_OS(self, OS):
    #     machine_cur_time = [0] * self.num_machine
    #     job_last_end_time = [0] * self.num_job
    #     job_op_index = [1] * self.num_job
    #     machine_op_list  = [queue.Queue() for _ in range(self.num_machine)]
    #     self.tmp_op_to_time = {}
    #     # print(OS)
    #     # print(self.num_job)
    #     for j_id in OS:
    #         op_id = job_op_index[j_id-1]
    #         ass_machine = self.MA[ self.job_MA_start[j_id-1] + op_id - 1 ]
    #         machine_op_list[ass_machine-1].put( (j_id, op_id)  ) 
    #         # print(j_id)
    #         job_op_index[j_id-1]+=1
            
    #     op_queue = queue.Queue()
    #     for op_l in machine_op_list:
    #         if op_l.empty(): continue
    #         op_queue.put(op_l.get())

    #     job_op_index = [1] * self.num_job
    #     makespan = 0
    #     while not op_queue.empty():
    #         jid, oid = op_queue.get() # (job, op_id)
            
    #         mid = self.MA[self.job_MA_start[ jid - 1 ] + oid -1 ]
        
    #         if job_op_index[jid-1] == oid:
    #             duration = self.var_jom_to_time[ (jid, oid, mid) ]
    #             if machine_cur_time[mid-1] < job_last_end_time[jid-1]:
    #                 self.tmp_op_to_time[ (jid, oid, mid) ] = job_last_end_time[jid-1]
    #                 machine_cur_time[mid-1] = job_last_end_time[jid-1] + duration 
    #             else:
    #                 self.tmp_op_to_time[ (jid, oid, mid) ] = machine_cur_time[mid-1]
    #                 machine_cur_time[mid-1] +=  duration
                
    #             job_last_end_time[jid-1] = machine_cur_time[mid-1]
    #             makespan = max(makespan, job_last_end_time[jid-1] )
                
    #             if not machine_op_list[mid-1].empty():
    #                 op_queue.put( machine_op_list[mid-1].get() )
                
    #             job_op_index[jid-1] += 1
    #         else:
    #             op_queue.put( (jid, oid) )

    #     return  makespan
    

    def eval_OS(self, OS):
        self.tmp_op_to_time = {}
        machine_cur_time = [0] * self.num_machine
        job_cur_time = [0] * self.num_job
        job_op_id = [1] * self.num_job

        for j_id in OS:
            o_id = job_op_id[j_id-1]
            m_id = self.MA[self.job_MA_start[j_id-1] + o_id]
            p_time = self.var_jom_to_time[(j_id, o_id, m_id)]
            if machine_cur_time[m_id-1] < job_cur_time[j_id-1]:
                self.tmp_op_to_time[(j_id, o_id, m_id)] = job_cur_time[j_id-1]
                machine_cur_time[m_id-1] = job_cur_time[j_id-1] + p_time
            else:
                self.tmp_op_to_time[(j_id, o_id, m_id)] = machine_cur_time[m_id-1]
                machine_cur_time[m_id-1] += p_time
            job_cur_time[j_id-1] = machine_cur_time[m_id-1]
            job_op_id[j_id-1] += 1
        makespan = max(job_cur_time)
        # print(f"Makespan: {makespan}")
        return makespan

    # minimization
    def fitness(self, val):
        return 1 / (1 + val)
    
    
    
    def roulette_selection(self, probs):
        """
        The roulette selection
        :param pro: probability
        :return:
        """
        r = rand.random()
        probability = 0
        sum_prob = sum(probs)
        for i in range(len(probs)):
            probability += probs[i] / sum_prob
            if probability >= r:
                return i
    
    
    def incor_proc_jop_MA(self, MA):
        for m, jop_list in enumerate(self.machine_to_started_jop):
            for jop in jop_list:
                job, op = jop
                entry = self.job_MA_start[job-1] + op - 1
                MA[entry] = m+1
            
        return MA

    def incor_proc_jop_OS(self, OS):
        prefix_OS = []
        for m, jop_list in enumerate(self.machine_to_started_jop):
            for jop in jop_list:
                job, op = jop
                prefix_OS.append(job)
        
        for job, unproc_op in enumerate(self.job_to_unprocessed_op):
            del_count = unproc_op-1
            # job + 1
            for _ in range(del_count): OS.remove(job+1)
        return prefix_OS + OS
    
    
    
    
    
    def test_eval_OS(self):
        MA = [4, 2, 4, 3, 3, 1, 2, 4, 3, 1]
        OS = [2, 3, 3, 1, 4, 1, 2, 4, 3, 1]
        test_time_dict = { (3, 1, 1):7, (4, 2, 1):6, (3, 2, 2): 8, (1, 2, 2): 3,
                           (2, 1, 3):5, (4, 1, 3):8, (2, 2, 3): 9, (1, 1, 4): 6,
                           (3, 3, 4):5, (1, 3, 4):4} 
        machine_cur_time = [0, 0, 0, 0]
        job_last_end_time = [0, 0, 0, 0]
        job_MA_start   = [0, 3, 5, 8]
        job_op_index = [1, 1, 1, 1]
        machine_op_list  = [queue.Queue(), queue.Queue(), queue.Queue(), queue.Queue()]
        op_to_machine = {}
        op_to_time = {}
        
        for j_id in OS:
            op_id = job_op_index[j_id-1]
            ass_machine = MA[ job_MA_start[j_id-1] + op_id - 1 ]
            # print("Assign {} op of job {} to machine {}".format( op_id, j_id, ass_machine   ) )
            machine_op_list[ass_machine-1].put( (j_id, op_id)  ) 
            job_op_index[j_id-1]+=1
        
        op_queue = queue.Queue()
        for op_l in machine_op_list:
            op_queue.put(op_l.get())
        
        job_op_index = [1, 1, 1, 1]
        while not op_queue.empty():
            jid, oid = op_queue.get() # (job, op_id)
            
            mid = MA[job_MA_start[ jid - 1 ] + oid -1 ]
            
            print("Get({} {} {})".format(jid, oid, mid))
            if job_op_index[jid-1] == oid:
                if machine_cur_time[mid-1] < job_last_end_time[jid-1]:
                    op_to_time[ (jid, oid) ] = job_last_end_time[jid-1]
                    machine_cur_time[mid-1] = job_last_end_time[jid-1] + test_time_dict[ (jid, oid, mid) ]
                else:
                    op_to_time[ (jid, oid) ] = machine_cur_time[mid-1]
                    machine_cur_time[mid-1] += test_time_dict[ (jid, oid, mid) ]
                
                job_last_end_time[jid-1] = machine_cur_time[mid-1]
                
                if not machine_op_list[mid-1].empty():
                    op_queue.put( machine_op_list[mid-1].get() )
                
                job_op_index[jid-1] += 1
            else:
                op_queue.put( (jid, oid) )
                print("Put({} {} {})".format(jid, oid, mid))
            print(job_op_index)

        print(op_to_time)
            
            