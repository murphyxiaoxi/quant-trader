import datetime

import tushare


def is_open(date: str):
    """
    是否开市
    :param date:
    :return:
    """

    pro_api = tushare.pro_api('65ff56dd66d10436614eefa5a87498c265acb97fdb8be9937c4f2d80')
    cal_df = pro_api.trade_cal(exchange='', start_date=date, end_date=date)
    cals = cal_df[cal_df['is_open'] == 1]['cal_date']
    return len(cals) > 0


def previous_trade_date(date: str):
    yesterday = datetime.datetime.strptime(date, "%Y%m%d") - datetime.timedelta(days=1)
    thirty_date = datetime.datetime.strptime(date, "%Y%m%d") - datetime.timedelta(days=15)

    pro_api = tushare.pro_api('65ff56dd66d10436614eefa5a87498c265acb97fdb8be9937c4f2d80')
    cal_df = pro_api.trade_cal(exchange='', start_date=thirty_date.strftime('%Y%m%d'),
                               end_date=yesterday.strftime('%Y%m%d'))

    cals = cal_df[cal_df['is_open'] == 1]['cal_date']
    if len(cals) == 0:
        return None
    return sorted(cals)[-1]


if __name__ == '__main__':
    print(previous_trade_date('20190404'))
