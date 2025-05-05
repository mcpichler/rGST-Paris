
# Theme song:   Written In The Water
# Artist:       Gin Wigmore
# Album:        Blood To Bone
# Released:     2015

import os
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import MultipleLocator


# MATPLOTLIB PARAMS
matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = ["Lato", "sans-serif"]
matplotlib.rcParams["axes.titlesize"] = 8


# USEFUL BITS

def std_to_90pCI(std):
    return 1.645 * std


def hex_to_rgb(hexcode):
    h = hexcode.strip("#")
    rgb = np.asarray(list(int(h[i : i + 2], 16) for i in (0, 2, 4)))

    return rgb


def get_dataset_names_for_category(cat):
    dataset_names = {
        "GMST": ["HadCRUT5", "NOAAGloTemp", "BerkeleyEarth", "ERA5-GMST_INCLSI_F", "JRA-3Q-GMST_INCLSI_F", "ERA5-GMST_INCLSI", "JRA-3Q-GMST_INCLSI", "ERA5-GMST_NOSI_F", "JRA-3Q-GMST_NOSI_F",],
        "SST": ["HadSST4", "ERSSTv5", "IAPv4-SST", "ERA5-SST", "JRA-3Q-SST",],
        "LSAT": ["CRUTEM5", "GHCNv4", "BerkeleyEarth-Land", "ERA5-LSAT", "JRA-3Q-LSAT",],
        "SSAT": ["ERA5-SSAT", "JRA-3Q-SSAT",],
        "GSAT": ["ERA5-GSAT", "JRA-3Q-GSAT",],
        "CT": ["ClimTrace-GMST", "ClimTrace-GSAT"]
        }

    return dataset_names[cat]


def get_color_for_dataset(name):
    if "ERA" in name:
        return "tab:red"
    elif "JRA" in name:
        return "tab:cyan"
    elif "Had" in name or "CRU" in name:
        return "#0485D1"
    elif "GHCN" in name or "ERSST" in name or "NOAA" in name:
        return "#EB6F0A"
    elif "IAP" in name:
        return "#2000B1"
    elif "Berkeley" in name:
        return "#2000B1"
    elif "ClimTrace" in name:
        return "black"


def get_symbol_for_category(category):
    symbols = {
        "GMST":("|", 3),
        "SST":("d", 2),
        "LSAT":("+", 3),
        "SSAT":("D", 1.5),
        "GSAT":(7, 3),
        "CT":("x", 3),
        }

    return symbols[category]


def get_color_for_category(category):
    colors = {
        "GMST":"black",
        "SST":"#2000B1",
        "LSAT":"tab:green",
        "SSAT":"tab:cyan",
        "GSAT":"xkcd:crimson",
        }

    return colors[category]

def get_legend_position(cat):
    legend_positions = {
        "GMST": (0.5, 0.9),
        "SST": (0.3, 0.9),
        "LSAT": (0.75, 0.9),
        "GSAT": (0.55, 0.3),
        "SSAT": (0.13, 0.3),
        "PROF": (0.02, 0.9),
        }

    return legend_positions[cat]


def find_possible_minmax(data, data_unc):
    minimum = min((data-data_unc).values)
    maximum = max((data+data_unc).values)

    return (minimum, maximum)

# READING STUFF

def read_surface_trend_rates(input_dir):
    surface_trends = pd.read_csv(
        os.path.join(
            input_dir,
            "SurfTempTrendRates_1991-2023_AllDatasets.csv",
            ),
        index_col=0,
        )
    surface_trend_uncerts = pd.read_csv(
        os.path.join(
            input_dir,
            "SurfTempTrendRateUncerts_1991-2023_AllDatasets.csv",
            ),
        index_col=0,
        )

    return surface_trends, surface_trend_uncerts


def read_trend_profile(input_dir, name):
    prof = pd.read_csv(
        os.path.join(
            input_dir,
            f"{name}_1991-2023_TrendProfile.csv",
            ),
        index_col=0,
        )

    if name == "IAPv4":
        prof.index = -prof.index

    return prof

def read_trend_uncertainty_profile(input_dir, name):
    prof = pd.read_csv(
        os.path.join(
            input_dir,
            f"{name}_1991-2023_TrendProfile_1sigma.csv",
            ),
        index_col=0,
        )

    if name == "IAPv4":
        prof.index = -prof.index

    return prof


def read_gmst_to_gsat_factors(input_data_dir):
    gmst2gsat = pd.read_csv(
        os.path.join(
            input_data_dir,
            "GMST2GSATfactors_ERA5toClimTrace.csv",
            ),
        index_col=0,
        )

    return gmst2gsat


# PLOTTING STUFF

def add_box(
    ax, position, center, halfrange, color="white", alpha=1, boxwidth=0.7, add_center_dot=False, add_dots=None, fadeout=None,
):

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
                    zorder=6,
                    clip_on=False,
                )
            )

    if add_dots:
        lower_limit=min(add_dots)
        upper_limit=max(add_dots)
    else:
        lower_limit = center - halfrange
        upper_limit = center + halfrange

    box = ax.bxp(
        [
            {
                "med": center,
                "q1": lower_limit,
                "q3": upper_limit,
                "whislo": center,
                "whishi": center,
            }
        ],
        widths=[boxwidth],
        positions=[position],
        patch_artist=True,
        showfliers=False,
        zorder=4,
    )

    box["boxes"][0].set(facecolor=color, alpha=alpha)
    box["boxes"][0].set(linewidth=0.5)
    box["medians"][0].set(linewidth=0)

    for whisker, cap in zip(box["whiskers"], box["caps"]):
        whisker.set_visible(False)
        cap.set_visible(False)

    if add_center_dot:
        ax.plot(
            position,
            center,
            linewidth=0,
            marker="o",
            ms=5,
            color="black",
            zorder=5,
            clip_on=False,
            )

    if not add_dots == None:
        for dot in add_dots:
            ax.plot(
                position,
                dot,
                linewidth=0,
                marker="o",
                ms=1.5,
                markerfacecolor="black",
                markeredgecolor="grey",
                markeredgewidth=0.5,
                zorder=5.5,
                clip_on=False,
                    )

    if fadeout == "upper" or fadeout == "both":
        ax.plot(
            [position-boxwidth/2, position+boxwidth/2],
            [upper_limit, upper_limit],
            color="white",
            linewidth=0.5,
            zorder=4,
            )

        draw_gradient_rectangle(ax, position-boxwidth/2, upper_limit-0.0003, boxwidth, 0.01, color, alpha, 0, 100)

    if fadeout == "lower" or fadeout == "both":
        ax.plot(
            [position-boxwidth/2, position+boxwidth/2],
            [lower_limit, lower_limit],
            color="white",
            linewidth=0.5,
            zorder=4,
            )

        draw_gradient_rectangle(ax, position-boxwidth/2, lower_limit-0.01+0.0003, boxwidth, 0.01, color, 0, alpha, 100)

def plot_surface_temperature_trends(ax, trends, cat):
    trends = trends.loc[get_dataset_names_for_category(cat)]
    symbols = {}
    marker = get_symbol_for_category(cat)

    for i in trends.index:

        if "ClimTrace" in i:
            offset = 0
        elif cat == "SST" and ("ERA" in i or "JRA" in i):
            offset = 0
        elif cat == "SST" or cat == "GMST":
            offset = 4
        else:
            offset = -4

        if cat == "GMST" and ("ERA" in i or "JRA" in i) and "NOSI" not in i:
            ax.plot(
                trends.loc[i, "1991-2023"],
                offset,
                linewidth=0,
                marker=marker[0],
                ms=marker[1],
                color=get_color_for_dataset(i),
                clip_on=False,
                zorder=2,
            )
        else:
            (symbols[i],) = ax.plot(
                trends.loc[i, "1991-2023"],
                offset,
                linewidth=0,
                marker=marker[0],
                ms=marker[1],
                label=i,
                color=get_color_for_dataset(i),
                clip_on=False,
                zorder=2,
            )

    return symbols


def plot_trend_profile(ax, data, uncertainty, color, scale_y=1):
    profile, = ax.plot(
        data["1991-2023"].values,
        data.index*scale_y,
        color=color,
        linewidth=0.5,
        marker="o",
        ms=1,
        zorder=1,
        )

    ax.fill_betweenx(
        data.index*scale_y,
        data["1991-2023"].values-uncertainty["1991-2023"].values,
        data["1991-2023"].values+uncertainty["1991-2023"].values,
        color=color,
        linewidth=0,
        alpha=0.2,
        zorder=1,
        )

    return profile


def plot_minmax_range_for_cat(ax, data, data_unc, cat):

    if cat == "SST" or cat == "GMST":
        offset = 8
    else:
        offset = -8

    data = data.loc[get_dataset_names_for_category(cat)]
    data_unc = data_unc.loc[get_dataset_names_for_category(cat)]

    try:
        minimum, maximum = find_possible_minmax(
            data,
            data_unc
        )
        ax.fill_between(
            [minimum[0], maximum[0]],
            offset,
            0,
            color=get_color_for_category(cat),
            alpha=0.2,
            linewidth=0,
            clip_on=False
        )

    except ValueError:
        pass


# FORMATTING STUFF

def format_atmos_axis(ax):
    ax.set_ylabel("Altitude | atmosphere (km)", labelpad=12)

    ax.set_ylim(0, 2.5)
    ax.set_xlim(0.05, 0.40)

    ax.tick_params(
        axis="x", which="both", bottom=False, top=False, labelbottom=False
    )

    ax.yaxis.set_major_locator(FixedLocator([0.5, 1, 1.5, 2, 2.5, 3]))
    ax.xaxis.set_major_locator(MultipleLocator(0.05))
    ax.xaxis.set_minor_locator(MultipleLocator(0.01))

    ax.grid(zorder=0, alpha=0.1, linewidth=1)


def format_ocean_axis(ax):
    ax.set_ylabel("Depth | oceans (m)", labelpad=9.5)
    ax.set_xlabel("Temperature trend rate (°C/decade)")

    ax.set_ylim(200, 0)
    ax.set_xlim(0.05, 0.40)

    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.xaxis.set_major_locator(MultipleLocator(0.05))
    ax.xaxis.set_minor_locator(MultipleLocator(0.01))

    ax.grid(zorder=0, alpha=0.1, linewidth=1)

    for spine in ax.spines.values():
        spine.set_zorder(0)


def format_factors_axis(ax):
    ax.set_xlabel("Lines of evidence")
    ax.set_ylabel("GMST-to-GSAT scaling factor")

    ax.set_ylim(0.9, 1.15)
    ax.set_xlim(-0.5, 11.5)
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    ax.xaxis.set_major_locator(FixedLocator([0.5, 10.5]))

    ax.set_xticklabels(["AR6", "ClimTrace"])


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
        zorder=5,
    )


def add_legend(ax, entries, fontsize, category="PROF"):
    if not category == "PROF":
        dummy_entry, = ax.plot([], [], linewidth=0, ms=0)
        total_entries = {f"{category}":dummy_entry}
        total_entries.update(entries)


        legend = ax.legend(
            total_entries.values(),
            [s.replace(f"-{category}", "").replace("-Land", "").replace("_NOSI_F","") for s in total_entries.keys()],
            loc="upper left",
            framealpha=0,
            fontsize=fontsize,
            bbox_to_anchor=get_legend_position(category),
            borderaxespad=0,
        )
        legend.texts[0].set_position((-90, 0))


    else:
        total_entries = entries
        legend = ax.legend(
            total_entries.values(),
            total_entries.keys(),
            loc="upper left",
            framealpha=0,
            fontsize=fontsize,
            bbox_to_anchor=get_legend_position(category),
            borderaxespad=0,
        )

    legend.get_frame().set_linewidth(0)
    legend.get_frame().set_boxstyle("Round", pad=0, rounding_size=0)
    ax.add_artist(legend)


def add_label(ax, position, label):
    ax.vlines(
        position,
        ymin=0.993,
        ymax=1.00,
        color="black",
        linewidth=1,
        alpha=1,
        )

    add_text(ax, label, position, 0.99, ax.transData, va="top", ha="center", color="black", rotation=90)


# MAIN

def main():
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

    # basic layout
    fig = plt.figure(figsize=(17 / 2.54, 0.9 * 9.44 / 2.54), dpi=600)

    gs = gridspec.GridSpec(
        2, 4, width_ratios=[9, 1, 0.7, 7], height_ratios=[5/9, 4/9], hspace=0
    )

    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[1,0])
    ax3 = fig.add_subplot(gs[0:2,3])

    # load
    surface_trend_rates, surface_trend_rate_uncerts = read_surface_trend_rates(input_data_dir)

    iap_trend_profile = read_trend_profile(input_data_dir, "IAPv4")
    iap_trend_uncertainty_profile = read_trend_uncertainty_profile(input_data_dir, "IAPv4")
    iap_trend_profile.index = -iap_trend_profile.index # convert to positive depth coordinate
    iap_trend_uncertainty_profile.index = -iap_trend_uncertainty_profile.index


    era5_trend_profile = read_trend_profile(input_data_dir, "ERA5_global")
    era5_land_trend_profile = read_trend_profile(input_data_dir, "ERA5_land")
    era5_ocean_trend_profile = read_trend_profile(input_data_dir, "ERA5_ocean")

    era5_trend_uncertainty_profile = read_trend_uncertainty_profile(input_data_dir, "ERA5_global")
    era5_land_trend_uncertainty_profile = read_trend_uncertainty_profile(input_data_dir, "ERA5_land")
    era5_ocean_trend_uncertainty_profile = read_trend_uncertainty_profile(input_data_dir, "ERA5_ocean")

    gmst2gsat_era = read_gmst_to_gsat_factors(input_data_dir)

    # plot
    legend_entries = {}
    for cat in ["GMST", "GSAT", "SST", "LSAT", "SSAT"]:
        legend_entries[cat] = plot_surface_temperature_trends(ax2, surface_trend_rates, cat)
        plot_minmax_range_for_cat(ax2, surface_trend_rates, surface_trend_rate_uncerts, cat)

    legend_entries["PROF"] = {}
    legend_entries["PROF"]["ERA5 globally"]= plot_trend_profile(ax1, era5_trend_profile.loc[200:3000], era5_trend_uncertainty_profile.loc[200:3000], "tab:red", scale_y=(1/1000))
    legend_entries["PROF"]["ERA5 over land"] = plot_trend_profile(ax1, era5_land_trend_profile.loc[200:3000], era5_land_trend_uncertainty_profile.loc[200:3000], "tab:green", scale_y=(1/1000))
    legend_entries["PROF"]["ERA5 over oceans"] = plot_trend_profile(ax1, era5_ocean_trend_profile.loc[200:3000], era5_ocean_trend_uncertainty_profile.loc[200:3000], "tab:blue", scale_y=(1/1000))
    legend_entries["PROF"]["IAPv4 oceans"] = plot_trend_profile(ax2, iap_trend_profile.loc[10:200], iap_trend_uncertainty_profile.loc[10:200], "#2000B1")
    legend_entries["PROF"]["ClimTrace\nGMST, GSAT"] = list(plot_surface_temperature_trends(ax2, surface_trend_rates, cat="CT").values())[0]


    # add legends

    add_legend(ax1, legend_entries["PROF"], fontsize=5)

    for cat in ["GMST", "SST", "LSAT"]:
        plot_minmax_range_for_cat
        add_legend(ax2, legend_entries[cat], fontsize=5, category=cat)
    for cat in ["GSAT", "SSAT"]:
        add_legend(ax1, legend_entries[cat], fontsize=5, category=cat)


    # panel b boxes
    add_box(ax3, position=0.5, center=1, halfrange=0.1, color="#0485D1", alpha=0.6, boxwidth=1, add_center_dot=True)
    add_text(ax3, "(<1 from NMAT uncert)", 0.5, 0.992, ax3.transData, va="top", ha="center", color="black", rotation=90)

    add_box(ax3, position=2, center=1.03, halfrange=0.01, color="#0485D1", alpha=0.3)
    add_label(ax3, position=2, label="AR6 - Reanalyses")

    add_box(ax3, position=3, center=1.09, halfrange=0.03, color="#0485D1", alpha=0.3)
    add_label(ax3, position=3, label="AR6 - CMIP5 models")

    add_box(ax3, position=4, center=1.05, halfrange=0.03, color="#0485D1", alpha=0.3)
    add_label(ax3, position=4, label="AR6 - CMIP6 models")

    era_trend_ratio = surface_trend_rates.loc["ERA5-GSAT"] / surface_trend_rates.loc["ERA5-GMST_INCLSI"]
    jra3q_trend_ratio = surface_trend_rates.loc["JRA-3Q-GSAT"] / surface_trend_rates.loc["JRA-3Q-GMST_INCLSI"]
    era_trend_ratio_f = surface_trend_rates.loc["ERA5-GSAT"] / surface_trend_rates.loc["ERA5-GMST_INCLSI_F"]
    jra3q_trend_ratio_f = surface_trend_rates.loc["JRA-3Q-GSAT"] / surface_trend_rates.loc["JRA-3Q-GMST_INCLSI_F"]
    era_trend_ratio_n = surface_trend_rates.loc["ERA5-GSAT"] / surface_trend_rates.loc["ERA5-GMST_NOSI"]
    jra3q_trend_ratio_n = surface_trend_rates.loc["JRA-3Q-GSAT"] / surface_trend_rates.loc["JRA-3Q-GMST_NOSI"]
    era_trend_ratio_nf = surface_trend_rates.loc["ERA5-GSAT"] / surface_trend_rates.loc["ERA5-GMST_NOSI_F"]
    jra3q_trend_ratio_nf = surface_trend_rates.loc["JRA-3Q-GSAT"] / surface_trend_rates.loc["JRA-3Q-GMST_NOSI_F"]

    mean_trend_ratio = np.mean([era_trend_ratio, jra3q_trend_ratio])
    trend_ratio_spread = np.std([era_trend_ratio, jra3q_trend_ratio])

    mean_trend_ratio_f = np.mean([era_trend_ratio_f, jra3q_trend_ratio_f])
    trend_ratio_spread_f = np.std([era_trend_ratio_f, jra3q_trend_ratio_f])

    mean_trend_ratio_n = np.mean([era_trend_ratio_n, jra3q_trend_ratio_n])
    trend_ratio_spread_n = np.std([era_trend_ratio_n, jra3q_trend_ratio_n])

    mean_trend_ratio_nf = np.mean([era_trend_ratio_nf, jra3q_trend_ratio_nf])
    trend_ratio_spread_nf = np.std([era_trend_ratio_nf, jra3q_trend_ratio_nf])

    add_box(ax3, position=6, center=1.06, halfrange=0.06, color="#8c000f", alpha=0.2, fadeout="upper")
    add_label(ax3, position=6, label="Physical understanding")

    add_box(ax3, position=7, center=mean_trend_ratio, halfrange=std_to_90pCI(trend_ratio_spread), color="#8c000f", alpha=0.2, add_center_dot=True, add_dots=[era_trend_ratio["1991-2023"], jra3q_trend_ratio["1991-2023"]], fadeout="both")

    add_box(ax3, position=7, center=mean_trend_ratio_f, halfrange=std_to_90pCI(trend_ratio_spread_f), color="#8c000f", alpha=0.2, add_center_dot=True, add_dots=[era_trend_ratio_f["1991-2023"], jra3q_trend_ratio_f["1991-2023"]], fadeout="both")

    add_box(ax3, position=7, center=mean_trend_ratio_nf, halfrange=std_to_90pCI(trend_ratio_spread_nf), color="#8c000f", alpha=0.2, add_center_dot=True, add_dots=[era_trend_ratio_nf["1991-2023"], jra3q_trend_ratio_nf["1991-2023"]], fadeout="both")

    add_label(ax3, position=7, label="ERA, JRA trend ratios")


    add_box(ax3, position=8, center=gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2010:2020].mean(), halfrange=gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2010:2020].std(), color="#8c000f", alpha=0.2, add_dots=list(gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2010:2020].values), add_center_dot=True)
    add_label(ax3, position=8, label="ERA5 2010-2020")

    add_box(ax3, position=9, center=gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2016:2024].mean(), halfrange=gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2016:2024].std(), color="#8c000f", alpha=0.2, add_dots=list(gmst2gsat_era["ERA5/ClimTraceGMST"].loc[2016:2024].values), add_center_dot=True)
    add_label(ax3, position=9, label="ERA5 2016-2024")

    add_box(ax3, position=10.5, center=1.06, halfrange=0.04, boxwidth=1, color="#8c000f", alpha=0.4, add_center_dot=True)

    # format axes
    format_atmos_axis(ax1)
    format_ocean_axis(ax2)

    format_factors_axis(ax3)

    # helpful lines
    ax3.hlines(1, xmin=-0.5, xmax=15.5, color="black", linewidth=1, alpha=1)
    ax3.hlines(1.02, xmin=-0.5, xmax=15.5, color="black", linewidth=1, linestyle="dashed", alpha=0.2)
    ax3.hlines(1.10, xmin=-0.5, xmax=15.5, color="black", linewidth=1, linestyle="dashed", alpha=0.2)
    ax3.vlines(5, ymin=0.9, ymax=1.12, color="black", linewidth=1, alpha=0.2)

    # panel titles
    add_text(
        ax3,
        "Evidence-based "r"$f_\mathrm{GMST2GSAT}$ estimate",
        0.02,
        0.98,
        ha="left",
        fontsize=8,
        color="black",
        transform=ax3.transAxes,
    )
    add_text(
        ax1,
        "Temp trends 1991-2023",
        0.02,
        0.98,
        ha="left",
        fontsize=8,
        color="black",
        transform=ax1.transAxes,
    )

    # panel labels
    ax1.text(
        -0.05, 1.09, "a", fontsize=10, fontweight=900, transform=ax1.transAxes
    )
    ax3.text(
        -0.05, 1.05, "b", fontsize=10, fontweight=900, transform=ax3.transAxes
    )


    # tight layout
    fig.tight_layout()
    plt.subplots_adjust(wspace=0)

    # save
    plt.savefig(
        os.path.join(
            fig_dir,
            "ClimTrace_Fig3ab_GMSTtoGSATfactors_v20250417.png",
        ),
        dpi=600,
    )

if __name__ == "__main__":
    main()
