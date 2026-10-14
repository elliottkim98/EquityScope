def sma(values, period=20):
    if period < 1:
        raise ValueError('period must be positive')
    return [None if i < period - 1 else sum(values[i-period+1:i+1])/period for i in range(len(values))]


def rsi(values, period=14):
    if period < 1:
        raise ValueError('period must be positive')
    if len(values) <= period:
        return None
    differences = [b-a for a, b in zip(values, values[1:])]
    gain = sum(max(d, 0) for d in differences[:period])/period
    loss = sum(max(-d, 0) for d in differences[:period])/period
    for d in differences[period:]:
        gain = (gain*(period-1)+max(d, 0))/period
        loss = (loss*(period-1)+max(-d, 0))/period
    if gain == loss == 0:
        return 50.0
    return 100.0 if loss == 0 else 100-100/(1+gain/loss)
