# Tested units and installations

Which units and installation scenarios are known to work with this
integration, and which are not tested yet. This page describes **installations
the integration has been used in**; how the unit itself behaves, for any
installation, is in [`references/UNIT_BEHAVIOUR.md`](references/UNIT_BEHAVIOUR.md).
The open hardware questions are in [`../plans/todo.md`](../plans/todo.md).

## What the status means

| Status | Meaning |
|--------|---------|
| **Works** | Used on a real unit in this setup by the maintainer or by a reporter, and behaved as described. The row says what was seen. |
| **Partly** | Part of it was seen on a real unit; the row says what is still open. |
| Context | Not a feature: where the reference unit is installed. |
| **Not tested** | Only covered by the handbooks and by CI (a simulated unit and a real Home Assistant container). It may work; nobody has confirmed it. |

CI alone never makes a row **Works**. Evidence from the unit itself is logged
in [`references/UNIT_BEHAVIOUR.md` §13](references/UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)
(`T1`, `T2`, …); a row here cites it.

## Units

| Unit | Firmware | Status | Notes |
|------|----------|--------|-------|
| hej.luft **HRDS+ 30** `H R K DC`, headless | `V01.00.09.02` [T1] | **Works** | The maintainer's unit (reference unit). Seen: identity and the whole register map read, the required settings and the first Modbus ON, OFF written over Modbus [T1 to T9, T14]; full dehumidify cycles with valve and pump, damper, fan and compressor read-backs, start and stop [T10 to T19]; the fan speed owned by the unit [T22 to T28]; the season switch [T31]; the on/off state kept across a power cycle [T30]. An integration (INT) cycle is not recorded yet |
| HRDS+ 50 | — | Not tested | The size has no register (the `model` option sets it). Only the airflow estimate differs |
| Units without recirculation (non-`R`) | — | Not tested | No fan, damper or fan entities are created when the damper output ([1134](references/MODBUS_REGISTERS.md#reg-1134)) reads *disabled* |
| Units without the integration function (no `DC`, [PG02](references/MODBUS_REGISTERS.md#pg02) = 0) | — | Not tested | *Cool* and *Heat* are not offered |
| Unit with a CNU2 display | — | Not tested | The display and [HA00](references/MODBUS_REGISTERS.md#ha00) = 1/2 path, the headless sync skipped |
| Unit with external room or outdoor probes | — | Not tested | Target humidity and temperature, climate *Auto* mode (CI only) |

The firmware column is the revision the unit reports, shown as
[*Firmware*](entity-reference.md#firmware) on the device page; please include it in a report.

## The same unit under other names

Before hej.luft, the HRDS was sold in Italy only by other companies, partly
with their own displays or small differences; who builds and sells the unit:
[`references/README.md`](references/README.md#who-makes-and-sells-the-unit).
The sellers named by the vendor:

| Brand | Models | Status |
|-------|--------|--------|
| [Vortice](https://www.vortice.it/it/vmc_recupero_calore/moduli-aggiuntivi-da-condotto/per-deumidificazione) | HRDS 30 DC, HRDS 30 R DC, HRDS 50 DC, HRDS 50 R DC | Not tested |
| [VMC Group](https://www.vmcgroup.it/prodotti-deumidificatori/mdr-k) | MDR K (supply air only) and MDR K R (with recirculation), sizes 15-30 and 25-50, versions D and DC | Not tested |
| Cappellotto S.r.l. | Not known (no product page found) | Not tested |
| Geatherm | Not known (no product page found) | Not tested |

The Vortice and VMC Group manuals ([`references/`](references/README.md))
show the same unit: the same type code (size, `H`, `R`, `K` electronics,
`D`/`DC`), terminal strip, alarm numbers, menu levels and compressor states
as the HRDS+. How they differ from the hej.luft HRDS+:

* **On/off compressor instead of an inverter.** It runs at one speed and
  switches on and off to hold the humidity instead of modulating, so the
  capacity is lower (about 22–40 L/day against 56 / 89 L/day), and the
  inverter settings (compressor speed and ramps, PE24 to PE33) do not apply.
* Refrigerant R134a instead of R410A.
* The older CNU display panel instead of the CNU2.

**None of these units has been tried with the integration.** It connects only
when the controller reports an EVCO `EPB9…` product code, and whether the
registers match the HRDS+ register map is unconfirmed. If you have one of
them and try it, please report what you see, working or not: open an issue
with the diagnostic output, see [Add your setup](#add-your-setup).

## Installation scenarios

### Control path

| Scenario | Status | Notes |
|----------|--------|-------|
| Headless ([PH01](references/MODBUS_REGISTERS.md#ph01) = 0, [HA00](references/MODBUS_REGISTERS.md#ha00) = 0), no display, no probes | **Works** | Home Assistant is the controller: requests over Modbus. First Modbus ON takes the unit out of *off by display* [T7]. Every setup-check issue cleared once the settings were made |
| Modbus RTU (RS-485) to TCP gateway | **Works** | Reads must be small: a 120-register read got no reply, 10-register reads cover the map [T9]. Modbus unit id 1, the default |
| Installed behind a Zehnder ComfoAir Q350 (MVHR) | Context | Where the reference unit is installed. Nothing about coupling to the MVHR is recorded |

### Water circuit

The unit's water source decides what it can do (see
[`references/UNIT_BEHAVIOUR.md` §2.2](references/UNIT_BEHAVIOUR.md) for the
handbook's variants 1 to 6 and the separate ground loop).

| Scenario | Status | Notes |
|----------|--------|-------|
| **Brine circuit of a ground-source heat pump, handbook variant 6**: the unit sits in a branch **parallel** to the heat pump, with its own small brine pump on the `PM` output. It runs independently of the heat pump and also at the same time | **Partly** | Seen: the unit starts the pump on a request, the pump runs and [*Water valve / pump output*](entity-reference.md#water-valve-pump-output) follows [T10, T11]; valve and pump off within a minute of the request ending [T19]; the anti-stagnation pulses while the unit is on, none while it is off [T13, T14, T20, T37]. **Known problem:** while the heat pump compressor runs, its pump overpowers the small `PM` pump and the unit loses flow: water up to 46 °C, AL12, and AL03 ended the request [T38]. It likely needs a hardware fix ([`plans/todo.md`](../plans/todo.md)). Not yet confirmed: the passive cold-water path with early-summer brine, the brine temperature guard (default 8 °C), AL16 ([`plans/todo.md`](../plans/todo.md)) |
| Brine circuit, variant 4 or 5 (in series with the heat pump, inlet or outlet side) | Not tested | Same wiring of `PM`; the brine temperatures differ |
| Separate ground loop (handbook §3.8.8) | Not tested | |
| Heating/cooling circuit of a heat pump, variants 1 to 3 | Not tested | The heat pump must be in cooling mode in summer; water about 16 to 20 °C, so the compressor runs |

### Operating modes

| Mode | Status | Notes |
|------|----------|--------|-------|
| Dehumidify (DEU) request over Modbus, summer | **Works** | Valve and pump, damper, fan and compressor start and stop in order, no alarm, the climate entity shows *Drying* [T11 to T19]. Seen on 0.9.4 at a stop: *Drying* changed to *Fan* when the request ended and to *Idle* when the compressor was off, while the fan could still be running on [T19, T36]. [*Supply fan running*](entity-reference.md#supply-fan-running) has not been through a run yet. The passive cold-water path (water below [PU08](references/MODBUS_REGISTERS.md#pu08), compressor off) is open |
| Integration (INT) request over Modbus, summer (cooling) | Not tested | |
| Season switch without a display ([*Season*](entity-reference.md#season), [HB04](references/MODBUS_REGISTERS.md#hb04)) | **Partly** | Summer to winter works. The select shows the old season right after the write and the new one at the next read cycle [T31]. Back to summer is not tested |
| Fan speed | **Works** (read-only) | The unit sets the speed; a written speed has no effect, raising the band minimum raises it [T22 to T28] |
| Winter integration (heating) | Not tested | Impossible on brine. Needs a warm heating circuit |
| Free cooling | Not tested | |
| Automatic setpoint control (display or room probe), climate *Auto* | Not tested | Simulated display unit in CI only |

## Add your setup

A report from another unit or installation is what moves a row from *Not
tested* to *Works*. Attach the diagnostic output as described under
[Reporting issues](../README.md#reporting-issues) and say which unit, water
circuit, control path and operating modes you used; the maintainer adds the
row with the evidence.
