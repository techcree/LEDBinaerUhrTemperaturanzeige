# Raspberry Pi Pico LED Binäruhr und Temperaturanzeige by StSkanta (TechCree) 838375
# Start Script
import machine
from machine import Pin
import utime
from machine import I2C
import time
import LEDtest
import os
import gc
# Lade RTC Zeitmodul und berechne Zeit in lesbarem Format
address = 0x68
register = 0x00
#Sekunden Minuten Stunden Woche Tag Jahr - Zeit festlegen
NowTime = b'\x00\x27\x14\x24\x02\x20\x22'  ###Nach dem Zeit setzen die #Zeilen aussetzen
w  = ["SUN","Mon","Tues","Wed","Thur","Fri","Sat"];
#/dev/i2c-1
bus = I2C(1)
#def ds3231SetTime(): ###After set time kill this line
#    bus.writeto_mem(int(address),int(register),NowTime)  ###After set time kill this line
def ds3231ReadTime():
    return bus.readfrom_mem(int(address),int(register),7);
#ds3231SetTime()  ###After set time kill this line
#Aktiviere GPIO und ordne LEDs zu
#GPIO Belegung auf raspberry Pi Pico
# Enter an "X" for your occupied pins
#                        [X] LED onBoard
# led00 GP0  [X]  (1)  sek1                 (40)  [ ] VBUS
# led01 GP1  [X]  (2)  sek2                 (39)  [ ] VSYS
#       GND  [ ]  (3)              BuzzerGND(38)  [X] GDN        lED Panel GDN
# led02 GP2  [X]  (4)  sek4                 (37)  [ ] 3V3_EN
# led03 GP3  [X]  (5)  sek8                 (36)  [X] 3V3(OUT)   RTC Power
# led04 GP4  [X]  (6)  sek10                (35)  [ ] -
# led05 GP5  [X]  (7)  sek20          sek40 (34)  [X] GP28 led06
#       GND  [ ]  (8)                       (33)  [ ] GND
#       GP6  [X]  (9)  (RTCMod)        stu8 (32)  [X] GP27 led19
#       GP7  [X]  (10) (RTCMod)             (31)  [X] GP26 
# led08 GP8  [X]  (11) min                  (30)  [ ] RUN
# led09 GP9  [X]  (12) min2           stu40 (29)  [X] GP22 led22 
#       GND  [ ]  (13)                      (28)  [ ] GND
# led10 GP10 [X]  (14) min4           stu20 (27)  [X] GP21 led21 
# led11 GP11 [X]  (15) min8             stu (26)  [X] GP20 led20 
# led12 GP12 [X]  (16) min            Buzzer(25)  [x] GP19
# led13 GP13 [X]  (17) min20           stu4 (24)  [X] GP18 led18 
#       GND  [ ]  (18)                      (23)  [ ] GDN
# led14 GP14 [X]  (19) min40           stu2 (22)  [X] GP17 led17 
# led07 GP15 [X]  (20) min80            stu (21)  [X] GP16 led16  
#                    [ ]SWCLK [ ]GND [ ]SWDIO
# The LED on the Pico board is the LED PIN 25
# Mainboard LED
led25 =  Pin(25, Pin.OUT)
#Uhrzeit und Temperatur LEDs
#Anrodnung der LED Schema
#   8						O	led19.value(0)						O	led11.value(0)	O	led07.value(0)	O	led03.value(0)	8
#   3	O	led22.value(0)	O	led18.value(0)	O	led14.value(0)	O	led10.value(0)	O	led06.value(0)	O	led02.value(0)	3
#   2	O	led21.value(0)	O	led17.value(0)	O	led13.value(0)	O	led09.value(0)	O	led05.value(0)	O	led01.value(0)	2
#   1	O	led20.value(0)	O	led16.value(0)	O	led12.value(0)	O	led08.value(0)	O	led04.value(0)	O	led00.value(0)	1
#sekunden Einer
led00 = Pin(0, Pin.OUT) # sek1 gruen (1)
led01 = Pin(1, Pin.OUT) # sek1 gruen (2)
led02 = Pin(2, Pin.OUT) # sek1 gruen (4)
led03 = Pin(3, Pin.OUT) # sek1 gruen (8)
#sekunden Zehner
led04 = Pin(4, Pin.OUT) # sek10 gruen (1) 
led05 = Pin(5, Pin.OUT) # sek10 gruen (2)
#Pin6 wird vom RTC Modul benötigt###
led06 = Pin(28, Pin.OUT) # sek10 gruen (4)
# Pin7 wird vom RTC Modul benötigt###
led07 = Pin(15, Pin.OUT) # sek10 gruen (8)
# Minuten Einer
led08 = Pin(8, Pin.OUT) # min rot (1)
led09 = Pin(9, Pin.OUT) # min rot (2)
led10 = Pin(10, Pin.OUT) # min rot (4)
led11 = Pin(11, Pin.OUT) # min rot (8)
#Minuten Zehner
led12 = Pin(12, Pin.OUT) # min rot (1)
led13 = Pin(13, Pin.OUT) # min rot (2)
led14 = Pin(14, Pin.OUT) # min rot (4)
# min10 (8) rot wird nicht benötigt
#Stunden Einer
led16 = Pin(16, Pin.OUT) # std1 gelb (1)
led17 = Pin(17, Pin.OUT) # std1 gelb (2)
led18 = Pin(18, Pin.OUT) # std1 gelb (4)
led19 = Pin(27, Pin.OUT) # std1 gelb (8)
#Stunden Zehner
led20 = Pin(20, Pin.OUT) # std10 gelb (1)
led21 = Pin(26, Pin.OUT) # std10 gelb (2)
led22 = Pin(22, Pin.OUT) # std10 gelb (4)
# std10 (8) gelb wird nicht benötigt
#Initialisiere Buzzer
buzzer = Pin(21, Pin.OUT)
# Setze Runden für die Loop der Uhrzeitanzeige
#loop1loops = int(input("Anzahl Schleifen Uhrzeit?")) # Zeile ausschalten
# Starte Script Uhrzeit
while True:
    #print(gc.mem_free()) #Bei Problemen mit dem Speicher die Zeile freigeben um freien Speicherplatz anzuzeigen
    loop1 = 0 #Beginn der Schleife für die Uhrzeitanzeige
    while loop1 <= 30: # oder setze loop1loops siehe auch Zeile 660        
        t = ds3231ReadTime()
        a = t[0]&0x7F  #sec
        b = t[1]&0x7F  #min
        c = t[2]&0x3F  #hour
        d = t[3]&0x07  #week
        e = t[4]&0x3F  #day
        f = t[5]&0x1F  #mouth
        #print("20%x/%02x/%02x %02x:%02x:%02x %s" %(t[6],t[5],t[4],t[2],t[1],t[0],w[t[3]-1]))
        #Variablen für Zeit
        sek = int("%2x" %a)
        min = int("%2x" %b)
        stu = int("%2x" %c)
        #print(stu, min, sek)
        #print(loop1)
        #alternate with input    
        #    stu = int(input("Stunden 1er?"))
        #    min =  int(input("Minuten 1er?"))
        #    sek = int(input("Sekunden 1er?"))
        # Starte Zuordnung GPIO zur Zeit für SEKUNDEN
        if sek == 1:
            led00.value(1) 
        if sek == 2:
            led01.value(1)
        if sek == 3:    
            led00.value(1)
            led01.value(1)
        if sek == 4:    
            led02.value(1)
        if sek == 5:    
            led00.value(1)
            led02.value(1)
        if sek == 6:
            led01.value(1)
            led02.value(1)
        if sek == 7:
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 8:    
            led03.value(1)
        if sek == 9:
            led00.value(1)
            led03.value(1)
        if sek == 10:    
            led04.value(1)
        if sek == 11:
            led04.value(1)
            led00.value(1)
        if sek == 12:
            led04.value(1)
            led01.value(1)
        if sek == 13:
            led04.value(1)
            led00.value(1)
            led01.value(1)
        if sek == 14:
            led04.value(1)
            led02.value(1)
        if sek == 15:
            led04.value(1)
            led00.value(1)
            led02.value(1)
        if sek == 16:
            led04.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 17:
            led04.value(1)
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 18:
            led04.value(1)
            led03.value(1)
        if sek == 19:
            led04.value(1)
            led00.value(1)
            led03.value(1)
        if sek == 20:    
            led05.value(1)
        if sek == 21:
            led05.value(1)
            led00.value(1)
        if sek == 22:
            led05.value(1)
            led01.value(1)
        if sek == 23:
            led05.value(1)
            led00.value(1)
            led01.value(1)
        if sek == 24:
            led05.value(1)
            led02.value(1)
        if sek == 25:
            led05.value(1)
            led00.value(1)
            led02.value(1)
        if sek == 26:
            led05.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 27:
            led05.value(1)
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 28:
            led05.value(1)
            led03.value(1)
        if sek == 29:
            led05.value(1)
            led00.value(1)
            led03.value(1)
        if sek == 30:    
            led04.value(1)
            led05.value(1)
        if sek == 31:
            led04.value(1)
            led05.value(1)
            led00.value(1)
        if sek == 32:
            led04.value(1)
            led05.value(1)
            led01.value(1)
        if sek == 33:
            led04.value(1)
            led05.value(1)
            led00.value(1)
            led01.value(1)
        if sek == 34:
            led04.value(1)
            led05.value(1)
            led02.value(1)
        if sek == 35:
            led04.value(1)
            led05.value(1)
            led00.value(1)
            led02.value(1)
        if sek == 36:
            led04.value(1)
            led05.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 37:
            led04.value(1)
            led05.value(1)
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 38:
            led04.value(1)
            led05.value(1)
            led03.value(1)
        if sek == 39:
            led04.value(1)
            led05.value(1)
            led00.value(1)
            led03.value(1)
        if sek == 40:    
            led06.value(1)
        if sek == 41:
            led06.value(1)
            led00.value(1)
        if sek == 42:
            led06.value(1)
            led01.value(1)
        if sek == 43:
            led06.value(1)
            led00.value(1)
            led01.value(1)
        if sek == 44:
            led06.value(1)
            led02.value(1)
        if sek == 45:
            led06.value(1)
            led00.value(1)
            led02.value(1)
        if sek == 46:
            led06.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 47:
            led06.value(1)
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 48:
            led06.value(1)
            led03.value(1)
        if sek == 49:
            led06.value(1)
            led00.value(1)
            led03.value(1)
        if sek == 50:
           led04.value(1)
           led06.value(1)
        if sek == 51:
            led04.value(1)
            led06.value(1)
            led00.value(1)
        if sek == 52:
            led04.value(1)
            led06.value(1)
            led01.value(1)
        if sek == 53:
            led04.value(1)
            led06.value(1)
            led00.value(1)
            led01.value(1)
        if sek == 54:
            led04.value(1)
            led06.value(1)
            led02.value(1)
        if sek == 55:
            led04.value(1)
            led06.value(1)
            led00.value(1)
            led02.value(1)
        if sek == 56:
            led04.value(1)
            led06.value(1)
            led01.value(1)
            led01.value(1)
        if sek == 57:
            led04.value(1)
            led06.value(1)
            led00.value(1)
            led01.value(1)
            led02.value(1)
        if sek == 58:
            led04.value(1)
            led06.value(1)
            led03.value(1)
        if sek == 59:
            led04.value(1)
            led06.value(1)
            led00.value(1)
            led03.value(1)
        # Starte Zuordnung GPIO zur Zeit für MINUTEN
        if min == 1:    
            led08.value(1)
        if min == 2:        
            led09.value(1)
        if min == 3:
            led08.value(1)
            led09.value(1)
        if min == 4:    
            led10.value(1)
        if min == 5:
            led08.value(1)
            led10.value(1)      
        if min == 6:
            led09.value(1)
            led10.value(1)
        if min == 7:
            led08.value(1)
            led09.value(1)
            led10.value(1)  
        if min == 8:
            led11.value(1)
        if min == 9:
            led08.value(1)
            led11.value(1)    
        if min == 10:
            led12.value(1)
        if min == 11:
            led12.value(1)
            led08.value(1)
        if min == 12:
            led12.value(1)
            led09.value(1)
        if min == 13:
            led12.value(1)
            led08.value(1)
            led09.value(1)
        if min == 14:
            led12.value(1)
            led10.value(1)
        if min == 15:
            led12.value(1)
            led08.value(1)
            led10.value(1)
        if min == 16:
            led12.value(1)
            led09.value(1)
            led10.value(1)
        if min == 17:
            led12.value(1)
            led08.value(1)
            led09.value(1)
            led10.value(1)
        if min == 18:
            led12.value(1)
            led11.value(1)
        if min == 19:
            led12.value(1)
            led08.value(1)
            led11.value(1)
        if min == 20:
            led13.value(1)
        if min == 21:
            led13.value(1)
            led08.value(1)
        if min == 22:
            led13.value(1)        
            led09.value(1)
        if min == 23:
            led13.value(1)
            led08.value(1)
            led09.value(1)
        if min == 24:
            led13.value(1)    
            led10.value(1)
        if min == 25:
            led13.value(1)
            led08.value(1)
            led10.value(1)      
        if min == 26:
            led13.value(1)
            led09.value(1)
            led10.value(1)
        if min == 27:
            led13.value(1)
            led08.value(1)
            led09.value(1)
            led10.value(1)  
        if min == 28:
            led13.value(1)
            led11.value(1)
        if min == 29:
            led13.value(1)
            led08.value(1)
            led11.value(1)
        if min == 30:
            led12.value(1)
            led13.value(1)
        if min == 31:
            led12.value(1)
            led13.value(1)
            led08.value(1)
        if min == 32:
            led12.value(1)
            led13.value(1)        
            led09.value(1)
        if min == 33:
            led12.value(1)
            led13.value(1)
            led08.value(1)
            led09.value(1)
        if min == 34:
            led12.value(1)
            led13.value(1)    
            led10.value(1)
        if min == 35:
            led12.value(1)
            led13.value(1)
            led08.value(1)
            led10.value(1)      
        if min == 36:
            led12.value(1)
            led13.value(1)
            led09.value(1)
            led10.value(1)
        if min == 37:
            led12.value(1)
            led13.value(1)
            led08.value(1)
            led09.value(1)
            led10.value(1)  
        if min == 38:
            led12.value(1)
            led13.value(1)
            led11.value(1)
        if min == 39:
            led12.value(1)
            led13.value(1)
            led08.value(1)
            led11.value(1)
        if min == 40:
            led14.value(1)
        if min == 41:
            led14.value(1)
            led08.value(1)
        if min == 42:
            led14.value(1)
            led09.value(1)
        if min == 43:
            led14.value(1)
            led08.value(1)
            led09.value(1)
        if min == 44:
            led14.value(1)
            led10.value(1)
        if min == 45:
            led14.value(1)
            led08.value(1)
            led10.value(1)
        if min == 46:
            led14.value(1)
            led09.value(1)
            led10.value(1)
        if min == 47:
            led14.value(1)
            led08.value(1)
            led09.value(1)
            led10.value(1)
        if min == 48:
            led14.value(1)
            led11.value(1)
        if min == 49:
            led14.value(1)
            led08.value(1)
            led11.value(1)
        if min == 50:
            led12.value(1)
            led14.value(1)
        if min == 51:
            led12.value(1)
            led14.value(1)
            led08.value(1)
        if min == 52:
            led12.value(1)
            led14.value(1)
            led09.value(1)
        if min == 53:
            led12.value(1)
            led14.value(1)
            led08.value(1)
            led09.value(1)
        if min == 54:
            led12.value(1)
            led14.value(1)
            led10.value(1)
        if min == 55:
            led12.value(1)
            led14.value(1)
            led08.value(1)
            led10.value(1)
        if min == 56:
            led12.value(1)
            led14.value(1)
            led09.value(1)
            led10.value(1)
        if min == 57:
            led12.value(1)
            led14.value(1)
            led08.value(1)
            led09.value(1)
            led10.value(1)
        if min == 58:
            led12.value(1)
            led14.value(1)
            led11.value(1)
        if min == 59:
            led12.value(1)
            led14.value(1)
            led08.value(1)
            led11.value(1)
        # Starte Zuordnung GPIO zur Zeit für STUNDEN
        if stu == 1:        
            led16.value(1)
        if stu == 2:
            led17.value(1)
        if stu == 3:
            led16.value(1)
            led17.value(1)
        if stu == 4:
            led18.value(1)
        if stu == 5:
            led16.value(1)
            led18.value(1)
        if stu == 6:
            led17.value(1)
            led18.value(1)
        if stu == 7:
            led16.value(1)
            led17.value(1)
            led18.value(1)
        if stu == 8:
            led19.value(1)
        if stu == 9:
            led16.value(1)
            led19.value(1)
        if stu == 10:        
            led20.value(1)
            led16.value(1)
        if stu == 11:
            led20.value(1)
            led16.value(1)
        if stu == 12:
            led20.value(1)
            led17.value(1)
        if stu == 13:
            led20.value(1)
            led16.value(1)
            led17.value(1)
        if stu == 14:
            led20.value(1)
            led18.value(1)
        if stu == 15:
            led20.value(1)
            led16.value(1)
            led18.value(1)
        if stu == 16:
            led20.value(1)
            led17.value(1)
            led18.value(1)
        if stu == 17:
            led20.value(1)
            led16.value(1)
            led17.value(1)
            led18.value(1)
        if stu == 18:
            led20.value(1)
            led19.value(1)
        if stu == 19:
            led20.value(1)
            led16.value(1)
            led19.value(1)
        if stu == 20:        
            led21.value(1)
        if stu == 21:
            led21.value(1)
            led16.value(1)
        if stu == 22:
            led21.value(1)
            led17.value(1)
        if stu == 23:
            led21.value(1)
            led16.value(1)
            led17.value(1)
        if stu == 24: #??
            led21.value(1)
            led18.value(1)     
        time.sleep(1)
        #Reset LEDS
        led00.value(0) 
        led01.value(0) 
        led02.value(0) 
        led03.value(0) 
        led04.value(0) 
        led05.value(0) 
        led06.value(0) 
        led07.value(0)
        led08.value(0) 
        led09.value(0)
        led10.value(0)
        led11.value(0)
        led12.value(0)
        led13.value(0)
        led14.value(0)
        #led15.value(0)
        led16.value(0)
        led17.value(0)
        led18.value(0)
        led19.value(0)
        led20.value(0)
        led21.value(0)
        led22.value(0)
    #    led24.value(0)
        loop1 = loop1 + 1          
    if loop1 >= 31: # oder setze loop1loops
#        exec(open('temperatur.py').read())
###
        # Setup Temperaturmessung und Konvertierung
        sensor_temp = machine.ADC(4) 
        conversion_factor = 3.3 / (65535) 
        #startsequenz optional mit #Buzzer
        #buzzer.value(1)
        #utime.sleep(1)
        #buzzer.value(0)
        #utime.sleep(1)
        #Welcome
        led14.value(1)
        led09.value(1)
        led13.value(1)
        led10.value(1)
        utime.sleep(1)
        #Welcome Ende
        led14.value(0)
        led09.value(0)
        led13.value(0)
        led10.value(0)
        #utime.sleep(1)
        while True:
                loop2 = 0
                while loop2 <= 2:
                    h = 0
                    o = 0
                    reading = sensor_temp.read_u16() * conversion_factor
                    temperature = round(27 - (reading - 0.706) / 0.001721)
                    tempa=temperature
                    #print("TEMPERATUR")
                    #print (tempa)
                    #print("  " + "{:.0f}".format(temperature) + "." + "c", 10, 30, 0, 7)
                    utime.sleep(1)      
                    #print(loop2)        
                    #LED zeigen Temperaturbereiche an    
                    if tempa == 0:
                        led22.value(1)              
                    if tempa == 1:
                        led00.value(1)           
                    if tempa == 2:
                        led01.value(1)
                    if tempa == 3:
                        led00.value(1)
                        led01.value(1)           
                    if tempa == 4:
                        led02.value(1)         
                    if tempa == 5:
                        led00.value(1)
                        led02.value(1)                
                    if tempa == 6:
                        led01.value(1)
                        led02.value(1)            
                    if tempa == 7:
                        led00.value(1)
                        led01.value(1)
                        led02.value(1)
                    if tempa == 8:
                        led03.value(1)
                    if tempa == 9:
                        led00.value(1)
                        led03.value(1)
                    if tempa == 10:
                        led04.value(1)
                    if tempa == 11:
                        led00.value(1)
                        led04.value(1)
                    if tempa == 12:
                        led01.value(1)
                        led04.value(1)
                    if tempa == 13:
                        led00.value(1)
                        led01.value(1)
                        led04.value(1)
                    if tempa == 14:
                        led02.value(1)
                        led04.value(1)
                    if tempa == 15:
                        led00.value(1)
                        led02.value(1)
                        led04.value(1)                  
                    if tempa == 16:
                        led01.value(1)
                        led02.value(1)
                        led04.value(1)            
                    if tempa == 17:
                        led00.value(1)
                        led01.value(1)
                        led02.value(1)
                        led04.value(1)
                    if tempa == 18:
                        led03.value(1)
                        led04.value(1)
                    if tempa == 19:
                        led00.value(1)
                        led03.value(1)
                        led04.value(1)
                    if tempa == 20:
                        led05.value(1)
                    if tempa == 21:
                        led00.value(1)
                        led05.value(1)
                    if tempa == 22:
                        led01.value(1)
                        led05.value(1)
                    if tempa == 23:
                        led00.value(1)
                        led01.value(1)
                        led05.value(1)
                    if tempa == 24:
                        led02.value(1)
                        led05.value(1)
                    if tempa == 25:
                        led00.value(1)
                        led02.value(1)
                        led05.value(1)
                    if tempa == 26:
                        led01.value(1)
                        led02.value(1)
                        led05.value(1)
                    if tempa == 27:
                        led00.value(1)
                        led01.value(1)
                        led02.value(1)
                        led05.value(1)
                    if tempa == 28:
                        led03.value(1)
                        led05.value(1)
                    if tempa == 29:
                        led01.value(1)
                        led03.value(1)
                        led05.value(1)
                    if tempa == 30:
                        led04.value(1)
                        led05.value(1)
                    if ((tempa>= 31) and (tempa<= 50)):
                        led00.value(1)
                    utime.sleep(5)
                    #Reset
                    led00.value(0)
                    led01.value(0)
                    led02.value(0)
                    led03.value(0)
                    led04.value(0)
                    led05.value(0)
                    led06.value(0)
                    led07.value(0)
                    led08.value(0)
                    led09.value(0)
                    led10.value(0)
                    led11.value(0)
                    led12.value(0)
                    led13.value(0)
                    led14.value(0)
                    led16.value(0)
                    led17.value(0)
                    led18.value(0)
                    led19.value(0)
                    led20.value(0)
                    led21.value(0)
                    led22.value(0)                    
                    loop2 = loop2 + 1
                    #print(loop2)
                    #startsequenz optional mit #Buzzer
                    #buzzer.value(1)
                    #utime.sleep(1)
                    #buzzer.value(0)
                    #utime.sleep(1)
                    #Welcome
                    led14.value(1)
                    led09.value(1)
                    led13.value(1)
                    led10.value(1)
                    utime.sleep(1)
                    #Welcome Ende
                    led14.value(0)
                    led09.value(0)
                    led13.value(0)
                    led10.value(0)
                    #utime.sleep(1)                  
                if loop2 >= 3:
                    break
                continue
#Ende