# Practice
This is a package of different attempts.

Run with joinquant.

local back-testing framework developing...


# ETFs Rotation
This strategy is a quantitative investment strategy based on ETF rotation, aiming to select the best-performing ETFs for investment by calculating their historical price momentum, while managing drawdown risks through risk control mechanisms to achieve stable returns. The strategy targets an annualized return of approximately 20%-30%, with a maximum drawdown controlled within 18%.

The strategy selects eight ETFs as investment targets, including the ChiNext ETF, SSE 180 ETF, Gold ETF, Nasdaq ETF, Nasdaq Technology ETF, CSI 1000 ETF, S&P 500 ETF, and Sci-Tech Innovation 100 ETF. These ETFs cover different markets and asset classes, aiming to diversify risks through diversified investments.

The calculation of the momentum factor takes into account several aspects:
- **Base Momentum**: Calculated through linear regression to determine the ETF's annualized return and R² value.
- **Risk Adjustment**: Adjusts the impact of volatility on returns by calculating the Sharpe ratio.
- **Multi-Period Momentum**: Calculates short-term (5-day) and medium-term (10-day) momentum.
- **Volume Trend**: Calculates the recent changes in trading volume.

These factors are weighted and summed to obtain a comprehensive score for each ETF, with the highest-scoring ETFs being selected as investment targets.

In terms of trading logic, the strategy checks trading signals daily and adjusts positions weekly:
- **Buying Logic**: Selects the highest-scoring ETFs for investment. If the currently held ETFs are not on the target list, they are sold. If the target ETFs are on the suspension list, buying is skipped.
- **Selling Logic**: Sells currently held ETFs that are not on the target list. If an ETF triggers the risk control mechanism, it is sold and trading is suspended for a period.

The risk control mechanism includes:
- **Maximum Drawdown Threshold**: Set at 5%, triggering risk control when the daily drawdown exceeds this threshold.
- **Suspension Period**: If an ETF triggers risk control, trading of the ETF is suspended for a period (10 days).
- **Daily Drawdown Check**: The strategy checks the drawdown of the held ETFs daily, and if the drawdown exceeds the threshold, a sell order is executed.

To better monitor and manage the investment process, the strategy records daily trading signals, position status, risk check results, and other information, and sends these details to a designated group via a DingTalk robot, enabling investors to stay informed about their investment status and make timely decisions.


# Multi-factor

#### Initialization
- **Basic Setup**: Define the benchmark as CSI 300 Index (`000300.XSHG`), enable real price trading, and set order costs.
- **Strategy Parameters**: Set the number of stocks to hold (`g.stock_num = 30`), rebalancing cycle (`g.rebalance_days = 10`), and initialize the last rebalance date.
- **Scheduled Tasks**: Schedule daily tasks for market open trading logic (`market_open`) and limit-up check (`check_limit_up`).

#### Market Open Logic
- **Rebalancing Check**: Determine if the rebalancing cycle has passed since the last rebalance.
- **Stock Selection**: Call `get_stock_list` to obtain a list of target stocks based on predefined criteria.
- **Portfolio Adjustment**: Call `rebalance_portfolio` to adjust the portfolio by selling non-target stocks and buying new ones.
- **Update Last Rebalance Date**: Update the last rebalance date to the current date.

#### Stock Selection
- **Initial Filtering**: Retrieve all stock securities and filter out new stocks, KCB stocks, and ST stocks.
- **Financial Criteria**: Apply financial filters (e.g., ROE > 5%, increasing revenue and net profit) and order by circulating market cap.
- **Final Selection**: Select the top `g.stock_num` stocks by market cap to form the target list.

#### Portfolio Rebalancing
- **Sell Non-Target Stocks**: Liquidate positions that are not in the target list.
- **Calculate Target Positions**: Determine the target value for each stock based on the total portfolio value and number of stocks.
- **Buy New Stocks**: Allocate funds to new stocks up to the target number, ensuring the portfolio is balanced.

#### Limit-Up Monitoring
- **Identify Limit-Up Stocks**: Check for stocks that hit the upper limit the previous day and store them in `g.high_limit_list`.
- **Avoid Buying Limit-Up Stocks**: Prevent buying stocks that are likely to be less liquid or have limited trading opportunities.

#### Helper Functions
- **Filter New Stocks**: Exclude recently listed stocks to avoid high volatility and uncertainty.
- **Filter KCB and ST Stocks**: Remove stocks from the KCB board and those marked as ST to focus on more stable investments.


# Low PE High DY 

- **Stock Selection**
  - Exclude stocks from the Science and Technology Innovation Board (STAR Market) and the Beijing Stock Exchange, as well as ST stocks and newly listed stocks (less than 300 trading days).
  - Select the top 10% of stocks with the highest average dividend yield over the past three years.
  - Filter stocks based on:
    - PE ratio between 0 and 20.
    - ROE greater than 3%.
    - Year-over-year increase in total revenue greater than 5%.
    - Year-over-year increase in net profit greater than 11%.
    - PEG ratio between 0.08 and 2.
  - Exclude suspended and limit-up stocks from the previous day, and select the top 10 stocks as the buy pool.

- **Trading Execution**
  - Rebalance the portfolio once a month on the first trading day at the market open.
  - Sell stocks not in the final selection and those that were limit-up the previous day but not on the current day.
  - Buy the top 10 selected stocks, distributing available cash evenly.

- **Risk Management**
  - Daily check and sell stocks that were limit-up the previous day but not on the current day.
  - Strictly limit the number of holdings to 10 stocks.

- **Strategy Characteristics**
  - Focuses on stability and steady growth, suitable for conservative investors.
  - Emphasizes dividend income, low PE ratios, and growth potential.
