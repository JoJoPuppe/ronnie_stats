from datetime import datetime

class Utilities(object):
    def __init__(self):
        pass

    def strfdelta(self, sec, fmt):
        d = {}
        d["minutes"], d["seconds"] = divmod(sec, 60)
        d["hours"], d["minutes"] = divmod(d["minutes"], 60)
        return fmt.format(**d)

    def convert_epoch_time(self, seconds):
        local_time = datetime.fromtimestamp(seconds)
        return [local_time.strftime('%a %d.%m.%y'), local_time.strftime('%H:%M')]

    def convert_inches(self, inches):
        meter = inches // 39.3701
        kilometer = round(meter / 1000, 2)
        return f"{kilometer}km"
