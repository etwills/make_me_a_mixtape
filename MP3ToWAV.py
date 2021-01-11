# import sys
# sys.path.append('/path/to/ffmpeg')

from os import path
from pydub import AudioSegment

class MP3ToWAV:

    def __init__(self, songs):
        self.songsMP3 = songs
        self.songsWAV = []

    def convert(self):

        for song in self.songsMP3:

            # files                                                                         
            src = song
            # dst = "test.wav"

            # convert wav to mp3                                                            
            sound = AudioSegment.from_mp3(src)
            self.songsWAV.append(sound)
            # sound.export(dst, format="wav")

        # return wav_songs

    def get_wav(self):
        return self.songsWAV


    def get_mp3(self):
        return self.songsMP3


# converter = MP3ToWAV(["./songs/ANNA - Hidden Beauties (Original Mix).mp3"])
# converter.convert()


def mp3_to_wav(song):

        # convert wav to mp3                                                            
        sound = AudioSegment.from_mp3(song)

        return sound
