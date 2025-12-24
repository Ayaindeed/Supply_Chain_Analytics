import pytest

from scripts.validation import validate_raw_dataframe


def test_validate_raw_dataframe_missing_column_raises():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({
        "order_id": [1],
        # "order_item_id" missing on purpose
        "order_date_dateorders": ["2017-01-01"],
        "shipping_date_dateorders": ["2017-01-03"],
        "order_customer_id": [100],
        "order_country": ["France"],
        "sales": [10.0],
        "order_item_total": [10.0],
        "order_profit_per_order": [2.0],
    })

    with pytest.raises(ValueError):
        validate_raw_dataframe(df)


def test_validate_raw_dataframe_duplicate_pk_raises():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({
        "order_id": [1, 1],
        "order_item_id": [10, 10],
        "order_date_dateorders": ["2017-01-01", "2017-01-01"],
        "shipping_date_dateorders": ["2017-01-03", "2017-01-03"],
        "order_customer_id": [100, 100],
        "order_country": ["France", "France"],
        "sales": [10.0, 10.0],
        "order_item_total": [10.0, 10.0],
        "order_profit_per_order": [2.0, 2.0],
    })

    with pytest.raises(ValueError):
        validate_raw_dataframe(df)


def test_validate_raw_dataframe_valid_passes():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({
        "order_id": [1, 2],
        "order_item_id": [10, 20],
        "order_date_dateorders": ["2017-01-01", "2017-01-02"],
        "shipping_date_dateorders": ["2017-01-03", "2017-01-04"],
        "order_customer_id": [100, 101],
        "order_country": ["France", "Germany"],
        "sales": [10.0, 15.5],
        "order_item_total": [10.0, 15.5],
        "order_profit_per_order": [2.0, 3.0],
    })

    # Should not raise
    validate_raw_dataframe(df)
