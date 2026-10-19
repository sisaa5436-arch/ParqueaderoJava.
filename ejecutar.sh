#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin
java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 -d bin src/ec/edu/ups/parqueadero/*.java
java -cp bin ec.edu.ups.parqueadero.Main "$@"
