# coding=utf-8
import paho.mqtt.publish as publish
import socket
import time
import json
from os import environ

##  this agent reads from the solarmax inverter socket and
## publishes the data to a mqtt broker


inverter_ip = environ.get('INVERTER_IP')

# 12345 should be the port of the inverter
if environ.get('INVERTER_PORT'):
    inverter_port = int(environ.get('INVERTER_PORT'))
else:
    inverter_port = 12345

mqtt_broker_ip = environ.get('MQTT_BROKER_IP')
mqtt_broker_port = int(environ.get('MQTT_BROKER_PORT'))
mqtt_broker_auth = environ.get('MQTT_BROKER_AUTH')
mqtt_inverter_topic = environ.get('MQTT_INVERTER_TOPIC')

# PAC = "PAC" # AC power (W)
# PD01 = "PD01" # DC Power String 1 (W)
# PD02 = "PD02" # DC Power String 2 (W)
# PDC = "PDC" # DC Power (W)
# PDA = "PDA" # ????

# QAC = "QAC" # ????
# SAC = "SAC" # ????
# TKK = "TKK" # ????
# TNF = "TNF" # AC Freq (Hz)
# TYP = "TYP" # Type
# SWV = "SWV" # Software Version
# CAC = "CAC" # Start ups

# "DYR": "Year",
# "DMT": "Month",
# "DDY": "Day",
# "THR": "Hour",
# "TMI": "Minute",

# "TYP": "Type",


# KHR = "KHR" # poweronhours
# KYR = "KYR" # Energy year (kwh)
# KLY = "KLY" # energy Last year (kwh)
# KMT = "KMT" # Energy month (kwh)
# KLM = "KLM" # Energy last month (kwh)
# KDY = "KDY" # Energy day (wh)
# KLD = "KLD" # Energy yesterday (kwh)
# KT0 = "KT0" # Energy Total (kwh)
# PIN = "PIN" # Installed power (W)
# ADR = "ADR" # Adress
# PRL = "PRL" # relative Power % 
# UDC = "UDC" # DC Voltage (mv)
# UD01 = "UD01" # DC Voltage String 1 (mv)
# UD02 = "UD02" # DC Voltage String 2 (mv)

# UI1 = "UI1" # ????
# UI2 = "UI2" # ????
# UI3 = "UI3" # ????

# UM1 = "UM1" # Uac 10m L1
# UM2 = "UM2" # Uac 10m L2
# UM3 = "UM3" # Uac 10m L3


# UL1 = "UL1" # AC Voltage Phase 1
# UL2 = "UL2" # AC Voltage Phase 2
# UL3 = "UL3" # AC Voltage Phase 3
# IDC = "IDC" # DC Current
# ID01 = "ID01" # DC Current String 1
# ID02 = "ID02" # DC Current String 2
# IED = "IED" # Ierr DC Fehlerstrom
# IEE = "IEE" # Ierr AC Fehlerstrom

# IL1 = "IL1" # AC Current Phase 1
# IL2 = "IL2" # AC Current Phase 2
# IL3 = "IL3" # AC Current Phase 3
# IML1 = "IML1" # Iac mean L1
# IML2 = "IML2" # Iac mean L2
# IML3 = "IML3" # Iac mean L3
# PAM = "PAM" # ????
# SAL = "SAL" # Alarm Codes
# SYS = "SYS" # status code


# Sys parameter

status_codes = {
    20000: "Keine Kommunikation",
    20001: "In Betrieb",
    20002: "Zu wenig Einstrahlung",
    20003: "Anfahren",
    20004: "Betrieb auf MPP",
    20005: "Ventilator laeuft",
    20006: "Betrieb auf Maximalleistung",
    20007: "Temperaturbegrenzung",
    20008: "Netzbetrieb",
}


# SAL parameter
alarm_codes = { 
    0: 'kein Fehler',
    1: 'Externer Fehler 1',
    2: 'Isolationsfehler DC-Seite',
    4: 'Fehlerstrom Erde zu Groß',
    8: 'Sicherungsbruch Mittelpunkterde',
    16: 'Externer Alarm 2',
    32: 'Langzeit-Temperaturbegrenzung',
    64: 'Fehler AC-Einspeisung',
    128: 'Externer Alarm 4',
    256: 'Ventilator defekt',
    512: 'Sicherungsbruch',
    1024: 'Ausfall Temperatursensor',
    2048: 'Alarm 12',
    4096: 'Alarm 13',
    8192: 'Alarm 14',
    16384: 'Alarm 15',
    32768: 'Alarm 16',
    65536: 'Alarm 17'
}

# Max length of the message is 255 bytes
# --> max. 28 Parameters
field_map_inverter = {

    "KDY": "Energy_Day (Wh)",
    "KMT": "Energy_Month (kWh)",
    "KYR": "Energy_Year (kWh)",
    "KT0": "Energy_Total (kWh)",

    "PDC": "DC_Power (W)",
    "PD01": "DC_Power_String_1 (W)",
    "PD02": "DC_Power_String_2 (W)",

    "UD01": "DC_Voltage_String_1 (V)",
    "UD02": "DC_Voltage_String_2 (V)",

    "IDC": "DC_Current (A)",
    "ID01": "DC_Current_String_1 (A)",
    "ID02": "DC_Current_String_2 (A)",

    "PAC": "AC_Power (W)",
    "UL1": "AC_Voltage_Phase_1 (V)",
    "UL2": "AC_Voltage_Phase_2 (V)",
    "UL3": "AC_Voltage_Phase_3 (V)",
    
    "IL1": "AC_Current_Phase_1 (A)",
    "IL2": "AC_Current_Phase_2 (A)",
    "IL3": "AC_Current_Phase_3 (A)",

    "CAC": "Startups",
    "KHR": "poweronhours",
    "TKK": "inverter_operating_temp (C)",
    "SAL": "Alarm_Codes",
    "SYS": "status_Code",
}

req_data = "{FB;01;!!|64:&&|$$$$}"

def build_request(map):
    """ build the request message """
    r = ""
    for i in map:
        r = r+";"+i
    r = r[1:]
    req = req_data.replace("&&",r)
    # replace xy in req with length of string in 2 count hex
    req = req.replace('!!',format(len(req),'02X'))
    # replace $$$$ with checksum
    req = req.replace('$$$$',checksum((req[1:])[:-5]))
   
    return req

def checksum(data):
    """ calculate the checksum for the message """
    sum = 0
    print(data)
    for c in data:
        sum = sum + ord(c)
    # return 4 count hex value with leading zero
    print(sum)
    return format(sum, '04X')

def publish_message(topic, data, ip, port, auth):
    """ publish the message to the mqtt broker
    --- accepts a JSON payload
    --- publishs to the """
    ## following line is for local broker
    # client.publish(topic, json.dumps(data))
    publish.single(topic, payload=json.dumps(data), hostname=ip, port=port, auth=json.loads(auth), client_id="Energymeter",)
    print ('published: ' + json.dumps(data) + '\n' + 'to topic: ' + topic)
    return


def map_data(f, v):
    # Convert to useful Units

    if f == "SYS":
        if v in status_codes:
            return status_codes[v]
        else:
            return "Unknown Status Code"
    elif f == "SAL":
        if v in alarm_codes:
            return alarm_codes[v]
        else:
            return "Unknown Alarm Code"
    elif f == "PAC" or f == "PD01" or f == "PD02" or f == "PDC":
        return v/2
    elif f == "UL1" or f == "UL2" or f == "UL3" or f == "UDC" or f == "UD01" or f == "UD02": 
        return v/10.0
    elif f == "IDC" or f == "ID01" or f == "ID02" or f == "IL1" or f == "IL2" or f == "IL3":
        return v/100.0
    
    else:
        return v

def convert_to_json(map, data):
    # Example data:
    #b'{01;FB;EA|64:PAC=1F0A;PD01=CB2;PD02=13BA;PDC=206C;CAC=CAF;KHR=3DB3;KYR=B7E;KLY=14AB;KMT=BE;KLM=387;KDY=110;KLD=C6;KT0=4933;UDC=B70;UD01=B70;UD02=EAB;UL1=956;UL2=956;UL3=951;IDC=4CA;IL1=23F;IL2=23C;IL3=23C;SAL=0;SYS=4E28,0;TKK=31|3883}'
    data_split = data.split(':')[1].split('|')[0].split(';')
    test_dict = {}
    for i in data_split:
        field = i.split('=')[0]
        if field == "SYS":
            # Cutoff the ",0" in SYS status
            value = int(i.split('=')[1].split(',')[0], 16)
        else:
            value = int(i.split('=')[1], 16)
        test_dict[field] = {
            "Value": map_data(field, value),
            "Description": map[field],
            "Raw Value": value,
            
            }
    print(test_dict)
    return test_dict

def connect_to_inverter(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((ip, port))
    except socket.error as e:
        print( 'Failed to create socket: Error code: ' + str(e))
        return False
        # sys.exit()
    return s

def read_data(sock, request):
    print ('sending: ' + request)
    sock.send(bytes(request, 'utf-8'))
    data_received = False
    response = ''
    print ('waiting for response')
    while not data_received:
        buf = sock.recv(1024)
        print ('received: ' + str(buf))
        if len(buf) > 0:
            response = response + str(buf)
            data_received = True
    print ('received: ' + response)
    return response

def generate_empty_data(map):
    data = {}
    for i in map:
        if i == "SYS":
            data[i] = {
                "Value": "Keine Kommunikation",
                "Description": map[i],
                "Raw Value": "20000",
                }
        data[i] = {
            "Value": "0",
            "Description": map[i],
            "Raw Value": "0",
            }
    return data

def main():
    print ("starting...")
    req_data_inverter = build_request(map=field_map_inverter) 
    while True:
        try:
            inv_s = connect_to_inverter(ip= inverter_ip, port= inverter_port)
            print ("connected to inverter")
            if inv_s:
                data = read_data(inv_s, req_data_inverter)
                json_data = convert_to_json(map=field_map_inverter, data=data)
                publish_message(topic=mqtt_inverter_topic, data=json_data, ip=mqtt_broker_ip, port=mqtt_broker_port, auth=mqtt_broker_auth)
                inv_s.close()
                time.sleep(10)
            else:
                json_data = generate_empty_data(map=field_map_inverter)
                publish_message(topic=mqtt_inverter_topic, data=json_data, ip=mqtt_broker_ip, port=mqtt_broker_port, auth=mqtt_broker_auth)
                time.sleep(30)

        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            continue

main()