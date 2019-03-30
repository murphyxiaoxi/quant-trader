from typing import Dict, List, Any

from backend.commons.enums.date_format_enums import DateFormatStrEnum


def get_from_dic(d: Dict[str, Any], k: str):
    return d[k] if k in d else None


class PositionDO(object):
    def __init__(
            self,
            date_str: str,
            symbol_position: Dict[str, int]
    ):
        """

        :param date_str: 日期
        :param symbol_position: 每只证券现有头寸
        """
        self.date_str: str = date_str

        self.symbol_position: Dict[str, int] = symbol_position

    def convert_2_dict(self):
        return {
            "date_str": self.date_str,
            "symbol_position": self.symbol_position
        }

    @staticmethod
    def convert_from_dict(d: Dict[str, Any]):
        return PositionDO(
            get_from_dic(d, 'date_str'),
            get_from_dic(d, 'symbol_position')
        )


class HoldingDO(object):
    def __init__(
            self,
            date_str: str,
            cash: float,
            commission: float,
            total: float,
            symbol_hold: Dict[str, float]
    ):
        """

        :param date_str: 日期
        :param cash: 剩余现金
        :param commission: 交易费用
        :param total: 总持有金额
        :param symbol_hold: 每只证券持有金额
        """
        self.date_str: str = date_str
        self.cash: float = cash
        self.commission: float = commission
        self.total: float = total
        self.symbol_hold: Dict[str, float] = symbol_hold

    def convert_2_dict(self):
        return {
            "date_str": self.date_str,
            "cash": self.cash,
            "commission": self.commission,
            "total": self.total,
            "symbol_hold": self.symbol_hold
        }

    @staticmethod
    def convert_from_dict(d: Dict[str, Any]):
        return HoldingDO(
            get_from_dic(d, 'date_str'),
            get_from_dic(d, 'cash'),
            get_from_dic(d, 'commission'),
            get_from_dic(d, 'total'),
            get_from_dic(d, 'symbol_hold')
        )


class PortfolioDO(object):
    def __init__(
            self,
            portfolio_id: int,
            name: str,
            description: str,
            start_date_str: str,
            date_format: DateFormatStrEnum,
            symbol_list: List[str],
            initial_capital: float,
            all_position: List[PositionDO],
            current_position: PositionDO,
            all_holding: List[HoldingDO],
            current_holding: HoldingDO
    ):
        """

        :param portfolio_id: 证券投资组合账户ID
        :param name: 名称
        :param description: 描述信息
        :param start_date_str: 起始时间
        :param date_format: 日期格式
        :param symbol_list: 证券集合
        :param initial_capital: 起始资金
        :param all_position: 所有证券持有头寸
        :param current_position: 当前所有证券持有头寸
        :param all_holding: 所有证券持有金额
        :param current_holding: 当前所有证券持有金额
        """
        self.portfolio_id: int = portfolio_id
        self.name: str = name
        self.description: str = description
        self.start_date_str: str = start_date_str
        self.date_format: DateFormatStrEnum = date_format
        self.symbol_list: List[str] = symbol_list
        self.initial_capital: float = initial_capital
        self.all_position: List[PositionDO] = all_position
        self.current_position: PositionDO = current_position
        self.all_holding: List[HoldingDO] = all_holding
        self.current_holding: HoldingDO = current_holding

    def convert_2_dict(self):
        return {
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "description": self.description,
            "start_date_str": self.start_date_str,
            "date_format": self.date_format.value,
            "symbol_list": self.symbol_list,
            "initial_capital": self.initial_capital,
            "all_position":
                None if self.all_position is None
                else [item.convert_2_dict() for item in self.all_position],
            "current_position":
                None if self.current_position is None
                else self.current_position.convert_2_dict(),
            "all_holding":
                None if self.all_holding is None
                else [item.convert_2_dict() for item in self.all_holding],
            "current_holding":
                None if self.current_holding is None
                else self.current_holding.convert_2_dict()
        }

    @staticmethod
    def convert_from_dict(d: Dict[str, Any]):
        return PortfolioDO(
            get_from_dic(d, 'portfolio_id'),
            get_from_dic(d, 'name'),
            get_from_dic(d, 'description'),
            get_from_dic(d, 'start_date_str'),
            DateFormatStrEnum.convert_from_value(get_from_dic(d, 'date_format')),
            get_from_dic(d, 'symbol_list'),
            get_from_dic(d, 'initial_capital'),
            PortfolioDO._parse_all_position(d),
            PortfolioDO._parse_current_position(d),
            PortfolioDO._parse_all_holding(d),
            PortfolioDO._parse_current_holding(d)
        )

    @staticmethod
    def _parse_all_position(d: Dict[str, Any]):
        tmp_list = get_from_dic(d, 'all_position')
        if tmp_list is None:
            return None
        else:
            return [PositionDO.convert_from_dict(item) for item in tmp_list]

    @staticmethod
    def _parse_current_position(d: Dict[str, Any]):
        m = get_from_dic(d, 'current_position')
        if m is None:
            return None
        else:
            return PositionDO.convert_from_dict(m)

    @staticmethod
    def _parse_all_holding(d: Dict[str, Any]):
        tmp_list = get_from_dic(d, 'all_holding')
        if tmp_list is None:
            return None
        else:
            return [HoldingDO.convert_from_dict(item) for item in tmp_list]

    @staticmethod
    def _parse_current_holding(d: Dict[str, Any]):
        m = get_from_dic(d, 'current_holding')
        if m is None:
            return None
        else:
            return HoldingDO.convert_from_dict(m)


if __name__ == '__main__':
    portfolio = PortfolioDO(1, "test", "desc", "2019-01-01", DateFormatStrEnum.DAY_BASE,
                            ['s1', 's2'], 1000.0, [PositionDO('2019-01-01', {'s1': 1})],
                            PositionDO('2019-01-01', {'s1': 1}),
                            [HoldingDO('2019-01-01', 10.0, 0.1, 5.0, {'s2': 5.0})],
                            HoldingDO('2019-01-01', 10.0, 0.1, 5.0, {'s2': 5.0}))

    dic = portfolio.convert_2_dict()

    print(dic)

    port = PortfolioDO.convert_from_dict(dic)
    print(port.date_format)
