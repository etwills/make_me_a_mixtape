
# import bpm_detector
import numpy as np

"""
Data structure for a song read from a wav file 
# TODO: fix so the class can handle stereo and mono waves 
"""
class Song:

    def __init__(self, wav_song):
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
        return 128
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

        # for i in range(len(self.song)):
        #     sample = self.song[i]
        #     if (sample[0] != 0 or sample[1] != 0):
        #         return i

        cutoff = int(8 * self.samples_per_beat)

        # find the gradient of the song
        grad = np.array([self.song[i+1] - self.song[i] for i in range(cutoff)])
        average_grad = np.array([val[0]/2 + val[1]/2 for val in grad])
    
        # find the peak on the right hand side. Not sure if this might be a problem later on
        peak_idx = np.where(average_grad == max(average_grad))
    
        # start from the discovered peak
        first_peak = peak_idx[0][0]
        while first_peak - self.samples_per_beat >= 0:
            # work backwards until you can't go further
            first_peak -= self.samples_per_beat
    
        # now we're at the true first peak. the phase shift is then 
        phase_shift = first_peak  # could probably adjust to be more lenient
        return int(phase_shift)
                

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
       




