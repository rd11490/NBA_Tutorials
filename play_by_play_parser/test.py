
def parse_time_elapsed(time_str, period):
    max_minutes = 12 if period < 5 else 5
    [minutes, sec] = time_str.split(':')
    minutes = int(minutes)
    sec = int(sec)
    min_elapsed = max_minutes - minutes - 1
    sec_elapsed = 60 - sec

    out =  (min_elapsed * 60) + sec_elapsed

    print('{} -> {}'.format(time_str, out))

    return out





parse_time_elapsed('12:00', 1)
parse_time_elapsed('7:42', 1)
parse_time_elapsed('0:00', 1)
parse_time_elapsed('0:38', 1)
parse_time_elapsed('0:00', 5)
parse_time_elapsed('0:38', 5)


