import pandas as pd
from jqdata import *

def initialize(context):
    set_benchmark('000300.XSHG')
    log.set_level('order', 'error')
    set_option('use_real_price', True)
    set_option('avoid_future_data', True)
    set_slippage(FixedSlippage(0.02))
    g.stock_num = 10
    g.month = context.current_dt.month - 1

def before_trading_start(context):
    prepare_stock_list(context)
    print(context.run_params.type)

def handle_data(context, data):
    hour = context.current_dt.hour
    minute = context.current_dt.minute
    if context.current_dt.month != g.month and hour == 9 and minute == 30:
        my_Trader(context)
        g.month = context.current_dt.month
    if hour == 14 and minute == 0:
        check_limit_up(context)
    record(cash=context.portfolio.available_cash / context.portfolio.total_value * 100)

def my_Trader(context):
    dt_last = context.previous_date
    stocks = get_all_securities('stock', dt_last).index.tolist()
    stocks = filter_kcbj_stock(stocks)
    stocks = filter_st_stock(stocks)
    stocks = filter_new_stock(context, stocks)
    stocks = choice_try_A(context, stocks)
    stocks = filter_paused_stock(stocks)
    stocks = filter_limit_stock(context, stocks)[:g.stock_num]
    cdata = get_current_data()
    slist(context, stocks)
    for s in context.portfolio.positions:
        if s not in stocks and cdata[s].last_price < cdata[s].high_limit:
            log.info('Sell', s, cdata[s].name)
            order_target(s, 0)
    position_count = len(context.portfolio.positions)
    if g.stock_num > position_count:
        psize = context.portfolio.available_cash / (g.stock_num - position_count)
        for s in stocks:
            if s not in context.portfolio.positions:
                log.info('buy', s, cdata[s].name)
                order_value(s, psize)
                if len(context.portfolio.positions) == g.stock_num:
                    break

def slist(context, stock_list):
    current_data = get_current_data()
    for stock in stock_list:
        df = get_fundamentals(query(valuation).filter(valuation.code == stock))
        print('股票代码：{0},  名称：{1},  总市值:{2:.2f},  流通市值:{3:.2f},  PE:{4:.2f},股价：{5:.2f}'.format(stock, get_security_info(stock).display_name, df['market_cap'][0], df['circulating_market_cap'][0], df['pe_ratio'][0], current_data[stock].last_price))

def prepare_stock_list(context):
    g.hold_list = []
    g.high_limit_list = []
    for position in list(context.portfolio.positions.values()):
        stock = position.security
        g.hold_list.append(stock)
    if g.hold_list != []:
        for stock in g.hold_list:
            df = get_price(stock, end_date=context.previous_date, frequency='daily', fields=['close', 'high_limit'], count=1)
            if df['close'][0] >= df['high_limit'][0] * 0.98:
                g.high_limit_list.append(stock)

def check_limit_up(context):
    now_time = context.current_dt
    if g.high_limit_list != []:
        for stock in g.high_limit_list:
            current_data = get_current_data()
            if current_data[stock].last_price < current_data[stock].high_limit:
                log.info("[%s]涨停打开，卖出" % (stock))
                order_target(stock, 0)
            else:
                log.info("[%s]涨停，继续持有" % (stock))

def filter_kcbj_stock(stock_list):
    for stock in stock_list[:]:
        if stock[0] == '4' or stock[0] == '8' or stock[:2] == '68':
            stock_list.remove(stock)
    return stock_list

def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]

def filter_st_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].is_st and 'ST' not in current_data[stock].name and '*' not in current_data[stock].name and '退' not in current_data[stock].name]

def filter_limit_stock(context, stock_list):
    last_prices = history(1, unit='1m', field='close', security_list=stock_list)
    current_data = get_current_data()
    return [stock for stock in stock_list if stock in context.portfolio.positions.keys() or current_data[stock].low_limit < last_prices[stock][-1] < current_data[stock].high_limit]

def get_dividend_ratio_filter_list(context, stock_list, sort, p1, p2):
    time1 = context.previous_date
    time0 = time1 - datetime.timedelta(days=365 * 3)
    interval = 1000
    list_len = len(stock_list)
    q = query(finance.STK_XR_XD.code, finance.STK_XR_XD.a_registration_date, finance.STK_XR_XD.bonus_amount_rmb).filter(finance.STK_XR_XD.a_registration_date >= time0, finance.STK_XR_XD.a_registration_date <= time1, finance.STK_XR_XD.code.in_(stock_list[:min(list_len, interval)]))
    df = finance.run_query(q)
    if list_len > interval:
        df_num = list_len // interval
        for i in range(df_num):
            q = query(finance.STK_XR_XD.code, finance.STK_XR_XD.a_registration_date, finance.STK_XR_XD.bonus_amount_rmb).filter(finance.STK_XR_XD.a_registration_date >= time0, finance.STK_XR_XD.a_registration_date <= time1, finance.STK_XR_XD.code.in_(stock_list[interval * (i + 1):min(list_len, interval * (i + 2))]))
            temp_df = finance.run_query(q)
            df = df.append(temp_df)
    dividend = df.fillna(0)
    dividend = dividend.groupby('code').sum()
    temp_list = list(dividend.index)
    q = query(valuation.code, valuation.market_cap).filter(valuation.code.in_(temp_list))
    cap = get_fundamentals(q, date=time1)
    cap = cap.set_index('code')
    cap['dividend_ratio'] = (dividend['bonus_amount_rmb'] / 10000) / cap['market_cap']
    cap = cap.sort_values(by=['dividend_ratio'], ascending=sort)
    final_list = list(cap.index)[int(p1 * len(cap)):int(p2 * len(cap))]
    return final_list

def filter_new_stock(context, stock_list):
    return [stock for stock in stock_list if (context.previous_date - datetime.timedelta(days=300)) > get_security_info(stock).start_date]

def choice_try_A(context, stocks):
    stocks = get_dividend_ratio_filter_list(context, stocks, False, 0, 0.1)
    df = get_fundamentals(query(valuation.code, valuation.circulating_market_cap).filter(valuation.code.in_(stocks), valuation.pe_ratio.between(0, 25), indicator.inc_return > 3, indicator.inc_total_revenue_year_on_year > 5, indicator.inc_net_profit_year_on_year > 11, valuation.pe_ratio / indicator.inc_net_profit_year_on_year > 0.08, valuation.pe_ratio / indicator.inc_net_profit_year_on_year < 1.9))
    stocks = list(df.code)
    print("分红比率筛选后的股票有：{}".format(len(stocks)))
    return stocks
