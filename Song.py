
# import bpm_detector
import numpy as np

"""
Data structure for a song read from a wav file 
# TODO: fix so the class can handle stereo and mono waves 
"""
class Song:

    def __init__(self, wav_song, name):
        self.song_name = name
        self.sample_rate = wav_song[0]
        self.song = wav_song[1]
        self.key = self.find_key()
        self.bpm = self.find_bpm()

        beats_per_second = self.bpm/60
        self.samples_per_beat = self.sample_rate / beats_per_second
        self.start_index = self.get_start_point()
        self.song = self.song[self.start_index:]
        

    """
    Sets the song if one wasn't given initially
    """
    def set_song(self, song_array):
        pass


    """
    Finds the bpm of a song
    # TODO fix to implement any BPM
    """
    def find_bpm(self):

        # bpm, corr = bpm_detector(self.song, self.sample_rate) 

        # return bpm
        return 125
        # pass


    """
    Finds the key of the song
    # TODO fix this to not be the default 
    """
    def find_key(self):
        return "C"


    """
    Get discrete fourier transform of the array
    """
    def dft(self):
        pass

    
    """
    Gets the start index of the song, i.e. the first entry in the array of the song that is not zero on both channels
    This is useful because it allows 
    """
    def get_start_point(self):

        # # for i in range(len(self.song)):
        # #     sample = self.song[i]
        # #     if (sample[0] != 0 or sample[1] != 0):
        # #         return i

        # cutoff = int(8 * self.samples_per_beat)

        # find the gradient of the song
        # grad = np.array([self.song[i+1] - self.song[i] for i in range(cutoff)])
        # average_grad = np.array([val[0]/2 + val[1]/2 for val in grad])
    
        # # find the peak on the right hand side. Not sure if this might be a problem later on
        # peak_idx = np.where(average_grad == max(average_grad))
    
        # # start from the discovered peak
        # first_peak = peak_idx[0][0]
        # while first_peak - self.samples_per_beat >= 0:
        #     # work backwards until you can't go further
        #     first_peak -= self.samples_per_beat
    
        # # now we're at the true first peak. the phase shift is then 
        # phase_shift = first_peak  # could probably adjust to be more lenient
        # return int(phase_shift)
       
        cutoff = int(8 * self.samples_per_beat)

        sample = self.song[0:cutoff]

        fft_left = np.fft.fft(sample[0:, 0])
        fft_right = np.fft.fft(sample[0:, 1])
        fft_freq = np.fft.fftfreq(sample.shape[0], 1/self.sample_rate)

        fft_left[fft_freq < 0] = 0
        fft_left[fft_freq > 500] = 0

        fft_right[fft_freq < 0] = 0
        fft_right[fft_freq > 500] = 0

        only_low_left = np.fft.ifft(fft_left).real
        only_low_right = np.fft.ifft(fft_right).real
        sample = np.array([only_low_left, only_low_right]).transpose()
        sample = sample.astype("i2")

        # find the gradient of the song
        grad = np.array([sample[i+1] - sample[i] for i in range(cutoff - 1)], dtype="float64")
        # grad = np.array([self.song[i+1] - self.song[i] for i in range(cutoff)], dtype="float64")
        # average_grad = np.array([val[0]/2 + val[1]/2 for val in grad])


        # sample = self.song[0:8*int(self.samples_per_beat)]
        fst = self.find_first_beat(grad, self.bpm, self.sample_rate)
        return fst
    
    """
    Finds the first beat of the song to try and align the three
    TODO fix this so that it can better detect kick drum peaks that aren't so high
    """
    def find_first_beat(self, signal, bpm, sf):
    
        bps = bpm/60  # beats per second
        spb = int(sf/bps)  # samples per beat
    
        peak_idxs = set()   # store the ids of discovered peaks
        
        for i in [1,2,4]:
            idxs = self.detect_peaks(signal, int(spb/i))
            for k in idxs:
                peak_idxs.add(k)  # Look for different beat timings
        
        signal = signal.astype("float64")
        mono_signal = np.mean(signal, axis=1)  # Average the two channels together
        
        peak_idxs = np.sort(np.array(list(peak_idxs)))
        print(peak_idxs)
        peak_amps = mono_signal[peak_idxs]  # get all the values of the peaks
        # print(peak_amps)
        max_peak = np.max(peak_amps)
        mean_peak = np.mean(peak_amps)  # average peak amplitude
        std_peak = np.std(peak_amps)  # std of peak
                      
        for i in peak_idxs:
            # Not having this condition below allows any peak to be chosen. I don't like that
            # With this condition it should be guaranteed to match some two beats, either exact or offbeats. No some small peaks get matched
            # So I could add a test that looks from this first peak to see if other peaks are an integer multiple of beats per second away
            if mono_signal[i] >= max_peak - std_peak:  # If the peak value is within one standard deviation of the peak mean
                
                if i > 100:
                    print("mean - sd", mean_peak - std_peak)
                    print("peak chosen", i)
                    return i  # the first index we can find
    


    def detect_peaks(self, signal, resolution):
    
        r = resolution
        N = len(signal)
        k = int(np.floor(N/r))  # How many strips are we computing the average energy over
        
        signal = signal.astype("float64")
        mono_signal = np.mean(signal, axis=1)  # Average the two channels together
        mean_amp = np.mean(mono_signal)  # the average value for the signal across both channel
        std_amp = np.std(mono_signal)  # find the standard deviation in the signal
        # max_amp = np.max(mono_signal) 
        
        peak_idxs = []  # store the indexs of discovered peaks
        
        # For each block
        for i in range(k):
            # Find the peak value in the block
            sample = mono_signal[i*r:(i+1)*r]
            peak = np.max(sample) 
            
            
            # If the peak exceeds the threshold, record it as a beat. We do this to not detect 0s as part of the beat
            if peak >= mean_amp + 2 * std_amp:
                idx = np.where(sample == peak)[0][0]
                peak_idxs.append(i*r + idx)  # find the first location of the peak
        
        return peak_idxs


    """
    Downsample the song by a certain factor, to make the files smaller
    """
    def downsample(self, downsample_factor = 2):
        
        assert self.sample_rate % downsample_factor == 0  # check that the downsample factor divides the sample rate
        
        # change the song
        self.song = np.array([self.song[i] for i in range(len(self.song)) if i%downsample_factor == 0])
        
        # change the sampling rate variables
        self.sample_rate = self.sample_rate / downsample_factor
        self.samples_per_beat = self.samples_per_beat / 2


       




