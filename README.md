# testing-motoneuron-types

Repo for running a simulation of slow (S) vs. fast fatigue-resistant (FR) motoneurons. Adapted from Jones & Bawa, 1995.

### Getting Started 

All simulations are run in NEURON. Instructions for setting up NEURON can be found [here](https://www.neuron.yale.edu/neuron/download). Once installed, NEURON must be configured by running the following from the home directory: 

```nrnivmodl mod_files```

The rest of the required packages can be found in `requirements.txt` and can be installed using:

```pip install -r requirements.txt``` 

### Run simulation

```compareSvsFR_EPSPProperties.py```: Plots a comparison of EPSPs (of same amplitude), and EPSP summation in subthreshold and suprathreshold case. 

```compareSvsFR_Excitability.py```: Finds the rheobase for S vs. FR motoneurons as a function of background input. 

Both can be run using ```python scripts/[script_name].py```. 