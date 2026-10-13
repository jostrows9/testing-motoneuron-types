import numpy as np
from neuron import h
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import sys
sys.path.append('../testing-motoneuron-types/')
from cells import Motoneuron

def measure_excitability(mn_type: str = 'slow', stim_freq: int = 0, plot: bool = False):
    """
    Measure rheobase and extract spike features from the first action potential.
    """

    cur_amps = list(range(1, 40000, 500)) 
    divisor = 10000

    dt = 0.025  # ms

    for cur_amp in cur_amps:
        print(f'Measuring excitability for {mn_type} MN with current amplitude: {cur_amp / divisor:.4f} nA and stimulation frequency: {stim_freq} Hz')

        np.random.seed(0)

        h.load_file("stdrun.hoc")

        mn = Motoneuron(mn_type=mn_type)

        t_vec = h.Vector().record(h._ref_t)
        v_vec = h.Vector().record(mn.soma(0.5)._ref_v)

        stim = h.IClamp(mn.soma(0.5))
        stim.delay = 200
        stim.dur = 500
        stim.amp = cur_amp / divisor
        
        if stim_freq != 0:
            weights, inputs = mn.build_stim_input(stim_freq)

        h.finitialize(-70)
        h.tstop = 600
        h.run()

        if cur_amp == 1:
            t = t_vec.to_python()
        v = np.array(v_vec)

        # Detect spikes
        peaks, _ = find_peaks(v, height=0)

        if len(peaks) > 0:
            rheobase = cur_amp / divisor

            first_peak_idx = peaks[0]
            first_peak_v = v[first_peak_idx]
            first_peak_t = t[first_peak_idx]

            dvdt = np.gradient(v, dt)

            threshold_candidates = np.where(
                (dvdt > 10) &
                (np.arange(len(v)) < first_peak_idx)
            )[0]

            if len(threshold_candidates) > 0:
                threshold_idx = threshold_candidates[0]
            else:
                threshold_idx = first_peak_idx

            threshold_v = v[threshold_idx]
            threshold_t = t[threshold_idx]

            spike_amplitude = first_peak_v - threshold_v
            half_height = threshold_v + spike_amplitude / 2

            left_crossings = np.where(v[:first_peak_idx] >= half_height)[0]
            right_crossings = np.where(v[first_peak_idx:] <= half_height)[0]

            if len(left_crossings) > 0 and len(right_crossings) > 0:
                left_idx = left_crossings[0]
                right_idx = first_peak_idx + right_crossings[0]
                spike_width_ms = t[right_idx] - t[left_idx]
            else:
                spike_width_ms = np.nan

            search_end = min(first_peak_idx + int(200 / dt), len(v))

            ahp_region = v[first_peak_idx:search_end]
            ahp_min_idx_local = np.argmin(ahp_region)
            ahp_min_idx = first_peak_idx + ahp_min_idx_local
            ahp_min_v = v[ahp_min_idx]
            resting_v = np.mean(v[:int(400 / dt)])
            ahp_depth = resting_v - ahp_min_v

            # AHP duration:
            # time until membrane returns to resting potential
            recovery_candidates = np.where(
                v[ahp_min_idx:] >= resting_v
            )[0]

            if len(recovery_candidates) > 0:
                recovery_idx = ahp_min_idx + recovery_candidates[0]
                ahp_duration_ms = t[recovery_idx] - t[first_peak_idx]
            else:
                ahp_duration_ms = np.nan

            latency_ms = threshold_t - stim.delay

            n_spikes = len(peaks)

            firing_rate_hz = n_spikes / (stim.dur / 1000)

            features = {
                "rheobase": rheobase,
                "spike_threshold": threshold_v,
                "spike_peak": first_peak_v,
                "spike_amplitude": spike_amplitude,
                "spike_width_ms": spike_width_ms,
                "ahp_min": ahp_min_v,
                "ahp_depth": ahp_depth,
                "ahp_duration_ms": ahp_duration_ms,
                "latency_to_first_spike_ms": latency_ms,
                "firing_rate_hz": firing_rate_hz,
                "n_spikes": n_spikes,
            }

            if plot:

                plt.figure(figsize=(10, 4))

                plt.plot(t, v, label='Membrane voltage')
                plt.scatter(threshold_t, threshold_v, label='Threshold')
                plt.scatter(first_peak_t, first_peak_v, label='Spike peak')
                plt.scatter(t[ahp_min_idx], ahp_min_v, label='AHP minimum')

                plt.xlabel('Time (ms)')
                plt.ylabel('Voltage (mV)')
                plt.legend()
                plt.tight_layout()
                

            return features

    # No spike case
    return {
        "rheobase": np.nan,
        "spike_threshold": np.nan,
        "spike_peak": np.nan,
        "spike_amplitude": np.nan,
        "spike_width_ms": np.nan,
        "ahp_min": np.nan,
        "ahp_depth": np.nan,
        "ahp_duration_ms": np.nan,
        "latency_to_first_spike_ms": np.nan,
        "firing_rate_hz": 0,
        "n_spikes": 0,
    }


if __name__ == '__main__':
    stim_freqs = [x for x in range(0, 1200, 200)]
    slow_mn_rheobase = []
    fr_mn_rheobase = []

    for stim_freq in stim_freqs: 
        slow_mn_rheobase.append(measure_excitability(mn_type='slow', stim_freq=stim_freq, plot=False)['rheobase'])
        fr_mn_rheobase.append(measure_excitability(mn_type='fr', stim_freq=stim_freq, plot=False)['rheobase'])

    slow_mn_rheobase = np.array(slow_mn_rheobase)
    fr_mn_rheobase = np.array(fr_mn_rheobase)

    plt.plot(stim_freqs, slow_mn_rheobase, marker='o', label='Slow MN')
    plt.plot(stim_freqs, fr_mn_rheobase, marker='o', label='FR MN')
    plt.legend()
    plt.ylabel('Estimated rheobase (nA)')
    plt.xlabel('Stimulation frequency (Hz)')
    plt.title('Stimulation-evoked change in rheobase per MN type')
    
    plt.figure()
    plt.plot(stim_freqs, (slow_mn_rheobase-slow_mn_rheobase[0])/slow_mn_rheobase[0], marker='o', label='Slow MN')
    plt.plot(stim_freqs, (fr_mn_rheobase-fr_mn_rheobase[0])/fr_mn_rheobase[0], marker='o', label='FR MN')
    plt.legend()
    plt.ylabel('% change in rheobase (nA)')
    plt.xlabel('Stimulation frequency (Hz)')
    plt.title('Stimulation-evoked % change in rheobase per MN type')

    plt.figure()
    plt.plot(stim_freqs, (slow_mn_rheobase)/slow_mn_rheobase[0], marker='o', label='Slow MN')
    plt.plot(stim_freqs, (fr_mn_rheobase)/fr_mn_rheobase[0], marker='o', label='FR MN')
    plt.legend()
    plt.ylabel('Normalized change in rheobase (nA)')
    plt.xlabel('Stimulation frequency (Hz)')
    plt.title('Normalized stimulation-evoked change in rheobase per MN type')

    plt.figure()
    plt.plot(stim_freqs, slow_mn_rheobase-slow_mn_rheobase[0], marker='o', label='Slow MN')
    plt.plot(stim_freqs, fr_mn_rheobase-fr_mn_rheobase[0], marker='o', label='FR MN')
    plt.legend()
    plt.ylabel('Baseline-subtracted change in rheobase (nA)')
    plt.xlabel('Stimulation frequency (Hz)')
    plt.title('Stimulation-evoked change in rheobase per MN type')

    plt.show()