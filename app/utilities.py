from datetime import datetime

class Utilities(object):
    def __init__(self):
        pass

    def strfdelta(self, sec, fmt):
        if isinstance(sec, str):
            return sec

        d = {}
        d["minutes"], d["seconds"] = divmod(sec, 60)
        d["hours"], d["minutes"] = divmod(d["minutes"], 60)
        return fmt.format(**d)

    def convert_epoch_time(self, seconds):
        local_time = datetime.fromtimestamp(seconds)
        return [local_time.strftime('%a %d.%m.%y'), local_time.strftime('%H:%M')]

    def convert_inches(self, inches):
        if isinstance(inches, str):
            return inches

        meter = inches // 39.3701
        kilometer = round(meter / 1000, 1)
        if kilometer > 99:
            kilometer = round(kilometer)
        return f"{kilometer}km"

    def convert_scores(self, score):
        if isinstance(score, str):
            return score

        if score > 999999:
            score = str(round(score / 1000000)) + "m"
        elif score > 999:
            score = str(round(score / 1000)) + "k"
        return score

