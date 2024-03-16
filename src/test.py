import unittest
import numpy as np
from scipy.io import wavfile
from main import apply_delay, apply_echo, reverb, chipmunk_effect, reverse_playback, slow_motion, \
    apply_distortion, pitch_shift


class TestAudioEffects(unittest.TestCase):

    def setUp(self):
        # Load a sample audio file for testing
        self.samplerate, self.audio_data = wavfile.read('Test-voice-note.wav')

    def test_apply_delay(self):
        delay_time = 0.1
        delayed_audio = apply_delay(self.audio_data, delay_time, self.samplerate)
        self.assertEqual(len(delayed_audio), len(self.audio_data) + int(delay_time * self.samplerate))

    def test_apply_echo(self):
        delay_time = 0.1
        decay_factor = 0.5
        echoed_audio = apply_echo(self.audio_data, delay_time, decay_factor, self.samplerate)
        self.assertEqual(len(echoed_audio), len(self.audio_data) + int(delay_time * self.samplerate))

    def test_reverb(self):
        delay = int(0.1 * self.samplerate)
        decay = 0.5
        reverb_data = reverb(self.audio_data, delay, decay)
        self.assertEqual(len(reverb_data), len(self.audio_data))

    def test_chipmunk_effect(self):
        speedup_factor = 2
        chipmunk_audio, new_samplerate = chipmunk_effect(self.audio_data, self.samplerate, speedup_factor)
        self.assertTrue(new_samplerate > self.samplerate)
        self.assertEqual(len(chipmunk_audio), int(len(self.audio_data) / speedup_factor))

    def test_reverse_playback(self):
        reversed_audio = reverse_playback(self.audio_data)
        self.assertTrue(np.array_equal(reversed_audio, np.flipud(self.audio_data)))

    def test_apply_distortion(self):
        gain = 1.5
        folded_audio = apply_distortion(self.audio_data, gain)
        self.assertTrue(np.max(np.abs(folded_audio)) <= np.iinfo(np.int16).max)

    def test_pitch_shift_robot(self):
        filter_type = 'robot'
        shifted_audio = pitch_shift(self.audio_data, self.samplerate, filter_type)
        self.assertEqual(len(shifted_audio), len(self.audio_data))

    def test_pitch_shift_helium(self):
        filter_type = 'helium'
        shifted_audio = pitch_shift(self.audio_data, self.samplerate, filter_type)
        self.assertEqual(len(shifted_audio), len(self.audio_data))


if __name__ == '__main__':
    unittest.main()
