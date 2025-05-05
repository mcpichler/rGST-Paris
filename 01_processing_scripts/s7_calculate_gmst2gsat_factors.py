
# Theme song:   Scale
# Artist:       Katie Gately
# Album:        Fawn / Brute
# Released:     2023

import os
import numpy as np
import pandas as pd
import xarray as xr


# HELPFUL BITS
def Kelvin_to_Celsius(Kelvin):
    return Kelvin - 273.15


# READING STUFF

def read_era5(input_data_dir):
    filename = f"gsat_annual_climtrace_1850-2024.csv"

    data = pd.read_csv(
        os.path.join(
            input_data_dir, filename,
        ),
        index_col=0,
    )

    return data["ERA5 (C3S-CDS)"]



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


# CALCULATING STUFF

def anchor_era_to_climtrace(era5, climtrace):
    era5_anom = era5 - era5.loc["1951":"1980"].mean()
    era5_vs_preind = era5_anom + climtrace.loc["1951":"1980"].mean().values

    return era5_vs_preind


def main():
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

    era5 = read_era5(os.path.join(output_data_dir))

    climtrace_gmst_annual = read_annual_climtrace(output_data_dir, "GMST")
    climtrace_gsat_annual = read_annual_climtrace(output_data_dir, "GSAT")

    era5_vs_preind = anchor_era_to_climtrace(era5, climtrace_gsat_annual)
    output = pd.DataFrame(
        index=np.arange(2010, 2025),
        columns=[
            "ERA5abs",
            "ERA5vsPreind",
            "ClimTraceGMST",
            "ERA5/ClimTraceGMST",
             ],
        )

    output["ERA5abs"] = era5.loc["2010":"2024"]
    output["ERA5vsPreind"] = era5_vs_preind.loc["2010":"2024"]
    output["ClimTraceGMST"] = climtrace_gmst_annual.loc["2010":"2024"]
    output["ClimTraceGSAT"] = climtrace_gsat_annual.loc["2010":"2024"]

    output["ERA5/ClimTraceGMST"] = output["ERA5vsPreind"]/ output["ClimTraceGMST"].values

    output.to_csv(
        os.path.join(
            output_data_dir,
            "GMST2GSATfactors_ERA5toClimTrace.csv",
            )
        )


if __name__ == "__main__":
    main()

