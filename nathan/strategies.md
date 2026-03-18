# Strategies Brainstorm

1. Cross-sectional Momentum
Rank stocks by recent return. Buy the strongest and short the weakest.

2. Time Series Momentum
For each stock independently, use signals like moving average crossover, breakout, and past k-day return.

3. Pairs Trading
Check for pairs with high cointegration and trade means reversion.

Also can model one stock relative to a small basket using regression residuals, and then trade the residual spread.

4. Regression
Just dump everything in a regression model and make sure to do dimensionality reduction to avoid overfitting

5. Volatility & Volume based strategies
I don't know too much here.

6. Regime-filtered
Detect market regime from the cross-section or average index-like basket trend/volatility. 
Then switch between momentum and mean-reversion behavior.