from typing import Dict, List, Any

from backend.commons.enums.date_format_enums import DateFormatStrEnum


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
    def convert_from_dict(dic: Dict[str, Any]):
        return PositionDO(
            PositionDO._get(dic, 'date_str'),
            PositionDO._get(dic, 'symbol_position')
        )

    @staticmethod
    def _get(dic: Dict[str, Any], k: str):
        return dic[k] if k in dic else None


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
    def convert_from_dict(dic: Dict[str, Any]):
        return HoldingDO(
            HoldingDO._get(dic, 'date_str'),
            HoldingDO._get(dic, 'cash'),
            HoldingDO._get(dic, 'commission'),
            HoldingDO._get(dic, 'total'),
            HoldingDO._get(dic, 'symbol_hold')
        )

    @staticmethod
    def _get(dic: Dict[str, Any], k: str):
        return dic[k] if k in dic else None


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
    def convert_from_dict(dic: Dict[str, Any]):
        return PortfolioDO(
            PortfolioDO._get(dic, 'portfolio_id'),
            PortfolioDO._get(dic, 'name'),
            PortfolioDO._get(dic, 'description'),
            PortfolioDO._get(dic, 'start_date_str'),
            DateFormatStrEnum.convert_from_value(PortfolioDO._get(dic, 'date_format')),
            PortfolioDO._get(dic, 'symbol_list'),
            PortfolioDO._get(dic, 'initial_capital'),
            PortfolioDO._parse_all_position(dic),
            PortfolioDO._parse_current_position(dic),
            PortfolioDO._parse_all_holding(dic),
            PortfolioDO._parse_current_holding(dic)
        )

    @staticmethod
    def _get(dic: Dict[str, Any], k: str):
        return dic[k] if k in dic else None

    @staticmethod
    def _parse_all_position(dic: Dict[str, Any]):
        tmp_list = PortfolioDO._get(dic, 'all_position')
        if tmp_list is None:
            return None
        else:
            return [PositionDO.convert_from_dict(item) for item in tmp_list]

    @staticmethod
    def _parse_current_position(dic:Dict[str, Any]):
        m = PortfolioDO._get(dic, 'current_position')
        if m is None:
            return None
        else:
            return PositionDO.convert_from_dict(m)

    @staticmethod
    def _parse_all_holding(dic:Dict[str, Any]):
        tmp_list = PortfolioDO._get(dic, 'all_holding')
        if tmp_list is None:
            return None
        else:
            return [HoldingDO.convert_from_dict(item) for item in tmp_list]

    @staticmethod
    def _parse_current_holding(dic:Dict[str, Any]):
        m = PortfolioDO._get(dic, 'current_holding')
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
