#!/usr/bin/env python3

import argparse
import re
import serial
import sys

class Modem(object):

    def __init__(self, device, speed):
        self._device = device
        self._speed = speed
        self._debug = False

    def set_debug(self, debug):
        self._debug = debug

    def reset(self):
        self._command("ATZ")

    def noop(self):
        self._command("AT")

    def activate(self):
        self._command("AT+CFUN=1")

    def _command(self, cmd):
        out_line = "%s\r\n" % cmd
        in_lines = []
        with serial.Serial(port=self._device, baudrate=self._speed, timeout=1) as ser:
            data = out_line.encode()
            if self._debug:
                print(data, file=sys.stderr)
            ser.write(data)
            while True:
                in_line = ser.readline()
                if self._debug:
                    print(in_line, file=sys.stderr)
                if len(in_line) == 0:
                    break
                in_line_str = in_line.decode().rstrip("\r\n")
                in_lines.append(in_line_str)
                if in_line_str == "OK":
                    break
                if in_line_str == "NO CARRIER":
                    break
                if in_line_str == "ERROR":
                    raise Exception("Modem command failed: %s" % cmd)
        return in_lines

    def get_time(self):
        lines = self._command("AT+CCLK?")
        data = lines[1]
        p = re.compile('^\+CCLK: "(\d\d)/(\d\d)/(\d\d),(\d\d):(\d\d):(\d\d)"$')
        m = p.match(data)
        if m is None:
            raise Exception("%s didn't match regex %s" % (data, p.pattern))
        year = int(m.group(1))
        if year >= 80:
            year += 1900
        else:
            year += 2000
        month = int(m.group(2))
        day = int(m.group(3))
        hour = int(m.group(4))
        minute = int(m.group(5))
        seconds = int(m.group(6))
        print("%04d-%02d-%02d %02d:%02d:%02d" % (year, month, day, hour, minute, seconds))

    def get_pdu(self):
        self._command("AT+CMEE=1")
        self._command("AT+CMGF=0")
        self._command("AT+CPMS=\"SM\",\"SM\",\"SM\"")
        lines = self._command("AT+CMGL=4")
        while len(lines) > 0:
            line = lines.pop(0)
            p = re.compile('^\+CMGL: (\d+),(\d+),[^,]*,(\d+)$')
            m = p.match(line)
            if m is None:
                continue
            length = int(m.group(3))
            pdu = lines.pop(0)
            print("%d,%s" % (length, pdu))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", required=True)
    parser.add_argument("--speed", type=int, default=115200)
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("action")
    args = parser.parse_args()

    modem = Modem(args.device, args.speed)
    modem.set_debug(args.debug)
    modem.reset()
    modem.noop()
    modem.activate()

    if args.action == "clock":
        modem.get_time()
    elif args.action == "readpdu":
        modem.get_pdu()
