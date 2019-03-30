from enum import Enum, unique


@unique
class DateFormatStrEnum(Enum):
    DAY_BASE = "%y-%m-%d"
    HOUR_BASE = "%y-%m-%d HH"
    MINUTE_BASE = "%y-%m-%d HH:MM"

    @staticmethod
    def convert_from_value(format_str:str):
        if format_str is None:
            return None
        if "%y-%m-%d" == format_str.strip():
            return DateFormatStrEnum.DAY_BASE
        if "%y-%m-%d HH" == format_str.strip():
            return DateFormatStrEnum.HOUR_BASE
        if "%y-%m-%d HH:MM" == format_str.strip():
            return DateFormatStrEnum.MINUTE_BASE

        return None
