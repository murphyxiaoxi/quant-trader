from dao.stock_data import load_data_2_csv_file

if __name__ == '__main__':
    # less data 'SH512880'  'SZ161227'

    symbols = ['SH510300', 'SH510500', 'SH510050',
               'SZ159902', 'SH510880', 'SZ159928',
               'SZ159903']

    load_data_2_csv_file(symbols, '19900101', '20150101', '-etf-end-2015.csv')
