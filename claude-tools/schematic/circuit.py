"""Circuit definition for Frugal-IoT V0.2 (source of truth for parts and nets).
Each part: dict(prefix, lib, value, fp, nets{pin:net}, dnp, lcsc, mpn, block, note, ref)
net 'NC' => no-connect marker. Decisions referenced as Dn are in ../../DECISIONS.md.
"""
P = []
def part(prefix, lib, value, fp, nets, block, dnp=False, lcsc='', mpn='', rot=None, note='', ref=None):
    P.append(dict(prefix=prefix, lib=lib, value=value, fp=fp, nets=nets, block=block,
                  dnp=dnp, lcsc=lcsc, mpn=mpn, rot=rot, note=note, ref=ref))

R06 = 'Resistor_SMD:R_0603_1608Metric'; C06 = 'Capacitor_SMD:C_0603_1608Metric'
LED06 = 'LED_SMD:LED_0603_1608Metric'; LED08 = 'LED_SMD:LED_0805_2012Metric'
SMA = 'Diode_SMD:D_SMA'; SOT23 = 'Package_TO_SOT_SMD:SOT-23'
TB254 = 'TerminalBlock:TerminalBlock_Xinya_XY308-2.54-{n}P_1x0{n}_P2.54mm_Horizontal'
HDR = 'Connector_PinHeader_2.54mm:PinHeader_1x0{n}_P2.54mm_Vertical'
BTN = 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A'
SJ = 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'
SJ3 = 'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm'
XY = {2: ('C557685', 'XY308-2.54-2P'), 3: ('C557686', 'XY308-2.54-3P'), 5: ('C915914', 'XY308-2.54-5P')}

RES = {'10k': 'C25804', '100k': 'C25803', '1k': 'C21190', '4.7k': 'C23162', '5.1k': 'C23186',
       '1M': 'C22935', '120R': 'C22787', '680R': 'C23228'}
CAP = {'100nF': 'C14663', '1uF': 'C15849', '10uF': 'C19702'}

def R(v, a, b, blk, dnp=False, note=''):
    part('R', 'Device:R', v, R06, {'1': a, '2': b}, blk, dnp, RES.get(v, ''), note=note)
def C(v, a, b, blk, dnp=False, note=''):
    part('C', 'Device:C', v, C06, {'1': a, '2': b}, blk, dnp, CAP.get(v, ''), note=note)
def LED(col, anode, cathode, blk):  # JLCPCB Basic: red KT-0603R, green KT-0805G
    part('D', 'Device:LED', col, {'RED': LED06, 'GREEN': LED08}[col], {'2': anode, '1': cathode}, blk, rot=180,
         lcsc={'RED': 'C2286', 'GREEN': 'C2297'}[col], mpn={'RED': 'KT-0603R', 'GREEN': 'KT-0805G'}[col])
def PFET(g, s, d, blk):
    part('Q', 'Transistor_FET:AO3401A', 'AO3401A', SOT23, {'1': g, '2': s, '3': d}, blk, lcsc='C15127')
def BUTTON(a, b, blk, val):
    part('SW', 'Switch:SW_Push', val, BTN, {'1': a, '2': b}, blk, lcsc='C318884', mpn='TS-1187A-B-A-B')
def TERM(ref, n, nets, blk, val, dnp=False):
    lc, mpn = XY[n]
    part('J', f'Connector:Screw_Terminal_01x0{n}', val, TB254.format(n=n),
         {str(i + 1): net for i, net in enumerate(nets)}, blk, dnp, lc, mpn, ref=ref)

# ---------------- USB-C (power + native USB) ----------------
B = 'usb'
part('J', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
     {'A1': 'GND', 'B1': 'GND', 'A12': 'GND', 'B12': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
      'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_D_P', 'B6': 'USB_D_P', 'A7': 'USB_D_N', 'B7': 'USB_D_N',
      'A8': 'NC', 'B8': 'NC', 'SH': 'GND'}, B, lcsc='C165948', mpn='TYPE-C-31-M-12', ref='J1')
R('5.1k', 'CC1', 'GND', B); R('5.1k', 'CC2', 'GND', B)
TERM('J6', 2, ['VBUS', 'GND'], B, '5V IN (aux)')   # D10: external 5 V beside USB; fitted from D34

# ---------------- Charger + cell protection ----------------
B = 'chg'
part('U', 'Battery_Management:TP4056-42-ESOP8', 'TP4056', 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm',
     {'1': 'GND', '2': 'CHG_PROG', '3': 'GND', '4': 'VBUS', '5': 'VBAT', '6': 'nSTDBY', '7': 'nCHRG',
      '8': 'VBUS', '9': 'GND'}, B, lcsc='C16581', note='TEMP grounded: no cell NTC')
C('10uF', 'VBUS', 'GND', B); C('10uF', 'VBAT', 'GND', B)
R('4.7k', 'CHG_PROG', 'GND', B, note='~250 mA')
R('4.7k', 'CHG_PROG', 'CHG_PROG2', B, note='with JP1: ~500 mA')
part('JP', 'Jumper:SolderJumper_2_Open', '500mA', SJ, {'1': 'CHG_PROG2', '2': 'GND'}, B)
R('1k', 'VBUS', 'LED_CHRG', B); LED('RED', 'LED_CHRG', 'nCHRG', B)
R('1k', 'VBUS', 'LED_STDBY', B); LED('GREEN', 'LED_STDBY', 'nSTDBY', B)
part('J', 'Connector:Conn_01x02_Pin', 'CELL', 'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal',
     {'1': 'CELL_NEG', '2': 'VBAT'}, B, lcsc='C173752', mpn='S2B-PH-K-S', ref='J4')
part('U', 'frugal:XB5353A', 'XB5353A', 'Package_TO_SOT_SMD:SOT-23-5',
     {'1': 'NC', '2': 'CELL_NEG', '3': 'VBAT', '4': 'GND', '5': 'GND'}, B, lcsc='C80628', mpn='XB5353A')
C('100nF', 'VBAT', 'CELL_NEG', B)

# ---------------- System power ----------------
B = 'pwr'
part('D', 'Device:D_Schottky', 'SS34', SMA, {'2': 'VBUS', '1': 'VSYS'}, B, lcsc='C8678', mpn='SS34', rot=180)
PFET('VBUS', 'VSYS', 'VBAT', B)                  # load sharing: cell feeds VSYS when USB is absent
R('100k', 'VBUS', 'GND', B)
C('10uF', 'VSYS', 'GND', B)
part('U', 'Regulator_Linear:ME6211C33M5', 'ME6211C33M5G', 'Package_TO_SOT_SMD:SOT-23-5',
     {'1': 'VSYS', '3': 'VSYS', '2': 'GND', '4': 'NC', '5': '+3V3'}, B, lcsc='C82942', mpn='ME6211C33M5G-N')
C('10uF', '+3V3', 'GND', B)
R('1M', 'VBAT', 'VBAT_SENSE', B); R('1M', 'VBAT_SENSE', 'GND', B); C('100nF', 'VBAT_SENSE', 'GND', B)
PFET('nRAIL_EN', '+3V3', '+3V3_SW', B)           # GPIO5 low = sensors on; pull-up keeps it off at reset
R('100k', '+3V3', 'nRAIL_EN', B, note='rail off at reset')
C('1uF', '+3V3_SW', 'GND', B)

# ---------------- MCU ----------------
B = 'mcu'
part('U', 'RF_Module:ESP32-C3-WROOM-02U', 'ESP32-C3-WROOM-02U-N4', 'RF_Module:ESP32-C3-WROOM-02U',
     {'1': '+3V3', '2': 'EN', '3': 'GPIO4', '4': 'nRAIL_EN', '5': 'I2C_SDA', '6': 'I2C_SCL', '7': 'STATUS_LED',
      '8': 'BOOT', '9': 'GND', '10': 'GPIO10', '11': 'RXD0', '12': 'TXD0', '13': 'USB_D_N', '14': 'USB_D_P',
      '15': 'VBAT_SENSE', '16': 'GPIO2', '17': 'SENS2', '18': 'SENS1', '19': 'GND'},
     B, lcsc='C2926676', mpn='ESP32-C3-WROOM-02U-N4')
C('10uF', '+3V3', 'GND', B); C('100nF', '+3V3', 'GND', B)
R('10k', '+3V3', 'EN', B); C('1uF', 'EN', 'GND', B); BUTTON('EN', 'GND', B, 'RESET')
R('10k', '+3V3', 'BOOT', B); BUTTON('BOOT', 'GND', B, 'BOOT')
R('10k', '+3V3', 'GPIO2', B, note='GPIO2 strap high')
R('10k', '+3V3', 'STATUS_LED', B, note='GPIO8 strap high')
R('1k', '+3V3', 'LED_STAT', B); LED('GREEN', 'LED_STAT', 'STATUS_LED', B)
part('J', 'Connector:Conn_01x02_Pin', 'EXT LED', HDR.format(n=2), {'1': 'LED_STAT', '2': 'STATUS_LED'}, B,
     dnp=True, ref='J7', note='off-board LED: 1 = anode, 2 = cathode')

# ---------------- Sensor connectors ----------------
B = 'conn'
R('4.7k', '+3V3_SW', 'I2C_SDA', B); R('4.7k', '+3V3_SW', 'I2C_SCL', B)
# Fitted (D31): R18 = SENS1 pull-up (e.g. DS18B20), C12 = SENS2 filter (analog). R19, C11 stay options.
for s, fit_r, fit_c in (('SENS1', True, False), ('SENS2', False, True)):
    R('4.7k', '+3V3_SW', s, B, dnp=not fit_r, note='pull-up (e.g. DS18B20)' if fit_r else 'pull-up option (e.g. DS18B20)')
    C('100nF', s, 'GND', B, dnp=not fit_c, note='filter (analog)' if fit_c else 'filter option (analog)')
# J2: main sensor connector (fitted) = two 5-way XY308 side by side, pins 1-10 as v0.1 (D4)
TERM('J2', 5, ['GND', 'I2C_SDA', 'I2C_SCL', '+3V3_SW', 'GND'], B, 'J2 SENSORS 1-5')
TERM('J12', 5, ['SENS1', '+3V3_SW', 'GND', 'SENS2', '+3V3_SW'], B, 'J2 SENSORS 6-10')
# J3: same layout (D5); pins 2-3 = RS485 A/B as delivered (JP2/JP3 bridged 1-2), or UART RX/TX (cut, bridge 2-3)
TERM('J3', 5, ['GND', 'J3_P2', 'J3_P3', '+3V3_SW', 'GND'], B, 'J3 RS485 1-5')   # fitted with the RS485 option (D29)
TERM('J13', 5, ['GPIO2', '+3V3_SW', 'GND', 'GPIO4', '+3V3_SW'], B, 'J3 SPARE 6-10')   # fitted (D31)
part('JP', 'Jumper:SolderJumper_3_Bridged12', 'A/RX', SJ3, {'1': 'RS485_A', '2': 'J3_P2', '3': 'RXD0'}, B)
part('JP', 'Jumper:SolderJumper_3_Bridged12', 'B/TX', SJ3, {'1': 'RS485_B', '2': 'J3_P3', '3': 'TXD0'}, B)
TERM('J5', 3, ['GND', 'GPIO10', '+3V3_SW'], B, 'GPIO10', dnp=True)   # D14

# ---------------- RS485 option (fitted by default, D29; omit to save cost) ----------------
B = 'rs485'
part('U', 'Interface_UART:SP3485EN', 'SP3485EN', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
     {'1': 'RXD0', '2': 'GPIO10', '3': 'GPIO10', '4': 'TXD0', '5': 'GND', '6': 'RS485_A', '7': 'RS485_B',
      '8': '+3V3_SW'}, B, lcsc='C8963', mpn='SP3485EN-L/TR')
C('100nF', '+3V3_SW', 'GND', B)
R('10k', 'GPIO10', 'GND', B, note='receive by default')
R('680R', '+3V3_SW', 'RS485_A', B, note='bias'); R('680R', 'RS485_B', 'GND', B, note='bias')
R('120R', 'RS485_A', 'RS485_TERM', B)
part('JP', 'Jumper:SolderJumper_2_Open', 'TERM', SJ, {'1': 'RS485_TERM', '2': 'RS485_B'}, B)
part('D', 'Diode:SM712_SOT23', 'PSM712', SOT23, {'1': 'RS485_A', '2': 'RS485_B', '3': 'GND'}, B,
     lcsc='C32677', mpn='PSM712-LF-T7')
