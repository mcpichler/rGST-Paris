
# Theme song:   Accelerationen
# Artist:       Johann Strauss II.
# Album:        -
# Released:     1860

import os
import numpy as np
import pandas as pd
import scipy.stats as stats


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


def get_output_filename(var, regress, lag, smooth):
    if regress is not None:
        regnames_for_filename = [r.replace("_", "") for r in regress]
        filename_mod = "_".join(
            [f"{r}lag{l}smooth{s}" for r, l, s in zip(regress, lag, smooth)]
        )
        filename = f"{var}_{filename_mod}_acceleration_test_summary.txt"

    else:
        filename = f"{var}_acceleration_test_summary.txt"

    return filename


# READING STUFF

def read_temperature_derivative(input_data_dir, input_filename, var):
    obs_temp = pd.read_csv(
        os.path.join(
            input_data_dir,
            input_filename,
        ),
        index_col=0,
    )

    return obs_temp[
        [
            f"ClimTrace_{var}_DecadalDerivative",
            f"ClimTrace_{var}_DecadalDerivative_1sigma",
        ]
    ]


# MAIN

def main(regress=None, lag=None, smooth=None):

    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
        "acceleration_test_summary",
    )

    for var in ["GMST", "GSAT"]:
        input_filename = get_input_filename(var, regress, lag, smooth)
        input_filename_noregress = f"{var.lower()}_decadalmean_climtrace_1850-2040.csv"

        decadal_derivative = read_temperature_derivative(
            data_dir, input_filename, var
        )

        decadal_derivative_noregress = read_temperature_derivative(
            data_dir, input_filename_noregress, var
        )

        yr1 = 1990
        yr2 = 2015

        n = 21
        dof = 2 * n - 2

        siglvl = 0.05

        slp1 = decadal_derivative_noregress.loc[yr1][
            f"ClimTrace_{var}_DecadalDerivative"
        ]
        slp2 = decadal_derivative_noregress.loc[yr2][
            f"ClimTrace_{var}_DecadalDerivative"
        ]

        bse1 = decadal_derivative.loc[yr1][
            f"ClimTrace_{var}_DecadalDerivative_1sigma"
        ]
        bse2 = decadal_derivative.loc[yr2][
            f"ClimTrace_{var}_DecadalDerivative_1sigma"
        ]

        diff = slp2 - slp1
        pooled_error = np.sqrt(bse1**2 + bse2**2)

        t = diff / pooled_error

        t_dist = stats.t(dof)

        p = 1 - t_dist.cdf(x=t)

        t_crit = t_dist.ppf(1 - siglvl)

        output = f"""
        T-TEST SUMMARY
        --------------

        regressors: {regress}

        value 1: {slp1:.4f} ± {bse1:.4f}
        value 2: {slp2:.4f} ± {bse2:.4f}

        degrees of freedom: {dof}
        significance level: {siglvl}

        difference: {diff:.4f}
        pooled standard error: {pooled_error:.4f}
        t-statistic: {t:.4f}
        critical t: {t_crit:.4f}
        p-value: {p:.4f}

        CONCLUSION:
        {'The values are significantly different.' if p < siglvl else 'The values are not significantly different.'}
        """

        output_filename = get_output_filename(var, regress, lag, smooth)
        with open(
            os.path.join(output_dir, output_filename),
            "w",
        ) as file:
            file.write(output)


if __name__ == "__main__":
    main()
