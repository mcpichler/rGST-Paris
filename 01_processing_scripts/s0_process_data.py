
# Theme song:   Everything at Once
# Artist:       Lenka
# Album:        Two
# Released:     2011

import os
import argparse

import s1_calculate_climtrace_gmst
import s2_calculate_climtrace_gsat
import s3_calculate_decadal_means_trend_rates
import s4_process_scenario_data
import s5_test_acceleration
import s6_calculate_recent_trends
import s7_calculate_gmst2gsat_factors

# argparse for optional regression
def parse_regression_args():
    parser = argparse.ArgumentParser(
        description="Parse regressors to be regressed out."
    )

    # --regress argument
    parser.add_argument(
        "--regress",
        choices=["nino34_ERSST", "volc"],
        nargs="+",
        help="List of regressors for optional linear regression (choices: 'enso', 'volc')",
    )

    # --lag argument
    parser.add_argument(
        "--lag",
        type=int,
        nargs="*",
        help="Lag values (one per regression type).",
    )

    # --smooth argument
    parser.add_argument(
        "--smooth",
        type=int,
        nargs="*",
        help="Smooth values (one per regression type).",
    )

    args = parser.parse_args()

    # Validate that --lag and --smooth are correctly provided if --regress is given
    if args.regress:
        expected_count = len(args.regress)

        if args.lag is None or len(args.lag) != expected_count:
            parser.error(
                f"--lag must have {expected_count} integer(s) if --regress is given."
            )

        if args.smooth is None or len(args.smooth) != expected_count:
            parser.error(
                f"--smooth must have {expected_count} integer(s) if --regress is given."
            )

    return args


def main():
    args = parse_regression_args()

    s1_calculate_climtrace_gmst.main(args.regress, args.lag, args.smooth)
    s2_calculate_climtrace_gsat.main(args.regress, args.lag, args.smooth)
    s3_calculate_decadal_means_trend_rates.main(args.regress, args.lag, args.smooth)
    s4_process_scenario_data.main(args.regress, args.lag, args.smooth)
    s5_test_acceleration.main(args.regress, args.lag, args.smooth)
    s6_calculate_recent_trends.main()
    s7_calculate_gmst2gsat_factors.main()


if __name__ == "__main__":
    main()
