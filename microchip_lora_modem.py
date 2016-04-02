import binascii
import pyb

uart_lora = pyb.UART(3, 57600)

debug = True


def send_command(cmd):
    if debug:
        print(cmd)
    uart_lora.write(cmd + '\r\n')
    uart_read(uart_lora)


''' Sets the network session and the appkey, default thethingsnetwork'''


def set_network_settings(nwkskey='2B7E151628AED2A6ABF7158809CF4F3C',
                         appskey='2B7E151628AED2A6ABF7158809CF4F3C'):
    send_command('mac set nwkskey ' + nwkskey)
    send_command('mac set appskey' + appskey)
    send_command('mac save')


''' Sets the device adress'''
def set_device_adress(addr):
    send_command('mac set devaddr ' + addr)
    send_command('mac save')

''' indx 1 = 14dBm'''
def set_output_power(indx):
    send_command('mac set pwridx' + indx)
    send_command('mac save')

def connect_lora(datarate='2'):
    send_command('mac join abp')
    send_command('mac set dr ' + datarate)
    send_command('mac set adr on')


def send_message(message, confirmation='uncnf', port='1'):
    msg = binascii.hexlify(message).decode('utf-8')
    send_command('mac tx ' + confirmation + ' ' + port + ' ' + msg)


def uart_read(uart, ok_raise=False):
    msg = ''
    attempts = 10
    while attempts >= 0:
        pyb.delay(50)
        if uart.any():
            msg += uart.readall().decode('utf-8')
            if 'ok' or 'RN' in msg:
                if debug:
                    print(msg)
                break
        attempts -= 1
    if attempts < 0 and ok_raise:
        raise Exception('no OK received!')
    return msg
