'''
Neuron simulator export for:

Components:
    Lavrentovich2008_Ca_Oscillations_0 (Type: Lavrentovich2008_Ca_Oscillations:  vin=0.05 (dimensionless) kout=0.5 (dimensionless) vM3=40.0 (dimensionless) k_CaA=0.15 (dimensionless) n=2.02 (dimensionless) k_CaI=0.15 (dimensionless) m=2.2 (dimensionless) kip3=0.1 (dimensionless) vM2=15.0 (dimensionless) k2=0.1 (dimensionless) kf=0.5 (dimensionless) vp=0.05 (dimensionless) kp=0.3 (dimensionless) kdeg=0.08 (dimensionless) tscale=1.0 (SI per_time) compartment=1.0 (dimensionless) ER=1.0 (dimensionless) init_X=0.1 (dimensionless) init_Y=1.5 (dimensionless) init_Z=0.1 (dimensionless))
    sim1 (Type: Simulation:  length=1000.0 (SI time) step=0.01 (SI time))


    This NEURON file has been generated by org.neuroml.export (see https://github.com/NeuroML/org.neuroml.export)
         org.neuroml.export  v1.10.0
         org.neuroml.model   v1.10.0
         jLEMS               v0.11.0

'''

import neuron

import time
import datetime
import sys

import hashlib
h = neuron.h
h.load_file("stdlib.hoc")

h.load_file("stdgui.hoc")

h("objref p")
h("p = new PythonObject()")

class NeuronSimulation():

    def __init__(self, tstop, dt=None, seed=123456789, abs_tol=None, rel_tol=None):

        print("\n    Starting simulation in NEURON of %sms generated from NeuroML2 model...\n"%tstop)

        self.setup_start = time.time()
        self.seed = seed
        self.abs_tol = abs_tol
        self.rel_tol = rel_tol
        self.randoms = []
        self.next_global_id = 0  # Used in Random123 classes for elements using random(), etc. 

        self.next_spiking_input_id = 0  # Used in Random123 classes for elements using random(), etc. 

        '''
        Adding simulation Component(id=sim1 type=Simulation) of network/component: Lavrentovich2008_Ca_Oscillations_0 (Type: Lavrentovich2008_Ca_Oscillations:  vin=0.05 (dimensionless) kout=0.5 (dimensionless) vM3=40.0 (dimensionless) k_CaA=0.15 (dimensionless) n=2.02 (dimensionless) k_CaI=0.15 (dimensionless) m=2.2 (dimensionless) kip3=0.1 (dimensionless) vM2=15.0 (dimensionless) k2=0.1 (dimensionless) kf=0.5 (dimensionless) vp=0.05 (dimensionless) kp=0.3 (dimensionless) kdeg=0.08 (dimensionless) tscale=1.0 (SI per_time) compartment=1.0 (dimensionless) ER=1.0 (dimensionless) init_X=0.1 (dimensionless) init_Y=1.5 (dimensionless) init_Z=0.1 (dimensionless))
        
        '''
        # ######################   Population: population_null
        print("Population population_null contains 1 instance(s) of component: Lavrentovich2008_Ca_Oscillations_0 of type: Lavrentovich2008_Ca_Oscillations")

        h(" {n_population_null = 1} ")
        '''
        Population population_null contains instances of Component(id=Lavrentovich2008_Ca_Oscillations_0 type=Lavrentovich2008_Ca_Oscillations)
        whose dynamics will be implemented as a mechanism (Lavrentovich2008_Ca_Oscillations_0) in a mod file
        '''
        h(" create population_null[1]")
        h(" objectvar m_Lavrentovich2008_Ca_Oscillations_0_population_null[1] ")

        for i in range(int(h.n_population_null)):
            h.population_null[i](0.5).cm = 318.31
            h.population_null[i].L = 10.0               # length to use for section in Neuron
            h.population_null[i](0.5).diam = 10.0       # diameter to use for section in Neuron
            h.population_null[i].push()
            h(" population_null[%i]  { m_Lavrentovich2008_Ca_Oscillations_0_population_null[%i] = new Lavrentovich2008_Ca_Oscillations_0(0.5) } "%(i,i))

            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].vin = 0.05 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].kout = 0.5 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].vM3 = 40.0 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].k_CaA = 0.15 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].n = 2.02 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].k_CaI = 0.15 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].m = 2.2 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].kip3 = 0.1 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].vM2 = 15.0 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].k2 = 0.1 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].kf = 0.5 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].vp = 0.05 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].kp = 0.3 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].kdeg = 0.08 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].tscale = 0.001 # NRN unit is: (kHz)
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].compartment = 1.0 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].ER = 1.0 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].init_X = 0.1 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].init_Y = 1.5 # NRN unit is: 
            h.m_Lavrentovich2008_Ca_Oscillations_0_population_null[i].init_Z = 0.1 # NRN unit is: 
            h.pop_section()

            self.next_global_id+=1


        trec = h.Vector()
        trec.record(h._ref_t)

        h.tstop = tstop

        if self.abs_tol is not None and self.rel_tol is not None:
            cvode = h.CVode()
            cvode.active(1)
            cvode.atol(self.abs_tol)
            cvode.rtol(self.rel_tol)
        else:
            h.dt = dt
            h.steps_per_ms = 1/h.dt



        # ######################   File to save: Lavrentovich2008_Ca_Oscillations.dat (outputFile1)
        # Column: X
        h(' objectvar v_os_X_outputFile1 ')
        h(' { v_os_X_outputFile1 = new Vector() } ')
        h(' { v_os_X_outputFile1.record(&m_Lavrentovich2008_Ca_Oscillations_0_population_null[0].X) } ')
        if self.abs_tol is None or self.rel_tol is None:

            h.v_os_X_outputFile1.resize((h.tstop * h.steps_per_ms) + 1)
        # Column: Y
        h(' objectvar v_os_Y_outputFile1 ')
        h(' { v_os_Y_outputFile1 = new Vector() } ')
        h(' { v_os_Y_outputFile1.record(&m_Lavrentovich2008_Ca_Oscillations_0_population_null[0].Y) } ')
        if self.abs_tol is None or self.rel_tol is None:

            h.v_os_Y_outputFile1.resize((h.tstop * h.steps_per_ms) + 1)
        # Column: Z
        h(' objectvar v_os_Z_outputFile1 ')
        h(' { v_os_Z_outputFile1 = new Vector() } ')
        h(' { v_os_Z_outputFile1.record(&m_Lavrentovich2008_Ca_Oscillations_0_population_null[0].Z) } ')
        if self.abs_tol is None or self.rel_tol is None:

            h.v_os_Z_outputFile1.resize((h.tstop * h.steps_per_ms) + 1)

        # ######################   File to save: time.dat (time)
        # Column: time
        h(' objectvar v_time ')
        h(' { v_time = new Vector() } ')
        h(' { v_time.record(&t) } ')
        if self.abs_tol is None or self.rel_tol is None:

            h.v_time.resize((h.tstop * h.steps_per_ms) + 1)

        self.initialized = False

        self.sim_end = -1 # will be overwritten

        setup_end = time.time()
        self.setup_time = setup_end - self.setup_start
        print("Setting up the network to simulate took %f seconds"%(self.setup_time))

    def run(self):

        self.initialized = True
        sim_start = time.time()
        if self.abs_tol is not None and self.rel_tol is not None:
            print("Running a simulation of %sms (cvode abs_tol = %sms, rel_tol = %sms; seed=%s)" % (h.tstop, self.abs_tol, self.rel_tol, self.seed))
        else:
            print("Running a simulation of %sms (dt = %sms; seed=%s)" % (h.tstop, h.dt, self.seed))

        try:
            h.run()
        except Exception as e:
            print("Exception running NEURON: %s" % (e))
            quit()


        self.sim_end = time.time()
        self.sim_time = self.sim_end - sim_start
        print("Finished NEURON simulation in %f seconds (%f mins)..."%(self.sim_time, self.sim_time/60.0))

        try:
            self.save_results()
        except Exception as e:
            print("Exception saving results of NEURON simulation: %s" % (e))
            quit()


    def advance(self):

        if not self.initialized:
            h.finitialize()
            self.initialized = True

        h.fadvance()


    ###############################################################################
    # Hash function to use in generation of random value
    # This is copied from NetPyNE: https://github.com/Neurosim-lab/netpyne/blob/master/netpyne/simFuncs.py
    ###############################################################################
    def _id32 (self,obj): 
        return int(hashlib.md5(obj.encode('utf-8')).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


    ###############################################################################
    # Initialize the stim randomizer
    # This is copied from NetPyNE: https://github.com/Neurosim-lab/netpyne/blob/master/netpyne/simFuncs.py
    ###############################################################################
    def _init_stim_randomizer(self,rand, stimType, gid, seed): 
        #print("INIT STIM  %s; %s; %s; %s"%(rand, stimType, gid, seed))
        rand.Random123(self._id32(stimType), gid, seed)


    def save_results(self):

        print("Saving results at t=%s..."%h.t)

        if self.sim_end < 0: self.sim_end = time.time()


        # ######################   File to save: time.dat (time). Note, saving in SI units
        py_v_time = [ t/1000 for t in h.v_time.to_python() ]  # Convert to Python list for speed...

        f_time_f2 = open('time.dat', 'w')
        num_points = len(py_v_time)  # Simulation may have been stopped before tstop...

        for i in range(num_points):
            f_time_f2.write('%f'% py_v_time[i])  # Save in SI units...
        f_time_f2.close()
        print("Saved data to: time.dat")

        # ######################   File to save: Lavrentovich2008_Ca_Oscillations.dat (outputFile1). Note, saving in SI units
        py_v_os_X_outputFile1 = [ float(x ) for x in h.v_os_X_outputFile1.to_python() ]  # Convert to Python list for speed, variable has dim: none
        py_v_os_Y_outputFile1 = [ float(x ) for x in h.v_os_Y_outputFile1.to_python() ]  # Convert to Python list for speed, variable has dim: none
        py_v_os_Z_outputFile1 = [ float(x ) for x in h.v_os_Z_outputFile1.to_python() ]  # Convert to Python list for speed, variable has dim: none

        f_outputFile1_f2 = open('Lavrentovich2008_Ca_Oscillations.dat', 'w')
        num_points = len(py_v_time)  # Simulation may have been stopped before tstop...

        for i in range(num_points):
            f_outputFile1_f2.write('%e\t%e\t%e\t%e\t\n' % (py_v_time[i], py_v_os_X_outputFile1[i], py_v_os_Y_outputFile1[i], py_v_os_Z_outputFile1[i], ))
        f_outputFile1_f2.close()
        print("Saved data to: Lavrentovich2008_Ca_Oscillations.dat")

        save_end = time.time()
        save_time = save_end - self.sim_end
        print("Finished saving results in %f seconds"%(save_time))

        print("Done")

        quit()


if __name__ == '__main__':

    ns = NeuronSimulation(tstop=1000000.0, dt=10.0, seed=123456789, abs_tol=None, rel_tol=None)

    ns.run()

