################################
# Author: Luis Sanchez         #
# Date: November 20, 2021      #
# Feel free to ask me anything #
# luis.sanchez3   gmail        #
################################

# LIBRERIA GENERALES
from machine import Pin, SoftI2C, freq, RTC, reset
from esp32 import raw_temperature
from time import sleep
from ubinascii import hexlify
import uasyncio as asyncio
import _thread
# LIBRERIA WIFI
from network import WLAN, STA_IF
from uping import ping
# LIBRERIA SENSOR TEMPERATURA
from onewire import OneWire, OneWireError
from ds18x20 import DS18X20
# LIBRERIA MQTT
from mqtt_as import MQTTClient, config
# LIBRERIA JSON
from ujson import dumps, loads, load, dump
# LIBRERIA OLED
from ssd1306 import SSD1306_I2C
# LIBRERIA NTP
from ntptime import host, settime
# LIBRERIA MEMORIA RAM
from gc import enable, collect
enable()

# PERIFERICOS ENTRADAS Y SALIDAS
boton_reset = Pin(2, Pin.IN)  # Reset
boton_on_off = Pin(17, Pin.IN)  # ON OFF
boiler_out = Pin(33, Pin.OUT, value=0)  # Boiler Salida
boiler_in = Pin(32, Pin.IN)  # Boiler Entrada
led = Pin(25, Pin.OUT, value=0)  # LED Indicador
collect()

# CARGAR ARCHIVO SECRETO
with open("secret.json") as f:
    secret = load(f)
    print('Se cargo archivo secret...')
    f.close()
    sleep(2)
    collect()

# CARGAR ARCHIVO STANDBY
with open("standby.json") as f:
    standby = load(f)
    print("Se cargo archivo standby...")
    f.close()
    sleep(2)
    collect()

# ESP32
freq(240000000)
freq_esp = freq()/1000000
print(f'Frecuencia de operacion ESP32: {freq_esp} MHz')
sleep(2)
collect()

# OLED
rst = Pin(16, Pin.OUT)
rst.value(1)
scl = Pin(15, Pin.OUT, Pin.PULL_UP)
sda = Pin(4, Pin.OUT, Pin.PULL_UP)
i2c = SoftI2C(scl=scl, sda=sda, freq=450000)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)
collect()


def oled_cls():
    oled.fill(0)
    oled.show()
    collect()


oled_cls()


def oled_r0(msg, x):
    oled.text(str(msg), x, 0)
    oled.show()
    collect()


def oled_r1(msg, x):
    oled.text(str(msg), x, 10)
    oled.show()
    collect()


def oled_r2(msg, x):
    oled.text(str(msg), x, 20)
    oled.show()
    collect()


def oled_r3(msg, x):
    oled.text(str(msg), x, 30)
    oled.show()
    collect()


def oled_r4(msg, x):
    oled.text(str(msg), x, 40)
    oled.show()
    collect()


def oled_r5(msg, x):
    oled.text(str(msg), x, 50)
    oled.show()
    collect()


def oled_reng(x):
    if x < 0 or x > 5:
        print("OLED SIN RENGLON")
        oled.fill(0)
        oled.text('ERROR OLED', 0, 10)
        oled.text('NO RENGLON', 0, 30)
        oled.show()
        collect()
    if x >= 0 or x <= 5:
        oled.fill_rect(0, (x*10), 128, 10, 0)
        oled.show()
        collect()


def oled_t(msg):
    oled.fill_rect(85, 10, 42, 10, 0)
    oled.text(str(msg), 85, 10)
    oled.show()
    collect


try:
    oled_cls()
    oled_r0('BOILER SC', 26)
    oled_r2('SECUENCIA DE', 0)
    oled_r3('INICIO', 0)
except:
    pass
collect()
sleep(2)

# TEMPERATURA ESP32


def esp_temp():
    tf = raw_temperature()
    tc = (tf-32.0)/1.8
    collect()
    return round(tc, 2)


# SENSOR TEMPERATURA DS18B20
collect()
ds_pin = Pin(22)
ds_sensor = DS18X20(OneWire(ds_pin))
sleep(0.750)
roms = ds_sensor.scan()
sleep(0.750)

try:
    while True:
        if not roms:
            sleep(0.750)
            roms = ds_sensor.scan()
        else:
            try:
                oled_cls()
                oled_r0('BOILER SC', 26)
                oled_r1('Termometro: OK!', 0)
            except:
                pass
            break
except:
    pass
print('Dispositivo Termometor DS18B20 Encontrado:', roms)
collect()

# INICIALIZANDO WIFI
collect()
wlan = WLAN(STA_IF)
sleep(1)
print('Iniciando Controlador Wifi modo cliente...')
mac = hexlify(WLAN().config('mac'), ':').decode()
print('MAC Address de Controlador wifi:', str.upper(mac))
sleep(1)
collect()


def do_conn_sync(ssid, passwd):
    wlan.active(True)
    collect()
    if wlan.isconnected():
        return None
    print('Intentando conexion a %s...' % ssid, tm_stmp())
    wlan.connect(ssid, passwd)
    collect()
    for retry in range(100):
        connected = wlan.isconnected()
        collect()
        if connected:
            break
        sleep(0.1)
        print('.', end='')
        collect()
    if connected:
        print('\n¡Conexión Inalámbrica Exitosa!', tm_stmp())
        print(
            f'Configuración de red\nIP: {wlan.ifconfig()[0]}\nNetmask: {wlan.ifconfig()[1]} \nGateway: {wlan.ifconfig()[2]}\nDNS: {wlan.ifconfig()[3]}')
        print('Sincronizando con servidor NTP...', tm_stmp())
        asyncio.run(tm_sync(secret['ntp_host']))
        collect()
    else:
        print('\nIntento de Conexion Fallido: ' + ssid, tm_stmp())
        collect()
    return connected

# SINCRONIZACION TIEMPO NTP


def tm_stmp():
    collect()
    return str("{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}:{}".format(RTC().datetime()[0], RTC().datetime()[1], RTC().datetime()[2], RTC().datetime()[4], RTC().datetime()[5], RTC().datetime()[6], str(RTC().datetime()[7])[:3]))


async def tm_sync(host):
    collect()
    r = 0
    while r == 0:
        try:
            host = host
            print('Servidor NTP:', host)
            await asyncio.sleep(1)
            settime()
            (year, month, mday, weekday, hour, minute,
             second, milisecond) = RTC().datetime()
            RTC().init((year, month, mday, weekday, hour-7, minute, second, milisecond))
            print("Tiempo sincronizado:", tm_stmp())
            collect()
            r = 1
        except OverflowError as e:
            print('ERROR DESBORDAMIENTO DE MEMORIA')
            print(e)
            reset()
        except OSError as e:
            print('Error de conexion con servidor...')
            print(e)
            reset()

# PAQUETES JSON
a = {"equipo": "Boiler G&E 110v",
     "temperatura": "",
     "estado": False,
     "coretemp": "",
     "timestamp": "",
     "timer": 0,
     "com_rx": False
     }

collect()

b = {"comando": False}

collect()


def msg_tx():
    try:
        collect()
        if boiler_in.value() == 0:
            a['estado'] = False
            standby['estado'] = False
        if boiler_in.value() == 1:
            a['estado'] = True
            standby['estado'] = True
        a['coretemp'] = esp_temp()
        a['timestamp'] = tm_stmp()
        return bytes(dumps(a), 'UTF-8')
    except ValueError as e:
        print('Error al procesar paquete JSON de salida:', e, tm_stmp())


def msg_rx(r):
    global task
    collect()
    try:
        b = loads(r)
        if b['comando'] == True:
            if boiler_in() == 1:
                pass
            else:
                task = asyncio.create_task(boiler_on())
        elif b['comando'] == False:
            if boiler_in() == 0:
                pass
            else:
                a['com_rx'] = False
        else:
            print("Error en mando", tm_stmp())
        collect()
    except ValueError as e:
        print('Error al procesar paquete JSON de entrada:', e, tm_stmp())

# MQTT


def callback(topic, msg, retained):
    msg_rx(msg)


async def conn_han(client):
    await client.subscribe(bytes(secret['topic_sub'], 'UTF-8'), 1)


async def main_mqtt(client):
    await client.connect()
    while True:
        await client.publish(bytes(secret['topic_pub'], 'UTF-8'), msg_tx(), qos=1)
        print('Paquete MQTT enviado...', tm_stmp())
        save_standby()
        print('Estado standby salvado...', tm_stmp())
        collect()

config['subs_cb'] = callback
config['connect_coro'] = conn_han
config['server'] = secret['mqtt_server']
config['ssid'] = secret['ssid']
config['wifi_pw'] = secret['password']
config['client_id'] = secret['client_mqtt']

collect()
MQTTClient.DEBUG = True
client = MQTTClient(config)
print('Parametros de conexion a servidor MQTT Cargados...')
sleep(2)
collect()

# LOGICA


def res_boton():
    collect()
    btn_prev = boton_reset.value()
    while (boton_reset.value() == 1) or (boton_reset.value() == btn_prev):
        collect()
        btn_prev = boton_reset.value()
        sleep(0.04)
    collect()
    print('Boton Reset Presionado')
    standby['estado'] = False
    standby['timer'] = 0
    save_standby()
    reset()


def on_boton():
    collect()
    while True:
        collect()
        btn_prev = boton_on_off.value()
        while (boton_on_off.value() == 1) or (boton_on_off.value() == btn_prev):
            collect()
            btn_prev = boton_on_off.value()
            sleep(0.04)
        if boiler_in() == 1:
            collect()
            a['com_rx'] = False
            print('Boton OFF Presionado')
        else:
            collect()
            task = asyncio.create_task(boiler_on())
            print('Boton ON Presionado')


async def cuenta(t):
    while t:
        collect()
        mins, secs = divmod(t, 60)
        oled_t('{:02d}:{:02d}'.format(mins, secs))
        await asyncio.sleep(1)
        t -= 1
        mins, secs = divmod(t, 60)
        oled_t('{:02d}:{:02d}'.format(mins, secs))
        a['timer'] = t
        standby['timer'] = t
        if a['com_rx'] == False:
            break


async def boiler_on():
    timer = int(secret['timer'])
    hora(timer)
    print('Inicia Secuencia de Encendido...', tm_stmp())
    boiler_out.on()
    led.on()
    oled_reng(2)
    oled_r2('BOILER ON!', 0)
    a['com_rx'] = True
    collect()
    await cuenta(timer)
    collect()
    print('Temporizador terminado...', tm_stmp())
    boiler_out.off()
    led.off()
    await boiler_off()
    collect()


async def boiler_off():
    print('Inicia Secuencia de Apagado...', tm_stmp())
    boiler_out.off()
    led.off()
    oled_reng(2)
    oled_r2('BOILER OFF!', 0)
    oled_t('00:00')
    collect()


async def boiler_continue():
    timer = int(standby['timer'])
    hora(timer)
    print('Inicia Secuencia de Encendido...', tm_stmp())
    boiler_out.on()
    led.on()
    oled_reng(2)
    oled_r2('BOILER ON!', 0)
    a['com_rx'] = True
    collect()
    await cuenta(timer)
    collect()
    print('Temporizador terminado...', tm_stmp())
    boiler_out.off()
    led.off()
    await boiler_off()
    collect()


def sh_temp():
    collect()
    oled_r4('Cent', 95)
    while True:
        collect()
        roms = ds_sensor.scan()
        try:
            collect()
            ds_sensor.convert_temp()
            bt = ds_sensor.read_temp(roms[0])
            collect()
            if bt != None:
                x.acquire()
                a['temperatura'] = round(bt, 2)
                t = a['temperatura']
                x.release()
                oled.fill_rect(40, 40, 55, 10, 0)
                oled.text(str(t), 40, 40)
                oled.show()
        except OneWireError:
            print('Error en sensor de temperatura...', tm_stmp())
        except RuntimeError as e:
            print('OneWire Error:' + e, tm_stmp())
        except:
            print('OneWireError desconocido...', tm_stmp())
        sleep(1)


def hora(t):
    collect()
    m = RTC().datetime()[5]
    h = RTC().datetime()[4]
    t = int((t+480)/60)
    x = int((h * 60) + m + t)
    h, m = divmod(x, 60)
    if h == 24:
        h = 0
    elif h == 25:
        h = 1
    elif h == 26:
        h = 2
    oled.fill_rect(75, 30, 53, 10, 0)
    oled_r3('{:02d}:{:02d}'.format(h, m), 75)
    collect()


# SECUENCIA DE INICIO
try:
    oled_r2('Parametros: OK!', 0)
    sleep(1)
except:
    print('Error OLED...')

collect()

try:
    while True:
        if wlan.isconnected() == True:
            oled_r3('Wifi:       OK!', 0)
            sleep(1)
            oled_r4('NTP Sync:   OK!', 0)
            break
        else:
            do_conn_sync(secret['ssid'], secret['password'])
except:
    print('Error conexion Wifi y Sync...')

collect()

try:
    p = ping(secret['mqtt_server'])
    if p[1] == 4:
        oled_r5('MQTT Server:OK!', 0)
        print('Servidor MQTT en Linea...')
    elif p[1] > 0 or p[1] < 4:
        oled_r5('MQTT Serv: Weak', 0)
    elif p[1] == 0:
        oled_r5('MQTT Serv: OFF!', 0)
        print('Servidor MQTT Fuera de Linea...')
except:
    print('Error conexion servidor MQTT')

sleep(5)
collect()

# BUCLE PARA PURGAR LAS PRIMERAS MALAS MEDICIONES DEL DS18B20
while True:
    roms = ds_sensor.scan()
    collect()
    ds_sensor.convert_temp()
    bt = ds_sensor.read_temp(roms[0])
    collect()
    if bt != None:
        a['temperatura'] = round(bt, 2)
        print('Purga de valores de temperatura:', a['temperatura'], '°C')
        break
    sleep(1)
collect()

# LOCK DE THREAD
x = _thread.allocate_lock()
collect()
# PANTALLA PRINCIPAL
oled_cls()
oled_r0('BOILER SC', 26)
oled_r1('TIMER OFF:', 0)
oled_r4('TEMP:', 0)
oled_r3('HORA OFF:', 0)
oled_r2('BOILER OFF!', 0)
collect()

# FUNCIONES ULTIMO ESTADO


def save_standby():
    with open('standby.json', 'w') as outfile:
        dump(standby, outfile)
        collect()


def ultimo_estado():
    if standby['estado'] == True:
        print('Se detecto una operación interurmpida...')
        sleep(2)
        print('Se incia secuencia de continuacion de operación...')
        sleep(2)
        print('standby.json = ', standby)
        task = asyncio.create_task(boiler_continue())
    else:
        print('No hay operacion interrumpida...')


collect()
# FUNCIONES PRINCIPALES
collect()
_thread.start_new_thread(res_boton, ())
collect()
_thread.start_new_thread(on_boton, ())
collect()
_thread.start_new_thread(sh_temp, ())
collect()
_thread.start_new_thread(ultimo_estado, ())
collect()
asyncio.run(main_mqtt(client))
collect()
