# Momentum-vs-MeanReversion-4-asset-strategy-backtester
Momentum vs Mean Reversion backtest on S&amp;P 500, Nasdaq, Gold, and 30-Year Bonds (2021-2026)
# Momentum vs Mean Reversion Backtester

## Overview
This project backtests two systematic trading strategies on a 4-asset portfolio:
- **S&P 500**
- **Nasdaq**  
- **Gold**
- **30-Year Bonds**

## Strategies
| Strategy | Description |
|----------|-------------|
| Momentum | Buy when price > 50-day moving average |
| Mean Reversion | Buy when z-score < -0.5 (oversold) |

## Results
| Strategy | Total Return | Sharpe Ratio | Max Drawdown |
|----------|-------------|--------------|---------------|
| Momentum | 46.6% | 1.56 | -5.9% |
| Mean Reversion | 26.8% | 1.03 | -5.9% |
| Buy & Hold | 65.9% | 1.42 | -14.2% |

## Key Finding
Momentum delivered strong risk-adjusted returns (Sharpe 1.56) with only -5.9% drawdown, significantly better than Buy & Hold's -14.2% drawdown.

## Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib

## How to Run
1. Install dependencies: `pip install pandas numpy matplotlib`
2. Download CSV files (S&P 500, Nasdaq, Gold, 30-Year Bonds)
3. Update file paths in the code
4. Run the script
