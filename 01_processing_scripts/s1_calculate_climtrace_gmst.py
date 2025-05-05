
# Theme song:   The Ocean
# Artist:       Led Zeppelin
# Album:        Houses of the Holy
# Released:     1973

import os
import numpy as np
import pandas as pd
import logging

from utils import su2_linear_regression as regression

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


# HELPFUL BITS

def remove_incomplete_years(df):
    """
    Removes any incomplete years from a DataFrame containing
    monthly data.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the monthly data.

    Returns
    -------
    complete_years : pandas.DataFrame
        A DataFrame containing only the complete years of data.
    """

    def filter_complete_years(group):
        return len(group) == 12

    complete_years = df.groupby(df.index.year).filter(filter_complete_years)

    return complete_years


def get_output_filename(regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = f"gmst_annual_{filename_mod}_climtrace_1850-2024.csv"

    else:
        filename = "gmst_annual_climtrace_1850-2024.csv"

    return filename


# READING STUFF

def read_hadcrut(input_data_dir, temp_resolution="monthly"):
    """
    Read the HadCRUT5 dataset from file.

    Parameters
    ----------
    input_data_dir : str
        The directory containing the input data files.
    temp_resolution : str
        The temporal resolution of the input data.
        Options are "monthly" or "annual".

    Returns
    -------
    hadcrut5 : pandas.DataFrame
        A pandas DataFrame containing the HadCRUT5 dataset.
    """
    # Read the HadCRUT5 dataset from file
    hadcrut5 = pd.read_csv(
        os.path.join(
            input_data_dir,
            f"HadCRUT.5.0.2.0.analysis.summary_series.global.{temp_resolution}.csv",
        ),
        index_col="Time",
    )

    # Set the index to datetime
    if temp_resolution == "monthly":
        hadcrut5.index = pd.to_datetime(hadcrut5.index).rename("time")

    return hadcrut5


def read_noaa_gt(input_data_dir):
    """
    Read the NOAA Global Temperature data from the file.

    Parameters
    ----------
    input_data_dir : str
        The directory containing the input data files.

    Returns
    -------
    noaa_gt : pandas.Series
        A pandas Series containing the NOAA Global Temperature data.
    """
    # Read the NOAA Global Temperature data
    noaa_gt = pd.read_csv(
        os.path.join(
            input_data_dir,
            "NOAAGlobalTemp_aravg_mon_land_ocean_90S_90N_v6_0_0_202503.asc",
        ),
        sep=r"\s+",
        usecols=range(0, 3),
        names=["Year", "Month", "GMST Anomaly"],
        header=None,
        index_col=0,
    )

    # Convert the NOAA monthly data to a timeseries
    noaa_gt = pd.Series(
        data=noaa_gt["GMST Anomaly"].values,
        index=pd.date_range(
            f"{noaa_gt.index[0]}-{noaa_gt.Month.iloc[0]}",
            f"{noaa_gt.index[-1]}-{noaa_gt.Month.iloc[-1]}",
            freq="MS",
        ),
    )

    return noaa_gt


def read_berkeley(input_data_dir):
    """
    Read the Berkeley Earth data from the file.

    Parameters
    ----------
    input_data_dir : str
        The directory containing the input data files.

    Returns
    -------
    berkeley : pandas.Series
        A pandas Series containing the Berkeley Earth global mean
        surface temperature anomaly data.
    """
    # Read the Berkeley Earth data
    berkeley = pd.read_csv(
        os.path.join(
            input_data_dir,
            "BerkeleyEarth_Land_and_Ocean_complete.txt",
        ),
        sep=r"\s+",
        skiprows=86,
        nrows=2095,
        usecols=range(0, 3),
        names=["Year", "Month", "GMST Anomaly"],
        header=None,
        index_col=0,
    )

    # Convert the Berkeley Earth monthly data to a timeseries
    berkeley = pd.Series(
        data=berkeley["GMST Anomaly"].values,
        index=pd.date_range(
            f"{berkeley.index[0]}-{berkeley.Month.iloc[0]}",
            f"{berkeley.index[-1]}-{berkeley.Month.iloc[-1]}",
            freq="MS",
        ),
    )

    return berkeley


# CALCULATING STUFF

def get_hadcrut_1sigma(input_data_dir):
    hadcrut_upper_conflim = read_hadcrut(
        input_data_dir, temp_resolution="annual"
    )["Upper confidence limit (97.5%)"]

    hadcrut_lower_conflim = read_hadcrut(
        input_data_dir, temp_resolution="annual"
    )["Lower confidence limit (2.5%)"]

    hadcrut_sigma = (
        (hadcrut_upper_conflim - hadcrut_lower_conflim) * (1 / 2) * (1 / 2.241)
    )

    return hadcrut_sigma


def calculate_climtrace_uncertainty(
    hadcrut_sigma, ensemble_spread, earliest_ensemble_spread
):

    # account for ensemble spread
    climtrace_sigma = np.sqrt(hadcrut_sigma**2 + ensemble_spread**2)

    # account for larger spread and uncertainty in very early period
    climtrace_sigma.loc[1850:1857] = earliest_ensemble_spread

    # linearly relax larger uncertainty constraint
    slp = (climtrace_sigma.loc[1857] - climtrace_sigma.loc[1864]) / (
        1857 - 1864
    )
    for i, y in enumerate(climtrace_sigma.loc[1857:1864].index):
        climtrace_sigma.loc[y] = climtrace_sigma.loc[1857] + i * slp

    return climtrace_sigma


# MAIN

def main(regress=None, lag=None, smooth=None):

    # input datasets
    input_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "surface_temperature",
    )

    hadcrut5 = read_hadcrut(input_data_dir)
    noaa_gt = read_noaa_gt(input_data_dir)
    berkeley = read_berkeley(input_data_dir)

    hadcrut5_sigma = get_hadcrut_1sigma(input_data_dir)

    # Create a joint DataFrame for the input datasets
    gmst_data = pd.DataFrame(index=hadcrut5.index)

    # Add the input datasets to the DataFrame
    gmst_data["HadCRUT5"] = hadcrut5["Anomaly (deg C)"]
    gmst_data["NOAAGlobalTemp"] = noaa_gt
    gmst_data["BerkeleyEarth"] = berkeley

    # Align reference periods in 1951-1980
    reference_period = ("1951", "1980")
    gmst_data = (
        gmst_data
        - gmst_data.loc[reference_period[0] : reference_period[1]].mean()
    )

    # Calculate ClimTrace
    gmst_data["ClimTrace_GMST"] = gmst_data.mean(axis=1, skipna=True)

    # Set reference to ClimTrace 1850-1900 mean
    reference_period = ("1850", "1900")
    gmst_data = (
        gmst_data
        - gmst_data["ClimTrace_GMST"]
        .loc[reference_period[0] : reference_period[1]]
        .mean()
    )

    gmst_data = remove_incomplete_years(gmst_data)

    # optional regression
    if regress is not None:
        logging.info(
            f"Performing regression with the following regressor(s): {regress}"
        )

        for c in gmst_data.columns:
            residual, model = regression.regression(
                gmst_data[c],
                regress,
                lag,
                smooth,
                data_smoother=5,
                sequential=True,
            )
            gmst_data[c] = residual
        gmst_data = gmst_data.loc[residual.index]

    gmst_annual_average = gmst_data.groupby(gmst_data.index.year).mean()

    ensemble_spread = (
        gmst_annual_average.drop(columns="ClimTrace_GMST")
        .subtract(gmst_annual_average["ClimTrace_GMST"], axis=0)
        .loc[1951:1980]
        .values.std()
    )

    earliest_ensemble_spread = (
        gmst_annual_average.drop(columns="ClimTrace_GMST")
        .subtract(gmst_annual_average["ClimTrace_GMST"], axis=0)
        .loc[1850:1864]
        .values.std()
    )

    gmst_annual_average["HadCRUT5_1sigma"] = hadcrut5_sigma

    gmst_annual_average["ClimTrace_GMST_1sigma"] = (
        calculate_climtrace_uncertainty(
            hadcrut5_sigma,
            ensemble_spread,
            earliest_ensemble_spread,
        )
    )

    output_filename = get_output_filename(regress, lag, smooth)
    gmst_annual_average.to_csv(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "02_output_data",
            output_filename,
        )
    )


if __name__ == "__main__":
    main()
