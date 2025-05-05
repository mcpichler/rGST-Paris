
# Theme song:   I Don't Know
# Artist:       Lisa Hannigan
# Album:        Sea Sew
# Released:     2008

import os
import math
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import plotutils.pu1_datareaders as rd


# MATPLOTLIB PARAMS
matplotlib.rcParams["font.family"] = ["Lato", "sans-serif"]


# HELPFUL BITS

def std_to_90pCI(std):
    return 1.645 * std


def calculate_total_spread(df, period):
    datapoints = df.loc[period[0] : period[1]].values.flatten()
    sigma = np.sqrt((datapoints**2).sum()/len(datapoints))
    return std_to_90pCI(sigma)


def find_number_inside_range(halfrange, data, timerange):

    halfrange = halfrange.loc[timerange[0] : timerange[1]]
    data = data.loc[timerange[0] : timerange[1]]

    data_inside_range = data.where((data < halfrange) & (data > -halfrange))

    n_data_inside_range = len(data_inside_range.dropna())
    f_data_inside_range = n_data_inside_range / len(data)

    return n_data_inside_range, f_data_inside_range


# PLOTTING STUFF


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
            ms=1,
            label=dataset,
            zorder=4,
        )

    return scatters


def plot_uncertainty_corridor(ax, uncertainty, color, alpha):
    ax.fill_between(
        uncertainty.loc[:2023].index,
        -std_to_90pCI(uncertainty.loc[:2023].values),
        std_to_90pCI(uncertainty.loc[:2023].values),
        color=color,
        alpha=alpha,
        linewidth=0,
    )


# FORMATTING STUFF

def add_text(
    ax, text, x, y, transform, va="top", ha="left", fontsize=12, color="black"
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


def add_legend(ax, entries, bbox_to_anchor):
    legend = ax.legend(
        entries.values(),
        entries.keys(),
        loc="upper right",
        framealpha=0,
        bbox_to_anchor=bbox_to_anchor,
    )

    legend.texts[1].set_position((-240, 0))


def format_axis(ax):
    ax.grid(zorder=0, alpha=0.1, linewidth=1)

    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    ax.yaxis.set_minor_locator(MultipleLocator(0.01))

    ax.set_xlim(1850, 2025)
    ax.set_ylim(-0.25, 0.25)


def add_inside_uncertainty_infobox(
    fig, ax, n_inside, f_inside, since, fontsize=10, textboxpad=0.3
):

    if "ERA5 (C3S-CDS)" in n_inside.keys():
       strings = [
            f"{n[0]}: {n[1]:0>2}/46 ({np.round(f[1]*100, 2):0>4.1f} %)\n"
            for n, f in zip(n_inside.items(), f_inside.items())
        ]
    else:
        strings = [
            f"{n[0]}: {n[1]:0>2} ({np.round(f[1]*100, 2):0>4.1f} %)\n"
            for n, f in zip(n_inside.items(), f_inside.items())
        ]

    text = f"Inside CI90-range since {since}:\n" + "".join(strings)[:-1]

    t = ax.annotate(
        text,
        xy=(1, 0),
        size=fontsize,
        textcoords="offset points",
        ha="left",
        va="bottom",
        xycoords=ax.transAxes,
    )

    t.set_bbox(
        {
            "boxstyle": f"square,pad={textboxpad}",
            "fc": "white",
            "ec": "black",
            "linewidth": 0.5,
        }
    )

    fig.canvas.draw()
    bbox = t.get_window_extent()
    bbox_width_points = math.ceil(bbox.width / fig.dpi * 72)
    current_xytext = t.get_position()
    new_xytext = (
        current_xytext[0] - bbox_width_points - fontsize * textboxpad,
        current_xytext[1] + fontsize * textboxpad,
    )
    t.set_position(new_xytext)
    fig.canvas.draw()


# MAIN

def main():
    # paths
    input_data_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "02_output_data",
    )

    fig_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "04_figures",
    )

    for var, panel in zip(["GMST", "GSAT"], ["a", "b"]):
        # basic layout
        fig = plt.figure(figsize=(17 / 2.54, 0.75 * 17 / 2.54), dpi=600)
        ax = fig.add_subplot(111)

        ax.set_ylabel("Uncertainty range | data deviates 1850-2024 (°C)")
        ax.set_xlabel("Time (years)")

        # load
        annual_data = rd.read_annual_data(
            input_data_dir, var, timerange=(1850, 2024)
        )
        comparison_data = rd.read_comparison_data(input_data_dir, var)

        if var == "GMST":
            base_sigma = rd.read_hadcrut_sigma(input_data_dir)
        else:
            base_sigma = rd.read_annual_data(
                input_data_dir, "GMST", timerange=(1850, 2024)
            )[f"ClimTrace_GMST_1sigma"]
            comparison_data = comparison_data.loc[1950:]

        # subtract climtrace baseline
        baseline = annual_data[f"ClimTrace_{var}"].copy()
        comparison_data_dev = comparison_data.subtract(baseline, axis=0)

        # calculate some stats
        n_inside_uncertainty = {}
        f_inside_uncertainty = {}
        if var == "GSAT":
            timerange = (1979, 2024)
        else:
            timerange = (1850, 2024)

        for c in comparison_data_dev.columns:
            n_inside_uncertainty[c], f_inside_uncertainty[c] = (
                find_number_inside_range(
                    std_to_90pCI(annual_data[f"ClimTrace_{var}_1sigma"]),
                    comparison_data_dev[c],
                    timerange=timerange,
                )
            )

        preind_mean = annual_data[f"ClimTrace_{var}"].loc[1850:1900].mean()
        alignperiod_mean = (
            annual_data[f"ClimTrace_{var}"].loc[1951:1980].mean()
        )
        alignperiod_spread = calculate_total_spread(
            comparison_data_dev, (1951, 1980)
        )
        recent_spread = calculate_total_spread(comparison_data_dev, (1979, 2024))

        # plot
        scatters = plot_comparison_data(ax, comparison_data_dev)

        plot_uncertainty_corridor(ax, base_sigma, "black", alpha=0.15)
        plot_uncertainty_corridor(
            ax, annual_data[f"ClimTrace_{var}_1sigma"], "grey", alpha=0.2
        )

        # zero-line
        zeroline = ax.hlines(
            0,
            xmin=1850,
            xmax=2024,
            color="black",
            linewidth=1,
            label="ClimTrace",
        )

        # add legend
        (dummy,) = plt.plot([], [], linewidth=0)
        if var == "GMST":
            dummytitle = r"$\it{Input}$ $\it{datasets}$:"
        else:
            dummytitle = r"$\it{Verification}$ $\it{dataset}:$"
        legend_entries = {
            "ClimTrace": zeroline,
            dummytitle: dummy,
        }
        legend_entries.update(scatters)

        add_legend(ax, legend_entries, bbox_to_anchor=(1, 0.95))

        # infobox on CI90-adherance of datasets
        add_inside_uncertainty_infobox(
            fig,
            ax,
            n_inside_uncertainty,
            f_inside_uncertainty,
            since=timerange[0],
        )

        # format panel
        format_axis(ax)

        # panel title
        add_text(
            ax,
            f"{var} uncertainty range and data deviates (Ref: ClimTrace)",
            0.02,
            0.98,
            transform=ax.transAxes,
        )

        # infotext on stats
        if var == "GSAT":
            text = (
                f"ClimTrace Mean1850-1900: {np.round(abs(preind_mean), 3):.3f}°C\n"
                + f"ClimTrace+ERA5 Mean1951-1980: {np.round(alignperiod_mean, 3):.3f}°C\n"
                + f"Spread-CI90 of ERA5 1951-1980: {np.round(alignperiod_spread, 3):.3f}°C\n"
                + f"Spread-CI90 of ERA5 1979-2024: {np.round(recent_spread, 3):.3f}°C\n"
                + "(annual data spread of ERA5 vs ClimTrace)"
            )
            ypos = -0.16

        else:
            text = (
                f"ClimTrace Mean1850-1900: {np.round(abs(preind_mean), 3):.3f}°C\n"
                + f"ClimTrace+Datasets Mean1951-1980: {np.round(alignperiod_mean, 3):.3f}°C\n"
                + f"Spread-CI90 of Datasets 1951-1980: {np.round(alignperiod_spread, 3):.3f}°C\n"
                + "(annual data spread of Datasets vs ClimTrace)"
            )
            ypos = -0.18

        add_text(
            ax,
            text,
            x=1865,
            y=ypos,
            fontsize=8,
            transform=ax.transData,
        )

        # helpful lines
        ax.vlines(
            1950,
            ymin=-0.25,
            ymax=2.6,
            color="black",
            alpha=0.2,
            linewidth=1,
            zorder=0,
        )

        # panel labels
        ax.text(
            -0.125, 1, panel, fontsize=15, fontweight=900, transform=ax.transAxes
        )

        # save
        plt.savefig(
            os.path.join(
                fig_dir,
                f"ClimTrace_Fig2{panel}_{var}_deviates_v20250417.png",
            ),
            dpi=600,
        )


if __name__ == "__main__":
    main()
