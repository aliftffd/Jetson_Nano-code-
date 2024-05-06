import Jetson.GPIO as GPIO
import time
from serial import Serial

GPIO.setmode(GPIO.BOARD)
# Atur pin GPIO Jetson Nano yang digunakan
ENA = 33
IN1 = 35
IN2 = 37
ENB = 32
IN3 = 40
IN4 = 38

# Atur mode pin GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Inisialisasi PWM untuk motor A dan B
pwm_A = GPIO.PWM(ENA, 100)  # Frekuensi PWM: 100Hz
pwm_B = GPIO.PWM(ENB, 100)

# Mulai PWM dengan duty cycle 0%
pwm_A.start(100)
pwm_B.start(100)

def set_speed_A(speed):
    # Batas kecepatan antara 0 dan 100
    if speed < 0:
        speed = 0
    elif speed > 100:
        speed = 100
    
    # Atur duty cycle PWM motor A sesuai dengan kecepatan yang diminta
    pwm_A.ChangeDutyCycle(speed)

def set_speed_B(speed):
    # Batas kecepatan antara 0 dan 100
    if speed < 0:
        speed = 0
    elif speed > 100:
        speed = 100
    
    # Atur duty cycle PWM motor B sesuai dengan kecepatan yang diminta
    pwm_B.ChangeDutyCycle(speed)

def motor_A_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def motor_A_backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

def motor_B_forward():
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def motor_B_backward():
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

# Inisialisasi Serial Port untuk RFID
rfid_serial = Serial('/dev/ttyUSB0', 115200, timeout=0.1)

# Fungsi untuk mengirim perintah RFID dan membaca respons
def send_rfid_cmd(cmd):
    data = bytes.fromhex(cmd)
    rfid_serial.write(data)
    response = rfid_serial.read(512)
    response_hex = response.hex().upper()
    hex_list = [response_hex[i:i+2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    return hex_space

try:
    while True:
        # Baca tag RFID
        tag_data = send_rfid_cmd('BB 00 22 00 00 22 7E')
        # Ubah respons dari RFID menjadi tag yang terdeteksi
        if '6C DC B9 33' in tag_data:  # Tag 1
            speed = 30
        elif '88 DD 43 D1' in tag_data:  # Tag 2
            speed = 10
        elif 'E8 DC 42 5E' in tag_data:  # Tag 3
            speed = 0
        else:
            # Jika tag tidak dikenali, motor akan dimatikan
            speed = 0
        
        # Atur kecepatan motor A dan B
        set_speed_A(speed)
        set_speed_B(speed)

except KeyboardInterrupt:
    # Hentikan PWM dan reset pin GPIO saat program berhenti
    pwm_A.stop()
    pwm_B.stop()
    GPIO.cleanup()
