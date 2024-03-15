import argparse
import scipy
from scipy.io import wavfile
import sounddevice as sd
import numpy as np



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
    parser.add_argument('effect', choices=['delay', 'reverb','chipmunk'], help='Effect to apply')
    parser.add_argument('--output_file', type=str, default='output.wav',
                        help='Output WAV file path (default: output.wav)')
    parser.add_argument('--delay_time', type=float, default=0.5,
                        help='Delay time for delay effect in seconds (default: 0.5)')
    parser.add_argument('--decay_factor', type=float, default=0.5, help='Decay factor for reverb effect (default: 0.5)')
    parser.add_argument('--speedup_factor',type=float, default=2, help='speedup factor for chipmunk effect (default: 2)')
    return parser.parse_args()


# Main function
def main():
    # Parse command-line arguments
    global processed_audio
    args = parse_arguments()

    # Read the input WAV file
    samplerate, audio_data = wavfile.read(args.input_file)
    # Apply selected effect
    if args.effect == 'delay':
        processed_audio = apply_delay(audio_data, args.delay_time, samplerate)
    elif args.effect == 'reverb':
        processed_audio = reverb(audio_data, args.delay_factor, args.decay_factor)
    elif args.effect == 'chipmunk':
        processed_audio, new_rate = chipmunk_effect(audio_data, samplerate, args.speedup_factor)

    # Save processed audio to WAV file
    wavfile.write(args.output_file, samplerate, processed_audio.astype(np.int16))

    print("Playing input audio file")
    # Play the  output wave using sounddevice
    sd.play(audio_data.astype(np.int16), samplerate)
    sd.wait()  # Wait for the sound to finish playing
    print("Applying ", args.effect, "to input audio file")
    print("Playing output audio file")

    # Play the  output wave using sounddevice
    sd.play(processed_audio.astype(np.int16), samplerate)
    sd.wait()  # Wait for the sound to finish playing




if __name__ == "__main__":
    main()
