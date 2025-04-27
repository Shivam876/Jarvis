import speech_recognition as sr

def test_microphone():
    print("Testing microphone access...")
    
    # List all available microphones
    print("\nAvailable microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone {index}: {name}")
    
    # Try to access the default microphone
    try:
        with sr.Microphone() as source:
            print("\nSuccessfully accessed microphone!")
            print("Please speak something to test...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)
            print("Audio captured successfully!")
    except Exception as e:
        print(f"\nError accessing microphone: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure your microphone is properly connected")
        print("2. Check Windows Sound Settings:")
        print("   - Press Windows + I to open Settings")
        print("   - Go to System > Sound")
        print("   - Under Input, make sure your microphone is selected")
        print("3. Check microphone permissions:")
        print("   - Go to Windows Settings > Privacy & Security > Microphone")
        print("   - Make sure 'Microphone access' is turned on")
        print("   - Under 'Let apps access your microphone', make sure it's enabled")
        print("4. Try running Python as administrator")

if __name__ == "__main__":
    test_microphone() 