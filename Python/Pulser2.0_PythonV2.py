import csv
import serial
from datetime import datetime
import time
import os
import xlsxwriter
import sys
import pandas as pd
from easygui import choicebox, ccbox

from files.functions import channel, mensaje, check, grounds, serial_ports, portIsUsable, escexcell


adc_voltage_ref = 1.1
#############################################################################
##########################-OPTIONS-##########################################
#Debug
debug = False

#Thresholds
threshDCs = 220
threshDCi = 190

threshACs = 100
threshACi = 30

#Serial Communication
portName = ''
bps = 57600

#Print info to CSV
print_CSV = False

## Load PAD information and mapping
padStrip_choices = ["P1 Strip", "P2 Strip", "Pad"]
selected_board = choicebox('Please select one of the following board options', 'Board Selector', padStrip_choices)

if selected_board == padStrip_choices[0]:
    not_in_map_str = 'NONE'
    df = pd.read_csv("files/P1_sTGC_AB_Mapping_strip.csv")
    df.drop('GFZ Connector', axis=1, inplace=True)
    df.set_index('GFZ_NAME', drop=True, inplace=True)
    df.fillna(not_in_map_str, inplace=True)
    if debug:
        print(df.head())

    save_prefix = 'P1_Strip_'

elif selected_board == padStrip_choices[1]:
    not_in_map_str = 'NONE'
    df = pd.read_csv("files/P2_sTGC_AB_Mapping_strip.csv")
    df.drop('GFZ Connector', axis=1, inplace=True)
    df.set_index('GFZ_NAME', drop=True, inplace=True)
    df.fillna(not_in_map_str, inplace=True)
    if debug:
        print(df.head())
    save_prefix = 'P2_Strip_'

elif selected_board == padStrip_choices[2]:
    not_in_map_str = 'NONE'
    df = pd.read_csv("files/sTGC_AB_Mapping_Pad.csv")
    df.set_index('GFZ_NAME', drop=True, inplace=True)
    df.fillna(not_in_map_str, inplace=True)
    if debug:
        print(df.head())
    save_prefix = 'Pad_'

selected_map = choicebox('Please select the mapping', 'Map Selector', df.columns)
print('The selected Mapping is', selected_map)
save_prefix += selected_map + '_'

msg = 'The selected options are: ' + selected_board + ', ' + selected_map + '.\n Do you want to continue?'
title = 'Please Confirm'
if ccbox(msg, title):     # show a Continue/Cancel dialog
    pass  # user chose Continue
else:  # user chose Cancel
    sys.exit(0)



if len(portName) < 3:
    ports = serial_ports()
    portName = choicebox('COM port not selected, please select the right port.', 'COM port Selector', ports)
    if debug:
        print(ports)

## Load connector information and mapping
with open('files/Maping.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    numero = -1
    channels = []
    for row in csv_reader:
        if debug:
            print(row)
        channels.append(channel(row))




for channel in channels:
    name = df.loc[channel.gfz, selected_map]
    if name == not_in_map_str:
        channel.pad_map = name
    else:
        channel.pad_map = str(int(name))

    if debug:
        print(channel.gfz, '-->', channel.pad_map)




## Commands [Start,ID,Letter,Port,Number,Comand,Stop]
##Send
## [#,S,0,0,0,$] Start
## [#,W,2,0,1,$] Write Mult A Port 0 and Pin 1 a signal of 5V, read current and send it back
## [#,E,0,0,0,$] Read errors and send them back
## [#,P,I,0,0,$] Turn PWM ON
## [#,P,O,0,0,$] Turn PWM OFF

##Recive
## Turn on PWM
## [#,P,I,0,0,$] Turn PWM ON
if portIsUsable(portName):
    print_CSV = True
    arduino = serial.Serial(portName, bps)
    print('Arduino on port:', arduino.name)

    if debug:
        print('DEBUG MODE ON')

    arduino.timeout = 5
    time.sleep(5)

    ##Start comunication
    arduino.write('#'.encode('utf-8'))
    cond = True
    while cond:
        msj = arduino.readline()
        if len(msj) > 0:
            if mensaje(msj) == 1:
                cond = False
            print(msj.decode('utf-8'))


    ## Start AC Test
    print('AC test')
    arduino.write(('#P'+'I'+'$').encode('utf-8')) ## Turn on PWM
    print((arduino.readline()).decode('utf-8'))
    time.sleep(1)


    for test in range(0,10):
        msj = '#W640$'
        arduino.write(msj.encode('utf-8'))
        msj = arduino.readline()
        msj = msj.decode('utf-8')
        if debug:
            print(str(test) + ". AC test value", int(msj.split(',')[4]))

    for channel in channels:
        if channel.mult >= 0:
            msj = '#W' + str(channel.mult) + str(channel.port) + str(channel.pin) + '$'
            arduino.write(msj.encode('utf-8'))
            msj = arduino.readline()
            msj = msj.decode('utf-8')
            channel.responseAC = msj
            channel.ADC_AC = int(msj.split(',')[4])
            check(channel.info2, msj)
            if debug:
                print(channel.info+': ' + str(channel.ADC_AC))
            elif channel.pad_map != not_in_map_str:
                print(channel.pad_map+': ' + str(channel.ADC_AC))


    # Start DC Test
    print('DC test')
    arduino.write(('#P'+'O'+'$').encode('utf-8'))   # Turn off PWM
    print((arduino.readline()).decode('utf-8'))
    time.sleep(1)

    for channel in channels:
        if channel.mult >= 0:
            msj = '#W' + str(channel.mult) + str(channel.port) + str(channel.pin)+'$'
            arduino.write(msj.encode('utf-8'))
            msj = arduino.readline()
            msj = msj.decode('utf-8')
            channel.responseDC = msj
            channel.ADC_DC = int(msj.split(',')[4])
            check(channel.info2, msj)
            if debug:
                print(channel.info+': '+str(channel.ADC_DC))
            elif channel.pad_map != not_in_map_str:
                print(channel.pad_map + ': ' + str(channel.ADC_DC))




    for channel in channels:
        if channel.mult >= 0:
            if channel.ADC_AC > threshACs:
                channel.messages.append('Error in AC current (to High)')
            elif channel.ADC_AC > threshACi:
                channel.connection = True
            else:
                channel.messages.append('Error in AC current (to Low)')


            if channel.ADC_DC > threshDCs:
                channel.cc = True
                msj = '#E' + str(channel.mult) + str(channel.port) + str(channel.pin) + '$'
                arduino.write(msj.encode('utf-8'))

                cond = True
                while cond:
                    msj = arduino.readline()
                    msj = msj.decode('utf-8')
                    msj = msj.split(',')
                    if msj[0] == 'R':
                        cond = False
                    else:
                        channel.errors.append([msj[1], msj[2], msj[3]])

                    if debug:
                        print(msj)

                channel.messages.append('Error in DC current (to High)')

            elif channel.ADC_DC < threshDCi:
                channel.messages.append('Error in DC current (to Low)')
    arduino.close()

else:
    print("Couldn't open COM port, aborting...")

if print_CSV:
    grounds(channels)

    # Excel setup
    fecha = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    directory = os.getcwd()
    print("Date and Time =", fecha)

    nombre = directory + '\Results' + '\\' + save_prefix + fecha + '.xlsx'
    workbook = xlsxwriter.Workbook(nombre)

    bueno = workbook.add_format()
    bueno.set_bg_color('green')
    bueno.set_align('center')
    bueno.set_border(1)

    malo = workbook.add_format()
    malo.set_bg_color('red')
    malo.set_align('center')
    malo.set_border(1)

    white = workbook.add_format()
    white.set_bg_color('white')
    white.set_border(1)
    white.set_align('center')




    prueba = workbook.add_worksheet('Test')
    prueba.write(0, 0, fecha)
    prueba.write(0, 3, 'PAD NAME:')
    prueba.write(0, 4, selected_map)
    prueba.set_column(3, 4, 10)
    escexcell(['Mult', 'Port', 'Pin', 'ADC DC', 'Voltage DC', 'Current DC mA', 'ADC AC', 'Voltage AC', 'Current AC mA', 'Name', 'PAD_Number', 'Messages'], 2, prueba, 0, white)
    prueba.write(0, 0, fecha)

    errores = workbook.add_worksheet('Errors')
    errores.write(0, 0, 'PAD NAME:')
    errores.write(0, 1, selected_map)
    errores.write(1, 0, 'PIN NAME:')
    errores.write(1, 1, 'GFZ NAME:')
    escexcell(['Mult', 'Port', 'Pin'], 1, errores, 2, white)
    escexcell(['Mult', 'Port', 'Pin'], 1, errores, 6, white)


    conectorDC = workbook.add_worksheet('ConnectorDC')
    conectorDC.set_column(0, 0, 20)
    conectorDC.write(0, 0, 'Upper DC Threshold:', white)
    conectorDC.write(0, 1, threshDCs, white)
    conectorDC.write(1, 0, 'Lower DC Threshold:', white)
    conectorDC.write(1, 1, threshDCi, white)
    conectorDC.write(2, 0, 'PAD NAME:', white)
    conectorDC.write(2, 1, selected_map, white)
    conectorDC.set_column(3, 12, 12)


    conectorAC = workbook.add_worksheet('ConnectorAC')
    conectorAC.set_column(0, 0, 20)
    conectorAC.write(0, 0, 'Upper AC Threshold:', white)
    conectorAC.write(0, 1, threshACs,white)
    conectorAC.write(1, 0, 'Lower AC Threshold:', white)
    conectorAC.write(1, 1, threshACi, white)
    conectorAC.write(2, 0, 'PAD NAME:', white)
    conectorAC.write(2, 1, selected_map, white)
    conectorAC.set_column(3, 12, 12)


    for channel in channels:
        if channel.connection:
            if channel.pad_map == not_in_map_str:
                channel.AC_color_code = white
            else:
                channel.AC_color_code = bueno
        else:
            channel.AC_color_code = malo

        if channel.cc:
            channel.DC_color_code = malo
            channel.color_code = malo
        else:
            if channel.pad_map == not_in_map_str:
                channel.DC_color_code = white
                channel.color_code = white
            else:
                channel.DC_color_code = bueno
                channel.color_code = bueno


    counter1 = 1
    counter2 = 1
    for channel in channels:
        if True:
            channel.update_VI()
            channel.update()


            # AC window
            conectorAC.write(channel.x + 2, channel.y + 2, channel.pad_map+': '+str(channel.ADC_AC), channel.AC_color_code)

            # Test window
            escexcell(channel.summary, counter1 + 2, prueba, 0, channel.color_code)

            # DC window
            conectorDC.write(channel.x + 2, channel.y + 2, channel.pad_map + ': ' + str(channel.ADC_DC), channel.DC_color_code)
            if channel.cc:
                #Error window
                errores.write(counter2 + 2, 0, channel.pad_map, channel.DC_color_code)
                errores.write(counter2 + 2, 1, channel.gfz, channel.DC_color_code)
                offset = 2
                for error in channel.errors:
                    escexcell(error, counter2 + 2, errores, offset, channel.color_code)
                    offset += 4
                counter2 += 1


            counter1 += 1




    workbook.close()

