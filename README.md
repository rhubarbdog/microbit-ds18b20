# microbit-ds18b20 - a ds18b20 thermometer class

This is a class for the dallas ds18b20 thermometer it has the following methods.

`read` - has a single the argument it can be  READ_SCRATCH, SEARCH_ROM or READ_ROM. 8 or 9 bytes of data is returned

`temperature` - has a single argument the scratchpad, which it processes bytes 0 and 1 to create a decimal number

`write_scratch` - write arguments register tH, register tL and the number of bits resolution to the scratchpad adjusting the running of the device.

`scratch_data` - has a single argument the scratchpad and returns a list of the scratchpad data, register tH, register Tl and bits of resolution

`match_rom` - has a single argument the ROM code, this method signals to a ds18b20 that the next read, write or command is for it.

methods with no arguments.
`parasitic_power` - has return True if the sensor is running on parasitic power

`skip_rom` - alerts all roms that the next instruction is for them to processs such as converting the temperature on all sensors simultaneously or can be used when ther is only on sensor on the wire to avoid having to match the rom before each operation.

`read_rom` - gets the ROM code of the *ONLY* sensor on this wire

`convert` - instruct the sensor to convert raw data into a temperature and write to scratchpad, this takes some time between 90ms and 750ms the sensor signals when ready, one can wait with the `convert_wait` method, sleep or just get on with processing knowing plenty of time will have elapsed

`convert_wait` - use this method imediately after the `conver` method to pause processing until the ds18b20 is ready for the next operation

`reset` - use this method on a new powered up sensor to initialise or to correct alarm coditions or other running issues


single operation is as follows

```
sensor = DS18B20(pin0)

sensor.reset()
sensor.skip_rom()
sensor.convert()
sleep(1000)

sensor.skip_rom()
data = sensor.read(sensor.READ_SCRATCH)
print(sensor.temperature(data))
```