# Parameter backup and restore over Modbus: implementation plan

A firmware update resets every parameter
([`VENDOR_PARAMETERS.md`](../doc/references/VENDOR_PARAMETERS.md#loading-the-values)). Today the only way back is
hej.luft's Parameters Manager. A small program next to
[`tests/diagnose_hrds.py`](../tests/diagnose_hrds.py) should do it over a Modbus TCP gateway:

* **backup**: read the unit's parameters and save them as a parameter file
  (`.map`), in the same format as hej.luft's files.
* **restore**: read a `.map` file (a backup, or one of
  [`parameter-files/`](../doc/references/parameter-files/)) and write its values to the unit.

Typical use: backup → firmware update → restore the backup (or hej.luft's
file for the new firmware).

**Independent of the integration.** The program is a service tool for the
unit. It needs neither Home Assistant nor a configured integration, and the
integration's write rules (ADR-0010, ADR-0022, ADR-0023) do not apply to it:
it writes what the file holds. It only reuses the repository's register
knowledge and the device check.

## The `.map` format

What the program reads and writes, as in hej.luft's files:

* XML, ISO-8859-1, CRLF, no checksum. Header: `DATE`, `LANGUAGE`, `DEVICE`
  with `DRIVER` (`drv970AA09`) and `MODEL` (`50122_9_1`), `LISTMODE`.
* One `ITEM key="ky…" R_map="RW"` per parameter (372), with `DESC` and a
  `VALUE` holding:
  * `USR`: the value as shown (`7`, `Unit ON`, `6h`);
  * `INTERNAL`: the raw value of an enum (149 items);
  * `VALBLOB`: the raw value of a time (122 items; 32-bit, a Low and a High
    register);
  * otherwise `USR` alone, a number with the parameter's decimals.
* Some items carry `UNTRANSLATED`; keep it as it is.
* The file holds **no firmware version**.

The items are the parameters only. Run-time values (working hours, last
maintenance, manual requests, live states) are not in the files, so backup
and restore ignore them: **the key set of hej.luft's files is the set the
program handles**, nothing more.

## Mapping a key to a register

A key is `ky` + the register's name. Stripping `ky` gives a name that
[`MODBUS_REGISTERS.md`](../doc/references/MODBUS_REGISTERS.md) already has. Checked for all 372 keys of hej.luft's
files (all eight hold the same keys), each against the address in hej.luft's parameter definitions
(`Drv970AA09`): every resolved address agrees.

| Rule | Keys | Example |
|------|------|---------|
| Name equals the register name in `MODBUS_REGISTERS.md` | 296 | `kyHoliday_Days` → `Holiday_Days` (1497) |
| Same name, other letter case | 1 | `kyMOdE_OperatingMode` → `Mode_OperatingMode` (1583) |
| Leading parameter code (`PU13`, `HA00`, `HCF1`) → the code's anchor; the rest of the name differs between the handbook and the definitions | 73 | `kyPU13_DisableDehum_MinTempSetpoint` → [PU13](../doc/references/MODBUS_REGISTERS.md#pu13) (1889) |
| `_custom` alias of a register | 2 | `kyPH04_HolidayType_custom` → [PH04](../doc/references/MODBUS_REGISTERS.md#ph04) (1780); `kyStartHoliday_custom`: the holiday start command, a run-time action, never written (backup writes `---` / 0) |

So no separate key table is needed. The program reads the register rows of
`MODBUS_REGISTERS.md` (address, scale, range, enum values) the way the
simulator (`tests/sim/registers.py`) does, and resolves each key with the rules
above. A key that resolves to nothing stops the program.

**Kept in sync by `wiring_check.py`** (no Home Assistant needed, runs in the
lint CI), a new check "parameter files resolve against the reference doc":

* every key of every `.map` in `parameter-files/` resolves to exactly one
  register row, with the rules above;
* each value in those files is inside the row's range and, for an enum, one
  of its values;
* every `_custom` or never-written key is on the program's explicit list.

With the existing check that every `REG` in `const.py` has its row in
`MODBUS_REGISTERS.md`, the integration, the register page, the program and
the stored files cannot drift apart: changing a row name or address that a
file uses fails CI.

## Program

`tests/hrds_parameters.py`, standalone like `diagnose_hrds.py`: needs only
`pymodbus` and reuses `identity.py` to check that the device is an HRDS+.

```
python3 tests/hrds_parameters.py HOST backup  [FILE]
python3 tests/hrds_parameters.py HOST restore FILE            # dry run
python3 tests/hrds_parameters.py HOST restore FILE --apply    # writes
```

Common: `--port`, `--unit` as in `diagnose_hrds.py`. Stop if the device check
fails.

### Firmware

The program cannot tell which firmware a `.map` was made for. It reads the
unit's firmware revision (FC 43) and prints it with the file's `DRIVER`,
`MODEL` and `DATE`, then asks: *"The unit runs firmware X. Do the values in
FILE fit this firmware? [y/N]"*. Anything but `y` stops before any write.
`--yes` answers for scripts. Backup names its default file after the
firmware and date (`HRDS_fw9.3_2026-11-08.map`), since the file itself cannot
hold it.

### backup

1. Read every resolved address (FC 03, in blocks like `build_blocks`).
2. Write a `.map`: the header of hej.luft's files with today's `DATE`, then
   one item per key in the files' order, with `USR` and `INTERNAL` /
   `VALBLOB` as the item needs.
3. A register that does not answer: stop and say which, rather than save a
   partial file.

### restore

1. Parse the file; refuse a driver other than `drv970AA09` or a key that
   does not resolve.
2. Take the raw value (`INTERNAL`, `VALBLOB`, or `USR` scaled) and check it
   against the register's range.
3. Read the unit's current values and print a table of what differs.
4. Firmware question (above).
5. Dry run by default; with `--apply`, write the registers that differ
   (FC 06; both words of a 32-bit value), read each back, report mismatches.
6. **Everything in the file is written**, including:
   * PH01 and HA00 (display and probe source): a firmware update resets them,
     so they must come back from the file;
   * the Modbus enables PH02 / PH27 / PH28. hej.luft's files hold
     PH02 = Disabled; the difference table shows it, so the owner sees it
     before confirming.
7. Only the serial settings [PH11](../doc/references/MODBUS_REGISTERS.md#ph11) to [PH13](../doc/references/MODBUS_REGISTERS.md#ph13) (Modbus address, baud
   rate, parity) are skipped unless `--include-serial`, and then written
   last: changing them cuts the connection.

## Steps

1. ADR (`/adr new`): a standalone service tool, outside the integration's
   write rules, may write parameters when the owner runs it with `--apply`
   and confirms the firmware; dry run by default.
2. Shared parser for the register rows of `MODBUS_REGISTERS.md` (move the
   simulator's reader to a module both use) and the key rules; the new
   `wiring_check.py` check uses them.
3. `tests/hrds_parameters.py` with `backup` and `restore`; `.map` read/write
   in the same file.
4. Tests (`tests/sim`):
   * Round trip: load hej.luft's file into the simulator, back it up; the
     backup equals the file except `DATE` (byte for byte, encoding and CRLF
     included).
   * Restore dry run writes nothing; `--apply` writes only differing
     registers, including PH01, HA00 and the enables; serial settings only
     with `--include-serial`.
   * No `y` to the firmware question: nothing written.
   * Out-of-range value, unknown key, wrong driver: refused before any write.
   * Run-time registers are never read into a backup nor written.
5. Docs: usage in `tests/CLAUDE.md`; the parameter loading in
   `VENDOR_PARAMETERS.md` "Loading the values" and the README "After a
   firmware update" point to it. CHANGELOG entry.
