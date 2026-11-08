# Evaporator setpoint per request: implementation plan

The unit has one evaporator setpoint, [PU11](../doc/references/MODBUS_REGISTERS.md#pu11), for both requests. The vendor
suggests a low setpoint for a dehumidify (DEU) request and a higher one for
integration (INT) cooling, never above 12 °C
([`UNIT_BEHAVIOUR.md` §2.1](../doc/references/UNIT_BEHAVIOUR.md#21-air-path)). The integration should set PU11 to match the
request, as an option the user turns on.

## Behaviour

* **Off by default.** A switch on the setup device turns the feature on. It is
  kept across restarts, like [*Allow operational requests*](../doc/entity-reference.md#allow-operational-requests).
* **Two settings**, two numbers on the setup device, kept across restarts:
  the setpoint for dehumidifying (default 6.0 °C) and for cooling
  (default 11.0 °C), each 0–12 °C. They are the integration's own policy, not
  a copy of a register; PU11 itself keeps showing the unit's read-back.
* **When it writes.** Only when Home Assistant raises a request, in the same
  service call, before the request itself:

  | Request raised from Home Assistant | PU11 is set to |
  |------------------------------------|----------------|
  | DEU (climate *Dry*, [*Dehumidify request*](../doc/entity-reference.md#dehumidify-request) on) | the dehumidify setting |
  | INT in summer (climate *Cool*, the [integration request](../doc/entity-reference.md#integration-request-cool-in-summer-heat-in-winter) on) | the cooling setting |
  | INT in winter (heating, no compressor) | nothing |
  | Request switched off, or raised by the display or the terminals | nothing |

* **Only when it differs.** `_write_registers` already reads the register
  first and skips a value the unit holds (ADR-0023), so PU11 is written only
  when the request type changes. A user does not switch between DEU and INT
  back and forth, so this is a few writes a season.
* **Failure.** If the PU11 write fails, log a warning and still send the
  request: the request is what the user asked for.

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
  request has passed `check_write_allowed`.

Record this as a new ADR (`/adr new`) before coding, so `/adr check` knows the
write is intended.

## Steps

1. ADR: setpoint per request, as above.
2. `const.py`: the switch and the two numbers (integration-held, restored,
   setup device, in `SETUP_KEYS`), with en/de translations.
3. `__init__.py`: in the request path (`write_entity_value` for the DEU and
   INT requests and the climate modes), after `check_write_allowed`, write
   PU11 through `_write_registers` when the switch is on.
4. `doc/entity-reference.md`: the three entities under the setup device.
   README: a short section under "Using the integration". CHANGELOG entry.
5. Tests (`tests/ha`, simulator):
   * DEU on with the feature on: PU11 becomes the dehumidify setting, then the
     request is written.
   * Same request again: no second PU11 write.
   * INT in summer: the cooling setting. INT in winter: no PU11 write.
   * Feature off: PU11 is never written.
   * PU11 write fails: warning, and the request is still written.
   * A request refused by `check_write_allowed`: no PU11 write.

## Open

* When both requests are on (for example INT with [PU05](../doc/references/MODBUS_REGISTERS.md#pu05) = 1 also raises DEU),
  which setting wins? Proposal: INT in summer wins, because the cooling
  setpoint protects the ducts.
