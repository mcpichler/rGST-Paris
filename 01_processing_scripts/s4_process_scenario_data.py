
# Theme song:   Hypotheticals
# Artist:       Lake Street Dive
# Album:        Obviously
# Released:     2021

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm


# HELPFUL BITS

def get_input_filename(var, regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = (
            f"{var.lower()}_decadalmean_{filename_mod}_climtrace_1850-2040.csv"
        )

    else:
        filename = f"{var.lower()}_decadalmean_climtrace_1850-2040.csv"

    return filename


def get_output_filename(var, regress, lag, smooth, deriv=False):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        if not deriv:
            filename = f"{var.lower()}_scenarios_{filename_mod}_climtrace_1850-2100.csv"
        else:
            filename = f"{var.lower()}_deriv_scenarios_{filename_mod}_climtrace_1850-2100.csv"

    else:
        if not deriv:
            filename = f"{var.lower()}_scenarios_climtrace_1850-2100.csv"
        else:
            filename = f"{var.lower()}_deriv_scenarios_climtrace_1850-2100.csv"

    return filename


def scale_gsat_to_gmst(gsat):
    return gsat * (1 / 1.06)


def weighted_linear_regression(x, y, weights):
    X = sm.add_constant(x)

    model = sm.WLS(y, X, weights=weights)
    results = model.fit()
    return results


# READING STUFF

def read_raw_scenario_data(input_data_dir):
    data = pd.read_csv(
        os.path.join(input_data_dir, "WegCTLM_gsat_scenarios_1850-2100.csv"),
        index_col=0,
    )

    return data


def read_obs_decmean_temperature(
    input_data_dir, input_filename, var, deriv=False
):
    obs_temp = pd.read_csv(
        os.path.join(
            input_data_dir,
            input_filename,
        ),
        index_col=0,
    )

    if deriv:
        return obs_temp[f"ClimTrace_{var}_DecadalDerivative"]
    else:
        return obs_temp[f"ClimTrace_{var}_DecadalMean"]


# CALCULATING STUFF

def anchor_scens_to_obs(obs, scen_data, year):
    anchored_scen_data = pd.DataFrame(
        index=scen_data.index, columns=scen_data.columns
    )
    for scen in scen_data.columns:

        offset = obs.loc[year] - scen_data[scen].loc[year]
        anchored_scen_data.loc[year:, scen] = (
            scen_data.loc[year:, scen].copy() + offset
        )
        anchored_scen_data.loc[:year, scen] = obs.loc[:year].copy()

    return anchored_scen_data.dropna()


def adjust_scens_to_obs(scen_data, scen_deriv_data, obs_deriv, year):
    adj_scen_data = scen_data.copy()
    adj_scen_deriv_data = pd.DataFrame(
        index=scen_deriv_data.index, columns=scen_deriv_data.columns
    )

    for scen in scen_deriv_data.columns:
        f_adj = obs_deriv.loc[year] / scen_deriv_data.loc[year, scen]
        f_adj_fadeout = np.concat([np.linspace(f_adj, 1, 21), np.ones(59)])
        adj_scen_deriv_data[scen] = f_adj_fadeout * scen_deriv_data[scen].copy()

        deriv_adj = adj_scen_deriv_data[scen] - scen_deriv_data[scen]
        abs_adj = pd.Series(index=deriv_adj.index, data=0.0)

        for t in deriv_adj.iloc[:-1].index:
            abs_adj[t + 1] = abs_adj[t] + (1 / 2) * (
                deriv_adj.loc[t + 1] + deriv_adj.loc[t]
            )

        adj_scen_data.loc[abs_adj.index, scen] = (
            adj_scen_data.loc[abs_adj.index, scen] + abs_adj
        )

    # smooth out transition between observation and scenario
    adj_scen_deriv_data = adj_scen_deriv_data.reindex(np.arange(2017, 2101))
    for scen in scen_deriv_data.columns:
        adj_scen_deriv_data.loc[2017:2020, scen] = obs_deriv.loc[
            2017:2020
        ].copy()
        adj_scen_deriv_data.loc[2019:2024, scen] = (
            adj_scen_deriv_data.loc[2017:2026, scen]
            .rolling(window=5, center=True)
            .mean()
            .dropna()
        )

    # correct for overoptimistic neg-emission assumptions in SSP1-1.9
    adj_scen_data.loc[2060:,"ssp119"] = adj_scen_data.loc[2060:,"ssp119"] + 0.00045*(0.2/2)*(adj_scen_data.loc[2060:,"ssp119"].index-2060)**2

    return adj_scen_data, adj_scen_deriv_data


def calculate_scen_deriv(scen_data):
    scen_deriv = pd.DataFrame(
        index=scen_data.index,
        columns=scen_data.columns,
    )

    for scen in scen_data.columns:
        for t in np.arange(2021, 2101):
            x = scen_data.loc[t - 2 : t + 2, scen].index.values
            y = scen_data.loc[t - 2 : t + 2, scen].values
            weights = np.ones(len(x))

            fit = weighted_linear_regression(x, y, weights)
            scen_deriv.loc[t, scen] = fit.params[1]

    return scen_deriv.dropna()


# MAIN

def main(regress=None, lag=None, smooth=None):
    input_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "surface_temperature",
    )
    output_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )

    # read
    raw_gsat_scenarios = read_raw_scenario_data(input_data_dir)

    input_filename = get_input_filename("GSAT", regress, lag, smooth)
    obs_gsat = read_obs_decmean_temperature(
        output_data_dir, input_filename, "GSAT"
    )

    # anchor raw scenarios to observed decadal mean
    anchored_gsat_scens = anchor_scens_to_obs(
        obs_gsat, raw_gsat_scenarios, 2021
    )

    # calculate derivative scenarios
    raw_gsat_deriv_scens = calculate_scen_deriv(anchored_gsat_scens)

    # relative adjustment of (derivative) scenarios to match observed derivative
    obs_gsat_deriv = read_obs_decmean_temperature(
        output_data_dir, input_filename, "GSAT", deriv=True
    )
    adj_gsat_scens, adj_gsat_deriv_scens = adjust_scens_to_obs(
        anchored_gsat_scens,
        raw_gsat_deriv_scens,
        obs_gsat_deriv,
        2021,
    )

    # scale gmst scenarios from gsat scenarios
    adj_gmst_scens = scale_gsat_to_gmst(adj_gsat_scens)
    adj_gmst_deriv_scens = scale_gsat_to_gmst(adj_gsat_deriv_scens)  #

    for var in ["gsat", "gmst"]:

        # save data
        output_filename = get_output_filename(var, regress, lag, smooth)
        eval(f"adj_{var}_scens").to_csv(
            os.path.join(
                output_data_dir,
                output_filename,
            )
        )

        output_filename_deriv = get_output_filename(
            var, regress, lag, smooth, deriv=True
        )

        eval(f"adj_{var}_deriv_scens").to_csv(
            os.path.join(
                output_data_dir,
                output_filename_deriv,
            )
        )

        anchored_gsat_scens.to_csv(
            os.path.join(
                output_data_dir,
                "unadjusted_gsat_scenarios.csv",
                ),
            )


if __name__ == "__main__":
    main()
