import math
import pandas as pd
import numpy as np
import statsmodels.api as sm


def calculate_weighted_least_squares(y, x, weights):
    """Perform weighted least squares regression."""
    x_with_constant = sm.add_constant(x)
    model = sm.WLS(y, x_with_constant, weights=weights).fit()
    return model


def eot_filter(series, coreWW, WWrange):
    """Calculates a number of linear fits for each center year,
    then returns the average value of the linear fits at that
    center year. The linear fits differ only in range.
    """

    deriv_lengths = np.arange(coreWW - WWrange, coreWW + WWrange + 1, 1)
    derivs = pd.Series(index=series.index, dtype=float)
    anom = pd.Series(index=series.index, dtype=float)
    anom_unc = pd.Series(index=series.index, dtype=float)
    deriv_unc = pd.Series(index=series.index, dtype=float)

    central = deriv_lengths[len(deriv_lengths) // 2]

    for i in series.index:
        slopes = {}
        anom_bse = []
        deriv_bse = []
        intercepts = {}
        cyrXs = []
        for l in deriv_lengths:
            # if window width is even, there is no precise center year;
            # these cases are handled by using the next largest odd window
            # width and half-weighting the edge-years
            if l % 2 == 1:
                delta = (l - 1) / 2
                weights = np.ones(l)
            else:
                delta = l / 2
                weights = np.ones(l + 1)
                weights[0] = 0.5
                weights[-1] = 0.5

            # if the window is not fully within the data range, apply special
            # index-shift treatment for marginal years.
            if (i - delta >= series.index[0]) and (i + delta <= series.index[-1]):
                y = series.loc[i - delta : i + delta]
                x = np.arange(-len(y.index) // 2 + 1, len(y.index) // 2 + 1)
                res = calculate_weighted_least_squares(y, x, weights)
                intercepts[l] = res.params.const
                cyrXs.append(res.params.const)
            elif i - delta < series.index[0]:
                j = i + (series.index[0] - (i - delta))
                y = series.loc[j - delta : j + delta]
                x = np.arange(-len(y.index) // 2 + 1, len(y.index) // 2 + 1)
                res = calculate_weighted_least_squares(y, x, weights)
                cyrXs.append(res.params.const + (i - j) * res.params.x1)
            else:
                j = i - ((i + delta) - series.index[-1])
                y = series.loc[j - delta : j + delta]
                x = np.arange(-len(y.index) // 2 + 1, len(y.index) // 2 + 1)
                res = calculate_weighted_least_squares(y, x, weights)
                cyrXs.append(res.params.const + (i - j) * res.params.x1)

            slopes[l] = res.params.x1

            anom_bse.append(
                np.sqrt(
                    res.bse.x1**2 * (math.ceil(len(x) * 1 / 2)) ** 2
                    + res.bse.const**2
                )
            )

            deriv_bse.append(res.bse.x1)

        anom.loc[i] = sum(cyrXs) / len(cyrXs)
        anom_unc[i] = sum(anom_bse) / len(anom_bse)

        if i >= series.index[0] + math.floor(central / 2) and i <= series.index[
            -1
        ] - math.floor(central / 2):
            deriv_unc[i] = np.sqrt(1/len(deriv_bse) * sum([d**2 for d in deriv_bse]))
            derivs.loc[i] = slopes[central]
        else:
            derivs.loc[i] = np.nan
            deriv_unc.loc[i] = np.nan

    return anom, derivs, anom_unc, deriv_unc


def mw_eot_smoother(
    ts,
    ts_unc,
    nStart=1960,
    nEnd=2023,
    mInnerHW=8,
    mOuterHW=11,
    nFlattertrendsStart=2019,
    nDataEnd=2023,
):

    ##############
    # PARAMETERS #
    ##############

    nDataStart = min(ts.index[0], nStart)
    mCoreHW = (mOuterHW + mInnerHW) / 2
    mCoreHWYrs = math.ceil(mCoreHW)

    mInnerFW = 2*mInnerHW + 1
    mOuterFW = 2*mOuterHW + 1
    mCoreFW = int(2*mCoreHW + 1)

    mXjitterfilterHW = mInnerHW // 4
    mDXjitterfilterHW = mInnerHW // 4

    N_Trendfits = mOuterFW - mInnerFW + 1

    nFilterStart = max(nStart-mOuterHW, nDataStart)
    nFilterEnd = nDataEnd

    nCoreyearsStart = nFilterStart + mCoreHWYrs
    nCoreyearsEnd = nFilterEnd - mCoreHWYrs

    ##########
    # STEP 1 #
    ##########

    ts = ts.loc[nFilterStart:nFilterEnd]
    ts_unc = ts_unc.loc[nFilterStart:nFilterEnd]

    # run EOT-Filter
    X, _, X_se, DX_se = eot_filter(
        ts, mCoreFW, (mCoreFW - mInnerFW)
    )

    # Combine EOT-uncertainty with Obs.-Uncertainty
    X_se = np.sqrt(X_se**2 + ts_unc**2)

    # Apply additional moving-boxcar noise filter
    X.update(X.rolling(window=(mXjitterfilterHW * 2 + 1), center=True).mean())
    X_se.update(
        X_se.rolling(window=(mXjitterfilterHW * 2 + 1), center=True).mean()
    )

    ##########
    # STEP 2 #
    ##########

    # CoreWW=20 and WWrange=0 setting of EOT-Filter is equivalent
    # to single-window (WW20) moving fit
    _, DX, _, _ = eot_filter(
        X,
        mCoreFW,
        0,
    )

    ##########
    # STEP 3 #
    ##########

    # curvature
    CX = DX - DX.shift(1)

    RecentAnnualMeanCX = CX.loc[
        (nCoreyearsEnd - mCoreFW + 1) : nCoreyearsEnd
    ].mean()

    # cumulative addition of mean curvature
    DX = DX.reindex(
        np.arange(
            DX.index[0],
            nFlattertrendsStart + 1,
        )
    )

    DX.loc[nCoreyearsEnd + 1 : nFlattertrendsStart] = DX.loc[
        nCoreyearsEnd
    ] + RecentAnnualMeanCX * np.arange(1, nFlattertrendsStart - nCoreyearsEnd + 1)
    DX_se.loc[nCoreyearsEnd + 1 : nFlattertrendsStart] = DX_se[nCoreyearsEnd]

    ##########
    # STEP 4 #
    ##########

    DX_se = np.sqrt(
        DX_se**2
        + (
            np.minimum(
                abs((X_se / X).loc[:nFlattertrendsStart]) * abs(DX),
                0.25 * abs(DX),
            )
            ** 2
        )
    )

    DX.update(
        DX.rolling(window=(mDXjitterfilterHW * 2 + 1), center=True).mean()
    )

    DX_se.update(
        DX_se.rolling(window=(mDXjitterfilterHW * 2 + 1), center=True).mean()
    )

    ##########
    # STEP 5 #
    ##########

    DX = DX.reindex(
        np.arange(
            DX.index[0],
            nEnd + 1,
        )
    )

    DX_se = DX_se.reindex(
        np.arange(
            DX_se.index[0],
            nEnd + 1,
        )
    )

    phi = np.multiply([30, 60, 90, 120, 150], (np.pi / 180))

    for i, n in enumerate(DX.loc[nFlattertrendsStart + 1 : nEnd + 1].index):
        try:
            DX[n] = DX[n - 1] + RecentAnnualMeanCX * (
                0.5 * (1 + np.cos(phi[i]))
            )
        except IndexError:
            DX[n] = DX[n - 1]
        DX_se[n] = DX_se[n - 1]

    ##########
    # STEP 6 #
    ##########

    nCXstartOK = max((nCoreyearsStart + 1), 1971)

    AvgAnnualCXSDev = CX.loc[(nCXstartOK+1) : (nCoreyearsEnd)].std()

    ExtensionDXUnc = pd.Series(index=DX.index, data=np.zeros(len(DX.index)))

    ExtensionDXUnc.loc[nCoreyearsEnd:nEnd] = (
        np.arange(0, nEnd - nCoreyearsEnd + 1) * AvgAnnualCXSDev
    )

    TotalDXUnc = np.sqrt(DX_se**2 + ExtensionDXUnc**2)

    ##########
    # STEP 7 #
    ##########

    X = X.reindex(
        np.arange(
            X.index[0],
            nEnd + 1,
        )
    )

    for n in X.loc[nCoreyearsEnd + 1 : nEnd + 1].index:
        X[n] = X[n - 1] + (1 / 2) * (DX[n - 1] + DX[n])

    X_se = X_se.reindex(
        np.arange(
            X.index[0],
            nEnd + 1,
        )
    )

    X_se.loc[nCoreyearsEnd + 1 : nEnd] = X_se[nCoreyearsEnd]

    ExtensionXUnc = pd.Series(index=X.index, data=np.zeros(len(X.index)))

    for y in range(nCoreyearsEnd + 1, nEnd + 1):
        ExtensionXUnc.loc[y] = ExtensionXUnc.loc[y - 1] + (1 / 2) * (ExtensionDXUnc.loc[y - 1] + ExtensionDXUnc.loc[y])

    EstimationXUnc = X_se
    EstimationXUnc = EstimationXUnc.reindex(ExtensionXUnc.index).fillna(0)
    TotalXUnc = np.sqrt(ExtensionXUnc**2 + EstimationXUnc**2)

    return X, DX, TotalXUnc, TotalDXUnc
