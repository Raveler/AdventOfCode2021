
from itertools import groupby
import re
import math
import pprint
pp = pprint.PrettyPrinter(indent=4)
from collections import defaultdict
import numpy
import binascii
from collections import Counter


def decode_to_binary(hex_string):
    scale = 16  ## equals to hexadecimal
    num_of_bits = 8
    return bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)


sum_version_numbers = 0

class BitStream:

    def __init__(self, text):
        self.text = text
        self.index = 0

    def read_bits(self, n_bits):
        str = self.text[self.index:self.index + n_bits]
        self.index += n_bits
        return str

    def read_int(self, n_bits):
        str = self.read_bits(n_bits)
        return int(str, 2)

    def read_literal(self):
        str = self.read_bits(5)
        literal_str = ""
        literal_str += str[1:]
        while str[0] == '1':
            str = self.read_bits(5)
            literal_str += str[1:]
        return int(literal_str, 2)

    def get_substream(self, n_bits):
        return BitStream(self.text[self.index:self.index+n_bits])

    def skip(self, n_bits):
        self.index += n_bits

    def is_done(self):
        return self.index >= len(self.text)


class Packet:

    def __init__(self, stream):
        self.subpackets = []
        self.stream = stream

    def parse(self):
        stream = self.stream

        version = stream.read_int(3)
        sum_version_numbers = version
        type = stream.read_int(3)

        print(f"Parse packet with version {version} and type {type}")

        # literal value
        if type == 4:
            self.literal = stream.read_literal()
            print(f"Literal packet with value {self.literal}")
            self.value = self.literal


        # operator
        else:

            length_type_id = stream.read_bits(1)
            if length_type_id == '0':
                total_length_in_bits = stream.read_int(15)
                print(f"Operator packet with {total_length_in_bits} bits for the subpackets")

                substream = stream.get_substream(total_length_in_bits)
                stream.skip(total_length_in_bits)
                while not substream.is_done():
                    subpacket = Packet(substream)
                    sum_version_numbers += subpacket.parse()
                    self.subpackets.append(subpacket)




            else:
                number_of_subpackets = stream.read_int(11)
                print(f"Operator packet with {number_of_subpackets} subpackets")

                for i in range(0, number_of_subpackets):
                    subpacket = Packet(stream)
                    sum_version_numbers += subpacket.parse()
                    self.subpackets.append(subpacket)

            # go over all subpackets and perform the operation
            subvalues = [subpacket.value for subpacket in self.subpackets]
            if type == 0:
                self.value = sum(subvalues)
            elif type == 1:
                self.value = numpy.prod(subvalues)
            elif type == 2:
                self.value = min(subvalues)
            elif type == 3:
                self.value = max(subvalues)
            elif type == 5:
                if subvalues[0] > subvalues[1]:
                    self.value = 1
                else:
                    self.value = 0
            elif type == 6:
                if subvalues[0] < subvalues[1]:
                    self.value = 1
                else:
                    self.value = 0
            elif type == 7:
                if subvalues[0] == subvalues[1]:
                    self.value = 1
                else:
                    self.value = 0


        return sum_version_numbers








def solve():
    with open("input16-2.txt") as f:

        lines = [line.strip("\n") for line in f.readlines()]

        binary = decode_to_binary(lines[0])
        stream = BitStream(binary)
        packet = Packet(stream)
        sum_version_numbers = packet.parse()

        print(f"The sum of all version numbers is {sum_version_numbers}")
        print(f"The final value is {packet.value}")

solve()

