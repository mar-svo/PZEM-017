
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

client = ModbusClient(method='RTU', port='/dev/ttyUSB0', timeout=1, baudrate=9600, stopbits=2, bytesize=8, parity='N')

if not client.connect():
    print("unable to connect")
    exit(-1)

# TEST: Read and print ALL 8 registers:
print("TEST ALL 8 registers: " + str(client.read_input_registers(0, 8, unit=0x01).registers) + "\n")


data = client.read_input_registers(0, 6)
dataDecoder = BinaryPayloadDecoder.fromRegisters(data.registers, byteorder=Endian.Big, wordorder=Endian.Little)
    
#0x0000    Voltage value            1LSB correspond to 0.01V
voltage = dataDecoder.decode_16bit_int() / 100
print("voltage = " + str(voltage) + " V")

#0x0001    Current value            1LSB correspond to 0.01A
current = dataDecoder.decode_16bit_int() / 100
print("curent = " + str(current) + " A")

#0x0002    Power value low 16 bits  1LSB correspond to 0.1W
#0x0003    Power value high 16 bits    
power = dataDecoder.decode_32bit_int() / 10
print("power = " + str(power) + " W")

#0x0004    Energy value low 16 bits 1LSB correspond to 1Wh
#0x0005    Energy value high 16 bits    
energy = dataDecoder.decode_32bit_int()
print("energy = " + str(energy) + " Wh")


#0x0006    High voltage alarm status 0xFFFF is alarm,0x0000 is not alarm
#0x0007    Low voltage alarm status 0xFFFF is alarm,0x0000 is not alarm
