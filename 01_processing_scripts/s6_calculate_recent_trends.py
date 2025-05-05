
# Theme song:   No One Fits Me (Better Than You)
# Artist:       Airbourne
# Album:        Black Dog Barking
# Released:     2013

import os
import numpy as np
import pandas as pd
import xarray as xr
import statsmodels.api as sm

# READING STUFF

def read_hadcrut(input_data_dir, temp_resolution="monthly"):
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


def read_noaa_gt(input_data_dir, region):
    if region == "land_ocean":
        name = "NOAA-GlobalTemp"
    elif region == "land":
        name = "NOAA-GT-Land"
    # Read the NOAA Global Temperature data
    noaa_gt = pd.read_csv(
        os.path.join(
            input_data_dir,
            f"NOAAGlobalTemp_aravg_mon_{region}_90S_90N_v6_0_0_202503.asc",
        ),
        sep=r"\s+",
        usecols=range(0, 3),
        names=["Year", "Month", "Anomaly"],
        header=None,
        index_col=0,
    )

    # Convert the NOAA monthly data to a timeseries
    noaa_gt = pd.Series(
        data=noaa_gt["Anomaly"].values,
        index=pd.date_range(
            f"{noaa_gt.index[0]}-{noaa_gt.Month.iloc[0]}",
            f"{noaa_gt.index[-1]}-{noaa_gt.Month.iloc[-1]}",
            freq="MS",
        ),
        name=name,
    )

    return noaa_gt


def read_gistemp_lsat(input_data_dir):
    def convert_fractional_year_to_datetime(year_fraction):
        year = int(year_fraction)
        month_lookup = {0.04:1, 0.13:2, 0.21:3, 0.29:4, 0.38:5, 0.46:6,
                        0.54:7, 0.63:8, 0.71:9, 0.79:10, 0.88:11, 0.96:12,
                        }
        month = month_lookup[round(year_fraction%1, 2)]
        return pd.to_datetime(f"{year}-{month:02d}")

    gt_land = pd.read_csv(
        os.path.join(
            input_data_dir,
            "gistemp_lsatv4.csv",
            ),
        skiprows=1,
        usecols=[0,3],
        index_col=0,
        )

    gt_land.index = pd.Index([convert_fractional_year_to_datetime(t) for t in gt_land.index])

    return gt_land.rename(columns={"Land_Only":"GHCNv4"})


def read_berkeley(input_data_dir, landonly=False):
    if landonly:
        filename = "BerkeleyEarth_Complete_TAVG_complete.txt"
        skiprows = 1235
        name = "BerkeleyEarth-Land"
    else:
        filename = "BerkeleyEarth_Land_and_Ocean_complete.txt"
        skiprows = 86
        name = "BerkeleyEarth"
    # Read the Berkeley Earth data
    berkeley = pd.read_csv(
        os.path.join(
            input_data_dir,
            filename,
        ),
        sep=r"\s+",
        skiprows=skiprows,
        nrows=2100,
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
        name=name,
    )

    return berkeley


def read_annual_climtrace(data_dir, var):
    climtrace_annual = pd.read_csv(
        os.path.join(
            data_dir,
            f"{var.lower()}_annual_climtrace_1850-2024.csv",
        ),
        usecols=["time", f"ClimTrace_{var}"],
        index_col=0,
    )

    return climtrace_annual


def read_ersst(input_data_dir):
    ersst = xr.load_dataset(
        os.path.join(
            input_data_dir,
            "timemerge_fldmean_ersst.v5.nc",
            )
        )

    ersst = pd.DataFrame(
        data=ersst.sel(lon=0, lat=0, lev=0)["ssta"].values,
        index=pd.date_range(
            f"{ersst.time.dt.year.values[0]}-{ersst.time.dt.month.values[0]}",
            f"{ersst.time.dt.year.values[-1]}-{ersst.time.dt.month.values[-1]}",
            freq="MS",
        ),
        columns=["ERSSTv5"]
    )

    return ersst


def read_iap_sst(input_data_dir):
    iap_sst = xr.load_dataset(
        os.path.join(
            input_data_dir,
            "fldmean_IAPv4_t1m_1960-2024.nc",
            )
        )

    iap_sst = pd.DataFrame(
        data=iap_sst.sel(lon=0, lat=0)["temp"].values,
        index=pd.date_range(
            f"{iap_sst.time.dt.year.values[0]}-{iap_sst.time.dt.month.values[0]}",
            f"{iap_sst.time.dt.year.values[-1]}-{iap_sst.time.dt.month.values[-1]}",
            freq="MS",
        ),
        columns=["IAPv4-SST"]
    )

    return iap_sst


def read_era5_data(input_data_dir, metric):
    date = "2025-03-15"
    filename = f"era5_{metric}_monthly_gloavg_{date}.nc"

    era5_data = xr.load_dataarray(
        os.path.join(
            input_data_dir,
            filename,
            )
        )

    era5_data = pd.DataFrame(
        data=era5_data,
        index=pd.date_range(
            f"{era5_data.valid_time.dt.year.values[0]}-{era5_data.valid_time.dt.month.values[0]}",
            f"{era5_data.valid_time.dt.year.values[-1]}-{era5_data.valid_time.dt.month.values[-1]}",
            freq="MS",
        ),
        columns=[f"ERA5-{metric.upper()}"]
    )

    return era5_data


def read_jra3q_data(input_data_dir, metric):
    date = "2025-03-14"
    # filename = f"fldmean_jra-3q_{metric}_monthly_gloavg_{date}.nc"
    filename = f"jra-3q_{metric}_monthly_gloavg_{date}.nc"

    jra3q_data = xr.load_dataarray(
        os.path.join(
            input_data_dir,
            filename,
            )
        )

    jra3q_data = pd.DataFrame(
        data=jra3q_data,
        index=pd.date_range(
            f"{jra3q_data.time.dt.year.values[0]}-{jra3q_data.time.dt.month.values[0]}",
            f"{jra3q_data.time.dt.year.values[-1]}-{jra3q_data.time.dt.month.values[-1]}",
            freq="MS",
        ),
        columns=[f"JRA-3Q-{metric.upper()}"]
    )

    return jra3q_data


def read_hadsst(input_data_dir):
    hadsst = pd.read_csv(
        os.path.join(
            input_data_dir,
            "HadSST.4.0.1.0_monthly_GLOBE.csv",
            ),
        usecols=["year", "month", "anomaly"],
        index_col=[0],
        )

    hadsst = pd.Series(
        data=hadsst["anomaly"].values,
        index=pd.date_range(
            f"{hadsst.index[0]}-{hadsst.month.iloc[0]}",
            f"{hadsst.index[-1]}-{hadsst.month.iloc[-1]}",
            freq="MS",
        ),
    )

    return hadsst


def read_crutem(input_data_dir):
    crutem = pd.read_csv(
        os.path.join(
            input_data_dir,
            "CRUTEM.5.0.2.0.summary_series.global.monthly.csv",
            ),
        usecols=[0,1],
        index_col=0,
        )

    crutem.index = crutem.index.astype("datetime64[ns]")
    return crutem


def read_ghcn_cams(input_data_dir):
    ghcn_cams = xr.load_dataset(
        os.path.join(
            input_data_dir,
            "fldmean_ghcn_cams_air.mon.mean.nc",
            )
        )

    ghcn_cams = pd.DataFrame(
        data=ghcn_cams.sel(lon=0, lat=0)["air"].values,
        index=pd.date_range(
            f"{ghcn_cams.time.dt.year.values[0]}-{ghcn_cams.time.dt.month.values[0]}",
            f"{ghcn_cams.time.dt.year.values[-1]}-{ghcn_cams.time.dt.month.values[-1]}",
            freq="MS",
        ),
        columns=["GHCN/CAMS"]
    )

    return ghcn_cams


def read_iap_temperature_depthprofile(input_data_dir):
    iap_profs = xr.load_dataset(
        os.path.join(
            input_data_dir,
            "fldmean_IAPv4_Temp_anomaly_monthly_1_200m_1960-2024.nc",
            ),
        )

    iap_profs = pd.DataFrame(
        index=iap_profs.time,
        columns=iap_profs.depth_std,
        data=iap_profs.sel(lon=0, lat=0).temp.values,
        )

    return iap_profs


def read_era5_altitudeprofile(input_data_dir, region=None):
    date = "2025-03-12"

    filename = f"era5_temp_on_altitude_monthly_gloavg_{date}_100minterp.nc"
    era5_profs = xr.load_dataset(
        os.path.join(
            input_data_dir,
            filename,
            ),
        )

    if not region == None:
        era5_profs = pd.DataFrame(
            index=era5_profs.time,
            columns=era5_profs.altitude,
            data=era5_profs[f"temperature_adj_over_{region}"]
            )
    else:
        era5_profs = pd.DataFrame(
            index=era5_profs.time,
            columns=era5_profs.altitude,
            data=era5_profs[f"temperature_adj"]
            )

    return era5_profs


# CALCULATING STUFF

def calculate_linear_trends(data, start_year, end_year, window_size=33, conversion_factor=10):
    trend_slopes = pd.DataFrame(index=data.columns, columns=[f"{start_year+i}-{start_year+window_size+i-1}" for i in range(0, end_year - window_size - start_year + 1)])
    slope_uncerts = pd.DataFrame(index=data.columns)

    for c in data.columns:
        i = 0
        while start_year + window_size + i - 1 <= end_year:
            try:
                subset = data.loc[start_year+i:start_year+window_size+i-1]
            except TypeError:
                subset = data.loc[str(start_year+i):str(start_year+window_size+i-1)]

            x = np.arange(0, len(subset.index))
            X = sm.add_constant(x)

            y = subset[c].values

            model = sm.OLS(y, X)
            results = model.fit()

            trend_slopes.loc[c, f"{start_year+i}-{start_year+window_size+i-1}"] = results.params[1]*conversion_factor
            slope_uncerts.loc[c, f"{start_year+i}-{start_year+window_size+i-1}"] = results.bse[1]*conversion_factor

            i += 1

    return trend_slopes, slope_uncerts


def deseasonalize_timeseries(data, reference_period):
    def seasonal_adjustment(data, annual_cycle):
        deseasonalized_data = data.copy()
        for date in data.index:
            deseasonalized_data.loc[date] = data.loc[date] - annual_cycle.loc[date.month]
        return deseasonalized_data

    reference = data.loc[str(reference_period[0]):str(reference_period[1])]
    annual_cycle = reference.groupby(reference.index.month).mean()

    return seasonal_adjustment(data, annual_cycle)


# MAIN

def main():
    input_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "surface_temperature",
    )

    profile_input_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "temperature_profiles",
    )

    output_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )

    start_year = 1991
    end_year = 2023

    # profiles

    iap_profiles = read_iap_temperature_depthprofile(profile_input_data_dir)
    iap_annual_profiles = iap_profiles.groupby(iap_profiles.index.year).mean()
    iap_trend_profile, iap_uncert_profile = calculate_linear_trends(iap_annual_profiles, start_year, end_year, conversion_factor=10)
    iap_trend_profile["average"] = iap_trend_profile.mean(axis=1)
    iap_uncert_profile["average"] = np.sqrt((iap_uncert_profile**2).sum(axis=1)/len(iap_uncert_profile.columns))

    era5_profiles = read_era5_altitudeprofile(profile_input_data_dir)
    era5_land_profiles = read_era5_altitudeprofile(profile_input_data_dir, "land")
    era5_ocean_profiles = read_era5_altitudeprofile(profile_input_data_dir, "oceans")

    era5_profiles_deseasonalized = deseasonalize_timeseries(era5_profiles, (1991, 2020))
    era5_land_profiles_deseasonalized = deseasonalize_timeseries(era5_land_profiles, (1991, 2020))
    era5_ocean_profiles_deseasonalized = deseasonalize_timeseries(era5_ocean_profiles, (1991, 2020))

    era5_annual_profiles = era5_profiles_deseasonalized.groupby(era5_profiles.index.year).mean()
    era5_land_annual_profiles = era5_land_profiles_deseasonalized.groupby(era5_land_profiles.index.year).mean()
    era5_ocean_annual_profiles = era5_ocean_profiles_deseasonalized.groupby(era5_ocean_profiles.index.year).mean()

    era5_trend_profile, era5_uncert_profile = calculate_linear_trends(era5_annual_profiles, start_year, end_year, conversion_factor=10)
    era5_trend_profile["average"] = era5_trend_profile.mean(axis=1)
    era5_uncert_profile["average"] = np.sqrt((era5_uncert_profile**2).sum(axis=1)/len(era5_uncert_profile.columns))

    era5_land_trend_profile, era5_land_uncert_profile = calculate_linear_trends(era5_land_annual_profiles, start_year, end_year, conversion_factor=10)
    era5_land_trend_profile["average"] = era5_land_trend_profile.mean(axis=1)
    era5_land_uncert_profile["average"] = np.sqrt((era5_land_uncert_profile**2).sum(axis=1)/len(era5_land_uncert_profile.columns))

    era5_ocean_trend_profile, era5_ocean_uncert_profile = calculate_linear_trends(era5_ocean_annual_profiles, start_year, end_year, conversion_factor=10)
    era5_ocean_trend_profile["average"] = era5_ocean_trend_profile.mean(axis=1)
    era5_ocean_uncert_profile["average"] = np.sqrt((era5_ocean_uncert_profile**2).sum(axis=1)/len(era5_ocean_uncert_profile.columns))

    iap_trend_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"IAPv4_{start_year}-{end_year}_TrendProfile.csv",
        )
    )
    iap_uncert_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"IAPv4_{start_year}-{end_year}_TrendProfile_1sigma.csv",
        )
    )

    era5_trend_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_global_{start_year}-{end_year}_TrendProfile.csv",
        )
    )
    era5_uncert_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_global_{start_year}-{end_year}_TrendProfile_1sigma.csv",
        )
    )

    era5_land_trend_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_land_{start_year}-{end_year}_TrendProfile.csv",
        )
    )
    era5_land_uncert_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_land_{start_year}-{end_year}_TrendProfile_1sigma.csv",
        )
    )

    era5_ocean_trend_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_ocean_{start_year}-{end_year}_TrendProfile.csv",
        )
    )
    era5_ocean_uncert_profile.to_csv(
        os.path.join(
            output_data_dir,
            f"ERA5_ocean_{start_year}-{end_year}_TrendProfile_1sigma.csv",
        )
    )

    # GMST
    hadcrut5 = read_hadcrut(input_data_dir)
    climtrace_gmst = read_annual_climtrace(output_data_dir, "GMST")

    gmst_data = pd.DataFrame(index=hadcrut5.index)

    gmst_data["HadCRUT5"] = hadcrut5["Anomaly (deg C)"]

    era5_gmst_inclsi = read_era5_data(input_data_dir, "gmst_inclsi")
    era5_gmst_inclsi = deseasonalize_timeseries(era5_gmst_inclsi, (1991, 2020))
    era5_gmst_nosi = read_era5_data(input_data_dir, "gmst_nosi")
    era5_gmst_nosi = deseasonalize_timeseries(era5_gmst_nosi, (1991, 2020))
    era5_gmst_inclsi_f = read_era5_data(input_data_dir, "gmst_inclsi_f")
    era5_gmst_inclsi_f = deseasonalize_timeseries(era5_gmst_inclsi_f, (1991, 2020))
    era5_gmst_nosi_f = read_era5_data(input_data_dir, "gmst_nosi_f")
    era5_gmst_nosi_f = deseasonalize_timeseries(era5_gmst_nosi_f, (1991, 2020))

    jra3q_gmst_inclsi = read_jra3q_data(input_data_dir, "gmst_inclsi")
    jra3q_gmst_inclsi = deseasonalize_timeseries(jra3q_gmst_inclsi, (1991, 2020))
    jra3q_gmst_nosi = read_jra3q_data(input_data_dir, "gmst_nosi")
    jra3q_gmst_nosi = deseasonalize_timeseries(jra3q_gmst_nosi, (1991, 2020))
    jra3q_gmst_inclsi_f = read_jra3q_data(input_data_dir, "gmst_inclsi_f")
    jra3q_gmst_inclsi_f = deseasonalize_timeseries(jra3q_gmst_inclsi_f, (1991, 2020))
    jra3q_gmst_nosi_f = read_jra3q_data(input_data_dir, "gmst_nosi_f")
    jra3q_gmst_nosi_f = deseasonalize_timeseries(jra3q_gmst_nosi_f, (1991, 2020))

    gmst_data = pd.concat([gmst_data, era5_gmst_inclsi, era5_gmst_inclsi_f, era5_gmst_nosi, era5_gmst_nosi_f, jra3q_gmst_inclsi, jra3q_gmst_inclsi_f, jra3q_gmst_nosi, jra3q_gmst_nosi_f], axis=1)

    gmst_data["NOAAGloTemp"] = read_noaa_gt(input_data_dir, "land_ocean")
    gmst_data["BerkeleyEarth"] = read_berkeley(input_data_dir)


    gmst_annual_average = gmst_data.groupby(gmst_data.index.year).mean()
    gmst_annual_average["ClimTrace-GMST"] = climtrace_gmst["ClimTrace_GMST"]

    gmst_slopes = calculate_linear_trends(gmst_annual_average, start_year, end_year)

    # GSAT

    climtrace_gsat = read_annual_climtrace(output_data_dir, "GSAT")
    era5_gsat = read_era5_data(input_data_dir, "gsat")
    era5_gsat = deseasonalize_timeseries(era5_gsat, (1991, 2020))
    jra3q_gsat = read_jra3q_data(input_data_dir, "gsat")
    jra3q_gsat = deseasonalize_timeseries(jra3q_gsat, (1991, 2020))

    gsat_data = pd.DataFrame(index=era5_gsat.index, data=era5_gsat.values, columns=["ERA5-GSAT"])

    gsat_data = pd.concat([gsat_data, jra3q_gsat], axis=1)

    gsat_annual_average = gsat_data.groupby(gsat_data.index.year).mean()
    gsat_annual_average["ClimTrace-GSAT"] = climtrace_gsat["ClimTrace_GSAT"]

    gsat_slopes = calculate_linear_trends(gsat_annual_average, start_year, end_year)

    # SST
    ersst = read_ersst(os.path.join(input_data_dir, "sst"))
    hadsst = read_hadsst(os.path.join(input_data_dir, "sst"))
    era5_sst = read_era5_data(os.path.join(input_data_dir, "sst"), "sst")
    era5_sst = deseasonalize_timeseries(era5_sst, (1991, 2020))
    iap_sst = read_iap_sst(os.path.join(input_data_dir, "sst"))
    jra3q_sst = read_jra3q_data(os.path.join(input_data_dir, "sst"), "sst")
    jra3q_sst = deseasonalize_timeseries(jra3q_sst, (1991, 2020))

    sst_data = pd.DataFrame(index=hadsst.index)

    sst_data["HadSST4"] = hadsst.values
    sst_data = pd.concat([sst_data, ersst, era5_sst, iap_sst, jra3q_sst], axis=1)

    sst_annual_average = sst_data.groupby(sst_data.index.year).mean()
    sst_slopes = calculate_linear_trends(sst_annual_average, start_year, end_year)

    # LSAT
    crutem = read_crutem(os.path.join(input_data_dir, "lsat"))
    gt_land = read_gistemp_lsat(os.path.join(input_data_dir, "lsat"))
    berkeley_lsat = read_berkeley(os.path.join(input_data_dir, "lsat"), landonly=True)
    era5_lsat = read_era5_data(os.path.join(input_data_dir, "lsat"), "lsat")
    era5_lsat = deseasonalize_timeseries(era5_lsat, (1991, 2020))
    jra3q_lsat = read_jra3q_data(os.path.join(input_data_dir, "lsat"), "lsat")
    jra3q_lsat = deseasonalize_timeseries(jra3q_lsat, (1991, 2020))

    lsat_data = pd.DataFrame(index=crutem.index)
    lsat_data["CRUTEM5"] = crutem.values

    lsat_data = pd.concat([lsat_data, gt_land, berkeley_lsat, era5_lsat, jra3q_lsat,], axis=1)

    lsat_annual_average = lsat_data.groupby(lsat_data.index.year).mean()
    lsat_slopes = calculate_linear_trends(lsat_annual_average, start_year, end_year)

    # ## TEMPORARY: DIAGNOSTIC PLOT ##
    #
    # import matplotlib.pyplot as plt
    #
    # import ipdb; ipdb.set_trace()
    # def get_color(name):
    #     colors = {
    #         "HadSST": "tab:blue",
    #         "CRUTEM5": "tab:blue",
    #         "NOAA-GT-Land": "tab:orange",
    #         "GHCN/CAMS": "tab:orange",
    #         "ERSST": "tab:orange",
    #         "BerkeleyEarth-Land": "tab:olive",
    #         "IAPv4-SST": "tab:olive",
    #         "ERA5-LSAT": "tab:red",
    #         "ERA5-SST": "tab:red",
    #         "JRA3Q-LSAT": "tab:cyan",
    #         "JRA3Q-SST": "tab:cyan",
    #         }
    #     return colors[name]
    # for i in lsat_data.columns:
    #     plt.plot(
    #     lsat_annual_average.loc["1981":str(end_year)].index,
    #     (lsat_annual_average[i]-lsat_annual_average[i].loc["1991":"2020"].mean()).loc["1981":str(end_year)],
    #     label=f"{i}, k={round(float(lsat_slopes.mean(axis=1).loc[i]), 2)} °C/dec", color=get_color(i),
    #     )
    #     plt.plot(
    #         lsat_annual_average.loc["1991":str(end_year)].index,
    #     (1/10)*lsat_slopes.mean(axis=1).loc[i]*np.arange(-16, 17, (1/12)),
    #         color=get_color(i),
    #         )
    #     plt.legend()
    #     plt.grid()
    # plt.show()
    #
    # for i in sst_data.columns:
    #     plt.plot(
    #     sst_annual_average.loc["1981":str(end_year)].index,
    #     (sst_annual_average[i]-sst_annual_average[i].loc["1991":"2020"].mean()).loc["1981":str(end_year)],
    #     label=f"{i}, k={round(float(sst_slopes.mean(axis=1).loc[i]), 2)} °C/dec", color=get_color(i),
    #     )
    #     plt.plot(
    #         sst_annual_average.loc["1991":str(end_year)].index,
    #         (1/10)*sst_slopes.mean(axis=1).loc[i]*np.arange(-16, 17, (1/12)),
    #         color=get_color(i),
    #         )
    #     plt.legend()
    #     plt.grid()
    # plt.show()

    # SSAT
    era5_ssat = read_era5_data(os.path.join(input_data_dir, "ssat"), "ssat")
    jra3q_ssat = read_jra3q_data(os.path.join(input_data_dir, "ssat"), "ssat")

    ssat_data = pd.DataFrame(index=era5_ssat.index)
    ssat_data["ERA5-SSAT"] = era5_ssat.values
    ssat_data = pd.concat([ssat_data, jra3q_ssat], axis=1)

    ssat_annual_average = ssat_data.groupby(ssat_data.index.year).mean()
    ssat_slopes = calculate_linear_trends(ssat_annual_average, start_year, end_year)

    # combine and save
    all_slopes = pd.concat([gmst_slopes[0], gsat_slopes[0], sst_slopes[0], lsat_slopes[0], ssat_slopes[0]], axis=0)
    all_slope_uncerts = pd.concat([gmst_slopes[1], gsat_slopes[1], sst_slopes[1], lsat_slopes[1], ssat_slopes[1]], axis=0)

    all_slopes.to_csv(
        os.path.join(
            output_data_dir,
            f"SurfTempTrendRates_{start_year}-{end_year}_AllDatasets.csv",
        )
    )

    all_slope_uncerts.to_csv(
        os.path.join(
            output_data_dir,
            f"SurfTempTrendRateUncerts_{start_year}-{end_year}_AllDatasets.csv",
        )
    )

if __name__ == "__main__":
    main()
