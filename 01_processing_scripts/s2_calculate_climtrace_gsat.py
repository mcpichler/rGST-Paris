
# Theme song:   Sea Breeze
# Artist:       Tyrone Wells
# Album:        Snapshot
# Released:     2003

import os
import numpy as np
import pandas as pd


# HELPFUL BITS

def get_input_filename(regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = f"gmst_annual_{filename_mod}_climtrace_1850-2024.csv"

    else:
        filename = "gmst_annual_climtrace_1850-2024.csv"

    return filename


def get_output_filename(regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = f"gsat_annual_{filename_mod}_climtrace_1850-2024.csv"

    else:
        filename = "gsat_annual_climtrace_1850-2024.csv"

    return filename


# READING STUFF

def read_climtrace_gmst(data_dir, filename):
    """
    Read the ClimTrace GMST data.

    Parameters
    ----------
    data_dir : str
        The directory containing the input data files.

    Returns
    -------
    climtrace_gmst : pandas.DataFrame
        The ClimTrace GMST data with columns "ClimTrace_GMST" and
        "ClimTrace_GMST_1sigma".
    """
    climtrace_gmst = pd.read_csv(
        os.path.join(
            data_dir,
            filename,
        ),
        usecols=[0, 4, 6],
        index_col=0,
    )

    return climtrace_gmst


def read_era5_gsat():
    era5_gsat = pd.read_csv(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "00_input_data",
            "surface_temperature",
            "fig2b_GCH2023_timeseries_global_surface_temperature_annual_anomalies_ref1991-2020.csv",
        ),
        skiprows=3,
        usecols=range(0, 2),
        index_col=0,
        na_values=-999,
    )

    return era5_gsat


def calculate_climtrace_gsat(climtrace_gmst, f_gmst_to_gsat):
    climtrace_gsat = climtrace_gmst["ClimTrace_GMST"].to_frame().copy()
    climtrace_gsat.loc[1930:] = climtrace_gsat.loc[1930:] * f_gmst_to_gsat

    climtrace_gsat.rename(
        columns={"ClimTrace_GMST": "ClimTrace_GSAT"}, inplace=True
    )

    return climtrace_gsat


def calculate_climtrace_gsat_uncertainty(
    climtrace_gsat,
    climtrace_gmst,
    climtrace_gmst_uncertainty,
    f_gmst_to_gsat,
    f_gmst_to_gsat_sigma,
):

    climtrace_gsat_uncertainty = climtrace_gmst_uncertainty.copy()

    # Propagate GMST uncertainty and scaling factor uncertainty
    # to final GSAT uncertainty
    climtrace_gsat_uncertainty.loc[1930:] = np.sqrt(
        climtrace_gmst_uncertainty**2 * f_gmst_to_gsat**2
        + f_gmst_to_gsat_sigma**2 * abs(climtrace_gmst) ** 2
    ).loc[1930:]

    return climtrace_gsat_uncertainty


# MAIN

def main(regress=None, lag=None, smooth=None):

    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )

    f_gmst_to_gsat = 1.06
    f_gmst_to_gsat_ci90 = 0.04
    f_gmst_to_gsat_sigma = f_gmst_to_gsat_ci90 * (1 / 1.645)

    input_filename = get_input_filename(regress, lag, smooth)

    climtrace_gmst = read_climtrace_gmst(data_dir, input_filename)
    climtrace_gsat = calculate_climtrace_gsat(climtrace_gmst, f_gmst_to_gsat)

    era5_gsat = read_era5_gsat()
    offset = (
        climtrace_gsat["ClimTrace_GSAT"].loc[1951:1980].mean()
        - era5_gsat.loc[1951:1980].mean()
    )

    climtrace_gsat["ERA5 (C3S-CDS)"] = era5_gsat + offset

    climtrace_gsat["ClimTrace_GSAT_1sigma"] = (
        calculate_climtrace_gsat_uncertainty(
            climtrace_gsat,
            climtrace_gmst["ClimTrace_GMST"],
            climtrace_gmst["ClimTrace_GMST_1sigma"],
            f_gmst_to_gsat,
            f_gmst_to_gsat_sigma,
        )
    )

    output_filename = get_output_filename(regress, lag, smooth)

    climtrace_gsat.to_csv(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "02_output_data",
            output_filename,
        )
    )


if __name__ == "__main__":
    main()
