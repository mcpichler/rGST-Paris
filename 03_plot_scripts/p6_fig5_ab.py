
# Theme song:   Imagine
# Artist:       Zaz
# Album:        Isa
# Released:     2021

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


def get_pclass_color(pclass):
    pclasscolors = {
        "T1.5": "#028F1E",
        "WB2C": "#1EA4C2",
        "RB2C": "#E52D20",
        "EX2C": "#C9323C",
    }

    if type(pclass) == str:
        return pclasscolors[pclass]

    else:
        if pclass < 1.5:
            return pclasscolors["T1.5"]
        elif pclass < 1.7:
            return pclasscolors["WB2C"]
        elif pclass < 2:
            return pclasscolors["RB2C"]
        else:
            return pclasscolors["EX2C"]


def get_ssp_color(ssp):
    ssp_colors = {
        "ssp119": "#1EA4C2",
        "ssp126": "#2A3A5C",
        "ssp245": "#D9853B",
        "ssp585": "#C9323C",
    }

    return ssp_colors[ssp]


# PLOTTING STUFF

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
        decadal_data.loc[1960:].index,
        decadal_data.loc[1960:][f"ClimTrace_{var}_DecadalMean"],
        color="#8C000F",
        marker="o",
        ms=1.5,
        linewidth=1,
        label="decadal|20y mean (and 90% CI)",
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

    ax.plot(
        decadal_data.loc[2023:].index,
        decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean"]
        + std_to_90pCI(
            decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        color="#8C000F",
        linewidth=0.5,
        linestyle="dotted",
        zorder=3,
    )

    ax.plot(
        decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean"]
        - std_to_90pCI(
            decadal_data.loc[2023:][f"ClimTrace_{var}_DecadalMean_1sigma"]
        ),
        color="#8C000F",
        linewidth=0.5,
        linestyle="dotted",
        zorder=3,
    )


def plot_scenario_data(ax, scenario_data, linestyle="-"):
    for scen in scenario_data.columns:
        color = get_ssp_color(scen)
        ax.plot(scenario_data.loc[:, scen], color=color, linewidth=1, linestyle=linestyle, zorder=4)


def add_sgwr(ax, year, lower, upper, color, boxwidth=0.5):
    # little hack to cover the scenarios below the SGWR
    add_box_for_year(
        ax,
        year,
        (upper+lower)/2,
        (upper-lower)/2,
        color=get_pclass_color("RB2C"),
        filled=False,
        centerdot=False
        )

    ax.vlines(
        x=[year-boxwidth/2, year+boxwidth/2],
        ymin=lower,
        ymax=upper,
        color=color,
        linewidth=0.5,
        zorder=6
        )
    ax.hlines(
        y=[lower, upper],
        xmin=year-boxwidth/2,
        xmax=year+boxwidth/2,
        color=color,
        linewidth=0.5,
        zorder=6
        )


def add_box_for_year(
    ax, year, central_estimate, halfrange, color, boxwidth=0.5, markersize=2.5, filled=True, centerdot=True,
):
    lower_limit = central_estimate - halfrange
    upper_limit = central_estimate + halfrange

    if filled:
        facecolor=color
        zorder=5
    else:
        facecolor="white"
        zorder=4

    box = ax.bxp(
        [
            {
                "med": central_estimate,
                "q1": lower_limit,
                "q3": upper_limit,
                "whislo": central_estimate,
                "whishi": central_estimate,
            }
        ],
        widths=[boxwidth],
        positions=[year],
        patch_artist=True,
        showfliers=False,
        zorder=zorder,
    )

    box["boxes"][0].set(facecolor=facecolor, edgecolor=color, alpha=1)
    box["boxes"][0].set(linewidth=markersize / 5)
    box["medians"][0].set(linewidth=0)

    for whisker, cap in zip(box["whiskers"], box["caps"]):
        whisker.set_visible(False)
        cap.set_visible(False)

    if centerdot:
        ax.plot(
            year,
            central_estimate,
            marker="o",
            ms=markersize,
            color=color,
            markeredgewidth=markersize / 5,
            markeredgecolor="black",
            zorder=6,
        )


def draw_exceedance_indicator(ax):
    ax.hlines(1.7, xmin=0.55, xmax=0.85, color="#8C000F", linewidth=1)
    ax.vlines(
        [0.55, 0.85],
        ymin=1.05,
        ymax=2.55,
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
        ax,
        0.1,
        2.5,
        0.3,
        0.05,
        color=get_pclass_color("EX2C"),
        alpha1=1,
        alpha2=0,
        n=100,
    )
    draw_gradient_rectangle(
        ax,
        0.1,
        2,
        0.3,
        0.5,
        color=get_pclass_color("EX2C"),
        alpha1=1,
        alpha2=1,
        n=100,
    )
    draw_gradient_rectangle(
        ax,
        0.1,
        1.7,
        0.3,
        0.3,
        color=get_pclass_color("RB2C"),
        alpha1=1,
        alpha2=1,
        n=100,
    )
    draw_gradient_rectangle(
        ax,
        0.1,
        1.5,
        0.3,
        0.2,
        color=get_pclass_color("WB2C"),
        alpha1=1,
        alpha2=1,
        n=100,
    )
    draw_gradient_rectangle(
        ax,
        0.1,
        1,
        0.3,
        0.5,
        color=get_pclass_color("T1.5"),
        alpha1=0,
        alpha2=1,
        n=100,
    )


# FORMAT STUFF

def add_text(
    ax,
    text,
    x,
    y,
    transform,
    va="top",
    ha="left",
    fontsize=6,
    color="grey",
    rotation=0,
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
        rotation=rotation,
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

    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(0.1))

    ax.xaxis.set_tick_params(labelsize=6)
    ax.yaxis.set_tick_params(labelsize=6)

    ax.set_xlim(2010, 2050)
    ax.set_ylim(1.0, 2.5)

    ax.set_xlabel("Time (years)")


def format_boxaxis(ax):

    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(0.1))

    ax.xaxis.set_tick_params(labelsize=6)
    ax.yaxis.set_tick_params(labelsize=6)

    ax.set_xlim(2020, 2100)
    ax.set_ylim(1.0, 2.5)

    ax.set_xlabel("Time (years)")


def format_suppaxis(ax):
    ax.set_axis_off()
    ax.set_ylim(1.0, 2.5)
    ax.set_xlim(0.0, 1.0)


def turn_axis_invisible(ax):
    ax.set_facecolor("none")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


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
    fig = plt.figure(figsize=(17 / 2.54, 0.85 * 9.44 / 2.54), dpi=600)
    gs = gridspec.GridSpec(1, 4, width_ratios=[9, 1, 0.7, 7])

    ax1 = fig.add_subplot(gs[0])
    ax1_1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[3])

    ax1.set_ylabel("Anomaly relative to Mean1850-1900 (°C)")

    # load
    annual_data = rd.read_annual_data(data_dir, "GSAT", timerange=(2010, 2024))
    decadal_data = rd.read_decadal_data(
        data_dir, "GSAT", timerange=(2010, 2040)
    )
    scenario_data = rd.read_scenario_data(
        data_dir, "GSAT", timerange=(2021, 2100)
    )

    # plot
    plot_annual_data(ax1, annual_data, "GSAT")
    plot_annual_data(ax2, annual_data, "GSAT")
    plot_decadal_data(ax1, decadal_data.loc[:2034], "GSAT")
    plot_decadal_data(ax2, decadal_data.loc[:2023], "GSAT")
    plot_scenario_data(ax1, scenario_data)

    draw_exceedance_indicator(ax1_1)
    draw_parisclass_indicator(ax1_1)

    plot_scenario_data(ax2, scenario_data)

    # legend
    add_legend(ax1, fontsize=7, bbox_to_anchor=(0, 0.93))

    # format panel
    format_axis(ax1)
    format_suppaxis(ax1_1)
    format_boxaxis(ax2)

    # add paris class boxes;
    # bit hack-y because of weird plt.bxp()-influence on the x-axis.
    # So we just plot them in transparent overlay-axes.
    bxp_ax1 = fig.add_subplot(gs[0])
    bxp_ax2 = fig.add_subplot(gs[3])
    format_axis(bxp_ax1)
    format_boxaxis(bxp_ax2)
    turn_axis_invisible(bxp_ax1)
    turn_axis_invisible(bxp_ax2)

    add_box_for_year(
        bxp_ax1,
        2024,
        decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2024],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("T1.5"),
    )

    add_box_for_year(
        bxp_ax1,
        2028,
        decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2028],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("WB2C"),
    )

    add_box_for_year(
        bxp_ax1,
        2032,
        decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2032],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2032]
        ),
        color=get_pclass_color("WB2C"),
        filled=False,
    )

    add_box_for_year(
        bxp_ax1,
        2032,
        decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2032],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("WB2C"),
    )

    add_sgwr(
        bxp_ax1,
        2047,
        scenario_data["ssp119"].loc[2047]-std_to_90pCI(decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]),
        scenario_data["ssp585"].loc[2047]+decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2034]+std_to_90pCI(decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2034])-scenario_data["ssp585"].loc[2034],
        color=get_pclass_color("RB2C"),
        )

    add_sgwr(
        bxp_ax1,
        2036,
        scenario_data["ssp119"].loc[2036]-std_to_90pCI(decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]),
        scenario_data["ssp585"].loc[2036]+decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2034]+std_to_90pCI(decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2034])-scenario_data["ssp585"].loc[2034],
        color=get_pclass_color("RB2C"),
        )

    add_box_for_year(
        bxp_ax1,
        2036,
        scenario_data["ssp119"].loc[2037],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("WB2C"),
    )

    add_box_for_year(
        bxp_ax1,
        2036,
        scenario_data["ssp245"].loc[2036],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("RB2C"),
    )

    add_box_for_year(
        bxp_ax1,
        2047,
        scenario_data["ssp245"].loc[2047],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("EX2C"),
    )

    add_box_for_year(
        bxp_ax1,
        2047,
        scenario_data["ssp119"].loc[2047],
        std_to_90pCI(
            decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
        ),
        color=get_pclass_color("WB2C"),
    )

    # plot_scenario_data(bxp_ax1, scenario_data.loc[2040:])

    for y in np.arange(2024, 2100):
        add_box_for_year(
            bxp_ax2,
            y,
            scenario_data["ssp119"].loc[y],
            std_to_90pCI(
                decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
            ),
            color=get_pclass_color(scenario_data["ssp119"].loc[y]),
            boxwidth=0.6,
            markersize=1,
        )
    for y in np.arange(2028, 2100):
        add_box_for_year(
            bxp_ax2,
            y,
            scenario_data["ssp245"].loc[y],
            std_to_90pCI(
                decadal_data["ClimTrace_GSAT_DecadalMean_1sigma"].loc[2024]
            ),
            color=get_pclass_color(scenario_data["ssp245"].loc[y]),
            boxwidth=0.6,
            markersize=1,
        )

    # helpful lines
    for ax in [ax1, ax2]:
        ax.hlines(
            [
                2.0,
                1.7,
                1.5,
                # decadal_data["ClimTrace_GSAT_DecadalMean"].loc[2015]
            ],
            xmin=2010,
            xmax=2100,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

        ax.vlines(
            2023,
            ymin=0.8,
            ymax=1.5,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

    ax1.vlines(
        2028,
        ymin=0.8,
        ymax=1.6,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax1.vlines(
        2036,
        ymin=0.8,
        ymax=1.7,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax1.vlines(
        2047,
        ymin=0.8,
        ymax=1.55,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax2.vlines(
        2029,
        ymin=0.8,
        ymax=1.5,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax2.vlines(
        2059,
        ymin=0.8,
        ymax=1.5,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax2.vlines(
        2036,
        ymin=1.5,
        ymax=2.0,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    ax2.vlines(
        2046,
        ymin=1.7,
        ymax=2.15,
        color="black",
        alpha=0.2,
        linewidth=1,
        zorder=0,
    )

    add_text(
        ax1,
        "Paris effort goal T1.5C (<1.5°C)",
        2010.5,
        1.46,
        va="center",
        # color="#373737",
        color="black",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "Paris limit goal WB2C (<1.7°C)",
        2010.5,
        1.6,
        va="center",
        # color="#373737",
        color="black",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "Paris exceedance RB2C (<2°C)",
        2010.5,
        1.85,
        va="center",
        # color="#373737",
        color="black",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "Paris exceedance EX2C (>2°C)",
        2010.5,
        2.05,
        va="center",
        # color="#373737",
        color="black",
        fontsize=5,
        transform=ax1.transData,
    )

    # further explanatory text
    add_text(
        ax1,
        "CGWL\n2024",
        2024.2,
        1.25,
        va="center",
        ha="left",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "CYGWL\n2028",
        2028.2,
        1.35,
        va="center",
        ha="left",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "PGWL\n2032",
        2032.2,
        1.43,
        va="center",
        ha="left",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "SGWR\n2036",
        2036.2,
        1.44,
        va="center",
        ha="left",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "SGWR\n2047",
        2047.2,
        1.42,
        va="center",
        ha="left",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "T1.5C",
        2025.5,
        1.02,
        va="bottom",
        ha="center",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "WB2C",
        2032,
        1.02,
        va="bottom",
        ha="center",
        fontsize=5,
        transform=ax1.transData,
    )

    add_text(
        ax1,
        "WB2C or Exceedance",
        2041.5,
        1.02,
        va="bottom",
        ha="center",
        fontsize=5,
        transform=ax1.transData,
    )

    # SSP labels
    add_text(
        ax1,
        "SSP1-1.9",
        2043,
        1.58,
        ha="center",
        color=get_ssp_color("ssp119"),
        fontsize=5,
        transform=ax1.transData,
        rotation=-5,
    )
    add_text(
        ax1,
        "SSP1-2.6",
        2043,
        1.75,
        ha="center",
        color=get_ssp_color("ssp126"),
        fontsize=5,
        transform=ax1.transData,
        rotation=10,
    )
    add_text(
        ax1,
        "SSP2-4.5",
        2043,
        1.92,
        ha="center",
        color=get_ssp_color("ssp245"),
        fontsize=5,
        transform=ax1.transData,
        rotation=30,
    )
    add_text(
        ax1,
        "SSP5-8.5",
        2043,
        2.17,
        ha="center",
        color=get_ssp_color("ssp585"),
        fontsize=5,
        transform=ax1.transData,
        rotation=43,
    )

    add_text(
        ax2,
        "SSP1-1.9",
        2046,
        1.49,
        ha="center",
        color=get_ssp_color("ssp119"),
        fontsize=5,
        transform=ax2.transData,
        rotation=-15,
    )
    add_text(
        ax2,
        "SSP1-2.6",
        2055,
        1.82,
        ha="center",
        color=get_ssp_color("ssp126"),
        fontsize=5,
        transform=ax2.transData,
        rotation=10,
    )
    add_text(
        ax2,
        "SSP2-4.5",
        2061,
        2.26,
        ha="center",
        color=get_ssp_color("ssp245"),
        fontsize=5,
        transform=ax2.transData,
        rotation=47,
    )
    add_text(
        ax2,
        "SSP5-8.5",
        2048.5,
        2.4,
        ha="center",
        color=get_ssp_color("ssp585"),
        fontsize=5,
        transform=ax2.transData,
        rotation=67,
    )

    add_text(
        ax2,
        "T1.5C overshoot 2029-59",
        2044,
        1.34,
        va="bottom",
        ha="center",
        fontsize=5,
        transform=ax2.transData,
    )

    add_text(
        ax2,
        "Return to T1.5C 2060+",
        2060,
        1.24,
        va="bottom",
        ha="left",
        fontsize=5,
        transform=ax2.transData,
    )

    add_text(
        ax2,
        "RB2C 2036-46",
        2049,
        1.88,
        va="bottom",
        ha="left",
        fontsize=5,
        transform=ax2.transData,
    )
    add_text(
        ax2,
        "EX2C 2047+",
        2054,
        2.01,
        va="bottom",
        ha="left",
        fontsize=5,
        transform=ax2.transData,
    )

    # panel titles
    add_text(
        ax1,
        "GSAT change 2010-2023|2024-2050",
        0.02,
        0.98,
        fontsize=8,
        color="black",
        transform=ax1.transAxes,
    )

    add_text(
        ax2,
        "GSAT change\nStylized\nCYGWLs\n2024-2100",
        0.02,
        0.98,
        fontsize=8,
        color="black",
        transform=ax2.transAxes,
    )

    # panel labels
    ax1.text(
        -0.05, 1.05, "a", fontsize=10, fontweight=900, transform=ax1.transAxes
    )
    ax2.text(
        -0.05, 1.05, "b", fontsize=10, fontweight=900, transform=ax2.transAxes
    )

    # tight layout
    fig.tight_layout()
    plt.subplots_adjust(wspace=0)

    # save
    plt.savefig(
        os.path.join(
            fig_dir,
            "ClimTrace_Fig5ab_2010-2050-GSAT_v20250417.png",
        ),
        dpi=600,
    )


if __name__ == "__main__":
    main()
