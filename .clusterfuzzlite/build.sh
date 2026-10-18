#!/bin/bash -eu
# Runtime dependencies, pinned by version and hash.

# Bundle every fuzz target with the package (and any data files it loads at import time).
for fuzzer in $(find "$SRC/control-gap-analyzer/fuzz" -name 'fuzz_*.py'); do
  compile_python_fuzzer "$fuzzer" --paths "$SRC/control-gap-analyzer"
done
