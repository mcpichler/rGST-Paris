
# Theme song:   Sympathy For The Devil
# Artist:       The Rolling Stones
# Album:        Beggars Banquet
# Released:     1968

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


# HELPFUL BITS

def std_to_90pCI(std):
    return 1.645 * std


def hex_to_rgb(hexcode):
    h = hexcode.strip("#")
    rgb = np.asarray(list(int(h[i : i + 2], 16) for i in (0, 2, 4)))

    return rgb


# PLOTTING STUFF

def plot_annual_data(ax, annual_data, var):
    (annual_line,) = ax.plot(
        annual_data.index,
        annual_data[f"ClimTrace_{var}"],
        color="black",
        marker="o",
        ms=0.5,
        linewidth=0.5,
        label="annual mean (and 90% CI)",
        zorder=2,
    )

    ax.errorbar(
        annual_data.index,
        annual_data[f"ClimTrace_{var}"],
        yerr=std_to_90pCI(annual_data[f"ClimTrace_{var}_1sigma"]),
        color="black",
        linewidth=0.5,
        capsize=0,
    )


def plot_decadal_data(ax, decadal_data, var):
    (decadal_line,) = ax.plot(
        decadal_data.index,
        decadal_data[f"ClimTrace_{var}_DecadalMean"],
        color="#8C000F",
        marker="o",
        ms=0.5,
        linewidth=0.5,
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
        2024,
        prediction,
        color="black",
        marker="D",
        s=1,
    )
    ax.errorbar(
        2024,
        prediction,
        yerr=std_to_90pCI(prediction_uncertainty),
        color="black",
        linewidth=0.7,
        capsize=0,
        capthick=0,
    )


def draw_exceedance_indicator(ax):
    ax.hlines(1.7, xmin=0.55, xmax=0.85, color="#8C000F", linewidth=1)
    ax.vlines(
        [0.55, 0.85],
        ymin=1.05,
        ymax=2.65,
        color="black",
        linewidth=0.5,
        clip_on=False,
    )
    ax.text(
        0.7,
        1.83,
        "Exceedance",
        va="bottom",
        ha="center",
        rotation=90,
        fontsize=6,
    )
    ax.text(
        0.7, 1.6, "Paris range", va="top", ha="center", rotation=90, fontsize=6
    )


def draw_parisclass_indicator(ax):
    def draw_gradient_rectangle(
        ax, x, y, width, height, color, alpha1, alpha2, n
    ):
        color_rgb = hex_to_rgb(color) / 255.0

        gradient_color = []

        for i in range(n):
            interp_alpha = (1 - i / n) * alpha1 + (i / n) * alpha2
            ax.add_patch(
                plt.Rectangle(
                    (x, y + (i * height / n)),
                    width,
                    height / n,
                    color=(*color_rgb, interp_alpha),
                    linewidth=0,
                    zorder=0,
                    clip_on=False,
                )
            )

    draw_gradient_rectangle(
        ax, 0.1, 2.6, 0.3, 0.05, color="#C9323C", alpha1=1, alpha2=0, n=100
    )
    draw_gradient_rectangle(
        ax, 0.1, 2, 0.3, 0.6, color="#C9323C", alpha1=1, alpha2=1, n=100
    )
    draw_gradient_rectangle(
        ax, 0.1, 1.7, 0.3, 0.3, color="#E52D20", alpha1=1, alpha2=1, n=100
    )
    draw_gradient_rectangle(
        ax, 0.1, 1.5, 0.3, 0.2, color="#1EA4C2", alpha1=1, alpha2=1, n=100
    )
    draw_gradient_rectangle(
        ax, 0.1, 1, 0.3, 0.5, color="#028F1E", alpha1=0, alpha2=1, n=100
    )


# FORMAT STUFF

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


def format_axis(ax):

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Anomaly relative to Mean1850-1900 (°C)")

    ax.xaxis.set_major_locator(MultipleLocator(50))
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    ax.xaxis.set_tick_params(labelsize=6)
    ax.yaxis.set_tick_params(labelsize=6)

    ax.set_xlim(1850, 2050)
    ax.set_ylim(-0.2, 2.6)


def format_suppaxis(ax):
    ax.set_axis_off()
    ax.set_ylim(-0.2, 2.6)
    ax.set_xlim(0.0, 1.0)


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

    for var, panel in zip(["GSAT", "GMST"], ["a", "b"]):

        # basic layout
        fig = plt.figure(figsize=(11 / 2.54, 0.85 * 9.44 / 2.54))
        gs = gridspec.GridSpec(1, 2, width_ratios=[9, 1])

        ax1 = fig.add_subplot(gs[0])
        ax1_1 = fig.add_subplot(gs[1])

        # load
        annual_data = rd.read_annual_data(
            data_dir, var, timerange=(1850, 2024)
        )
        decadal_data = rd.read_decadal_data(
            data_dir, var, timerange=(1850, 2034)
        )
        scenario_data = rd.read_scenario_data(
            data_dir, var, timerange=(2021, 2050)
        )
        # prediction, prediction_uncertainty = rd.read_prediction_data(
        #     data_dir, var
        # )

        # calculate some stats
        preind_mean = annual_data[f"ClimTrace_{var}"].loc[1850:1900].mean()
        alignperiod_mean = (
            annual_data[f"ClimTrace_{var}"].loc[1951:1980].mean()
        )
        ltc_2015 = decadal_data[f"ClimTrace_{var}_DecadalMean"].loc[2015]

        # plot
        plot_annual_data(ax1, annual_data, var)
        plot_decadal_data(ax1, decadal_data, var)
        plot_scenario_data(ax1, scenario_data)
        # plot_prediction_data(ax1, prediction, prediction_uncertainty)

        if var == "GSAT":
            draw_exceedance_indicator(ax1_1)
            draw_parisclass_indicator(ax1_1)

        # legend
        if var == "GSAT":
            bbox = (0, 1.06*0.411)
        else:
            bbox = (0, 0.411)
        add_legend(ax1, fontsize=7, bbox_to_anchor=bbox)

        # format panel
        format_axis(ax1)
        format_suppaxis(ax1_1)

        # helpful lines
        if var == "GSAT":
            ax1.hlines(
                [
                    2.0,
                    1.7,
                ],
                xmin=1850,
                xmax=2050,
                color="black",
                alpha=0.2,
                linewidth=1,
                zorder=0,
            )
        else:
            ax1.hlines(
                [
                    2.0,
                    1.7,
                ],
                xmin=2023,
                xmax=2050,
                color="black",
                alpha=0.2,
                linewidth=1,
                zorder=0,
            )

        ax1.hlines(
            [
                1.5,
                ltc_2015,
                preind_mean,
            ],
            xmin=1850,
            xmax=2050,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

        ax1.hlines(
            alignperiod_mean,
            xmin=1951,
            xmax=2050,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

        ax1.vlines(
            2023,
            ymin=-0.2,
            ymax=2.6,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

        if var == "GSAT":
            add_text(
                ax1,
                "Paris effort goal T1.5C (<1.5°C)",
                1852,
                1.4,
                va="center",
                color="#373737",
                transform=ax1.transData,
            )
            add_text(
                ax1,
                "Paris limit goal WB2C (<1.7°C)",
                1852,
                1.6,
                va="center",
                color="#373737",
                transform=ax1.transData,
            )
            add_text(
                ax1,
                "Paris exceedance RB2C (<2°C)",
                1852,
                1.85,
                va="center",
                color="#373737",
                transform=ax1.transData,
            )
            add_text(
                ax1,
                "Paris exceedance EX2C (>2°C)",
                1852,
                2.18,
                color="#373737",
                transform=ax1.transData,
            )

        else:
            add_text(
                ax1,
                "Paris climate goal 1.5°C",
                1852,
                1.48,
                color="grey",
                transform=ax1.transData,
            )

        add_text(
            ax1,
            f"Preindustrial reference {np.round(abs(preind_mean), 2)}°C",
            1935,
            preind_mean - 0.02,
            color="grey",
            transform=ax1.transData,
        )
        add_text(
            ax1,
            f"Mean1951-1980 {np.round(alignperiod_mean, 3)}°C",
            1979,
            alignperiod_mean - 0.02,
            color="grey",
            transform=ax1.transData,
        )
        add_text(
            ax1,
            f"CY2015-20ymean {np.round(ltc_2015, 2)}°C",
            1852,
            ltc_2015 - 0.02,
            color="grey",
            transform=ax1.transData,
        )

        # panel title
        add_text(
            ax1,
            f"{var} change 1850-2023|2024-2050",
            0.02,
            0.98,
            fontsize=8,
            color="black",
            transform=ax1.transAxes,
        )

        # panel labels
        ax1.text(
            -0.12, 1, panel, fontsize=10, fontweight=900, transform=ax1.transAxes
        )


        # tight layout
        fig.tight_layout()
        plt.subplots_adjust(wspace=0)

        # save
        plt.savefig(
            os.path.join(
                fig_dir,
                f"ClimTrace_Fig4{panel}_1850-2050-{var}_v20250417.png",
            ),
            dpi=600,
        )


if __name__ == "__main__":
    main()
