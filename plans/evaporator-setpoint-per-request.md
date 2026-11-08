# Evaporator setpoint per request: implementation plan

The unit has one evaporator setpoint, [PU11](../doc/references/MODBUS_REGISTERS.md#pu11), for both requests. The vendor
suggests a low setpoint for a dehumidify (DEU) request and a higher one for
integration (INT), never above 12 °C, and INT not below 8 °C
([`UNIT_BEHAVIOUR.md` §2.1](../doc/references/UNIT_BEHAVIOUR.md#21-air-path)). The integration should set PU11 to match the
request, as an option the user turns on, and refuse INT while PU11 is below
8 °C.

## Behaviour

* **Off by default.** A switch on the setup device turns the feature on. It is
  kept across restarts, like [*Allow operational requests*](../doc/entity-reference.md#allow-operational-requests).
* **Two settings**, two numbers on the setup device, kept across restarts:
  the setpoint for dehumidifying (default 6.0 °C, 0–12 °C) and for
  integration (default 11.0 °C, 8–12 °C). They are the integration's own
  policy, not a copy of a register; PU11 itself keeps showing the unit's
  read-back.
* **When it writes.** Only when Home Assistant raises a request (see Scope), in the same
  service call, before the request itself:

  | Request raised from Home Assistant | PU11 is set to |
  |------------------------------------|----------------|
  | DEU (climate *Dry*, [*Dehumidify request*](../doc/entity-reference.md#dehumidify-request) on), INT off | the dehumidify setting |
  | INT, summer or winter (climate *Cool* or *Heat*, the [integration request](../doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter) on) | the integration setting |
  | DEU while INT is on | nothing: INT's setting stays |
  | Request switched off, or raised by the display or the terminals | nothing |

  INT's setting wins whenever INT is on: it is the higher one, INT implies
  dehumidifying in summer, and in winter the unit heats, where a low setpoint
  never helps.
* **Only when it differs.** `_write_registers` already reads the register
  first and skips a value the unit holds (ADR-0023), so PU11 is written only
  when the request type changes. A user does not switch between DEU and INT
  back and forth, so this is a few writes a season.
* **INT guard (always, with or without the feature).** An INT request from
  Home Assistant is refused while PU11 reads below 8 °C, or is unknown. With
  the feature on, the guard checks PU11 after its write, so:
  * PU11 write succeeds: INT is sent.
  * PU11 write fails and PU11 still reads 8 °C or more: warning, INT is sent.
  * PU11 write fails and PU11 reads below 8 °C: INT is refused, with the
    reason.
* **DEU failure.** If the PU11 write for DEU fails, log a warning and still
  send DEU: the request is what the user asked for.

## Why the ADRs allow it

* **ADR-0010 (only PH01/HA00 written unasked):** PU11 is written only as part
  of a request the user raises, with the feature switched on, so it is not
  written unasked.
* **ADR-0023 (write only what changes):** the write is skipped when PU11
  already holds the value, and it happens only when the request type changes.
  It is not a periodic write.
* **ADR-0034 (no option shadows a register):** the two settings say what to
  write, not what PU11 holds; PU11 stays the unit's read-back.
* **ADR-0012, ADR-0013, ADR-0014:** the PU11 write happens only after the
  request has passed `check_write_allowed`. The 8 °C rule is a new guard in
  `check_write_allowed` for INT, next to the enables, season and brine guard.

Record this as a new ADR (`/adr new`) before coding: the PU11 write with a
request, and the 8 °C INT guard. Then `/adr check` knows both are intended.

## Steps

1. ADR: setpoint per request and the INT guard, as above.
2. `const.py`: the switch and the two numbers (integration-held, restored,
   setup device, in `SETUP_KEYS`), with en/de translations; the 8 °C limit as
   a constant.
3. `__init__.py`:
   * `check_write_allowed`: refuse INT on while PU11 is below 8 °C or
     unknown.
   * Request path (`write_entity_value` for DEU, INT and the climate modes):
     after the other guards, when the switch is on, write PU11 through
     `_write_registers`, then apply the INT guard to the read-back.
4. `doc/entity-reference.md`: the three entities under the setup device, and
   the INT guard in the INT row. README: a short section under "Using the
   integration", and the guard where INT is described. CHANGELOG entry.
5. Tests (`tests/ha`, simulator):
   * DEU on, feature on: PU11 becomes the dehumidify setting, then DEU is
     written. Same request again: no second PU11 write.
   * INT on (summer and winter): PU11 becomes the integration setting, then
     INT.
   * DEU on while INT is on: PU11 is not lowered.
   * Feature off: PU11 is never written; INT is refused while PU11 < 8 °C.
   * PU11 write fails: DEU still sent; INT sent if PU11 ≥ 8 °C, refused if
     below.
   * A request refused by another guard: no PU11 write.

## Scope

PU11 is checked and set only when Home Assistant raises a DEU or INT request.
Nothing else reads it as a trigger or writes it:

* Switching a request off is not a request: PU11 stays as it is, also when
  INT goes off and DEU stays on.
* A change to PU11 by anyone else (display, BMS, installer device) is not
  reacted to; the next request from Home Assistant checks it.
* Requests raised on the display or the terminals are the unit's own
  business; the integration does not step in.
