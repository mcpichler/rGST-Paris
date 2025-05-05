
# Theme song:   Smooth Operator
# Artist:       Sade
# Album:        Diamond Life
# Released:     1984

import os
import pandas as pd
import utils.su1_mw_eot_algorithm as eot_decadal_mean


# HELPFUL BITS

def get_input_filename(var, regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = (
            f"{var.lower()}_annual_{filename_mod}_climtrace_1850-2024.csv"
        )

    else:
        filename = f"{var.lower()}_annual_climtrace_1850-2024.csv"

    return filename


def get_output_filename(var, regress, lag, smooth):
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


# READING STUFF


def read_annual_climtrace_gst(data_dir, filename):

    data = pd.read_csv(
        os.path.join(data_dir, filename),
        index_col=0,
    )

    return data


# MAIN

def main(regress=None, lag=None, smooth=None):
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )

    for var in ["GMST", "GSAT"]:

        input_filename = get_input_filename(var, regress, lag, smooth)
        annual_data = read_annual_climtrace_gst(data_dir, input_filename)

        (
            decadal_mean,
            decadal_derivative,
            decadal_mean_sigma,
            decadal_derivative_sigma,
        ) = eot_decadal_mean.mw_eot_smoother(
            annual_data[f"ClimTrace_{var}"],
            annual_data[f"ClimTrace_{var}_1sigma"],
            nStart=1850,
            nEnd=2040,
        )

        output = pd.concat(
            [
                decadal_mean,
                decadal_mean_sigma,
                decadal_derivative,
                decadal_derivative_sigma,
            ],
            axis=1,
            keys=[
                f"ClimTrace_{var}_DecadalMean",
                f"ClimTrace_{var}_DecadalMean_1sigma",
                f"ClimTrace_{var}_DecadalDerivative",
                f"ClimTrace_{var}_DecadalDerivative_1sigma",
            ],
        )

        output_filename = get_output_filename(var, regress, lag, smooth)

        output.to_csv(
            os.path.join(
                data_dir,
                output_filename,
            )
        )


if __name__ == "__main__":
    main()
