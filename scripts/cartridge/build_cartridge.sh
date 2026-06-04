#!/usr/bin/env bash

# Script that builds the assembly located at <game_name>/graphics/game.S


# If BUILDCARTRIDGE_SH_INCLUDED is already set, stop reading this file
if [ -n "${BUILDCARTRIDGE_SH_INCLUDED:-}" ]; then
    return 0 2>/dev/null || exit 0
fi
readonly BUILDCARTRIDGE_SH_INCLUDED=1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT_DIR/scripts/utilities/env_variables.sh"
. "$ROOT_DIR/scripts/utilities/logging.sh"

# OLD VERSION
# build_cartridge() {
#   local game_name="$1"
#   local source="$GAMES_DIR/$game_name/graphics/game.S"
#   local out="$BUILD_DIR/${game_name}.prg32"

#   [[ -f "$source" ]] || die "Missing game source: $source"

#   log_info "Building cartridge: $game_name"
#   CPATH="$BUILD_DIR/config:$BUILD_DIR${CPATH:+:$CPATH}" \
#     python3 "$GAME_TOOL" build \
#       "$source" \
#       --firmware-elf "$QEMU_ELF" \
#       --name "$game_name" \
#       --out "$out"

#   [[ -s "$out" ]] || die "Cartridge build failed: $out was not created"
#   log_ok "Cartridge created: $out"
# }

build_cartridge() {
    local game_name="$1"
    local source="$GAMES_DIR/$game_name/graphics/game.S"
    local out="$BUILD_DIR/${game_name}.prg32"

    [[ -f "$source" ]] || die "Missing game source: $source"

    log_info "Building cartridge: $game_name"
    
    # Fixed the CPATH string parsing here
    CPATH="$BUILD_DIR/config:$BUILD_DIR:${CPATH:+:$CPATH}" \
    python3 "$GAME_TOOL" build \
        "$source" \
        --firmware-elf "$QEMU_ELF" \
        --name "$game_name" \
        --out "$out"

    [[ -s "$out" ]] || die "Cartridge build failed: $out was not created"
    log_ok "Cartridge created: $out"
}

print_usage() {
    echo "Usage: $0 <game_name>"
}

main() {
    set -e 
    
    if [ "$#" -ne 1 ]; then
        print_usage
        exit 1
    fi

    build_cartridge "$1"
}

# Only run main if the script is being executed directly, not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi