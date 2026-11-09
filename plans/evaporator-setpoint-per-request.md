# Evaporator setpoint per request: implementation plan

The unit has one evaporator setpoint, [PU11](../doc/references/MODBUS_REGISTERS.md#pu11), for both requests. The vendor
suggests a low setpoint for a dehumidify (DEU) request and a higher one for
integration (INT), and INT not below 8 °C
([`UNIT_BEHAVIOUR.md` §2.1](../doc/references/UNIT_BEHAVIOUR.md#21-air-path)). Agreed with the vendor: PU11 is
never set outside 5 to 12 °C, so the compressor is not brought into
unpleasant operating conditions. The integration sets PU11 to match the
request and refuses INT while PU11 is below 8 °C. All of it is an option the
user turns on: a newer HRDS that no longer needs it runs without it.

## Behaviour

* **Optional, off by default.** A switch on the setup device turns the whole
  feature on: the PU11 writes and the INT guard. With it off the integration
  never touches PU11 and adds no guard, so a unit that does not need it (a
  newer HRDS) is not affected. It is kept across restarts, like
  [*Allow operational requests*](../doc/entity-reference.md#allow-operational-requests).
* **Two settings**, two numbers on the setup device, kept across restarts:
  the setpoint when only DEU runs (default 6.0 °C, range 5–12 °C) and when
  INT runs (default 11.0 °C, range 8–12 °C). They are the integration's own
  policy, not a copy of a register; PU11 itself keeps showing the unit's
  read-back.
* **The ranges are checked.** The number entities enforce the range. The
  value is checked again before every PU11 write, so a stored value outside
  its range (for example from an older version) is never written: the
  default is used and a warning is logged.
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
* **INT guard (with the feature on).** An INT request from Home Assistant is
  refused while PU11 reads below 8 °C, or is unknown. The guard checks PU11
  after the write above, so:
  * PU11 write succeeds: INT is sent.
  * PU11 write fails and PU11 still reads 8 °C or more: warning, INT is sent.
  * PU11 write fails and PU11 reads below 8 °C: INT is refused, with the
    reason.
* **DEU failure.** If the PU11 write for DEU fails, log a warning and still
  send DEU: the request is what the user asked for.

## Why the ADRs allow it

* **ADR-0010 (only PH01/HA00 written unasked):** PU11 is written only as part
  of a request the user raises, with the feature switched on, so it is not
  written unasked. The ranges mean the written value is always 5 to 12 °C.
* **ADR-0023 (write only what changes):** the write is skipped when PU11
  already holds the value, and it happens only when the request type changes.
  It is not a periodic write.
* **ADR-0034 (no option shadows a register):** the two settings say what to
  write, not what PU11 holds; PU11 stays the unit's read-back.
* **ADR-0012, ADR-0013, ADR-0014:** the PU11 write happens only after the
  request has passed `check_write_allowed`. The 8 °C rule is a new guard in
  `check_write_allowed` for INT, next to the enables, season and brine guard;
  it applies only when the feature is on.

Record this as a new ADR (`/adr new`) before coding: the PU11 write with a
request, and the 8 °C INT guard. Then `/adr check` knows both are intended.

## Steps

1. ADR: setpoint per request and the INT guard, as above.
2. `const.py`: the switch and the two numbers (integration-held, restored,
   setup device, in `SETUP_KEYS`), with en/de translations; the 8 °C limit as
   a constant.
3. `__init__.py`:
   * `check_write_allowed`: with the switch on, refuse INT on while PU11 is
     below 8 °C or unknown.
   * Request path (`write_entity_value` for DEU, INT and the climate modes):
     after the other guards, when the switch is on, check the setting's range,
     write PU11 through `_write_registers`, then apply the INT guard to the
     read-back.
4. `installer_params.py`: the PU11 installer number allows 5–12 °C (now
   0–12), the same limits as the two settings. `doc/entity-reference.md`: the
   three entities under the setup device, the INT guard in the INT row, and
   the PU11 range. README: a short section under "Using the
   integration", and the guard where INT is described. CHANGELOG entry.
5. Tests (`tests/ha`, simulator):
   * DEU on, feature on: PU11 becomes the dehumidify setting, then DEU is
     written. Same request again: no second PU11 write.
   * INT on (summer and winter): PU11 becomes the integration setting, then
     INT.
   * DEU on while INT is on: PU11 is not lowered.
   * Feature off: PU11 is never written and INT is not refused for PU11.
   * Ranges: a setting outside its range is rejected by the entity; a stored
     value outside it is not written (default used, warning logged).
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
