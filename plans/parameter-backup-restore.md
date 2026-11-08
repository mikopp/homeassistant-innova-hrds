# Parameter backup and restore over Modbus: implementation plan

A firmware update resets every parameter
([`VENDOR_PARAMETERS.md`](../doc/references/VENDOR_PARAMETERS.md#loading-the-values)). Today the only way back is
hej.luft's Parameters Manager. A small program next to
[`tests/diagnose_hrds.py`](../tests/diagnose_hrds.py) should do it over the same Modbus TCP gateway:

* **backup**: read the unit's parameters and save them as a parameter file
  (`.map`), in the same format as hej.luft's files.
* **restore**: read a `.map` file (a backup, or one of
  [`parameter-files/`](../doc/references/parameter-files/)) and write its values to the unit.

Typical use: backup → firmware update → restore the backup (or hej.luft's
file for the new firmware).

## The `.map` format

What the program reads and writes, as in hej.luft's files:

* XML, ISO-8859-1, CRLF, no checksum. Header: `DATE`, `LANGUAGE`, `DEVICE`
  with `DRIVER` (`drv970AA09`) and `MODEL` (`50122_9_1`), `LISTMODE`.
* One `ITEM key="ky…" R_map="RW"` per parameter (372), with `DESC` and a
  `VALUE` holding:
  * `USR`: the value as shown (`7`, `Unit ON`, `6h`);
  * `INTERNAL`: the raw value of an enum (149 items);
  * `VALBLOB`: the raw value of a time (122 items);
  * otherwise `USR` alone, a number with the parameter's decimals.
* Some items carry `UNTRANSLATED`; keep it as it is.

The items are the parameters only. Run-time values (working hours, last
maintenance, manual requests, live states) are not in the files, so backup
and restore ignore them: **the key set of hej.luft's files is the set the
program handles**, nothing more.

## Key table: which register each item is

A `.map` item names a key, not an address. The address, decimals, sign and
range come from hej.luft's parameter definitions (`Drv970AA09`), which are
not in the repository.

* Generate once, from `Drv970AA09`, a key table and commit it:
  `doc/references/parameter-files/keys-AA09.csv` with `key, address, decimals,
  signed, min, max, kind (number / enum / time)`, for the 372 keys of the
  files. Facts about registers, no vendor text beyond the key names.
* Share it with the integration's register knowledge instead of a second
  copy of addresses: `wiring_check.py` checks that every row's address has a
  row in [`MODBUS_REGISTERS.md`](../doc/references/MODBUS_REGISTERS.md) and agrees with `const.py` and
  `installer_params.py` (code, decimals, signedness) where they define the
  register. A key table that disagrees with the integration fails CI.
* Enum labels for `USR` come from the same table (or from `MODBUS_REGISTERS.md`
  values), so a backup reads like hej.luft's file.

## Program

`tests/hrds_parameters.py`, standalone like `diagnose_hrds.py`: needs only
`pymodbus`, loads `const.py` through the `wiring_check` stubs, and reuses
`identity.verify_device` (ADR-0009).

```
python3 tests/hrds_parameters.py HOST backup  backup.map
python3 tests/hrds_parameters.py HOST restore backup.map            # dry run
python3 tests/hrds_parameters.py HOST restore backup.map --apply    # writes
```

Common: `--port`, `--unit` as in `diagnose_hrds.py`. Stop if the device check
fails.

### backup

1. Read every address of the key table (FC 03, blocks like `build_blocks`).
2. Write a `.map`: the header of hej.luft's files with today's `DATE`, then
   one item per key in the files' order, with `USR` and `INTERNAL` /
   `VALBLOB` as the key's kind needs.
3. A key that does not answer: stop and say which, rather than save a
   partial file.

### restore

1. Parse the file; refuse a driver other than `drv970AA09` or a key not in the
   table.
2. Take the raw value (`INTERNAL`, `VALBLOB`, or `USR` × 10^decimals) and
   check it against min/max.
3. Read the unit's current values. Print a table of what differs.
4. Dry run by default; with `--apply`, write only the registers that differ
   (FC 06), read each back, report mismatches.
5. **Skipped unless asked:**
   * the Modbus enables PH02 / PH27 / PH28 (ADR-0022 for the integration;
     here the owner decides with `--include-enables`);
   * the serial settings (address, baud rate, parity): writing them cuts the
     connection. With `--include-serial` they are written last.
6. Print the skipped keys and their file values, so they can be set on the
   display.

## Steps

1. ADR (`/adr new`): a standalone tool may write parameters when the owner
   runs it with `--apply`; dry run by default; enables and serial settings
   only on request. Name ADR-0009, ADR-0022 and ADR-0023 as the rules it
   follows.
2. Generate and commit `keys-AA09.csv`; add the cross-check to
   `wiring_check.py`.
3. `tests/hrds_parameters.py` with `backup` and `restore`; shared `.map`
   read/write code in the same file.
4. Tests (`tests/sim`):
   * Round trip: load hej.luft's file into the simulator, back it up; the
     backup equals the file except `DATE` (byte for byte, encoding and CRLF
     included).
   * Restore dry run writes nothing; `--apply` writes only differing
     registers and skips enables and serial settings by default.
   * Out-of-range value, unknown key, wrong driver: refused before any write.
   * Run-time registers are never read into a backup nor written.
5. Docs: usage in `tests/CLAUDE.md`; the firmware-update steps in
   `VENDOR_PARAMETERS.md` "Loading the values" and the README "After a
   firmware update" point to it. CHANGELOG entry.

## Open

* Does firmware 9.2 accept the 9.3/9.4 keys unchanged? The addresses are the
  same in every revision; the 9.2 files here are made that way [INFERRED].
* PH01 / HA00 without a display: restore the file's value or keep the unit's?
  The integration's headless sync (ADR-0010) sets them anyway on connect.
