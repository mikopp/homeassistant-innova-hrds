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

| Unit | Status | Notes |
|------|--------|-------|
| hej.luft **HRDS+ 30** `H R K DC` (Innova DEH+ 30 H), headless | **Works** | The maintainer's unit (reference unit). Seen: identity and the whole register map read, the required settings and the first Modbus ON, OFF written over Modbus [T1 to T9, T14]; full dehumidify cycles with valve and pump, damper, fan and compressor read-backs, start and stop [T10 to T19]; the fan speed owned by the unit [T22 to T28]; the season switch [T31]; the on/off state kept across a power cycle [T30]. An integration (INT) cycle is not recorded yet |
| HRDS+ 50 / DEH+ 50 H | Not tested | The size has no register (the `model` option sets it). Only the airflow estimate differs |
| Units without recirculation (non-`R`) | Not tested | No fan, damper or fan entities are created when the damper output (1134) reads *disabled* |
| Units without the integration function (no `DC`, PG02 = 0) | Not tested | *Cool* and *Heat* are not offered |
| Unit with a CNU2 display | Not tested | The display and `HA00 = 1/2` path, the headless sync skipped |
| Unit with external room or outdoor probes | Not tested | Target humidity and temperature, climate *Auto* mode (CI only) |

## Installation scenarios

### Control path

| Scenario | Status | Notes |
|----------|--------|-------|
| Headless (`PH01 = 0`, `HA00 = 0`), no display, no probes | **Works** | Home Assistant is the controller: requests over Modbus. First Modbus ON takes the unit out of *off by display* [T7]. Every setup-check issue cleared once the settings were made |
| Modbus RTU (RS-485) to TCP gateway | **Works** | Reads must be small: a 120-register read got no reply, 10-register reads cover the map [T9]. Modbus unit id 1, the default |
| Native Modbus TCP, no gateway | Not tested | |
| Installed behind a Zehnder ComfoAir Q350 (MVHR) | Context | Where the reference unit is installed. Nothing about coupling to the MVHR is recorded |

### Water circuit

The unit's water source decides what it can do (see
[`references/UNIT_BEHAVIOUR.md` §2.2](references/UNIT_BEHAVIOUR.md) for the
handbook's variants 1 to 6 and the separate ground loop).

| Scenario | Status | Notes |
|----------|--------|-------|
| **Brine circuit of a ground-source heat pump, handbook variant 6**: the unit sits in a branch **parallel** to the heat pump, with its own small brine pump on the `PM` output. It runs independently of the heat pump and also at the same time | **Partly** | Seen: the unit starts the pump on a request, the pump runs and `sensor.water_valve_pump` follows [T10, T11]; valve and pump off within a minute of the request ending [T19]; the anti-stagnation pulses while the unit is on, none while it is off [T13, T14, T20, T37]. **Known problem:** while the heat pump compressor runs, its pump overpowers the small `PM` pump and the unit loses flow: water up to 46 °C, AL12, and AL03 ended the request [T38]. It likely needs a hardware fix ([`plans/todo.md`](../plans/todo.md)). Not yet confirmed: the passive cold-water path with early-summer brine, the brine temperature guard (default 8 °C), AL16 ([`plans/todo.md`](../plans/todo.md)) |
| Brine circuit, variant 4 or 5 (in series with the heat pump, inlet or outlet side) | Not tested | Same wiring of `PM`; the brine temperatures differ |
| Separate ground loop (handbook §3.8.8) | Not tested | |
| Heating/cooling circuit of a heat pump, variants 1 to 3 | Not tested | The heat pump must be in cooling mode in summer; water about 16 to 20 °C, so the compressor runs |

### Operating modes

| Mode | Status | Notes |
|------|--------|-------|
| Dehumidify (DEU) request over Modbus, summer | **Works** | Valve and pump, damper, fan and compressor start and stop in order, no alarm, the climate entity shows *Drying* [T11 to T19]. Seen on 0.9.4 at a stop: *Drying* changed to *Fan* when the request ended and to *Idle* when the compressor was off, while the fan could still be running on [T19, T36]. `binary_sensor.supply_fan_running` has not been through a run yet. The passive cold-water path (water below `PU08`, compressor off) is open |
| Integration (INT) request over Modbus, summer (cooling) | Not tested | |
| Season switch without a display (`select.season`, HB04) | **Works** | Winter and back to summer; the read-back shows the new season at the next read cycle [T31] |
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
