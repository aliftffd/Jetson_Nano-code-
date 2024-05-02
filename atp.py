from firebase_admin import credentials 
from firebase_admin import db 
import firebase_admin 
import serial 
import time 

cred = credentials.Certificate('/home/atp2023/PROJECT_CD/Test_Project/test-app-2d14a-firebase-adminsdk-c885z-5f53873fce.json')
firebase_admin.initialize_app(cred, 
{
    'databaseURL' : "https://test-app-2d14a-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace with your serial port and baud rate
#direction = 1  # 1 untuk searah, -1 untuk berbalik arah
threshold_value = 0  # Nilai ambang batas untuk mengubah arah
max_data_count = 100
try:  # Add a try block for the main code
    while True:
        data = ser.readline().decode("utf-8")
        #print(data, end="")
        separated_data = data.split(',')

        # Cek apakah ada dua elemen setelah pemisahan
        if len(separated_data) == 2:
            unit = separated_data[0].strip()  # Menghapus spasi ekstra
            value = float(separated_data[1])  # Mengonversi nilai menjadi float
            print("Unit:", unit)
            print("Value:", value)
             # Logika untuk mengubah arah
            # Lakukan sesuatu berdasarkan arah yang ditentukan
            direction = "Moving forward" if value > threshold_value else "Moving backward"

            print(direction)
            data_to_upload = {
                'Kecepatan' : value,
                'Satuan'    : unit,  # Add commas to separate dictionary items
                'Arah'      : direction
            }
            result = db.reference('/Data_Kecepatan_OPS243c/').push(data_to_upload)

            data_count = len(db.reference('/Data_Kecepatan_OPS243c/').get())
            print('Banyak data: ',data_count)
            if data_count > 100: 
                oldest_data = db.reference('/Data_Kecepatan_OPS243c/').order_by_key().limit_to_first(data_count - max_data_count).get()
                for key in oldest_data: 
                    db.reference('/Data_Kecepatan_OPS243c/' + key).delete()
        # Tunggu selama 1 detik 
        time.sleep(1)
except KeyboardInterrupt: 
    print("Keyboard Interrupt detected, Exitting ...")
finally: 
    ser.close()
