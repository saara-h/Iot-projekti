from grove.gpio import GPIO
import time

# Pin number depends on Grove port you plugged into!
# Example: if you used D5, use pin 5
BUZZER_PIN = 5  

buzzer = GPIO(BUZZER_PIN, GPIO.OUT)

def play_tone(freq, duration,buzzer):
    """
    Play a tone at a specific frequency for a duration.
    freq: in Hertz
    duration: seconds
    """
    period = 1.0 / freq
    half = period / 2

    end_time = time.time() + duration
    while time.time() < end_time:
        buzzer.write(1)
        time.sleep(half)
        buzzer.write(0)
        time.sleep(half)


'''# Example usage
print("Playing tone 1000 Hz...")
play_tone(1000, 1)

print("Playing 440 Hz (A4)...")
play_tone(440, 1)

print("Done!")'''