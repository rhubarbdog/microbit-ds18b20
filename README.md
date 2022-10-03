# microbit-ds18b20 - a ds18b20 thermometer class

This is a class for the dallas ds18b20 thermometer it has the following methods.

<table>
<tr><td>
`read` </td><td>has a single the argument, it can be  `READ_SCRATCH`, `SEARCH_ROM`, `ALARM_SEARCH` or `READ_ROM`. on success 8 or 9 bytes of data is returned. If there is no data `None` will be returned for SEARCH commands, but will raise an exception for `READ_SCRATCH` and `READ_ROM`.
Only use `READ_ROM`  if there is *ONLY* one sensor on the wire. If there a multiple sensors when using `READ_ROM` they all will respond causing a data  collision on the wire. With a sucessful read the ROM code of the sensor will be returned.
Using the `SEARCH_ROM` or `ALARM_SEARCH` argument has to be done in a loop until no sensor responds and `None` is returned.
`READ_SCRATCH` retrieves the scratchpad for further processing with the `temperature` or `scratch_data` methods
</td></tr>

<tr><td>
`temperature` </td><td>has a single argument the scratchpad, which it processes bytes 0 and 1 to create a decimal number
</td></tr>

<tr><td>
`write_scratch` </td><td>write arguments register tH, register tL and the number of bits resolution to the scratchpad adjusting the running of the device.
</td></tr>

<tr><td>
`scratch_data` </td><td>has a single argument the scratchpad and returns a list of the scratchpad data, register tH, register Tl and bits of resolution
</td></tr>

<tr><td>
`match_rom` </td><td>has a single argument the ROM code, this method signals to a ds18b20 that the next read, write or command is for it.
</td></tr>
</table>

These methods have no arguments.

<table>
<tr><td>
`on_parasitic_power` </td><td>has return True if the sensor is running on parasitic power
</td></tr>

<tr><td>
`skip_rom` </td><td>alerts all roms that the next instruction is for them to processs such as converting the temperature on all sensors simultaneously or can be used when ther is only one sensor on the wire to avoid having to match the rom before each operation.
</td></tr>

<tr><td>
`convert` </td><td>instruct the sensor to convert raw data into a temperature and write to scratchpad, this takes some time between 90ms and 750ms the sensor signals when ready, one can wait with the `convert_wait` method, sleep or just get on with processing knowing plenty of time will have elapsed before a `read(READ_SCRATCH)` method is called
</td></tr>

<tr><td>
`convert_wait` </td><td>use this method imediately after the `convert` method to pause processing until the ds18b20 is ready for the next operation
</td></tr>

<tr><td>
`reset` </td><td>use this method on a new powered up sensor to initialise or to correct alarm coditions or other running issues
</td></tr>

<tr><td>
`copy_to_eprom` </td><td>copies the tH and tL registers and the control byte which stores the number of bits of precission to calculate temperatures to.
</td></tr>

<tr><td>
`cache_from_eprom` </td><td>restores the registers tH and tL an the contol byte to scratchpad
</td> </tr>

</table>

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