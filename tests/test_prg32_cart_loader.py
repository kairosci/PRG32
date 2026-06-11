from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CART_LOADER = ROOT / "components" / "prg32" / "prg32_cart.c"


def test_abi_table_cartridges_do_not_require_runtime_load_addr_match() -> None:
    text = CART_LOADER.read_text(encoding="utf-8")
    legacy_check = (
        "if (import_model == PRG32_IMPORT_MODEL_LEGACY_ABSOLUTE &&\n"
        "        h->load_addr != (uint32_t)(uintptr_t)prg32_cart_exec)"
    )

    assert legacy_check in text
    assert '"cartridge linked for a different runtime address"' not in text


def test_abi_table_entries_receive_runtime_abi_table_pointer() -> None:
    text = CART_LOADER.read_text(encoding="utf-8")

    assert "typedef void (*prg32_cart_abi_entry_t)(const prg32_abi_table_t *abi);" in text
    assert "((prg32_cart_abi_entry_t)entry)(&prg32_abi_table);" in text
