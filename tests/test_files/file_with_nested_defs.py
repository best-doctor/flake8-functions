def nested_with_returns():
    def wrapper1():
        return 1

    def wrapper2():
        return 2

    def wrapper3():
        return 3

    def wrapper4():
        return 4

    wrapper1()
    wrapper2()
    wrapper3()
    wrapper4()

    return 0
