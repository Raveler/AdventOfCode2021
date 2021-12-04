

def puzzle1():
    f = open("input1-1.txt")
    lines = f.readlines()

    depths = [int(line) for line in lines]

    prev_depth = depths[0]

    increments = 0
    for i in range(1, len(depths)):
        depth = depths[i]

        if prev_depth < depth:
            increments += 1

        prev_depth = depth


    print("Increments: " + str(increments))


def puzzle2():
    f = open("input1-1.txt")
    lines = f.readlines()

    depths = [int(line) for line in lines]

    increments = 0
    for i in range(0, len(depths)-3):

        print(depths[i:i+3])
        print(depths[i+1:i+4])

        first_sum = sum(depths[i:i+3])
        second_sum = sum(depths[i+1:i+4])
        print(str(first_sum) + " < " + str(second_sum))

        if first_sum < second_sum:
            increments += 1


    print("Sum increments: " + str(increments))




puzzle1()
puzzle2()