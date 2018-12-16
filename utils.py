"""utility functions for data cleaning and visualisation"""
from typing import Any, Dict, List, Tuple

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
    df['year_month'] = df['date'].dt.to_period('M')

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


def aggregate_and_plot(
    df: pd.DataFrame,
    station: str,
    county: str,
    timescale: str,
    agg: str,
) -> None:
    """aggreate and plot a dataframe"""
    # split the data into the past decade, and everything else
    last_decade, historic = split_data(df, cutoff_year=2008)

    # get the start and end years for the historic data
    start_end_year = get_start_end_years(historic)
    print(f'Historic data from: {start_end_year[0]}–{start_end_year[1]}')


    # aggregate the two DataFrames based on the timescale selected above
    historic_agg = aggregate_data(historic, timescale=timescale)
    last_decade_agg = aggregate_data(last_decade, timescale=timescale)

    # get a DataFrame with the record-breaking highs
    rec_high = record_high(last_decade_agg, historic_agg, agg=agg)

    # print out the number of record-breaking days, weeks, or months
    ess = 's' if rec_high.shape[0] > 1 else ''
    print(f'Record high recorded {rec_high.shape[0]} {timescale}{ess} in the past decade')

    # plot the data
    plot(
        historic_agg,
        last_decade_agg,
        rec_high,
        aggregation=agg,
        timescale=timescale,
        start_end_year=start_end_year,
        station=station,
        county=county,
    )


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


def plot_top_months(
    data: Dict[str, Dict[str, List[Any]]],
    county: str,
    station_name: str,
    n_months: int,
    highlight_top_only: bool,
) -> None:
    df = pd.DataFrame.from_dict(data[county])
    top_n = df.sort_values('rainfall', ascending=False).head(n=n_months)

    # these are the default matplotlib plot sizes
    sx, sy = 8.0, 6.0
    multiplier = 1.35
    # scale up the plot
    sx *= multiplier
    sy *= multiplier

    # alpha value for displayed text
    text_alpha = 0.7
    # colours to be used for bars
    grayed_out = 'silver'
    colour = '#8da0cb'

    plt.figure(figsize=(sx, sy))
    ax = plt.gca()

    labels = top_n['year_month']
    label_pos = np.arange(labels.shape[0])
    rainfall_mm = top_n['rainfall']

    bars = plt.bar(
        range(n_months),
        rainfall_mm,
        align='center',
        color=grayed_out,
    )

    if highlight_top_only:
        # colour top bar only
        bars[0].set_color(colour)
    else:
        # enumerate the indices
        index_map = dict(zip(top_n.index, range(n_months)))

        # get indices of years >= 2006 in the DataFrame
        indices = top_n[top_n.year >= 2006].index.values

        # get the indices of the bars to highlight
        recent_years = set(index_map[i] for i in indices)

        for idx in recent_years:
            bars[idx].set_color(colour)

    # set up the tickmarks and labels
    ax.set_xticks(label_pos)
    ax.set_xticklabels(labels)

    # turn off tickmarks and labels on left
    # turn off tickmarks on bottom, but leave label on
    plt.tick_params(
        bottom=False,
        left=False,
        labelleft=False,
        labelbottom=True,
    )

    # remove the frame
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # directly label each bar
    for bar in bars:
        plt.gca().text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() - 30,
            f'{bar.get_height():.1f}',
            ha='center',
            color='w',
            fontsize=11,
        )

    # add transparency to the xlabels
    for l in ax.xaxis.get_ticklabels():
        l.set_alpha(text_alpha)

    # set the title
    title = f'Top {n_months} monthly rainfall levels (mm) recorded in {station_name}, {county}'
    ax.set_title(title, alpha=text_alpha)
