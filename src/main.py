import argparse
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


def apply_reverb(audio_data, decay_factor):
    # Implement reverb effect
    pass


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
    input_file = "Punch.wav"
    output_file = "Delay_output.wav"

    # Read the input WAV file
    samplerate, data = wavfile.read(input_file)
    # Apply the delay effect
    delayed_data = apply_delay(data, 0.25, samplerate)
    # Save the delayed audio to a WAV file
    wavfile.write(output_file, samplerate, delayed_data.astype(np.int16))




if __name__ == "__main__":
    main()
