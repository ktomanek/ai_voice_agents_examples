import pyaudio

def list_audio_devices():
    """List all available audio input and output devices using PyAudio."""
    p = pyaudio.PyAudio()
    
    print("Available Audio Devices:")
    print("=" * 50)
    
    # Get the number of available devices
    device_count = p.get_device_count()
    print(f"Total devices: {device_count}\n")
    
    # List each device's information
    for i in range(device_count):
        try:
            device_info = p.get_device_info_by_index(i)
            
            # Format the device information
            device_name = device_info['name']
            input_channels = device_info['maxInputChannels']
            output_channels = device_info['maxOutputChannels']
            sample_rate = int(device_info['defaultSampleRate'])
            
            # Determine if it's an input, output, or both
            device_type = []
            if input_channels > 0:
                device_type.append("INPUT")
            if output_channels > 0:
                device_type.append("OUTPUT")
            device_type = "+".join(device_type)
            
            # Check if it's the default device
            default_marks = []
            if p.get_default_input_device_info()['index'] == i:
                default_marks.append("DEFAULT INPUT")
            if p.get_default_output_device_info()['index'] == i:
                default_marks.append("DEFAULT OUTPUT")
            default_status = f" ({', '.join(default_marks)})" if default_marks else ""
            
            # Print the formatted device information
            print(f"Device {i}: {device_name}{default_status}")
            print(f"    Type: {device_type}")
            print(f"    Input Channels: {input_channels}")
            print(f"    Output Channels: {output_channels}")
            print(f"    Default Sample Rate: {sample_rate} Hz")
            print("-" * 50)
            
        except Exception as e:
            print(f"Device {i}: Could not get device info - {e}")
            print("-" * 50)
    
    # Terminate the PyAudio instance
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()