# ALWAYS IMPORT SOUND BEFORE ANYTHING ELSE

# MAKE SURE ALL NON-STANDARD LIBRARY IMPORTS IN THIS FILE ARE
# DONE AFTER pygame.init()

import pygame
import random
import os
import math

music_muted = False
sfx_muted = False

CHANNEL_COUNT = 16
pygame.mixer.init(22050, -16, CHANNEL_COUNT, 64)
pygame.mixer.set_num_channels(CHANNEL_COUNT)
pygame.init()

channels = [pygame.mixer.Channel(channel) for channel in range(CHANNEL_COUNT)]
soundsets = []

import debug

note_strings = ['a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#']
A2 = 0  # 3 for the third octave on the piano
AS2 = 1  # S stands for Sharp, so AS is A-Sharp
B2 = 2
C2 = 3
CS2 = 4
D2 = 5
DS2 = 6
E2 = 7
F2 = 8
FS2 = 9
G2 = 10
GS2 = 11
A3 = 12
AS3 = 13
B3 = 14
C3 = 15
CS3 = 16
D3 = 17
DS3 = 18
E3 = 19
F3 = 20
FS3 = 21
G3 = 22
GS3 = 23

normal_scale = None
ghost_note = None


def update():
    global normal_scale
    global ghost_note

    for soundset in soundsets:
        if soundset.limited:
            for i in reversed(range(len(soundset.durations))):
                if soundset.durations[i] <= 0:
                    del soundset.durations[i]
                else:
                    soundset.durations[i] -= 1

    music_position = pygame.mixer.music.get_pos()
    scale_num = (music_position % music_length) // chord_length
    normal_scale = normal_scales[scale_num]
    ghost_note = ghost_notes[scale_num]

    ghost_volume = music_position % 2000
    ghost_volume = -0.125 * math.sin((0.18 * math.pi / 180) * ghost_volume) + 0.75

    ghost_note.set_volume(ghost_volume)
    debug.debug(ghost_volume)


def load_music(path):
    pygame.mixer.music.load(pathify(path))


def play_music():
    pygame.mixer.music.play(-1)


def set_music_volume(volume):
    pygame.mixer.music.set_volume(volume)


def pathify(string):
    return os.path.join("sounds", string + ".wav")


def load(string):
    return pygame.mixer.Sound(pathify(string))


def play(sound, volume=1.0):
    channel = pygame.mixer.find_channel()
    if channel:
        channel.set_volume(volume)
        channel.play(sound)


def load_numbers(path, count):
    """Loads a set of sounds whose filenames are the same except they
    contain incrementing numbers.

    path is a string which should contain a %i representing where the number is.
    count is the amount of sounds.
    """
    paths = [path % (number + 1) for number in range(count)]
    return SoundSet(paths)


def load_strings(path, strings):
    """Loads a set of sounds whose filenames are the same, except they
    all have one part that varies.

    path is the part of the string that stays the same.  must contain a %s
    strings is a list of strings, containing all the differences.
    """
    paths = [path % string for string in strings]
    return SoundSet(paths)


class SoundSet:
    def __init__(self, paths):
        self.sounds = [load(path) for path in paths]
        self.variants = len(self.sounds)
        self.lastPlayed = 0
        soundsets.append(self)

        self.limited = False
        self.limit = 0
        self.durations = []
        self.sound_duration = 0

    def play(self, sound_id, volume=1.0, force_play=False):
        if not force_play:
            if sfx_muted:
                return

            if self.limited and len(self.durations) >= self.limit:
                return

            for duration in self.durations:
                if duration > self.sound_duration - 2:
                    return

        if volume > 1.0:
            volume = 1.0

        play(self.sounds[sound_id], volume)
        self.lastPlayed = sound_id

        if self.limited:
            self.durations.append(self.sound_duration)

    def play_random(self, volume=1.0, force_play=False):
        if self.variants == 1:
            sound_id = 0
        else:
            sound_id = random.randint(0, self.variants - 1)
            while sound_id == self.lastPlayed:
                sound_id = random.randint(0, self.variants - 1)

        self.play(sound_id, volume, force_play)

    def set_volumes(self, volume):
        for sound in self.sounds:
            sound.set_volume(volume)

    def set_sound_limit(self, limit, sounds_length):
        """Limits the amount of sounds the soundset can play at once.

        sound_duration is an approximation of the sound's lenght in frames.
        can't automate sound_duration since pygame's sound.length() returns
        to the nearest second.
        """
        self.limited = True
        self.limit = limit
        self.sound_duration = sounds_length


class Scale:
    def __init__(self, instrument, notes):
        self.instrument = instrument
        self.notes = notes
        self.octaves = len(soundsets)

    def play_tonic(self, volume=1.0, force_play=False):
        """Plays the first note in the scale."""
        note = self.notes[0]
        soundset = self.instrument.octaves[note // 12]
        note %= 12
        soundset.play(note, volume, force_play)

    def play_random(self, volume=1.0, force_play=False):
        note = random.choice(self.notes)
        soundset = self.instrument.octaves[note // 12]
        note %= 12
        soundset.play(note, volume, force_play)


class Instrument:
    def __init__(self, octave_strings):
        """octave_strings is a list of strings, each of which will load
        12 sounds, one per each note.  Make sure that each string includes one
        format modifier (the "%s", indicating where the note part of the
        file name is)
        """
        self.octaves = []
        for string in octave_strings:
            self.octaves.append(load_strings(string, note_strings))
        self.octave_count = len(self.octaves)

    def set_limits(self, limit, sound_length):
        """Sets the limit of how many sounds each octave can play at
        once.  sound_length is in frames.
        """
        for octave in self.octaves:
            octave.set_sound_limit(limit, sound_length)


normal_instrument = Instrument(("normal_%s2", "normal_%s3"))
normal_instrument.set_limits(4, 30)

# the ghost bass is just a single note for each chord
ghost_fs0 = load("ghost_f#0")
ghost_a1 = load("ghost_a1")
ghost_as1 = load("ghost_a#1")
ghost_b1 = load("ghost_b1")
ghost_cs1 = load("ghost_c#1")
ghost_ds1 = load("ghost_d#1")
ghost_fs1 = load("ghost_f#1")

# these scale names may or may not be accurate
scale_progression = ((CS2, F2, FS2, GS2),  # F# Major
                     (CS2, DS2, F2, FS2, GS2),  # B Major
                     (CS2, A2, B2, D2, E2, FS2, GS2),  # F# Aeolian
                     (CS3, DS2, F2, FS2, GS2, AS3),  # D# Dorian

                     (CS2, F2, FS2, GS2),  # Those four again
                     (CS2, DS2, F2, FS2, GS2),
                     (CS2, A2, B2, D2, E2, FS2, GS2),
                     (CS2, DS2, F2, FS2, GS2, AS3),

                     (AS2, C2, CS2, DS2, F2, GS2),  # A# Natural Minor
                     (CS2, DS2, F2, FS2, GS2, AS3, C3),  # C# Major
                     (DS2, F2, FS2, GS2, AS3, C3, CS3),  # D# Dorian
                     (FS2, GS2, A3, C3, CS3, DS3, F3),  # IDK What This Scale Is

                     (F2, FS2, GS2, AS3, C3, CS3),  # Okay starting to
                     (CS2, DS2, F2, GS2, AS3),  # realize that these
                     (F2, FS2, GS2, A3, CS3, DS3),  # are just notes I think
                     (DS2, F2, FS2, A3, C3, CS3)  # sound nice with the chord
                     # and aren't actually scales
                     )

normal_scales = [Scale(normal_instrument, notes) for notes in scale_progression]
ghost_notes = (ghost_cs1, ghost_b1, ghost_a1, ghost_fs0,
               ghost_cs1, ghost_b1, ghost_a1, ghost_fs0,
               ghost_as1, ghost_cs1, ghost_ds1, ghost_fs1,
               ghost_cs1, ghost_cs1, ghost_fs1, ghost_ds1)


load_music("test_music")
set_music_volume(0.3)

chord_length = 4000  # chord length in milliseconds
# music track length in milliseconds
music_length = chord_length * len(scale_progression)
