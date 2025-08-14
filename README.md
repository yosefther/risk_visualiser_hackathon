# MVP plane 
### Core features and finance bullshit
- Data intake: CSV upload (date, open/high/low/close, volume), optional API later

- **CSV Data Upload** – Upload historical OHLCV data (Date, Open, High, Low, Close, Volume).
- **Portfolio Metrics** – Calculate:
  - Daily and annualized returns
  - Volatility (σ)
  - Sharpe ratio
  - Sortino Ratio
  - Maximum drawdown
  - Beta
  - Correlation Matrix
- **Risk Measures**:
  - Historical VaR (Value at Risk)
  - Historical CVaR (Conditional VaR)
- **Visualizations**:
  - Cumulative returns line chart
  - Drawdown chart
  - Correlation heatmap

**concepts**
``` 
volatility==> A statistical measure of how much returns vary (i.e., the standard deviation of returns)

sharpe ratio ==> measures the performance of an investment such as a security or portfolio compared to a risk-free asset, after adjusting for its risk

sharpe Ratio ==>Measures excess return per unit of risk (volatility)

maximum drawdown ==> The largest percentage drop from a peak to a trough in portfolio value

beta => Measures how much your asset moves relative to a benchmark (e.g., S&P 500)

correlation Matrix ==> A table showing the correlation coefficient between each pair of assets

Historical VaR (Value at Risk) ==> An estimate of the maximum expected loss over a given period at a certain confidence level, based on historical returns

Historical CVaR (Conditional Value at Risk) ==> The average loss given that you are already in the worst-case tail (beyond the VaR point)

Cumulative Returns Line Chart ==> A plot showing how your investment grows (or shrinks) over time if profits are reinvested

Drawdown Chart ==> A chart that tracks how far your portfolio value has fallen from its peak at any point in time

Correlation Heatmap ==> A color-coded grid showing correlations between assets in the portfolio
```
## Calculations

### **Daily Return**

$r_t = \frac{P_t}{P_{t-1}} - 1$

### **Annualized Volatility**

$\sigma_a = \sigma_d \sqrt{252}$

### **Sharpe Ratio**

$\text{Sharpe} = \frac{\mu_a - r_f}{\sigma_a}$

### **Sortino Ratio**

$\text{Sortino} = \frac{\mu_a - r_f}{\sigma_{\text{downside}}}$

### **Max Drawdown**

$\text{MDD} = \min_t \left( \frac{P_t - \max_{s \le t} P_s}{\max_{s \le t} P_s} \right)$

### **Beta**

$\beta = \frac{\text{Cov}(R_a, R_m)}{\text{Var}(R_m)}$

### **Correlation Coefficient**

$\rho_{xy} = \frac{\text{Cov}(R_x, R_y)}{\sigma_x \sigma_y}$

### **Historical VaR (95%)**

5th percentile of historical returns.

### **Historical CVaR (95%)**

Average of returns below VaR.

// todo : figure out the math + check the math latter i found it on some shady website
// note : most of the math you can find it on wikipedia


# tech stack 
- FastAPI 
- Pandas & NumPy 
- Plotly 
- SQLModel – ORM for PostgreSQL //maybe
- Uvicorn  //maybe
- data forma ==> CSV
  
Disclaimer: This is just for a hackathon so don’t take it seriously or as financial advice most of it is bullshit and I honestly have no idea what I’m doing. (:




# Disclaimer: This is just for a hackathon, so don’t take it seriously or as financial advice. Most of it is bullshit, and I honestly have no idea what I’m doing.

