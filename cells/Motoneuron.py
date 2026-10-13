from .Cell import Cell
from neuron import h
import random as rnd
import numpy as np

class Motoneuron(Cell):
	""" Model motoneuron adapted from Formento, 2018, and Jones & Bawa, 1995. """

	def __init__(self, mn_type=str, syn_weight=0.001):
		Cell.__init__(self)

		self._mn_type = mn_type

		# Define parameters
		self.synapses = []

		if self._mn_type == 'slow':  
			self._nDendrites = 17
			self._diamDend = [25, 25, 25, 25, 25, 25, 25, 15, 
					 		15, 12, 10, 8, 7, 1, 1, 1, 0.63]
			self._lengthDend = [7000/self._nDendrites] * self._nDendrites
			self._synapseWeights = [45, 50, 75, 42, 30, 12, 12, 11, 
						   8, 7, 5, 3, 0, 0, 0, 0, 0]
			self._synapseWeights = [sw * syn_weight for sw in self._synapseWeights]
			
		elif self._mn_type == 'fr': 
			self._nDendrites = 19
			self._diamDend = [40, 40, 40, 40, 40, 30, 28, 26, 
					 		15, 12, 10, 8, 7, 5, 4, 3, 2, 1, 1]
			self._lengthDend = [6675/self._nDendrites] * self._nDendrites
			self._synapseWeights = [45, 50, 60, 45, 38, 18, 17, 16, 
						  8, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			self._synapseWeights = [sw * syn_weight for sw in self._synapseWeights]

		self._create_sections()
		self._define_biophysics()
		self._build_topology()


	def _create_sections(self):
		""" Create the sections of the cell. """
		# NOTE: cell=self is required to tell NEURON of this object.
		self.soma = h.Section(name='soma',cell=self)
		self.dendrite = [h.Section(name='dendrite',cell=self) for x in range(self._nDendrites)]
		self.initSegment = h.Section(name='soma', cell=self)

	def _define_biophysics(self):
		""" Assign geometry and membrane properties across the cell. """
		self.soma.nseg = 1
		self.soma.cm = 1
		
		if (self._mn_type == 'slow'): 
			self.soma.L = 50.9
			self.soma.diam = 50.9
			self.soma.Ra = 200 # need to confirm
			self.soma.insert('pas')
			self.soma.g_pas = 1.4e-3 # Jones & Bawa, 1995

		elif self._mn_type == 'fr': 
			self.soma.L = 48.8
			self.soma.diam = 48.8
			self.soma.Ra = 200 # need to confirm
			self.soma.insert('pas')
			self.soma.g_pas = 4.4e-3 # Jones & Bawa, 1995

		self.soma.insert('motoneuron') # Insert the Neuron motoneuron mechanism developed by McIntyre 2002

		self.initSegment.nseg = 1
		self.initSegment.L = 100
		self.initSegment.diam = 10
		self.initSegment.insert('initial') # Insert the Neuron initial mechanism developed by McIntyre
		self.initSegment.gnap_initial = 0
		self.initSegment.Ra = 200
		self.initSegment.cm = 1

		for dendrite,i in zip(self.dendrite,list(range(self._nDendrites))):
			dendrite.nseg = 11
			dendrite.diam = self._diamDend[i]
			dendrite.L = self._lengthDend[i]
			if (self._mn_type == 'slow'): 
				dendrite.Ra = 262 # from the relationship between Rm and lambda in Jones & Bawa, 1995 -- need to confirm 
				dendrite.insert('pas') # Insert the Neuron pas mechanism
				dendrite.g_pas = 5e-5 # Jones & Bawa, 1995
				dendrite.e_pas = -70.0
			elif self._mn_type == 'fr': 
				dendrite.Ra = 545 # from the relationship between Rm and lambda in Jones & Bawa, 1995 -- need to confirm
				dendrite.insert('pas') # Insert the Neuron pas mechanism
				dendrite.g_pas = 9e-5 # Jones & Bawa, 1995
				dendrite.e_pas = -70.0
			dendrite.cm = 1
			

	def _build_topology(self):
		""" Connect the sections together. """
		self.initSegment.connect(self.soma,0,0)
		self.dendrite[0].connect(self.soma,1,0)

		for i in range(self._nDendrites-1):
			self.dendrite[i+1].connect(self.dendrite[i],1,0)

	def create_synapse(self, den_ind=None):
		""" 
		Create and return a synapse that links motoneuron state variables to external events 
		at the dendritic index provided (if None given, link at middle of dendrite). 

		The created synapse is also appended to a list containing all synapses the this motoneuron has.
		"""
		if not den_ind: 
			den_ind = int(self._nDendrites/2)

		syn = h.ExpSyn(self.dendrite[den_ind](0.5))
		syn.tau = 0.2 # from Bawa & Jones 1995, was 0.5 in Formento
		syn.e = 0

		self.synapses.append(syn)

		return syn
	

	def build_stim_input(self, stim_rate=0.1): 
		connections = []
		inputs = []

		for ind in range(self._nDendrites): 
			syn_ = self.create_synapse(ind)

			input = h.NetStim()
			input.interval = 1000.0/ stim_rate   # Inter-spike interval in ms
			input.noise = 0
			input.number = 1e999
			inputs.append(input)

			nc = h.NetCon(input, syn_)
			nc.weight[0] = self._synapseWeights[ind]
			connections.append(nc)

		return connections, inputs
	
			