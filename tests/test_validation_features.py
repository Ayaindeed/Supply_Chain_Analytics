import pytest

from scripts.validation import validate_features_dataframe


def test_validate_features_missing_column_raises():
    pd = pytest.importorskip("pandas")
    required = ["order_month", "market_encoded", "profit_margin"]
    df = pd.DataFrame({
        "order_month": [1, 2],
        # missing market_encoded
        "profit_margin": [10.0, 20.0],
    })

    with pytest.raises(ValueError):
        validate_features_dataframe(df, required)


def test_validate_features_nan_threshold_raises():
    pd = pytest.importorskip("pandas")
    np = pytest.importorskip("numpy")
    required = ["order_month", "market_encoded", "profit_margin"]
    df = pd.DataFrame({
        "order_month": [1, 2, 3, 4],
        "market_encoded": [np.nan, np.nan, np.nan, 1],  # 75% NaNs > 1%
        "profit_margin": [10.0, 20.0, 30.0, 40.0],
    })

    with pytest.raises(ValueError):
        validate_features_dataframe(df, required)


def test_validate_features_valid_passes():
    pd = pytest.importorskip("pandas")
    required = ["order_month", "market_encoded", "profit_margin"]
    df = pd.DataFrame({
        "order_month": [1, 2, 3, 4],
        "market_encoded": [0, 1, 2, 1],
        "profit_margin": [10.0, 20.0, 30.0, 40.0],
    })

    validate_features_dataframe(df, required)
