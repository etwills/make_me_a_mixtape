import numpy as np

"""
Return the song with the frequencies cut from the given range
:param signal: a numpy array either 2D or 1D, or a normal array
:rtype: numpy ND array with the cut signal
"""
def filter_freqs(signal, sample_rate, type = "high_pass", cutoff = 200):
    
    # make sure we're working with a numpy array
    if not isinstance(signal, np.ndarray):
        signal = np.array(signal)

    # if the signal is stereo
    if signal.shape[1] == 2:
        fft_amps_left = np.fft.fft(signal[0:, 0])  # get the left channel transform
        fft_amps_right = np.fft.fft(signal[0:, 1])   # get the right channel transform

        W = np.fft.fftfreq(fft_amps_left.size, 1/sample_rate)   # Get the frequencies

        fft_amps_left[W < cutoff] = 0  
        fft_amps_right[W < cutoff] = 0

        # Recreate the signals and only take the real component. data type should be float64
        cut_left_signal = np.fft.ifft(fft_amps_left).real
        cut_right_signal = np.fft.ifft(fft_amps_right).real

        new_signal = np.array([cut_left_signal, cut_right_signal]).transpose() 

        return new_signal  # I think we want to return a list

    # otherwise the signal is mono
    else:
        pass