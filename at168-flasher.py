#!/usr/bin/env python3

# Copyright 2025 Dual Tachyon
# https://github.com/DualTachyon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from binascii import hexlify
from struct import pack

import serial
import sys

print('Anytone D168UV raw firmware flasher. Copyright 2025 Dual Tachyon')
print('')

if len(sys.argv) != 3:
    print('Usage: %s <serial port> <firmware binary>' % sys.argv[0])
    print('')
    sys.exit(1)

try:
    firmware = open(sys.argv[2], 'rb').read()
except:
    print('Error trying to load firmware binary')
    print('')
    sys.exit(1)

try:
    s = serial.Serial(port=sys.argv[1], baudrate=4000000, timeout=1)
except:
    print('Error trying to open serial port')
    print('')
    sys.exit(1)

s.write(b'UPDATE')
r = s.read()
if r != b'\x06':
    print('Failed to start update mode!')
    print('')
    sys.exit(1)

if len(firmware) % 32 > 0:
    firmware += b'\x00' * (32 - (len(firmware) % 32))

offset = 0
while offset != len(firmware):
    body = pack('<I', 0x08004000 + offset) + firmware[offset : offset + 32]
    checksum = sum(body)
    packet = b'\x01' + body + pack('<H', checksum) + b'\x06'
    print('\rUpdating %08X' % (0x08004000 + offset), end='')
    s.write(packet)
    r = s.read()
    if r != b'\x06':
        print('Failed to update!')
        print('')
        sys.exit(1)
    offset += 32

s.write(b'\x18')

print('\rUpdate complete! ')
print('')

sys.exit(0)

