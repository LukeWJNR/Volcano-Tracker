"""
Utility functions for generating, processing, and playing volcano audio profiles.

This module provides functionality to create audio representations of volcanic activity,
allowing users to "hear" the differences between various types of volcanoes and eruption patterns.
"""

import os
import base64
import numpy as np
import librosa
import librosa.display
import soundfile as sf
from pydub import AudioSegment
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Directory for storing generated audio files
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Define characteristic frequencies and amplitudes for different volcano types
VOLCANO_TYPE_PROFILES = {
    'stratovolcano': {
        'base_freq': 220.0,  # Lower frequency for stratovolcanoes (more explosive)
        'harmonics': [1.0, 0.8, 0.6, 0.4, 0.2],  # Strong harmonics for complex sound
        'noise_level': 0.3,  # Moderate noise for explosivity
        'attack': 0.05,  # Fast attack for explosive eruptions
        'sustain': 0.3,  # Moderate sustain
        'release': 0.6,  # Longer release/decay
        'duration': 5.0,  # Sound duration in seconds
    },
    'shield volcano': {
        'base_freq': 165.0,  # Lower frequency
        'harmonics': [1.0, 0.3, 0.1],  # Fewer harmonics (smoother sound)
        'noise_level': 0.1,  # Less noise (quieter, effusive eruptions)
        'attack': 0.2,  # Slower attack
        'sustain': 0.5,  # Longer sustain
        'release': 0.3,  # Moderate release
        'duration': 6.0,  # Sound duration in seconds
    },
    'caldera': {
        'base_freq': 110.0,  # Very low frequency for large calderas
        'harmonics': [1.0, 0.9, 0.8, 0.7, 0.6, 0.5],  # Rich harmonics for complex sound
        'noise_level': 0.4,  # Higher noise for potential catastrophic eruptions
        'attack': 0.02,  # Very fast attack 
        'sustain': 0.2,  # Shorter sustain
        'release': 0.8,  # Very long release
        'duration': 7.0,  # Sound duration in seconds
    },
    'cinder cone': {
        'base_freq': 330.0,  # Higher frequency for smaller volcanoes
        'harmonics': [1.0, 0.5, 0.2],  # Some harmonics
        'noise_level': 0.25,  # Moderate noise
        'attack': 0.1,  # Moderate attack
        'sustain': 0.2,  # Short sustain
        'release': 0.4,  # Moderate release
        'duration': 4.0,  # Sound duration in seconds
    },
    'default': {  # For any unrecognized volcano type
        'base_freq': 220.0,
        'harmonics': [1.0, 0.5, 0.3],
        'noise_level': 0.2,
        'attack': 0.1,
        'sustain': 0.3,
        'release': 0.6,
        'duration': 5.0,
    },
}

# Mapping between alert levels and sound modifications
ALERT_LEVEL_MODIFIERS = {
    'Normal': {
        'freq_shift': 0.0,  # No frequency shift
        'amplitude_mod': 1.0,  # Normal amplitude
        'tremor': 0.0,  # No tremor/vibrato
    },
    'Advisory': {
        'freq_shift': 0.05,  # Slight frequency increase
        'amplitude_mod': 1.2,  # Slightly louder
        'tremor': 0.1,  # Slight tremor
    },
    'Watch': {
        'freq_shift': 0.15,  # Moderate frequency increase
        'amplitude_mod': 1.5,  # Notably louder
        'tremor': 0.2,  # Moderate tremor
    },
    'Warning': {
        'freq_shift': 0.3,  # Large frequency shift
        'amplitude_mod': 2.0,  # Much louder
        'tremor': 0.4,  # Strong tremor
    },
    'Unknown': {
        'freq_shift': 0.0,
        'amplitude_mod': 1.0,
        'tremor': 0.05,  # Small amount of uncertainty
    },
}

def get_volcano_type_profile(volcano_type: str) -> Dict[str, Any]:
    """
    Determine the audio profile parameters based on volcano type.
    
    Args:
        volcano_type (str): The type of volcano
    
    Returns:
        Dict[str, Any]: Audio profile parameters
    """
    # Convert to lowercase for case-insensitive matching
    volcano_type_lower = volcano_type.lower() if volcano_type else ""
    
    # Try to find the closest match in our profiles
    for key in VOLCANO_TYPE_PROFILES:
        if key.lower() in volcano_type_lower:
            return VOLCANO_TYPE_PROFILES[key]
    
    # If no match, return default profile
    return VOLCANO_TYPE_PROFILES['default']

def get_alert_level_modifiers(alert_level: str) -> Dict[str, float]:
    """
    Get audio modifiers based on the volcano's alert level.
    
    Args:
        alert_level (str): The volcano's current alert level
    
    Returns:
        Dict[str, float]: Audio modifiers for the alert level
    """
    if not alert_level or alert_level not in ALERT_LEVEL_MODIFIERS:
        return ALERT_LEVEL_MODIFIERS['Unknown']
    
    return ALERT_LEVEL_MODIFIERS[alert_level]

def apply_envelope(signal: np.ndarray, sr: int, attack: float, sustain: float, release: float) -> np.ndarray:
    """
    Apply an ADSR (Attack, Decay, Sustain, Release) envelope to an audio signal.
    
    Args:
        signal (np.ndarray): The audio signal
        sr (int): Sample rate
        attack (float): Attack time in seconds
        sustain (float): Sustain time in seconds 
        release (float): Release time in seconds
    
    Returns:
        np.ndarray: Signal with envelope applied
    """
    total_length = len(signal)
    attack_samples = int(attack * sr)
    sustain_samples = int(sustain * sr)
    release_samples = int(release * sr)
    
    # Create envelope segments
    attack_env = np.linspace(0, 1, attack_samples) if attack_samples > 0 else np.array([])
    sustain_env = np.ones(sustain_samples) if sustain_samples > 0 else np.array([])
    release_env = np.linspace(1, 0, release_samples) if release_samples > 0 else np.array([])
    
    # Combine segments
    envelope = np.concatenate([attack_env, sustain_env, release_env])
    
    # Ensure envelope matches signal length
    if len(envelope) > total_length:
        envelope = envelope[:total_length]
    elif len(envelope) < total_length:
        padding = np.zeros(total_length - len(envelope))
        envelope = np.concatenate([envelope, padding])
    
    # Apply envelope
    return signal * envelope

def generate_volcano_sound(volcano_data: Dict[str, Any]) -> Tuple[np.ndarray, int]:
    """
    Generate audio representing a volcano's characteristics and activity level.
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano data
    
    Returns:
        Tuple[np.ndarray, int]: Audio signal and sample rate
    """
    # Extract volcano characteristics
    volcano_type = volcano_data.get('type', 'default')
    alert_level = volcano_data.get('alert_level', 'Unknown')
    last_eruption = volcano_data.get('last_eruption', 'Unknown')
    
    # Get base sound profile for volcano type
    profile = get_volcano_type_profile(volcano_type)
    
    # Get modifiers for alert level
    modifiers = get_alert_level_modifiers(alert_level)
    
    # Base parameters
    sr = 22050  # Sample rate
    duration = profile['duration']
    samples = int(duration * sr)
    
    # Apply modifiers
    base_freq = profile['base_freq'] * (1 + modifiers['freq_shift'])
    amplitude = modifiers['amplitude_mod']
    
    # Generate time array
    t = np.linspace(0, duration, samples, endpoint=False)
    
    # Generate base sine wave with harmonics
    signal = np.zeros_like(t)
    
    for i, harmonic_strength in enumerate(profile['harmonics']):
        # Apply slight tremor/vibrato effect based on alert level
        tremor_rate = 5.0  # Hz
        tremor_depth = modifiers['tremor']
        tremor = tremor_depth * np.sin(2 * np.pi * tremor_rate * t)
        
        # Add harmonic with tremor
        freq = base_freq * (i + 1) * (1 + tremor)
        signal += harmonic_strength * np.sin(2 * np.pi * freq * t)
    
    # Normalize
    signal = signal / np.max(np.abs(signal))
    
    # Add noise component for "roughness" in sound
    noise = np.random.normal(0, profile['noise_level'], samples)
    
    # Combine signal and noise
    combined_signal = signal + noise
    
    # Normalize again
    combined_signal = combined_signal / np.max(np.abs(combined_signal))
    
    # Apply amplitude modifier
    combined_signal = combined_signal * amplitude
    
    # Apply envelope
    final_signal = apply_envelope(
        combined_signal, 
        sr, 
        profile['attack'], 
        profile['sustain'], 
        profile['release']
    )
    
    # Ensure we don't clip
    final_signal = np.clip(final_signal, -1.0, 1.0)
    
    return final_signal, sr

def get_volcano_sound_file(volcano_data: Dict[str, Any], force_regenerate: bool = False) -> Optional[str]:
    """
    Get the path to an audio file for the volcano, generating one if it doesn't exist.
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano data
        force_regenerate (bool): Whether to force regeneration of the audio file
        
    Returns:
        Optional[str]: Path to the audio file, or None if generation fails
    """
    # Create a unique filename based on volcano ID and alert level
    volcano_id = volcano_data.get('id', 'unknown')
    alert_level = volcano_data.get('alert_level', 'Unknown')
    
    filename = f"volcano_{volcano_id}_{alert_level}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    # Generate a new file if it doesn't exist or if regeneration is forced
    if force_regenerate or not os.path.exists(filepath):
        try:
            # Generate sound
            signal, sr = generate_volcano_sound(volcano_data)
            
            # Save as WAV file
            sf.write(filepath, signal, sr, subtype='PCM_16')
            
        except Exception as e:
            print(f"Error generating volcano sound: {str(e)}")
            return None
    
    return filepath

def get_audio_base64(filepath: str) -> Optional[str]:
    """
    Convert an audio file to a base64 string for embedding in HTML.
    
    Args:
        filepath (str): Path to the audio file
        
    Returns:
        Optional[str]: Base64-encoded audio data, or None if conversion fails
    """
    try:
        with open(filepath, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode()
            return audio_b64
    except Exception as e:
        print(f"Error encoding audio file: {str(e)}")
        return None

def generate_audio_html(audio_b64: str, file_extension: str = "wav") -> str:
    """
    Generate HTML for embedding audio in Streamlit.
    
    Args:
        audio_b64 (str): Base64-encoded audio data
        file_extension (str): Audio file extension
        
    Returns:
        str: HTML code for audio player
    """
    # Get MIME type based on file extension
    mime_types = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
    }
    mime_type = mime_types.get(file_extension.lower(), "audio/wav")
    
    # Create HTML with custom styling
    html = f"""
    <div style="display: flex; justify-content: center; width: 100%;">
        <audio controls style="width: 100%; max-width: 500px;">
            <source src="data:{mime_type};base64,{audio_b64}" type="{mime_type}">
            Your browser does not support the audio element.
        </audio>
    </div>
    """
    return html

def generate_waveform_plot(filepath: str) -> Optional[str]:
    """
    Generate a waveform visualization for the audio file.
    
    Args:
        filepath (str): Path to the audio file
        
    Returns:
        Optional[str]: Base64-encoded image data for the waveform plot
    """
    try:
        # Load audio file
        y, sr = librosa.load(filepath)
        
        # Set up the plot
        plt.figure(figsize=(10, 2))
        
        # Plot waveform
        librosa.display.waveshow(y, sr=sr, alpha=0.8)
        plt.title('Waveform')
        plt.tight_layout()
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        # Convert to base64
        img_b64 = base64.b64encode(buf.read()).decode()
        return img_b64
    except Exception as e:
        print(f"Error generating waveform plot: {str(e)}")
        return None

def get_volcano_sound_player(volcano_data: Dict[str, Any], 
                             include_waveform: bool = True, 
                             force_regenerate: bool = False) -> Optional[str]:
    """
    Get HTML for an audio player with the volcano's sound profile.
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano data
        include_waveform (bool): Whether to include a waveform visualization
        force_regenerate (bool): Whether to force regeneration of the audio file
        
    Returns:
        Optional[str]: HTML for the audio player and waveform, or None if generation fails
    """
    # Get the audio file
    audio_path = get_volcano_sound_file(volcano_data, force_regenerate)
    if not audio_path:
        return None
    
    # Convert audio to base64
    audio_b64 = get_audio_base64(audio_path)
    if not audio_b64:
        return None
    
    # Generate audio player HTML
    html = generate_audio_html(audio_b64)
    
    # Add waveform if requested
    if include_waveform:
        waveform_b64 = generate_waveform_plot(audio_path)
        if waveform_b64:
            html += f"""
            <div style="margin-top: 10px; display: flex; justify-content: center; width: 100%;">
                <img src="data:image/png;base64,{waveform_b64}" 
                     style="width: 100%; max-width: 500px;">
            </div>
            """
    
    return html