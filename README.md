# rGST-Paris repository

This repository provides the necessary data and scripts to reproduce the data and figures behind _A tracable global warming record and clarity for the 1.5°C and well-below-2°C goals_, including the ClimTrace global warming record, diagnostic metrics and figures included in the paper.

## Installation

This package relies on [poetry](https://python-poetry.org/) for package management:

1. [Install poetry](https://python-poetry.org/docs).
2. Clone this repo, then run `cd rGST-Paris`.
3. To install all necessary dependencies, run `poetry install`.

## Usage

To create all necessary data for the figures, you can simply run
```
cd 01_processing_scripts
poetry run python s0_process_data
poetry run python s0_process_data --regress nino34_ERSST volc --lag 3 7 --smooth 5 5
```

This will execute the processing scripts in the right order, once without and once with the optional regression.
Then, you may run
```
cd ..
cd 03_plot_scipts
poetry run python p0_create_figures.py
```

## Contact
Moritz Pichler: moritz.pichler@uni-graz.at\
Gottfried Kirchengast: gottfried.kirchengast@uni-graz.at

## Suggested Citations
**This repository:** Pichler, M. and G. Kirchengast, 2025. Data processing and figure generation for _A tracable global warming record and clarity for the 1.5°C and well-below-2°C goals_. Version 1.0. **TODO: INSERT FINAL URL.** 

**A tracable global warming record and clarity for the 1.5°C and well-below-2°C goals:** Kirchengast, G. and M. Pichler, 2025. A tracable global warming record and clarity for the 1.5°C and well-below-2°C goals. _Nat. Commun. Earth Envir._ **TODO: COMPLETE FINAL CITATION**

## Playlist
I'm a great fan of Chris Smith's idea of including a playlist featuring a theme song for each script in a repository, as he has done [in the ar6-wg1-ch7 repository](https://github.com/chrisroadmap/ar6/?tab=readme-ov-file#playlist).
Therefore, every script in here has a theme song, too.
These were made by some artists that I like and are, at least in my mind, typically loosely related to the script.

Here's a summary (more info in the respective script header):

_Processing scripts_
- s0: Everything at Once (Lenka)
- s1: The Ocean (Led Zeppelin)
- s2: Sea Breeze (Tyrone Wells)
- s3: Smooth Operator (Sade)
- s4: Hypotheticals (Lake Street Dive)
- s5: Accelerationen (J. Strauss II)
- s6: No One Fits Me (Airbourne)
- s7: Scale (Katie Gately)

_Plotscripts_
- p0: Colors of the Wind (Judy Kuhn)
- p1: Big Yellow Taxi (Joni Mitchell)
- p2: Waiting on the World to Change (John Mayer)
- p3: I Don't Know (Lisa Hannigan)
- p4: Written in the Water (Gin Wigmore)
- p5: Sympathy For The Devil (The Rolling Stones)
- p6: Imagine (Zaz)

## MW-EOT algorithm description
The following is a description of the smoothing algorithm primarily used in _A tracable global warming record and clarity for the 1.5°C and well-below-2°C goals_, as compiled by Gottfried Kirchengast.

**MW-EOT smoothing algorithm description v8-16Oct2024** --- GCCIv2.3 moving-window (MW) ensemble-of-trendlines (EOT) smoothing algorithm for computing decadal-mean timeseries from annual-data anomaly timeseries of CWM-GLO variables; related trend rates (derivatives) as well as uncertainty estimates for both the mean and the trend rates are consistently co-computed.

[*begin change record*

v1-10Jun2023 - original version.

v2-12Jun2023 - updates: 1. inserted 'nCXokyearsStart' parameter and its use; 2. terminology-improved "...SDev" to "...SUnc" in resulting standard uncertainty timeseries where needed.

v3-28Jun2023 - updates: 1. several variable definitions extended and improved; 2. baseline values of 'nEnd' and 'nCXokyearsStart' parameters updated; 3. algo steps 1 and 2 updated (included co-estimation of uncertainty timeseries); 4. algo steps 7 to 9 updated (provision of complete uncertainty timeseries included).

v4-16Aug2023 - updates: 1. uncertainty input timeseries SUnc_of_X_n included in addition to X_n; 2. a few variable and parameter definitions extended and improved; 3. baseline value of the 'nCXokyearsStart' parameter updated; 4. algo step 1 updated (SUnc_of_X_n included and formulation further clarified) and editorial refinements in steps 3 and 9.

v5-28Dec2023 - updates: 1. improved SUnc_of_DXmean_n algo and various editorial improvements in Sections 1 and 4; 2. parameter definitions divided from variables (Section 1) into separate Section 2; 3. baseline settings of parameters 'nDataEnd' and 'nEnd' updated and a few further editorial refinements in Section 3.

v6-30Dec2023 - updates: 1. definition of input obs-based uncertainty in DXmean_n (SUnc_of_DX_n) consolidated in Section 1; 2. algo description related to SUnc_of_DX_n adjusted accordingly in step 4 in Section 4.

v7-15Oct2024 - updates: 1. editorial refinements in Sections 1-3; 2. simplification of jitterfilter (same for Xmean_n, DXmean_n); 3. algorithm sequence in Section 4 streamlined from 9 to 7 steps, simplifying the description in line with a consolidation of the code.

v8-16Oct2024 - updates: editorial refinements in Sections 1-4.

*end change record*]

----------------------------------------------------------------

**Table of Contents - Sections:**

1. Variable definitions
2. Parameter definitions
3. Baseline settings of parameters
4. Algorithm sequence

----------------------------------------------------------------

### 1. Variable definitions

*Input variables:*

**X_n**, also briefly termed X and 'annual anomaly timeseries':\
annual-data anomaly timeseries (data years n); **the input timeseries** to the algorithm.

**SUnc_of_X_n**:\
Observational standard uncertainty timeseries associated with the X_n timeseries; **the uncertainty input timeseries associated with the input timeseries** of the algorithm.\
For the CWM-GLO input timeseries, it is reasonably assumed to be of bias-type character over the +/-decade timescale spanned by the filter full width (mCoreFW) of the EOT trendline fits. That is, it is interpreted with respect to each center year n as a constant relative uncertainty (SUnc_of_X_n/Xmean_n) valid across mCoreFW, yielding for Xmean_n an associated mean uncertainty of just SUnc_of_X_n and for the derivative timeseries DXmean_n an associated mean uncertainty SUnc_of_DX_n = (SUnc_of_X_n/Xmean_n)\*DXmean_n (limited in actual use to the linear-deviations domain within 0.25\*DXmean_n, keeping validity for small Xmean_n).
SUnc_of_X_n can hence be assumed uncorrelated with the uncertainty co-estimated with the trendline fits towards Xmean_n, Unc_of_XtrendlineCYrValueMean_n, and RMS-combined with it. Similarly, SUnc_of_DX_n can be assumed uncorrelated and is RMS-combined with the uncertainty co-estimated for the trendline slopes towards DXmean_n, Unc_of_DXtrendslopeValueMean_n.



*Result variables:*

**Xmean_n**, also briefly termed Xmean and 'LTC anomaly timeseries':\
Long-term change (LTC) anomaly timeseries; **the main result timeseries** of the algorithm.

**SUnc_of_Xmean_n**, involving also CXinducedSUnc_of_extrapolXmean_n:\
Xmean_n standard uncertainty timeseries associated with the Xmean_n timeseries; **the uncertainty result timeseries associated with the main result timeseries** of the algorithm.\
SUnc_of_Xmean_n is composed of the trendline-fits uncertainty Unc_of_XtrendlineCYrValueMean_n (typically the primary contribution) and the input observational uncertainty SUnc_of_X_n, encompassing in the extrapolation time range from nCoreyearsEnd onwards also the Xmean_n extrapolation uncertainty CXinducedSUnc_of_extrapolXmean_n.

**DXmean_n**, also briefly termed DXmean and 'LTC derivative timeseries':\
Long-term change (LTC) derivative timeseries, the centered-in-time derivative of Xmean_n; **the complementary result timeseries** of the algorithm.

**SUnc_of_DXmean_n**, involving also CXinducedSUnc_of_extrapolDXmean_n:\
DXmean_n standard uncertainty timeseries associated with the DXmean_n timeseries; **the uncertainty result timeseries associated with the complementary result timeseries** of the algorithm.\
SUnc_of_DXmean_n is composed of the trendline-slopes uncertainty Unc_of_DXtrendslopeValueMean_n (typically the primary contribution) and the input observations-based uncertainty SUnc_of_DX_n, encompassing in the extrapolation time range from nCoreyearsEnd onwards also the DXmean_n extrapolation uncertainty CXinducedSUnc_of_extrapolDXmean_n.



*Auxiliary variables:*

**SUnc_of_DX_n**:\
Input observations-based standard uncertainty estimate for the LTC derivative timeseries DXmean_n, derived from the bias-type relative uncertainty (SUnc_of_X_n/Xmean_n) in the robust linear-deviations form SUnc_of_DX_n = Min[ Abs(SUnc_of_X_n/Xmean_n)\*Abs(DXmean_n), 0.25\*Abs(DXmean_n) ]; see also the explanations along with the SUnc_of_X_n input variable above.

**CXmean_n**, also briefly termed CXmean and 'LTC curvature timeseries':\
Long-term change (LTC) curvature timeseries, the backward-in-time derivative of the LTC derivative timeseries; used as auxiliary dataset of annual curvature values CXmean_n = (DXmean_n - DXmean_n-1), to help estimate the DXmean_n extension and associated uncertainties along the extrapolation range (by suitable mean and standard deviation estimates from annual curvature values).

**CYr_n**, also briefly termed CYr:\
center year (core year) of the EOT fits centered on year n, to which the EOT filtering results are assigned (within the 'Near-margin years' of the EOT fits, CYr_n is actually not central to the filter window and hence termed core year; everywhere else within the 'CYrs inner domain' it is an actual center year, however).

**XtrendlineCYrValue(k)\_n, XtrendlineCYrValueMean_n**:\
X value of a fitted trendline in year CYr_n for trendline-fit number k (out of the total of N_Trendfits trendline fits), and their ensemble mean; computed as primary result towards Xmean_n. Note that, for the CWM-GLO input timeseries, the standard deviation (spread) of the values XtrendlineCYrValue(k)_n around their mean is small compared to the co-estimated trendline-fits uncertainty Unc_of_XtrendlineCYrValueMean_n, and correlated with it, and hence disregarded.

**Unc_of_XtrendlineCYrValue(k)\_n, Unc_of_XtrendlineCYrValueMean_n**:\
Uncertainty estimate for the X value XtrendlineCYrValue(k)_n for trendline-fit number k (total number N_Trendfits), and their variance-based ensemble mean, i.e., the mean computed in the form Unc_Mean = SqRt{ (1/N) * Sum[ Unc(k)^2 ] }; co-estimated along with the Xmean_n computation as the key result towards SUnc_of_Xmean_n. 

**Unc_of_DXtrendslopeValue(k)_n, Unc_of_DXtrendslopeValueMean_n**:\
Uncertainty estimate for the DX value (i.e., slope) of a fitted trendline for CYr_n for trendline-fit number k (total number N_Trendfits), and their variance-based ensemble mean, i.e., the mean computed in the form Unc_Mean = SqRt{ (1/N) * Sum[ Unc(k)^2 ] }; co-estimated along with the Xmean_n computation as the key result towards SUnc_of_DXmean_n.

**XmeanTrendslopeValueDXmean_n**:\
DXmean value of fitted corewindow-trendline of CYr_n for trendline-fit number kCenter to the Xmean_n timeseries; computed as primary result towards DXmean_n. Note that, for the CWM-GLO input timeseries, the standard deviation (spread) of the k trend-slope values around this mean is small compared to the co-estimated uncertainty Unc_of_DXtrendslopeValueMean_n of the fitted slope values, and correlated with it, and hence disregarded.

**RecentAnnualMeanCX, AvgAnnualCXSDev**:\
Mean annual curvature value of the DXmean_n timeseries over the recent years from nCoreyearsEnd backwards over one mCoreFW timespan, and standard deviation of the annual curvature values of the DXmean_n timeseries over nCXokyearsStart to nCoreyearsEnd.

----------------------------------------------------------------

### 2. Parameter definitions

**nStart, nEnd**:
start and end year of the overall time domain of targeted center years (CYr).

**nDataStart, nDataEnd**:
start and end year of the available input timeseries X_n.

**mInnerHW, mOuterHW, mCoreHW, mCoreHWYrs**:
the filter halfwidths (in years) of the EOT fits, over the years before and after any CYr_n.

**mJitterfilterHW**:
the filter halfwidth (in years) of the moving-average jitterfilter on Xmean_n, DXmean_n and their Uncs; applied on top of the EOT filtering for "polishing off" any possible small residual numerical noise (setting of size 2 to mInnerHW).

**mInnerFW, mOuterFW, mCoreFW**:
the filter full widths (in years) of the EOT fits, including the center year CYr_n.

**N_Trendfits**:
number of trendline fits available from the inner to outer filter full widths; corresponds to the EOT ensemble size.

**nFilterStart, nFilterEnd**:
start and end year covered by the MW-EOT filtering; i.e., the algorithm formally runs over this full range of years, including the 'Near-margin years' (of width mCoreHWYrs) towards start and towards end, respectively.

**nCoreyearsStart, nCoreyearsEnd**:
start and end year of the X_n that belong to the CYrs inner domain, bounded towards nFilterStart and nFilterEnd by the 'Near-margin years'.

**nCXokyearsStart**:
year from which on the DXmean_n timeseries is considered of suitable quality and adequacy to use it as basis for computing CXmean_n annual curvature values.

**nFlattertrendsStart**:
year where linear trend increase extrapolation of DXmean_n from nCoreyearsEnd stops and half-cosine-downweighted 'fadeout' of the extropolated DXmean_n begins, gradually reaching constant DXmean_n five years after.

----------------------------------------------------------------

### 3. Baseline settings of parameters

nStart = 1960\
nEnd = 2034\
nDataStart < = nStart (lastest data start by nStart, but ideally at least by year nFilterStart so that as of nStart all years are inner-domain CYrs; practically nDataStart depends on the specific input X_n's, which start at different years)\
nDataEnd = 2023 (final year with data available while the current year is 2024; all input X_n's need to supply data values until nDataEnd)

mInnerHW = 8\
mOuterHW = 11\
mCoreHW = (mOuterHW+mInnerHW)/2. = 9.5\
mCoreHWYrs = NearestInt[ mCoreHW+EPS ] = 10

mJitterfilterHW = 2 (routine 'minimum value' for removing possibly remaining jitter noise)

mInnerFW = (2 * mInnerHW + 1) = 17\
mOuterFW = (2 * mOuterHW + 1) = 23\
mCoreFW = NearestInt[ 2 * mCoreHW + 1 ] = 20

N_Trendfits = (mOuterFW - mInnerFW + 1) = 7

nFilterStart = Max[ nStart - nOuterHW, nDataStart ]\
nFilterEnd = nDataEnd (nominally there are no data available beyond nDataEnd)

nCoreyearsStart = nFilterStart + mCoreHWYrs\
nCoreyearsEnd = nFilterEnd - mCoreHWYrs\
nCXokyearsStart = 1971\
nFlattertrendsStart = 2019

----------------------------------------------------------------------------------

### 4. Algorithm sequence:

**Step 1.**

**+** Apply the MW-EOT filtering to X_n over nFilterStart to nFilterEnd, and for each CYr_n compute the XtrendlineCYrValueMean_n timeseries from the ensemble of N_Trendfits trendline fits to obtain an initial Xmean_n timeseries by assigning Xmean_n = XtrendlineCYrValueMean_n.

**+** In addition, co-estimate the Unc_of_XtrendlineCYrValueMean_n and Unc_of_DXtrendslopeValueMean_n timeseries, respectively, from this ensemble of N_Trendfits trendline fits.

**+** Subsequently also obtain an initial Xmean_n uncertainty timeseries, by the RMS-combination SUnc_of_Xmean_n = SqRt[ Unc_of_XtrendlineCYrValueMean_n^2 + SUnc_of_X_n^2 ].

**+** Finally apply a numerical-noise jitter filtering over (nFilterStart + mJitterfilterHW) to (nFilterEnd - mJitterfilterHW) to the initial Xmean_n and SUnc_of_Xmean_n timeseries (note that due to the 'Near-margin years' towards start and end there is no need for any further specific treatment of the unfiltered marginal years of width mJitterfilterHW).

***Result step 1:*** *a safely smooth initial Xmean\_n timeseries (for steps 2 and 7) and associated SUnc\_of\_Xmean\_n timeseries (for step 7), complemented by the Unc\_of\_DXtrendslopeValueMean\_n timeseries needed towards the DXmean\_n uncertainty estimation (in step 4).*

**Step 2.**

**+** Apply the ensemble-center trendline-fit ( kCenter = (N_Trendfits+1)/2 ) to Xmean_n (from step 1) over nCoreyearsStart to nCoreyearsEnd, and for each CYr_n in this inner time domain compute the XmeanTrendslopeValueDXmean_n from this corewindow trendline-fit to obtain an initial DXmean_n timeseries by assigning DXmean_n = XmeanTrendslopeValueDXmean_n.

***Result step 2:** a fairly smooth inital DXmean_n* *timeseries over the core years of the time domain (for step 3).*

**Step 3.**

**+** Compute, by backward-differences on DXmean_n (from step 2), the CXmean_n over (nCoreyearsEnd - mCoreFW + 1) to nCoreyearsEnd, obtain RecentAnnualMeanCX = Mean[ CXmean_n ] from it, and use this in cumulative addition from nCoreyearsEnd to nFlattertrendsStart to linearly extend DXmean_n from nCoreyearsEnd to nFlattertrendsStart.

**+** Subsequently apply a numerical-noise jitter filtering over (nCoreyearsStart + mJitterfilterHW) to (nFlattertrendsStart - mJitterfilterHW) to the DXmean_n timeseries (note that the small non-jitter-smoothed filter-halfwidth margin towards start is of no concern; and towards end the linear extrapolation from nCoreyearsEnd ensures that this filter-halfwidth margin needs no extra treatment either).

***Result step 3:** a safely smooth* *DXmean_n timeseries now extrapolated up to* *year nFlattertrendsStart (for step 5).*

**Step 4.**

**+** Compute, from nCoreyearsStart to nFlattertrendsStart, an initial DXmean_n uncertainty timeseries, by obtaining the RMS-combination SUnc_of_DXmean_n = SqRt[ Unc_of_DXtrendslopeValueMean_n^2 + SUnc_of_DX_n^2 ] up to nCoreyearsEnd, then extending this uncertainty timeseries by using the SUnc_of_DXmean estimate at nCoreyearsEnd also for the further years up to nFlattertrendsStart.

**+** Subsequently apply a numerical-noise jitter filtering over (nCoreyearsStart + mJitterfilterHW) to (nFlattertrendsStart - mJitterfilterHW) to the SUnc_of_DXmean_n timeseries (note that due to the 'Near-margin years' towards start and end there is no need for any further specific treatment of the unfiltered marginal years of width mJitterfilterHW).

***Result step 4:*** *a safely smooth standard uncertainty timeseries SUnc_of_DXmean_n over nCoreyearsStart to nFlattertrendsStart (for step 6).*

**Step 5.**

**+** For completing the DXmean_n timeseries (of step 3) from nFlattertrendsStart to nEnd, add a half-cosine-downweighted serial addition of the RecentAnnualMeanCX curvature value over five years towards reaching zero DXmean_n increase as of nFlattertrendsStart + 5 years (details: use weights w_i = 0.5*[1+cos(phi_i)] with phi_i = (30 deg, 60 deg, 90 deg, 120 deg, 150 deg), yielding w1 = 0.933, w2 = 0.75, w3 = 0.5, w4 = 0.25, w5 = 0.067, and sequentially apply them at the time steps to years 1 to 5 after nFlattertrendsStart, respectively; for all further years n to nEnd, the value of DXmean_n-1 can be assigned, or, equivalently, the constant value DXmean_n = DXmean_nFlattertrendsStart + 2.5 * RecentAnnualMeanCX).

***Result step 5: a final smooth DXmean_n timeseries over nCoreyearsStart to nEnd.***

**Step 6.**

**+** Compute, by backward-differences on DXmean_n (from step 2), the CXmean_n over (nCXokyearsStart + 1) to nCoreyearsEnd, obtain AvgAnnualCXSDev = SDev[ CXmean_n ] from it, and use this in cumulative addition from nCoreyearsEnd to nEnd to create an extrapolation standard uncertainty timeseries CXinducedSUnc_of_extrapolDXmean_n over this extrapolation time range (for all years up to nCoreyearsEnd, this CXinducedSUnc_of_extrapolDXmean_n is zero, since no DXmean extrapolation is involved).

**+** Subsequently, from (nCoreyearsEnd + 1) up to nEnd, RMS-combine this extrapolation uncertainty with the one of the basic DXmean_n uncertainty timeseries (from step 4) applying at nCoreyearsEnd and beyond, i.e., compute SUnc_of_DXmean_n = SqRt[ SUnc_of_DXmean_nCoreyearsEnd^2 + CXinducedSUnc_of_extrapolDXmean_n^2 ].

***Result step 6: a final smooth SUnc_of_DXmean_n standard uncertainty timeseries, complementing the DXmean_n timeseries, over nCoreyearsStart to nEnd.***

**Step 7.**

**+** Starting from Xmean_nCoreyearsEnd, use the final DXmean_n timeseries (from step 5) in cumulative addition up to nEnd, to obtain a final Xmean_n timeseries that is consistent in its slope behavior over the extrapolation time range with the final DXmean_n timeseries. Ensure an adequate cumulative addition, being at each annual step from n-1 to n (initial n-1 := nCoreyearsEnd) of the mid-point form Xmean_n = Xmean_n-1 + 0.5*[DXmean_n + DXmean_n-1].

**+** Likewise, starting from Xmean_nCoreyearsEnd, use the CXinducedSUnc_of_extrapolDXmean_n timeseries (from step 6) in cumulative addition up to nEnd, to create an extrapolation standard uncertainty timeseries CXinducedSUnc_of_extrapolXmean_n over this extrapolation time range (for all years up to nCoreyearsEnd, this CXinducedSUnc_of_extrapolXmean_n is zero, since no Xmean extrapolation is involved).

**+** Subsequently, from (nCoreyearsEnd + 1) up to nEnd, RMS-combine the extrapolation uncertainty with the one of the basic Xmean_n uncertainty timeseries (from step 1) applying at nCoreyearsEnd and beyond, i.e., compute SUnc_of_Xmean_n = SqRt[ SUnc_of_Xmean_nCoreyearsEnd^2 + CXinducedSUnc_of_extrapolXmean_n^2 ].

***Result step 7: a final smooth Xmean_n timeseries and associated SUnc_of_Xmean_n standard uncertainty timeseries over nStart to nEnd.***
