import smbus2
import asyncua
import math

import logging
import asyncio
import sys
from asyncua import ua, Server
from asyncua.common.methods import uamethod

sys.path.insert(0, "..")

bus = smbus2.SMBus(1)
MPU = 0x68

@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger('asyncua')
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)
    
    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, 'MyObject')
    Accx = await myobj.add_variable(idx, 'MyVariable', 0.0)
    Accy = await myobj.add_variable(idx, 'MyVariable1', 0.0)
    Accz = await myobj.add_variable(idx, 'MyVariable2', 0.0)
    # Set MyVariable to be writable by clients
    await Accx.set_writable()
    await Accy.set_writable()
    await Accz.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    _logger.info('Starting server!')
    async with server:
        while True:
            acc_x_high = bus.read_byte_data(MPU, 0x3b)
            acc_x_low = bus.read_byte_data(MPU, 0x3c)
            acc_y_high = bus.read_byte_data(MPU, 0x3d)
            acc_y_low = bus.read_byte_data(MPU, 0x3e)
            acc_z_high = bus.read_byte_data(MPU, 0x3f)
            acc_z_low = bus.read_byte_data(MPU, 0x40)
            
            
            acc_x = (acc_x_high << 8) + acc_x_low
            acc_y = (acc_y_high << 8) + acc_y_low
            acc_z = (acc_z_high << 8) + acc_z_low
         
          
            await asyncio.sleep(1)
            new_val_x = acc_x
            new_val_y = acc_y
            new_val_z = acc_z
            await Accx.write_value(float(new_val_x))
            await Accy.write_value(float(new_val_y))
            await Accz.write_value(float(new_val_z))


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main(), debug=True)

