# Boiler_Control_Micropython
<b>Overengineering ON/OFF Boiler Control.</b>

So this is my project. The purpose of this (project) is to have a remote control to on/off my electrical boiler from my phone... BUT... That's too simple for a personal project.
In essence, this is an on/off relay control.

But why micropython?... because. ʘ_ʘ

<b>The begging -THE Wifi-</b>

First I want this thing to be remote, so I have two options a long stick to push the on/off button, or a wifi-way to sort that out. With that in mind, I have to choose a microcontroller with Wifi... So the ESP32 it is. In the beginning, I used a generic one (ESP32-WROOM-32) but It has a horrible WifI connection response, some times get connected to it, and some times doesn't, or some times just get connected and then dropoff the connection, and that's it, see you next day that I'll have cool-off my wifi stress. (Somehow with arduino this doesn't happen ¯\\_(ツ)_/¯.)

<b>Changing the board.</b>

So now I have to change something because this doesn't work. So I get the Heltec Lora ESP32 v2 with OLED... (Ooohhh that's something that I missed out on. On the first try, I  was using an LCD16x2 whit i2c control). OLED and LORA, NOW we are talking (but I didn't use the Lora), so now I have a stable Wifi connection and we can start working.

<b>How to connect to the wifi?</b>

In the begging, I was looking for the usual do_connect() that it's in the official documentation but then I found out the wifi manager from this github https://github.com/tayfunulu/WiFiManager It's really good but in the end, I couldn't make it work with the mqtt_as library... Oh, that's right!

<b>THE MQTT_AS Library</b>

So this is amazing. I was trying to use the simple.umqtt library from micropython but I was having all kinds of troubles and strange bugs and when I was trying to do some async methods, making some research found out that that already existed, and it was really good and I got it from here https://github.com/peterhinch/micropython-mqtt/tree/master/mqtt_as

<b>The Payload</b>

JSON of course but what should have content? so my JSON payload should have com_rx that define if a message of ON was received or was a local operation, a timer that gives us the time that is left to complete the on cycle, and equipment name, in this case, is my "Boiler G&E", the core temperature of my esp32 (just because ¯\\_(ツ)_/¯) a local state of my boiler if is on or off, external temperature measurement and a timestamp.

<b>The Timesatmp</b>

So for this, I got an NTP local server to sync and use the NTP and RTC functions of the micropython... no big mysteries here.

<b>The Termometer</b>

For this I use a DS18B20 it was a little bit tricky because at some point fail in some readings but nothing that a practical code can't fix.

<b>The Secret File</b>

This kind of solution here get me happy I have 3 variables that can change in time for external reasons so I get whit this JSON file that load all the variables so you don't need to mess with the code every time you change your wifi password or the NTP server or the MQTTserver or maybe the topics and the timer.
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

Something happened here, a blackout (kind of...) I have to change the power supply (cellphone charger) of the prototype because it got unstable and was making the microcontroller reboot for no reason (then I have other issues but you can see in the commits) so i came with this OTHER file that saves the last state just before the MQTT payload is sent, so if an unwanted reboot happened the microcontroller can pick up from when it left.
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
3. Parameters OK! check the secret file that is loads.
4. WIFI OK! chek, the Wifi connection it's done.
5. NTP Sync OK! Sync with the local NTP Server, if I get an error here it will reboot and try again.
6. MQTT Server OK! check the availability of the MQTT server whit a ping... (the uping library I got it from here https://github.com/olavmrk/python-ping ).

- Work Screen
1. TIMER OFF: 00:00 here display the count down of the TIMER OFF
2. BOILER OFF or BOILER ON
3. HORA OFF! here display the estimated time (local time) that it will be off.
4. TEMP here display the Boiler temperature that reads the DS18B20

Hope to include some schematics and nice pictures soon...
