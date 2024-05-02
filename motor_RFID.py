import Jetson.GPIO as GPIO
import time
from serial import Serial

# Set GPIO pins for motor control
ENA = 33
IN1 = 35
IN2 = 37
ENB = 32
IN3 = 40
IN4 = 38

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)

# Set initial motor speed
initial_speed = 100  # Initial speed

# Set direction of motors to forward
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.HIGH)
GPIO.output(IN4, GPIO.LOW)

# Initialize Serial Port for RFID
rfid_serial = Serial('/dev/ttyUSB0', 115200, timeout=0.1)

# Function to send RFID command and read response
def send_rfid_cmd(cmd):
    data = bytes.fromhex(cmd)
    rfid_serial.write(data)
    response = rfid_serial.read(512)
    response_hex = response.hex().upper()
    hex_list = [response_hex[i:i+2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    return hex_space

# Variable to store last detected speed
last_speed = initial_speed

try:
    while True:
        # Read RFID tag
        tag_data = send_rfid_cmd('BB 00 22 00 00 22 7E')
        # Convert RFID response to detected tag
        if '6C DC B9 33' in tag_data:  # Tag 1
            last_speed = 50
        elif '88 DD 43 D1' in tag_data:  # Tag 2
            last_speed = 15
        elif 'E8 DC 42 5E' in tag_data:  # Tag 3
            last_speed = 0
        
        # Set the motor speed
        if last_speed > 0:
            # Set ENA and ENB to HIGH for forward direction
            GPIO.output(ENA, GPIO.HIGH)
            GPIO.output(ENB, GPIO.HIGH)
            # Adjust speed by changing the duty cycle of ENA and ENB
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.LOW)
            time.sleep(0.1)
            # Change duty cycle based on the last detected speed
            GPIO.output(ENA, GPIO.LOW)
            GPIO.output(ENB, GPIO.LOW)
            time.sleep((100 - last_speed) / 100.0)
        else:
            # Stop the motors if speed is 0
            GPIO.output(ENA, GPIO.LOW)
            GPIO.output(ENB, GPIO.LOW)

except KeyboardInterrupt:
    # Clean up GPIO pins when the program stops
    GPIO.cleanup()
