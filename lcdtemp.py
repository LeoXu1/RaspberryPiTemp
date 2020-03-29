import os
import glob
import time
import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
from subprocess import call

#Initialize LCD
lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33,31,29,23], numbering_mode=GPIO.BOARD)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Location of raw sensor data
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Returns raw output from w1_slave
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#Returns tuple containing temperature in Celsius and Fahrenheit
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=') #The temperature reading is shown after 't='
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

temp = round(read_temp()[1], 1)
max = temp
min = temp
lcd.clear()
t = 0
tempsFile = open("temps.txt", 'w').close()
tempsFile = open("temps.txt", 'a')
while True:
    temp = round(read_temp()[1], 1)
    tempsFile.write(str((round(read_temp()[0], 1), temp)))
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Temp: "+str(temp)+unichr(223)+"F") #Temp display in Fahrenheit
    
    if temp > max:
        max = temp
    if temp < min:
        min = temp

    lcd.cursor_pos = (1, 0)
    lcd.write_string("Max:"+str(max)+"Min:"+str(min)) #Displaying Max and Min temp

    if t == 30:
        call(['espeak "done" 2>/dev/null'], shell=True) #Voice notification
    time.sleep(1)
    t = t + 1
