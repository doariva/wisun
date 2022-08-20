from prometheus_client import start_http_server, Gauge
from time import sleep
import serial
import logging
import schedule
import sys
import config

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

ENERGY_HEALTH = Gauge('energy_health', 'This is Energy Health')
ENERGY_METRICS_W = Gauge('energy_metrics_w', 'This is Energy Metrics [W]')
ENERGY_METRICS_A = Gauge('energy_metrics_a', 'This is Energy Metrics [A]')

logging.info("Start")
ser = serial.Serial(config.dev, 115200, timeout=30.0)
ipv6 = config.ipv6

echonetLiteFrame = b''
EHD = b'\x10\x81'       # EHD
TID = b'\x00\x01'       # TID
SEOJ = b'\x05\xFF\x01'  # SEOJ
DEOJ = b'\x02\x88\x01'  # DEOJ
ESV = b'\x62'           # ESV
OPC = b'\x03'           # OPC
##
EPC1 = b'\x80'          # EPC 動作状態 0x30=on/0x31=off
# EPC1 = b'\x97'        # EPC 現在時刻
# EPC1 = b'\x98'        # EPC 現在年月日
# EPC1 = b'\xD3'        # EPC 係数
# EPC = b'\xD7'         # EPC 積算電力量有効桁数
# EPC = b'\xE0'         # EPC 積算電力量計測値(正方向計測値)
# EPC = b'\xE1'         # EPC 積算電力量単位(正方向、逆方向計測値)
# EPC = b'\xE2'         # EPC 積算電力量計測値履歴１(正方向計測値)
# EPC = b'\xE3'         # EPC 積算電力量計測値(逆方向計測値)
# EPC = b'\xE4'         # EPC 積算電力量計測値履歴１(逆方向計測値)
# EPC = b'\xE5'         # EPC 積算履歴収集日1
EPC2 = b'\xE7'          # EPC 瞬時電力計測値
EPC3 = b'\xE8'          # EPC 瞬時電流計測値
# EPC = b'\xEA'         # EPC 定時積算電力量計測値(正方向計測値)
# EPC = b'\xEB'         # EPC 定時積算電力量計測値(逆方向計測値)
# EPC = b'\xEC'         # EPC 積算電力量計測値履歴2(正方向、逆方向計測値)
# EPC = b'\xED'         # EPC 積算履歴収集日2
##
PDC = b'\x00'           # PDC
echonetLiteFrame += EHD + TID + SEOJ + DEOJ + ESV + OPC \
        + EPC1 + PDC \
        + EPC2 + PDC \
        + EPC3 + PDC

tmp_cmd = 'SKSENDTO 1 {0} 0E1A 1 {1:04X} '.format(ipv6, len(echonetLiteFrame))
command = tmp_cmd.encode() + echonetLiteFrame + b'\r\n'


# @ENERGY_HEALTH.track_inprogress()
# @ENERGY_METRICS_W.track_inprogress()
# @ENERGY_METRICS_A.track_inprogress()
def get():
    read = []
    hasERXUDP = False
    # logging.debug(command)
    ser.write(command)

    while not hasERXUDP:
        read = ser.readline().decode().strip().split()
        logging.debug(read)
        if "ERXUDP" in read:
            hasERXUDP = True
            break

    try:
        # ERXUDP = read[0]
        SENDER = read[1]
        DEST = read[2]
        # RPORT = read[3]
        # LPORT = read[4]
        # SENDERLLA = read[5]
        # SECURED = read[6]
        # DATALEN = read[7]
        DATA = read[8]
        logging.debug("SRC: " + SENDER)
        logging.debug("DST: " + DEST)
        logging.debug("DATA: " + DATA)
        # EHD = DATA[0:4]
        # TID = DATA[4:8]
        # SEOJ = DATA[8:14]
        # DEOJ = DATA[14:20]
        # ESV = DATA[20:22]
        # OPC = DATA[22:24]
        EPC3 = DATA[24:26]
        PDC3 = DATA[26:28]
        MET3 = DATA[28:30]
        EPC4 = DATA[30:32]
        PDC4 = DATA[32:34]
        MET4 = DATA[34:42]
        EPC5 = DATA[42:44]
        PDC5 = DATA[44:46]
        MET5 = DATA[46:54]
        # logging.debug(EHD)
        # logging.debug(TID)
        # logging.debug(SEOJ)
        # logging.debug(DEOJ)
        # logging.debug(ESV)
        # logging.debug(OPC)
        # logging.debug("EPC: " + EPC)
        # logging.debug(PDC)
        # logging.debug("MET: " + MET)
    except IndexError:
        logging.error("ParseError")
        return

    logging.debug("EPC3: " + EPC3)
    logging.debug("PDC3: " + PDC3)
    logging.debug("MET3: " + MET3)
    logging.debug("EPC4: " + EPC4)
    logging.debug("PDC4: " + PDC4)
    logging.debug("MET4: " + MET4)
    logging.debug("EPC5: " + EPC5)
    logging.debug("PDC5: " + PDC5)
    logging.debug("MET5: " + MET5)

    try:
        if EPC3 == "80":
            if MET3 == "30":
                logging.info("isHealth: True")
                ENERGY_HEALTH.set(1.0)
            else:
                logging.info("isHealth: False")
                ENERGY_HEALTH.set(0.0)
        if EPC4 == "E7":
            metrics = int(MET4, 16)
            logging.info("瞬時電力計測値[W]: {0}".format(metrics))
            ENERGY_METRICS_W.set(metrics)
            metrics = -1
        if EPC5 == "E8":
            metrics = int(MET5[4:], 16)/10
            logging.info("瞬時電流計測値[A]: {0}".format(metrics))
            ENERGY_METRICS_A.set(metrics)
            metrics = -1
        # if EPC == "D3":
        #   logging.info("係数: {0}".format(int(MET, 16)))
    except ValueError:
        logging.error("ValueError")
    hasERXUDP = False


def reconnect():
    ser.write(str.encode("SKJOIN " + ipv6 + "\r\n"))

    while True:
        read = ser.readline().decode().strip().split()
        logging.debug(read)
        if ("EVENT" in read and "25" in read):
            logging.info("ReConnect Success")
            global isAuth
            isAuth = True
            return True
        elif "FAIL" in read:
            logging.error("ReConnect Failed")
        continue


def reauth():
    logging.info("ReAuth")
    ser.write(str.encode("SKREJOIN\r\n"))

    while True:
        read = ser.readline().decode().strip().split()
        logging.debug(read)
        if ("EVENT" in read and "25" in read):
            logging.info("ReAuth Success")
            global isAuth
            isAuth = True
            break
        elif "FAIL" in read:
            logging.error("ReAuth Failed")
            continue


def expiredAuth():
    global isAuth
    isAuth = False


def exit():
    logging.warning("exit()")
    sys.exit()


global isAuth
isAuth = False

schedule.every(6).hours.at(":05").do(reconnect)
schedule.every().hour.at(":45").do(expiredAuth)
schedule.every().day.at("04:10").do(exit)


if __name__ == '__main__':
    reconnect()
    start_http_server(8000)
    while True:
        schedule.run_pending()
        if isAuth:
            get()
        else:
            reauth()
        sleep(30)

