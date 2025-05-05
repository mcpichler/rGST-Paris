import os
import pandas as pd


# USEFUL BITS
def megaton_to_gigaton(mt):
    return mt*(1/1000)


# READING DATA

def read_climtrace_csv(data_dir, var, datatype, deriv=False):
    if datatype == "annual":
        endyear = 2024
    elif "decadalmean" in datatype:
        endyear = 2040
    elif "scenarios" in datatype:
        endyear = 2100
    else:
        raise KeyError(f"{datatype} not a valid datatype for read_climtrace_csv()")

    filename = f"{var.lower()}_{datatype}_climtrace_1850-{endyear}.csv"

    data = pd.read_csv(
        os.path.join(
            data_dir, filename,
        ),
        index_col=0,
    )

    return data


def read_annual_data(data_dir, var, timerange):
    data = read_climtrace_csv(data_dir, var, "annual")
    return data[[f"ClimTrace_{var}", f"ClimTrace_{var}_1sigma"]].loc[timerange[0]:timerange[-1]]


def read_hadcrut_sigma(data_dir):
    data = read_climtrace_csv(data_dir, "GMST", "annual")
    return data["HadCRUT5_1sigma"]


def read_decadal_data(data_dir, var, timerange, deriv=False, regress=None):
    datatype = "decadalmean"
    if not regress == None:
        # regnames_for_filename = [r.replace("_", "") for r in regress]
        datatype_mod = "_".join([r for r in regress])
        datatype = f"decadalmean_{datatype_mod}"

    data = read_climtrace_csv(data_dir, var, datatype)

    if deriv:
        columns_to_return = [f"ClimTrace_{var}_DecadalDerivative", f"ClimTrace_{var}_DecadalDerivative_1sigma"]
    else:
        columns_to_return = [f"ClimTrace_{var}_DecadalMean", f"ClimTrace_{var}_DecadalMean_1sigma"]

    return data[columns_to_return].loc[timerange[0]:timerange[-1]]


def read_comparison_data(data_dir, var):
    if var == "GMST":
        datasets = ["HadCRUT5", "NOAAGlobalTemp", "BerkeleyEarth"]
    elif var == "GSAT":
        datasets = ["ERA5 (C3S-CDS)"]

    data = read_climtrace_csv(data_dir, var, "annual")

    return data[datasets]


def read_scenario_data(data_dir, var, timerange):
    data = read_climtrace_csv(data_dir, var, "scenarios")

    return data.loc[timerange[0]:timerange[-1]]


def read_deriv_scenario_data(data_dir, var, timerange):
    data = read_climtrace_csv(data_dir, var, "deriv_scenarios")

    return data.loc[timerange[0]:timerange[-1]]


def read_prediction_data(input_dir, var):
    data = pd.read_csv(
        os.path.join(
            input_dir,
            "ClimTrace_2024_predictions",
            "ClimTrace_2024_GST_predictions.csv"
            ),
        index_col=0,
        )

    prediction = data.loc["prediction", var]
    uncertainty = data.loc["uncertainty", var]

    return prediction, uncertainty

def read_edgar_data(filepath):
    data = pd.read_excel(
        filepath,
        sheet_name="GHG_totals_by_country",
        index_col=1,
        )

    global_emissions_mt = data.drop(columns=["EDGAR Country Code"]).loc["GLOBAL TOTAL"]

    return megaton_to_gigaton(global_emissions_mt)


def read_gcb_data(filepath, sources=["fossil emissions excluding carbonation"]):
    data = pd.read_excel(
        filepath,
        sheet_name="Global Carbon Budget",
        skiprows=21,
        index_col=0,
        usecols=["Year", *sources],
        )

    c_emissions = data.sum(axis=1)
    co2_emissions = c_emissions * 3.664

    return co2_emissions


def read_emissions_scenario_data(filepath, scens):
    data = pd.read_csv(filepath)

    scens_data = data.where(data.Scenario.isin(scens))
    co2_scens = scens_data.where(scens_data.Variable=="Emissions|CO2")
    co2_scens_global = co2_scens.where(co2_scens.Region=="World")

    clean_co2_scens_global = co2_scens_global.drop(columns=["Model", "Region", "Variable", "Unit", "Mip_Era", "Activity_Id"]).dropna(axis=0, how="all")


    clean_co2_scens_global = clean_co2_scens_global.set_index("Scenario").T
    clean_co2_scens_global.index = clean_co2_scens_global.index.astype(int)

    clean_co2_scens_global_interp = clean_co2_scens_global.interpolate(method="linear")

    return megaton_to_gigaton(clean_co2_scens_global_interp.loc[2021:2050])
