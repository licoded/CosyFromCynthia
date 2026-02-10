#!/usr/bin/env bash
# Verify static linking of the built executable

EXE_PATH="${1:-build/apps/cynthia/cynthia-app}"

if [ ! -f "$EXE_PATH" ]; then
    echo "Error: Executable not found at $EXE_PATH"
    exit 1
fi

echo "Checking dynamic dependencies of: $EXE_PATH"
echo "==========================================="

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    otool -L "$EXE_PATH"

    echo ""
    echo "Expected result (macOS):"
    echo "  - Only system libraries should be dynamic:"
    echo "    * /usr/lib/libc++.1.dylib"
    echo "    * /usr/lib/libSystem.B.dylib"
    echo "  - User libraries (flex, sdd, spdlog) should NOT appear"
else
    # Linux
    ldd "$EXE_PATH"

    echo ""
    echo "Expected result (Linux):"
    echo "  - 'not a dynamic executable' for fully static build"
    echo "  - Or minimal system libraries only"
fi
