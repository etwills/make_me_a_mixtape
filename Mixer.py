import numpy as np
import function_tools as ft

from Song import Song
from filter_freqs import filter_freqs


"""
The mixer that mixes different songs together
This class:
- Has several song objects
- Decides the order to mix the songs
- For each song decides how they should be mixed
- 
"""
class Mixer:

    def __init__(self, song_list, desired_samp_freq = 44100):
        self.songs = self.make_all_same(song_list, desired_samp_freq)
        self.sample_frequency = desired_samp_freq
        self.bpm = 125
        self.samples_per_beat = self.sample_frequency / (self.bpm/60)  # samples per second divided by beats per second
        self.samples_per_bar = self.samples_per_beat * 4  # Assuming 4/4 timing

        self.mix = []
        self.mix_all()


    """
    Makes all songs have the same sample frequency by downsampling any that are too high
    """
    def make_all_same(self, song_list, desired_samp_rate):

        for song in song_list:
            assert song.sample_rate % desired_samp_rate == 0
            downsample_factor = int(song.sample_rate/desired_samp_rate)
            song.downsample(downsample_factor)

        return song_list


    """
    Returns the songs in the optimal order to mix
    """
    def order_to_mix(self):
        return self.songs


    """
    Returns an array of mixing types dictating how to mix song n with n+1
    """
    def how_to_mix(self):
        return ["sin_fade" for i in range(len(self.songs) - 1)] # default right now to just using 'fade' type


    """
    # TODO fix this so that songs are mixed so that "energy" is compatible
    Looks at the BPM of both songs and decides on a suitable place to mix the two songs
    """
    def get_mix_points(self):
        
        mix_points = []

        for song in self.songs:
            # get the BPM of each song and the sampling rate. These should always be the same though

            # Using the BPM and sampling rate work out what index would be a good place to mix
            # The best thing to do would be to look at the actual wavform and determine the best place to mix
            
            # how many bars approximately to 90% of the song
            k = int(0.85 * len(song.song) / self.samples_per_bar)
            # want to match from the end of a song, so how far back should we go
            mix_index = len(song.song) - int(k * self.samples_per_bar) 

            mix_points.append(mix_index)

        return mix_points
        # return [int(np.floor(0.9 * len(self.songs[i]))) for i in range(len(self.songs) - 1)]


    """
    Mixes all of the songs in the list together
    """
    def mix_all(self):
        
        # get the songs to be mixed in the right order
        songs = self.order_to_mix()

        # get the way to mix each song
        types = self.how_to_mix()

        # get the points to mix each song
        mix_indices = self.get_mix_points()

        # start the mix off by dividing everything by two. This will have small numpy arrays in it
        current_mix = [val/2 for val in self.songs[0].song]

        # mix each song into the current mix
        for i in range(len(songs) - 1):
            next_song = songs[i+1].song/2
            current_mix = self.mix_next_song(current_mix, next_song, types[i], mix_indices[i])

        self.mix = np.array(current_mix)

        # print(self.mix.shape)

        # print(self.mix[10000:20000])
        
        # clean the mix by scaling and converting everything to 16bit ints
        self.scale_values()

        # convert everything to integers
        self.mix = self.mix.astype("i2")


    """
    Takes the current mix that is being built up and mixes the next song into it
    :param current_mix: an array containing the current mix being built up
    :type current_mix: array
    :param next_song: an array with the next song to be mixed
    :type next_song: numpy 1D or 2D array
    :param mix_type: the technique to mix the two songs
    :type mix_type: string
    :param mix_index: how far from the end of the curent mix should we mix the next song in from
    :type mix_index: int
    """
    def mix_next_song(self, current_mix, next_song, mix_type, mix_index):
        # naively just overlap the two files and return the single file
        # we also scale the songs down by a lot though

        # # add the first song up until the mix_index
        # if mix_type = "first_song":

        # we should have the current mix here already containing everything in the first song
        # start from mix_index back into the current mix
        
        start_from = len(current_mix) - mix_index    
        
        print(mix_type)

        if mix_type == "sin_fade":
        
            mid = int(np.floor(mix_index/2)) # half way from the end of the song. The point where both songs are maxed

            # print(len(current_mix), mix_index, mid)
            for i in range(mid):
                # fade the song in according to a smooth sin 
                fade_factor = np.sin(np.pi/2 * (i / mid))
                current_mix[start_from + i] = current_mix[start_from + i] + fade_factor * next_song[i]

            # TODO fix this so that it doesn't sound like the first song ends so abruptly
            for i in range(mid, mix_index):
                # Fade the first song out according to a cos function
                fade_factor = max(np.cos((5 * np.pi/12) * (i - mid)/(mid)), 0)  
                current_mix[start_from + i] = fade_factor * current_mix[start_from + i] + next_song[i]


        # bring one sone in and the other out quickly with a low frequency cut
        elif mix_type == "low_cut":

            # start from mix_index back into the current mix
            start_from = len(current_mix) - mix_index
            
            # How many bars do we have remaining? Used to decide how much frequency cut to use
            num_bars = np.floor(mix_index / self.samples_per_bar)
            print(num_bars)

            # Ideally we want 12 bars to mix it all
            first = int(self.samples_per_bar * 15)  # first stage to fade the first song in
            second = int(self.samples_per_bar * 16) # index to cut the frequency of the first song
        
            # Use Fourier Transform to cut the lows out of the second song while we mix it in
            no_bass_second = filter_freqs(next_song[0:second], self.sample_frequency)
            
            for i in range(first):
                # fade the second song without any bass in according to a smooth sin 
                fade_factor = np.sin(np.pi/2 * (i / first))
                current_mix[start_from + i] = current_mix[start_from + i] + fade_factor * no_bass_second[i]

            # cut all lows from the first song until the end of the song
            no_bass_first = filter_freqs(current_mix[start_from + first:], self.sample_frequency) 
            # print(len(no_bass_first))
            # print(len(no_bass_second))
            # print(first, second)
            # print(mix_index)
            # Mix both low cut songs together
            for i in range(first, second):
                current_mix[start_from + i] = no_bass_first[i] + no_bass_second[i]


            # Bring the lows in from the second song
            # Mix-index - first is the length of no_bass_first
            for i in range(second, mix_index - second): 
                # Fade the first song out according to a cos function 
                # TODO make sure this works properly
                fade_factor = max(np.cos((5 * np.pi/12) * i/(mix_index - second)), 0)  
                current_mix[start_from + i] = fade_factor * no_bass_first[i] + next_song[i]


        # add the rest of the song on
        for i in range(mix_index, len(next_song)):
            current_mix.append(next_song[i])    
        

        return current_mix



    # """
    # Overlaps two arrays of arrays
    # """
    # def overlap_arrays(array_one, array_two, overlap_index):

    #     new_array = []

    #     # one = array_one.aslist

    #     n = len(array_one)
    #     m = len(array_two)

    #     # add song one up until overlap point
    #     for i in range(overlap_index):
    # #         if i%10 == 0:
    # #             print(array_one[i], array_one[i][0], array_one[i][1])
    #         new_array.append(array_one[i])

    #     # from overlap point mix both songs 
    #     for i in range(0, n - overlap_index):
            
    #         fst = array_one[overlap_index + i]
    #         scnd = array_two[i]
    #         val = add_together(fst, scnd)
    #         new_array.append(val)

    #     # after overlap point add song two
    #     for i in range(n - overlap_index, m):
    #         new_array.append(array_two[i])

    # #     print(new_array[100000:100100])
    #     return np.array(new_array)


    # def add_together(array_one, array_two):

    #     fst = array_one[0] + array_two[0]
    #     scnd = array_one[1] + array_two[1]
    #     # squish between -1 and 1
    #     return [fst, scnd]
    #     # return [squish(fst), squish(scnd)]


    # # def squish(val):
    # #     val = min(32767, val)
    # #     val = max(-32767, val)
    # #     return val


    """
    Goes through and scales all the values in the mix to be within the right range so that no clipping occurs
    """
    def scale_values(self, scale_factor = 1, max_output_amp = 10000):
        # max values in each channel and overall
        max_left = max([val[0] for val in self.mix])
        max_right = max([val[1] for val in self.mix])
        peak = max(max_left, max_right)

        # scale all the values to avoid clipping
        self.mix = max_output_amp * (self.mix/(peak*scale_factor))

       

    # """
    # Takes two arrays and mixes them from a certain point so as not to cause any clipping
    # To stop clipping it's probably just enough to scale all the values back by a lot
    # """
    # def mix(array_one, array_two, index):




    