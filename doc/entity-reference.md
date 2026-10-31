# Entity reference

Every entity the integration creates, grouped by the **device** it lives on.
This file is the single source of truth for entities: the README and the other
docs link here and do not repeat it, and `tests/wiring_check.py` fails when
this file and the code differ
([ADR-0030](../.claude/rules/adr/0030-entity-reference-is-the-source-of-truth-and-mirrors-the-devices.md)).
It is in English only. Back to the [README](../README.md).

**How to read the tables.**

* `platform.key` is the entity's key: the suffix of its unique id and its
  translation key. Home Assistant builds the visible entity id from the device
  name and the display name (column *Name*), so the setup check, for example,
  is `sensor.hrds_setup_setup_check`. The tables omit the device prefix.
* *Register* is the decimal Modbus address (see
  [`references/MODBUS_REGISTERS.md`](references/MODBUS_REGISTERS.md)); a dash means the
  value is computed or kept by the integration.
* Entities marked **¹** are only meaningful when a room temperature probe is
  present (CNU2 display or external NTC). Entities marked **²** require a room
  humidity probe. Entities marked **³** are built into the unit's control board
  and are always available. See [probe requirements](../README.md#probe-requirements)
  and [UNIT_BEHAVIOUR §8](references/UNIT_BEHAVIOUR.md#8-display-and-probe-configurations)
  for full detail.

## The three devices

A unit shows up as three linked devices (ADR-0016, ADR-0017). They exist
because the entities have three different audiences and three different risks:

| Device | Holds | Why it is separate | You use it |
|---|---|---|---|
| **HRDS+** (main) | Operating the unit, the tuning that belongs to it, and diagnostics | The page a household looks at. It is for operating and watching the unit; no one-off installation task is on it | Daily; *Configuration* occasionally; *Diagnostic* when troubleshooting |
| **HRDS+ setup** (child) | What decides whether the unit can run at all: the setup check, the operation gate, the Modbus enables, probe and wiring facts | A checklist, not a control surface. Keeping it off the main page leaves the operating surface clean, and these are the settings that put a unit into "off by display" when wrong | Once after installing, again when the wiring changes |
| **HRDS+ installer** (child, **opt-in**) | The installer menu of the handbook (§5.3), about 240 parameters | Rarely needed and partly dangerous (link settings, I/O allocation); reading them all would flood the regular poll | Rarely, by an installer; off by default |

## Main device: HRDS+

The operating surface. It has three groups, which Home Assistant shows as
three sections of the device page.

### Operational

No entity category: these are the entities for dashboards and automations.
Climate and fan are composite (not one register each); the rest are single
registers or values computed from them.

#### Climate

| Entity | Name | What it shows / does |
|---|---|---|
| `climate.hrds_climate` | Climate | HVAC mode (Off, Standby or Auto⁴, Dry, Cool in summer, Heat in winter if enabled) and action; no fan mode, since the unit takes no fan-speed request over Modbus (see the fan below). The mode says what can make the unit act. **Off** is the unit off: it clears the dehumidify and integration requests and switches the unit off. **Standby** (HA's *fan only*) is a unit that is on with nothing requested and no display or room probe, so nothing can start it by itself; action *Idle*, or *Fan* if the unit runs its fan with nothing requested. **Auto** turns the unit on with no request, so it regulates on its own setpoints; with a display or room probe that is what "on, nothing requested" means, so Standby is not offered then. *Turn on* clears both requests and switches the unit on (Standby, or Auto where offered); *turn off* is Off. **Cool**/**Heat** are offered only on a unit with the integration function ([PG02](references/MODBUS_REGISTERS.md#pg02)), and an INT request that cannot act (brine in winter, no integration function) does not show as Cool/Heat; a winter INT from elsewhere shows as Heat whatever *Allow winter heating* says. The action reports what the unit does: *Cooling* needs a summer INT the unit acts on with the compressor running and no AL03; *Heating* needs the evidence described in [Operating modes in winter](../README.md#operating-modes-in-winter). Target T¹ / RH² only when a display or room probe is configured. `current_temperature`¹ and `current_humidity`² are suppressed when the corresponding probe is absent. Target-humidity bounds follow the unit's own [PH29](references/MODBUS_REGISTERS.md#ph29)/[PH30](references/MODBUS_REGISTERS.md#ph30) clamps; the target temperature is [SEtC](references/MODBUS_REGISTERS.md#setc) in summer (15–35 °C) and [SEtH](references/MODBUS_REGISTERS.md#seth) in winter, limited to the unit's [PH09](references/MODBUS_REGISTERS.md#ph09)–[PH10](references/MODBUS_REGISTERS.md#ph10) clamp (factory 14 °C both). |

⁴ Only offered when a display or a room probe lets the unit raise requests by
itself (handbook §6.1), and while that reading is healthy. Not tested on a real
device (see the [release notice](../README.md#release-095)).

#### Fan

The fan is shown by readings only, with no fan entity: Modbus can neither
switch the unit's fan nor set its speed (ADR-0034). The unit runs the fan with
every dehumidify or integration request and stops it after a run-on. What the
fan does is shown by `binary_sensor.supply_fan_running`,
`sensor.supply_fan_status`, `sensor.supply_fan_output`,
`sensor.fan_manual_speed`, `sensor.supply_fan_rpm` and
`sensor.supply_fan_airflow`; the speed bands are the `number.fan_*` entities
under *Configuration*. How the fan is driven and what the bands do:
[Fan speed](../README.md#fan-speed) and
[UNIT_BEHAVIOUR §9](references/UNIT_BEHAVIOUR.md#9-fan). `R` units only: a
non-R unit has no fan of its own, its damper output reads *disabled*, and the
fan sensors and fan speed numbers are not created.

#### Request switches

| Entity | Name | Register | Notes |
|---|---|---|---|
| `switch.unit_on_off` | Unit on/off (Modbus) | [1105](references/MODBUS_REGISTERS.md#reg-1105) | BMS on/off request (requires [PH02](references/MODBUS_REGISTERS.md#ph02) = 1) |
| `switch.dehumidify` | Dehumidify (Modbus) | [1140](references/MODBUS_REGISTERS.md#reg-1140) | BMS dehumidify request (requires [PH28](references/MODBUS_REGISTERS.md#ph28) = 1). In winter on a brine circuit only with a passing brine temperature guard |
| `switch.integration_request` | Integration request (cool in summer, heat in winter) | [1139](references/MODBUS_REGISTERS.md#reg-1139) | **Integration request** (requires [PH27](references/MODBUS_REGISTERS.md#ph27) = 1): dehumidify + cool in summer, **heat in winter**. Refused while not in summer unless winter heating is enabled in the options; always refused in winter on a brine circuit |

#### Season

| Entity | Name | Register | Options | Notes |
|---|---|---|---|---|
| `select.season` | Season | [1825](references/MODBUS_REGISTERS.md#reg-1825) | Summer, Winter | [HB04](references/MODBUS_REGISTERS.md#hb04) — the season switch without a display (the Modbus manual's method: it flips how the open DI4 contact is read). Read-back is `sensor.operating_mode`. Switching to winter is refused while an integration request is on (it would turn into heating) and, on brine, while dehumidify is on. **If a contact is wired to DI4, closing it inverts the meaning.** |

#### Sensors

| Entity | Name | Unit | Probe needed | Notes |
|---|---|---|---|---|
| `sensor.room_temperature` | Room temperature | °C | ¹ Display or external NTC | Reg [499](references/MODBUS_REGISTERS.md#reg-499); used for automatic cooling trigger |
| `sensor.room_humidity` | Room humidity | %RH | ² Display or external humidity sensor | Reg [505](references/MODBUS_REGISTERS.md#reg-505); used for automatic dehumidify trigger |
| `sensor.outdoor_temperature` | Outdoor temperature | °C | External NTC (IP65) | Reg [500](references/MODBUS_REGISTERS.md#reg-500); only drives Free-Cooling/Heating ([PG03](references/MODBUS_REGISTERS.md#pg03)). Display-only otherwise. |
| `sensor.water_temperature` | Water temperature | °C | ³ Built-in | Reg [501](references/MODBUS_REGISTERS.md#reg-501); over-temperature protection |
| `sensor.supply_temperature` | Supply air temperature | °C | External NTC | Reg [503](references/MODBUS_REGISTERS.md#reg-503); monitoring only |
| `sensor.air_quality` | Air quality | ppm | External IAQ sensor | Reg [506](references/MODBUS_REGISTERS.md#reg-506); monitoring only |
| `sensor.actual_setpoint` | Active setpoint | °C | — | Reg [1111](references/MODBUS_REGISTERS.md#reg-1111); active room setpoint in use |
| `sensor.supply_fan_output` | Supply fan output | % | ³ Built-in | Reg [639](references/MODBUS_REGISTERS.md#reg-639) (×0.01 %); actual fan analog output |
| `sensor.fan_manual_speed` | Manual fan speed | % | ³ Built-in | Reg [1614](references/MODBUS_REGISTERS.md#reg-1614), [PM20](references/MODBUS_REGISTERS.md#pm20): the unit's own manual fan request, read-only. The unit sets it to the band minimum ([PF28](references/MODBUS_REGISTERS.md#pf28)) when the fan starts, up to a raised minimum during a run (T25) and to 0 when a request ends (T22); the fan is driven at it. Reads the same as `sensor.fan_manual_request` ([1114](references/MODBUS_REGISTERS.md#reg-1114)) |
| `sensor.compressor_output` | Compressor output | % | ³ Built-in | Reg [641](references/MODBUS_REGISTERS.md#reg-641) (×0.01 %); compressor modulation level |
| `sensor.supply_fan_rpm` | Supply fan speed | rpm | ³ Built-in | Reg [1117](references/MODBUS_REGISTERS.md#reg-1117). **Unknown** when no input is allocated to the fan tachometer (input function 45/46 on [HA01](references/MODBUS_REGISTERS.md#ha01), [HA04](references/MODBUS_REGISTERS.md#ha04)–[HA18](references/MODBUS_REGISTERS.md#ha18), [HB01](references/MODBUS_REGISTERS.md#hb01), [HB02](references/MODBUS_REGISTERS.md#hb02), [HB05](references/MODBUS_REGISTERS.md#hb05)–[HB07](references/MODBUS_REGISTERS.md#hb07), read at setup): the unit then has no speed to report and the register reads 0 with the fan running |
| `sensor.exhaust_temperature` | Exhaust air temperature | °C | External NTC | Reg [502](references/MODBUS_REGISTERS.md#reg-502); monitoring only |
| `sensor.evaporator_temperature` | Evaporator temperature | °C | ³ Built-in | Reg [511](references/MODBUS_REGISTERS.md#reg-511); drives compressor modulation, works on a headless unit |
| `sensor.recirculation_damper` | Recirculation damper | enum | ³ Built-in | Reg [1134](references/MODBUS_REGISTERS.md#reg-1134); Off/On/Disabled, the state of the motorised recirculation damper (R-variant only). *On* confirms room air is being recirculated across the coil; *Disabled* means no damper is wired (non-`R`) |
| `sensor.mode_status` | Mode status | enum | ³ Built-in | Reg [1110](references/MODBUS_REGISTERS.md#reg-1110); Summer/Winter × manual/auto/DI |
| `sensor.supply_fan_status` | Supply fan status | enum | ³ Built-in | Reg [1119](references/MODBUS_REGISTERS.md#reg-1119); Off/Starting/On/Stopping/Alarm |
| `sensor.compressor_status` | Compressor status | enum | ³ Built-in | Reg [1122](references/MODBUS_REGISTERS.md#reg-1122); Off/Wait/On/Alarm/Manual |
| `sensor.operating_mode` | Operating mode (season) | enum | ³ Built-in | Reg [1583](references/MODBUS_REGISTERS.md#reg-1583); Summer/Winter/Auto season |
| `sensor.supply_fan_airflow` | Supply fan airflow | m³/h | ³ Built-in | Computed from live fan output %; see [Airflow sensors](../README.md#airflow-sensors) |

#### Binary sensors

Alarm sensors map to a single bit of a packed alarm register
([MODBUS_REGISTERS.md §9.1](references/MODBUS_REGISTERS.md#91-active-alarm-bitmaps-ro-fc-04)). **ON = alarm is active.**

| Entity | Name | Probe needed | What ON means |
|---|---|---|---|
| `binary_sensor.dehumidify_request` | Dehumidify requested | ³ | Reg [1121](references/MODBUS_REGISTERS.md#reg-1121); Dehumidification currently requested |
| `binary_sensor.recirculation_active` | Recirculation active | ³ | (not a register) Damper ([1134](references/MODBUS_REGISTERS.md#reg-1134)) open **and** supply fan status *On* ([1119](references/MODBUS_REGISTERS.md#reg-1119)): room air is drawn across the coil. Off while the fan is still starting or runs on after the damper closed. R variant only |
| `binary_sensor.supply_fan_running` | Supply fan running | ³ | (not a register) The fan turns: supply fan status ([1119](references/MODBUS_REGISTERS.md#reg-1119)) *On* or *Stopping* (the run-on at [PF26](references/MODBUS_REGISTERS.md#pf26), T19). Off while *Starting* (the [PS01](references/MODBUS_REGISTERS.md#ps01) delay before the fan starts), off and in alarm; unknown when the status is unknown. The only on/off of the fan; Home Assistant cannot switch it. R variant only |
| `binary_sensor.alarm_active` | Alarm active | ³ | Reg [1103](references/MODBUS_REGISTERS.md#reg-1103); At least one alarm is active |
| `binary_sensor.alarm_compressor_lowpressure` | Alarm: compressor low-pressure / frost | ³ | AL11, reg [768](references/MODBUS_REGISTERS.md#reg-768) bit 10: Compressor stopped (low pressure / frost thermostat) |
| `binary_sensor.alarm_compressor_highpressure` | Alarm: compressor high-pressure | ³ | AL12, reg [768](references/MODBUS_REGISTERS.md#reg-768) bit 11: Compressor stopped (high pressure switch) |
| `binary_sensor.alarm_high_water_temperature` | Alarm: high water temperature (AL03) | ³ | AL03, reg [768](references/MODBUS_REGISTERS.md#reg-768) bit 2: Summer: water above [PC07](references/MODBUS_REGISTERS.md#pc07); cooling (and dehumidify unless [PU03](references/MODBUS_REGISTERS.md#pu03)) blocked |
| `binary_sensor.alarm_low_water_temperature` | Alarm: low water temperature (AL04) | ³ | AL04, reg [768](references/MODBUS_REGISTERS.md#reg-768) bit 3: Winter: water below [PC08](references/MODBUS_REGISTERS.md#pc08); heating blocked |
| `binary_sensor.alarm_water_antifreeze` | Alarm: water antifreeze | ³ | AL16, reg [768](references/MODBUS_REGISTERS.md#reg-768) bit 15: Fan stopped (antifreeze protection) |
| `binary_sensor.alarm_dirty_filter` | Alarm: dirty filter | ³ | AL22, reg [769](references/MODBUS_REGISTERS.md#reg-769) bit 5: Maintenance reminder; display only, manual reset |
| `binary_sensor.automatic_heating` | Unit heats on its own | — | (not a register) Only with a room temperature source and the integration function: ON = the unit, on in winter, can heat by itself below [SEtH](references/MODBUS_REGISTERS.md#seth) − [PF12](references/MODBUS_REGISTERS.md#pf12); attributes give the band and whether it heats now. See [The unit heats on its own](../README.md#the-unit-heats-on-its-own) |
| `binary_sensor.brine_temperature_guard` | Brine temperature guard | — | (not a register) Only with a [brine temperature guard](../README.md#brine-temperature-guard) configured: ON = the guard refuses to start requests (brine too cold, sensor stale or unavailable) |

### Configuration

Entity category *Configuration*. Why it is its own group: post-setup tuning that
is set once or occasionally and then left alone, so it stays off dashboards but
close to the operating entities. Setpoints are only created when a display or
probe lets the unit act on them (ADR-0011).

#### Numbers

| Entity | Name | Register | Range | Notes |
|---|---|---|---|---|
| `number.humidity_setpoint` | Humidity setpoint | [1586](references/MODBUS_REGISTERS.md#reg-1586) | 0–100 %RH | [PU01](references/MODBUS_REGISTERS.md#pu01); target humidity for automatic dehumidify. **Not created without a display or humidity probe** |
| `number.summer_setpoint` | Summer setpoint | [1584](references/MODBUS_REGISTERS.md#reg-1584) | 15–35 °C | [SEtC](references/MODBUS_REGISTERS.md#setc); target room temp for automatic summer integration, clamped by [PH07](references/MODBUS_REGISTERS.md#ph07)/[PH08](references/MODBUS_REGISTERS.md#ph08). **Not created without a display or room temperature probe** |
| `number.winter_setpoint` | Winter setpoint | [1585](references/MODBUS_REGISTERS.md#reg-1585) | 5–35 °C | [SEtH](references/MODBUS_REGISTERS.md#seth); target room temp for automatic winter heating: the unit heats by itself below [SEtH](references/MODBUS_REGISTERS.md#seth) − [PF12](references/MODBUS_REGISTERS.md#pf12) (see [The unit heats on its own](../README.md#the-unit-heats-on-its-own)). Clamped by the unit to [PH09](references/MODBUS_REGISTERS.md#ph09)–[PH10](references/MODBUS_REGISTERS.md#ph10) (factory 14 °C both). **Not created without a display or room temperature probe** |
| `number.fan_min_speed_dehumidify` | Fan min speed (dehumidify) | [1853](references/MODBUS_REGISTERS.md#reg-1853) | 0–100 % | [PF28](references/MODBUS_REGISTERS.md#pf28); lower fan bound in dehumidify mode, and the fan's start speed. The only way to change the speed over Modbus: raising it above the running speed raises the fan; lowering it does not slow a running fan (T24–T26). EEPROM parameter: set it when needed, not per cycle (ADR-0023) |
| `number.fan_max_speed_dehumidify` | Fan max speed (dehumidify) | [1647](references/MODBUS_REGISTERS.md#reg-1647) | 0–100 % | [PF10](references/MODBUS_REGISTERS.md#pf10); upper fan bound in dehumidify mode |
| `number.fan_min_speed_cooling` | Fan min speed (cooling) | [1852](references/MODBUS_REGISTERS.md#reg-1852) | 0–100 % | [PF27](references/MODBUS_REGISTERS.md#pf27); lower fan bound in active cooling |
| `number.fan_min_speed_vmc` | Fan min speed (VMC) | [1644](references/MODBUS_REGISTERS.md#reg-1644) | 0–100 % | [PF07](references/MODBUS_REGISTERS.md#pf07); lower fan bound in VMC (ventilation-only) mode |
| `number.fan_max_speed_cooling` | Fan max speed (cooling) | [1646](references/MODBUS_REGISTERS.md#reg-1646) | 0–100 % | [PF09](references/MODBUS_REGISTERS.md#pf09); upper fan bound in active cooling |
| `number.dehumidify_differential` | Dehumidify differential | [1694](references/MODBUS_REGISTERS.md#reg-1694) | 0–100 %RH | [PU07](references/MODBUS_REGISTERS.md#pu07); the unit's own dehumidify hysteresis. Not created without a display or humidity probe |
| `number.min_room_temp_dehumidify` | Min room temp for dehumidify | [1889](references/MODBUS_REGISTERS.md#reg-1889) | 0–30 °C | [PU13](references/MODBUS_REGISTERS.md#pu13); **below this the unit refuses to dehumidify, including over Modbus** |
| `number.min_room_temp_diff_dehumidify` | Min room temp differential | [1890](references/MODBUS_REGISTERS.md#reg-1890) | 0.1–20 °C | [PU14](references/MODBUS_REGISTERS.md#pu14); re-enable differential above [PU13](references/MODBUS_REGISTERS.md#pu13) |
| `number.fan_min_runtime` | Fan minimum runtime | [1638](references/MODBUS_REGISTERS.md#reg-1638) | 0–999 s | [PF01](references/MODBUS_REGISTERS.md#pf01); device-side minimum fan runtime |
| `number.fan_post_run_time` | Fan post-run time | [1640](references/MODBUS_REGISTERS.md#reg-1640) | 0–999 s | [PF03](references/MODBUS_REGISTERS.md#pf03); post-ventilation run-on |
| `number.humidity_setpoint_min` | Humidity setpoint minimum | [1892](references/MODBUS_REGISTERS.md#reg-1892) | 0–100 %RH | [PH29](references/MODBUS_REGISTERS.md#ph29); lower clamp on target humidity |
| `number.humidity_setpoint_max` | Humidity setpoint maximum | [1893](references/MODBUS_REGISTERS.md#reg-1893) | 0–100 %RH | [PH30](references/MODBUS_REGISTERS.md#ph30); upper clamp on target humidity |

#### Select

| Entity | Name | Register | Options | Notes |
|---|---|---|---|---|
| `select.winter_dehumidify` | Winter dehumidification | [1689](references/MODBUS_REGISTERS.md#reg-1689) | Disabled, With water, Without water | [PU02](references/MODBUS_REGISTERS.md#pu02); dehumidification during the heating season |

#### Switches

| Entity | Name | Register | Notes |
|---|---|---|---|
| `switch.force_dehumidify_in_cooling` | Force dehumidify when cooling | [1692](references/MODBUS_REGISTERS.md#reg-1692) | [PU05](references/MODBUS_REGISTERS.md#pu05) (factory on); an INT request also starts the compressor. Off: INT cools only with the water, see [Operating modes in summer](../README.md#operating-modes-in-summer) |

### Diagnostic

Entity category *Diagnostic*. Why it is its own group: read-only values for
troubleshooting (the water circuit, the display's own fan request, the airflow
calibration). The unit drives its water circuit itself; the integration only
shows it.

#### Sensors

| Entity | Name | Unit | Probe needed | Notes |
|---|---|---|---|---|
| `sensor.fan_manual_request` | Manual fan request (display) | % | ³ Built-in | Reg [1114](references/MODBUS_REGISTERS.md#reg-1114); the **display's** manual request, not ours — diagnostic. Without a display it reads the band minimum while the fan runs |
| `sensor.fan_integration_request` | Fan integration request | % | ³ Built-in | Reg [1112](references/MODBUS_REGISTERS.md#reg-1112) (`FanIntegration_Request`, ×0.01 %); the fan request of the integration (INT) fan control, one of the requests the unit's fan speed is the highest of ([UNIT_BEHAVIOUR §9.1](references/UNIT_BEHAVIOUR.md#91-bands-and-sources)). 0 during dehumidify; a non-zero value during INT is not yet seen on hardware. R variant only |
| `sensor.water_valve_pump` | Water valve / pump output | enum | ³ Built-in | Diagnostic. Reg [1126](references/MODBUS_REGISTERS.md#reg-1126); relay K5 — external water valve (V3V) and the pump output (PM) switched with it: Off / On / Not configured |
| `sensor.water_condenser_valve` | Water condenser valve | enum | ³ Built-in | Diagnostic. Reg [1124](references/MODBUS_REGISTERS.md#reg-1124); relay K4, the internal valve. A real unit reads On in standby, against the handbook's description, so its meaning is unverified ([UNIT_BEHAVIOUR §11.1](references/UNIT_BEHAVIOUR.md#111-internal-valve-relay-k4)); the climate action does not use it |
| `sensor.water_check` | Water circuit check | enum | — | Diagnostic. `ok` / `attention`; attribute `issues`, see [Water circuit](../README.md#water-circuit-and-brine) |
| `sensor.supply_fan_max_airflow` | Supply fan max airflow | m³/h | — | Computed constant; maximum fan airflow (from config) |
| `sensor.max_total_airflow` | Max total airflow | m³/h | — | Computed constant; same as supply_fan_max_airflow (from config) |

## Setup device: HRDS+ setup

**Why it exists.** A headless unit needs a dozen settings reviewed before it is
safe to operate: display priority, probes, the Modbus enables, time programs,
the remote contact. A plain entity list buried them, so they are one checklist
on their own device (ADR-0016). **Why it is separate:** the main device stays an
operating surface, and nothing here is touched day to day. The enables are yours
to set and the integration never writes them (ADR-0022); *Allow operational
requests* is the integration's own gate (ADR-0012). The **Setup check** sensor
lists what is left to fix; the
[first-use checklist](../README.md#first-use-checklist) walks through it.
Entity ids carry the device name, for example `sensor.hrds_setup_setup_check`.

#### Sensors

| Entity | Name | Register | Shows |
|---|---|---|---|
| `sensor.unit_status` | Unit status | [1104](references/MODBUS_REGISTERS.md#reg-1104) | OFF by display/DI/BMS/scheduler/clock, or ON |
| `sensor.machine_type` | Machine type ([PG01](references/MODBUS_REGISTERS.md#pg01)) | [1797](references/MODBUS_REGISTERS.md#reg-1797) | [PG01](references/MODBUS_REGISTERS.md#pg01) fan arrangement: *supply fan only* or *supply and exhaust fan*. **Not** a recirculation flag: an `R` unit reads *supply fan only*. |
| `sensor.setup_check` | Setup check | — | `ok` / `attention`; attribute `issues` lists the open items |
| `sensor.remote_onoff_input` | Remote on/off input ([HB03](references/MODBUS_REGISTERS.md#hb03)) | [1824](references/MODBUS_REGISTERS.md#reg-1824) | [HB03](references/MODBUS_REGISTERS.md#hb03) — unused / normally closed / normally open |
| `sensor.season_owner` | Season change owner ([PC11](references/MODBUS_REGISTERS.md#pc11)) | [1878](references/MODBUS_REGISTERS.md#reg-1878) | [PC11](references/MODBUS_REGISTERS.md#pc11) — who owns the season change when a display is connected |
| `sensor.temperature_unit` | Temperature unit ([PH05](references/MODBUS_REGISTERS.md#ph05)) | [1781](references/MODBUS_REGISTERS.md#reg-1781) | [PH05](references/MODBUS_REGISTERS.md#ph05) — Celsius or Fahrenheit |
| `sensor.fan_output_allocation` | Supply fan output allocation ([HC04](references/MODBUS_REGISTERS.md#hc04)) | [1832](references/MODBUS_REGISTERS.md#reg-1832) | [HC04](references/MODBUS_REGISTERS.md#hc04) — raw allocation of the supply fan output |
| `sensor.damper_relay_allocation` | Recirculation damper relay allocation ([HD01](references/MODBUS_REGISTERS.md#hd01)) | [1838](references/MODBUS_REGISTERS.md#reg-1838) | [HD01](references/MODBUS_REGISTERS.md#hd01) — raw allocation of relay DO1 (10 = recirculation damper NO, 9 = NC) |
| `sensor.damper_prestart_time` | Damper pre-start time ([PS01](references/MODBUS_REGISTERS.md#ps01)) | [1698](references/MODBUS_REGISTERS.md#reg-1698) | [PS01](references/MODBUS_REGISTERS.md#ps01) — damper pre-start time, seconds |

#### Binary sensors

| Entity | Name | Register | Shows |
|---|---|---|---|
| `binary_sensor.temp_probe_ok` | Room temperature probe OK | [769](references/MODBUS_REGISTERS.md#reg-769) bit 11 | Room temperature probe healthy (AL28 not active). **Unknown** without a display or a room temperature probe on AI2 ([HA02](references/MODBUS_REGISTERS.md#ha02)): there is nothing to check |
| `binary_sensor.humidity_probe_ok` | Room humidity probe OK | [770](references/MODBUS_REGISTERS.md#reg-770) bit 1 | Room humidity probe healthy (AL34 not active). **Unknown** without a display or a humidity probe on AI3 ([HA03](references/MODBUS_REGISTERS.md#ha03)) |
| `binary_sensor.integration_available` | Unit has integration function ([PG02](references/MODBUS_REGISTERS.md#pg02)) | [1798](references/MODBUS_REGISTERS.md#reg-1798) | ON: the unit has the integration (INT) function ([PG02](references/MODBUS_REGISTERS.md#pg02) = 1). Read-only: an installer setting, not a Modbus permission |
| `binary_sensor.remote_contact_closed` | Remote on/off contact closed | [257](references/MODBUS_REGISTERS.md#reg-257) bit 0 | State of the remote on/off contact (meaning inferred, unverified) |

#### Switches

| Entity | Name | Register | Shows |
|---|---|---|---|
| `switch.operation_allowed` | Allow operational requests | — | Not a register: the integration's own gate. Off by default; while off, on/dehumidify/cooling/non-zero fan requests are refused. Restored across restarts |
| `switch.enable_time_programs` | Time programs enabled ([PH03](references/MODBUS_REGISTERS.md#ph03)) | [1779](references/MODBUS_REGISTERS.md#reg-1779) | [PH03](references/MODBUS_REGISTERS.md#ph03) — time programs can switch the unit off |
| `switch.enable_onoff_by_di_request` | Unit on by DI request ([PC12](references/MODBUS_REGISTERS.md#pc12)) | [1894](references/MODBUS_REGISTERS.md#reg-1894) | [PC12](references/MODBUS_REGISTERS.md#pc12) — DI requests start the unit despite an open OFF contact |
| `switch.enable_onoff_display` | Enable on/off via display ([PH01](references/MODBUS_REGISTERS.md#ph01)) | [1777](references/MODBUS_REGISTERS.md#reg-1777) | [PH01](references/MODBUS_REGISTERS.md#ph01) — on/off by wired display. Forced **off** while `has_display` is off (the default); turning it on by hand is undone on the next poll |
| `switch.enable_onoff_bms` | Enable on/off via Modbus ([PH02](references/MODBUS_REGISTERS.md#ph02)) | [1778](references/MODBUS_REGISTERS.md#reg-1778) | [PH02](references/MODBUS_REGISTERS.md#ph02) — lets Home Assistant switch the unit on and off. Yours to set; the integration never writes it ([step 4](../README.md#4-choose-what-home-assistant-may-control)) |
| `switch.enable_dehumidify_bms` | Enable dehumidify (DEU) via Modbus ([PH28](references/MODBUS_REGISTERS.md#ph28)) | [1870](references/MODBUS_REGISTERS.md#reg-1870) | [PH28](references/MODBUS_REGISTERS.md#ph28) — lets Home Assistant request dehumidifying (DEU). Yours to set |
| `switch.enable_integration_bms` | Enable integration (INT) via Modbus ([PH27](references/MODBUS_REGISTERS.md#ph27)) | [1869](references/MODBUS_REGISTERS.md#reg-1869) | [PH27](references/MODBUS_REGISTERS.md#ph27) — lets Home Assistant request integration (INT: cool in summer, heat in winter). Yours to set |
| `switch.enable_free_cooling` | Enable free cooling/heating | [1799](references/MODBUS_REGISTERS.md#reg-1799) | [PG03](references/MODBUS_REGISTERS.md#pg03); while off, outdoor temperature drives nothing |

#### Select

| Entity | Name | Register | Shows |
|---|---|---|---|
| `select.probe_source` | T/H probe source ([HA00](references/MODBUS_REGISTERS.md#ha00)) | [1803](references/MODBUS_REGISTERS.md#reg-1803) | [HA00](references/MODBUS_REGISTERS.md#ha00) — which sensor feeds room T/H readings. **Set to "None / external probes" when running without a display.** Options: None/external, CNU2 T, CNU2 T+H, CNU T, CNU T+H, EPJ T, EPJ T+H. |
| `select.ai2_allocation` | T/H probe temperature input (AI2, [HA02](references/MODBUS_REGISTERS.md#ha02)) | [1805](references/MODBUS_REGISTERS.md#reg-1805) | [HA02](references/MODBUS_REGISTERS.md#ha02), *T/H probe temperature input*: what is wired to analog input AI2 (terminal M2). Without a display, this is the only room temperature the unit can regulate on. **Leave on "Unused" unless a probe is wired**, or the unit raises AL28. Options: Unused, Room temperature probe (NTC 10 kΩ). |
| `select.ai3_allocation` | T/H probe humidity input (AI3, [HA03](references/MODBUS_REGISTERS.md#ha03)) | [1806](references/MODBUS_REGISTERS.md#reg-1806) | [HA03](references/MODBUS_REGISTERS.md#ha03), *T/H probe humidity input*: the same for AI3 (terminal M3) and a humidity probe; with nothing wired it raises AL34. A code other than these shows as unknown and the setup check reports `probe_input_unrecognised`. Options: Unused, Room humidity probe (4–20 mA), Room humidity probe (0–10 V). |

## Installer device: HRDS+ installer

**Why it exists.** The handbook's installer menu (§5.3) has about 240
parameters with a Modbus address. They are not needed for setup or normal use.
**Why it is separate and opt-in:** a few of them cut the connection or are
destructive, and reading them all makes the poll too heavy for the real unit, so the device is **off by default** and its registers are
never part of the regular poll (ADR-0017). Turn on *Installer device* in the
integration options (Settings → Devices & services → HRDS+ → Configure); turning
it off again removes the device and its entities. Entity ids carry the parameter
code, for example `number.hrds_installer_pc07_max_water_temperature...`.

The parameters are read when the option is turned on, at each start of the
integration, and when you press **Refresh installer parameters**; after you
change one, just that register is read back. ([PC07](references/MODBUS_REGISTERS.md#pc07), [PC08](references/MODBUS_REGISTERS.md#pc08), [PU08](references/MODBUS_REGISTERS.md#pu08), [PF12](references/MODBUS_REGISTERS.md#pf12), [PH09](references/MODBUS_REGISTERS.md#ph09) and
[PH10](references/MODBUS_REGISTERS.md#ph10), which the water check and the heating logic use, are read once at start
even without the installer device.)

The parameters are **not listed one by one** here: they are generated from
`installer_params.py`, and the full list with addresses and scaling is
[`references/MODBUS_REGISTERS.md` §16](references/MODBUS_REGISTERS.md#16-installer-menu-parameters-installer-device). The two
entities that are not parameters:

| Entity | Name | Register | Shows |
|---|---|---|---|
| `button.refresh_installer` | Refresh installer parameters | — | Reads every installer register once |
| `sensor.installer_last_read` | Installer parameters last read | — | Timestamp of the last read |

* Writable parameters are under *Configuration*: fans (PF), compressor (PE),
  water valves (Pb), dehumidification (PU), alarms (PA), season change (PC),
  setpoint limits ([PH07](references/MODBUS_REGISTERS.md#ph07)–[PH10](references/MODBUS_REGISTERS.md#ph10)), probe offsets (PM8x) and hour counters ([PM00](references/MODBUS_REGISTERS.md#pm00)–[PM04](references/MODBUS_REGISTERS.md#pm04)).
* Read-only, under *Diagnostic*: the Modbus/CAN link ([PH11](references/MODBUS_REGISTERS.md#ph11)–[PH17](references/MODBUS_REGISTERS.md#ph17); changing them
  would cut the connection), the I/O allocation (HA, HB, HC, HD; manufacturer
  level), refrigerant and pressure-probe ranges, the compressor safety-time
  bypass ([PE05](references/MODBUS_REGISTERS.md#pe05)), forced compressor ([PM21](references/MODBUS_REGISTERS.md#pm21)) and test mode (PT).
* Parameters the HRDS+ does not use (return fan, air quality, heat-recovery
  defrost, external damper, rotary exchanger, expansion I/O) exist but are
  **disabled by default**; enable them in the entity settings if needed.
* Never exposed: passwords, PH15 *restore factory defaults*, PH18 *clear alarm
  history*.
