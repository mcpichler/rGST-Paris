
# Theme song:   Big Yellow Taxi
# Artist:       Joni Mitchell
# Album:        Ladies of the Canyon
# Released:     1970

import os
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec

import plotutils.pu1_datareaders as rd

# MATPLOTLIB PARAMS
matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = ["Lato", "sans-serif"]
matplotlib.rcParams["axes.titlesize"] = 8


# IPCC REFERENCE VALUES

ipcc_ref = {
    "GSAT": {
        "median": 1.09,
        "lower": 0.91,
        "upper": 1.23,
    },
    "GMST": {
        "median": 1.09,
        "lower": 0.95,
        "upper": 1.20,
    },
}


# HELPFUL BITS

def std_to_90pCI(std):
    return 1.645 * std


# PLOTTING DATA

def plot_annual_data(ax, annual_data, var):
    (annual_line,) = ax.plot(
        annual_data.index,
        annual_data[f"ClimTrace_{var}"],
        color="black",
        marker="o",
        ms=1.5,
        linewidth=1,
        label="annual mean (and 90% CI)",
        zorder=2,
        clip_on=False,
    )

    ax.errorbar(
        annual_data.index,
        annual_data[f"ClimTrace_{var}"],
        yerr=std_to_90pCI(annual_data[f"ClimTrace_{var}_1sigma"]),
        color="black",
        linewidth=0.5,
        capsize=0,
    )

    return annual_line


def plot_decadal_data(ax, decadal_data, var):
    (decadal_line,) = ax.plot(
        decadal_data.loc[1960:].index,
        decadal_data.loc[1960:][f"ClimTrace_{var}_DecadalMean"],
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
        decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalMean"]
        + std_to_90pCI(
            decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalMean"]
        - std_to_90pCI(
            decadal_data.loc[:2023][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        color="#8C000F",
        alpha=0.2,
        zorder=3,
        linewidth=0,
    )

    ax.fill_between(
        decadal_data.loc[2023:].index,
        decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean"]
        + std_to_90pCI(
            decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean"]
        - std_to_90pCI(
            decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        color="#8C000F",
        alpha=0.4,
        zorder=3,
        linewidth=0,
    )

    ax.errorbar(
        [2015, 2030],
        [decadal_data.loc[2015][f"ClimTrace_{var}_DecadalMean"], decadal_data.loc[2030][f"ClimTrace_{var}_DecadalMean"]],
        yerr=[std_to_90pCI(decadal_data.loc[2015][f"ClimTrace_{var}_DecadalMean_1sigma"]), std_to_90pCI(decadal_data.loc[2030][f"ClimTrace_{var}_DecadalMean_1sigma"])],
        color="#8C000F",
        linewidth=0.5,
        linestyle="none",
        capsize=0,
        )

    return decadal_line


def plot_comparison_data(ax, comparison_data):
    scatters = {}
    colors = {
        "HadCRUT5": "#0485D1",
        "NOAAGlobalTemp": "#EB6F0A",
        "BerkeleyEarth": "#2000B1",
        "ERA5 (C3S-CDS)": "#0485D1",
    }
    for dataset in comparison_data.columns:
        (scatters[dataset],) = ax.plot(
            comparison_data.index,
            comparison_data[dataset],
            color=colors[dataset],
            marker="o",
            linewidth=0,
            ms=0.5,
            label=dataset,
            zorder=4,
        )

    return scatters


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

        ax.plot(scenario_data.loc[:, scen], color=color, linewidth=1, zorder=4)


def plot_prediction_data(ax, prediction, prediction_uncertainty):
    ax.scatter(
        2025,
        prediction,
        color="black",
        marker="D",
        s=1,
    )
    ax.errorbar(
        2025,
        prediction,
        yerr=std_to_90pCI(prediction_uncertainty),
        color="black",
        linewidth=0.7,
        capsize=0,
        capthick=0,
    )


def add_boxes(ax, decadal_data, var):
    boxes = ax.bxp(
        [
            {
                "med": ipcc_ref[var]["median"],
                "q1": ipcc_ref[var]["lower"],
                "q3": ipcc_ref[var]["upper"],
                "whislo": ipcc_ref[var]["median"],
                "whishi": ipcc_ref[var]["median"],
            },
            {
                "med": decadal_data.loc[2015][f"ClimTrace_{var}_DecadalMean"],
                "q1": decadal_data.loc[2015][f"ClimTrace_{var}_DecadalMean"]
                - std_to_90pCI(
                    decadal_data.loc[2015][
                        f"ClimTrace_{var}_DecadalMean_1sigma"
                    ]
                ),
                "q3": decadal_data.loc[2015][f"ClimTrace_{var}_DecadalMean"]
                + std_to_90pCI(
                    decadal_data.loc[2015][
                        f"ClimTrace_{var}_DecadalMean_1sigma"
                    ]
                ),
                "whishi": decadal_data.loc[2015][
                    f"ClimTrace_{var}_DecadalMean"
                ],
                "whislo": decadal_data.loc[2015][
                    f"ClimTrace_{var}_DecadalMean"
                ],
            },
            {
                "med": decadal_data.loc[2030][f"ClimTrace_{var}_DecadalMean"],
                "q1": decadal_data.loc[2030][f"ClimTrace_{var}_DecadalMean"]
                - std_to_90pCI(
                    decadal_data.loc[2030][
                        f"ClimTrace_{var}_DecadalMean_1sigma"
                    ]
                ),
                "q3": decadal_data.loc[2030][f"ClimTrace_{var}_DecadalMean"]
                + std_to_90pCI(
                    decadal_data.loc[2030][
                        f"ClimTrace_{var}_DecadalMean_1sigma"
                    ]
                ),
                "whishi": decadal_data.loc[2030][
                    f"ClimTrace_{var}_DecadalMean"
                ],
                "whislo": decadal_data.loc[2030][
                    f"ClimTrace_{var}_DecadalMean"
                ],
            },
        ],
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
        0.45,
        "AR6 2011-2020",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )
    ax.text(
        1.8,
        0.45,
        "CY2015-20ymean",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )
    ax.text(
        2.8,
        0.45,
        "CY2030-20ymean",
        ha="left",
        va="bottom",
        rotation=90,
        fontsize=6,
        color="black",
    )


# FORMATTING STUFF

def add_text(
    ax, text, x, y, transform, va="top", ha="left", fontsize=6, color="grey"
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


def add_legend(ax, entries, fontsize, bbox_to_anchor):
    legend = ax.legend(
        entries.values(),
        entries.keys(),
        loc="upper left",
        framealpha=0,
        fontsize=fontsize,
        bbox_to_anchor=bbox_to_anchor,
        borderaxespad=0,
    )

    legend.get_frame().set_linewidth(0)
    legend.get_frame().set_boxstyle("Round", pad=0, rounding_size=0)
    ax.add_artist(legend)


def format_axis(ax):
    ax.grid(zorder=0, alpha=0.1, linewidth=1)

    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    ax.xaxis.set_tick_params(labelsize=6)
    ax.yaxis.set_tick_params(labelsize=6)

    ax.set_xlim(1960, 2035)
    ax.set_ylim(0, 2)


def format_suppaxis(ax):
    ax.set_axis_off()
    ax.set_ylim(0, 2)
    ax.set_xlim(0.5, 3.5)


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

    # basic layout
    fig = plt.figure(figsize=(19 / 2.54, 0.85 * 9.44 / 2.54))
    gs = gridspec.GridSpec(1, 6, width_ratios=[3.95, 0.5, 0.6, 3.95, 0.5, 0.6])

    ax1 = fig.add_subplot(gs[0])
    ax1_1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[3])
    ax2_1 = fig.add_subplot(gs[4])

    ax1.set_ylabel("Anomaly relative to Mean1850-1900 (°C)")

    for axes, var in zip([[ax1, ax1_1], [ax2, ax2_1]], ["GMST", "GSAT"]):
        # load
        annual_data = rd.read_annual_data(
            data_dir, var, timerange=(1960, 2024)
        )
        decadal_data = rd.read_decadal_data(
            data_dir, var, timerange=(1960, 2034)
        )
        comparison_data = rd.read_comparison_data(data_dir, var)
        scenario_data = rd.read_scenario_data(
            data_dir, var, timerange=(2021, 2035)
        )
        prediction, prediction_uncertainty = rd.read_prediction_data(
            data_dir, var
        )

        # plot
        annual_line = plot_annual_data(axes[0], annual_data, var)
        decadal_line = plot_decadal_data(axes[0], decadal_data, var)
        plot_scenario_data(axes[0], scenario_data)
        plot_prediction_data(axes[0], prediction, prediction_uncertainty)
        comparison_legend_entries = plot_comparison_data(
            axes[0], comparison_data
        )

        add_boxes(axes[1], decadal_data, var)

        # add legend
        legend_entries = {
            "annual mean (and 90% CI)": annual_line,
            "decadal|20y mean (and 90% CI)": decadal_line,
        }

        add_legend(
            axes[0],
            comparison_legend_entries,
            fontsize=6,
            bbox_to_anchor=(0.3, 0.15),
        )
        add_legend(
            axes[0], legend_entries, fontsize=7, bbox_to_anchor=(0, 0.93)
        )

        # format panel
        format_axis(axes[0])
        format_suppaxis(axes[1])

        # helpful lines
        axes[0].vlines(
            2023,
            ymin=0,
            ymax=2,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
            )
        axes[0].hlines(
            [1.5, ipcc_ref[var]["median"]],
            xmin=1960,
            xmax=2045,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
            clip_on=False,
        )

        add_text(
            axes[0],
            "Paris Climate Goal 1.5°C",
            1961,
            1.48,
            transform=axes[0].transData,
        )
        add_text(
            axes[0],
            "IPCC AR6 2011-2020 1.09°C",
            1961,
            1.07,
            transform=axes[0].transData,
        )

        # panel title
        add_text(
            axes[0],
            f"{var} change",
            0.02,
            0.98,
            fontsize=8,
            color="black",
            transform=axes[0].transAxes,
        )

    # panel labels
    ax1.text(
        -0.15, 1, "a", fontsize=10, fontweight=900, transform=ax1.transAxes
    )
    ax2.text(
        -0.15, 1, "b", fontsize=10, fontweight=900, transform=ax2.transAxes
    )

    # tight layout
    fig.tight_layout()
    plt.subplots_adjust(wspace=0)

    # save
    plt.savefig(
        os.path.join(
            fig_dir,
            "ClimTrace_Fig1ab_1960-2035-GMST-GSAT_v20250417.png",
        ),
        dpi=600,
    )


if __name__ == "__main__":
    main()
