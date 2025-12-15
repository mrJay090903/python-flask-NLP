import pandas as pd

def records_to_dataframe(records):
    rows = [r.to_dict() for r in records]
    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df['recorded_at'] = pd.to_datetime(df['recorded_at'])
    return df


def timeseries_aggregate(df, freq='D'):
    if df.empty:
        return df

    ts = df.set_index('recorded_at').resample(freq)['value'].sum().reset_index()
    return ts


def moving_average(df, window=3):
    if df.empty:
        return df

    df = df.copy()
    df['ma'] = df['value'].rolling(window=window).mean()
    return df
