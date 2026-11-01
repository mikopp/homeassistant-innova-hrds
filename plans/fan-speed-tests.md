# Fan speed over Modbus: hardware test plan

For an agent (or the owner) with access to the reference unit, HRDS+ 30 `R` `DC`,
headless. The integration shows the fan with read-only sensors and writes
only the four band registers ([PF28](../doc/references/MODBUS_REGISTERS.md#pf28), [PF10](../doc/references/MODBUS_REGISTERS.md#pf10), [PF27](../doc/references/MODBUS_REGISTERS.md#pf27), [PF09](../doc/references/MODBUS_REGISTERS.md#pf09)) through the *Fan min/max speed*
numbers (ADR-0034, [`doc/entity-reference.md`](../doc/entity-reference.md)). Each
test below checks one open question from
[`doc/references/UNIT_BEHAVIOUR.md` §9.1](../doc/references/UNIT_BEHAVIOUR.md#91-bands-and-sources).
Tags (`[HB 6.2]`, `[MB p.7]`, `T23`) are explained in §0 of that file.

## Proven

All on the reference unit, headless, during DEU runs.

| Fact | Evidence |
|------|----------|
| With every fan request at 0 the fan runs at the band minimum; the unit sets [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) ([1614](../doc/references/MODBUS_REGISTERS.md#reg-1614)) and the display request ([1114](../doc/references/MODBUS_REGISTERS.md#reg-1114)) from 0 to the minimum when the fan starts and back to 0 when the request ends | T16, T22 |
| A [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) write inside the band (60, 55 %) is acknowledged and changes nothing; at reads 0.5 s apart [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) never moved | T23, T28 |
| A [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) write below the band minimum (40, 45 % against 50 %) is refused with exception 04 (FC 06). The unit therefore reads the ×0.01 scaled value and compares it with the band | T27 (with T23, T25) |
| Raising [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) during a run raises the fan, [639](../doc/references/MODBUS_REGISTERS.md#reg-639) and [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) in the same poll (polls ≤ 60 s apart) | T25 |
| Lowering [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) during a run leaves the fan where it is (50 → 45 at 50 %, 55 → 50 at 55 %); the unit's manual request is an absolute percentage clamped into the band | T24, T26 |
| [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) reads 0 through every DEU run | T16, T18, T41 |
| No input is allocated to the fan tachometer, so [1117](../doc/references/MODBUS_REGISTERS.md#reg-1117) reads 0 with the fan running | T21 |
| Allocations on the reference unit: [HA01](../doc/references/MODBUS_REGISTERS.md#ha01) = 58 (fan potentiometer 0–10 V), [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = [HA03](../doc/references/MODBUS_REGISTERS.md#ha03) = 0, [HA06](../doc/references/MODBUS_REGISTERS.md#ha06) = 6, [HA07](../doc/references/MODBUS_REGISTERS.md#ha07) = 8, [HB01](../doc/references/MODBUS_REGISTERS.md#hb01) = 27, [HB02](../doc/references/MODBUS_REGISTERS.md#hb02) = 26, [HB03](../doc/references/MODBUS_REGISTERS.md#hb03) = 2, [HB04](../doc/references/MODBUS_REGISTERS.md#hb04) = 4, [HB05](../doc/references/MODBUS_REGISTERS.md#hb05)..[HB07](../doc/references/MODBUS_REGISTERS.md#hb07) = 0 | T21 |
| [HB04](../doc/references/MODBUS_REGISTERS.md#hb04) can be written over Modbus to switch the season; no contact is wired to M9 | T31 |

## How to scale the fan

Hypotheses, each with the test that decides it. Nothing here is proven yet
beyond what the Proven table says.

1. **Pin the band (no hardware).** Write [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) = [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) = the target
   speed (during INT [PF27](../doc/references/MODBUS_REGISTERS.md#pf27) = [PF09](../doc/references/MODBUS_REGISTERS.md#pf09)). With one value in the band the clamp
   gives that speed whatever the unit's own manual request holds. Going up,
   write the minimum first; going down, the maximum first, so the minimum
   never exceeds the maximum. Up is proven (T25); down needs test G, the
   pinned band test B. It works with the existing entities
   [*Fan min speed (dehumidify)*](../doc/entity-reference.md#fan-min-speed-dehumidify) and [*Fan max speed (dehumidify)*](../doc/entity-reference.md#fan-max-speed-dehumidify), but every change is
   two EEPROM writes: once per run, not as a continuous control (ADR-0023).
2. **0–10 V on FAN+ (wiring).** The handbook's own proportional control:
   linear across the band, no EEPROM write [HB 4.5]. A 0–10 V output (for
   example a Shelly) driven from Home Assistant. Test D.
3. **Forced fan from an unwired input (no hardware).** Allocate the unused
   AI2 ([HA02](../doc/references/MODBUS_REGISTERS.md#ha02)) to function 19 "Fans forced by DI NC". An NC function reads an
   open contact as active, the same way [HB04](../doc/references/MODBUS_REGISTERS.md#hb04) 3/4 switches the season with
   nothing wired to M9 (T31); analog inputs already work as digital inputs on
   this unit ([HA06](../doc/references/MODBUS_REGISTERS.md#ha06) = 6, [HA07](../doc/references/MODBUS_REGISTERS.md#ha07) = 8, T21). [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) is then the fan speed. Test J0.
4. **Time bands and the potentiometer calibration.** [FSC](../doc/references/MODBUS_REGISTERS.md#fsc) with time
   programs on (test I) and [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) (test L; no effect expected without a
   signal on FAN+).

## Why PM20 does not work and what else could

Evidenced:

* The Modbus manual's fan chapter lists as writable only the four band
  registers [PF27](../doc/references/MODBUS_REGISTERS.md#pf27), [PF09](../doc/references/MODBUS_REGISTERS.md#pf09), [PF28](../doc/references/MODBUS_REGISTERS.md#pf28), [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) (two implied decimals: 40 % = 4000);
  [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) are marked "(read only)" [MB p.7].
* [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) is R/W only in the raw parameter table [MB p.18]. The handbook
  defines it as the display setting "via Display (read only)" [HB 5.3].
* There is no fan enable among the Modbus enables, which are
  [PH01](../doc/references/MODBUS_REGISTERS.md#ph01), [PH02](../doc/references/MODBUS_REGISTERS.md#ph02), [PH27](../doc/references/MODBUS_REGISTERS.md#ph27) and [PH28](../doc/references/MODBUS_REGISTERS.md#ph28) [MB p.5].
* The fan's request sources are the display, the 0–10 V input FAN+/FAN−,
  the room temperature (INT only), the time bands, the air-quality control and
  a forced-fan input; each is placed in the active band and the highest wins
  ([`UNIT_BEHAVIOUR.md` §9.1](../doc/references/UNIT_BEHAVIOUR.md#91-bands-and-sources)). On the reference unit none of them asks for
  more than the minimum during DEU, which is why the fan stays at [PF28](../doc/references/MODBUS_REGISTERS.md#pf28).
  [PF31](../doc/references/MODBUS_REGISTERS.md#pf31) changes only the integration (INT) fan control: 0 temperature,
  1 maximum of manual and remote, 2 maximum of all [HB 5.3].
* With time programs on ([PH03](../doc/references/MODBUS_REGISTERS.md#ph03)), the fan setpoints [FSC](../doc/references/MODBUS_REGISTERS.md#fsc)/[FSE](../doc/references/MODBUS_REGISTERS.md#fse)/[FSN](../doc/references/MODBUS_REGISTERS.md#fsn)
  ([1595](../doc/references/MODBUS_REGISTERS.md#reg-1595)–[1597](../doc/references/MODBUS_REGISTERS.md#reg-1597), R/W) feed the supply-fan time-band request
  [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115), and manual display control is active only without time
  programs [HB 6.2; MB p.18].
* [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) ([1660](../doc/references/MODBUS_REGISTERS.md#reg-1660), handbook default 70 %) is the supply fan speed forced by a
  digital input with input function 19 (normally closed) or 20 (normally
  open) "Fans forced by DI" [HB 5.3, input functions]. The state shows in
  `Packed_logicDI2` ([258](../doc/references/MODBUS_REGISTERS.md#reg-258)) bits 2–3 "Forced fan" [MB p.13].
* All [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) writes so far were FC 06 (T23, T27, T28). The Modbus manual defines
  `R/W` as holding registers read with FC 03 and names no write function
  [MB p.5]; FC 06 and FC 16 are the standard Modbus writes, and nothing says
  which one [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) needs.

[INFERRED], not tested:

* [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) holds the display screen's state, and the controller overwrites it
  each cycle with its own request.
* The order matters: [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) is set by the unit itself at fan start and cleared at
  the end (T22), and every write so far came in the middle of a run. The display
  may set the fan speed and send the request in a fixed order (speed, then
  request, or request, then speed); a write during a run might also be taken
  over only when the request is sent again. Nothing in the evidence shows
  whether any of these orders is accepted, because none was tried (tests K1 to K3).
* A write path that works must act on one of the two request sources, on
  the time-band request, or on the forced-fan input, because no register
  carries a BMS fan request.

What else could act, each with a test below: a different function code on
[PM20](../doc/references/MODBUS_REGISTERS.md#pm20) (test H), another order of the write and the request (test K), the time-band route (test I), a voltage on FAN+ (test D), the
forced-fan input (test J; test J0 without wiring), the potentiometer
calibration (test L). The band is the lever that works today (tests A, B,
F, G refine it).

## Run order

Cheapest and least risky first. The letters are fixed labels, not an order.

| Order | Test | What | Effort / risk |
|-------|------|------|---------------|
| 1 | H | One FC 16 write to [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) | One write, no wiring |
| 2 | K | [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) written before, during the start of, or again with the request | Writes only; K3 repeats the request once |
| 3 | G | Lower through the maximum (pin the band, downward) | 2 EEPROM writes, pulls the fan down |
| 4 | B | Top of the band, [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) = [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) | 2 EEPROM writes |
| 5 | J0 | Forced fan from an unwired input | 2 [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) writes, up to 2 [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) writes; no wiring |
| 6 | E | INT run, read [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) | Reads only, needs summer and [PH27](../doc/references/MODBUS_REGISTERS.md#ph27) |
| 7 | A | Jump or ramp of a raised minimum | 2 EEPROM writes |
| 8 | F | Band written while idle | 2 EEPROM writes |
| 9 | I | Time-program route | Writes [PH03](../doc/references/MODBUS_REGISTERS.md#ph03), [FSC](../doc/references/MODBUS_REGISTERS.md#fsc) and a slot; can switch the unit off |
| 10 | L | Potentiometer calibration [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) | 2 EEPROM writes |
| 11 | D | 0–10 V on FAN+ | Wiring, no EEPROM write |
| 12 | J | Forced fan by a wired contact | Wiring, [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) and [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) EEPROM writes |

## Open questions

| # | Question | Source | Test |
|---|----------|--------|------|
| Q1 | Does an FC 16 write of 6000 to [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) change [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) or [639](../doc/references/MODBUS_REGISTERS.md#reg-639)? Expected: no effect | [INFERRED] | H |
| Q2 | Is [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) a 0–100 % request that is non-zero during INT? | [MB p.14; INFERRED] | E |
| Q3 | Does a raised [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) jump the output, or ramp it in [PF11](../doc/references/MODBUS_REGISTERS.md#pf11) steps? | [INFERRED] | A |
| Q4 | Does a [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) written while idle apply from the next fan start? | [INFERRED from T22] | F |
| Q5 | Is [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) = [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) accepted and does it give that speed? | [INFERRED] | B |
| Q6 | Does lowering [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) below the running speed pull the fan down, and does restoring [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) keep the lower speed? | [INFERRED from T24–T26] | G |
| Q7 | Does a time-band fan setpoint ([FSC](../doc/references/MODBUS_REGISTERS.md#fsc)) move [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) with [PH03](../doc/references/MODBUS_REGISTERS.md#ph03) on? | [HB 6.2; MB p.18; INFERRED for the interplay] | I |
| Q8 | Does 0–10 V on FAN+ raise [639](../doc/references/MODBUS_REGISTERS.md#reg-639) and [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) but not [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114)/[1614](../doc/references/MODBUS_REGISTERS.md#reg-1614)? | [HB 4.5, 6.2] | D |
| Q9 | Does a digital-input function 19/20 on [HA02](../doc/references/MODBUS_REGISTERS.md#ha02)/[HA03](../doc/references/MODBUS_REGISTERS.md#ha03) force the fan to [PF23](../doc/references/MODBUS_REGISTERS.md#pf23)? | [HB 5.3; INFERRED for analog terminals] | J |
| Q10 | Is a [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) write taken over when it comes before the request, while the fan is still waiting to start, or together with a repeated request? | [INFERRED from T22, T35] | K |
| Q11 | Does [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 19 with nothing wired set [258](../doc/references/MODBUS_REGISTERS.md#reg-258) bits 2–3 and drive the fan to [PF23](../doc/references/MODBUS_REGISTERS.md#pf23)? With or without a request, with the damper? | [HB 5.3; INFERRED from T31, T21] | J0 |
| Q12 | Does [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) change [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) or [639](../doc/references/MODBUS_REGISTERS.md#reg-639) with no signal on FAN+? Expected: no | [HB 5.3; INFERRED] | L |

## Tools and rules

* **Writes through Home Assistant** whenever an entity exists. The numbers
  below go through the integration's guards (ADR-0006, ADR-0012). Entities
  used (display names; the real entity id may carry the device prefix):

  | Entity | Register | Parameter |
  |--------|----------|-----------|
  | [*Fan min speed (dehumidify)*](../doc/entity-reference.md#fan-min-speed-dehumidify) | [1853](../doc/references/MODBUS_REGISTERS.md#reg-1853) | [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) |
  | [*Fan max speed (dehumidify)*](../doc/entity-reference.md#fan-max-speed-dehumidify) | [1647](../doc/references/MODBUS_REGISTERS.md#reg-1647) | [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) |
  | [*Fan min speed (cooling)*](../doc/entity-reference.md#fan-min-speed-cooling) | [1852](../doc/references/MODBUS_REGISTERS.md#reg-1852) | [PF27](../doc/references/MODBUS_REGISTERS.md#pf27) |
  | [*Fan max speed (cooling)*](../doc/entity-reference.md#fan-max-speed-cooling) | [1646](../doc/references/MODBUS_REGISTERS.md#reg-1646) | [PF09](../doc/references/MODBUS_REGISTERS.md#pf09) |
  | [*Dehumidify (Modbus)*](../doc/entity-reference.md#dehumidify-modbus) | [1140](../doc/references/MODBUS_REGISTERS.md#reg-1140) | DEU |
  | [*Integration request (cool in summer, heat in winter)*](../doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter) | [1139](../doc/references/MODBUS_REGISTERS.md#reg-1139) | INT |

* **Writes without an entity** (tests H, I, J, J0, L: [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) with FC 16, [PH03](../doc/references/MODBUS_REGISTERS.md#ph03),
  [FSC](../doc/references/MODBUS_REGISTERS.md#fsc), the time-program slot, [HA02](../doc/references/MODBUS_REGISTERS.md#ha02)/[HA03](../doc/references/MODBUS_REGISTERS.md#ha03), [PF23](../doc/references/MODBUS_REGISTERS.md#pf23), [PM88](../doc/references/MODBUS_REGISTERS.md#pm88)): write directly with a
  Modbus tool, because the integration cannot. Do it by hand, one write at a
  time, with Home Assistant idle (no write of its own is pending) so two
  masters never talk at once. Record each value before the write and
  restore it afterwards.
* **Reads:**
  * Home Assistant polls about once a minute: [*Supply fan output*](../doc/entity-reference.md#supply-fan-output)
    ([639](../doc/references/MODBUS_REGISTERS.md#reg-639)), [*Manual fan request (display)*](../doc/entity-reference.md#manual-fan-request-display) ([1114](../doc/references/MODBUS_REGISTERS.md#reg-1114)), [*Manual fan speed*](../doc/entity-reference.md#manual-fan-speed)
    ([1614](../doc/references/MODBUS_REGISTERS.md#reg-1614)), [*Supply fan status*](../doc/entity-reference.md#supply-fan-status) ([1119](../doc/references/MODBUS_REGISTERS.md#reg-1119)), [*Fan integration request*](../doc/entity-reference.md#fan-integration-request)
    ([1112](../doc/references/MODBUS_REGISTERS.md#reg-1112)).
  * For 1–5 s resolution, and for registers without an entity ([1113](../doc/references/MODBUS_REGISTERS.md#reg-1113), [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115),
    [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116)), run `python3 tests/diagnose_hrds.py <host> --no-snapshot --watch
    <seconds> --interval 1`. It is read-only and prints every change of
    the registers 380–390, 495–515 (so [507](../doc/references/MODBUS_REGISTERS.md#reg-507)), 630–645, 768–775 and 1100–1140, of
    [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) and of the fan band (1644–1647, [1852](../doc/references/MODBUS_REGISTERS.md#reg-1852), [1853](../doc/references/MODBUS_REGISTERS.md#reg-1853)). It does not
    watch [258](../doc/references/MODBUS_REGISTERS.md#reg-258), 1595–1597, [1660](../doc/references/MODBUS_REGISTERS.md#reg-1660), [1779](../doc/references/MODBUS_REGISTERS.md#reg-1779) or [1805](../doc/references/MODBUS_REGISTERS.md#reg-1805): read those with a Modbus tool,
    or run the script once without `--no-snapshot`, which reads 255–260 and
    1590–1900 once.
  * Keep each request at 10 registers or fewer (T9): read [639](../doc/references/MODBUS_REGISTERS.md#reg-639), then
    1112–1119, then [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) and [1853](../doc/references/MODBUS_REGISTERS.md#reg-1853).
  * Never write from that script.
* **Preconditions, all set by the owner; the integration never sets them:**
  * the unit is ON;
  * [PH02](../doc/references/MODBUS_REGISTERS.md#ph02)/[PH28](../doc/references/MODBUS_REGISTERS.md#ph28) (and [PH27](../doc/references/MODBUS_REGISTERS.md#ph27) for test E) are on;
  * the gate [*Allow operational requests*](../doc/entity-reference.md#allow-operational-requests) is on;
  * the MVHR runs at 150 m³/h or more;
  * the season is summer.
* **EEPROM:** [PF28](../doc/references/MODBUS_REGISTERS.md#pf28)/[PF10](../doc/references/MODBUS_REGISTERS.md#pf10)/[PF27](../doc/references/MODBUS_REGISTERS.md#pf27)/[PF09](../doc/references/MODBUS_REGISTERS.md#pf09) are EEPROM parameters (ADR-0023), and so are
  [HA02](../doc/references/MODBUS_REGISTERS.md#ha02)/[HA03](../doc/references/MODBUS_REGISTERS.md#ha03), [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) and [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) [INFERRED]. The band tests (A, B,
  F, G) need about 8 parameter writes, tests I, J, J0 and L a few more. Count
  them, and do not loop or automate them.
* **Before the first write,** record [1853](../doc/references/MODBUS_REGISTERS.md#reg-1853), [1647](../doc/references/MODBUS_REGISTERS.md#reg-1647), [1852](../doc/references/MODBUS_REGISTERS.md#reg-1852), [1646](../doc/references/MODBUS_REGISTERS.md#reg-1646) and [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614).
  Restore them at the end. Shipped values: 5000, 8500, 5000, 8500 (§15).
* **Never set a minimum above its maximum.** What the unit does then is
  unknown.

## Tests

### H. FC 16 write to PM20 (Q1)

Needs no wiring and one write. Not through Home Assistant.

1. During a DEU run with the band at 50–85 %, start the 1–2 s read loop on
   [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639), and read [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) once.
2. Write 6000 (60 %, two implied decimals [MB p.7]) to [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) with one FC 16
   (write multiple registers) request of one register.
3. Read [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for 1 minute.

Expected [INFERRED]: no effect, as with FC 06 (T23, T28). Record the response
(acknowledged or an exception), and how long [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) held 60 if it did. If
[639](../doc/references/MODBUS_REGISTERS.md#reg-639) moves to 60, stop and report: the integration would then need a write
path for [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) with FC 16.

### K. Order of the PM20 write and the request (Q10)

The unit sets [PM20](../doc/references/MODBUS_REGISTERS.md#pm20) itself at fan start (0 to the band minimum) and clears it
at the end (T22). All writes so far came in the middle of a run (T23, T27,
T28). The display may work in a fixed order, so try each order. Not through
Home Assistant; with the band at 50–85 % and one write of 6000 (60 %, two
implied decimals [MB p.7]) per step. Run each step with FC 06 and, if it was
refused, once with FC 16. Keep the read loop at 0.5 s on [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [639](../doc/references/MODBUS_REGISTERS.md#reg-639),
[1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) and [1134](../doc/references/MODBUS_REGISTERS.md#reg-1134) for the whole test.

**K1. Write first, then the request.**
1. With no request and the fan off, write 6000 to [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614). Record the response
   (acknowledged or an exception) and read [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) and [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) for 1 minute.
2. Start DEU ([*Dehumidify (Modbus)*](../doc/entity-reference.md#dehumidify-modbus) on). Watch [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) at
   the fan start.

Expected [INFERRED]: the write is refused or cleared, and the fan starts at the
band minimum (T22). If [639](../doc/references/MODBUS_REGISTERS.md#reg-639) starts at 60, the order is the lever: stop and report.

**K2. Request first, then the write before the fan runs.**
1. Start DEU. The fan starts 29 to 120 s after the damper opens (T35, PS01 as
   shipped 90 s), and until then [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) reads OFF and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) 0.
2. As soon as [1134](../doc/references/MODBUS_REGISTERS.md#reg-1134) reads on and [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) is still OFF, write 6000 to [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614).
3. Watch [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) through the fan start.

Expected [INFERRED]: as K1. If the fan starts at 60, record how late the write
could be and still count.

**K3. A write in the middle of a run, followed by the request again.**
1. During a DEU run with the fan at 50, write 6000 to [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614). Expected: no effect
   (T23). Note the response.
2. Within 2 s, write 1 to [1140](../doc/references/MODBUS_REGISTERS.md#reg-1140) again (the request is already on, so there is no
   edge). Read [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for 1 minute.
3. If still nothing: write 6000 to [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) once more, then write 0 and 1 to
   [1140](../doc/references/MODBUS_REGISTERS.md#reg-1140) about 1 s apart. The unit mirrors requests late (T39, 12 to 30 s), so
   the pulse may not register at all; the unit's compressor protection times
   apply [HB 6.3]. Do this once, not in a loop.

Expected [INFERRED]: no effect. The repeated 1 is a write of the value it already
holds, and the unit may even ignore it.

Record what each step returned, and which step, if any, made [639](../doc/references/MODBUS_REGISTERS.md#reg-639) leave
the band minimum.

### E. INT request (Q2)

1. With [PG02](../doc/references/MODBUS_REGISTERS.md#pg02) = 1, [PH27](../doc/references/MODBUS_REGISTERS.md#ph27) on and summer, start INT
   ([*Integration request (cool in summer, heat in winter)*](../doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter) on). Leave DEU off.
2. Log [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112), [1113](../doc/references/MODBUS_REGISTERS.md#reg-1113), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115), [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for 10 minutes.
3. Read [PF31](../doc/references/MODBUS_REGISTERS.md#pf31) ([1856](../doc/references/MODBUS_REGISTERS.md#reg-1856); the reference unit ships it at 1), [PF27](../doc/references/MODBUS_REGISTERS.md#pf27) and [PF09](../doc/references/MODBUS_REGISTERS.md#pf09).

Expected [INFERRED]: [1112](../doc/references/MODBUS_REGISTERS.md#reg-1112) reads a percentage inside [PF27](../doc/references/MODBUS_REGISTERS.md#pf27)..[PF09](../doc/references/MODBUS_REGISTERS.md#pf09), not only 0 or 1.

### A. A raised minimum: jump or ramp (Q3)

Raising and lowering [PF28](../doc/references/MODBUS_REGISTERS.md#pf28) are proven (T24–T26); what remains is the 5 s
log of a raise.

1. Start DEU ([*Dehumidify (Modbus)*](../doc/entity-reference.md#dehumidify-modbus) on). Wait until [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) = ON and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) is
   steady (about 2 min after the damper opens).
2. Start the 5 s read loop: [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614), [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116), [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119).
3. With the fan at 50, set [*Fan min speed (dehumidify)*](../doc/entity-reference.md#fan-min-speed-dehumidify) to 65. Log for
   2 minutes.
4. Set it back to 50. Log for 2 minutes.

Expected: [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) reach 65. After step 4 all three stay at 65
until the request ends (T26).

| [639](../doc/references/MODBUS_REGISTERS.md#reg-639) after step 3 | Meaning |
|------------------|---------|
| Reads 65 at once | The band is a live lever |
| Steps up by [PF11](../doc/references/MODBUS_REGISTERS.md#pf11) (7 %) every few seconds | Ramp. Note the interval |
| Stays 50 | Contradicts T25. Stop and report |

### F. Band written while idle (Q4)

1. With no request, set [*Fan min speed (dehumidify)*](../doc/entity-reference.md#fan-min-speed-dehumidify) to 60.
2. Start DEU and read [639](../doc/references/MODBUS_REGISTERS.md#reg-639) at fan start.
3. Restore 50.

Expected: [639](../doc/references/MODBUS_REGISTERS.md#reg-639) reads 60 from the start, since the request starts at 0 and is
clamped up to the minimum (T22).

### B. Top of the band (Q5)

During a run:

1. Set [*Fan min speed (dehumidify)*](../doc/entity-reference.md#fan-min-speed-dehumidify) to 85 (= [PF10](../doc/references/MODBUS_REGISTERS.md#pf10)). Log [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for
   1 minute.
2. Set it back to 50.

Expected: [639](../doc/references/MODBUS_REGISTERS.md#reg-639) reads 85 and stays there after step 2 (T26). Use test G to bring
it down. Do not write a minimum above 85.

### G. Lower through the maximum (Q6)

1. During a run with the fan above 50 (for example at 55 after a test-A
   raise), start the 5 s read loop on [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614).
2. Set [*Fan max speed (dehumidify)*](../doc/entity-reference.md#fan-max-speed-dehumidify) ([PF10](../doc/references/MODBUS_REGISTERS.md#pf10)) to 52. Log for 1 minute.
   Expected: [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) and [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) read 52.
3. Set [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) back to 85. Log for 1 minute. Expected: they stay at 52.
4. Never set [PF10](../doc/references/MODBUS_REGISTERS.md#pf10) below [PF28](../doc/references/MODBUS_REGISTERS.md#pf28).

This decides whether any speed within the band can be set with two band
writes (method 1 of *How to scale the fan*), or only a raise (`plans/todo.md`, *Speed control through the band*).

### I. Time-program route (Q7)

No wiring. The unit can switch itself off by schedule (`sm_UnitStatus` 3,
[1104](../doc/references/MODBUS_REGISTERS.md#reg-1104)), so keep the owner at hand and the slot short.

1. Record [PH03](../doc/references/MODBUS_REGISTERS.md#ph03) ([1779](../doc/references/MODBUS_REGISTERS.md#reg-1779)), [FSC](../doc/references/MODBUS_REGISTERS.md#fsc) ([1595](../doc/references/MODBUS_REGISTERS.md#reg-1595)), [FSE](../doc/references/MODBUS_REGISTERS.md#fse), [FSN](../doc/references/MODBUS_REGISTERS.md#fsn) and the F1..F4 slot
   registers of today's weekday ([MODBUS_REGISTERS.md §17.2](../doc/references/MODBUS_REGISTERS.md#172-time-programs)).
2. Start DEU and wait for a steady fan at the band minimum. Start the 5 s
   read loop on [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115), [1106](../doc/references/MODBUS_REGISTERS.md#reg-1106), [1104](../doc/references/MODBUS_REGISTERS.md#reg-1104).
3. Write [FSC](../doc/references/MODBUS_REGISTERS.md#fsc) to a value inside the band (for example 6000), set one slot of
   today to mode 2 (Comfort) starting a few minutes ahead, then write
   [PH03](../doc/references/MODBUS_REGISTERS.md#ph03) = 1.
4. Watch [1106](../doc/references/MODBUS_REGISTERS.md#reg-1106) and [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115) until the slot starts, then [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for 5 minutes.
5. Restore the recorded [PH03](../doc/references/MODBUS_REGISTERS.md#ph03) first, then the slot and [FSC](../doc/references/MODBUS_REGISTERS.md#fsc).

Expected [INFERRED]: [1115](../doc/references/MODBUS_REGISTERS.md#reg-1115) follows [FSC](../doc/references/MODBUS_REGISTERS.md#fsc) in the Comfort slot and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) follows
[1115](../doc/references/MODBUS_REGISTERS.md#reg-1115) within the band, while [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114) is no longer the request that counts
(manual control is active only without time programs [HB 6.2]). Record
whether the slot mode 1 (OFF) or the time program as a whole switches the
unit off, and how the fan behaves outside the slots.

### L. Potentiometer calibration (Q12)

1. During a DEU run with a steady fan, record [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) ([1624](../doc/references/MODBUS_REGISTERS.md#reg-1624)), [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116), [507](../doc/references/MODBUS_REGISTERS.md#reg-507), [639](../doc/references/MODBUS_REGISTERS.md#reg-639).
2. Write [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) = 10. Read [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116), [507](../doc/references/MODBUS_REGISTERS.md#reg-507), [639](../doc/references/MODBUS_REGISTERS.md#reg-639) for 2 minutes.
3. Restore [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) = 0.

Expected [INFERRED]: no change, because [507](../doc/references/MODBUS_REGISTERS.md#reg-507) reads `0x7FFA` with nothing on
FAN+ (T3). A change would make [PM88](../doc/references/MODBUS_REGISTERS.md#pm88) a Modbus lever of up to 10 %.

### D. 0–10 V on FAN+ (Q8)

The fan has a dedicated input, AI1 ([HA01](../doc/references/MODBUS_REGISTERS.md#ha01) = 58, T21), on the display terminal
block: FAN+ and FAN−, with a 12 V output for a potentiometer [HB 4.5].
0 V is the band minimum, 10 V the band maximum, linear, and the higher of
this and the manual request wins; a signal above 10 V disables it [HB 4.5,
6.2]. No EEPROM write is needed. The owner wires it; an agent does not.

* **Source:** a real voltage source into FAN+ (for example a Shelly dimmer
  with a 0–10 V output, or a 10 kΩ linear potentiometer on the 12 V
  output with a series resistor [HB 4.5]). Many "0/1–10 V" dimmers only
  sink current and give no voltage: check the model before wiring.
* **Risk:** alarm AL36 (fan potentiometer faulty or disconnected) disables
  the controls that depend on it [MB p.9]. It is a risk if the input is
  later left open; keep the source connected, and read the alarm bits
  (768–775) during the test.

1. Start DEU and wait for a steady fan at the band minimum (50 % with the
   band at 50–85).
2. Log [507](../doc/references/MODBUS_REGISTERS.md#reg-507), [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116), [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114), [1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) every 1–5 s.
3. Step the voltage: 0, 2.5, 5, 7.5, 10 V, then back to 0, about 1 minute
   each. If the source allows it, try a value above 10 V once at the end,
   within the source's rating.

Expected:
* [507](../doc/references/MODBUS_REGISTERS.md#reg-507) leaves its no-signal value `0x7FFA` [T3].
* [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) rises with the voltage, and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) rises with it to about 67.5 % at 5 V
  (the middle of 50–85).
* [1114](../doc/references/MODBUS_REGISTERS.md#reg-1114)/[1614](../doc/references/MODBUS_REGISTERS.md#reg-1614) stay at 50 [HB 6.2].
* [INFERRED from T22, T24–T26]: the unit's manual request is at least the
  band minimum, so the signal can raise the fan above the minimum but not
  below it. At 0 V and 2.5 V [639](../doc/references/MODBUS_REGISTERS.md#reg-639) then stays at 50.

Record: [639](../doc/references/MODBUS_REGISTERS.md#reg-639) and [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) per step; whether [1116](../doc/references/MODBUS_REGISTERS.md#reg-1116) reads the raw percentage
(about 50 at 5 V) or the value scaled into the band (about 67.5); the
behaviour at 0 V and above 10 V; whether any alarm bit appears.

### J0. Forced fan from an unwired input (Q11)

No wiring. Two writes to [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) (an I/O allocation, EEPROM) and up to two to
[PF23](../doc/references/MODBUS_REGISTERS.md#pf23). AI2 (M2) is unused on the reference unit ([HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 0, T21); nothing is
connected to it, so its contact reads open.

1. Record [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) ([1805](../doc/references/MODBUS_REGISTERS.md#reg-1805)), [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) ([1660](../doc/references/MODBUS_REGISTERS.md#reg-1660)) and [258](../doc/references/MODBUS_REGISTERS.md#reg-258). Unit ON, no request.
2. Write [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 20 (NO: open = inactive). Read [258](../doc/references/MODBUS_REGISTERS.md#reg-258), [768](../doc/references/MODBUS_REGISTERS.md#reg-768)–[770](../doc/references/MODBUS_REGISTERS.md#reg-770) (alarms):
   expected bits 2–3 = 0, no alarm.
3. Write [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 19 (NC: open = active). Read [258](../doc/references/MODBUS_REGISTERS.md#reg-258), [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119), [639](../doc/references/MODBUS_REGISTERS.md#reg-639), [1134](../doc/references/MODBUS_REGISTERS.md#reg-1134)
   at 1–5 s for 2 minutes. Records whether a forced fan runs without a
   request and whether the damper opens.
4. Start DEU; wait for a steady fan. Read [639](../doc/references/MODBUS_REGISTERS.md#reg-639): [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) (70 % handbook
   default), the band, or the higher of the two?
5. Write [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) once to another value inside the band; read [639](../doc/references/MODBUS_REGISTERS.md#reg-639).
6. Restore [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) and [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 0 (first [HA02](../doc/references/MODBUS_REGISTERS.md#ha02), so the fan is no longer forced),
   end DEU.

If step 3 runs the fan in standby, stop there and restore [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 0.

### J. Forced fan by a digital input (Q9)

Wiring plus EEPROM writes; run it last. The forced speed [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) applies only
while an input with function 19 or 20 is active [HB 5.3].

* **Which input:** [HA02](../doc/references/MODBUS_REGISTERS.md#ha02)/[HA03](../doc/references/MODBUS_REGISTERS.md#ha03) (AI2/AI3, terminals M2/M3) accept codes 0–60
  [HB 5.3], so 19 or 20 is allowed by range. Whether it works on those
  analog terminals is untested [INFERRED]. On the reference unit M2/M3 are
  unused ([HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = [HA03](../doc/references/MODBUS_REGISTERS.md#ha03) = 0, T21). Do not reuse the others: M6/M7 are the
  DEU/INT contacts ([HA06](../doc/references/MODBUS_REGISTERS.md#ha06) = 6, [HA07](../doc/references/MODBUS_REGISTERS.md#ha07) = 8), M8 is remote on/off ([HB03](../doc/references/MODBUS_REGISTERS.md#hb03) = 2),
  HV1/HV2 are the pressure switches ([HB01](../doc/references/MODBUS_REGISTERS.md#hb01) = 27, [HB02](../doc/references/MODBUS_REGISTERS.md#hb02) = 26), and M9 is the season
  input ([HB04](../doc/references/MODBUS_REGISTERS.md#hb04) = 4; no contact is wired, the season is switched over Modbus,
  T31, so M9 must not get another function). The expansion inputs
  ([HB05](../doc/references/MODBUS_REGISTERS.md#hb05)–[HB07](../doc/references/MODBUS_REGISTERS.md#hb07), [HA08](../doc/references/MODBUS_REGISTERS.md#ha08)…) belong to an optional expansion board
  ([PG05](../doc/references/MODBUS_REGISTERS.md#pg05) "Enable expansion", off) that is not fitted.
* **Contact:** a potential-free relay contact (a Shelly or similar) between
  the terminal and its common. Check the wiring diagram in the technical
  handbook PDF for M2/M3 and the common terminal; the text does not
  describe the type of these inputs.

1. Record [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) ([1805](../doc/references/MODBUS_REGISTERS.md#reg-1805)) and [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) ([1660](../doc/references/MODBUS_REGISTERS.md#reg-1660)). Start DEU and wait for a steady fan.
2. Write [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 19 (normally closed) or 20 (normally open), matching the
   relay's rest state. Watch for AL28 and other alarms: [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) is the room
   probe input, and a probe code with nothing wired raises AL28.
3. Change the contact. Read [258](../doc/references/MODBUS_REGISTERS.md#reg-258) bits 2–3, [1119](../doc/references/MODBUS_REGISTERS.md#reg-1119) and [639](../doc/references/MODBUS_REGISTERS.md#reg-639), at 1–5 s, for
   2 minutes.
4. Release the contact and read the same registers again.
5. Write [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) to a new value inside the band (an EEPROM write, so only once),
   close the contact again and read [639](../doc/references/MODBUS_REGISTERS.md#reg-639).
6. Restore [PF23](../doc/references/MODBUS_REGISTERS.md#pf23) and [HA02](../doc/references/MODBUS_REGISTERS.md#ha02) = 0.

Expected [INFERRED]: [258](../doc/references/MODBUS_REGISTERS.md#reg-258) bits 2–3 change with the contact and [639](../doc/references/MODBUS_REGISTERS.md#reg-639) goes to
[PF23](../doc/references/MODBUS_REGISTERS.md#pf23) (70 % is the handbook default). Unknown, to record: whether the forced
fan also needs a DEU or INT request, and whether it opens the damper.

## Recording the results

* For each test, add a `T` row to `UNIT_BEHAVIOUR.md` §13, starting at T42.
  Replace the `[INFERRED]` tags it settles in §3.5, §9.1 and §14.
* Put a run file in `tests/devices/runs/`, named
  `hrds_30+_fan_speed_tests_<date>.json`. Use the same layout as the two run
  files there: `_about`, `timeline`, `findings`, `open`.
* `plans/todo.md`:
  * tick the items these tests answer;
  * add the result to *Speed control through the band*;
  * a code change is decided there and recorded as an ADR that supersedes
    ADR-0034 (`/adr supersede`).
* Do not change integration code in the same PR as the evidence.
