# The functions in this .py file are used to compare predictions from two API instances side by side.
# To use it, run in the terminal "python -m comparison.compare_two_apis URL_A URL_B". 
# This would send the same acceptance-test inputs to both APIs and prints a table showing estimated values, confidence ranges, and the difference.

import sys

import httpx

from model_acceptance_tests.test_cases import ACCEPTANCE_TEST_CASES


def fetch_estimate(base_url: str, payload: dict, timeout: float = 10.0) -> dict | None:
    #POST /estimate/ and return the JSON body, or None on error.
    url = f"{base_url.rstrip('/')}/estimate/"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload)
        if resp.status_code != 200:
            return None
        return resp.json()
    except httpx.HTTPError:
        return None


def run_comparison(url_a: str, url_b: str) -> None:
    # Skip cases that expect a non-200 status (e.g. invalid type → 422)
    cases = [c for c in ACCEPTANCE_TEST_CASES if c.expected_status is None]

    results: list[dict] = []
    for case in cases:
        payload = case.input.model_dump()
        a = fetch_estimate(url_a, payload)
        b = fetch_estimate(url_b, payload)
        results.append({"name": case.name, "a": a, "b": b})

    # Header
    print()
    print(f"  API A: {url_a}")
    print(f"  API B: {url_b}")
    print()

    header = (
        f"{'Case':<35} {'Est A (€)':>12} {'Est B (€)':>12} "
        f"{'Diff (€)':>12} {'Range A':>22} {'Range B':>22}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        name = r["name"]
        a, b = r["a"], r["b"]

        est_a = f"{a['estimated_value_eur']:,.0f}" if a else "ERROR"
        est_b = f"{b['estimated_value_eur']:,.0f}" if b else "ERROR"

        if a and b:
            diff = b["estimated_value_eur"] - a["estimated_value_eur"]
            diff_str = f"{diff:+,.0f}"
        else:
            diff_str = "n/a"

        range_a = (
            f"{a['value_low_eur']:,.0f} – {a['value_high_eur']:,.0f}"
            if a
            else "n/a"
        )
        range_b = (
            f"{b['value_low_eur']:,.0f} – {b['value_high_eur']:,.0f}"
            if b
            else "n/a"
        )

        print(
            f"{name:<35} {est_a:>12} {est_b:>12} "
            f"{diff_str:>12} {range_a:>22} {range_b:>22}"
        )

    print()


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m comparison.compare_two_apis <URL_A> <URL_B>")
        sys.exit(1)
    run_comparison(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
