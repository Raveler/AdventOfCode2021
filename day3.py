
from itertools import groupby

f = open("input3-1.txt")
lines = f.readlines()

bit_length = len(lines[0])-1 # avoid \n

def get_most_common(lines, pos):
    bits = [line[pos] for line in lines]
    bits = sorted(bits)
    bit_count = [len(list(group)) for key, group in groupby(bits)]
    if bit_count[0] == bit_count[1]:
        val = 1
        return val
    elif bit_count[0] < bit_count[1]:
        return 1
    else:
        return 0


gamma_rate = ""
epsilon_rate = ""
for i in range(0, bit_length):

    # select the bits
    most_common = get_most_common(lines, i)

    if most_common == 0:
        gamma_rate += "0"
        epsilon_rate += "1"
    else:
        gamma_rate += "1"
        epsilon_rate += "0"


def filter_out(invert_most_common):
    codes = list(lines)

    for i in range(0, bit_length):
        most_common = get_most_common(codes, i)
        if invert_most_common:
            most_common = 1-most_common

        codes = list(filter(lambda code: int(code[i]) == most_common, codes))

        if len(codes) == 1:
            return codes[0]


gamma_rate = int(gamma_rate, 2)
epsilon_rate = int(epsilon_rate, 2)

power_consumption = gamma_rate * epsilon_rate

print("Power consumption: " + str(power_consumption))

oxygen_rating = int(filter_out(False), 2)
scrubber_rating = int(filter_out(True), 2)

print("Oxygen rating: " + str(oxygen_rating))
print("Scrubber rating: " + str(scrubber_rating))
print("Life support: " + str(oxygen_rating * scrubber_rating))

