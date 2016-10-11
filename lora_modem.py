import binascii
import pyb

debug = True

model = None
uart_lora = None

def init(m='RN2483'):
    global model
    global uart_lora
    model = m
    
    # tmp
    uart_lora = pyb.UART(1, 57600)
    
    # tmp
    pin_pwr_gnd = pyb.Pin('X12', pyb.Pin.OUT_PP)
    pin_pwr_vcc = pyb.Pin('X11', pyb.Pin.OUT_PP)
    pin_pwr_gnd.low()
    pin_pwr_vcc.high()
    
    if reset() is False:
        return False
    
    log('lora modem initialized (' + model + ')')
    return True

def reset():
    version = send('sys reset')
    if version is '':
        log_error('invalid version')
        return False
    else:
        log('version: ' + version)
        return True

''' Sets the credentials for ABP'''
def set_network_settings_ABP(devaddr, nwkskey,appskey):
    send_command('mac set devaddr ' + devaddr)
    send_command('mac set nwkskey ' + nwkskey)
    send_command('mac set appskey ' + appskey)
    
''' Sets the credentials for OTAA'''
def set_network_settings_OTAA(appEUI, appKey):
    devEUI = send('sys get hweui')
    send_command('mac set appeui ' + appEUI)
    send_command('mac set deveui ' + devEUI)
    send_command('mac set appkey ' + appKey)
    if send_command('mac join otaa') == '':
        log_error('send join command failed')
        return

def connect_ABP():
    if 'ok' not in send_command('mac join abp'):
        log_error('join command failed')
        return False
    return True

def connect_OTTA():
    if 'ok' not in send_command('mac join otaa'):
        log_error('join command failed')
        return False
    return True


''' decimal number representing the data rate, from 0 and 7. '''
def set_data_rate(rate):
    if rate < 0 or rate > 7:
        log_error( 'invalid data rate' )
        return False
    return 'ok' in send_command('mac set dr ' + str(rate))

''' adaptive data rate '''
def enable_adaptive_data_rate(en):
    return 'ok' in send_command('mac set adr ' + ('on' if en else 'off'))

''' indx 1 = 14dBm'''
def set_output_power(idx):
    return 'ok' in send_command('mac set pwridx' + idx)


''' This command will save configuration parameters to the user EEPROM.'''
def saveEEPROM():
    send_command('mac save')



def send(cmd):
    uart_lora.write(cmd + '\r\n')
    return uart_read()

def send_command(cmd):
    if debug:
        log('> send command: ' + cmd)
    ret = send(cmd)
    log('< ' + ret)
    return ret

def send_message(msg, confirmation='uncnf', port='1'):
    if debug:
        log('> send message: ' + msg)
    msg = binascii.hexlify(msg).decode('utf-8')
    ret = send('mac tx ' + confirmation + ' ' + port + ' ' + msg)
    log('< ' + ret)
    return ret

def send_message_raw(msg, confirmation='uncnf', port='1'):
    if debug:
        log('> send message (raw): ' + msg)
    ret = send('mac tx ' + confirmation + ' ' + port + ' ' + msg)
    log('< ' + ret)
    return ret

def sleep(time):
    send_command('sys sleep ' + str(time))


def show_status():
    log('lora modem status:')
    log_nnl('EUI: ' + send('sys get hweui'))
    log_nnl('Battery: ' + send('sys get vdd'))
    log_nnl('AppEUI: ' + send('mac get appeui'))
    log_nnl('DevEUI: ' + send('mac get deveui'))
    log_nnl('DevAddr: ' + send('mac get devaddr'))
    if model == 'RN2483':
        log_nnl('Band: ' + send('mac get band'))
    log_nnl('Data Rate: ' + send('mac get dr'))
    log_nnl('RX Delay 1: ' + send('mac get rxdelay1'))
    log_nnl('RX Delay 2: ' + send('mac get rxdelay2'))

def log(msg):
    print(msg)
def log_nnl(msg):
    print(msg,end="",flush=True)
def log_error(msg):
    print('lora modem error: ' + msg)

def uart_read():
    msg = ''
    attempts = 20
    while attempts >= 0:
        pyb.delay(50)
        if uart_lora.any():
            msg += uart_lora.readall().decode('utf-8')
        attempts -= 1
    return msg
