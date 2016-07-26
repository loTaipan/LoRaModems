import binascii
import pyb

uart_lora = pyb.UART(3, 57600)

debug = True

'''TODO:
'''

def send_command(cmd):
    if debug:
        print(cmd)
    uart_lora.write(cmd + '\r\n')
    uart_read(uart_lora)

''' Sets the credentials for ABP'''
def set_network_settings_ABP(devaddr, nwkskey,appskey):
	send_command('mac set devaddr ' + devaddr)
    send_command('mac set nwkskey ' + nwkskey)
    send_command('mac set appskey' + appskey)
    send_command('mac save')

''' Sets the credentials for OTAA'''	
def set_network_settings_OTAA(deveui, appeui):
	send_command('mac set deveui ' + deveui)
    send_command('mac set appeui ' + appeui)
    send_command('mac save')	

''' indx 1 = 14dBm'''
def set_output_power(indx='1'):
    send_command('mac set pwridx' + indx)
    send_command('mac save')

		
def connect(datarate='0', mode ='abp', adr = 'off'):
    send_command('mac join ' + mode)
    send_command('mac set dr ' + datarate)
    send_command('mac set adr ' + adr)

def send_message(message, confirmation='uncnf', port='1'):
    msg = binascii.hexlify(message).decode('utf-8')
    send_command('mac tx ' + confirmation + ' ' + port + ' ' + msg)

def process_downlink(message):
	pass
	
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
			if 'mac rx' in msg:
				if debug:
					print(msg)
				break
				process_downlink(msg)
        attempts -= 1
    if attempts < 0 and ok_raise:
        raise Exception('no OK received!')
    return msg
