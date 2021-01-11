
import os
from pydub import AudioSegment
import scipy.io.wavfile as wvf
import numpy as np

from Song import Song
from mix_songs import mix_songs
from Mixer import Mixer


def read_wav_songs(dir_name):
    song_names = os.listdir(dir_name)
    wav_songs = [wvf.read(dir_name + name) for name in song_names if name[-3:] == "wav"]
    return wav_songs


def mp3_to_wav(dir_name):

    song_names = os.listdir(dir_name)
    song_names = only_mp3_songs(song_names)
    # print(song_names, len(song_names))

    for name in song_names:
        wav_song = AudioSegment.from_mp3(dir_name + name)

        dst = dir_name + name.strip("mp3") + "wav"
        wav_song.export(dst, format="wav")
    

def wav_to_mp3(file_name, output_path):
    wav_song = AudioSegment.from_wav(file_name)
    wav_song.normalize()
    wav_song.export(output_path)
    

def only_mp3_songs(song_names):
    return [name for name in song_names if name[-3:]=="mp3"]



if __name__ == "__main__":
    
    # mp3_to_wav all songs
    # mp3_to_wav("./songs/128/")

    # read in the MP3 Songs and convert them to wav
    wav_songs = read_wav_songs("./songs/128_test/")
    # print(wav_songs[0])

    # create song objects
    songs = [Song(wav_song) for wav_song in wav_songs]

    # mix song objects together to create a new song object. I KNOW THIS WORKS!!!
    # mix = mix_songs(songs[0], songs[1])

    mixer = Mixer(songs, 22050)

    # print(mixer.sample_frequency, mixer.mix[100000:100200])
    # output mix to file
    dst = "./songs/mixes/output_mix_128.wav"
    wvf.write(dst, mixer.sample_frequency, mixer.mix)

    # convert wav to mp3
    wav_to_mp3(dst, "./songs/mixes/output_mix_128.mp3")

