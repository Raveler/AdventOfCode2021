

position = 0
depth = 0
aim = 0

f = open("input2-1.txt")
lines = f.readlines()

for line in lines:
    split = line.split(" ")
    cmd = split[0]
    distance = int(split[1])

    if cmd == "forward":
        position += distance
        depth += aim * distance

    elif cmd == "down":
        aim += distance

    elif cmd == "up":
        aim -= distance

    else:
        raise "Invalid command " + line


print("Final position: " + str(position) + ", depth: " + str(depth))
print("Answer #1: " + str(position * depth))