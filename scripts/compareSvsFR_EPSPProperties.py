from neuron import h
import matplotlib.pyplot as plt
import numpy as  np

import sys
sys.path.append('../testing-motoneuron-types/')
from cells.Motoneuron import Motoneuron

"""
Script for running small simulations of the slow and fatigue-resistant (FR) motoneurons 
to compare properties (EPSP duration, temporal summation for sub- and supra-threshold inputs). 
Plots comparisons. 
"""

### compare EPSP duration
h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='slow')
weights, inputs = mn.build_stim_input(stim_rate=5)
mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize(-70)
h.tstop = 550
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

mn_record = mn_record[time > 400]
mn_record = mn_record - np.mean(mn_record[:50])

plt.plot(time[time > 400]-400, mn_record, label='Slow') 

h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='fr', syn_weight=0.00155)
weights, inputs = mn.build_stim_input(stim_rate=5)

mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize(-70)
h.tstop = 550
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

mn_record = mn_record[time > 400]
mn_record = mn_record - np.mean(mn_record[:50])

plt.plot(time[time > 400]-400, mn_record, label='FR') 
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Comparison of Equal Height EPSP Slow vs. FR MNs')

plt.legend()

plt.figure()

### compare subthreshold temporal summation 
h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='slow')
weights, inputs = mn.build_stim_input(stim_rate=1000)
mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize(-70)
h.tstop = 1000
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

plt.plot(time, mn_record, label='Slow') 

h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='fr', syn_weight=0.0016)
weights, inputs = mn.build_stim_input(stim_rate=1000)

mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize(-70)
h.tstop = 1000
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

plt.plot(time, mn_record, label='FR') 
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Slow vs. FR MNs at 1kHz stimulation')

plt.legend()

plt.figure()

### compare suprathreshold summation 
h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='slow')
weights, inputs = mn.build_stim_input(stim_rate=1500)
mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize()
h.tstop = 1000
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

plt.plot(time, mn_record, label='Slow') 

h.load_file('stdrun.hoc')

mn = Motoneuron(mn_type='fr', syn_weight=0.0016)
weights, inputs = mn.build_stim_input(stim_rate=1500)

mn_record = h.Vector().record(mn.soma(0.5)._ref_v)
time = h.Vector().record(h._ref_t)

h.finitialize()
h.tstop = 1000
h.run()

mn_record = np.array(mn_record)
time = np.array(time)

plt.plot(time, mn_record, label='FR') 
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Slow vs. FR MNs at 1.5kHz stimulation')

plt.legend()

plt.show()