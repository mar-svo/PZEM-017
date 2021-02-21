"""
<plugin key="PZEM-017" name="PZEM-017 Modbus" author="Maxim" version="2020.02">
    <description>
        <h3>PZEM-017 Modbus</h3>
        https://github.com/mar-svo/PZEM-017
        Simple plugin for monitoring small photovoltaic power plant (actual current, actual voltage and actual/produced energy).
    </description>
    <params>
        <param field="SerialPort" label="SerialPort" width="140px" default="/dev/ttyUSB0"/>
        <param field="Port" label="Debug mode" width="140px" required="true">
            <options>
                <option label="NO" value="0"/>
                <option label="YES" value="1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import gettext
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class PZEM_017:

    def __init__(self):
        
        # TRANSLATE CMDs:
        #   pygettext3.8 -d base -o locales/base.pot plugin.py
        #   locales/cs/LC_MESSAGES# msgfmt -o base.mo base
        translate = gettext.translation('base', localedir='plugins/bmr-hc64/locales', fallback=True, languages=['cs'])
        translate.install()
        _ = translate.gettext
       
        self.uVoltage = 1
        self.uCurrent = 2
        self.uPower = 3
                
        return

    def onStart(self):
                
        if (Parameters["Port"] == "1"):
            Domoticz.Debugging(1)
            DumpConfigToLog()
            Domoticz.Debug("***** NOTIFICATION: Debug is enabled!")
        else:
            Domoticz.Debugging(0)
        Domoticz.Debug("onStart called")
        
        Domoticz.Heartbeat(int(10)) # Device pollrate (heartbeat) : 10s

        self.Port = Parameters["SerialPort"]
        
        if self.uVoltage not in Devices: Domoticz.Device(Unit=self.uVoltage, DeviceID="Voltage", Name=_("Voltage"), Type=243, Subtype=8, Used=1).Create()
        if self.uCurrent not in Devices: Domoticz.Device(Unit=self.uCurrent, DeviceID="Current", Name=_("Current"), Type=243, Subtype=23, Used=1).Create()
        if self.uPower not in Devices: Domoticz.Device(Unit=self.uPower, DeviceID="Power", Name=_("Power"), Type=243, Subtype=29, Used=1).Create()
        
        return

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
                       
        try: 
            client = ModbusClient(method='RTU', port=self.Port, timeout=1, baudrate=9600, stopbits=2, bytesize=8, parity='N')
            client.connect()
        except: Domoticz.Error("Can not connect to Modbus on: " + self.Port)
        
        try: data = client.read_input_registers(0, 6)
        except: Domoticz.Error("Modbus communication error - cannot read data. Check it out!")
        
        try:dataDecoder = BinaryPayloadDecoder.fromRegisters(data.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        except: Domoticz.Error("Modbus communication error - cannot decode data. Check it out!")

        #0x0000    Voltage value            1LSB correspond to 0.01V
        voltage = dataDecoder.decode_16bit_int() / 100
        Domoticz.Debug("voltage = " + str(voltage) + " V")

        #0x0001    Current value            1LSB correspond to 0.01A
        current = dataDecoder.decode_16bit_int() / 100
        Domoticz.Debug("curent = " + str(current) + " A")

        #0x0002    Power value low 16 bits  1LSB correspond to 0.1W
        #0x0003    Power value high 16 bits    
        power = dataDecoder.decode_32bit_int() / 10
        Domoticz.Debug("power = " + str(power) + " W")

        #0x0004    Energy value low 16 bits 1LSB correspond to 1Wh
        #0x0005    Energy value high 16 bits    
        energy = dataDecoder.decode_32bit_int()
        Domoticz.Debug("energy = " + str(energy) + " Wh")

        Devices[self.uVoltage].Update(0, str(voltage))
        Devices[self.uCurrent].Update(0, str(current))
        Devices[self.uPower].Update(0, str(power) + ";" + str(energy))

        return 

global _plugin
_plugin = PZEM_017()

def onStart():
    global _plugin
    _plugin.onStart()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device ID='" + str(Devices[x].ID) + "', DeviceID='" + str(Devices[x].DeviceID) + "', Name='" + Devices[x].Name 
                       + "', nValue='" + str(Devices[x].nValue) + "', sValue='" + Devices[x].sValue + "', LastLevel='" + str(Devices[x].LastLevel) 
                       + "', Type='" + str(Devices[x].Type) + "', SubType='" + str(Devices[x].SubType) + "', SwitchType='" + str(Devices[x].SwitchType) + "'")

    return
