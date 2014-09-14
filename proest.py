# -*- coding: utf8 -*-
"""Proest-python

Simple implementation of Proest in python.

This implementation does *not* make any claims regarding security!

See http://competitions.cr.yp.to/round1/proestv1.pdf

Author: Thom Wiggers
Licence: BSD
"""
from __future__ import print_function, unicode_literals


def rotate_left(bits, register, amount):
    """Rotate a bits-sized register by amount

    >>> rotate_left(8, 1, 1)
    2
    >>> rotate_left(2, 2, 1)
    1
    """
    amount %= bits
    strval = bin(register)[-bits]
    if len(strval) < bits:
        strval = '0'*(bits-len(strval)) + strval
    return int(strval[amount:] + strval[:amount], 2)


def rotate_right(bits, register, amount):
    """Rotate a bits-sized register by amount

    >>> rotate(8, 1, 1)
    128
    """
    return rotate_left(bits, register, bits-amount)


class Proest(object):

    # Constants for AddConstants
    c1 = 0x7581
    c2 = 0x2bc5

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
                self.state[i][j] &= rotate_left(16, self.c1, round + i*4 + j)
                self.state[i][j+1] &= rotate_left(16, self.c2, round + i*4 + j + 1)

    def _shift_planes(self, round):
        for i in range(4):
            for j in range(4):
                if round % 2 == 0:
                    self.state[i][j] = rotate_right(self.state[i][j], pi_1[i])
                else:
                    self.state[i][j] = rotate_right(self.state[i][j], p2_1[i])

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
        pass

    def _init(self, x, key):
        self.state = [[],[],[],[]]
        for i in range(4):
            for j in range(4):
                self.state[i][j] = 0

    def encrypt(self, x):
        self._init(x)
        for i in range(self.rounds):
            self._sub_rows()
            self._mix_slices()
            self._shift_planes()
            self._add_constant(i)
