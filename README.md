# Innova DEH+ / hej.luft HRDS+ — Home Assistant integration

[![Release](https://img.shields.io/github/v/release/mikopp/homeassistant-innova-hrds)](https://github.com/mikopp/homeassistant-innova-hrds/releases)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Lint](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/lint.yaml/badge.svg)](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/lint.yaml)
[![hassfest](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hassfest.yaml)
[![HACS](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hacs.yaml/badge.svg)](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hacs.yaml)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mikopp&repository=homeassistant-innova-hrds&category=integration)

**English** · [Deutsch](README.de.md)

Home Assistant integration (install with **HACS**) for the **Innova
DEH+** / **hej.luft HRDS+** ducted dehumidifiers (models *HRDS+ 30* and
*HRDS+ 50*, or *DEH+ 30* / *DEH+ 50*). It controls and monitors the unit
locally over **Modbus TCP**, without any cloud.

## Compatible devices

The unit is made by **[INNOVA S.r.l.](https://www.innova.it/)** (Storo, Italy).
hej.luft sells it in Austria under its own name as an OEM product.

* **[hej.luft HRDS+ 30 / HRDS+ 50](https://www.hejluft.at/hrds)**, with the
  type-plate codes of the [technical handbook](https://www.hejluft.at/_files/ugd/714411_f1ffc5d222f4476da2e37f29c64a7f93.pdf),
  for example *HRDS+ 30 H R K DC*.
* **[Innova DEH+ 30 / 50 H](https://www.innova.it/en/products/vmc/dehumidifiers/deh-ad-incasso-orizzontale/)**:
  Innova's own name for the same unit, with the same sizes and nominal airflow
  (300 / 500 m³/h). The maintainer's HRDS+ 30 was shipped directly from Italy
  and is physically a DEH+ 30 H; the integration was developed against it. The
  DEH+ installation manual in `doc/references/` describes an older controller,
  not the EVCO "K" board of the HRDS+: registers and behaviour here come from
  the HRDS+ handbooks.

> *If your unit uses the Innova board and is sold under another name, open an
> issue and link its product page.*

## Release 0.9.6

The integration is released and usable.

* **Developed against and tested on** one hej.luft **HRDS+ 30 with
  recirculation** (`R` variant), run **headless** (no CNU2 display, no external
  probes), behind a Modbus RTU→TCP gateway, in the brine circuit of a
  ground-source heat pump. What was seen on it, and which other setups are
  known to work: [Tested units and installations](doc/tested-setups.md).
* **Not tested on real hardware:** the HRDS+ 50, units without recirculation
  (non-`R`), units with a display or external probes (including climate *Auto*,
  which CI tests only against a simulated unit), winter heating and free
  cooling. The open items are in [`plans/todo.md`](plans/todo.md).
* **The fan speed is the unit's.** Home Assistant cannot set a speed directly;
  it can raise the fan through its speed band, and a 0–10 V signal on the unit
  sets it freely ([Fan speed](#fan-speed)).

Reports from other units are very welcome, see
[Reporting issues](#reporting-issues). The aim for 1.0 is in
[Road to 1.0](#road-to-10).

## Quick start

1. [Install](#1-install) the integration with HACS and restart Home Assistant.
2. [Add it](#2-add-the-integration) under *Settings → Devices & Services*,
   with the address of your Modbus-TCP gateway.
3. [Check the setup](#3-check-the-setup): open the **HRDS+ setup** device and
   make sure [*Setup check*](doc/entity-reference.md#setup-check) reads `ok`.
4. **[Choose what Home Assistant may control](#4-choose-what-home-assistant-may-control).**
   Turn on the **Modbus enables** for the functions you want (on/off,
   dehumidify, integration), then [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests). All of them
   are **off after a fresh install** and the integration never turns them on
   by itself. Until then it only monitors: readings and settings work.
5. Try it ([First run](#5-first-run)) and read [How the unit works](#how-the-unit-works)
   for what *Dry* and *Cool* do.

## What it does

* **A climate entity** with room temperature and humidity (where the unit has
  them), the current action (off / idle / fan / drying / cooling / heating) and
  a mode you can set: **Off**, **Standby** (on, nothing requested), **Dry**
  (dehumidify), **Cool** (summer), **Heat** (winter; needs the option *Allow
  winter heating*, never on a brine circuit) and, only with a display or room
  probe, **Auto**. There is no fan mode ([Fan speed](#fan-speed)). What each
  mode does: [Climate in the entity reference](doc/entity-reference.md#climate).
* **Sensors, binary sensors, switches, numbers and selects** for readings,
  alarms, the two requests, setpoints, fan bands, season and probe source. This
  includes three computed airflow sensors ([Airflow sensors](#airflow-sensors)).
* **The fan and the water circuit as read-only values.** The unit runs its
  fan, valve and pump itself; Home Assistant only shows them, with a *Water
  circuit check* summary.
* **A setup device** with a [*Setup check*](doc/entity-reference.md#setup-check) and the switches that decide what
  Home Assistant may do, and an optional **installer device** with the whole
  installer menu (about 240 parameters, off by default).

Every entity, by device: the [entity reference](doc/entity-reference.md). How
the unit itself behaves, with sources and hardware evidence:
[`doc/references/UNIT_BEHAVIOUR.md`](doc/references/UNIT_BEHAVIOUR.md). The
registers: [`doc/references/MODBUS_REGISTERS.md`](doc/references/MODBUS_REGISTERS.md).

## Install and set up

### Before you start

* An Innova DEH+ / hej.luft HRDS+ with the Modbus RTU/RS-485 control board and a
  Modbus-RTU-to-TCP gateway reachable on your network. You need the gateway's
  IP address or hostname, its port (usually [502](doc/references/MODBUS_REGISTERS.md#reg-502)) and the unit's Modbus slave ID
  (factory: 1).
* Home Assistant 2026.10 or newer (see [Requirements](#requirements)).
* [HACS](https://www.hacs.xyz/) installed in Home Assistant.
* Room temperature and humidity readings need the wired CNU2 display or external
  probes (see [Probe requirements](#probe-requirements)). Without either, the
  integration still works; Home Assistant then does the regulating.

### 1. Install

Install it with [HACS](https://www.hacs.xyz/).

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mikopp&repository=homeassistant-innova-hrds&category=integration)

Or in HACS:

Search for **Innova DEH+ / hej.luft HRDS+ Dehumidifier** and select
   **Download**.

Restart Home Assistant.

HACS installs the latest
[GitHub release](https://github.com/mikopp/homeassistant-innova-hrds/releases).
Releases 0.9.x are normal (not "pre-release") releases, so you do not need
HACS' beta versions.

To update, wait for HACS to show a new release of the integration, read its
release notes there, select **Update** and restart Home Assistant. Check the
notes for breaking changes first: they list what to change in automations,
scripts and dashboards.

### 2. Add the integration

Add the integration from **Settings → Devices & Services → Add Integration →
Innova HRDS+**, then provide:

| Field | Default | Notes |
|-------|---------|-------|
| Name  | `HRDS+` | Display name / device name |
| Host  | —       | IP / hostname of the Modbus-TCP gateway |
| Port  | [502](doc/references/MODBUS_REGISTERS.md#reg-502)   | Modbus TCP port |
| Modbus slave ID | `1` | Factory default unit address |
| Scan interval | `30 s` | Polling period (min 5 s) |
| Model | `30`    | Device size: `30` = HRDS+ 30 (max 300 m³/h), `50` = HRDS+ 50 (max 500 m³/h). Sets the airflow defaults. |
| A wired CNU2 display is connected | off | Leave **off** for a unit driven only from Home Assistant (see below). |
| Water register connected to | Heating/cooling circuit | Choose **Brine circuit** if the unit is on the brine of a ground-source heat pump ([Water circuit and brine](#water-circuit-and-brine)). |
| Allow winter heating | off | Lets Home Assistant request heating in winter, with water from the heating circuit, and accepts that the unit heats on its own ([The unit heats on its own](#the-unit-heats-on-its-own)). Off: Home Assistant refuses its own winter integration requests. Cannot be turned on together with a brine circuit. |
| Brine temperature guard sensor | empty | Optional Home Assistant temperature sensor on the brine supply ([Brine temperature guard](#brine-temperature-guard)). |
| Brine guard minimum temperature | 8 °C | Lowest brine temperature at which a request may start. |

All fields can be changed later under **Configure**. The unit size also sets
the maximum airflow for the [airflow sensors](#airflow-sensors), which you can
adjust there.

Before anything is written, the integration checks that the address really is an
HRDS+: the controller must identify itself as EVCO `EPB9…` over Modbus (FC 43)
and its status registers must make sense. Anything else is refused with
*"not an HRDS+"*, so a wrong IP or slave ID cannot have settings written into it.
If the form says *"Cannot reach the unit"*, check the host, the port and the
slave ID.

Without a display, the integration keeps two registers at the values the unit
needs to run under Modbus control. They are the only registers it writes on its
own:

* **[PH01](doc/references/MODBUS_REGISTERS.md#ph01) = 0**: no on/off from a display. With [PH01](doc/references/MODBUS_REGISTERS.md#ph01) = 1 and no display
  the unit stays *Off (display)* and ignores Modbus.
* **[HA00](doc/references/MODBUS_REGISTERS.md#ha00) = 0**: no display sensors.

It reads both with every poll and writes one only when it reads back a wrong
value, for example after a factory reset or a manual change. While both hold 0
nothing is written, not on connection, restart or power cycle, because the
unit keeps its settings and its memory wears with every write. If the unit does
not keep a write, the integration stops trying after a few polls (see
[ADR-0010](.claude/rules/adr/0010-headless-by-default.md)). If you *do* have a
display, tick the option and the integration leaves both alone. Nothing else is
written on connection: the Modbus enables are yours
([step 4](#4-choose-what-home-assistant-may-control)).

### 3. Check the setup

All setup happens through the integration, after it has connected. Nothing needs
to be changed on the unit beforehand. Open **Settings → Devices & Services →
Innova HRDS+** and look at the **HRDS+ setup** device first. The entities are
split over three devices by purpose:

| Device | What is there | When you touch it |
|--------|---------------|-------------------|
| **HRDS+ setup** (linked to the main device) | What decides whether the unit can run at all: the [*Setup check*](doc/entity-reference.md#setup-check), [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests), the Modbus and display enables, probe allocation, remote on/off and season inputs, time programs, wiring facts | Once, after installing, and again if the wiring changes |
| **HRDS+**, main section | Climate, season, the request switches, live readings, status and alarms | Day to day |
| **HRDS+**, *Configuration* section | Tuning: setpoints (only with a probe), fan bands, minimum room temperature, fan run times | Occasionally |
| **HRDS+**, *Diagnostic* section | Water valve and pump, water circuit check, airflow calibration | When troubleshooting |
| **HRDS+ installer** (linked, opt-in) | The rest of the installer menu ([Installer device](doc/entity-reference.md#hrds-installer)) | Rarely, by an installer |

Entity names start with the name you gave the unit when adding the integration
(*HRDS+* by default); the setup and installer devices add *setup* and
*installer*. Every entity, by device: the [entity reference](doc/entity-reference.md).

[*Setup check*](doc/entity-reference.md#setup-check) (setup device) reads `ok` or *Needs attention*. The device page
cannot show attributes, so open the sensor itself (click the row, then
*Attributes*): `to_fix` lists each open item in plain words, in the Home
Assistant language, with what to do about it, and `issues` has the same items
as short codes, explained below.

#### First-use checklist

1. [*Setup check*](doc/entity-reference.md#setup-check) reads `ok`. If not, the `issues` attribute lists what to look
   at:

   | Issue | Meaning and what to do |
   |-------|------------------------|
   | `headless_settings_pending` | Without a display, [PH01](doc/references/MODBUS_REGISTERS.md#ph01) and [HA00](doc/references/MODBUS_REGISTERS.md#ha00) must be 0. The integration writes them on the next poll; if this persists, the unit does not keep the write and the integration gives up (check the log). |
   | `unit_off_by_digital_input` | The remote on/off contact (OFF/OFF terminals, [HB03](doc/references/MODBUS_REGISTERS.md#hb03)) is open, so the unit is forced off. Close it (the factory bridge) or set [HB03](doc/references/MODBUS_REGISTERS.md#hb03) accordingly. |
   | `unit_off_by_scheduler` / `unit_off_by_clock` | A time program or the internal clock holds the unit off. Switch off *Time programs enabled* ([PH03](doc/references/MODBUS_REGISTERS.md#ph03)) for Modbus-only control. |
   | `unit_waiting_for_first_on` | Without a display, [*Unit status*](doc/entity-reference.md#unit-status) still reads *off by display* although [PH01](doc/references/MODBUS_REGISTERS.md#ph01) is 0: the unit keeps a stored OFF until the first Modbus ON. Turn on *Enable on/off via Modbus ([PH02](doc/references/MODBUS_REGISTERS.md#ph02))* and [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests), then switch on [*Unit on/off request*](doc/entity-reference.md#unit-on-off-request) once. |
   | `unit_off_by_display` | Only with the display option ticked: the display has switched the unit off. |
   | `room_temperature_probe_missing` / `room_humidity_probe_missing` | A probe input ([HA02](doc/references/MODBUS_REGISTERS.md#ha02) for temperature on AI2, [HA03](doc/references/MODBUS_REGISTERS.md#ha03) for humidity on AI3) says a probe is connected, but nothing is wired, so the unit waits for a reading. Set the input to *Unused* or wire the probe. |
   | `probe_input_unrecognised` | [HA02](doc/references/MODBUS_REGISTERS.md#ha02) or [HA03](doc/references/MODBUS_REGISTERS.md#ha03) holds a code that is not a documented probe code, so the select shows unknown (the raw code is in the log). Pick an option, or ask the installer. |
   | `time_programs_enabled` | [PH03](doc/references/MODBUS_REGISTERS.md#ph03) is on; the unit may switch itself off on schedule. |
   | `free_cooling_without_outdoor_probe` | [*Enable free cooling/heating*](doc/entity-reference.md#enable-free-cooling-heating) ([PG03](doc/references/MODBUS_REGISTERS.md#pg03)) is on but no outdoor probe delivers a value. Turn it off unless an outdoor probe is fitted. A factory unit usually shows this. |
   | `temperature_unit_fahrenheit` | [PH05](doc/references/MODBUS_REGISTERS.md#ph05) is set to °F; the integration assumes °C. |
   | `water_pump_output_not_configured` | Relay K5 (external water valve and pump output) is not configured, so the unit cannot start the circulation pump. Check [HD05](doc/references/MODBUS_REGISTERS.md#hd05) on the installer device (12 = water valve) and the wiring. |
   | `winter_dehumidify_on_brine` | Brine circuit, no brine temperature guard, but [PU02](doc/references/MODBUS_REGISTERS.md#pu02) allows dehumidifying in winter: the coil can freeze. Set [*Winter dehumidification*](doc/entity-reference.md#winter-dehumidification) to *Disabled*, or configure a [brine temperature guard](#brine-temperature-guard). |
   | `unit_heats_on_its_own` | In winter the unit heats by itself and *Allow winter heating* is off. Accept it (turn the option on) or stop it, see [The unit heats on its own](#the-unit-heats-on-its-own). |
   | `unit_heats_on_its_own_on_brine` | The same on a brine circuit, where the unit pumps cold brine through the register instead of heating. Lower the winter setpoint (and [PH09](doc/references/MODBUS_REGISTERS.md#ph09)) or switch the unit off in winter. |
   | `winter_heating_without_integration` | *Allow winter heating* is on but the unit has no integration function ([PG02](doc/references/MODBUS_REGISTERS.md#pg02) = 0), so nothing can heat. Turn the option off or enable [PG02](doc/references/MODBUS_REGISTERS.md#pg02) on the unit. |

2. **Probe settings match what is wired.** Without a display and without
   probes, *T/H probe source ([HA00](doc/references/MODBUS_REGISTERS.md#ha00))* is *None / external probes* (the
   integration sets it) and both *T/H probe temperature / humidity input*
   selects are *Unused*. Select a probe type only where a probe is really
   wired, otherwise the unit raises alarm AL28 / AL34.
3. **The unit facts are right:** *Machine type*, *Recirculation damper relay
   allocation* (not `disabled` on an `R` model), *Remote on/off input* and
   *contact closed*, *Temperature unit* (°C).
4. **Season and water circuit fit your installation:** [*Season*](doc/entity-reference.md#season), and the options
   *Water register connected to* and *Allow winter heating*. On a circuit fed by
   a pump the HRDS+ switches (brine in particular), watch *Water valve / pump
   output* turn *On* with the first request and [*Water circuit check*](doc/entity-reference.md#water-circuit-check) stay
   `ok` ([Water circuit and brine](#water-circuit-and-brine)).
5. **Minimum room temperature ([PU13](doc/references/MODBUS_REGISTERS.md#pu13))** in the Configuration section: the unit
   refuses to dehumidify below it. With no room temperature probe, a Modbus
   dehumidify request started the compressor at the shipped 10 °C
   ([T15](doc/references/UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware));
   a higher value is untested.
6. Each setup switch carries a `hint` attribute that says when to leave it on or
   off. Two matter most: leave [*Enable free cooling/heating*](doc/entity-reference.md#enable-free-cooling-heating) ([PG03](doc/references/MODBUS_REGISTERS.md#pg03)) **off**
   unless an outdoor probe is wired, and leave *Enable on/off via display*
   ([PH01](doc/references/MODBUS_REGISTERS.md#ph01)) **off** without a CNU2 display. The Modbus enables are your choice
   (next step).

When the setup check is `ok`, continue with
[step 4](#4-choose-what-home-assistant-may-control).

### 4. Choose what Home Assistant may control

You are in charge of two things, both on the **HRDS+ setup** device. The
integration never turns either on by itself.

1. **The Modbus enables on the unit**, one per function. Turn on the ones for
   the functions you want Home Assistant to control. Leave a function's enable
   off to keep it on the unit's own controls (display, remote contact, digital
   inputs): Home Assistant then only shows what the unit does, and refuses that
   operation with a message naming the switch to turn on.
2. [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests), the integration's own safety gate (below).

With every enable off (or the gate off), the integration is a monitor: every
reading, status, alarm and setting works, and nothing can make the unit act.

#### Which enable gives which function

| To do this from Home Assistant | Turn on (setup device) | Register | While it is off |
|---|---|---|---|
| Switch the unit **on and off**: climate *Off*, climate *turn on/off*, switching from *Off* to any mode, [*Unit on/off request*](doc/entity-reference.md#unit-on-off-request) | **Enable on/off via Modbus ([PH02](doc/references/MODBUS_REGISTERS.md#ph02))** | [1778](doc/references/MODBUS_REGISTERS.md#reg-1778) | The unit's own controls switch it. The climate offers only the modes on the side the unit is on: no *Off* while it runs, only *Off* while it is off. |
| **Dehumidify**: climate *Dry*, [*Dehumidify request*](doc/entity-reference.md#dehumidify-request) | **Enable dehumidify (DEU) via Modbus ([PH28](doc/references/MODBUS_REGISTERS.md#ph28))** | [1870](doc/references/MODBUS_REGISTERS.md#reg-1870) | No *Dry*. A dehumidify request from the unit's own humidity logic or the DEU input still shows as *Dry*. |
| **Cool in summer, heat in winter**: climate *Cool* / *Heat*, [*Integration request (cool in summer, heat in winter)*](doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter) | **Enable integration (INT) via Modbus ([PH27](doc/references/MODBUS_REGISTERS.md#ph27))**; the unit also needs the integration function ([PG02](doc/references/MODBUS_REGISTERS.md#pg02), `DC` models) | [1869](doc/references/MODBUS_REGISTERS.md#reg-1869) | No *Cool* / *Heat*. The unit's own integration (its room temperature logic, the INT input) still shows. |

Good to know:

* **Full control** of a unit without a display: turn on all three, then *Allow
  operational requests*.
* A request that is still on when you turn its enable on starts at once
  ([UNIT_BEHAVIOUR §3.3](doc/references/UNIT_BEHAVIOUR.md#33-requests-deu-and-int)).
  The integration therefore checks that like a start (the gate, the brine guard,
  the season).
* The unit keeps its settings across a power cycle, so the enables stay as you
  left them ([UNIT_BEHAVIOUR §3.6](doc/references/UNIT_BEHAVIOUR.md#36-persistence-across-a-power-cycle)).
* Fan speed bands and every other setting (setpoints, selects, setup entities)
  need no enable.

#### Allow operational requests

> **This is the switch that makes the unit operational.** After a fresh install
> [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests) (on the **HRDS+ setup** device) is **off**.
> While it is off, Home Assistant cannot make the unit act.

| Blocked while the switch is off | Always works |
|---|---|
| Turning the unit **on** (also climate *Auto*), **dehumidify** (climate *Dry*, [*Dehumidify request*](doc/entity-reference.md#dehumidify-request)), **integration** (climate *Cool* / *Heat*, [*Integration request (cool in summer, heat in winter)*](doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter)) | Turning things **off** (climate *Off*, switches off), reading every sensor, and every configuration write (setpoints, selects, setup entities) |

A blocked request fails with *"Operational requests are not allowed yet. Review
the setup entities, then turn on 'Allow operational requests'."* That message
means this switch is still off.

To turn it on, open the **HRDS+ setup** device and toggle **Allow operational
requests**, or call the service (the entity ID of a unit named *HRDS+*):

```yaml
action: switch.turn_on
target:
  entity_id: switch.hrds_setup_allow_operational_requests
```

* It is the integration's own safety gate, not a register on the unit, and it
  is not tied to the setup check: you decide when you have looked at the setup
  entities. Turn it on once the setup check is `ok`. Your choice is remembered
  across restarts and reloads.
* Turning it off again does not stop a running unit; it only refuses new
  requests. To stop the unit, set the climate to *Off*: that clears both
  requests and switches the unit off (with [PH02](doc/references/MODBUS_REGISTERS.md#ph02) on).

### 5. First run

1. Set the climate entity to **Dry** (or turn on [*Dehumidify request*](doc/entity-reference.md#dehumidify-request)). Only
   turning on [*Unit on/off request*](doc/entity-reference.md#unit-on-off-request) is not enough on a unit without a display
   or room probe: it then has nothing to act on, so the climate entity shows
   *Standby* with the action *Idle*.
2. Watch [*Unit status*](doc/entity-reference.md#unit-status): a unit waiting for its first request reads *Off
   (Modbus)* and changes to *On*. The recirculation fan (`R` units) starts
   with the request.
3. If it does not start, look at the [*Setup check*](doc/entity-reference.md#setup-check) `issues`, at the error
   Home Assistant showed for the request (a refused request names the reason),
   and at the Home Assistant log. See [Reporting issues](#reporting-issues) if
   you need help.

## How the unit works

A short summary for using the integration. The full description, with handbook
references and what was seen on real hardware, is
[`doc/references/UNIT_BEHAVIOUR.md`](doc/references/UNIT_BEHAVIOUR.md).

### What is inside

The unit sits in the supply duct of the central ventilation (MVHR). The air
passes an **evaporator** (cold, so moisture condenses) and then a **water
register**. The compressor's heat goes into the building's water circuit; an
internal valve decides whether that warm water also reheats the dried air. An
external valve and pump connect the unit to your water circuit: the heating and
cooling circuit of a heat pump, the brine of a ground-source heat pump, or a
separate ground loop. `R` units add a recirculation fan and damper that run with
**every** request ([Fan and recirculation](#fan-and-recirculation)). Details:
[UNIT_BEHAVIOUR §2](doc/references/UNIT_BEHAVIOUR.md#2-hardware-air-path-water-path-terminals).

### Two requests

The unit knows exactly two requests, and the integration's switches and climate
modes map onto them:

* **DEU**, dehumidify: [*Dehumidify request*](doc/entity-reference.md#dehumidify-request), climate **Dry**.
* **INT**, integration: [*Integration request (cool in summer, heat in winter)*](doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter),
  climate **Cool** in summer and **Heat** in winter.

What they do depends on the season and on how cold the water is.

### Operating modes in summer

| Mode | Requested by | What the unit does | Air leaves |
|------|--------------|--------------------|-----------|
| **Dehumidify** | DEU (**Dry**) | The compressor runs; its heat reheats the air | Dried, at about room temperature |
| **Cool and dehumidify** | INT (**Cool**) | The compressor runs; all its heat goes into the water | Dried and cold |
| **Passive (cold water)** | Any request while the water is below [PU08](doc/references/MODBUS_REGISTERS.md#pu08) (factory 10 °C) | The compressor stays off; the cold water cools and dries the air | Dried and cooled, without compressor |

The unit picks the path from the water temperature; nothing has to be set.
Cold brine early in summer runs the passive path, a heat pump in cooling mode
delivers water warm enough for the compressor, and water that is too warm
blocks the request (alarm AL03). [*Force dehumidify when cooling*](doc/entity-reference.md#force-dehumidify-when-cooling) ([PU05](doc/references/MODBUS_REGISTERS.md#pu05),
factory on) is what makes an INT request start the compressor; with it off the
unit presumably cools with the water only, which is not tested on a real unit.
The rest, with sources:
[UNIT_BEHAVIOUR §6](doc/references/UNIT_BEHAVIOUR.md#6-summer-operation).

### Operating modes in winter

| Request | What the unit does |
|---------|--------------------|
| INT (**Heat**) | **Heating support**: compressor off, warm water from the heating circuit through the water register. Home Assistant requests it only with the option *Allow winter heating*, never on brine; the unit also raises it by itself ([The unit heats on its own](#the-unit-heats-on-its-own)) |
| DEU (**Dry**) | Only if [PU02](doc/references/MODBUS_REGISTERS.md#pu02) ([*Winter dehumidification*](doc/entity-reference.md#winter-dehumidification)) allows it; factory: disabled. On brine only with a passing [brine temperature guard](#brine-temperature-guard) |

The unit has **no heat source of its own**: the air only gets warmer if the
building's heating circuit delivers warm water. The climate shows *Heating*
only when the unit can be doing it
([Climate](doc/entity-reference.md#climate)); otherwise *Idle*, or *Drying*
while the unit dehumidifies. Heating is not tested on a real unit. On a brine
circuit the handbook forbids heating and active winter dehumidifying (the
register can freeze) and recommends switching the unit off in winter, see
[Water circuit and brine](#water-circuit-and-brine). The rest:
[UNIT_BEHAVIOUR §7](doc/references/UNIT_BEHAVIOUR.md#7-winter-operation).

### How to use it

1. **Set the season** with [*Season*](doc/entity-reference.md#season) (without a display; see
   [Season and winter heating](#season-and-winter-heating)).
2. **Pick the mode on the climate entity:** **Dry** to dry the air at room
   temperature, **Cool** to dry and cool (summer), **Auto** to let the unit
   decide from its own room sensors (only with a display or room probe),
   **Standby** to have it on and waiting (without a display or room probe),
   **Off** to stop: it clears both requests and turns the unit off. *Turn on*
   goes to Standby (Auto where the unit regulates by itself), *turn off* to
   Off. The switches [*Dehumidify request*](doc/entity-reference.md#dehumidify-request) and *Integration request (cool in
   summer, heat in winter)* do the same per request. Every start needs the
   matching Modbus enable and [Allow operational requests](#4-choose-what-home-assistant-may-control).
3. **Decide who regulates.** Without a display or room probe the unit runs
   while a request is on and ignores its setpoints, so let Home Assistant
   switch **Dry** / **Cool** on and off (for example a generic hygrostat or
   thermostat on your own sensors). With a display or probe the unit regulates
   to its own targets ([Setting target humidity and target temperature](#setting-target-humidity-and-target-temperature)).
4. **Leave the passive path to the unit.** You can see it run: the request is
   on, [*Water valve / pump output*](doc/entity-reference.md#water-valve-pump-output) is *On*, [*Water temperature*](doc/entity-reference.md#water-temperature) is below
   [PU08](doc/references/MODBUS_REGISTERS.md#pu08) and [*Compressor status*](doc/entity-reference.md#compressor-status) is not *On*. The water check then lists
   `water_below_compressor_limit`, which here is information, not a fault.
5. **The fan** starts at the active mode's minimum speed; raise the minimum
   to run it faster ([Fan speed](#fan-speed)).

## Using the integration

### Season and winter heating

Without a display the season is set with [*Season*](doc/entity-reference.md#season) ([HB04](doc/references/MODBUS_REGISTERS.md#hb04): 4 summer, 3 winter).
Because winter turns the integration request from cooling into heating, the
integration guards it:

* An integration request (switch, or climate Cool/Heat) is **refused unless the
  unit reports summer**, unless you enabled **Allow winter heating**. With the
  season on *auto* ([1583](doc/references/MODBUS_REGISTERS.md#reg-1583)), the mode status ([1110](doc/references/MODBUS_REGISTERS.md#reg-1110)) decides which season is
  in force; an unknown season counts as not summer.
* Switching the season to winter is refused while an integration request is on,
  and on brine without a passing brine guard while the unit is on and could
  dehumidify in winter by itself ([PU02](doc/references/MODBUS_REGISTERS.md#pu02) enabled).
* *Allow winter heating* governs only what Home Assistant requests. The unit
  can still heat by itself, see below.

### The unit heats on its own

With a room temperature source (a display, or a probe on AI2) and the
integration function ([PG02](doc/references/MODBUS_REGISTERS.md#pg02)), the unit raises its own winter integration
request when the room falls below **[SEtH](doc/references/MODBUS_REGISTERS.md#seth) − [PF12](doc/references/MODBUS_REGISTERS.md#pf12)** and drops it above
[SEtH](doc/references/MODBUS_REGISTERS.md#seth) + [PF12](doc/references/MODBUS_REGISTERS.md#pf12). It does not ask Home Assistant, and *Allow winter heating*
cannot stop it: the unit knows nothing of that option. The factory cap on
[SEtH](doc/references/MODBUS_REGISTERS.md#seth) ([PH10](doc/references/MODBUS_REGISTERS.md#ph10), 14 °C) leaves the unit heating whenever the room is below
13.5 °C ([UNIT_BEHAVIOUR §3.3](doc/references/UNIT_BEHAVIOUR.md#33-requests-deu-and-int)).
Headless without a probe it never heats by itself.

The integration tells you instead of pretending otherwise:

* [*Unit heats on its own*](doc/entity-reference.md#unit-heats-on-its-own) is **on** while the unit, switched on in winter, can
  heat by itself. Its attributes give the thresholds, the room temperature and
  whether it heats right now. It is not created without a room temperature
  source or the integration function.
* The climate entity shows **Auto** with the action **Heating** while it does,
  and **Off** switches the unit off, since only that stops its own logic.
* The setup check lists `unit_heats_on_its_own` while *Allow winter heating* is
  off, and `unit_heats_on_its_own_on_brine` on a brine circuit.

To react, either accept it (turn *Allow winter heating* on) or stop it:

* **Lower the threshold**: set *[PH09](doc/references/MODBUS_REGISTERS.md#ph09) Winter setpoint min* (installer device,
  enable it in the options) to 5 °C or less, then the winter setpoint to 5 °C.
  The unit then only heats below 4.5 °C.
* **Switch the unit off in winter** (what the handbook recommends on brine).
* Setting [PG02](doc/references/MODBUS_REGISTERS.md#pg02) = 0 or unallocating the room probe also stops it, but takes
  summer cooling or the unit's own humidity control with it.

### Water circuit and brine

The unit switches its water circuit itself: relay K5 drives the external valve
and, together with it, the pump output. The integration only shows it (*Water
valve / pump output*) and never overrides it. The [*Water circuit check*](doc/entity-reference.md#water-circuit-check) sensor
(attribute `issues`) flags:

| Issue | Meaning |
|-------|---------|
| `pump_off_while_compressor_runs` | Compressor on but valve and pump off: no water through the condenser |
| `water_too_warm` | While circulating, the water is above [PC07](doc/references/MODBUS_REGISTERS.md#pc07) (30 °C); alarm AL03 follows after [PA16](doc/references/MODBUS_REGISTERS.md#pa16) |
| `water_below_compressor_limit` | While circulating, the water is below [PU08](doc/references/MODBUS_REGISTERS.md#pu08): the compressor will not start and the unit runs on the [passive cold-water path](#operating-modes-in-summer). Expected with cold brine in early summer, not a fault |
| `high_water_temperature_alarm` / `low_water_temperature_alarm` / `antifreeze_alarm` | AL03 / AL04 / AL16 active |
| `brine_unit_on_in_winter` | Brine circuit, winter, unit on. The anti-stagnation cycle pulses valve and pump and can blow short bursts of cold air; the handbook recommends switching the unit off in winter |
| `brine_guard_blocking` | The [brine temperature guard](#brine-temperature-guard) currently refuses requests |

With **Water register connected to = Brine circuit** the handbook forbids
heating and active winter dehumidifying, because the coil can freeze. The
integration therefore refuses winter integration requests regardless of the
heating option, and winter dehumidify requests unless a brine temperature guard
is configured and passing. Without a guard, the setup check flags [PU02](doc/references/MODBUS_REGISTERS.md#pu02) if it
allows winter dehumidifying. The brine variants (handbook 4 to 6) switch an
additional brine pump through the unit's PM output; that is what *Water valve /
pump output* reflects. The maintainer's unit is wired as variant 6 (a branch
parallel to the heat pump), see [Tested units and installations](doc/tested-setups.md).

#### Brine temperature guard

The unit cannot tell how cold the brine is before it starts, and its own
protections react only after the fact
([UNIT_BEHAVIOUR §11.4](doc/references/UNIT_BEHAVIOUR.md#114-water-temperature-thresholds-summary)).
If Home Assistant has a temperature sensor on the brine supply, for example from
the heat pump, set it as **Brine temperature guard sensor** in the options.
Then:

* A dehumidify or integration request, or switching the unit on while one is
  latched, **starts only while that sensor reads at least the minimum**
  (**Brine guard minimum temperature**, default 8 °C) **and has reported within
  the last 24 h**. This applies in every season and to any water circuit. A
  sensor that is unavailable, not numeric or not a temperature also blocks.
  Switching off is always allowed.
* 8 °C stays above the unit's own frost alarm (AL16, which stops the fan) and
  below [PU08](doc/references/MODBUS_REGISTERS.md#pu08) (10 °C), so early-summer brine can still run the passive path.
* On a brine circuit a passing guard is what permits **dehumidifying in
  winter** (and only if [PU02](doc/references/MODBUS_REGISTERS.md#pu02) allows it; the factory value is *Disabled*).
  Without a guard it is always refused. Winter heating stays impossible on
  brine, guard or not.
* [*Brine temperature guard*](doc/entity-reference.md#brine-temperature-guard) (device class *problem*) is **on** while the guard
  blocks. Its attributes give the source, temperature, minimum, last report and
  reason (`too_cold`, `stale`, `unavailable`, `not_a_number`,
  `not_a_temperature`). It exists only when a sensor is configured and stays
  available while the Modbus link is down.

The guard decides whether a request may **start**. It does not stop a request
that is already running when the brine cools; the indicator turns on and the
unit's own protections (AL16, AL11) remain in charge.

### Setting target humidity and target temperature

Without a display or a configured room probe the unit **ignores** its setpoints
([UNIT_BEHAVIOUR §3.4](doc/references/UNIT_BEHAVIOUR.md#34-setpoints)). The
integration then does not create them and the climate entity offers no targets:
use Home Assistant (a generic hygrostat or thermostat on your own sensors) to
switch **Dry** / **Cool** on and off. The decision is made at start-up from
[HA02](doc/references/MODBUS_REGISTERS.md#ha02)/[HA03](doc/references/MODBUS_REGISTERS.md#ha03); reload the integration after wiring a probe.

With a display or probe, both targets are on the **climate entity** (and as
numbers: [*Humidity setpoint*](doc/entity-reference.md#humidity-setpoint), [*Summer setpoint*](doc/entity-reference.md#summer-setpoint), [*Winter setpoint*](doc/entity-reference.md#winter-setpoint)):

* **Target humidity** ([PU01](doc/references/MODBUS_REGISTERS.md#pu01), %RH) is the level the unit dehumidifies towards.
  It acts only while the unit is on and dehumidifying, that is in **Dry** or
  **Cool**; in **Off** it is stored and does nothing. The unit limits it to
  [PH29](doc/references/MODBUS_REGISTERS.md#ph29)–[PH30](doc/references/MODBUS_REGISTERS.md#ph30).
* **Target temperature** is the summer setpoint, the room temperature the unit
  aims for in **Cool**. The winter setpoint is its own number, for the heating
  season.

### Fan and recirculation

* On an `R` unit every **Dry** or **Cool** request opens the recirculation
  damper and runs the fan (damper first, fan after a delay, then the
  compressor). [*Recirculation damper*](doc/entity-reference.md#recirculation-damper) and [*Supply fan output*](doc/entity-reference.md#supply-fan-output) show it. So an
  `R` unit never dehumidifies on passive airflow; the fan runs at least at its
  band minimum.
* With no request (off, or on and idle) the fan is off and only the MVHR moves
  air: [*Supply fan status*](doc/entity-reference.md#supply-fan-status) reads *Off*.
* A non-`R` unit has no fan and no damper and dehumidifies on the MVHR flow
  alone.

Sources, vendor statements and an unofficial field workaround:
[UNIT_BEHAVIOUR §9.3](doc/references/UNIT_BEHAVIOUR.md#93-recirculation-is-coupled-to-every-request-r-variant)
and [§9.4](doc/references/UNIT_BEHAVIOUR.md#94-non-r-variant).

### Airflow sensors

Three computed sensors estimate the recirculation airflow from the fan output:
[*Supply fan airflow*](doc/entity-reference.md#supply-fan-airflow), live in m³/h and updated every poll, and two static ones
with the configured maximum ([entity reference](doc/entity-reference.md)). The
formula is proportional, `Q = (output % / 100) × Q_max`. The fan counts as
running only when the unit's own fan status says *On* or *Stopping* (the
run-on); otherwise the estimate is 0 m³/h.

`Q_max` comes from the model (HRDS+ 30: 300 m³/h, HRDS+ 50: 500 m³/h). Change
*Supply fan max airflow (m³/h)* under **Configure** if your duct or filter
changes the flow at 100 %. It is an open-loop estimate: loaded filters or
restrictive ducts make the real flow lower. The derivation and a two-point
calibration recipe are in
[Translating fan speed to airflow](doc/references/README.md#translating-fan-speed-to-airflow).

### Fan speed

**The fan is the unit's; Home Assistant shows it but cannot switch it or set a
speed directly.** The unit runs the fan with every dehumidify or integration
request and stops it after a run-on. It has no register for a fan-speed request
from Modbus: [PM20](doc/references/MODBUS_REGISTERS.md#pm20) ("manual fan speed") holds the **display's** manual request,
the unit sets it itself, and a value written to it has no effect. So there is no fan
entity and the climate has no fan mode; the fan is shown by readings only
([*Supply fan running*](doc/entity-reference.md#supply-fan-running), [*Supply fan status*](doc/entity-reference.md#supply-fan-status), [*Supply fan output*](doc/entity-reference.md#supply-fan-output), *Manual fan
speed*).

What you can change over Modbus is the speed band: *Fan min speed* and *Fan max
speed* for dehumidify and for cooling. The fan starts at the band minimum (50 %
as shipped) and the unit keeps its speed within the band. On the reference unit,
raising the minimum above the running speed raised the fan within a minute;
lowering it did not slow the fan, and the next run starts at the minimum.
Lowering the maximum and the cooling band are not tested. Each change is a write
to the unit's memory, so do not drive the band from a control loop. Details:
[UNIT_BEHAVIOUR §9.1](doc/references/UNIT_BEHAVIOUR.md#91-bands-and-sources); the
open tests: [`plans/fan-speed-tests.md`](plans/fan-speed-tests.md).

For free control of the speed, the unit takes a 0–10 V signal on its `FAN+`
terminals, placed across the band ([UNIT_BEHAVIOUR §2.3](doc/references/UNIT_BEHAVIOUR.md#23-terminals-inputs-and-outputs)).

## Entity reference

Every entity, with its register and what it shows, is in the
**[entity reference](doc/entity-reference.md)**, organised like the devices the
integration creates: **[HRDS+](doc/entity-reference.md#hrds)** (operating
surface, with a *Diagnostic* section), **[HRDS+ setup](doc/entity-reference.md#hrds-setup)**
(the one-time checklist) and **[HRDS+ installer](doc/entity-reference.md#hrds-installer)**
(the opt-in installer menu).

## Probe requirements

The unit's control board exposes temperature and humidity readings, but most
probes must be **installed by the installer**; they do not come built in.

| What you need | Hardware | Notes |
|--------------|----------|-------|
| Room temperature | NTC 10 kΩ B3435 (wall or duct mount) **or** CNU2 display | For automatic cooling/heating and dehumidify gating |
| Room humidity | 0–10 V or 4–20 mA humidity transmitter **or** CNU2 display | For automatic dehumidify |
| Outdoor temperature | NTC 10 kΩ B3435, IP65-rated | Only for free cooling/heating ([PG03](doc/references/MODBUS_REGISTERS.md#pg03)); otherwise optional |
| Exhaust / supply air temperature | NTC 10 kΩ B3435 | Optional; display and monitoring only |

**With no display and no external probes** (the default, with *A wired CNU2
display is connected* left off) the integration sets [HA00](doc/references/MODBUS_REGISTERS.md#ha00) = 0 and [PH01](doc/references/MODBUS_REGISTERS.md#ph01) = 0
for you. The unit then responds only to explicit Modbus commands: dehumidify and
cooling work normally; only the automatic setpoint-based triggers are inactive.
Probe readings that are not wired (room temperature and humidity, outdoor,
exhaust, supply air, air quality, the probe-OK flags) show **unknown**, and the
climate entity shows no current temperature or humidity. That is expected, not
an error. The factory-wired water and evaporator temperatures keep working.

What each display and probe configuration does:
[UNIT_BEHAVIOUR §8](doc/references/UNIT_BEHAVIOUR.md#8-display-and-probe-configurations).
The inputs, probe types and [HA00](doc/references/MODBUS_REGISTERS.md#ha00) values:
[MODBUS_REGISTERS §5.4](doc/references/MODBUS_REGISTERS.md#54-sensors-and-probes).

## Requirements

* **Home Assistant 2026.10 or newer.**
* `pymodbus` 3.13.1 or newer (declared in the manifest; Home Assistant 2026.10
  ships 3.13.1).

### Availability

Entities go **`unavailable`** when a poll fails, rather than continuing to show
the last good reading. If you drive this integration from templates or
automations, gate them on `has_value()`: a dehumidifier that acts on a
three-day-old humidity reading is worse than one that does nothing.

Writes that the unit rejects raise an error. In an automation a failed service
call **aborts the remaining steps**, so if you issue several writes in sequence,
either put the critical one first or mark the rest `continue_on_error: true`.

## Disclaimer

Use at your own risk. This is pre-1.0 software, and many of the writable registers
change installer-level behaviour. Only change settings you understand.

## Reporting issues

**Issues without the diagnostic output cannot be supported.** Whatever the
problem (a wrong value, a refused write, a unit that does not start), the
read-only diagnostic script shows what the unit reports and what the
integration would do, and without it there is nothing to go on.

It only reads (Modbus function codes 03, 04 and 43) and never writes to the
unit. It needs a copy of this repository (the HACS download contains only the
component) and `pymodbus`:

```
git clone https://github.com/mikopp/homeassistant-innova-hrds.git
cd homeassistant-innova-hrds
pip install 'pymodbus>=3.13.1'
python3 tests/diagnose_hrds.py <gateway-ip> --json diag.json
```

Add `--port N` / `--unit N` if your gateway does not use port [502](doc/references/MODBUS_REGISTERS.md#reg-502) / slave id 1,
and `--display` if a CNU2 display is fitted. **Attach `diag.json` to the issue.**
The file contains the gateway address in its `host` field: replace it before
posting.

Please also say which unit it is (HRDS+ 30 or 50, `R` or non-`R`, display or
headless, which probes are wired), the Home Assistant and integration versions,
the `issues` of [*Setup check*](doc/entity-reference.md#setup-check), and the relevant part of the Home
Assistant log. The issue form asks for all of this.
[Open an issue](https://github.com/mikopp/homeassistant-innova-hrds/issues/new/choose).

## Road to 1.0

1.0 is reached when a full automation runs in Home Assistant that combines the
integration with the automation of the MVHR and the dehumidification, proven in
summer 2027. [`plans/todo.md`](plans/todo.md) lists the open items to clarify
until then. The owner would welcome testing with another unit that has a
display, external probes, or is a different size or variant. Until then the
releases stay 0.x.

## Design decisions

Why the integration behaves as it does (what it never writes, which requests
it refuses, what the climate modes mean) is recorded one decision per file in
[`doc/adr/`](doc/adr/README.md).

## Credits

Architecture closely follows the
[`ha_comfoconnectpro`](https://github.com/hstrohmaier/ha_comfoconnectpro)
integration. Documentation © Innova / hej.luft (see `doc/references/`).
