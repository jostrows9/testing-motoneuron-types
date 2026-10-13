from neuron import h

class Cell:
	""" Interface class to build different types of cells. """

	def __init__(self):
		""" Object initialization. """
		# Neuron cell - source of netcons
		self.cell = None

	def __del__(self):
		""" Object destruction. """
		pass
