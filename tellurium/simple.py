
import tellurium as te
te.setDefaultPlottingEngine('matplotlib')

model = """
model test
    compartment C1;
    C1 = 1.0;
    species S1, S2;

    S1 = 10.0;
    S2 = 0.0;
    S1 in C1; S2 in C1;
    J1: S1 -> S2; k1*S1;

    k1 = 1.0;
end
"""
# load models
r = te.loada(model)

# simulate from 0 to 50 with 100 steps
r.simulate(0, 50, 100)
print("Simulation finished...")

import sys
if not '-nogui' in sys.argv:
    # plot the simulation
    r.plot()
