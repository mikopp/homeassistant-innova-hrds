# Entity reference

The entities the integration provides, by device and then by platform, as on
the integration pages of [home-assistant.io](https://www.home-assistant.io/integrations/).
It is in English only. Back to the [README](../README.md).

Entity names start with the name you gave the unit when adding the
integration (*HRDS+* by default), so *Dehumidify (Modbus)* shows as
*HRDS+ Dehumidify (Modbus)*. The setup and installer devices add *setup* and
*installer* to that name.

Each entity has a short description, the units it is available for (if not
all) and remarks: the Modbus register it reads or writes (see the
[register reference](references/MODBUS_REGISTERS.md)) and, for a setting that
Home Assistant keeps in its own section of the device page, *Configuration
entity*. Read-only values for troubleshooting are listed under *Diagnostic*.

## Devices

A unit shows up as three linked devices. They exist because the entities have
three different audiences and three different risks:

| Device | Holds | Why it is separate | You use it |
|---|---|---|---|
| **HRDS+** | Operating the unit, the tuning that belongs to it, and diagnostics | The page a household looks at. It is for operating and watching the unit; no one-off installation task is on it | Daily; configuration entities occasionally; the *Diagnostic* section when troubleshooting |
| **HRDS+ setup** (linked to HRDS+) | What decides whether the unit can run at all: the setup check, the operation gate, the Modbus enables, probe and wiring facts | A checklist, not a control surface. Keeping it off the main page leaves the operating surface clean, and these are the settings that put a unit into "off by display" when wrong | Once after installing, again when the wiring changes |
| **HRDS+ installer** (linked to HRDS+, **opt-in**) | The installer menu of the handbook (§5.3), about 240 parameters | Rarely needed and partly dangerous (link settings, I/O allocation); reading them all would make the regular poll too heavy | Rarely, by an installer; off by default |

## HRDS+

The operating surface: climate, requests, readings and alarms, plus the
configuration and diagnostic entities that belong to operating the unit.

### Binary sensors

- **Dehumidify requested**: On while the unit has a dehumidify request, from any source.
  - **Remarks**: Register [1121](references/MODBUS_REGISTERS.md#reg-1121).
- **Recirculation active**: On while the recirculation damper is open **and** the fan status is *On*: room air is drawn across the coil. Off while the fan is still starting or runs on after the damper closed.
  - **Available for**: `R` units.
  - **Remarks**: Derived from registers [1134](references/MODBUS_REGISTERS.md#reg-1134) and [1119](references/MODBUS_REGISTERS.md#reg-1119).
- **Supply fan running**: On while the fan turns: *Supply fan status* is *On* or *Stopping* (the run-on at [PF26](references/MODBUS_REGISTERS.md#pf26)). Off while *Starting* (the [PS01](references/MODBUS_REGISTERS.md#ps01) delay before the fan starts), off and in alarm; unknown when the status is unknown. Home Assistant cannot switch the fan.
  - **Available for**: `R` units.
  - **Remarks**: Derived from register [1119](references/MODBUS_REGISTERS.md#reg-1119).
- **Alarm active**: On while at least one alarm is active.
  - **Remarks**: Register [1103](references/MODBUS_REGISTERS.md#reg-1103).
- **Alarm: compressor low-pressure / frost**: AL11, on while the compressor is stopped by the low-pressure switch or the frost thermostat.
  - **Remarks**: Register [768](references/MODBUS_REGISTERS.md#reg-768), bit 10.
- **Alarm: compressor high-pressure**: AL12, on while the compressor is stopped by the high-pressure switch.
  - **Remarks**: Register [768](references/MODBUS_REGISTERS.md#reg-768), bit 11.
- **Alarm: high water temperature (AL03)**: Summer: the water is above [PC07](references/MODBUS_REGISTERS.md#pc07); cooling (and dehumidifying unless [PU03](references/MODBUS_REGISTERS.md#pu03)) is blocked.
  - **Remarks**: Register [768](references/MODBUS_REGISTERS.md#reg-768), bit 2.
- **Alarm: low water temperature (AL04)**: Winter: the water is below [PC08](references/MODBUS_REGISTERS.md#pc08); heating is blocked.
  - **Remarks**: Register [768](references/MODBUS_REGISTERS.md#reg-768), bit 3.
- **Alarm: water antifreeze**: AL16, on while the fan is stopped by the antifreeze protection.
  - **Remarks**: Register [768](references/MODBUS_REGISTERS.md#reg-768), bit 15.
- **Alarm: dirty filter**: AL22, a maintenance reminder; the unit keeps running. Reset at the unit.
  - **Remarks**: Register [769](references/MODBUS_REGISTERS.md#reg-769), bit 5.
- **Unit heats on its own**: On while the unit, switched on in winter, can heat by itself below [SEtH](references/MODBUS_REGISTERS.md#seth) − [PF12](references/MODBUS_REGISTERS.md#pf12). Its attributes give the band and whether it heats now. See [The unit heats on its own](../README.md#the-unit-heats-on-its-own).
  - **Available for**: units with a room temperature source (display or probe) and the integration function.
- **Brine temperature guard**: On while the guard refuses to start requests: the brine is too cold, or the sensor is stale or unavailable.
  - **Available for**: installations with a [brine temperature guard](../README.md#brine-temperature-guard) configured.

### Climate

- **Climate**: Current temperature and humidity, an HVAC mode to pick the operating mode, and the action the unit performs. There is no fan mode: the unit takes no fan-speed request over Modbus.
  - **Off** switches the unit off and clears the dehumidify and integration requests.
  - **Standby** (Home Assistant's *fan only*): the unit is on with nothing requested, and nothing on the unit can start a request by itself. The action is *Idle*, or *Fan* while the fan runs with nothing requested. Offered without a display or room probe.
  - **Auto**: the unit is on with nothing requested and regulates on its own setpoints. Offered instead of Standby with a display or room probe, while that reading is healthy. Not tested on a real unit.
  - **Dry**, **Cool** (summer), **Heat** (winter, when *Allow winter heating* is on): the dehumidify or the integration request. Cool and Heat are offered only on units with the integration function ([PG02](references/MODBUS_REGISTERS.md#pg02)); an integration request that cannot act (brine in winter, no integration function) does not show as Cool or Heat, and one set elsewhere in winter shows as Heat whatever *Allow winter heating* says.
  - *Turn on* switches the unit on with nothing requested (Standby, or Auto where offered); *turn off* is Off.
  - The action is *Cooling* only for a summer integration request the unit acts on with the compressor running and no AL03; *Heating* as in [Operating modes in winter](../README.md#operating-modes-in-winter).
  - **Available for**: all units. Current temperature, target temperature and target humidity only with a display or a room probe.
  - **Remarks**: The target humidity is limited to [PH29](references/MODBUS_REGISTERS.md#ph29)–[PH30](references/MODBUS_REGISTERS.md#ph30). The target temperature is [SEtC](references/MODBUS_REGISTERS.md#setc) in summer (15–35 °C) and [SEtH](references/MODBUS_REGISTERS.md#seth) in winter, limited to [PH09](references/MODBUS_REGISTERS.md#ph09)–[PH10](references/MODBUS_REGISTERS.md#ph10) (factory 14 °C both).

### Numbers

- **Humidity setpoint**: Target humidity for the unit's own dehumidifying, 0–100 %RH ([PU01](references/MODBUS_REGISTERS.md#pu01)).
  - **Available for**: units with a display or a humidity probe.
  - **Remarks**: Register [1586](references/MODBUS_REGISTERS.md#reg-1586). Configuration entity.
- **Summer setpoint**: Target room temperature for the unit's own cooling, 15–35 °C ([SEtC](references/MODBUS_REGISTERS.md#setc)), limited by the unit to [PH07](references/MODBUS_REGISTERS.md#ph07)–[PH08](references/MODBUS_REGISTERS.md#ph08).
  - **Available for**: units with a display or a room temperature probe.
  - **Remarks**: Register [1584](references/MODBUS_REGISTERS.md#reg-1584). Configuration entity.
- **Winter setpoint**: Target room temperature for the unit's own heating, 5–35 °C ([SEtH](references/MODBUS_REGISTERS.md#seth)): the unit heats by itself below [SEtH](references/MODBUS_REGISTERS.md#seth) − [PF12](references/MODBUS_REGISTERS.md#pf12) (see [The unit heats on its own](../README.md#the-unit-heats-on-its-own)). Limited by the unit to [PH09](references/MODBUS_REGISTERS.md#ph09)–[PH10](references/MODBUS_REGISTERS.md#ph10) (factory 14 °C both).
  - **Available for**: units with a display or a room temperature probe.
  - **Remarks**: Register [1585](references/MODBUS_REGISTERS.md#reg-1585). Configuration entity.
- **Fan min speed (dehumidify)**: Lower fan limit while dehumidifying, and the fan's start speed, 0–100 % ([PF28](references/MODBUS_REGISTERS.md#pf28)). The only way to change the speed over Modbus: raising it above the running speed raises the fan; lowering it does not slow a running fan.
  - **Available for**: `R` units.
  - **Remarks**: Register [1853](references/MODBUS_REGISTERS.md#reg-1853). The unit stores each change in a memory that wears with every write, so change it when needed, not from a control loop. Configuration entity.
- **Fan max speed (dehumidify)**: Upper fan limit while dehumidifying, 0–100 % ([PF10](references/MODBUS_REGISTERS.md#pf10)).
  - **Available for**: `R` units.
  - **Remarks**: Register [1647](references/MODBUS_REGISTERS.md#reg-1647). Configuration entity.
- **Fan min speed (cooling)**: Lower fan limit while cooling, 0–100 % ([PF27](references/MODBUS_REGISTERS.md#pf27)).
  - **Available for**: `R` units.
  - **Remarks**: Register [1852](references/MODBUS_REGISTERS.md#reg-1852). Configuration entity.
- **Fan max speed (cooling)**: Upper fan limit while cooling, 0–100 % ([PF09](references/MODBUS_REGISTERS.md#pf09)).
  - **Available for**: `R` units.
  - **Remarks**: Register [1646](references/MODBUS_REGISTERS.md#reg-1646). Configuration entity.
- **Fan min speed (VMC)**: Lower fan limit in ventilation-only (VMC) mode, 0–100 % ([PF07](references/MODBUS_REGISTERS.md#pf07)).
  - **Available for**: `R` units.
  - **Remarks**: Register [1644](references/MODBUS_REGISTERS.md#reg-1644). Configuration entity.
- **Dehumidify differential**: The unit's own dehumidify hysteresis, 0–100 %RH ([PU07](references/MODBUS_REGISTERS.md#pu07)).
  - **Available for**: units with a display or a humidity probe.
  - **Remarks**: Register [1694](references/MODBUS_REGISTERS.md#reg-1694). Configuration entity.
- **Min room temp for dehumidify**: Below this room temperature the unit refuses to dehumidify, **also when Home Assistant asks**, 0–30 °C ([PU13](references/MODBUS_REGISTERS.md#pu13)).
  - **Remarks**: Register [1889](references/MODBUS_REGISTERS.md#reg-1889). Configuration entity.
- **Min room temp differential**: How far above *Min room temp for dehumidify* the unit allows dehumidifying again, 0.1–20 °C ([PU14](references/MODBUS_REGISTERS.md#pu14)).
  - **Remarks**: Register [1890](references/MODBUS_REGISTERS.md#reg-1890). Configuration entity.
- **Fan minimum runtime**: The unit's minimum fan run time, 0–999 s ([PF01](references/MODBUS_REGISTERS.md#pf01)).
  - **Remarks**: Register [1638](references/MODBUS_REGISTERS.md#reg-1638). Configuration entity.
- **Fan post-run time**: How long the fan runs on after a request, 0–999 s ([PF03](references/MODBUS_REGISTERS.md#pf03)).
  - **Remarks**: Register [1640](references/MODBUS_REGISTERS.md#reg-1640). Configuration entity.
- **Humidity setpoint minimum**: Lowest humidity setpoint the unit accepts, 0–100 %RH ([PH29](references/MODBUS_REGISTERS.md#ph29)).
  - **Remarks**: Register [1892](references/MODBUS_REGISTERS.md#reg-1892). Configuration entity.
- **Humidity setpoint maximum**: Highest humidity setpoint the unit accepts, 0–100 %RH ([PH30](references/MODBUS_REGISTERS.md#ph30)).
  - **Remarks**: Register [1893](references/MODBUS_REGISTERS.md#reg-1893). Configuration entity.

### Selects

- **Season**: Summer or winter, for a unit without a display ([HB04](references/MODBUS_REGISTERS.md#hb04), the Modbus manual's method: it flips how the open DI4 contact is read). *Operating mode (season)* shows what the unit uses. Switching to winter is refused while an integration request is on (it would turn into heating) and, on brine, while dehumidifying.
  - **Options**: Summer, Winter.
  - **Remarks**: Register [1825](references/MODBUS_REGISTERS.md#reg-1825). **If a contact is wired to DI4, closing it inverts the meaning.**
- **Winter dehumidification**: Whether and how the unit dehumidifies in the heating season ([PU02](references/MODBUS_REGISTERS.md#pu02)).
  - **Options**: Disabled, With water, Without water.
  - **Remarks**: Register [1689](references/MODBUS_REGISTERS.md#reg-1689). Configuration entity.

### Sensors

- **Room temperature**: Room temperature in °C; the unit's automatic cooling and heating use it.
  - **Available for**: units with a display or a room temperature probe.
  - **Remarks**: Register [499](references/MODBUS_REGISTERS.md#reg-499).
- **Room humidity**: Room humidity in %RH; the unit's automatic dehumidifying uses it.
  - **Available for**: units with a display or a humidity probe.
  - **Remarks**: Register [505](references/MODBUS_REGISTERS.md#reg-505).
- **Outdoor temperature**: Outdoor temperature in °C. The unit only uses it for free cooling and heating ([PG03](references/MODBUS_REGISTERS.md#pg03)).
  - **Available for**: units with an outdoor probe (NTC, IP65).
  - **Remarks**: Register [500](references/MODBUS_REGISTERS.md#reg-500).
- **Water temperature**: Water temperature at the unit in °C; the unit's over- and under-temperature protection uses it.
  - **Remarks**: Register [501](references/MODBUS_REGISTERS.md#reg-501).
- **Supply air temperature**: Supply air temperature in °C, for monitoring.
  - **Available for**: units with a supply air probe (NTC).
  - **Remarks**: Register [503](references/MODBUS_REGISTERS.md#reg-503).
- **Exhaust air temperature**: Exhaust air temperature in °C, for monitoring.
  - **Available for**: units with an exhaust air probe (NTC).
  - **Remarks**: Register [502](references/MODBUS_REGISTERS.md#reg-502).
- **Evaporator temperature**: Evaporator temperature in °C; the unit modulates the compressor on it.
  - **Remarks**: Register [511](references/MODBUS_REGISTERS.md#reg-511).
- **Air quality**: Air quality in ppm, for monitoring.
  - **Available for**: units with an air quality sensor.
  - **Remarks**: Register [506](references/MODBUS_REGISTERS.md#reg-506).
- **Active setpoint**: The room temperature setpoint the unit uses right now, in °C.
  - **Remarks**: Register [1111](references/MODBUS_REGISTERS.md#reg-1111).
- **Supply fan output**: The speed the fan is driven at, in %.
  - **Available for**: `R` units.
  - **Remarks**: Register [639](references/MODBUS_REGISTERS.md#reg-639).
- **Supply fan speed**: Fan speed in rpm. **Unknown** unless an input of the unit is allocated to the fan tachometer (input function 45 or 46 on [HA01](references/MODBUS_REGISTERS.md#ha01), [HA04](references/MODBUS_REGISTERS.md#ha04)–[HA18](references/MODBUS_REGISTERS.md#ha18), [HB01](references/MODBUS_REGISTERS.md#hb01), [HB02](references/MODBUS_REGISTERS.md#hb02), [HB05](references/MODBUS_REGISTERS.md#hb05)–[HB07](references/MODBUS_REGISTERS.md#hb07), read at start); without one the unit reports 0 with the fan running.
  - **Available for**: `R` units.
  - **Remarks**: Register [1117](references/MODBUS_REGISTERS.md#reg-1117).
- **Supply fan status**: The unit's fan status: Off, Starting, On, Stopping or Alarm.
  - **Available for**: `R` units.
  - **Remarks**: Register [1119](references/MODBUS_REGISTERS.md#reg-1119).
- **Manual fan speed**: The unit's own manual fan request in % ([PM20](references/MODBUS_REGISTERS.md#pm20)), read-only. The unit sets it to the band minimum ([PF28](references/MODBUS_REGISTERS.md#pf28)) when the fan starts, up to a raised minimum during a run, and to 0 when a request ends; the fan runs at it. It reads the same as *Manual fan request (display)*.
  - **Available for**: `R` units.
  - **Remarks**: Register [1614](references/MODBUS_REGISTERS.md#reg-1614).
- **Supply fan airflow**: Estimated recirculation airflow in m³/h, from the fan output and the airflow calibration; see [Airflow sensors](../README.md#airflow-sensors).
  - **Available for**: `R` units.
- **Recirculation damper**: The motorised recirculation damper: *On* when room air is recirculated across the coil, *Off*, or *Disabled* when no damper is wired.
  - **Remarks**: Register [1134](references/MODBUS_REGISTERS.md#reg-1134).
- **Compressor output**: Compressor modulation in %.
  - **Remarks**: Register [641](references/MODBUS_REGISTERS.md#reg-641).
- **Compressor status**: The compressor's status: Off, Wait, On, Alarm or Manual.
  - **Remarks**: Register [1122](references/MODBUS_REGISTERS.md#reg-1122).
- **Mode status**: Summer or winter, each as manual, automatic or set by a digital input.
  - **Remarks**: Register [1110](references/MODBUS_REGISTERS.md#reg-1110).
- **Operating mode (season)**: The season setting: Summer, Winter or Auto.
  - **Remarks**: Register [1583](references/MODBUS_REGISTERS.md#reg-1583).

### Switches

- **Unit on/off (Modbus)**: Switches the unit on and off over Modbus.
  - **Remarks**: Register [1105](references/MODBUS_REGISTERS.md#reg-1105). Needs *Enable on/off via Modbus (PH02)* on the setup device.
- **Dehumidify (Modbus)**: The dehumidify request. In winter on a brine circuit only with a passing brine temperature guard.
  - **Remarks**: Register [1140](references/MODBUS_REGISTERS.md#reg-1140). Needs *Enable dehumidify (DEU) via Modbus (PH28)* on the setup device.
- **Integration request (cool in summer, heat in winter)**: The integration request: dehumidify and cool in summer, **heat in winter**. Refused outside summer unless *Allow winter heating* is on in the integration options; always refused in winter on a brine circuit.
  - **Remarks**: Register [1139](references/MODBUS_REGISTERS.md#reg-1139). Needs *Enable integration (INT) via Modbus (PH27)* on the setup device.
- **Force dehumidify when cooling**: On (factory): an integration request also starts the compressor. Off: the integration request cools only with the water, see [Operating modes in summer](../README.md#operating-modes-in-summer) ([PU05](references/MODBUS_REGISTERS.md#pu05)).
  - **Remarks**: Register [1692](references/MODBUS_REGISTERS.md#reg-1692). Configuration entity.

### Diagnostic

Read-only values for troubleshooting. Home Assistant shows them in the Diagnostic section of the device page.

- **Manual fan request (display)**: The display's manual fan request in %. Without a display it reads the band minimum while the fan runs.
  - **Available for**: `R` units.
  - **Remarks**: Register [1114](references/MODBUS_REGISTERS.md#reg-1114).
- **Fan integration request**: The fan request of the integration (INT) fan control in %, one of the requests the fan speed is the highest of ([UNIT_BEHAVIOUR §9.1](references/UNIT_BEHAVIOUR.md#91-bands-and-sources)). 0 while dehumidifying; a non-zero value during an integration request has not been seen on a real unit yet.
  - **Available for**: `R` units.
  - **Remarks**: Register [1112](references/MODBUS_REGISTERS.md#reg-1112).
- **Water valve / pump output**: Relay K5, the external water valve (V3V) and the pump output (PM) switched with it: Off, On or Not configured.
  - **Remarks**: Register [1126](references/MODBUS_REGISTERS.md#reg-1126).
- **Water condenser valve**: Relay K4, the internal valve. A real unit reads On in standby, against the handbook's description, so its meaning is unverified ([UNIT_BEHAVIOUR §11.1](references/UNIT_BEHAVIOUR.md#111-internal-valve-relay-k4)); the climate action does not use it.
  - **Remarks**: Register [1124](references/MODBUS_REGISTERS.md#reg-1124).
- **Water circuit check**: `ok` or `attention`; the attribute `issues` lists what is wrong, see [Water circuit](../README.md#water-circuit-and-brine).
- **Supply fan max airflow**: The maximum fan airflow in m³/h, from the airflow calibration in the integration options.
- **Max total airflow**: The same value as *Supply fan max airflow*, kept for convenience.
## HRDS+ setup

**Why it exists.** A headless unit needs a dozen settings reviewed before it is
safe to operate: display priority, probes, the Modbus enables, time programs,
the remote contact. They are one checklist on their own device. **Why it is
separate:** the main device stays an operating surface, and nothing here is
touched day to day. The Modbus enables are yours to set and the integration
never writes them; *Allow operational requests* is the integration's own gate.
The **Setup check** sensor lists what is left to fix; the
[first-use checklist](../README.md#first-use-checklist) walks through it.

### Binary sensors

- **Room temperature probe OK**: On while the room temperature probe is healthy (AL28 not active). **Unknown** without a display or a probe on AI2 ([HA02](references/MODBUS_REGISTERS.md#ha02)): there is nothing to check.
  - **Remarks**: Register [769](references/MODBUS_REGISTERS.md#reg-769), bit 11.
- **Room humidity probe OK**: On while the room humidity probe is healthy (AL34 not active). **Unknown** without a display or a probe on AI3 ([HA03](references/MODBUS_REGISTERS.md#ha03)).
  - **Remarks**: Register [770](references/MODBUS_REGISTERS.md#reg-770), bit 1.
- **Unit has integration function (PG02)**: On when the unit has the integration (INT) function ([PG02](references/MODBUS_REGISTERS.md#pg02) = 1). An installer setting, read-only, not a Modbus permission.
  - **Remarks**: Register [1798](references/MODBUS_REGISTERS.md#reg-1798).
- **Remote on/off contact closed**: State of the remote on/off contact (meaning inferred, unverified).
  - **Remarks**: Register [257](references/MODBUS_REGISTERS.md#reg-257), bit 0.

### Selects

- **T/H probe source (HA00)**: Which source feeds the room temperature and humidity ([HA00](references/MODBUS_REGISTERS.md#ha00)). **Set to *None / external probes* when running without a display.**
  - **Options**: None/external, CNU2 T, CNU2 T+H, CNU T, CNU T+H, EPJ T, EPJ T+H.
  - **Remarks**: Register [1803](references/MODBUS_REGISTERS.md#reg-1803).
- **T/H probe temperature input (AI2, HA02)**: What is wired to analog input AI2 (terminal M2), [HA02](references/MODBUS_REGISTERS.md#ha02). Without a display this is the only room temperature the unit can regulate on. **Leave on *Unused* unless a probe is wired**, or the unit raises AL28.
  - **Options**: Unused, Room temperature probe (NTC 10 kΩ).
  - **Remarks**: Register [1805](references/MODBUS_REGISTERS.md#reg-1805).
- **T/H probe humidity input (AI3, HA03)**: The same for AI3 (terminal M3) and a humidity probe ([HA03](references/MODBUS_REGISTERS.md#ha03)); with nothing wired it raises AL34. A code other than these shows as unknown and the setup check reports `probe_input_unrecognised`.
  - **Options**: Unused, Room humidity probe (4–20 mA), Room humidity probe (0–10 V).
  - **Remarks**: Register [1806](references/MODBUS_REGISTERS.md#reg-1806).

### Sensors

- **Setup check**: `ok` or `attention`; the attribute `issues` lists the open items and `to_fix` says what to do about each.
- **Unit status**: Why the unit is off (by display, digital input, Modbus, time program or clock), or On.
  - **Remarks**: Register [1104](references/MODBUS_REGISTERS.md#reg-1104).
- **Machine type (PG01)**: The fan arrangement ([PG01](references/MODBUS_REGISTERS.md#pg01)): *supply fan only* or *supply and exhaust fan*. **Not** a recirculation flag: an `R` unit reads *supply fan only*.
  - **Remarks**: Register [1797](references/MODBUS_REGISTERS.md#reg-1797).
- **Remote on/off input (HB03)**: How the remote on/off contact is used ([HB03](references/MODBUS_REGISTERS.md#hb03)): unused, normally closed or normally open.
  - **Remarks**: Register [1824](references/MODBUS_REGISTERS.md#reg-1824).
- **Season change owner (PC11)**: Who owns the season change when a display is connected ([PC11](references/MODBUS_REGISTERS.md#pc11)).
  - **Remarks**: Register [1878](references/MODBUS_REGISTERS.md#reg-1878).
- **Temperature unit (PH05)**: Celsius or Fahrenheit ([PH05](references/MODBUS_REGISTERS.md#ph05)).
  - **Remarks**: Register [1781](references/MODBUS_REGISTERS.md#reg-1781).
- **Supply fan output allocation (HC04)**: Raw allocation of the supply fan output ([HC04](references/MODBUS_REGISTERS.md#hc04)).
  - **Remarks**: Register [1832](references/MODBUS_REGISTERS.md#reg-1832).
- **Recirculation damper relay allocation (HD01)**: Raw allocation of relay DO1 ([HD01](references/MODBUS_REGISTERS.md#hd01)): 10 = recirculation damper NO, 9 = NC. Not *disabled* on an `R` unit.
  - **Remarks**: Register [1838](references/MODBUS_REGISTERS.md#reg-1838).
- **Damper pre-start time (PS01)**: How long the damper opens before the fan starts, in seconds ([PS01](references/MODBUS_REGISTERS.md#ps01)).
  - **Remarks**: Register [1698](references/MODBUS_REGISTERS.md#reg-1698).

### Switches

- **Allow operational requests**: The integration's own safety gate. Off after installing; while off, switching on, dehumidifying, cooling and heating are refused. Kept across restarts. See [Allow operational requests](../README.md#allow-operational-requests).
- **Enable on/off via Modbus (PH02)**: Lets Home Assistant switch the unit on and off ([PH02](references/MODBUS_REGISTERS.md#ph02)). Yours to set; the integration never changes it ([step 4](../README.md#4-choose-what-home-assistant-may-control)).
  - **Remarks**: Register [1778](references/MODBUS_REGISTERS.md#reg-1778).
- **Enable dehumidify (DEU) via Modbus (PH28)**: Lets Home Assistant request dehumidifying ([PH28](references/MODBUS_REGISTERS.md#ph28)). Yours to set.
  - **Remarks**: Register [1870](references/MODBUS_REGISTERS.md#reg-1870).
- **Enable integration (INT) via Modbus (PH27)**: Lets Home Assistant request integration: cool in summer, heat in winter ([PH27](references/MODBUS_REGISTERS.md#ph27)). Yours to set.
  - **Remarks**: Register [1869](references/MODBUS_REGISTERS.md#reg-1869).
- **Enable on/off via display (PH01)**: On/off by a wired display ([PH01](references/MODBUS_REGISTERS.md#ph01)). Kept **off** while the option *A wired CNU2 display is connected* is off (the default); turning it on by hand is undone on the next poll.
  - **Remarks**: Register [1777](references/MODBUS_REGISTERS.md#reg-1777).
- **Time programs enabled (PH03)**: Time programs can switch the unit off ([PH03](references/MODBUS_REGISTERS.md#ph03)); switch it off for control from Home Assistant only.
  - **Remarks**: Register [1779](references/MODBUS_REGISTERS.md#reg-1779).
- **Unit on by DI request (PC12)**: A request on a digital input starts the unit even with the OFF contact open ([PC12](references/MODBUS_REGISTERS.md#pc12)).
  - **Remarks**: Register [1894](references/MODBUS_REGISTERS.md#reg-1894).
- **Enable free cooling/heating**: Free cooling and heating on the outdoor temperature ([PG03](references/MODBUS_REGISTERS.md#pg03)); while off, the outdoor temperature drives nothing. Leave off without an outdoor probe.
  - **Remarks**: Register [1799](references/MODBUS_REGISTERS.md#reg-1799).

## HRDS+ installer

**Why it exists.** The handbook's installer menu (§5.3) has about 240
parameters with a Modbus address. They are not needed for setup or normal use.
**Why it is separate and opt-in:** a few of them cut the connection or are
destructive, and reading them all makes the poll too heavy for the real unit,
so the device is **off by default** and its registers are never part of the
regular poll. Turn on *Installer device* in the integration options
(**Settings → Devices & services → HRDS+ → Configure**); turning it off again
removes the device and its entities. Each parameter's name starts with its
code, for example *PC07 Max water temperature for dehumidify / summer
integration*.

The parameters are read when the option is turned on, at each start of the
integration, and when you press **Refresh installer parameters**; after you
change one, just that register is read back.
([PC07](references/MODBUS_REGISTERS.md#pc07), [PC08](references/MODBUS_REGISTERS.md#pc08),
[PU08](references/MODBUS_REGISTERS.md#pu08), [PF12](references/MODBUS_REGISTERS.md#pf12),
[PH09](references/MODBUS_REGISTERS.md#ph09) and [PH10](references/MODBUS_REGISTERS.md#ph10),
which the water check and the heating logic use, are read once at start even
without the installer device.)

The parameters are **not listed one by one** here; the full list with
addresses and scaling is
[`references/MODBUS_REGISTERS.md` §16](references/MODBUS_REGISTERS.md#16-installer-menu-parameters-installer-device).

* Writable parameters are configuration entities: fans (PF), compressor (PE),
  water valves (Pb), dehumidification (PU), alarms (PA), season change (PC),
  setpoint limits ([PH07](references/MODBUS_REGISTERS.md#ph07)–[PH10](references/MODBUS_REGISTERS.md#ph10)),
  probe offsets (PM8x) and hour counters ([PM00](references/MODBUS_REGISTERS.md#pm00)–[PM04](references/MODBUS_REGISTERS.md#pm04)).
* Read-only, diagnostic entities: the Modbus/CAN link
  ([PH11](references/MODBUS_REGISTERS.md#ph11)–[PH17](references/MODBUS_REGISTERS.md#ph17);
  changing them would cut the connection), the I/O allocation (HA, HB, HC, HD;
  manufacturer level), refrigerant and pressure-probe ranges, the compressor
  safety-time bypass ([PE05](references/MODBUS_REGISTERS.md#pe05)), forced
  compressor ([PM21](references/MODBUS_REGISTERS.md#pm21)) and test mode (PT).
* Parameters the HRDS+ does not use (return fan, air quality, heat-recovery
  defrost, external damper, rotary exchanger, expansion I/O) exist but are
  **disabled by default**; enable them in the entity settings if needed.
* Never exposed: passwords, [PH15](references/MODBUS_REGISTERS.md#ph15)
  *restore factory defaults*, [PH18](references/MODBUS_REGISTERS.md#ph18)
  *clear alarm history*.

### Buttons

- **Refresh installer parameters**: Reads every installer register once.
  - **Remarks**: Configuration entity.

### Diagnostic

Read-only; Home Assistant shows it in the Diagnostic section of the device page.

- **Installer parameters last read**: When the installer parameters were last read.
