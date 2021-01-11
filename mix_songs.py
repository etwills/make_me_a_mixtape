import numpy as np

from Song import Song



"""
Takes two Song objects and mixes them together
Right now it just naively overlaps songs at some point
"""
def mix_songs(song_one:Song, song_two:Song):
    
    # naively just overlap the two files and return the single file
    # we also scale the songs down by a lot though

    # cutoff1 = 44100 * 50
    # song_one.song = song_one.song[0:cutoff]
    # song_two.song = song_two.song[0:cutoff]

    # get the index to start mixing from
    overlap_index = int(np.floor(len(song_one.song) * 0.8859))

    print(len(song_one.song), len(song_two.song), overlap_index)
    print(len(song_one.song)/(44100*60), len(song_two.song)/(44100*60), overlap_index/(44100*60))

    # mix the two songs
    new_song = overlap_arrays(song_one.song, song_two.song, overlap_index)

    # scale the values to be in the correct size
    new_song = scale_values(new_song)

    # convert the song back to the correct data type
    new_song = new_song.astype("i2")

    print(len(new_song), len(new_song)/(44100*60))

    # make a new song object to return
    new_song = Song([song_one.sample_rate, new_song])

    return new_song


"""
Overlaps two arrays of arrays
"""
def overlap_arrays(array_one, array_two, overlap_index):

    new_array = []

    # reduce the intensity of both signals
    array_one = array_one/2
    array_two = array_two/2

    n = len(array_one)
    m = len(array_two)

    # add song one up until overlap point
    for i in range(overlap_index):
#         if i%10 == 0:
#             print(array_one[i], array_one[i][0], array_one[i][1])
        new_array.append(array_one[i])

    # from overlap point mix both songs 
    for i in range(0, n - overlap_index):

        val = array_one[overlap_index + i] + array_two[i]
        new_array.append(val)

    # after overlap point add song two
    for i in range(n - overlap_index, m):
        new_array.append(array_two[i])

    return np.array(new_array)

"""
Overlaps the two arrays as one channel
"""
def overlap_mono(array_one, array_two, overlap_index):
    new_array = []

    # reduce the intensity of both signals
    array_one = array_one/2
    array_two = array_two/2

    n = len(array_one)
    m = len(array_two)

    # add song one up until overlap point
    for i in range(overlap_index):
#         if i%10 == 0:
#             print(array_one[i], array_one[i][0], array_one[i][1])
        new_array.append(np.mean(array_one[i]))

    # from overlap point mix both songs 
    for i in range(0, n - overlap_index):

        val = [np.mean(array_one[overlap_index + i]) + np.mean(array_two[i])]
        new_array.append(val)

    # after overlap point add song two
    for i in range(n - overlap_index, m):
        new_array.append(np.mean(array_two[i]))

    return np.array(new_array)



"""
Goes through and scales all the values in the mix to be within the right range so that no clipping occurs
"""
def scale_values(song, scale_factor = 1, max_output_amp = 10000):
    # max values in each channel and overall
    max_left = max([val[0] for val in song])
    max_right = max([val[1] for val in song])
    peak = max(max_left, max_right)

    # scale all the values to avoid clipping
    new_song = max_output_amp * (song/(peak*scale_factor))

    return new_song

# """
# Takes two arrays and mixes them from a certain point so as not to cause any clipping
# To stop clipping it's probably just enough to scale all the values back by a lot
# """
# def mix(array_one, array_two, index):


