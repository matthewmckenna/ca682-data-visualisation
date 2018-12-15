"""utility functions for data cleaning and visualisation"""
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_data(fpath: str, station: Dict[str, Any]) -> pd.DataFrame:
    """load a CSV file and return a pandas DataFrame"""
    df = pd.read_csv(
        fpath,
        skiprows=station['header_line_num']-1,
        usecols=['date', 'rain'],
    )

    # format the date from a string to a proper datetime object
    df['date'] = pd.to_datetime(df['date'])

    # extract year, month, week, and day to separate columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.dayofyear
    df['week'] = df['date'].dt.weekofyear

    return df


def aggregate_data(df: pd.DataFrame, timescale: str = 'day'):
    """return a DataFrame with the mean and maximum rainfall by day of year"""
    return df.groupby(timescale)['rain'].agg(['max', 'mean'])


def record_high(df, df2, agg='max'):
    """
    check if values in `df` are higher than those in `df2`.
    """
    if agg == 'max':
        return df[df['max'] > df2['max']].drop('mean', axis=1)
    elif agg == 'mean':
        return df[df['mean'] > df2['mean']].drop('max', axis=1)
    else:
        raise ValueError('unknown test')


def split_data(df: pd.DataFrame, cutoff_year: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """return last decade and historic data"""
    return df[df.year >= cutoff_year], df[df.year < cutoff_year]


def split_and_aggregate(df: pd.DataFrame, cutoff_year: int = 2008, timescale: str = 'day'):
    df1, df2 = split_data(df, cutoff_year=cutoff_year)
    return aggregate_data(df1, timescale=timescale), aggregate_data(df2, timescale=timescale)


def get_start_end_years(df: pd.DataFrame) -> Tuple[int, int]:
    """get the start and end years from a DataFrame"""
    return df.iloc[0].year, df.iloc[-1].year


def plot(
    historic: pd.DataFrame,
    last_decade: pd.DataFrame,
    rec_high: pd.DataFrame,
    aggregation: str,
    timescale: str,
    start_end_year: Tuple[int, int],
    station: str,
    county: str,
) -> None:
    """plot the data"""
    # these are the default matplotlib plot sizes
    sx, sy = 8.0, 6.0
    multiplier = 1.35
    # scale up the plot
    sx *= multiplier
    sy *= multiplier

    text_alpha = 0.75

    # create the figure, and get the current axis
    plt.figure(figsize=(sx, sy))
    ax = plt.gca()

    if timescale == 'day':
        x_range = range(366)
    elif timescale == 'week':
        x_range = range(53)
    else:
        x_range = range(12)

    # unpack the historic data range
    start_year, end_year = start_end_year

    main_plot_label = f'{aggregation} rainfall {start_year}–{end_year}'

    if timescale in ('day', 'week'):
        plt.plot(
            x_range,
            historic[aggregation],
            color='#8da0cb',
            label=main_plot_label,
            linewidth=1,
            marker='.'
        )
    else:
        plt.bar(
            x_range,
            historic[aggregation],
            color='#8da0cb',
            label=main_plot_label,
        )

    # scatter plot for the record highs
    plt.scatter(
        rec_high.index-1,
        rec_high[aggregation],
        color='#fc8d62',
        s=25,
        label='record high in past decade',
    )

    # set up the x-axis ticks and labels
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    days_in_month = [0, 30, 29, 31, 30, 31, 30, 31, 31, 31, 31, 30, 31]
    month_pos = np.cumsum(days_in_month)[:-1] if timescale == 'day' else x_range

    if timescale in ('day', 'month'):
        ax.set_xticks(month_pos)
        ax.set_xticklabels(months)
    elif timescale == 'week':
        ax.set_xlabel('Week of year')

    max_mean = f'{"Maximum" if aggregation == "max" else "Mean"}'
    title = (
            f'{max_mean} rainfall per {timescale} in {station}, {county}, '
            f'{start_year}–{end_year}\n'
            f'and record rainfall per {timescale} in past decade'
    )

    # set the title
    ax.set_title(title, alpha=text_alpha)
    # set the y-axis label
    ax.set_ylabel('Rainfall (mm)', alpha=text_alpha)

    # disable the frame on the legend box
    leg = ax.legend(frameon=True)

    # set the alpha for the text for the x-axis, y-axis, and legend
    for t in leg.get_texts():
        t.set_alpha(text_alpha)
    for l in ax.yaxis.get_ticklabels():
        l.set_alpha(text_alpha)
    for l in ax.xaxis.get_ticklabels():
        l.set_alpha(text_alpha)
