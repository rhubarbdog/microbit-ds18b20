# microbit-ds18b20 - a ds18b20 thermometer class

This is a class for the dallas ds18b20 thermometer it has the following methods.

`read` - has a single the argument it can be  READ_SCRATCH, SEARCH_ROM, ALARM_SEARCH or READ_ROM. 8 or 9 bytes of data is returned. READ_ROM will get the ROM code of the *ONLY* sensor on this wire, if there a multiple sensors they all will respond causing a data  collision on the wire. Using the SEARCH_ROM or ALARM_SEARCH argument has to be done in a loop until no sensor responds. READ_SCRATCH retrieves the scratchpad for further processing with the `temperature` or `scratch_data` methods

`temperature` - has a single argument the scratchpad, which it processes bytes 0 and 1 to create a decimal number

`write_scratch` - write arguments register tH, register tL and the number of bits resolution to the scratchpad adjusting the running of the device.

`scratch_data` - has a single argument the scratchpad and returns a list of the scratchpad data, register tH, register Tl and bits of resolution

`match_rom` - has a single argument the ROM code, this method signals to a ds18b20 that the next read, write or command is for it.

These methods have no arguments.

`on_parasitic_power` - has return True if the sensor is running on parasitic power

`skip_rom` - alerts all roms that the next instruction is for them to processs such as converting the temperature on all sensors simultaneously or can be used when ther is only one sensor on the wire to avoid having to match the rom before each operation.

`convert` - instruct the sensor to convert raw data into a temperature and write to scratchpad, this takes some time between 90ms and 750ms the sensor signals when ready, one can wait with the `convert_wait` method, sleep or just get on with processing knowing plenty of time will have elapsed before a `read(READ_SCRATCH)` method is called

`convert_wait` - use this method imediately after the `convert` method to pause processing until the ds18b20 is ready for the next operation

`reset` - use this method on a new powered up sensor to initialise or to correct alarm coditions or other running issues

`copy_to_eprom` - copies the tH and Tl registers and the control byte which stores the number of bits of precission to calculate temperatures to.

`cache_from_eprom` - restores the registers tH and tL an the contol byte to scratchpad

An example of single operation is as follows:

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