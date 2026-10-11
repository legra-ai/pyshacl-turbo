#!/bin/sh
if ! formatter=$(cat rustfmt-toolchain); then
    printf 'Cannot read rustfmt-toolchain\n' >&2
    exit 1
fi
if ! cargo "+$formatter" fmt --all -- "$@"; then
    printf 'Rust formatting failed\n' >&2
    exit 1
fi
