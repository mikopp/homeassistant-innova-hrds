# TODO — verify against real hardware

Most of the register map, scaling and unit behaviour was distilled from the
manufacturer PDFs in [`doc/references/`](../doc/references/). What has been seen on the
real unit so far is recorded in the evidence log of
[`doc/references/UNIT_BEHAVIOUR.md` §13](../doc/references/UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware).
This file holds only what is still open. When an item is answered: add a `T`
row to that evidence log, replace the `[INFERRED]` tags it settles, fix the
code/docs, and remove the item from this file.

The reference unit is an HRDS+ 30 `R` `DC`, headless, no probes, on a brine
circuit, behind a ComfoAir Q350. Sections 1 to 7 can be tested on it; section 8
needs another unit, a display, a probe or extra wiring. Section 9 holds
decisions about the integration, not hardware questions.

## 1. Requests, enables and persistence

- [ ] **Enables gate the requests.** Confirm that with an enable off the unit
      ignores the matching request, that it keeps a request written while the
      enable was off, and starts it once the enable is turned on
      (`UNIT_BEHAVIOUR.md` §3.3, [INFERRED]). Entities (setup device):
      *Enable on/off via Modbus ([PH02](../doc/references/MODBUS_REGISTERS.md#ph02))* gates *Unit on/off (Modbus)*;
      *Enable dehumidify (DEU) via Modbus ([PH28](../doc/references/MODBUS_REGISTERS.md#ph28))* gates *Dehumidify (Modbus)*;
      *Enable integration (INT) via Modbus ([PH27](../doc/references/MODBUS_REGISTERS.md#ph27))* gates *Integration request*.
- [ ] **Power cycle with a request on.** The on/off state survives a power
      cycle (T30); do *Dehumidify (Modbus)* ([1140](../doc/references/MODBUS_REGISTERS.md#reg-1140)) and *Integration request*
      ([1139](../doc/references/MODBUS_REGISTERS.md#reg-1139)) survive too? Power-cycle once with a dehumidify request on.
- [ ] **An OFF always wins** over an ON from any source (display/DI/Modbus),
      per the manual [MB p.5].
- [ ] **Exact read-back lag per register.** ON and OFF are bracketed for [1140](../doc/references/MODBUS_REGISTERS.md#reg-1140)
      and the OFF of [1105](../doc/references/MODBUS_REGISTERS.md#reg-1105) (T39): the 25 s re-read of `PENDING_RECHECK_SECONDS`
      caught every ON, OFF once at 12 s. Debug logging for
      `custom_components.innova_hrds` ("HRDS+ confirmed <key>=<value> after
      N s") would give the rest: ON of [1105](../doc/references/MODBUS_REGISTERS.md#reg-1105), and the season (T31; its write
      time is not in the history).

## 2. Start and stop of a dehumidify (DEU) cycle

Data: `tests/devices/runs/` and T11–T22, T32–T38. Log at 5 s with
`diagnose_hrds.py --watch` for the items below.

- [ ] **Which parameter sets the start hold?** It counts from the request or
      the fan, not from the last compressor event, and `CmpStatus` reads OFF
      during it (T32); [PE01](../doc/references/MODBUS_REGISTERS.md#pe01) is the off time after a stop (T33). Log [1122](../doc/references/MODBUS_REGISTERS.md#reg-1122) and
      [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) every 5 s through a start, against [PS01](../doc/references/MODBUS_REGISTERS.md#ps01) + [PE04](../doc/references/MODBUS_REGISTERS.md#pe04) and [PE03](../doc/references/MODBUS_REGISTERS.md#pe03).
- [ ] **Does [PE32](../doc/references/MODBUS_REGISTERS.md#pe32) count minutes?** The compressor stops by itself after
      92–94 min (T34); [PE32](../doc/references/MODBUS_REGISTERS.md#pe32) reads 90 and is listed in seconds. Log the
      compressor output against [PE28](../doc/references/MODBUS_REGISTERS.md#pe28) (52 rps) through a run over 90 min. If
      it holds, correct the unit in `MODBUS_REGISTERS.md` §16.
- [ ] **Stop sequence at 5 s.** Three stops at 1-minute resolution (T19, T36,
      T38). Still to log: compressor stop against [PE02](../doc/references/MODBUS_REGISTERS.md#pe02), the ramp-down
      ([PE25](../doc/references/MODBUS_REGISTERS.md#pe25)), V3V + PM closing against [Pb01](../doc/references/MODBUS_REGISTERS.md#pb01), fan run-on against [PF03](../doc/references/MODBUS_REGISTERS.md#pf03).
- [ ] **Supply fan running and the climate action on the next stop.** No run since
      0.9.5 installed that sensor (`doc/tested-setups.md`). On 0.9.4
      `hvac_action` read *Idle* while the fan ran on at 40 % (T19): check
      against ADR-0028.
- [ ] **Does the fan stand still while the delay runs?** [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) read `off` and
      [639](../doc/references/MODBUS_REGISTERS.md#reg-639) read 0 between damper and fan at every poll, and `wait_on` was never
      read (T35). Log [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) every 5 s through a start for a short
      `wait_on`, and look at the fan; also [639](../doc/references/MODBUS_REGISTERS.md#reg-639) in `wait_off`.
      *Supply fan running* and *Recirculation active* depend on
      it.
- [ ] **First anti-stagnation pulse after a stop: 1 or 2 hours?** 2 hours after
      a clean stop (T20); about 1 hour after the sniffing pulse of an AL03 stop
      (T37). Needs a second clean stop with the unit left on in standby for
      over 2 hours.
- [ ] **[PU13](../doc/references/MODBUS_REGISTERS.md#pu13) at the handbook default (22 °C).** At the shipped 10 °C the
      compressor started without a room probe (T15). Only worth testing if
      [PU13](../doc/references/MODBUS_REGISTERS.md#pu13) is ever raised.

## 3. Fan

The fan is read-only (ADR-0034); the band is the Modbus lever (`UNIT_BEHAVIOUR.md`
§9.1). Remaining tests: [`fan-speed-tests.md`](fan-speed-tests.md).

- [ ] **Fan-speed tests A (jump or ramp), B, E, F and G** in
      [`fan-speed-tests.md`](fan-speed-tests.md). D needs a potentiometer
      (section 8).
- [ ] **Speed control through the band.** Once test G is run, decide whether
      to propose a speed control (raise via the minimum, lower via the
      maximum). It costs EEPROM writes per change (ADR-0023) and needs an ADR.
- [ ] **Fan = 0 during dehumidification, and keeping the damper closed.**
      Background: `UNIT_BEHAVIOUR.md` §9.3, forum F#77–#79, F#93. Untested and
      expected not to work; listed so it is run once and recorded, not
      because any option is recommended.
      1. Record [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1853](../doc/references/MODBUS_REGISTERS.md#reg-1853) ([PF28](../doc/references/MODBUS_REGISTERS.md#pf28)), [1647](../doc/references/MODBUS_REGISTERS.md#reg-1647) ([PF10](../doc/references/MODBUS_REGISTERS.md#pf10)), [1698](../doc/references/MODBUS_REGISTERS.md#reg-1698) ([PS01](../doc/references/MODBUS_REGISTERS.md#ps01)), [1831](../doc/references/MODBUS_REGISTERS.md#reg-1831) ([HC03](../doc/references/MODBUS_REGISTERS.md#hc03)),
         [1832](../doc/references/MODBUS_REGISTERS.md#reg-1832) ([HC04](../doc/references/MODBUS_REGISTERS.md#hc04)), [1838](../doc/references/MODBUS_REGISTERS.md#reg-1838) ([HD01](../doc/references/MODBUS_REGISTERS.md#hd01)) to restore them afterwards.
      2. Run the MVHR at 150 m³/h or more, start DEU (enables on, INT off).
      3. Write [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) ← 0. (A [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) write below the band is refused, T27, and
         one inside it is not kept, T23, so [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) alone does nothing.)
      4. After [PS01](../doc/references/MODBUS_REGISTERS.md#ps01) plus the start delays read [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1117](../doc/references/MODBUS_REGISTERS.md#reg-1117), [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119), [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112), [1134](../doc/references/MODBUS_REGISTERS.md#reg-1134),
         `Packed_DO1` ([384](../doc/references/MODBUS_REGISTERS.md#reg-384)) bits 8–9, [1122](../doc/references/MODBUS_REGISTERS.md#reg-1122), [1121](../doc/references/MODBUS_REGISTERS.md#reg-1121), `PackedAlarm_1` ([768](../doc/references/MODBUS_REGISTERS.md#reg-768)) bit 10
         (AL11). Check physically whether the fan turns and whether air is
         drawn in at the recirculation grille.
      5. Restore the recorded values.

      Options to keep the damper closed with the fan off (Modbus only):
      * **A.** [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) ← 0, [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) ← 100 and a low fan request. Likely not
        working: HB 6.5 opens the damper on every request; V#78; F#77 could
        not go below 30 %.
      * **B.** [HD01](../doc/references/MODBUS_REGISTERS.md#hd01) ([1838](../doc/references/MODBUS_REGISTERS.md#reg-1838)) 10 → 9 (damper NO → NC, F#79). Moves the open
        period to standby; whether it applies without a restart is unknown.
      * **C.** [HD01](../doc/references/MODBUS_REGISTERS.md#hd01) ← 0 (V#78). F#79: the compressor then does not start.
      * **D.** With B: [HC04](../doc/references/MODBUS_REGISTERS.md#hc04) ([1832](../doc/references/MODBUS_REGISTERS.md#reg-1832)) 1 → 0 and [HC03](../doc/references/MODBUS_REGISTERS.md#hc03) ([1831](../doc/references/MODBUS_REGISTERS.md#reg-1831)) 0 → 1, so the
        controller drives a "fan" on the empty AO3 (F#79, F#93 on an
        HRDS+ 50). [HC04](../doc/references/MODBUS_REGISTERS.md#hc04) ← 0 alone stops the compressor from starting.

      Side effects: after D, [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119), [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) and *Supply fan airflow*
      report a fan that is not turning. Whether HC/HD writes wear memory is
      unknown: do not toggle them per run. Restore the values afterwards.

## 4. Integration request (INT) and cooling

No INT request has been run yet. One summer INT run answers most of these.

- [ ] **Climate mode writes** (ADR-0025): COOL = on + dehumidify +
      integration_request **on**; HEAT = on + integration_request, dehumidify
      off; OFF = both requests off and the unit off. DRY is seen working
      (T11–T19). Confirm the others produce the expected unit behaviour and
      feedback.
- [ ] **`hvac_action` while cooling.** *Drying* shows during DEU; confirm
      *Cooling* during an INT run and *Idle*/*Off* after it.
- [ ] **K4 / [1124](../doc/references/MODBUS_REGISTERS.md#reg-1124) while cooling.** It reads 1 in standby and during DEU (T5,
      T11, T18); the Modbus manual labels `Packed_DO1` bits 12–13 `0 =
      Integration, 1 = Dehumidify`. Read [1124](../doc/references/MODBUS_REGISTERS.md#reg-1124) and those bits during INT with
      the compressor on: expect 0. If it tells cooling from dehumidifying,
      `hub.is_cooling` can use it. This also settles the [1124](../doc/references/MODBUS_REGISTERS.md#reg-1124) enum ([1126](../doc/references/MODBUS_REGISTERS.md#reg-1126) reads
      0 = off, 1 = on: T10, T11, T19).
- [ ] **What is [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) (`FanIntegration_Request`)?** 0 through every DEU run
      (T16, T18, T41); a 0–100 % fan request by the Modbus map. Read it during INT
      ([`fan-speed-tests.md`](fan-speed-tests.md) test E).
- [ ] **INT with [PU05](../doc/references/MODBUS_REGISTERS.md#pu05) off (water above [PU08](../doc/references/MODBUS_REGISTERS.md#pu08)).** Set
      *Force dehumidify when cooling* off, request Cool with no DEU:
      the compressor should stay off. Does the valve/pump run and does the
      supply air cool? Undocumented "passive cooling"; restore [PU05](../doc/references/MODBUS_REGISTERS.md#pu05) on
      afterwards.
- [ ] **INT + DEU with [PU05](../doc/references/MODBUS_REGISTERS.md#pu05) off.** The same as INT with [PU05](../doc/references/MODBUS_REGISTERS.md#pu05) on (internal
      valve closed, cold air), or does DEU's reheat win? Read [1124](../doc/references/MODBUS_REGISTERS.md#reg-1124) and the
      supply air temperature (section 8).

## 5. Water circuit and the passive path (early summer)

- [ ] **Brine flow lost while the heat pump runs (known, likely a hardware
      fix).** In the parallel branch (variant 6), the heat pump's pump
      overpowers the unit's small `PM` pump. When the heat pump compressor
      started during a DEU run the unit lost flow: water 17 → 46 °C in 3 min,
      AL12, then AL03 ended the request (T38). Fix the hydraulics (for example
      a stronger pump or a check valve; not chosen yet), then repeat a run with
      the heat pump compressor on. Until then avoid long requests while it
      runs.
- [ ] **Passive path (water below [PU08](../doc/references/MODBUS_REGISTERS.md#pu08)).** With water ([501](../doc/references/MODBUS_REGISTERS.md#reg-501)) below [PU08](../doc/references/MODBUS_REGISTERS.md#pu08) ([1695](../doc/references/MODBUS_REGISTERS.md#reg-1695),
      10 °C) and a DEU or INT request in summer: `compressor_status` ([1122](../doc/references/MODBUS_REGISTERS.md#reg-1122))
      stays off, `water_valve_pump` ([1126](../doc/references/MODBUS_REGISTERS.md#reg-1126)) is On, supply air colder and drier.
      Note which way [1124](../doc/references/MODBUS_REGISTERS.md#reg-1124) goes.
- [ ] **[PU09](../doc/references/MODBUS_REGISTERS.md#pu09) second step.** In the same state, does the compressor join after
      [PU10](../doc/references/MODBUS_REGISTERS.md#pu10) ([1697](../doc/references/MODBUS_REGISTERS.md#reg-1697), 120 min) while the request is on, and stop when the request
      is satisfied?
- [ ] **Does the unit judge the first, standing brine reading?** At the
      request start the probe reads the warm standing brine (18.3 °C), then
      14.8 °C once V3V + PM flow (T17). If the brine flows below [PU08](../doc/references/MODBUS_REGISTERS.md#pu08) but
      stands above it, does the unit take the passive path or start the
      compressor, and do [PC07](../doc/references/MODBUS_REGISTERS.md#pc07)/AL03 judge the standing value?
- [ ] **Brine guard default 8 °C.** With brine at 8–10 °C: requests start,
      the unit runs the passive path, AL16 ([PA43](../doc/references/MODBUS_REGISTERS.md#pa43) = 3 °C) does not trip, and
      the register does not ice up.

## 6. Season and winter

- [ ] **Back to summer.** Only [HB04](../doc/references/MODBUS_REGISTERS.md#hb04) 4 → 3 has been written (T31), and the
      unit stands in winter since 2026-10-30. Write 3 → 4 with *Season*
      and check the read-back follows at the next read cycle.
- [ ] **[PU02](../doc/references/MODBUS_REGISTERS.md#pu02) "with water" / "without water".** What changes between 1 and 2
      (does V3V/PM open)? Does [PU02](../doc/references/MODBUS_REGISTERS.md#pu02) = 0 also block a Modbus or DI dehumidify
      request in winter, or only the automatic one?
- [ ] **Automatic season with the water probe** ([PC05](../doc/references/MODBUS_REGISTERS.md#pc05) = 2, [PC06](../doc/references/MODBUS_REGISTERS.md#pc06) = 0): which
      thresholds decide? Not described in the handbook.

## 7. Registers, transport and setup checks

- [ ] **Block-read chunking** (`C_MAX_BLOCK=10`, `C_MAX_GAP=8` in
      `const.py`). 120 got no reply through the gateway (T9); 10 covers the
      map. The hub halves a block that is not answered and falls back to
      per-register reads on an error. Find the real limit (gateway or
      controller) and raise the cap if it is safe, and note which addresses
      answer "illegal data address". The Home Assistant log holds no such
      warning since its last restart; older ones are gone.
- [ ] **[1101](../doc/references/MODBUS_REGISTERS.md#reg-1101) and [1102](../doc/references/MODBUS_REGISTERS.md#reg-1102).** They change in every dump and have no row in
      `MODBUS_REGISTERS.md` (T41). [1102](../doc/references/MODBUS_REGISTERS.md#reg-1102) only rises and [1101](../doc/references/MODBUS_REGISTERS.md#reg-1101) looks like its low
      word, perhaps a seconds counter. Compare two dumps with known times, then
      document them.
- [ ] **Registers above 1900** ([PT05](../doc/references/MODBUS_REGISTERS.md#pt05)–[PT11](../doc/references/MODBUS_REGISTERS.md#pt11), [PH31](../doc/references/MODBUS_REGISTERS.md#ph31)–[PH35](../doc/references/MODBUS_REGISTERS.md#ph35), [PA61](../doc/references/MODBUS_REGISTERS.md#pa61)/[PA62](../doc/references/MODBUS_REGISTERS.md#pa62)): the dump's
      holding snapshot ends at 1900. Extend `diagnose_hrds.py`, and add them
      to the installer device if they are readable.
- [ ] **Installer scaling spot-checks.** [PM81](../doc/references/MODBUS_REGISTERS.md#pm81) ([1617](../doc/references/MODBUS_REGISTERS.md#reg-1617)) reads 0, so its ×0.1
      is unseen; [PA20](../doc/references/MODBUS_REGISTERS.md#pa20) ([1736](../doc/references/MODBUS_REGISTERS.md#reg-1736), not in the PDF table) reads 1 and is not an
      installer row yet.
- [ ] **`remote_contact_closed` (257 bit 0).** Confirm the meaning by opening
      the OFF/OFF contact (factory bridge) once.

## 8. Needs another unit, a display, a probe or extra wiring

- [ ] **Other variants' identity.** Does an HRDS+ 50, a non-`R` or a non-`DC`
      unit report an `EPB9…` product code (FC 43)? Loosen
      `EXPECTED_PRODUCT_PREFIX` if not. Also: what does a gateway that does
      not forward FC 43 return?
- [ ] **Non-`R` unit read-back.** Does `outDO_RecircDamper` ([1134](../doc/references/MODBUS_REGISTERS.md#reg-1134)) read
      `2 = Disable` without recirculation, and what do the fan registers read?
- [ ] **As-delivered settings.** The reference unit shipped with values that
      differ from the handbook (`UNIT_BEHAVIOUR.md` §15). A second unit's dump
      shows whether these are the distributor's presets.
- [ ] **Supply-air temperature.** The unit's supply probe ([503](../doc/references/MODBUS_REGISTERS.md#reg-503)) is not fitted,
      so "DEU gives dry air at about room temperature" (HB 2.6.1) is
      unverified. Log an external sensor downstream of the HRDS through a run;
      that also shows what K4 does to the air. With about 16.5 °C brine expect
      below room temperature (HB 3.8.5).
- [ ] **Room probe or display: humidity and setpoints.**
      * Room humidity ([505](../doc/references/MODBUS_REGISTERS.md#reg-505)) and the setpoint [PU01](../doc/references/MODBUS_REGISTERS.md#pu01) ([1586](../doc/references/MODBUS_REGISTERS.md#reg-1586)) are whole %RH, no
        ×0.1 (the clamps [PH29](../doc/references/MODBUS_REGISTERS.md#ph29)/[PH30](../doc/references/MODBUS_REGISTERS.md#ph30) read raw 55/65).
      * Target humidity acts only while on + dehumidifying, target
        temperature only in COOL/summer; the [PH29](../doc/references/MODBUS_REGISTERS.md#ph29)/[PH30](../doc/references/MODBUS_REGISTERS.md#ph30) clamps hold.
      * Summer/winter setpoint range: `const.py` clamps to 15–35 °C, the
        Modbus PDF lists Max `158.0`. Find the usable range.
- [ ] **Air quality ([506](../doc/references/MODBUS_REGISTERS.md#reg-506)).** Unit, scale and probe type. The device class is
      unset (`AQI` takes no unit); if it is CO₂, `SensorDeviceClass.CO2` with
      ppm.
- [ ] **A failed (wired but broken) probe.** Only `0x8004` and `0x7FFA` have
      been seen in the sentinel window `0x7FF0..0x800F`. What does a broken
      probe read, and does it raise AL28/AL34?
- [ ] **[PU13](../doc/references/MODBUS_REGISTERS.md#pu13) and a DI request.** Does [PU13](../doc/references/MODBUS_REGISTERS.md#pu13) veto a dehumidify request from
      the `DEU` contact? Needs a contact on the input.
- [ ] **Winter heating evidence.** `hub.is_heating` needs the valve/pump
      output on, no AL04, compressor off and water at or above [PC08](../doc/references/MODBUS_REGISTERS.md#pc08). Confirm on
      a unit on a heating circuit that this is when the supply air warms, and
      that AL04 raises below [PC08](../doc/references/MODBUS_REGISTERS.md#pc08). Not possible on brine.
- [ ] **0–10 V on FAN+** ([`fan-speed-tests.md`](fan-speed-tests.md) test D):
      needs a potentiometer on the display terminals.
- [ ] **Fan tachometer.** No input is allocated to it (T21), so the RPM reads
      0. Installer question: can the fan's tachometer wire go to a free input
      (function 45/46)?

## 9. Integration decisions (no hardware needed)

- [ ] ***Season* jumps back after a write.** It shows the old season
      until the next read cycle (T31), because `season` is not in
      `PENDING_KEYS`. Add it, so it shows the command until confirmed like the
      requests? Check against ADR-0006 first.
- [ ] Should the operation gate refuse climate `hvac_mode` writes with a
      friendlier message (it surfaces the `ServiceValidationError` today)?
- [ ] **`water_below_compressor_limit`** puts the water check on `attention`
      during normal passive operation. Once the passive path is confirmed
      (section 5), decide whether it becomes an informational attribute.
- [ ] **Alarm detail.** AL03, AL04, AL11, AL12, AL16, AL22, AL28 and AL34 are
      binary sensors. Expose the other alarm bits and the `BMS_ALxx` reset
      registers ([785](../doc/references/MODBUS_REGISTERS.md#reg-785)/[786](../doc/references/MODBUS_REGISTERS.md#reg-786)/[791](../doc/references/MODBUS_REGISTERS.md#reg-791))?
- [ ] **Remote fan request** ([1116](../doc/references/MODBUS_REGISTERS.md#reg-1116), R/O) is not exposed; the display's manual
      request ([1114](../doc/references/MODBUS_REGISTERS.md#reg-1114)) is (*Manual fan request (display)*). Expose it?
