'''
Brian simulator compliant Python export for:

Components:
    Lavrentovich2008_Ca_Oscillations_0 (Type: Lavrentovich2008_Ca_Oscillations:  vin=0.05 (dimensionless) kout=0.5 (dimensionless) vM3=40.0 (dimensionless) k_CaA=0.15 (dimensionless) n=2.02 (dimensionless) k_CaI=0.15 (dimensionless) m=2.2 (dimensionless) kip3=0.1 (dimensionless) vM2=15.0 (dimensionless) k2=0.1 (dimensionless) kf=0.5 (dimensionless) vp=0.05 (dimensionless) kp=0.3 (dimensionless) kdeg=0.08 (dimensionless) tscale=1.0 (SI per_time) compartment=1.0 (dimensionless) ER=1.0 (dimensionless) init_X=0.1 (dimensionless) init_Y=1.5 (dimensionless) init_Z=0.1 (dimensionless))
    sim1 (Type: Simulation:  length=1000.0 (SI time) step=0.01 (SI time))

'''
'''
    This Brian file has been generated by org.neuroml.export (see https://github.com/NeuroML/org.neuroml.export)
         org.neuroml.export  v1.9.0
         org.neuroml.model   v1.9.0
         jLEMS               v0.10.7
'''
from brian import *

from math import *
import sys

import numpy as np


if len(sys.argv) > 1 and sys.argv[1] == '-nogui':
    show_gui = False
else:
    show_gui = True

# Adding simulation Component(id=sim1 type=Simulation) of network: Lavrentovich2008_Ca_Oscillations_0 (Type: Lavrentovich2008_Ca_Oscillations:  vin=0.05 (dimensionless) kout=0.5 (dimensionless) vM3=40.0 (dimensionless) k_CaA=0.15 (dimensionless) n=2.02 (dimensionless) k_CaI=0.15 (dimensionless) m=2.2 (dimensionless) kip3=0.1 (dimensionless) vM2=15.0 (dimensionless) k2=0.1 (dimensionless) kf=0.5 (dimensionless) vp=0.05 (dimensionless) kp=0.3 (dimensionless) kdeg=0.08 (dimensionless) tscale=1.0 (SI per_time) compartment=1.0 (dimensionless) ER=1.0 (dimensionless) init_X=0.1 (dimensionless) init_Y=1.5 (dimensionless) init_Z=0.1 (dimensionless))

defaultclock.dt = 10.0*msecond
duration = 1000000.0*msecond
steps = int(duration/defaultclock.dt)+1


eqs=Equations('''
    dX/dt = (tscale * ((((rate__R1 - rate__R2) + (rate__R3 - rate__R4)) + rate__R5) / compartment)) :  1
    dY/dt = (tscale * (((0.0 - (1.0 * rate__R3)) + (rate__R4 - rate__R5)) / ER)) :  1
    dZ/dt = (tscale * ((rate__R6 - rate__R7) / compartment)) :  1
    tscale = 1.0 * second**-1 : second**-1 
    compartment = 1.0: 1 
    ER = 1.0: 1 
    init_X = 0.1: 1 
    init_Y = 1.5: 1 
    init_Z = 0.1: 1 
    vin = 0.05: 1 
    kout = 0.5: 1 
    vM3 = 40.0: 1 
    k_CaA = 0.15: 1 
    n = 2.02: 1 
    k_CaI = 0.15: 1 
    m = 2.2: 1 
    kip3 = 0.1: 1 
    vM2 = 15.0: 1 
    k2 = 0.1: 1 
    kf = 0.5: 1 
    vp = 0.05: 1 
    kp = 0.3: 1 
    kdeg = 0.08: 1 
    rate__R1 = (compartment * vin) :  1
    rate__R2 = ((compartment * kout) * X) :  1
    rate__R3 = ((((((ER * 4.0) * vM3) * (k_CaA ** n)) * ((X ** n) / (((X ** n) + (k_CaA ** n)) * ((X ** n) + (k_CaI ** n))))) * ((Z ** m) / ((Z ** m) + (kip3 ** m)))) * (Y - X)) :  1
    rate__R4 = ((compartment * vM2) * ((X ** 2.0) / ((X ** 2.0) + (k2 ** 2.0)))) :  1
    rate__R5 = ((ER * kf) * (Y - X)) :  1
    rate__R6 = ((compartment * vp) * ((X ** 2.0) / ((X ** 2.0) + (kp ** 2.0)))) :  1
    rate__R7 = ((compartment * kdeg) * Z) :  1
''')

OneComponentPop = NeuronGroup(1, model=eqs)
OneComponentPop.X = OneComponentPop.init_X
OneComponentPop.Y = OneComponentPop.init_Y
OneComponentPop.Z = OneComponentPop.init_Z
# Initialise a second time...
OneComponentPop.X = OneComponentPop.init_X
OneComponentPop.Y = OneComponentPop.init_Y
OneComponentPop.Z = OneComponentPop.init_Z

if show_gui:

    # Display: Component(id=disp1 type=Display)
    trace_disp1__X__S = StateMonitor(OneComponentPop,'X',record=[0]) # X__S (Type: Line:  scale=1.0 (dimensionless) timeScale=1.0 (dimensionless))
    trace_disp1__Y__S = StateMonitor(OneComponentPop,'Y',record=[0]) # Y__S (Type: Line:  scale=1.0 (dimensionless) timeScale=1.0 (dimensionless))
    trace_disp1__Z__S = StateMonitor(OneComponentPop,'Z',record=[0]) # Z__S (Type: Line:  scale=1.0 (dimensionless) timeScale=1.0 (dimensionless))

# Saving to file: Lavrentovich2008_Ca_Oscillations.dat, reference: outputFile1
record_outputFile1__os_X = StateMonitor(OneComponentPop,'X',record=[0]) # os_X (Type: OutputColumn)
record_outputFile1__os_Y = StateMonitor(OneComponentPop,'Y',record=[0]) # os_Y (Type: OutputColumn)
record_outputFile1__os_Z = StateMonitor(OneComponentPop,'Z',record=[0]) # os_Z (Type: OutputColumn)

print("Running simulation for %s (dt = %s, #steps = %s)"%(duration,defaultclock.dt, steps))
run(duration) # Run a simulation from t=0 to just before t=duration 
run(defaultclock.dt) # Run one more time step to allow saving the point at t=duration

# Saving to file: Lavrentovich2008_Ca_Oscillations.dat, reference: outputFile1
all_outputFile1 = np.array( [ record_outputFile1__os_X.times, record_outputFile1__os_X[0] , record_outputFile1__os_Y[0] , record_outputFile1__os_Z[0]  ] )
all_outputFile1 = all_outputFile1.transpose()
file_outputFile1 = open("Lavrentovich2008_Ca_Oscillations.dat", 'w')
for l in all_outputFile1:
    line = ''
    for c in l: 
        line = line + ('\t%s'%c if len(line)>0 else '%s'%c)
    file_outputFile1.write(line+'\n')
file_outputFile1.close()

if show_gui:

    import matplotlib.pyplot as plt

    # Display: Component(id=disp1 type=Display)
    display_disp1 = plt.figure("Simulation of SBML model: Lavrentovich2008_Ca_Oscillations from file: BIOMD0000000184.xml")
    plot_X__S = display_disp1.add_subplot(111, autoscale_on=True)
    plot_X__S.plot(trace_disp1__X__S.times/second,trace_disp1__X__S[0], color="#000000", label="X__S")
    plot_X__S.legend()
    plot_Y__S = display_disp1.add_subplot(111, autoscale_on=True)
    plot_Y__S.plot(trace_disp1__Y__S.times/second,trace_disp1__Y__S[0], color="#ff0000", label="Y__S")
    plot_Y__S.legend()
    plot_Z__S = display_disp1.add_subplot(111, autoscale_on=True)
    plot_Z__S.plot(trace_disp1__Z__S.times/second,trace_disp1__Z__S[0], color="#00ff00", label="Z__S")
    plot_Z__S.legend()
    plt.show()
