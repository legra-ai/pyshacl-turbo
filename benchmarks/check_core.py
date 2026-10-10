"""Manual performance regression: Core validation must beat the reference.

Run separately from other tests/builds. This timing gate is deliberately not a
unit-test assertion on shared CI machines. The matrix records all raw samples.
"""

from matrix import benchmark, make_case


def main():
    result = benchmark(make_case("core", 1000), repeats=7)
    print(result["measurements"])
    assert result["speedup"] > 1.0, (
        f"Core performance regression: Turbo is {1 / result['speedup']:.2f}x "
        "slower than pySHACL on 1,000 nodes."
    )


if __name__ == "__main__":
    main()
