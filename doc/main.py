import numpy as np
import matplotlib.pyplot as plt

# Filename of recording
filename = 'clap_dc_offset.raw'

# Configuration variables
dc_offset_factor = 0.9999
envelope_decay_factor = 0.999
onset_threshold = 1000
onset_ratio_threshold = 1.58
transient_timeout = 0.1
transient_decay_threshold_factor = 0.25

#Samplerate, should match the setting in your ESPHome yaml file
fs = 16000

# Get the signal
signal = np.fromfile(filename, dtype=np.int16)
t = np.arange(len(signal)) / fs

fig1, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex='col')

ax1.plot(t, signal, label='input signal')
ax1.legend()

# Remove DC offset
dc_offset = 0
for idx,sample in enumerate(signal):
    dc_offset = dc_offset_factor*dc_offset + (1.0-dc_offset_factor)*sample
    sample -= dc_offset
    signal[idx] = np.clip(sample, -32767, 32767)

ax2.plot(t, signal, label='offset removed')

# Take absolute value
abs_signal = abs(signal)
ax2.plot(t, abs_signal, label='absolute value')
ax2.legend()

# Calculate envelope
envelope = []
current_value = 0
for sample in abs_signal:
    current_value *= envelope_decay_factor
    if sample > current_value:
        current_value = sample
    envelope.append(current_value)
ax3.plot(t, envelope, label='envelope')
ax3.plot(t, [onset_threshold]*len(t), label='onset_threshold', linestyle='--', color='gray')
ax3.legend()

# Search for onset
previous_envelope = 0
onset = None
transient_peak = None

ratio = []
for idx, envelope_sample in enumerate(envelope):
    if previous_envelope > 0:
        ratio.append(envelope_sample / previous_envelope)
    else:
        ratio.append(1)
    previous_envelope = envelope_sample

    if onset is None and envelope_sample > onset_threshold and ratio[-1] > onset_ratio_threshold:
        onset = idx
        print(idx)
        transient_peak = envelope_sample
        ax3.axvline(t[onset], color='gray', linestyle='--')
        ax4.axvline(t[onset], color='green', linestyle='--')
        ax3.text(t[onset], max(envelope), "onset", color='gray')
        ax4.text(t[onset], max(ratio), "onset", color='green')

        ax3.axvline(t[onset]+transient_timeout, color='gray', linestyle='--')
        ax4.axvline(t[onset]+transient_timeout, color='gray', linestyle='--')
        ax3.text(t[onset]+transient_timeout, max(envelope)*0.9, "transient_timeout", color='gray')
        ax4.text(t[onset]+transient_timeout, max(ratio)*0.9, "transient_timeout", color='gray')

    if onset is not None:
        # We've detected an onset. Either wait for the transient to lower or timeout
        if envelope_sample > transient_peak:
            transient_peak = envelope_sample
        transient_time = t[idx] - t[onset]

        if transient_time > transient_timeout:
             # Timeout
            onset = None
            print('timeout')
        if envelope_sample < transient_peak * transient_decay_threshold_factor:
            ax4.axvline(t[idx], color='red')
            ax4.text(t[idx], max(ratio)/2, "clap detected", color='red')
            onset = None
            print('clap')

ax4.plot(t, ratio, label='ratio')
ax4.plot(t, [onset_ratio_threshold]*len(t), label='onset_ratio_threshold', linestyle='--', color='gray')
ax4.legend()

ax4.set_xlabel('seconds')
ax1.set_title('Clap detection algorithm')
plt.show()
