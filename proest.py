# -*- coding: utf8 -*-
"""Proest-python

Simple implementation of the Prøst permutation in python.

This implementation does *not* make any claims regarding security!

See http://competitions.cr.yp.to/round1/proestv1.pdf

https://github.com/thomwiggers/proest-python

Author: Thom Wiggers
Licence: BSD
"""
from __future__ import print_function, unicode_literals

import sys


def rotate_left(bits, register, amount):
    """Rotate a bits-sized register by amount

    >>> rotate_left(8, 1, 1)
    2
    >>> rotate_left(2, 2, 1)
    1
    """
    amount %= bits
    binreg = bin(register)
    if len(binreg) - 2 >= bits:
        strval = binreg[-bits:]
    else:
        strval = binreg[2:]
    if len(strval) < bits:
        strval = '0'*(bits-len(strval)) + strval
    return int(strval[amount:] + strval[:amount], 2)


def rotate_right(bits, register, amount):
    """Rotate a bits-sized register by amount

    >>> rotate_right(8, 1, 1)
    128
    >>> rotate_left(16, 0xb2c5, 1)
    """
    return rotate_left(bits, register, bits-amount)


class Proest(object):

    # Constants for AddConstants
    c1 = 0x7581
    c2 = 0xb2c5

    # For shiftPlanes
    pi_1 = [0, 2, 4, 6]
    pi_2 = [0, 1, 8, 9]

    def __init__(self, version=128):
        if not version == 128:
            raise NotImplementedError("Only implemented Prøst-128")

        self.rounds = 16
        self.bits = version

    def _add_constant(self, round):
        for i in range(4):
            for j in range(0, 4, 2):
                self.state[i][j] ^= rotate_left(16, self.c1, round + i * 4 + j)
                self.state[i][j+1] ^= rotate_left(
                    16, self.c2, round + i*4 + j + 1)

    def _shift_planes(self, round):
        for i in range(4):
            for j in range(4):
                if round % 2 == 0:
                    self.state[i][j] = rotate_right(16,
                                                    self.state[i][j],
                                                    self.pi_1[i])
                else:
                    self.state[i][j] = rotate_right(16,
                                                    self.state[i][j],
                                                    self.pi_2[i])

    def _mix_slices(self):
        M = ['1000100100101011',
             '0100100000011001',
             '0010010011001000',
             '0001001001100100',
             '1001100010110010',
             '1000010010010001',
             '0100001010001100',
             '0010000101000110',
             '0010101110001001',
             '0001100101001000',
             '1100100000100100',
             '0110010000010010',
             '1011001010011000',
             '1001000110000100',
             '1000110001000010',
             '0100011000100001']
        oldx = []
        newx = []
        for i in range(4):
            for j in range(4):
                oldx.append(self.state[i][j])

        for row in M:
            newrow = 0
            for i in range(16):
                if row[i] == '1':
                    newrow ^= oldx[i]
            newx.append(newrow)

        for i in range(4):
            for j in range(4):
                self.state[i][j] = newx[i*4+j]

    def _sub_rows(self):
        for i in range(4):
            # We can do this for the whole register at once bitsliced
            self.state[i] = self._sbox(self.state[i])

    def _sbox(self, bits):
        """Sbox via the formula"""
        (p, q) = bits[0], bits[1]
        bits[0] = bits[2] ^ (p & q)
        bits[1] = bits[3] ^ (q & bits[2])
        bits[2] = p ^ (bits[0] & bits[1])
        bits[3] = q ^ (bits[1] & bits[2])
        return bits

    def _init(self, x):
        self.state = [[0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]]
        for i in range(4):
            for j in range(4):
                self.state[i][j] = (x >> ((i*4 + j)*16)) & 0xffff

    def write_state(self):
        out = b''
        for i in range(4):
            for j in range(4):
                out += self.state[i][j].to_bytes(2, byteorder='little')

        return out

    def permute(self, x):
        self._init(x)
        for i in range(self.rounds):
            self._sub_rows()
            self._mix_slices()
            self._shift_planes(i)
            self._add_constant(i)

    def printstate(self):
        for char in self.write_state():
            print('%02x' % char, end='')
        print()

if __name__ == "__main__":
    proest = Proest()
    x, count = 0, 0
    for arg in sys.argv[1:]:
        for char in arg:
            x |= (ord(char) << (count * 8))
            count += 1
    proest.permute(x)
    print("Output: ", end='')
    proest.printstate()
