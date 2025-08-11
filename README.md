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
```
