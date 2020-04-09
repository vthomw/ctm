#!/usr/bin/env python3

import argparse
from collections import abc
import dataclasses
from typing import NamedTuple


class Binary:
    def __init__(self, data):
        if not isinstance(data, abc.Sequence):
            data = [data]
        self.data = data

    def __str__(self):
        return (f"{self.__class__.__name__}{len(self.data)}"
                f"({', '.join(map(hex, self.data))})")


class AnyPointer(NamedTuple):
    pos: int


class RecentPointer(AnyPointer):
    pass


class HistoryPointer(AnyPointer):
    pass


@dataclasses.dataclass
class AnyEntry:
    index: int
    flags1: int
    bgl: int
    flags2: int
    flags3: int
    flags4: int
    temp: int
    flags5: int

    def __init__(self, index, data):
        if len(data) != 6:
            raise ValueError("Need exactly six bytes of data.")
        self.index = index
        tmp = little_endian(data[:2])
        self.flags1 = tmp // 0x2000
        self.bgl = tmp & 0x1FFF
        self.flags2 = data[2]
        tmp = little_endian(data[3:5])
        self.flags3 = tmp // 0x4000
        self.flags4 = tmp & 0x3
        self.temp = (tmp & 0x3FFF) // 0x4
        self.flags5 = data[5]

    def __str__(self):
        representations = {
            'index': f'{self.index:02}',
            'bgl': f'{self.bgl:04}',
            'temp': f'{self.temp:04}',
            'flags1': f'{self.flags1:03b}',
            'flags2': f'{self.flags2:08b}',
            'flags3': f'{self.flags3:02b}',
            'flags4': f'{self.flags4:02b}',
            'flags5': f'{self.flags5:08b}',
        }
        attributes = ', '.join(f'{key}={val}'
                               for key, val in representations.items())
        return f'{self.__class__.__name__}({attributes})'


class RecentEntry(AnyEntry):
    pass


class HistoryEntry(AnyEntry):
    pass


class Timer(NamedTuple):
    time: int


def little_endian(a, b=None):
    if b is None:
        a, b = a
    return (b << 8) + a


def process(path):
    with open(path, 'rb') as infile:
        raw = infile.read()
    data = []
    data.append(Binary(raw[0:24]))
    data.append(Binary(raw[24:26]))
    data.append(RecentPointer(raw[26]))
    data.append(HistoryPointer(raw[27]))
    for i in range(16):
        data.append(RecentEntry(i, raw[6*i + 28:6*i + 34]))
    for i in range(32):
        data.append(HistoryEntry(i, raw[6*i + 124:6*i + 130]))
    data.append(Timer(little_endian(*raw[316:318])))
    data.append(Binary(raw[318:344]))
    return data


def output(data):
    for thing in data:
        print(thing)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Make data readable.')
    parser.add_argument(
        'files', help='path to data file', nargs='+')
    args = parser.parse_args()
    for path in args.files:
        output(process(path))
