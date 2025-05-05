
# Theme song:   Waiting on the World to Change
# Artist:       John Mayer
# Album:        Continuum
# Released:     2006

import os
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FixedLocator
import matplotlib.gridspec as gridspec

import plotutils.pu1_datareaders as rd


# MATPLOTLIB PARAMS
matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = ["Lato", "sans-serif"]
matplotlib.rcParams["axes.titlesize"] = 8


# SCALER
scaler = 10  # scales figure by this factor (e.g., 10: °C/yr to °C/dec)


# NDC PATHWAYS (see UN Emissions Gap Report 2024 Table ES.2)
# (anchored to 2021-obs-value)
ndcs = {
    "Unconditional NDCs": {
        2021: 55.121029,
        2030: 55,
        2035: 54,
    },
    "Conditional NDCs": {2021: 55.121029, 2030: 51, 2035: 51},
    "Below 2°C": {2021: 55.121029, 2030: 41, 2035: 36},
    "Below 1.5°C": {2021: 55.121029, 2030: 33, 2035: 25},
}


# HELFUL BITS

def std_to_90pCI(std):
    return 1.645 * std


def anchor_ndcs_to_obs(obs, ndcs):
    for key in ndcs.keys():
        ndcs[key][2021] = obs.iloc[-1]

    return ndcs


# PLOTTING STUFF

def plot_decadal_data(ax, decadal_data, var):
    ax.plot(
        decadal_data.loc[1960:].index,
        scaler * decadal_data.loc[1960:][f"ClimTrace_{var}_DecadalDerivative"],
        color="#8C000F",
        marker="o",
        ms=1.5,
        linewidth=1,
        label="decadal|20y mean (and 90% CI)",
        clip_on=False,
        zorder=5,
    )

    ax.fill_between(
        decadal_data.loc[:2023].index,
        scaler * decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalDerivative"]
        + scaler
        * std_to_90pCI(
            decadal_data.loc[:2023][
                f"ClimTrace_{var}_DecadalDerivative_1sigma"
            ]
        ),
        scaler * decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalDerivative"]
        - scaler
        * std_to_90pCI(
            decadal_data.loc[:2023][
                f"ClimTrace_{var}_DecadalDerivative_1sigma"
            ]
        ),
        color="#8C000F",
        alpha=0.2,
        zorder=3,
        linewidth=0,
    )

    ax.fill_between(
        decadal_data.loc[2023:].index,
        scaler * decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalDerivative"]
        + scaler
        * std_to_90pCI(
            decadal_data.loc[2023:][
                f"ClimTrace_{var}_DecadalDerivative_1sigma"
            ]
        ),
        scaler * decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalDerivative"]
        - scaler
        * std_to_90pCI(
            decadal_data.loc[2023:][
                f"ClimTrace_{var}_DecadalDerivative_1sigma"
            ]
        ),
        color="#8C000F",
        alpha=0.4,
        zorder=3,
        linewidth=0,
    )


def plot_scenario_data(ax, scenario_data):
    scen_colors = {
        "ssp119": "#1EA4C2",
        "ssp126": "#2A3A5C",
        "ssp245": "#D9853B",
        "ssp585": "#C9323C",
    }

    for scen in scenario_data.columns:
        if scen in scen_colors.keys():
            color = scen_colors[scen]
        else:
            raise KeyError(f"No associated color found for scenario {c}")

        ax.plot(
            scaler * scenario_data.loc[:, scen],
            color=color,
            linewidth=1,
            zorder=4,
        )


def plot_emission_data(ax, ghg_data, co2_data, ndcs, co2_scenarios):

    def scale_data_to_secax(data):
        return (1 / (4000 / scaler)) * (data - 60)

    ndcs_colors = {
        "Unconditional NDCs": "#FF843D",
        "Conditional NDCs": "#DC3340",
        "Below 2°C": "#42CEF4",
        "Below 1.5°C": "#5FB87D",
    }

    ssp_colors = {
        "ssp119": "#1EA4C2",
        "ssp126": "#2A3A5C",
        "ssp245": "#D9853B",
        "ssp585": "#C9323C",
    }

    # plot emission data scaled to fit the secondary axis
    ax.plot(
        ghg_data.index,
        scale_data_to_secax(ghg_data),
        color="grey",
        linewidth=1,
        zorder=1,
    )

    ax.plot(
        co2_data.index,
        scale_data_to_secax(co2_data),
        color="black",
        linewidth=1,
        zorder=1,
    )

    for ndc_scen in ndcs.keys():
        ax.plot(
            ndcs[ndc_scen].keys(),
            scale_data_to_secax(np.array(list(ndcs[ndc_scen].values()))),
            color=ndcs_colors[ndc_scen],
            linewidth=1,
            zorder=0,
        )

    for ssp_scen in co2_scenarios.columns[::-1]:
        ax.plot(
            co2_scenarios.index,
            scale_data_to_secax(co2_scenarios[ssp_scen].values),
            color=ssp_colors[ssp_scen],
            linewidth=1,
            zorder=0,
        )


def add_boxes(ax, decadal_data, var):
    box_data = [
        {
            "med": scaler
            * decadal_data.loc[year][f"ClimTrace_{var}_DecadalDerivative"],
            "q1": scaler
            * decadal_data.loc[year][f"ClimTrace_{var}_DecadalDerivative"]
            - scaler
            * std_to_90pCI(
                decadal_data.loc[year][
                    f"ClimTrace_{var}_DecadalDerivative_1sigma"
                ]
            ),
            "q3": scaler
            * decadal_data.loc[year][f"ClimTrace_{var}_DecadalDerivative"]
            + scaler
            * std_to_90pCI(
                decadal_data.loc[year][
                    f"ClimTrace_{var}_DecadalDerivative_1sigma"
                ]
            ),
            "whishi": scaler
            * decadal_data.loc[year][f"ClimTrace_{var}_DecadalDerivative"],
            "whislo": scaler
            * decadal_data.loc[year][f"ClimTrace_{var}_DecadalDerivative"],
        }
        for year in [1990, 2015, 2030]
    ]

    # Create the box plot using the box_data list
    boxes = ax.bxp(
        box_data,
        widths=[0.66, 0.66, 0.66],
        positions=[1.13, 2.13, 3.13],
        patch_artist=True,
        showfliers=False,
    )

    for box in boxes["boxes"]:
        box.set(facecolor="#8C000F", alpha=0.2)
    boxes["boxes"][2].set(alpha=0.4)

    for median in boxes["medians"]:
        median.set(color="#8C000F", linewidth=1)

    for whisker in boxes["whiskers"]:
        whisker.set_visible(False)

    for cap in boxes["caps"]:
        cap.set_visible(False)

    ax.text(
        0.8,
        scaler * 0.006,
        "CY1990",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )
    ax.text(
        1.8,
        scaler * 0.006,
        "CY2015",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )
    ax.text(
        2.8,
        scaler * 0.006,
        "CY2030",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )


def add_dumbell_bars(ax, decadal_data, var, years):
    for y in years:
        ax.errorbar(
            y,
            scaler * decadal_data.loc[y][f"ClimTrace_{var}_DecadalDerivative"],
            yerr=scaler
            * decadal_data.loc[y][f"ClimTrace_{var}_DecadalDerivative_1sigma"],
            color="#8C000F",
            linewidth=0,
            capsize=2,
        )
        ax.errorbar(
            y,
            scaler * decadal_data.loc[y][f"ClimTrace_{var}_DecadalDerivative"],
            yerr=scaler
            * std_to_90pCI(
                decadal_data.loc[y][
                    f"ClimTrace_{var}_DecadalDerivative_1sigma"
                ]
            ),
            color="#8C000F",
            linewidth=0.5,
            capsize=0,
        )


# FORMATTING STUFF

def format_axis(ax: plt.Axes) -> None:
    ax.grid(zorder=0, alpha=0.1, linewidth=1)

    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(
        FixedLocator(scaler * np.arange(0, 0.041, 0.01))
    )
    ax.yaxis.set_minor_locator(
        FixedLocator(scaler * np.arange(0, 0.041, 0.002))
    )

    ax.xaxis.set_tick_params(labelsize=6)
    ax.yaxis.set_tick_params(labelsize=6)

    ax.set_xlim(1960, 2035)
    ax.set_ylim(scaler * -0.015, scaler * 0.04)

    ax.set_xlabel("Time (years)")


def format_suppaxis(ax):
    ax.set_axis_off()
    ax.set_ylim(scaler * -0.015, scaler * 0.04)
    ax.set_xlim(0.5, 3.5)

    ax.text(
        2.8,
        -scaler * 0.015,
        "GtCO$_2$(eq) per year",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )


def add_secondary_axis(ax):
    secax = ax.secondary_yaxis(
        "right",
        functions=(
            lambda x: (x * (4000 / scaler) + 60),
            lambda x: (x / (4000 / scaler) - 60),
        ),
    )

    secax.yaxis.set_major_locator(FixedLocator([0, 20, 40, 60]))
    secax.yaxis.set_minor_locator(FixedLocator([10, 30, 50]))

    secax.yaxis.set_tick_params(labelsize=6)


def add_text(
    ax, text, x, y, transform, va="top", ha="left", fontsize=8, color="black"
):
    ax.text(
        x,
        y,
        text,
        va=va,
        ha=ha,
        fontsize=fontsize,
        color=color,
        transform=transform,
    )


def add_legend(ax, fontsize, bbox_to_anchor):
    legend = ax.legend(
        loc="upper left",
        framealpha=0,
        fontsize=fontsize,
        bbox_to_anchor=bbox_to_anchor,
        borderaxespad=0,
    )

    legend.get_frame().set_linewidth(0)
    legend.get_frame().set_boxstyle("Round", pad=0, rounding_size=0)
    ax.add_artist(legend)


def get_ylabel(scaler):
    if scaler == 1:
        time_unit = "year"
    elif scaler == 10:
        time_unit = "decade"
    elif scaler == 100:
        time_unit = "century"
    else:
        time_unit = f"{scaler}y"

    return f"                       Temperature trend rate (°C/{time_unit})"


# MAIN

def main():
    # paths
    data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )
    fig_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "04_figures",
    )
    edgar_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "emissions",
        "EDGAR_2024_GHG_booklet_2024.xlsx",
    )
    gcb_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "emissions",
        "Global_Carbon_Budget_2024_v1.0.xlsx",
    )
    rcmip_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "00_input_data",
        "emissions",
        "rcmip-emissions-annual-means-v5-1-0.csv",
    )

    # basic layout
    fig = plt.figure(figsize=(19 / 2.54, 0.85 * 9.44 / 2.54))
    gs = gridspec.GridSpec(1, 6, width_ratios=[3.95, 0.5, 0.6, 3.95, 0.5, 0.6])

    ax1 = fig.add_subplot(gs[0])
    ax1_1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[3])
    ax2_1 = fig.add_subplot(gs[4])

    ax1.set_ylabel(get_ylabel(scaler))

    for axes, var in zip([[ax1, ax1_1], [ax2, ax2_1]], ["GMST", "GSAT"]):
        # read
        decadal_derivative = rd.read_decadal_data(
            data_dir, var, timerange=(1960, 2034), deriv=True
        )
        decadal_derivative[f"ClimTrace_{var}_DecadalDerivative_1sigma"] = (
            rd.read_decadal_data(
                data_dir,
                var,
                timerange=(1960, 2034),
                deriv=True,
                regress=["nino34_ERSSTlag3smooth5", "volclag7smooth5"],
            )[f"ClimTrace_{var}_DecadalDerivative_1sigma"]
        )

        derivative_scenarios = rd.read_deriv_scenario_data(
            data_dir, var, timerange=(2019, 2035)
        )
        ghg_emissions = rd.read_edgar_data(edgar_path)
        co2_emissions = rd.read_gcb_data(gcb_path, sources=["fossil emissions excluding carbonation", "land-use change emissions"]).loc[1970:]
        co2_emissions_lulucf = rd.read_gcb_data(gcb_path, sources=["land-use change emissions"]).loc[1970:]
        ghg_emissions_incl_lulucf = ghg_emissions + co2_emissions_lulucf
        co2_scenarios = rd.read_emissions_scenario_data(
            rcmip_path, ["ssp119", "ssp126", "ssp245", "ssp585"]
        )

        # offset correction of co2_scenarios
        co2_scenarios = co2_scenarios - (
            co2_scenarios.loc[2021] - co2_emissions.loc[2021]
        )

        # plot
        plot_decadal_data(axes[0], decadal_derivative, var)
        add_dumbell_bars(axes[0], decadal_derivative, var, [1990, 2015, 2030])
        plot_scenario_data(axes[0], derivative_scenarios)
        plot_emission_data(
            axes[0], ghg_emissions_incl_lulucf, co2_emissions, ndcs, co2_scenarios
        )

        add_boxes(axes[1], decadal_derivative, var)

        # legend
        add_legend(axes[0], fontsize=7, bbox_to_anchor=(0, 0.93))

        # format panel
        add_secondary_axis(axes[0])
        format_axis(axes[0])
        format_suppaxis(axes[1])

        # helpful lines
        axes[0].vlines(
            2023,
            ymin=scaler * -0.015,
            ymax=scaler * 0.04,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
            )

        axes[0].hlines(
            [
                scaler
                * decadal_derivative[f"ClimTrace_{var}_DecadalDerivative"].loc[
                    1990
                ],
                scaler
                * decadal_derivative[f"ClimTrace_{var}_DecadalDerivative"].loc[
                    2015
                ],
            ],
            xmin=1960,
            xmax=2046,
            color="black",
            linewidth=1,
            alpha=0.2,
            clip_on=False,
        )
        axes[0].hlines(
            0,
            xmin=1970,
            xmax=2035,
            color="black",
            linewidth=1,
            alpha=0.2,
        )

        # panel title
        add_text(
            axes[0],
            f"{var} trend rate",
            0.02,
            0.98,
            transform=axes[0].transAxes,
        )

        # emission annotations
        add_text(
            axes[0],
            r"GHG emissions",
            1995,
            scaler * -0.005,
            ha="right",
            va="bottom",
            transform=axes[0].transData,
        )
        add_text(
            axes[0],
            r"CO$_2$ emissions",
            1997,
            scaler * -0.008,
            ha="left",
            va="top",
            transform=axes[0].transData,
        )

    # panel labels
    ax1.text(
        -0.15, 1, "c", fontsize=10, fontweight=900, transform=ax1.transAxes
    )
    ax2.text(
        -0.15, 1, "d", fontsize=10, fontweight=900, transform=ax2.transAxes
    )

    # tight layout
    fig.tight_layout()
    plt.subplots_adjust(wspace=0)

    plt.savefig(
        os.path.join(
            fig_dir,
            "ClimTrace_Fig1cd_1960-2035-dGMST-dGSAT_v20250417.png",
        ),
        dpi=600,
    )


if __name__ == "__main__":
    main()
