def get_counter_string(s):
    # get a string that helps me see how many chars long something is, for debugging
    n = len(s)
    if n == 0:
        return "0"
    elif n <= 9:
        return "123456789"[:len(s)]
    elif n <= 999:
        # print the 10s such that their last 0 is at that length, and 5s halfway
        # e.g. for length 28: ....5...10....5...20....5678
        n_tens, rem = divmod(n, 10)
        ten_strs = []
        for i in range(n_tens):
            ten_str = str(i+1) + "0"
            template = "....5....."
            ten_strs.append(template[:-len(ten_str)] + ten_str)
        assert all(len(x) == 10 for x in ten_strs)
        assert all(x[-1] == "0" for x in ten_strs)
        res = "".join(ten_strs)

        if rem == 0:
            pass
        elif rem == 1:
            # need to put a 1 here but it's right next to the last 10, so we'll hack by changing the 0 to a o
            res = res[:-1] + "o"
            res += "1"
        elif rem < 5:
            res += "." * (rem - 1) + str(rem)
        elif rem == 5:
            res += "....5"
        elif rem == 6:
            res += "....s6"
        else:
            res += "....5" + "." * (rem - 5 - 1) + str(rem)
        return res
    else:
        raise Exception("too long")
