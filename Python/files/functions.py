import serial
import sys
import glob

class channel():
    # Channel object, contains all the mappings and stores test results results
    def __init__(self, info, ADC_ref=1.1, reversed_x=True):
        self.multiplexer = info[0]
        if info[0]=='A':
            self.mult = 0
        elif info[0]=='B':
            self.mult = 1
        elif info[0]=='C':
            self.mult = 2
        elif info[0]=='D':
            self.mult = 3
        elif info[0]=='E':
            self.mult = 4
        elif info[0]=='F':
            self.mult = 5
        elif info[0] == 'G':
            self.mult = 6
        else:
            self.mult = -1


        self.port = info[1]
        self.pin = info[2]

        self.gfz = info[3]

        self.x = int(info[4])
        if reversed_x:
            self.y = int(info[5])
        else:
            self.y = 10-int(info[5])

        self.name = info[6]


        self.ADC_REF = ADC_ref
        self.ADC_DC = 0
        self.ADC_AC = 0
        self.currentDC = 0
        self.currentAC = 0
        self.voltageDC = 0
        self.voltageAC = 0
        self.short_resistance = 0

        self.responseDC = ""
        self.responseAC = ""

        self.info = str(self.multiplexer) + ', ' + self.port + ', ' + self.pin
        self.info2 = str(self.mult) + ',' + self.port + ',' + self.pin

        self.connection = False
        self.cc = False
        self.errors = []
        self.summary = []
        self.messages = []
        self.pad_map = 'NA'


    def update(self):
        format_str = '{0:.3g}'
        self.summary = [self.multiplexer, self.port, self.pin, self.ADC_DC, format_str.format(self.voltageDC), format_str.format(self.currentDC), self.ADC_AC, format_str.format(self.voltageAC), self.gfz, self.name, self.pad_map]
        for i in self.messages:
            self.summary.append(i)


    def calculate_short_res(self, V):
        self.short_resistance = calculate_equivalent_resistance(self.ADC_DC, V)


    def mult_list(self):
        return [self.multiplexer, str(self.port), str(self.pin)]


    def update_VI(self):
        self.voltageDC = self.ADC_DC * self.ADC_REF / 1024
        self.voltageAC = self.ADC_AC * self.ADC_REF / 1024



def mensaje(msj,deb=False):
    msj = msj.decode("utf-8")
    primer = msj[0]
    if primer == '#':
        splited = msj.split(',')
        mensaje = splited[1:splited.index('$')]
        if deb:
            print(mensaje)
        primer = mensaje[0]

        if primer=='I':
            return 1
        elif primer=='E':
            return 2
        elif primer=='L':
            return 3
        elif primer=='R':
            return 4
        elif primer=='C':
            return 5
        elif primer=='Q':
            return 6
        elif primer=='$':
            return -1
        else:
            return 0
    else:
        ##if(debug):
            ##print('Error decodificando')
        return 0

def check(msj1,msj2,debug=False):
    msj1 = msj1.split(',')
    msj2 = msj2.split(',')
    if msj1==msj2[1:4]:
        if debug:
            print(msj2)
    else:
        print('Communication error')

def grounds(list):
    new = channel(['G', '2', '0', 'G0', '4', '6', 'GND'])
    for ch in list:
        if ch.gfz == 'G0':
            ch.pad_map = 'GND'
            new = ch

        elif 'G' in ch.gfz:
            ch.port = new.port
            ch.pin = new.pin
            ch.multiplexer = new.multiplexer
            #ch.mult = new.mult

            ch.currentDC = new.currentDC
            ch.currentAC = new.currentAC

            ch.responseDC = new.responseDC
            ch.responseAC = new.responseAC

            ch.info = new.info
            ch.info2 = new.info2

            ch.connection = new.connection
            ch.cc = new.cc
            #ch.errors = new.errors
            ch.summary = new.summary
            ch.messages = new.messages

            ch.pad_map = 'GND'

            ch.update()

def encodeMessage(message):
    string = ''
    for item in message:
        string = string + str(item)

    return string.encode('utf-8')

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def portIsUsable(portName):
    try:
        return serial.Serial(portName)
    except:
        return False

def escexcell(info,fila,hoja,offset,color):
    for i in range(len(info)):
        hoja.write(fila,i+offset, info[i],color)

def calculate_RS_drop(Req, V=4.9, Rs=470, ADC_ref=1.1):
    # Calculates the expected ADC code [0,1023] based on an equivalent resistance
    I = V/Req
    V_ADC = Rs*I
    ADC_code = 1024*V_ADC/ADC_ref
    return int(ADC_code)

def calculate_ADC_code(Rc, V, Rp=9530, Rs=470, ADC_ref=1.1):
    #Calculates the expected ADC code [0,1023] based on an short circuit resistance
    Req = ((Rc+Rp)*Rp+Rs*(Rc+2*Rp))/(Rc+2*Rp)
    I = V/Req
    V_ADC = Rs*I
    ADC_code = 1024*V_ADC/ADC_ref
    return int(ADC_code)


def calculate_PCA_Voltage(ADC_code, Rp=9530, Rs=470, ADC_ref=1.1):
    #Calculates the expected Voltage at the output of a PCA9698 based on an adc reading
    Req = Rp + Rs
    V_ADC = (ADC_code * ADC_ref)/1024
    I = V_ADC / Rs
    V = Req * I
    return V


def calculate_equivalent_resistance(ADC_code, V, Rp=9530, Rs=470, ADC_ref=1.1):
    V_ADC = (ADC_code * ADC_ref)/1024
    I = V_ADC / Rs
    Req =  V / I

    if Req < (Rp+Rs):
        Rc = (2*Req*Rp - Rp*Rp - 2*Rs*Rp) / (Rp + Rs - Req)
    else:
        Rc = 2731515

    return int(Rc)

def correlated_pins(chns, errors):
    err_lst = []
    for ch in chns:
        for err in errors:
            if ch.mult_list() == err:
                err_lst.append([ch.pad_map, ch.name])
                pass
    return err_lst



if __name__ == "__main__":
    import pandas as pd
    results_df = pd.DataFrame(columns=['1', '2'])
    for i in range(20):
        results_df.loc[str(i), '1'] = i

        pass

    print(results_df)