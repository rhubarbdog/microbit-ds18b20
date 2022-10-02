#
# dht11.py - a microbit implementation of dht11
# author - Phil Hall, copyright (c) November 2018
\#
# License - MIT

from microbit import *
import time

DEGREES = u'\xb0'

class DataError(Exception):
    pass

class DS18B20:
    MATCH_ROM = 0x55
    CONVERT = 0x44
    SKIP_ROM = 0xcc
    #read modes
    READ_SCRATCH = 0xbe
    SEARCH_ROM = 0xf0
    READ_ROM = 0x33
    
    def __init__(self, pin):
        self._pin = pin
        
        id =- 1
        for i in range(17):
            if pin == eval('pin' + str(i)):
                id=i
                break
        # set the bit id for the asm_read and asm_write pin_id
        self._read = 0
        self._write = 0
        if id >= 0:
            tmp = (2, 3, 4, 15 ,19, -1 ,21, 22, 10) +\
                (9, 30, -1, 12, 17, 1, 13, -1)
            self._read= tmp[id]

            tmp = (2, 3, 4, 31, 28, -1, -1, 11, 10, 9) +\
                (30, -1, 12, 17, 1, 13, -1)
            self._write= tmp[id]


        if id == -1 or self._read == -1 or self._write == -1:
            raise ValueError('function not suitable for this pin')

    def string2bytes(self, string):
        tmp = len(string)
        bytes_ = bytearray(tmp)
        for i in range(tmp):
            if string[i] == "1":
                bytes_[i] = 1
            else:
                bytes_[i] = 0

        return bytes_

    
    def match_rom(self, rom_id):
        pin=self._pin
        pin.write_digital(1)
        binstr = ""

        for data in rom_id:
            for b in range(8):
                if data & 0x1:
                    binstr += '1'
                else:
                    binstr += '0'
                data >> 1
                    
        bytes1 = self.string2bytes(self.binary(self.MATCH_ROM, 8))
        bytes2 = self.string2bytes(binstr)
        
        self.write_data(self._write, bytes1, len(bytes1))
        self.write_data(self._write, bytes2, len(bytes2))
        
    def skip_rom(self):
        pin=self._pin
        pin.write_digital(1)
        bytes_ = self.string2bytes(self.binary(self.SKIP_ROM, 8))
        
        self.write_data(self._write, bytes_, len(bytes_))

        # when the pin goes high conver is over
        pin.read_digital()
        pin.set_pull(pin.PULL_UP)
    
    def convert(self):
        # pull wire low for atleast 480us then high
        pin = self._pin
        pin.write_digital(1)
    
        bytes_ = self.string2bytes(self.binary(self.CONVERT, 8))
                
        self.write_data(self._write, bytes_, len(bytes_))

        # when the pin goes high conver is over
        pin.read_digital()
        pin.set_pull(pin.PULL_UP)

    def convert_wait(self):
        pin.read_digital()
        pin.set_pull(pin.PULL_UP)
        elapsed = self.wait_low(self._read)
        print(elapsed)

    def reset(self):
        # pull wire low for atleast 480us then high
        pin = self._pin
        pin.write_digital(1)
        self.do_reset(self._write)

        time.sleep_us(15) # sleep 15 to 60
        
        # time response it should be 60 - 240us
        pin.read_digital()
        pin.set_pull(pin.PULL_UP)
        elapsed = self.wait_low(self._read)


    
    @staticmethod
    @micropython.asm_thumb
    #pin_id, data, bits
    def write_data(r0,r1 ,r2):
        b(START)
        # these are sixteenths of a us in register r0
        label(SLEEP)
        lsl(r0, r0, 20)
        label(snooze)
        mov(r7, 0x1)
        lsl(r7, r7, 6)
        add(r7, 0x0e)
        lsl(r7, r7, 8)
        add(r7, 0xf0)
        label(delay_loop)
        sub(r7, 1)
        bne(delay_loop)
        sub(r0, 1)
        bne(end_sleep)
        b(snooze)
        label(end_sleep)
        bx(lr)

        label(WRITE_R4)
        mov(r5, 0x1)
        lsl(r5, r0)
        push({r0, lr, })
        sub(r4, 0)
        bne(w4_high)
        mov(r0, 10)
        b(w4_next)
        label(w4_high)
        mov(r0, 90)
        
        label(w4_next)
        lsl(r0, r0, 4)
        str(r5, [r3, 12] )    #lo

        bl(SLEEP)

        str(r5, [r3, 8] )    #hi
        sub(r4, 0)
        bne(w4_end)
        mov(r0, 80)
        lsl(r0, r0, 4)
        bl(SLEEP)

        label(w4_end)

        mov(r0, 19)    # sleep 1us end of bit
        bl(SLEEP)

        pop({r0, lr, })
        bx(lr)
        
        label(START)
        cpsid('i')          # disable interrupts to go really fast
        mov(r3, 0x50)       # r1=0x50
        lsl(r3, r3, 16)     # r1=0x500000
        add(r3, 0x05)       # r1=0x500005
        lsl(r3, r3, 8)      # r1=0x50000500 -- this points to GPIO write digita

        
        sub(r2,3)
        label(loop)
        push({r2, })
        ldr(r2, [r1, 0]) # get value
        mov(r5, 0xff)
        and_(r2, r5)
        mov(r4, r2)
        bl(WRITE_R4)
        add(r1, 1)
        pop({r2, })
        sub(r2, 1)
        bne(loop)

        mov(r2, 3)
        label(last)
        push({r2, })
        lsr(r2, r2, 8)
        mov(r5, 0xff)
        and_(r2, r5)
        mov(r4, r9)
        bl(WRITE_R4)
        pop({r2, })
        sub(r2,1)
        bne(last)

        cpsie('i')          # enable interrupts to go really fast

    @staticmethod
    @micropython.asm_thumb
    def do_reset(r0):
        b(START)
        
        # these are sixteenths of a us in register r0
        label(SLEEP)
        mov(r7, 0x1)
        lsl(r7, r7, 6)
        add(r7, 0x0e)
        lsl(r7, r7, 8)
        add(r7, 0xf0)
        label(delay_loop)
        sub(r7, 1)
        bne(delay_loop)
        sub(r0, 1)
        bne(end_sleep)
        b(SLEEP)
        label(end_sleep)
        bx(lr)

        label(START)
        cpsid('i')          # disable interrupts to go really fast

        mov(r2, 0x50)       # r1=0x50
        lsl(r2, r2, 16)     # r1=0x500000
        add(r2, 0x05)       # r1=0x500005
        lsl(r2, r2, 8)      # r1=0x50000500 -- this points to GPIO write digita

        mov(r5, 0x1)
        lsl(r5, r0)

        
        str(r5, [r2, 12] )    #lo

        mov(r0, 0x1)      # set timer to 480 * 16
        lsl(r0, r0, 8)
        add(r0, 224)
        lsl(r0, r0, 4)
        mov(r4, r0)
        
        bl(SLEEP)

        str(r5, [r2, 8] )    #hi

        mov(r0, r4)
        cpsie('i')          # enable interrupts to go really fast

    @staticmethod
    @micropython.asm_thumb
    def wait_low(r0):
        b(START)

        # these are sixteenths of a us in register r0
        label(SLEEP)
        mov(r7, 0x1)
        lsl(r7, r7, 6)
        add(r7, 0x0e)
        lsl(r7, r7, 8)
        add(r7, 0xf0)
        label(delay_loop)
        sub(r7, 1)
        bne(delay_loop)
        sub(r0, 1)
        bne(end_sleep)
        b(SLEEP)
        label(end_sleep)
        bx(lr)

        label(START)
        cpsid('i')          # disable interrupts to go really fast

        mov(r2, 0x50)       # r1=0x50
        lsl(r2, r2, 16)     # r1=0x500000
        add(r2, 0x05)       # r1=0x500005
        lsl(r2, r2, 8)      # r1=0x50000500 -- this points to GPIO write digita
        add(r2, 0x10)       # r3=0x50000510 -- points to read_digital bits
        mov(r1, r0)

        mov(r5, 0x1)
        lsl(r5, r0)
        label(high)#wait while high
        ldr(r4, [r2, 0])   
        mov(r3, 0x01)      # create bit mask in r3  
        lsl(r3, r1)        # select bit from r0
        and_(r4, r3)
        lsr(r4, r1)
        sub(r4,0)
        bne(wait)
        b(low)
        label(wait)
        mov(r0, 0x1)
        bl(SLEEP)
        b(high)

        label(low)    # time the low in register r6
        ldr(r4, [r2, 0])  
        mov(r3, 0x01)      # create bit mask in r3  
        lsl(r3, r1)        # select bit from r0
        and_(r4, r3)
        lsr(r4, r1)
        sub(r4,0)
        bne(END)
        mov(r0, 0x10)
        add(r6,1)
        bl(SLEEP)
        b(low)

        label(END)
        mov(r0, r6)

    def binary(self, value, bits):

        save = bits-1
        binstring = ""
        while bits > 0:
            bits -= 1
        
            if value & (1<<(save-bits)):
                binstring += "1"
            else:
                binstring += '0'

        return binstring

              
    def read(self, command):
        # creating these locals speeds things up len() is very slow
        pin = self._pin
        
        buffer_ = bytearray(1024)
        length = len(buffer_)

        pin.write_digital(1)
        bytes_ = self.string2bytes(self.binary(command, 8))
        self.write_data(self._write, bytes_, len(bytes_))

        pin.read_digital()
        pin.set_pull(pin.PULL_UP)

        if self._grab_bits(self._read, buffer_, length) != length:
            raise Exception("Grab bits failed.")

        for b in buffer_:
            print(b, end = "")
        print('')
        
        data = self._parse_data(buffer_)

        del buffer_
        
        if data is None or len(data) != 40:
            if data is None:
                bits = 0
            else:
                bits = len(data)
            raise DataError("Too many or too few bits " + str(bits))

        data = self._calc_bytes(data)

        if not command == self.READ_SCRATCH:
            save = data[0]
            data[0]=0
        

        checksum = self._calc_checksum(data)
        if not command == self.READ_SCRATCH:
            data[0] = save
            
        if ((command == self.READ_ROM or command == self.SEARCH_ROM) \
            and not data[0] == checksum) or \
            (command == self.READ_SCRATCH and not data[8] == checksum):
            pass
        
        return data 

    # r0 - pin bit id
    # r1 - byte array
    # r2 - len byte array, must be a multiple of 4
    @staticmethod
    @micropython.asm_thumb
    def _grab_bits(r0, r1, r2):
        b(START)

        # DELAY routine
        label(DELAY)
        mov(r7, 0xa7)
        label(delay_loop)
        sub(r7, 1)
        bne(delay_loop)
        bx(lr)

        label(READ_PIN)
        mov(r3, 0x50)      # r3=0x50
        lsl(r3, r3, 16)    # r3=0x500000
        add(r3, 0x05)      # r3=0x500005
        lsl(r3, r3, 8)     # r3=0x50000500 -- this points to GPIO registers
        add(r3, 0x10)      # r3=0x50000510 -- points to read_digital bits
        ldr(r4, [r3, 0])   # move memory@r3 to r2
        mov(r3, 0x01)      # create bit mask in r3  
        lsl(r3, r0)        # select bit from r0
        and_(r4, r3)
        lsr(r4, r0)
        bx(lr)

        
        label(START)
        cpsid('i')         # disable interupst
        mov(r5, 0x00)      # r5 - byte array index 
        label(again)
        mov(r6, 0x00)      # r6 - current word
        bl(READ_PIN)
        orr(r6,  r4)       # bitwise or the pin into current word
        bl(DELAY)
        bl(READ_PIN)
        lsl(r4, r4, 8)     # move it left 1 byte
        orr(r6,  r4)       # bitwise or the pin into current word
        bl(DELAY)
        bl(READ_PIN)
        lsl(r4, r4, 16)     # move it left 2 bytes
        orr(r6,  r4)       # bitwise or the pin into current word
        bl(DELAY)
        bl(READ_PIN)
        lsl(r4, r4, 24)     # move it left 3 bytes
        orr(r6,  r4)       # bitwise or the pin into current word
        bl(DELAY)
    
        add(r1, r1, r5)   # add the index to the bytearra addres
        str(r6, [r1, 0])  # now 4 have been read store it
        sub(r1, r1, r5)   # reset the address
        add(r5, r5, 4)    # increase array index
        sub(r4, r2, r5)   # r4 - is now beig used to count bytes written
        bne(again)
    
        label(RETURN)
        mov(r0, r5)       # return number of bytes written
        cpsie('i')         # enable interupst

    def _parse_data(self, buffer_):

        max_bits = 128
        bits = bytearray(max_bits)
        length = 0
        bit_ = 0
        
        for current in buffer_:

            if current == 0:
                length += 1
            elif bit_ == 0 and length == 0:
                pass
            elif bit_ >= max_bits:
                pass  
            elif length > 0:
                bits[bit_] = length
                length = 0
                bit_ += 1
                
        if bit_ == 0:
            return None
        
        results = bytearray(bit_)
        for i in range(bit_):
            results[i] = bits[i]
        return results

    def _calc_bytes(self, lengths):

        shortest = 1 << 30
        longest = 0

        for i in range(0, len(lengths)):
            len_ = lengths[i]
            if len_ < shortest:
                shortest = len_
            if len_ > longest:
                longest = len_

        halfway = shortest + (longest - shortest) / 2
        data = bytearray(len(lengths)//8)
        did = 0
        byte = 0

        for i in range(len(data)):
            byte = byte << 1
            if pull_up_lengths[i] < halfway:
                byte = byte | 1

            if ((i + 1) % 8 == 0):
                data[did] = byte
                did += 1
                byte = 0
                
        return data

    def _calc_checksum(self, data):
        return data[0] + data[1] + data[2] + data[3] & 0xff


if __name__ == '__main__':

    sensor = DS18B20(pin0)
    sensor.reset()
    sensor.skip_rom()
    sensor.convert()
    sleep(1000)
    data = sensor.read(sensor.READ_SCRATCH)
    print(data)
    
