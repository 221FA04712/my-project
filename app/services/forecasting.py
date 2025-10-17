from typing import List


def _linear_regression_predict(y: List[float], steps_ahead: int) -> List[float]:
    n = len(y)
    if n == 0:
        return [0.0] * steps_ahead
    if n == 1:
        return [y[0]] * steps_ahead

    # x are 0..n-1
    x_sum = (n - 1) * n / 2
    x2_sum = (n - 1) * n * (2 * n - 1) / 6
    y_sum = sum(y)
    xy_sum = sum(i * y[i] for i in range(n))

    denom = n * x2_sum - x_sum * x_sum
    if denom == 0:
        slope = 0.0
    else:
        slope = (n * xy_sum - x_sum * y_sum) / denom
    intercept = (y_sum - slope * x_sum) / n

    return [max(0.0, intercept + slope * (n + k)) for k in range(steps_ahead)]


def forecast_series(period_labels: List[str], values: List[float], steps_ahead: int) -> List[float]:
    # period_labels unused in pure-Python version; retained for API stability
    return _linear_regression_predict(values, steps_ahead)


def estimate_department_future_impact(values: List[float], steps_ahead: int) -> float:
    future = _linear_regression_predict(values, steps_ahead)
    return float(sum(future))
