import argparse
import scipy
from scipy.interpolate import interp1d
from scipy.io import wavfile
import sounddevice as sd
import numpy as np


def delay(audio_data, delay_time, sampling_rate):
    """
       Apply a delay effect to the audio data.

       Parameters:
           audio_data (ndarray): The input audio data.
           delay_time (float): The delay time in seconds.
           sampling_rate (int): The sampling rate of the audio.

       Returns:
           ndarray: The delayed audio data.
       """
    # Calculate number of samples to delay
    delay_samples = int(delay_time * sampling_rate)
    # Pad the audio with zeros to accommodate the delay
    delayed_audio = np.concatenate((audio_data, np.zeros(delay_samples)))
    # Apply delay by shifting the audio
    delayed_audio[delay_samples:] += audio_data * 0.5  # 0.5 is the delay mix factor
    return delayed_audio.astype(np.int16)


def echo(audio_data, delay_time, decay_factor, sampling_rate):
    """
        Apply an echo effect to the audio data.

        Parameters:
            audio_data (ndarray): The input audio data.
            delay_time (float): The delay time in seconds.
            decay_factor (float): The decay factor for the echo effect.
            sampling_rate (int): The sampling rate of the audio.

        Returns:
            ndarray: The echoed audio data.
        """
    # Calculate number of samples to delay
    delay_samples = int(delay_time * sampling_rate)
    # Create an empty array to store the echoed audio
    echoed_audio = np.zeros(len(audio_data) + delay_samples)
    # Apply echo effect
    for i in range(len(audio_data)):
        # Add original audio to the echoed audio
        echoed_audio[i] += audio_data[i]
        # Add delayed audio with decay
        if i + delay_samples < len(audio_data):
            echoed_audio[i + delay_samples] += decay_factor * audio_data[i]
    return echoed_audio.astype(np.int16)


def reverb(audio_data, delay, decay):
    """
       Apply a reverb effect to the audio data.

       Parameters:
           audio_data (ndarray): The input audio data.
           delay (int): The delay in samples for the reverb effect.
           decay (float): The decay factor for the reverb effect.

       Returns:
           ndarray: The reverberated audio data.
       """
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
    """
        Apply a chipmunk effect to the audio data.

        Parameters:
            audio_data (ndarray): The input audio data.
            sampling_rate (int): The sampling rate of the audio.
            speedup_factor (float): The speedup factor for the chipmunk effect.

        Returns:
            ndarray: The chipmunk-effect audio data.
            int: The new sampling rate after applying the effect.
        """
    # Calculate the new length of the resampled audio
    new_length = int(len(audio_data) / speedup_factor)
    # Resample the audio data to increase playback speed (pitch)
    chipmunk_audio = scipy.signal.resample(audio_data, new_length)
    # Adjust the sampling rate
    new_sampling_rate = int(sampling_rate * speedup_factor)
    return chipmunk_audio.astype(np.int16), new_sampling_rate


def reverse_playback(audio_data):
    """
       Reverse the playback of the input audio data.

       Parameters:
           audio_data (ndarray): The input audio data.

       Returns:
           ndarray: The audio data with reversed playback.
       """
    # Reverse the order of audio samples
    reversed_audio = np.flipud(audio_data)
    return reversed_audio.astype(np.int16)


def slow_motion(audio_data, sampling_rate, slowdown_factor):
    """
        Apply a slow motion effect to the input audio data.

        Parameters:
            audio_data (ndarray): The input audio data.
            sampling_rate (int): The sampling rate of the audio.
            slowdown_factor (float): The slowdown factor.

        Returns:
            ndarray: The audio data with the slow motion effect applied.
            int: The new sampling rate after applying the effect.
        """
    # Calculate the new length of the resampled audio
    new_length = int(len(audio_data) * slowdown_factor)

    # Create a time array for the resampled audio
    old_time = np.linspace(0, len(audio_data) / sampling_rate, len(audio_data))
    new_time = np.linspace(0, len(audio_data) / sampling_rate, new_length)

    # Interpolate the audio data to stretch or shrink it
    interpolator = interp1d(old_time, audio_data.T)
    slowed_audio = interpolator(new_time).T

    return slowed_audio.astype(np.int16), sampling_rate


def distortion(audio_data, gain, fold_amount=0.5):
    """
        Apply distortion effect to the audio data.

        Parameters:
            audio_data (ndarray): The input audio data.
            gain (float): The gain for distortion effect.
            fold_amount (float): The amount to fold the audio data.

        Returns:
            ndarray: The distorted audio data.
        """
    # Apply distortion using wave folding
    folded_audio = np.clip(audio_data * gain, -fold_amount, fold_amount)
    return folded_audio


def pitch_shift(audio_data, sampling_rate, pitch_filter):
    """
    Apply a pitch shift effect to the audio data.

    Parameters:
        audio_data (ndarray): The input audio data.
        sampling_rate (int): The sampling rate of the audio.
        pitch_filter (str): The type of pitch shift filter to apply ('helium' or 'default').

    Returns:
        ndarray: The pitch-shifted audio data.
    """
    if pitch_filter == 'helium':
        shift_amount = 6000 // 150
    else:
        shift_amount = 2500 // 100

    frames_per_second = sampling_rate // 20
    num_frames = len(audio_data) // frames_per_second

    shifted_audio = np.zeros_like(audio_data)
    for frame_num in range(num_frames):
        frame_start = frame_num * frames_per_second
        frame_end = (frame_num + 1) * frames_per_second
        frame_data = audio_data[frame_start:frame_end]
        left_channel = frame_data[0::2]
        right_channel = frame_data[1::2]

        # Take DFT
        left_freq = np.fft.rfft(left_channel)
        right_freq = np.fft.rfft(right_channel)

        # Apply frequency shift
        left_freq_shifted = np.roll(left_freq, shift_amount)
        right_freq_shifted = np.roll(right_freq, shift_amount)
        left_freq_shifted[0:shift_amount] = 0
        right_freq_shifted[0:shift_amount] = 0

        # Take inverse DFT
        left_shifted = np.fft.irfft(left_freq_shifted)
        right_shifted = np.fft.irfft(right_freq_shifted)

        # Combine the shifted channels
        combined_channels = np.column_stack((left_shifted, right_shifted)).ravel().astype(np.int16)
        shifted_audio[frame_start:frame_end] = combined_channels

    return shifted_audio


# Parse command-line arguments
def parse_arguments():
    """
        Parse command-line arguments.

        Returns:
            Namespace: An object containing parsed arguments.
        """
    parser = argparse.ArgumentParser(description='Apply effects to WAV file.')
    parser.add_argument('input_file', type=str, help='Input WAV file path')
    parser.add_argument('effect',
                        choices=['delay', 'reverb', 'chipmunk', 'reverse_playback', 'slow_mo', 'echo', 'distortion',
                                 'pitch_shift'],
                        help='Effect to apply')
    parser.add_argument('--output_file', type=str, default='output.wav',
                        help='Output WAV file path (default: output.wav)')
    parser.add_argument('--delay_time', type=float, default=0.25,
                        help='Delay time for delay effect in seconds (default: 0.5)')
    parser.add_argument('--decay_factor', type=float, default=0.75,
                        help='Decay factor for reverb effect (default: 0.5)')
    parser.add_argument('--speedup_factor', type=float, default=2,
                        help='speedup factor for chipmunk effect (default: 2)')
    parser.add_argument('--slowdown_factor', type=float, default=2,
                        help='slowdown factor for slow-mo effect (default: 2)')
    parser.add_argument('--gain', type=float, default=1.2,
                        help='gain for distortion effect.Higher gain values result in more distortion. (default: 1.2)')
    parser.add_argument('--filter', type=str, default='robot',
                        help='Choice between helium or robot effect for pitch shift (default: robot)')
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
        processed_audio = delay(audio_data, args.delay_time, samplerate)
    elif args.effect == 'reverb':
        # Calculate number of samples for delay based on delay time and sampling rate
        delay_samples = int(args.delay_time * samplerate)
        processed_audio = reverb(audio_data, delay_samples, args.decay_factor)
    elif args.effect == 'chipmunk':
        processed_audio, new_rate = chipmunk_effect(audio_data, samplerate, args.speedup_factor)
    elif args.effect == 'reverse_playback':
        processed_audio = reverse_playback(audio_data)
    elif args.effect == 'slow_mo':
        processed_audio, samplerate = slow_motion(audio_data, samplerate, args.slowdown_factor)
    elif args.effect == 'echo':
        processed_audio = echo(audio_data, args.delay_time, args.decay_factor, samplerate)
    elif args.effect == 'distortion':
        processed_audio = distortion(audio_data, args.gain)
    elif args.effect == 'pitch_shift':
        processed_audio = pitch_shift(audio_data, samplerate, args.filter)

    # Save processed audio to WAV file
    wavfile.write(args.output_file, samplerate, processed_audio)

    print("Playing input audio file")
    # Play the  output wave using sounddevice
    sd.play(audio_data.astype(np.int16), samplerate)
    sd.wait()  # Wait for the sound to finish playing
    print("Applying ", args.effect, "to input audio file")
    print("Playing output audio file")

    # Play the  output wave using sounddevice
    sd.play(processed_audio, samplerate)
    sd.wait()  # Wait for the sound to finish playing


if __name__ == "__main__":
    main()
