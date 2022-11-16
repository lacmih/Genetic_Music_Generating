# Defining different functions, that add up the fitness value

# Subraters from paper Apply evolutionary algorithms for music generation
# url: https://odr.chalmers.se/server/api/core/bitstreams/2a2d8e3b-d16f-4d4d-8edd-ecdd599f1bfd/content

# Direction of melody:
def direction_fitness(melody_act):
    # dir = 1 -> up -1 -> down

    prev = melody_act[0]
    dir = 1
    n_act = 0
    n_same_dir = 0

    for i in melody_act[1:len(melody_act)]:
        # print(i)
        # +
        if dir == 1:
            if i >= prev:
                # print("+")
                n_act += 1
                if (n_act >= 3):
                    # print("++ novel")
                    n_same_dir += 1
            else:
                dir = -1
                n_act = 1
        # -
        else:
            if i <= prev:
                n_act += 1
                # print("-")
                if (n_act >= 3):
                    # print("-- novel")
                    n_same_dir += 1
            else:
                dir = 1
                n_act = 1
        prev = i
    print(n_same_dir, "/", len(melody_act))
    return n_same_dir / len(melody_act)
