from __future__ import annotations
from datetime import datetime, timedelta


class PeriodicSimpleTime:
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0, microsecond: int = 0):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.microsecond = microsecond

    def __str__(self):
        return f'{self.hour}:{self.minute}:{self.second}'

    @staticmethod
    def from_datetime(_datetime: datetime) -> PeriodicSimpleTime:
        r_millisecond = _datetime.microsecond % 1000
        millisecond = int((_datetime.microsecond - r_millisecond) / 1000)
        return PeriodicSimpleTime(_datetime.hour, _datetime.minute, _datetime.second, millisecond, r_millisecond)

    @staticmethod
    def from_microseconds(microseconds: float) -> PeriodicSimpleTime:
        assert microseconds <= 8.64e+10
        if not microseconds:
            return PeriodicSimpleTime()
        r_hour = microseconds % 3.6e+9
        hour = int((microseconds - r_hour) / 3.6e+9)
        r_minute = r_hour % 6e+7
        minute = int((r_hour - r_minute) / 6e+7)
        r_second = r_minute % 1e+6
        second = int((r_minute - r_second) / 1e+6)
        r_millisecond = r_second % 1000
        millisecond = int((r_second - r_millisecond) / 1000)
        return PeriodicSimpleTime(hour, minute, second, millisecond, int(r_millisecond))

    @staticmethod
    def from_dict(dictionary: dict) -> PeriodicSimpleTime:
        """
        Instantiate a PeriodicSimpleTime instance from a dict
        :param dictionary: Dict, that may contain: hour, minute, second, millisecond, microsecond
        :return: PeriodicSimpleTime
        """
        try:
            hour = dictionary['hour']
        except KeyError:
            hour = 0
        try:
            minute = dictionary['minute']
        except KeyError:
            minute = 0
        try:
            second = dictionary['second']
        except KeyError:
            second = 0
        try:
            millisecond = dictionary['millisecond']
        except KeyError:
            millisecond = 0
        try:
            microsecond = dictionary['microsecond']
        except KeyError:
            microsecond = 0
        return PeriodicSimpleTime(hour, minute, second, millisecond, microsecond)

    def to_seconds(self) -> float:
        return self.hour * 3600 + self.minute * 60 + self.second + self.millisecond / 1000 + self.microsecond / 1e+6

    def to_microseconds(self) -> float:
        return self.hour * 3.6e+9 + self.minute * 6e+7 + self.second * 1e+6 + self.millisecond * 1000 + self.microsecond

    def get_next_period(self, period: PeriodicSimpleTime) -> PeriodicSimpleTime:
        """
        Calculates the next period based on the current PeriodicSimpleTime instance and the multiply on a given period
        :param period: Period
        :return: PeriodicSimpleTime
        """
        ms = self.to_microseconds()
        p_ms = period.to_microseconds()
        assert 8.64e+10 % p_ms == 0
        if ms < p_ms:
            # time before period, therefore the period is also the next period time
            return period
        # calculate next period time based on
        # x times the period fits fully into the current time plus the period
        i = int((ms - (ms % p_ms)) / p_ms)
        next_p_ms = i * p_ms + p_ms
        if next_p_ms == 8.64e+10:
            # end of day, return 00:00 instead of 24:00
            return PeriodicSimpleTime()
        return PeriodicSimpleTime.from_microseconds(next_p_ms)

    def calc_difference(self, simple_time: PeriodicSimpleTime) -> tuple:
        """
        Calculate difference between the current PeriodicSimpleTime instance and the argument, supports overnight
        :param simple_time: PeriodicSimpleTime
        :return: Difference, if overnight
        """
        a, b = self.to_microseconds(), simple_time.to_microseconds()
        if a <= b:
            # same day
            diff = b - a
            is_overnight = False
        else:
            # overnight
            diff = 8.64e+10 - a + b
            is_overnight = True
        return PeriodicSimpleTime.from_microseconds(diff), is_overnight


def get_next_periodic_dt(period: PeriodicSimpleTime) -> datetime:
    """
    Calculate the next datetime based on a given period,
    e.g. you want the next 5min periodic datetime,
    currently it is 15:1:0,
    this method will calculate 15:5:0 as return
    :param period: Period
    :return: datetime
    """
    dt = datetime.utcnow()
    st = PeriodicSimpleTime.from_datetime(dt)
    next_p = st.get_next_period(period)
    _, is_overnight = st.calc_difference(next_p)
    if is_overnight:
        dt += timedelta(days=1)
    return datetime(year=dt.year, month=dt.month, day=dt.day,
                    hour=next_p.hour, minute=next_p.minute, second=next_p.second)
