import numpy as np
import pandas as pd

def sharpe_ratio(returns, periods=255):
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def drawdowns(pnl): #pnl is panda series *** as a percentage
    high_water_mark = [0]
    idx = pnl.index
    drawdown = pd.Series(index = idx)
    duration = pd.Series(index = idx)

    for percent in range(1, len(idx)):
        high_water_mark.append(max(high_water_mark[percent-1], pnl[percent]))
        drawdown[percent] = high_water_mark[percent] - pnl[percent]
        duration[percent] = (0 if drawdown[percent] == 0 else duration[percent-1] +1)
    return drawdown, max(drawdown), max(duration)


