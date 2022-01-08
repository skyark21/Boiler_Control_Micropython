# Boiler_Control_Micropython
<b>Overengineering ON/OFF Boiler Control.</b>

So this is my project. The purpose of this is to have a remote control to on/off my electrical boiler from my phone... BUT, Thats to simple for a personal project.
In essense this is an on/off relay control.

But why micropython?... because. ʘ_ʘ

<b>The begging -THE Wifi-</b>

First I want this thing to be remote so I have two options a long stick to push the botton or a wifi-way to sort that out, so with that in mind I have to choose the microcontroller with Wifi... So the ESP32 it is. At the beggining I used a generic one but It has a horrible connection response, some time it get connected it times doesn't or maybe just was connected and then drop the connection and thats it, see you next day that I'll have cooloff my wifi stress. (Some how with arduino this doesn't happend ¯\\_(ツ)_/¯.)

<b>Changing the board.</b>

So Now i have to change somethin because this doesnt work. So I get the Heltec Lora ESP32 v2 with OLED... (Ooohhh thats something that I missed out the first try was with a LCD16x2 whit i2c control). OLED and LORA, knwo we are talking (but i didn't use the Lora), so know I have a stable Wifi connection and we can start working.

<b>How to connect to the wifi?</b>

At the begging I was looking for the usual do_connect() that it's in the documentation but then I found the wifimanager from this github https://github.com/tayfunulu/WiFiManager It's really good but at the end I coudnt make it work with the mqtt_as library... Oh thats right!

<b>THE MQTT_AS Library</b>

So this is amazing i was trying to use the simple.umqtt library from micropython but I was having all kinds of trouble and when I was trying to do some async methods, found that that allready existed, and it was really good and i got it from here https://github.com/peterhinch/micropython-mqtt/tree/master/mqtt_as

<b>The Payload</b>

JSON ofcourse but what shoud have content? so my JSON payload shoud have com_rx that define if a message of on was received or was a local opration, a timer that give us the time that is left to complete the on cycle, a equipment name in this case is my Boiler G&E, the coretemp of my esp32 (just because ¯\\_(ツ)_/¯) a local state of my boiler if is on or off, an external temperature metter and a timestamp.

<b>The Timesatmp</b>

So for this i got a NTP local server to sync and use the NTP and RTC functions of the micropython... no big misteries here.

<b>The Termometer</b>

For this I use a DS18B20 it was a little bit tricky because at some point fail in some readings but nothing that a practical code can't fix.

<b>The Secret File</b>

This kinf od solution here get me really happy I have 3 variables that can change in time for external reazons so i get whit this json file that load all the variables so you don't need to mess with the code everythime you shange your wifi password or the ntp server or the mqtt server or maybe the topics and the timer.
```
{
    "ssid": "Example SSID",
    "password": "Example SSID PASSWORD",
    "ntp_host": "Exapmle pool.this.is.not",
    "mqtt_server": "this.is.not.mqtt.server",
    "topic_pub": "/please/change/this/topic",
    "topic_sub": "/also/change/this/topic/too",
    "client_mqtt": "some hardware number",
    "timer": 5400
}
```

<b>The Satndby File</b>

Something happend here, a blackout (kindof...) I have to change the power supply (cellphone charger) of the prototype because it got unstable and was makeing the microcontroller reboot for no reazon (then i have other issues but you can see in the commits) so i came with this OTHER file that saves thet last state just before the MQTT payload is sended, so if an unwanted reboot happend the microcontroller can pickup from when it left.
THIS LITTLE FILE SAVED ME FOR SOME HEADACHES.
```
{
    "estado" : false,
    "timer" : 0
}
```

<b>But what do you display in the OLED</b>

- Boot sequences 
1. Display the Name of the Project. BOILER SC (what does SC stand for?... ¯\\_(⊙︿⊙)_/¯)
2. Termometter OK! it reads the DS18B20.
3. Parammeters OK! check the secret file that is loades.
4. WIFI OK! chek the Wifi connection it's done.
5. NTP Sync OK! Sync with the local NTP Server, if i get an error here it will reboot and try again.
6. MQTT Server OK! check the aviability of the MQTT server whit a ping... (the uping library i got it from here https://github.com/olavmrk/python-ping ).

- Work Screen
1. TIMER OFF: 00:00 here display the count down of the TIMER OFF
2. BOILER OFF or BOILER ON
3. HORA OFF! here display the estimated time (local time) that it will be off.
4. TEMP here display the Boiler temperatura that reads the DS18B20

Hope to inlcude some schematics and nice pictures soon...
