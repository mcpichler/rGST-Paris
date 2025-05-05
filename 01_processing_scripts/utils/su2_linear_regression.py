import os
import math
import datetime
import numpy as np
import statsmodels.api as sm
import pandas as pd
from . import su1_mw_eot_algorithm as gdm


def load_index(name):
    idx_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "00_input_data",
            "regression_indices",
    )

    if name == "volc":
        filename = "volcanic_sAOD_monthly_-50001-202312.csv"
        data = pd.read_csv(
            os.path.join(
                idx_dir,
                filename,
                ),
            index_col=0,
            )["stratospheric_AOD"]


    elif name == "nino34_ERSST" or name == "nino34HadISST" or name == "noaa_nao:":
        if name == "nino34_ERSST":
            footer = 3
        elif name == "nino34_HadISST":
            footer = 8
        elif name == "noaa_nao":
            footer = 0

        filename = name+".txt"

        raw_data = pd.read_csv(
            os.path.join(
                idx_dir,
                filename,
                ),
            sep=r"\s+",
            skiprows=1,
            skipfooter=footer,
            index_col=0,
            header=None,
            names=np.arange(1, 13, 1),
            na_values=-99.99,
            engine="python",
            )

        data = pd.Series(
            index = np.arange(
                raw_data.index[0]+ 1/24,
                raw_data.index[-1] + 1,
                1/12),
            data=[raw_data[m].loc[y] for y in raw_data.index for m in raw_data.columns],
            )

        if name == "nino34_ERSST":
            data = (data - data.dropna().mean())/data.dropna().std()

    else:
        raise KeyError(f"Index name {name} does not correspond to a known index.")

    return data.dropna()


def regression(data, indices, lags, smoothers, data_smoother=1, sequential=False):
    if not len(indices) == len(lags):
        raise IndexError("regression: 'indices' and 'lags' must have same length.")
    if not len(indices) == len(smoothers):
        raise IndexError("regression: 'indices' and 'smoothers' must have same length.")
    idxs = {}

    # smooth regressors and data
    for name, lag, smooth in zip (indices, lags, smoothers):
        weights = np.hamming(smooth)
        idxs[f"{name}_lag{lag}"] = load_index(name).shift(lag).rolling(smooth, center=True).apply(lambda x: np.sum(weights*x)/sum(weights)).bfill().ffill()
        idxs[f"{name}_lag{lag}"].index = np.round(idxs[f"{name}_lag{lag}"].index, 3) # gets rid of some precision errors in some datasets

        weights = np.hamming(data_smoother)
        data = data.rolling(data_smoother, center=True).apply(lambda x: np.sum(weights*x)/sum(weights)).bfill().ffill()

    # remove long-term signal
    ltc, _, _, _ = gdm.mw_eot_smoother(data.groupby(data.index.year).mean().astype(float),
                                    data.groupby(data.index.year).mean().astype(float)*0, # uncertainty irrelevant here
                                    nStart=1850,
                                    nEnd=2024,
                                    )

    ltc.index = pd.date_range(f"{ltc.index[0]}-06-15", f"{ltc.index[-1]+1}-06-15", freq="YS-JUN")
    ltc = ltc.reindex(data.index).interpolate(method="linear").bfill()
    data = data - ltc

    # reindex to match load_index conventions
    time_start = data.index.year[0] - (1/24) + data.index.month[0] * (1/12)
    time_end = data.index.year[-1] - (1/24) + data.index.month[-1] * (1/12)

    data_time = np.linspace(
            time_start,
            time_end,
            round((time_end-time_start) * 12) + 1
        )

    data.index = np.round(data_time, 3)

    # shorten to longest common period
    alldata = [idx for idx in idxs.values()]
    alldata.append(data)

    first_months = [d.dropna().index[0] for d in alldata]
    time_start = np.max(first_months)

    last_months = [d.dropna().index[-1] for d in alldata]
    time_end = np.min(last_months)

    data = data.loc[time_start:time_end]
    for name in idxs.keys():
        idxs[name] = idxs[name].loc[time_start:time_end]

    # check if all timelines are identical now
    for idx in idxs.values():
        if not idx.index.equals(data.index):
            raise IndexError("regression: timelines of data and indices do not align")

    # regression

    if sequential:
        resid = data.copy()
        for idx in idxs.items():
            x = pd.DataFrame(
                index=idx[1].index,
                data=idx[1].values,
                columns=[idx[0]],
                dtype=float,
                )
            X = sm.add_constant(x)
            ols = sm.OLS(resid.astype(float), X)
            res = ols.fit()

            resid = res.resid
            resvar = resid.std()**2

        r2 = (data.std()**2 - resvar)/data.std()**2

        model = data - resid

    else:
        x = pd.DataFrame(
            index=data.index,
            data=np.array([idx.values for idx in idxs.values()]).T,
            columns=idxs.keys(),
            dtype=float,
            )
        X = sm.add_constant(x)
        ols = sm.OLD(data.astype(float), X)
        res = ols.fit()

        resid = res.resid
        r2 = res.rsquared

        model = (res.params*X).sum(axis=1)

    # convert back to datetime
    datetime_timeline = []
    for d in resid.index:
        year=int(math.floor(d))
        year_fraction = d - year

        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            days_in_year = 366
        else:
            days_in_year = 365

        day_of_year = int(round(year_fraction*days_in_year))
        month = (day_of_year - 1) // 30 + 1
        if month > 12:
            month = 12

        datetime_timeline.append(datetime.datetime(year, month, 1))

    resid.index = datetime_timeline
    model.index = datetime_timeline

    # add long-term signal
    resid = (resid + ltc.loc[resid.index[0]:resid.index[-1]]).dropna()

    return resid, model
