import argparse

import scipy
from scipy.io import wavfile
import sounddevice as sd
from scipy.io.wavfile import read, write
import numpy as np

# Define functions for effects
def apply_delay(audio_data, delay_time, sampling_rate):
    # Calculate number of samples to delay
    delay_samples = int(delay_time * sampling_rate)

    # Pad the audio with zeros to accommodate the delay
    delayed_audio = np.concatenate((audio_data, np.zeros(delay_samples)))

    # Apply delay by shifting the audio
    delayed_audio[delay_samples:] += audio_data * 0.5  # Adjust the delay mix factor as needed

    return delayed_audio


def reverb(audio_data, delay, decay):
    # Create a new array to store the reverb data
    reverb_data = np.zeros_like(audio_data)

    # Apply the reverb effect to the audio data
    for i in range(delay, len(audio_data)):
        reverb_data[i] = audio_data[i] + decay * audio_data[i - delay]

    # Normalize the reverb data
    max_val = np.max(np.abs(reverb_data))
    reverb_data = reverb_data / max_val * 0.5  # Normalize the amplitude

    return reverb_data


def chipmunk_effect(audio_data, sampling_rate, speedup_factor):
    # Calculate the new length of the resampled audio
    new_length = int(len(audio_data) / speedup_factor)

    # Resample the audio data to increase playback speed (pitch)
    chipmunk_audio = scipy.signal.resample(audio_data, new_length)

    # Adjust the sampling rate
    new_sampling_rate = int(sampling_rate * speedup_factor)

    return chipmunk_audio.astype(np.int16), new_sampling_rate


# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Apply effects to WAV file.')
    parser.add_argument('input_file', type=str, help='Input WAV file path')
    parser.add_argument('effect', choices=['delay', 'reverb'], help='Effect to apply')
    parser.add_argument('--output_file', type=str, default='output.wav',
                        help='Output WAV file path (default: output.wav)')
    parser.add_argument('--delay_time', type=float, default=0.5,
                        help='Delay time for delay effect in seconds (default: 0.5)')
    parser.add_argument('--decay_factor', type=float, default=0.5, help='Decay factor for reverb effect (default: 0.5)')
    return parser.parse_args()


# Main function
def main():
    # Parse command-line arguments
    # args = parse_arguments()

    # Specify input and output file paths
    input_file = "voice-note.wav"
    # output_file = "Delay_output.wav"
    output_file = "Reverb_output_Original.wav"

    # Read the input WAV file
    samplerate, data = wavfile.read(input_file)


    ##DELAY EFFECT CODE
    # Apply the delay effect
    # delayed_data = apply_delay(data, 0.5, samplerate)
    # # Save the delayed audio to a WAV file
    # wavfile.write(output_file, samplerate, delayed_data.astype(np.int16))

    ##REVERB CODE
    # Test parameters
    # test_delay = 300  # Delay of 300 samples
    # test_decay = 0.5  # Decay factor of 0.5
    # # Apply reverb effect
    # reverb_audio = reverb(data, test_delay, test_decay)
    # # Save processed audio to WAV file
    # wavfile.write(output_file, samplerate, reverb_audio)

    # Apply chipmunk effect
    speedup_factor = 2
    chipmunk_audio, new_rate = chipmunk_effect(data, samplerate, speedup_factor)
    # Save processed audio to WAV file
    wavfile.write(output_file, new_rate, chipmunk_audio)


if __name__ == "__main__":
    main()
