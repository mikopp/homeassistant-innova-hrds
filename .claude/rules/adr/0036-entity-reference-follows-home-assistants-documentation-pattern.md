---
status: accepted
date: 2026-10-31
decision-makers: mikopp
topics: [entities, docs]
supersedes: [ADR-0030]
paths:
  - "custom_components/innova_hrds/const.py"
  - "custom_components/innova_hrds/entity_common.py"
  - "custom_components/innova_hrds/installer_params.py"
  - "custom_components/innova_hrds/translations/*.json"
  - "doc/entity-reference.md"
---

# ADR-0036: The entity reference follows Home Assistant's documentation pattern and is checked

## Decision

- `doc/entity-reference.md` MUST be the only place that lists entities. The
  README, `CLAUDE.md` and other docs MUST link to it and MUST NOT restate it
  (ADR-0027); they name an entity by its English name, an entity ID only in a
  YAML example. Every entity name in italics in another Markdown file MUST be
  a link to that entity's item in the reference (`[*Setup check*](…/entity-reference.md#setup-check)`),
  so each item carries an anchor `<a id="setup-check"></a>` (the name in lower
  case, runs of other characters as one hyphen). Not in `CLAUDE.md`, the ADRs
  (ADR-0027: no links in agent-loaded files), the reference itself and released
  CHANGELOG sections.
- It MUST follow Home Assistant's "Supported functionality" pattern
  (`docs-supported-functions`): `## <device>` (HRDS+, HRDS+ setup, HRDS+
  installer, each saying why it exists and is separate, ADR-0016, ADR-0017),
  `### <platform>` (Binary sensors, Buttons, Climate, Numbers, Selects,
  Sensors, Switches), then one item per entity:
  `- <a id="slug"></a>**<English name>**: <description>` with sub-items `**Available for**`
  (when not all units), `**Options**` (selects) and `**Remarks**`.
- The entities `entity_category_for` makes diagnostic MUST be listed under a
  `### Diagnostic` section of their device (after the platform sections), not
  under their platform. The Modbus register MUST end the description in
  parentheses, linked to `MODBUS_REGISTERS.md` (`([1121](…))`, `([768](…), bit
  10)`, `(derived from [1134](…) and [1119](…))`), merged with the parameter
  code when the text names it (`([PU01](…), [1586](…))`). `**Remarks**` only
  say what else matters and MUST say "Configuration entity" for a configuration
  entity.
- It MUST use Home Assistant's terms (device, entity, name, platform) and MUST
  NOT name repository internals (keys, entity IDs, unique ids, ADRs, scripts,
  source files, evidence-log tags).
- Installer parameters (`INSTALLER_KEYS`) MUST NOT be listed one by one;
  `MODBUS_REGISTERS.md` §16 lists them.
- A change that adds, removes, renames, regroups or moves an entity, or changes
  its English name, register or what it shows, MUST update the reference in the
  same commit.
- `tests/wiring_check.py` (`check_entity_reference`) MUST fail when an entity's
  English name from `translations/en.json` is missing, unknown, duplicated, on
  the wrong device or platform heading, a diagnostic entity is outside
  `### Diagnostic`, or a configuration entity lacks its remark, when an item lacks its anchor, when an entity
  name in italics outside the reference is not a link, and when the README holds
  entity items.

## Context

ADR-0030 keyed the reference on `platform.key`, which users never see; they
read `switch.dehumidify` as an entity ID. A survey of home-assistant.io pages
(Husqvarna Automower, Tessie, AirGradient, BSB-LAN, Shelly, Enphase) and the
contributor guidance shows the established pattern: entities by display name,
grouped by platform (or by device for very different devices), with
description, availability and remarks; entity IDs only in examples.

## Considered options

- Entity IDs as the identifier: what users type in YAML, but they depend on
  the device name and language, and official pages do not list them.
- Platform-only grouping (the template's default): mixes the setup checklist
  with the operating entities.

## Consequences

- Good: the page reads like an official integration page; names come straight
  from the translations, so the check needs no Home Assistant.
- Bad: longer than a table; the register is a remark, not a column.

## Confirmation

- `tests/wiring_check.py` "entity reference matches the code"

```sh
! grep -nE 'ADR-[0-9]{4}|wiring_check|\.py\b|unique id|translation key' doc/entity-reference.md
! grep -nE '`(sensor|binary_sensor|switch|number|select|climate|button)\.[a-z0-9_]+`' doc/entity-reference.md
```

## More information

Pattern: contributors.home-assistant.io, quality-scale rule
`docs-supported-functions` and "Integration page structure". Supersedes
ADR-0030. How to add an entity: `.claude/rules/entities.md`.
