import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ========== LOAD FILES ==========
sp500 = pd.read_csv('sp500.csv', encoding='utf-8-sig')
nasdaq = pd.read_csv('nasdaq.csv', encoding='utf-8-sig')
gold = pd.read_csv('gold.csv', encoding='utf-8-sig')
bonds = pd.read_csv('DGS30.csv', encoding='utf-8-sig')

# ========== CLEAN PRICE COLUMNS (remove commas and convert to float) ==========
sp500['Price'] = sp500['Price'].astype(str).str.replace(',', '').astype(float)
nasdaq['Price'] = nasdaq['Price'].astype(str).str.replace(',', '').astype(float)
gold['Price'] = gold['Price'].astype(str).str.replace(',', '').astype(float)

# ========== REVERSE DATES (your data has newest first) ==========
sp500 = sp500.iloc[::-1].reset_index(drop=True)
nasdaq = nasdaq.iloc[::-1].reset_index(drop=True)
gold = gold.iloc[::-1].reset_index(drop=True)

# ========== BONDS: convert yield to price ==========
bonds['Date'] = pd.to_datetime(bonds['observation_date'])
bonds['Yield'] = bonds['DGS30'].astype(float)
bonds['Price'] = 100.0  # start at 100
for i in range(1, len(bonds)):
    bonds.loc[i, 'Price'] = bonds.loc[i-1, 'Price'] * (1 - (bonds.loc[i, 'Yield'] - bonds.loc[i-1, 'Yield']) * 10)

# ========== CALCULATE DAILY RETURNS ==========
sp500['Return'] = sp500['Price'].pct_change()
nasdaq['Return'] = nasdaq['Price'].pct_change()
gold['Return'] = gold['Price'].pct_change()
bonds['Return'] = bonds['Price'].pct_change()

# ========== MOMENTUM STRATEGY ==========
def momentum(prices, window=50):
    ma = prices.rolling(window).mean()
    signal = (prices > ma).astype(int).shift(1)
    return signal.fillna(0)

# ========== MEAN REVERSION STRATEGY ==========
def mean_reversion(prices, window=20, threshold=0.5):
    mean = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    zscore = (prices - mean) / std
    signal = (zscore < -threshold).astype(int).shift(1)
    return signal.fillna(0)

# ========== APPLY STRATEGIES ==========
sp500['Mom'] = momentum(sp500['Price']) * sp500['Return']
nasdaq['Mom'] = momentum(nasdaq['Price']) * nasdaq['Return']
gold['Mom'] = momentum(gold['Price']) * gold['Return']
bonds['Mom'] = momentum(bonds['Price']) * bonds['Return']

sp500['Rev'] = mean_reversion(sp500['Price']) * sp500['Return']
nasdaq['Rev'] = mean_reversion(nasdaq['Price']) * nasdaq['Return']
gold['Rev'] = mean_reversion(gold['Price']) * gold['Return']
bonds['Rev'] = mean_reversion(bonds['Price']) * bonds['Return']

# ========== PORTFOLIOS (equal weight) ==========
momentum_port = (sp500['Mom'] + nasdaq['Mom'] + gold['Mom'] + bonds['Mom']) / 4
reversion_port = (sp500['Rev'] + nasdaq['Rev'] + gold['Rev'] + bonds['Rev']) / 4
buyhold_port = (sp500['Return'] + nasdaq['Return'] + gold['Return'] + bonds['Return']) / 4

# Drop NaN values
momentum_port = momentum_port.dropna()
reversion_port = reversion_port.dropna()
buyhold_port = buyhold_port.dropna()

# ========== CALCULATE METRICS ==========
def total_return(returns):
    return (1 + returns).prod() - 1

def sharpe_ratio(returns):
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * (252 ** 0.5)

def max_drawdown(returns):
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

# ========== PRINT RESULTS ==========
print("\n" + "="*60)
print("MOMENTUM vs MEAN REVERSION vs BUY & HOLD")
print("="*60)
print(f"{'Strategy':<20} {'Total Return':<15} {'Sharpe Ratio':<15} {'Max Drawdown':<15}")
print("-"*65)
print(f"{'Momentum':<20} {total_return(momentum_port):>10.1%}      {sharpe_ratio(momentum_port):>10.2f}      {max_drawdown(momentum_port):>10.1%}")
print(f"{'Mean Reversion':<20} {total_return(reversion_port):>10.1%}      {sharpe_ratio(reversion_port):>10.2f}      {max_drawdown(reversion_port):>10.1%}")
print(f"{'Buy & Hold':<20} {total_return(buyhold_port):>10.1%}      {sharpe_ratio(buyhold_port):>10.2f}      {max_drawdown(buyhold_port):>10.1%}")
# CHECK DATA ORDER
# ========== TEST MOMENTUM LOGIC ==========
test_price = sp500['Price']
test_ma = test_price.rolling(50).mean()
test_signal = (test_price > test_ma).astype(int)

print("=== MOMENTUM TEST ===")
print(f"Total days where Price > MA: {test_signal.sum()}")
print(f"Total days where Price <= MA: {len(test_signal) - test_signal.sum()}")
print(f"\nFirst 10 comparisons:")
for i in range(10):
    print(f"Day {i}: Price={test_price.iloc[i]:.2f}, MA={test_ma.iloc[i]:.2f}, Signal={test_signal.iloc[i]}")

print(f"Moemntum signal found:{(momentum_port !=0).sum()} days")
# ========== PLOT ==========
plt.figure(figsize=(12, 6))
plt.plot((1 + momentum_port).cumprod(), label='Momentum', linewidth=2)
plt.plot((1 + reversion_port).cumprod(), label='Mean Reversion', linewidth=2)
plt.plot((1 + buyhold_port).cumprod(), label='Buy & Hold', linewidth=2, alpha=0.7)
plt.title('Momentum vs Mean Reversion vs Buy & Hold (4-Asset Portfolio)', fontsize=14)
plt.xlabel('Trading Days (since 2021)', fontsize=12)
plt.ylabel('Cumulative Return ($1 invested)', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('strategy_comparison.png', dpi=100)
plt.show()

print("\n✓ Chart saved as 'strategy_comparison.png'")
print("\n✓ Project complete! Add this to your CV.")

# ==================================================================
# TECHNICAL NOTE:
# The following code sets up the file path because PyScripter on my
# system doesn't recognize CSV files without explicit path declaration.
#
# If you run this on your machine, replace the path with your own.
# The actual strategy implementation starts after this section.
# ==================================================================


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
os.chdir(r"C:\Users\USER\Downloads")  # CHANGE THIS TO YOUR FOLDER PATH
print("Current working directory:", os.getcwd())


# ========== LOAD FILES ==========
sp500 = pd.read_csv('sp500.csv', encoding='utf-8-sig')
nasdaq = pd.read_csv('nasdaq.csv', encoding='utf-8-sig')
gold = pd.read_csv('gold.csv', encoding='utf-8-sig')
bonds = pd.read_csv('DGS30.csv', encoding='utf-8-sig')

# ========== CLEAN PRICE COLUMNS (remove commas and convert to float) ==========
sp500['Price'] = sp500['Price'].astype(str).str.replace(',', '').astype(float)
nasdaq['Price'] = nasdaq['Price'].astype(str).str.replace(',', '').astype(float)
gold['Price'] = gold['Price'].astype(str).str.replace(',', '').astype(float)

# ========== ADD DATE COLUMNS ==========
sp500['Date'] = pd.to_datetime(sp500['Date'])
nasdaq['Date'] = pd.to_datetime(nasdaq['Date'])
gold['Date'] = pd.to_datetime(gold['Date'])

# ========== REVERSE DATES (your data has newest first) ==========
sp500 = sp500.iloc[::-1].reset_index(drop=True)
nasdaq = nasdaq.iloc[::-1].reset_index(drop=True)
gold = gold.iloc[::-1].reset_index(drop=True)

# ========== BONDS (SIMPLIFIED - no loop) ==========
bonds['Date'] = pd.to_datetime(bonds['observation_date'])
bonds['Yield'] = bonds['DGS30'].astype(float)
bonds['Return'] = -bonds['Yield'].diff() / 100
bonds['Price'] = 100 + bonds['Return'].cumsum()
bonds['Price'] = bonds['Price'].fillna(100)

# ========== CALCULATE DAILY RETURNS ==========
sp500['Return'] = sp500['Price'].pct_change()
nasdaq['Return'] = nasdaq['Price'].pct_change()
gold['Return'] = gold['Price'].pct_change()
# bonds already has Return

# ========== MEAN REVERSION ==========
window_mr = 20
threshold = 0.5

# Calculate z-scores
sp500_mean = sp500['Price'].rolling(window_mr).mean()
sp500_std = sp500['Price'].rolling(window_mr).std()
sp500_zscore = (sp500['Price'] - sp500_mean) / sp500_std

nasdaq_mean = nasdaq['Price'].rolling(window_mr).mean()
nasdaq_std = nasdaq['Price'].rolling(window_mr).std()
nasdaq_zscore = (nasdaq['Price'] - nasdaq_mean) / nasdaq_std

gold_mean = gold['Price'].rolling(window_mr).mean()
gold_std = gold['Price'].rolling(window_mr).std()
gold_zscore = (gold['Price'] - gold_mean) / gold_std

bonds_mean = bonds['Price'].rolling(window_mr).mean()
bonds_std = bonds['Price'].rolling(window_mr).std()
bonds_zscore = (bonds['Price'] - bonds_mean) / bonds_std

# Generate signals (buy when z-score < -threshold)
sp500_rev_signal = (sp500_zscore < -threshold).astype(int).shift(1).fillna(0)
nasdaq_rev_signal = (nasdaq_zscore < -threshold).astype(int).shift(1).fillna(0)
gold_rev_signal = (gold_zscore < -threshold).astype(int).shift(1).fillna(0)
bonds_rev_signal = (bonds_zscore < -threshold).astype(int).shift(1).fillna(0)

# Calculate returns
sp500_rev_return = sp500_rev_signal * sp500['Return']
nasdaq_rev_return = nasdaq_rev_signal * nasdaq['Return']
gold_rev_return = gold_rev_signal * gold['Return']
bonds_rev_return = bonds_rev_signal * bonds['Return']

# Fill NaN
sp500_rev_return = sp500_rev_return.fillna(0)
nasdaq_rev_return = nasdaq_rev_return.fillna(0)
gold_rev_return = gold_rev_return.fillna(0)
bonds_rev_return = bonds_rev_return.fillna(0)

# Portfolio
reversion_port = (sp500_rev_return + nasdaq_rev_return + gold_rev_return + bonds_rev_return) / 4
reversion_port = reversion_port.iloc[50:]

print(f"\n✓ Mean Reversion portfolio created")
print(f"  Days with active trades: {(reversion_port != 0).sum()}")
print(f"  Mean Reversion total return: {(1 + reversion_port).prod() - 1:.1%}")

# ========== MEAN REVERSION STRATEGY (threshold=0.5) ==========
def mean_reversion(prices, window=20, threshold=0.5):
    mean = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    zscore = (prices - mean) / std
    signal = (zscore < -threshold).astype(int).shift(1)
    return signal.fillna(0)

# ========== APPLY STRATEGIES ==========
sp500['Mom'] = momentum(sp500['Price']) * sp500['Return']
nasdaq['Mom'] = momentum(nasdaq['Price']) * nasdaq['Return']
gold['Mom'] = momentum(gold['Price']) * gold['Return']
bonds['Mom'] = momentum(bonds['Price']) * bonds['Return']

sp500['Rev'] = mean_reversion(sp500['Price']) * sp500['Return']
nasdaq['Rev'] = mean_reversion(nasdaq['Price']) * nasdaq['Return']
gold['Rev'] = mean_reversion(gold['Price']) * gold['Return']
bonds['Rev'] = mean_reversion(bonds['Price']) * bonds['Return']

# ========== PORTFOLIOS (equal weight) ==========
momentum_port = (sp500['Mom'] + nasdaq['Mom'] + gold['Mom'] + bonds['Mom']) / 4
reversion_port = (sp500['Rev'] + nasdaq['Rev'] + gold['Rev'] + bonds['Rev']) / 4
buyhold_port = (sp500['Return'] + nasdaq['Return'] + gold['Return'] + bonds['Return']) / 4

# Drop NaN values
momentum_port = momentum_port.dropna()
reversion_port = reversion_port.dropna()
buyhold_port = buyhold_port.dropna()

# Get dates for x-axis (same length as portfolios)
plot_dates = sp500['Date'].iloc[1:len(momentum_port)+1]

# ========== CALCULATE METRICS ==========
def total_return(returns):
    return (1 + returns).prod() - 1

def sharpe_ratio(returns):
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * (252 ** 0.5)

def max_drawdown(returns):
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

# ========== PRINT RESULTS ==========
print("\n" + "="*60)
print("MOMENTUM vs MEAN REVERSION vs BUY & HOLD")
print("="*60)
print(f"{'Strategy':<20} {'Total Return':<15} {'Sharpe Ratio':<15} {'Max Drawdown':<15}")
print("-"*65)
print(f"{'Momentum (50d)':<20} {total_return(momentum_port):>10.1%}      {sharpe_ratio(momentum_port):>10.2f}      {max_drawdown(momentum_port):>10.1%}")
print(f"{'Mean Reversion (0.5)':<20} {total_return(reversion_port):>10.1%}      {sharpe_ratio(reversion_port):>10.2f}      {max_drawdown(reversion_port):>10.1%}")
print(f"{'Buy & Hold':<20} {total_return(buyhold_port):>10.1%}      {sharpe_ratio(buyhold_port):>10.2f}      {max_drawdown(buyhold_port):>10.1%}")

# ========== PLOT WITH YEARS ON X-AXIS ==========
plt.figure(figsize=(12, 6))

# Calculate cumulative returns
mom_cum = (1 + momentum_port).cumprod()
rev_cum = (1 + reversion_port).cumprod()
bh_cum = (1 + buyhold_port).cumprod()

# Plot with dates
plt.plot(plot_dates, mom_cum, label='Momentum (50-day)', linewidth=2, color='blue')
plt.plot(plot_dates, rev_cum, label='Mean Reversion (threshold 0.5)', linewidth=2, color='orange')
plt.plot(plot_dates, bh_cum, label='Buy & Hold', linewidth=2, color='green', alpha=0.7)

plt.title('Momentum vs Mean Reversion vs Buy & Hold (4-Asset Portfolio)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Cumulative Return ($1 invested)', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)

# Format x-axis to show years (2021, 2022, 2023, 2024, 2025, 2026)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.savefig('strategy_comparison.png', dpi=100)
plt.show()

print("\n✓ Chart saved as 'strategy_comparison.png'")
print("\n✓ Project complete! Add this to your CV.")

# ========== BREAKDOWN BY ASSET ==========
print("\n" + "="*70)
print("PERFORMANCE BY ASSET (Momentum Strategy)")
print("="*70)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ========== LOAD FILES ==========
sp500 = pd.read_csv('sp500.csv', encoding='utf-8-sig')
nasdaq = pd.read_csv('nasdaq.csv', encoding='utf-8-sig')
gold = pd.read_csv('gold.csv', encoding='utf-8-sig')
bonds = pd.read_csv('DGS30.csv', encoding='utf-8-sig')

# ========== CLEAN PRICES ==========
sp500['Price'] = sp500['Price'].astype(str).str.replace(',', '').astype(float)
nasdaq['Price'] = nasdaq['Price'].astype(str).str.replace(',', '').astype(float)
gold['Price'] = gold['Price'].astype(str).str.replace(',', '').astype(float)

# ========== ADD DATES AND SORT (oldest first) ==========
sp500['Date'] = pd.to_datetime(sp500['Date'])
nasdaq['Date'] = pd.to_datetime(nasdaq['Date'])
gold['Date'] = pd.to_datetime(gold['Date'])

sp500 = sp500.iloc[::-1].reset_index(drop=True)
nasdaq = nasdaq.iloc[::-1].reset_index(drop=True)
gold = gold.iloc[::-1].reset_index(drop=True)

# ========== BONDS ==========
bonds['Date'] = pd.to_datetime(bonds['observation_date'])
bonds['Yield'] = bonds['DGS30'].astype(float)
bonds['Return'] = -bonds['Yield'].diff() / 100
bonds['Price'] = 100 + bonds['Return'].cumsum()
bonds['Price'] = bonds['Price'].fillna(100)

# ========== ALIGN DATES ==========
start_date = max(sp500['Date'].min(), nasdaq['Date'].min(), gold['Date'].min(), bonds['Date'].min())
end_date = min(sp500['Date'].max(), nasdaq['Date'].max(), gold['Date'].max(), bonds['Date'].max())

sp500 = sp500[(sp500['Date'] >= start_date) & (sp500['Date'] <= end_date)]
nasdaq = nasdaq[(nasdaq['Date'] >= start_date) & (nasdaq['Date'] <= end_date)]
gold = gold[(gold['Date'] >= start_date) & (gold['Date'] <= end_date)]
bonds = bonds[(bonds['Date'] >= start_date) & (bonds['Date'] <= end_date)]

# ========== CALCULATE RETURNS ==========
sp500['Return'] = sp500['Price'].pct_change()
nasdaq['Return'] = nasdaq['Price'].pct_change()
gold['Return'] = gold['Price'].pct_change()

# ========== MOMENTUM (50-day) ==========
def momentum_strategy(prices, returns, window=50):
    ma = prices.rolling(window).mean()
    signal = (prices > ma).astype(int).shift(1).fillna(0)
    strat_return = signal * returns
    return strat_return.fillna(0)

# ========== MEAN REVERSION (threshold 0.5) ==========
def meanreversion_strategy(prices, returns, window=20, threshold=0.5):
    mean = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    zscore = (prices - mean) / std
    signal = (zscore < -threshold).astype(int).shift(1).fillna(0)
    strat_return = signal * returns
    return strat_return.fillna(0)

# ========== APPLY STRATEGIES ==========
sp500_mom = momentum_strategy(sp500['Price'], sp500['Return'])
nasdaq_mom = momentum_strategy(nasdaq['Price'], nasdaq['Return'])
gold_mom = momentum_strategy(gold['Price'], gold['Return'])
bonds_mom = momentum_strategy(bonds['Price'], bonds['Return'])

sp500_rev = meanreversion_strategy(sp500['Price'], sp500['Return'])
nasdaq_rev = meanreversion_strategy(nasdaq['Price'], nasdaq['Return'])
gold_rev = meanreversion_strategy(gold['Price'], gold['Return'])
bonds_rev = meanreversion_strategy(bonds['Price'], bonds['Return'])

# ========== PORTFOLIOS ==========
momentum_port = (sp500_mom + nasdaq_mom + gold_mom + bonds_mom) / 4
reversion_port = (sp500_rev + nasdaq_rev + gold_rev + bonds_rev) / 4
buyhold_port = (sp500['Return'].fillna(0) + nasdaq['Return'].fillna(0) + gold['Return'].fillna(0) + bonds['Return'].fillna(0)) / 4

# Remove first 50 days
momentum_port = momentum_port.iloc[50:]
reversion_port = reversion_port.iloc[50:]
buyhold_port = buyhold_port.iloc[50:]

# ========== INDIVIDUAL ASSET PERFORMANCE ==========
print("\n" + "="*60)
print("INDIVIDUAL ASSET PERFORMANCE")
print("="*60)

sp500_mom_return = (1 + sp500_mom.iloc[50:]).prod() - 1
nasdaq_mom_return = (1 + nasdaq_mom.iloc[50:]).prod() - 1
gold_mom_return = (1 + gold_mom.iloc[50:]).prod() - 1
bonds_mom_return = (1 + bonds_mom.iloc[50:]).prod() - 1

print("\n--- MOMENTUM STRATEGY ---")
print(f"S&P 500: {sp500_mom_return:.1%}")
print(f"Nasdaq: {nasdaq_mom_return:.1%}")
print(f"Gold: {gold_mom_return:.1%}")
print(f"Bonds: {bonds_mom_return:.1%}")

sp500_bh_return = (1 + sp500['Return'].iloc[50:].fillna(0)).prod() - 1
nasdaq_bh_return = (1 + nasdaq['Return'].iloc[50:].fillna(0)).prod() - 1
gold_bh_return = (1 + gold['Return'].iloc[50:].fillna(0)).prod() - 1
bonds_bh_return = (1 + bonds['Return'].iloc[50:].fillna(0)).prod() - 1

print("\n--- BUY & HOLD ---")
print(f"S&P 500: {sp500_bh_return:.1%}")
print(f"Nasdaq: {nasdaq_bh_return:.1%}")
print(f"Gold: {gold_bh_return:.1%}")
print(f"Bonds: {bonds_bh_return:.1%}")

# ========== PORTFOLIO RESULTS ==========
def sharpe(returns):
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * (252 ** 0.5)

def max_dd(returns):
    cum = (1 + returns).cumprod()
    peak = cum.expanding().max()
    dd = (cum - peak) / peak
    return dd.min()

print("\n" + "="*60)
print("PORTFOLIO RESULTS (4-Asset Equal Weight)")
print("="*60)
print(f"{'Strategy':<18} {'Total Return':<14} {'Sharpe':<10} {'Max DD':<10}")
print("-"*55)
print(f"{'Momentum':<18} {(1 + momentum_port).prod() - 1:>11.1%}    {sharpe(momentum_port):>8.2f}    {max_dd(momentum_port):>9.1%}")
print(f"{'Mean Reversion':<18} {(1 + reversion_port).prod() - 1:>11.1%}    {sharpe(reversion_port):>8.2f}    {max_dd(reversion_port):>9.1%}")
print(f"{'Buy & Hold':<18} {(1 + buyhold_port).prod() - 1:>11.1%}    {sharpe(buyhold_port):>8.2f}    {max_dd(buyhold_port):>9.1%}")

