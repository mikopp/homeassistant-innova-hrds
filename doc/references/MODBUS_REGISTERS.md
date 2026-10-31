# HRDS+ / Innova DEH+ — Modbus Register Definition

Machine-readable extraction of the Modbus register map for the **hej.luft HRDS+**
air-dehumidification module (OEM: **Innova DEH+**), taken from
[`HRDS+_Modbus_RTU_RS485_DE.pdf`](HRDS+_Modbus_RTU_RS485_DE.pdf) (Stand: Mai 2026).

This file is the **single source of truth for the registers**: which exist,
their addresses, names, encodings, ranges and value meanings. It is written to
be read by both humans and agents. If a value here disagrees with the PDF, the
PDF wins — please fix this file.

What the unit *does* with these registers (states, sequences, seasons,
variants, what was tested on hardware) is in
[`UNIT_BEHAVIOUR.md`](UNIT_BEHAVIOUR.md). How the Home Assistant integration
uses them is in [`../adr/`](../adr/README.md) and [`../../README.md`](../../README.md),
not here.

**Referring to a register.** Every row below carries two anchors, so any
document can link to it:

| You write | As | Anchor |
|---|---|---|
| A parameter code | plain text, `[PH02](MODBUS_REGISTERS.md#ph02)` | the code in lower case |
| A decimal address | plain number, `[1105](MODBUS_REGISTERS.md#reg-1105)` | `reg-` and the address |
| A register name | code font, `` `Status_OnOff_byBMS` ``, with the address after it where it helps | none (use the address) |
| A section | ``[`MODBUS_REGISTERS.md` §16](MODBUS_REGISTERS.md#16-installer-menu-parameters-installer-device)`` | the heading |

Every document except this one links every mention of a code or address; only
a code block stays plain. Inside this file a code or address is linked when it
points to a register defined in another row.

---

## 1. Transport & framing

The HRDS+ control board speaks **Modicon Modbus RTU over RS-485**. A
Modbus-TCP gateway (if fitted) exposes the same register model over TCP/[502](#reg-502).

Factory serial defaults:

| Setting       | Default | Register        |
|---------------|---------|-----------------|
| Modbus address| `1`     | `0x06ED` ([1773](#reg-1773)) |
| Baud rate     | `9600`  | `0x06EE` ([1774](#reg-1774)) — `0=1200,1=2400,2=4800,3=9600,4=19200,5=28800,6=38400,7=57600` |
| Parity        | `None`  | `0x06EF` ([1775](#reg-1775)) — `0=None,1=Odd,2=Even` |
| Stop bits     | `1`     | `0x06F0` ([1776](#reg-1776)) — `0=1 stop bit,1=2 stop bits` |

> The serial-port parameters above can **only** be changed from the wired
> remote (Installer menu → MODBUS, password `2`) or the service software — not
> over Modbus itself. Power-cycle the unit after changing them.

## 2. Addressing & data-type conventions

* **`Addr HEX` / `Addr DEC`** in the tables below are the *direct* protocol
  addresses. Use them as-is with pymodbus (`address=1105` for `0x0451`); do
  **not** apply a `-1` offset.
* All registers are **16-bit, big-endian**.
* **Function codes** (this is how Read/Write is split):
  * **`R/O` → FC 04** "Read Input Registers".
  * **`R/W` → FC 03** "Read Holding Registers" (read) and FC 06 / FC 16 (write).
* **Everything is analog.** The manufacturer explicitly states that even 0/1
  status flags are analog registers — **there are no Modbus coils or discrete
  inputs** on this device.
* **Signed vs unsigned:** registers whose `Min` is negative (e.g. temperatures
  with `Min -3276.8`) are **INT16**; the rest are **UINT16**.
* **Scaling** (derived from the `Min/Max`/`Default` columns and the in-text
  notes):
  * Temperatures: value ×0.1 °C (e.g. raw `245` → `24.5 °C`). Range shown as
    `-3276.8 … 3276.7` ⇒ INT16 ÷10.
  * Setpoints ([SEtC](#setc), [SEtH](#seth), `Actual_Setpoint`): ×0.1 °C.
  * **Fan speeds / analog-out percentages: value ×0.01 %** — *write two implied
    decimals*. e.g. `40 %` is the raw value `4000`; `85 %` is `8500`.
  * Humidity ([PU01](#pu01), `AI_HretRoom`, warning setpoint): integer **%RH**, no scale.
  * Working hours ([PM00](#pm00)…[PM04](#pm04)): raw = whole hours, one 16-bit word each
    ([UNIT_BEHAVIOUR T29](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)). The display's "Hours x10" shows raw ÷ 10, so
    the shipped limit raw `20000` ("2000.0") is 20000 h.

## 3. Function enables — **set these first**

Modbus write commands are **ignored** unless the matching "by BMS" function is
enabled. An `OFF` command always wins over any `ON` command, regardless of
source (contact, display, Modbus).

| Addr HEX | Addr DEC | Name                    | R/W | Description |
|----------|----------|-------------------------|-----|-------------|
| `0x06F2` | 1778 | <a id="reg-1778"></a><a id="ph02"></a>`Enable_OnOffByBMS`       | R/W | **PH02** — set `1` to allow On/Off over Modbus (`0=Disabled,1=Enabled`). |
| `0x074D` | 1869 | <a id="reg-1869"></a><a id="ph27"></a>`Enable_IntegByBMS`       | R/W | **PH27** — set `1` to allow the integration (INT) request over Modbus. |
| `0x074E` | 1870 | <a id="reg-1870"></a><a id="ph28"></a>`Enable_DehumByBMS`       | R/W | **PH28** — set `1` to allow the dehumidify request over Modbus. |
| `0x06F1` | 1777 | <a id="reg-1777"></a><a id="ph01"></a>`Enable_OnOffByDisplay`   | R/W | **PH01** — set `0` if no wired display is present. While `1` with no display the unit stays `sm_UnitStatus` = `0` (OFF by display) permanently, and an OFF from any source beats a Modbus ON. Factory value is `1`. See [UNIT_BEHAVIOUR §3.1](UNIT_BEHAVIOUR.md#31-on--off). |
| `0x070B` | 1803 | <a id="reg-1803"></a><a id="ha00"></a>`T/H Probe Source` (HA00) | R/W | Source for temp/humidity probes: `0=None`, `6=CNU2 display` (factory default; a unit seen in the field read `2`). Set `0` if no display. All values: §14.2. |

## 4. Operating commands (control)

| Addr HEX | Addr DEC | Name                  | R/W | Values / meaning |
|----------|----------|-----------------------|-----|------------------|
| `0x0451` | 1105 | <a id="reg-1105"></a>`Status_OnOff_byBMS`     | R/W | Unit On/Off request: `0=Off`, `1=On`. (Requires [PH02](#ph02)=1.) |
| `0x0474` | 1140 | <a id="reg-1140"></a>`Status_Dehum_byBMS`     | R/W | Dehumidify request: `0=No`, `1=Yes`. (Requires [PH28](#ph28)=1.) |
| `0x0473` | 1139 | <a id="reg-1139"></a>`Status_Integ_byBMS`     | R/W | Integration / **active-cooling** request: `0=No`, `1=Yes`. (Requires [PH27](#ph27)=1.) |
| `0x062F` | 1583 | <a id="reg-1583"></a>`Mode_OperatingMode`     | R/O | Season: `0=Summer`, `1=Winter`, `2=Auto`. Use as feedback. |
| `0x0721` | 1825 | <a id="reg-1825"></a><a id="hb04"></a>`DI4_Configuration`(HB04)| R/W | Season change w/o display: `4=Summer (DI4 N/O)`, `3=Winter (DI4 N/C)`. **Only 3 or 4 are valid — other values raise alarm AL25.** |
| `0x0766` | 1894 | <a id="reg-1894"></a><a id="pc12"></a>`PC12_Enable_OnOFF_by_INT_DEU` | R/W | `1` = a DEU/INT request on the **digital inputs** starts the unit even with the OFF/OFF contact open. |
| `0x0756` | 1878 | <a id="reg-1878"></a><a id="pc11"></a>`PriorityChangeMode_Display` (PC11) | R/W | Who owns season change: `0=Display`, `1=DI/Digital-IN`. |

> **Integration (INT)** (`0x0473`) cools in summer and supports heating in
> winter; **DEU** (`0x0474`) dehumidifies. What each request does in which
> season: [UNIT_BEHAVIOUR §6–§7](UNIT_BEHAVIOUR.md#6-summer-operation).

## 5. Setpoints

| Addr HEX | Addr DEC | Name                    | R/W | Default | Min | Max | Unit/scale |
|----------|----------|-------------------------|-----|---------|-----|-----|------------|
| `0x0630` | 1584 | <a id="reg-1584"></a><a id="setc"></a>`SEtC_SummerSetpoint`      | R/W | 24.0 | 15.0 | 158.0 | °C ×0.1 |
| `0x0631` | 1585 | <a id="reg-1585"></a><a id="seth"></a>`SEtH_WinterSetpoint`      | R/W | 20.0 | 15.0 | 158.0 | °C ×0.1 |
| `0x0632` | 1586 | <a id="reg-1586"></a><a id="pu01"></a>`PU01_Humidity_Setpoint`   | R/W | 55   | 0    | 100   | %RH |
| `0x0764` | 1892 | <a id="reg-1892"></a><a id="ph29"></a>`PH29_Min_Humidity_Setpoint` | R/W | — | 0 | 100 | %RH lower clamp for [PU01](#pu01) |
| `0x0765` | 1893 | <a id="reg-1893"></a><a id="ph30"></a>`PH30_Max_Humidity_Setpoint` | R/W | — | 0 | 100 | %RH upper clamp for [PU01](#pu01) |
| `0x06C7` | 1735 | <a id="pa19"></a><a id="reg-1735"></a>`Setpoint_HighHumWarning` (PA19) | R/W | 70 | 0 | 100 | %RH — triggers high-humidity warning AL02 |

> Setpoints only take effect when a display is present **or** external probes
> are connected [MB p.6]. Clamps and automatic thresholds:
> [UNIT_BEHAVIOUR §3.3–§3.4](UNIT_BEHAVIOUR.md#33-requests-deu-and-int).

## 6. Fan speed

Fan-speed registers are percentages with **two implied decimals** (write `4000`
for 40 %). Min/Max apply to the modulation band used in each mode.

| Addr HEX | Addr DEC | Name                 | R/W | Default | Range | Meaning |
|----------|----------|----------------------|-----|---------|-------|---------|
| `0x073D` | 1853 | <a id="reg-1853"></a><a id="pf28"></a>`MinSpeedFan_Dehum` (PF28) | R/W | 50.00 | 0–100 | Supply-fan min speed in dehumidify |
| `0x066F` | 1647 | <a id="reg-1647"></a><a id="pf10"></a>`MaxSpeedFan_Dehum` (PF10) | R/W | 85.00 | 0–100 | Supply-fan max speed in dehumidify |
| `0x073C` | 1852 | <a id="reg-1852"></a><a id="pf27"></a>`MinSpeedFan_Integ` (PF27) | R/W | 50.00 | 0–100 | Supply-fan min speed in integration (cooling) |
| `0x066C` | 1644 | <a id="reg-1644"></a><a id="pf07"></a>`MinSpeedSupplyFan_VMC` (PF07) | R/W | — | 0–100 | Supply-fan min speed in VMC (ventilation-only) mode |
| `0x066E` | 1646 | <a id="reg-1646"></a><a id="pf09"></a>`MaxSpeedFan_Integ` (PF09) | R/W | 85.00 | 0–100 | Supply-fan max speed in integration (cooling) |
| `0x064E` | 1614 | <a id="reg-1614"></a><a id="pm20"></a>`PM20_SupplyFan_Manual`    | R/W | — | 0–100 | Supply-fan manual setpoint of the **display**. Listed R/W in the raw parameter table [MB p.18], defined "via Display (read only)" in the handbook (PM20, §5.3); the unit sets it itself, a written value does not hold, one outside the band answers exception 04 ([UNIT_BEHAVIOUR §9.1](UNIT_BEHAVIOUR.md#91-bands-and-sources); evidence [T22, T23, T27, T28](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)). Not a fan-speed command |
| `0x0458` | 1112 | <a id="reg-1112"></a>`FanIntegration_Request`   | R/O | — | 0–100 | "Fans integration request": the fan request of the integration (INT) fan control ([PF31](#pf31)) [MB p.14]. Not a 0/1 flag and not the INT request ([1139](#reg-1139)), see §13. Read 0 while the fan ran during two dehumidify requests ([UNIT_BEHAVIOUR T16, T18](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)) |
| `0x0459` | 1113 | <a id="reg-1113"></a>`Supply_AirQualityRequest` | R/O | — | 0–100 | Supply-fan air-quality request [MB p.14] |
| `0x045A` | 1114 | <a id="reg-1114"></a>`SupplyFan_ManualRequest`  | R/O | — | 0–100 | Current manual (display) fan request; reads the same as [PM20](#pm20) |
| `0x045B` | 1115 | <a id="reg-1115"></a>`Supply_TimeBandsRequest`  | R/O | — | 0–100 | Supply-fan time-band request [MB p.15] |
| `0x045C` | 1116 | <a id="reg-1116"></a>`SupplyFan_RemoteRequest`  | R/O | — | 0–100 | Current potentiometer (0–10 V) fan request |
| `0x027F` | 639  | <a id="reg-639"></a>`outAO_SupplyFan`          | R/O | — | 0–100 | Actual supply-fan analog output %: the speed the fan is driven at |
| `0x045D` | 1117 | <a id="reg-1117"></a>`actRPMsupplyFan`          | R/O | — | 0–65535 | Supply-fan actual RPM. Needs an input allocated to the tachometer (input function 45 or 46, §16 `HA..`/`HB..`); 0 without one ([UNIT_BEHAVIOUR §9.1](UNIT_BEHAVIOUR.md#91-bands-and-sources)) |
| `0x045E` | 1118 | <a id="reg-1118"></a>`actRPMreturnFan` | R/O | — | 0–65535 | Return-fan actual RPM (no return fan on an HRDS+) |
| `0x046F` | 1135 | <a id="reg-1135"></a>`Return_AirQualityRequest` | R/O | — | 0–100 | Return-fan air-quality request [MB p.15] |
| `0x0470` | 1136 | <a id="reg-1136"></a>`Return_ManualRequest` | R/O | — | 0–100 | Return-fan manual request |
| `0x0471` | 1137 | <a id="reg-1137"></a>`Return_TimeBandsRequest` | R/O | — | 0–100 | Return-fan time-band request |
| `0x0472` | 1138 | <a id="reg-1138"></a>`Return_RemoteRequest` | R/O | — | 0–100 | Return-fan potentiometer request |

### 6.1 How the bands apply

The min/max pairs are per-mode bands; the handbook scales display and 0–10 V
requests linearly into the active band (§6.2). On a real unit the manual
(display) request mirrored in [1114](#reg-1114)/[1614](#reg-1614) is instead clamped into the band: a
raised minimum raises it, a lowered one leaves it ([UNIT_BEHAVIOUR T24–T26](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)).
No register takes a fan-speed
request from the BMS; the band registers are the only fan-speed registers the
Modbus manual's fan chapter lists as writable [MB p.7]. Other writable fan
setpoints, each tied to a condition: `FSC`/`FSE`/`FSN` (1595–1597, time bands,
need time programs [PH03](#ph03)) [MB p.18], [PF23](#pf23) ([1660](#reg-1660), forced by a digital input)
[MB p.20], [PF26](#pf26) ([1637](#reg-1637), run-on). Behaviour:
[UNIT_BEHAVIOUR §9.1](UNIT_BEHAVIOUR.md#91-bands-and-sources).

## 7. Sensors (read-only, FC 04)

| Addr HEX | Addr DEC | Name              | Type | Scale | Description |
|----------|----------|-------------------|------|-------|-------------|
| `0x01F3` | 499 | <a id="reg-499"></a>`AI_TreturnRoom`     | INT16 | ×0.1 °C | Return/room air temperature (needs display or external probe) |
| `0x01F4` | 500 | <a id="reg-500"></a>`AI_Toutdoor`        | INT16 | ×0.1 °C | Outdoor air temperature |
| `0x01F5` | 501 | <a id="reg-501"></a>`AI_Twater`          | INT16 | ×0.1 °C | Water-circuit temperature |
| `0x01F6` | 502 | <a id="reg-502"></a>`AI_Texhaust`        | INT16 | ×0.1 °C | Exhaust air temperature |
| `0x01F7` | 503 | <a id="reg-503"></a>`AI_Tdischarge`      | INT16 | ×0.1 °C | Discharge (supply) air temperature |
| `0x01F8` | 504 | <a id="reg-504"></a>`AI_TcmpDefrost` | INT16 | ×0.1 °C | Compressor defrost temperature probe |
| `0x01F9` | 505 | <a id="reg-505"></a>`AI_HretRoom`        | INT16 | %RH | Return/room relative humidity (needs display or external probe) |
| `0x01FA` | 506 | <a id="reg-506"></a>`AI_AirQuality`      | INT16 | ppm/raw | Air-quality probe |
| `0x01FB` | 507 | <a id="reg-507"></a>`AI_RemoteSupply` | INT16 | ×0.01 | Remote supply-fan potentiometer |
| `0x01FC` | 508 | <a id="reg-508"></a>`AI_HighPressure` | INT16 | ×0.1 | High-pressure condenser probe |
| `0x01FD` | 509 | <a id="reg-509"></a>`AI_RemoteReturn` | INT16 | ×0.01 | Remote return-fan potentiometer |
| `0x01FE` | 510 | <a id="reg-510"></a>`AI_TfreeCooling` | INT16 | ×0.1 °C | Free-cooling temperature probe |
| `0x01FF` | 511 | <a id="reg-511"></a>`AI_Tevaporation`    | INT16 | ×0.1 °C | Evaporator temperature (inverter-compressor version only) |
| `0x0200` | 512 | <a id="reg-512"></a>`AI_EvaporationPressure` | INT16 | ×0.1 | Evaporation pressure probe |
| `0x0457` | 1111| <a id="reg-1111"></a>`Actual_Setpoint`    | INT16 | ×0.1 °C | Active room setpoint in use |

## 8. Unit & component status (read-only, FC 04)

| Addr HEX | Addr DEC | Name              | Values |
|----------|----------|-------------------|--------|
| `0x0280` | 640 | <a id="reg-640"></a>`outAO_ReturnFan` | Return-fan output % (×0.01) |
| `0x0281` | 641  | <a id="reg-641"></a>`outAO_Cmp`          | Compressor output % (×0.01) |
| `0x0282` | 642 | <a id="reg-642"></a>`outAO_ExternalDamper` | External damper output % (×0.01) |
| `0x044F` | 1103 | <a id="reg-1103"></a>`OR_Alarms`          | `0/1` cumulative "any alarm active" flag |
| `0x0450` | 1104 | <a id="reg-1104"></a>`sm_UnitStatus`      | `0=OFF by display`, `1=OFF by DI`, `2=OFF by BMS`, `3=OFF by scheduler`, `4=OFF by RTC`, `5=ON` |
| `0x0452` | 1106 | <a id="reg-1106"></a>`ActualBand_TB` | Active time band: `0=Disable`, `1=OFF`, `2=Comfort`, `3=Economy`, `4=Night`, `5=Holiday`, `6=Economy DI` |
| `0x0456` | 1110 | <a id="reg-1110"></a>`ModeStatus`         | `0=Summer manual`, `1=Winter manual`, `2=Summer auto`, `3=Winter auto`, `4=Summer DI`, `5=Winter DI` |
| `0x045F` | 1119 | <a id="reg-1119"></a>`SupplyFan_Status`   | `0=Disable`, `1=OFF`, `2=Wait ON`, `3=ON`, `4=Wait OFF`, `5=Alarm` |
| `0x0460` | 1120 | <a id="reg-1120"></a>`ReturnFan_Status` | `0=Disable`, `1=OFF`, `2=Wait ON`, `3=ON`, `4=Wait OFF`, `5=Alarm` |
| `0x0461` | 1121 | <a id="reg-1121"></a>`DehumRequest`       | `0=No`, `1=Yes` — dehumidification currently requested |
| `0x0462` | 1122 | <a id="reg-1122"></a>`CmpStatus`          | `0=Disable`, `1=Alarm`, `2=Manual`, `3=Wait ON`, `4=ON`, `5=Wait OFF`, `6=OFF` — compressor (active cooling/dehum) |
| `0x0463` | 1123 | <a id="reg-1123"></a>`DefrostStatus` | Compressor defrost: `0=OFF`, `1=ON`, `2=Dripping` |
| `0x0464` | 1124 | <a id="reg-1124"></a>`outDO_WaterCond` | Internal water condenser valve (relay K4): `0=OFF`, `1=ON`, `2=Disable`. A real unit reads `1` in standby, against the handbook's description; see [UNIT_BEHAVIOUR §11.1](UNIT_BEHAVIOUR.md#111-internal-valve-relay-k4). |
| `0x0465` | 1125 | <a id="reg-1125"></a>`outDO_AirCond` | Air condenser valve: `0=OFF`, `1=ON`, `2=Disable` |
| `0x0466` | 1126 | <a id="reg-1126"></a>`outDO_WaterFlow` | External water valve V3V (relay K5) — the PM pump output is switched together with it: `0=OFF`, `1=ON`, `2=Disable` (output not configured). |
| `0x0467` | 1127 | <a id="reg-1127"></a>`ExtDamperModulating` | Modulating external damper position, % (×0.01) |
| `0x0468` | 1128 | <a id="reg-1128"></a>`ExtDamper_Status` | External damper: `0=Disable`, `1=OFF`, `2=Wait OFF`, `3=ON` |
| `0x0469` | 1129 | <a id="reg-1129"></a>`Status_HeatExchanger` | Heat exchanger: `0=Disable`, `1=OFF`, `2=OFF defrost`, `3=OFF free-cooling/free-heating`, `4=ON` |
| `0x046A` | 1130 | <a id="reg-1130"></a>`tempRecover` | Heat exchanger temperature (INT16 ×0.1 °C) |
| `0x046B` | 1131 | <a id="reg-1131"></a>`Efficiency_HeatExchanger` | Heat exchanger efficiency (INT16 ×0.01) |
| `0x046C` | 1132 | <a id="reg-1132"></a>`Request_FreeCoolingHeating` | `0/1` free-cooling / free-heating request |
| `0x046D` | 1133 | <a id="reg-1133"></a>`Preheating` | `0/1` pre-heating function active |
| `0x046E` | 1134 | <a id="reg-1134"></a>`outDO_RecircDamper` | `0=OFF` (damper closed), `1=ON` (damper open), `2=Disable` (no damper output allocated; expected on a non-`R` unit) |

### Packed digital I/O status (bit-fields, R/O)

The device packs digital inputs/outputs into 16-bit registers using **2 bits
per signal** (`bitN..bitN+1`); a non-zero pair means active. The exception is
`Packed_DI`, one bit per input.

| Addr HEX | Addr DEC | Name | Bits |
|----------|----------|------|------|
| `0x0100` | 256 | <a id="reg-256"></a>`Packed_DI` | bit0=DI01, bit1=DI02, bit2=DI03, bit3=DI04, bit4=DI01 Exp, bit5=DI02 Exp, bit6=DI03 Exp (1 bit per input) |
| `0x0101` | 257 | <a id="reg-257"></a>`Packed_logicDI1` | bit0-1=Remote on/off, bit2-3=Summer/Winter, bit4-5=Dehum request, bit6-7=Integration/thermo request, bit8-9=Water flow switch, bit10-11=Supply fan flow switch, bit12-13=Return fan flow switch, bit14-15=Supply air filter |
| `0x0102` | 258 | <a id="reg-258"></a>`Packed_logicDI2` | bit0-1=Return air filter, bit2-3=Forced fan, bit4-5=Thermal supply fan, bit6-7=Thermal return fan, bit8-9=Tacho supply fan, bit10-11=Tacho return fan, bit12-13=Low pressure, bit14-15=High pressure |
| `0x0103` | 259 | <a id="reg-259"></a>`Packed_logicDI3` | bit0-1=Thermal compressor, bit2-3=Fire/smoke alarm, bit4-5=Phase sequence, bit6-7=Antifreeze, bit8-9=Generic alarm, bit10-11=Generic warning, bit12-13=Economy, bit14-15=Only ventilation |
| `0x0180` | 384 | <a id="reg-384"></a>`Packed_DO1` | bit0-1=Supply fan, bit2-3=Return fan, bit4-5=Compressor (K6), bit6-7=External damper, bit8-9=Recirculation damper (K1), bit10-11=External water valve or pump (K5), bit12-13=Water condensation valve (K4) (`0=Integration,1=Dehumidify`), bit14-15=Air condensation valve |
| `0x0181` | 385 | <a id="reg-385"></a>`Packed_DO2` | bit0-1=Heat exchanger, bit2-3=Free-cooling bypass, bit4-5=On/Off, bit6-7=Summer/Winter, bit8-9=Serious alarm, bit10-11=Light alarm, bit12-13=High humidity |

## 9. Alarms

### 9.1 Active-alarm bitmaps (R/O, FC 04)

Each bit = one alarm code. Bit set ⇒ alarm active.

| Addr HEX | Addr DEC | Name | Bit → code |
|----------|----------|------|------------|
| `0x0300` | 768 | <a id="reg-768"></a>`PackedAlarm_1` | bit00=AL01 … bit15=AL16 |
| `0x0301` | 769 | <a id="reg-769"></a>`PackedAlarm_2` | bit00=AL17 … bit15=AL32 |
| `0x0302` | 770 | <a id="reg-770"></a>`PackedAlarm_3` | bit00=AL33, bit01=AL34, bit02=AL35, bit04=AL37, bit05=AL38, bit06=AL39 |

### 9.2 Alarm code reference

What triggers each alarm, what it stops and how it resets:
[UNIT_BEHAVIOUR §12](UNIT_BEHAVIOUR.md#12-alarms-and-what-they-do-to-the-flow).

| Code | Description |
|------|-------------|
| AL02 | High humidity |
| AL03 | High summer water temperature |
| AL04 | Low winter water temperature |
| AL11 | Compressor low-pressure / frost-thermostat |
| AL12 | Compressor high-pressure switch |
| AL16 | Water-circuit antifreeze |
| AL18 | Generic alarm |
| AL19 | Generic warning |
| AL22 | Dirty filters |
| AL25 | I/O configuration error |
| AL26 | RTC clock failed/disconnected |
| AL28 | Room/return temperature probe fault |
| AL29 | External temperature probe fault |
| AL30 | Water temperature probe fault |
| AL34 | Room/return humidity probe fault |
| AL36 | Fan potentiometer fault |
| AL39 | Evaporator temperature probe fault |

### 9.3 Alarm reset registers (R/W)

Only these alarms have a reset register; the others reset themselves or at
the unit.

| Addr HEX | Addr DEC | Name | Meaning |
|----------|----------|------|---------|
| `0x030B` | 779 | <a id="reg-779"></a>`BMS_AL01` | Write `1` to reset AL01 |
| `0x030C` | 780 | <a id="reg-780"></a>`BMS_AL02` | Write `1` to reset AL02 |
| `0x030D` | 781 | <a id="reg-781"></a>`BMS_AL07` | Write `1` to reset AL07 |
| `0x030E` | 782 | <a id="reg-782"></a>`BMS_AL08` | Write `1` to reset AL08 |
| `0x030F` | 783 | <a id="reg-783"></a>`BMS_AL09` | Write `1` to reset AL09 |
| `0x0310` | 784 | <a id="reg-784"></a>`BMS_AL10` | Write `1` to reset AL10 |
| `0x0311` | 785 | <a id="reg-785"></a>`BMS_AL11` | Write `1` to reset AL11 |
| `0x0312` | 786 | <a id="reg-786"></a>`BMS_AL12` | Write `1` to reset AL12 |
| `0x0313` | 787 | <a id="reg-787"></a>`BMS_AL13` | Write `1` to reset AL13 |
| `0x0314` | 788 | <a id="reg-788"></a>`BMS_AL14` | Write `1` to reset AL14 |
| `0x0315` | 789 | <a id="reg-789"></a>`BMS_AL15` | Write `1` to reset AL15 |
| `0x0316` | 790 | <a id="reg-790"></a>`BMS_AL17` | Write `1` to reset AL17 |
| `0x0317` | 791 | <a id="reg-791"></a>`BMS_AL18` | Write `1` to reset AL18 |
| `0x0318` | 792 | <a id="reg-792"></a>`BMS_AL19` | Write `1` to reset AL19 |
| `0x0319` | 793 | <a id="reg-793"></a>`BMS_AL21` | Write `1` to reset AL21 |
| `0x031A` | 794 | <a id="reg-794"></a>`BMS_AL26` | Write `1` to reset AL26 |

**Filter alarm AL22 is reset by writing `0` to `0x0644` ([1604](#reg-1604)).**

## 10. Key configuration parameters (R/W) worth knowing

| Addr HEX | Addr DEC | Name | Meaning |
|----------|----------|------|---------|
| `0x0705` | 1797 | <a id="reg-1797"></a><a id="pg01"></a>`PG01_MachineType` | Fan arrangement: `0=supply fan only`, `1=supply fan + exhaust fan` (handbook PG01: „Entfeuchter nur mit Zuluftventilator“ / „mit Zuluft- und Abluftventilator“). **Not** a flag for the recirculation fan: use `outDO_RecircDamper` ([1134](#reg-1134)) for that ([UNIT_BEHAVIOUR §1.2](UNIT_BEHAVIOUR.md#12-what-differs-between-the-variants)). |
| `0x0706` | 1798 | <a id="reg-1798"></a><a id="pg02"></a>`PG02_EnableIntegration` | Enable the active-cooling integration function |
| `0x0699` | 1689 | <a id="reg-1689"></a><a id="pu02"></a>`PU02_EnableWinterDehum` | `0=No`, `1=With water`, `2=Without water` |
| `0x069C` | 1692 | <a id="reg-1692"></a><a id="pu05"></a>`PU05_ForceDehumInCooling` | Force dehumidify when cooling requested |
| `0x06F5` | 1781 | <a id="reg-1781"></a><a id="ph05"></a>`PH05_TemperatureUM` | `0=°C`, `1=°F` |
| `0x06F3` | 1779 | <a id="reg-1779"></a><a id="ph03"></a>`PH03_EnableTimePrograms` | `0=No`, `1=Yes`. Time programs can switch the unit OFF (status `off_by_scheduler`). |
| `0x070D` | 1805 | <a id="reg-1805"></a><a id="ha02"></a>`HA02_AI2_Allocation` | Analog input 2 allocation. `0`=unused, `45`=room temperature probe. A probe code with nothing wired raises AL28. |
| `0x070E` | 1806 | <a id="reg-1806"></a><a id="ha03"></a>`HA03_AI3_Allocation` | Analog input 3 allocation. `0`=unused, `53`/`54`=room humidity probe. A probe code with nothing wired raises AL34. |
| `0x0720` | 1824 | <a id="reg-1824"></a><a id="hb03"></a>`DI3_Configuration` (HB03) | Remote ON/OFF contact (OFF/OFF terminals): `0=unused`, `1=normally closed`, `2=normally open`. With the contact open the unit is forced OFF (`off_by_di`). |
| `0x0728` | 1832 | <a id="reg-1832"></a><a id="hc04"></a>`HC04` | Analog output allocation of the supply fan (raw code; `1` = 0-10 V supply fan). |
| `0x072E` | 1838 | <a id="reg-1838"></a><a id="hd01"></a>`HD01` | Relay DO1 allocation (raw code; `10` = recirculation damper NO, `9` = NC). |
| `0x06A2` | 1698 | <a id="reg-1698"></a><a id="ps01"></a>`PS01_PreStartTime_RecircDamper` | Damper pre-start time before the fan starts, in seconds (handbook default 20; a real unit read 90). |
| `0x0642` | 1602 | <a id="pm00"></a><a id="reg-1602"></a>`PM00_Limit_FansHours` | Fan running-hours alarm limit (h; the display shows ÷ 10) |
| `0x0644` | 1604 | <a id="pm01"></a><a id="reg-1604"></a>`PM01_SupplyFan_Hours` | Fan running-hours counter (write 0 to reset filter alarm AL22) |

---

## 11. Cookbook — common operations

> Requires the matching **[PH02](#ph02) / [PH27](#ph27) / [PH28](#ph28)** enable register set to `1` first
> (see §3). All addresses are decimal Modbus PDU addresses.

**Turn the unit on / off**
1. One-time: write `1` to [1778](#reg-1778) ([PH02](#ph02) Enable_OnOffByBMS).
2. On: write `1` to [1105](#reg-1105); Off: write `0` to [1105](#reg-1105).
3. Read back [1104](#reg-1104) (`sm_UnitStatus`); `5` = ON.

**Turn dehumidification on / off**
1. One-time: write `1` to [1870](#reg-1870) ([PH28](#ph28) Enable_DehumByBMS).
2. On: write `1` to [1140](#reg-1140); Off: write `0`.
3. Read back [1121](#reg-1121) (`DehumRequest`) and [1122](#reg-1122) (`CmpStatus`).

**Turn active cooling (integration) on / off**
1. One-time: write `1` to [1869](#reg-1869) ([PH27](#ph27) Enable_IntegByBMS) and ensure
   `PG02_EnableIntegration` ([1798](#reg-1798)) = 1 (installer setting). In summer INT cools,
   in winter it supports heating.
2. On: write `1` to [1139](#reg-1139); Off: write `0`.
3. Compressor feedback via [1122](#reg-1122) (`CmpStatus`, `4`=ON).

**Set the air-flow (fan) speed**
* Dehumidify-mode band: min [1853](#reg-1853), max [1647](#reg-1647). Cooling band: min [1852](#reg-1852),
  max [1646](#reg-1646). Remember the **×100** encoding (`40 %` → `4000`). [1614](#reg-1614) ([PM20](#pm20))
  is the display's setpoint and does not hold a written value (§6).
* Actual output: [639](#reg-639) (`outAO_SupplyFan`, ×0.01 %), RPM: [1117](#reg-1117).

**Set the humidity target** — write %RH to [1586](#reg-1586) ([PU01](#pu01)), clamped by [1892](#reg-1892)/[1893](#reg-1893).

**Set the temperature target** — summer [1584](#reg-1584), winter [1585](#reg-1585) (°C ×0.1).

**Read sensors** — room temp [499](#reg-499) (×0.1 °C), room humidity [505](#reg-505) (%RH),
outdoor temp [500](#reg-500), water temp [501](#reg-501), supply/discharge temp [503](#reg-503).

**Is the unit on?** — read [1104](#reg-1104); `5` = ON, anything `0–4` = a specific OFF cause.
A written request reads back late (several polls on a real unit), see
[UNIT_BEHAVIOUR §3.3](UNIT_BEHAVIOUR.md#33-requests-deu-and-int).

**Check errors / status** — read [1103](#reg-1103) (any-alarm flag) then [768](#reg-768)/[769](#reg-769)/[770](#reg-770)
(per-bit alarm codes); decode with §9.2.

---

## 12. Transport notes

* **No coils / discrete inputs.** Read-only values are input registers (FC 04),
  read-write values holding registers (FC 03/06/16). 0/1 flags are analog
  registers, not bits [MB p.5].
* **Wide, sparse address space (≈0x0100–0x077A).** A single block read of the
  whole range exceeds Modbus' 125-register-per-request limit, so read in
  contiguous chunks per function code.
* **Keep the chunks small.** On a real unit behind an RS-485→TCP gateway a
  120-register read got no reply at all, while 10-register reads covered the
  whole map ([UNIT_BEHAVIOUR evidence T9](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)).
  Whether the limit is the gateway's or the controller's is open.
* **Enables are mandatory**: §3.
* See `HRDS+_Modbus_RTU_RS485_DE.pdf` §6 "FULL MODBUS REGISTER LIST" for the
  complete table (schedulers, probe calibration, alarm tuning, hardware I/O
  mapping); the installer parameters from it are in §16.

---

## 13. Two registers called "integration"

`Status_Integ_byBMS` ([1139](#reg-1139)) and `FanIntegration_Request` ([1112](#reg-1112)) both contain
the word *integration* but are unrelated: [1139](#reg-1139) is the **INT request**
(cooling in summer, heating support in winter, written by the BMS); [1112](#reg-1112) is a read-only "fans integration request", a fan request in % of the INT fan control (§6). It read 0 while the supply fan ran for a dehumidify request ([UNIT_BEHAVIOUR T16](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)).

Airflow behaviour (passive MVHR flow, recirculation coupled to every request,
the unofficial I/O workaround) is in
[UNIT_BEHAVIOUR §9](UNIT_BEHAVIOUR.md#9-fan), in particular
[§9.3 Recirculation is coupled to every request](UNIT_BEHAVIOUR.md#93-recirculation-is-coupled-to-every-request-r-variant).

---

## 14. Probes: inputs and probe source

### 14.1 Analog inputs

| Register | Addr DEC | Input | Probe | Notes |
|----------|----------|-------|-------|-------|
| `AI_TreturnRoom` | [499](#reg-499) | AI2 (M2) when [HA02](#ha02) = 45, or the display | NTC 10 kΩ @ 25 °C, B 3435 | Probe fault: AL28 |
| `AI_Toutdoor` | [500](#reg-500) | configurable input | NTC 10 kΩ B 3435, outdoor rated | Probe fault: AL29 |
| `AI_Twater` | [501](#reg-501) | AI5 (M5), factory wired | — | Probe fault: AL30 |
| `AI_Texhaust` | [502](#reg-502) | configurable input | NTC 10 kΩ B 3435 | — |
| `AI_Tdischarge` | [503](#reg-503) | configurable input | NTC 10 kΩ B 3435 | — |
| `AI_HretRoom` | [505](#reg-505) | AI3 (M3) when [HA03](#ha03) = 53/54, or the display | 4–20 mA (`53`) or 0–10 V (`54`), 0–100 %RH | Probe fault: AL34 |
| `AI_AirQuality` | [506](#reg-506) | configurable input | 0–10 V / 4–20 mA | — |
| `AI_Tevaporation` | [511](#reg-511) | AI4 (M4), factory wired | — | Inverter version only; probe fault: AL39 |

The high- and low-pressure switches (DI1/DI2, the frost thermostat on DI2's
input) are digital inputs with no analog register; they raise AL12 / AL11.
Sources: [HB 6.3, 6.7, 7.3]; [MB p.7].

What each probe drives, and how the unit behaves with and without a display
or probes: [UNIT_BEHAVIOUR §8](UNIT_BEHAVIOUR.md#8-display-and-probe-configurations).

### 14.2 Probe source: HA00 (register 1803)

Parameter **[HA00](#ha00)** tells the controller which source to use for room
temperature and humidity (handbook §5.3, §6.7).

| [HA00](#ha00) value | Meaning | Room T source | Room H source |
|-----------|---------|---------------|---------------|
| `0` | None / external probes | AI2 (M2) if allocated with code 45 | AI3 (M3) if allocated with code 53/54 |
| `1` | CNU display (Evj), T only | CNU built-in NTC | — |
| `2` | CNU display (Evj), T + H | CNU built-in NTC | CNU built-in humidity |
| `3` | EPJ display, T only | EPJ built-in NTC | — |
| `4` | EPJ display, T + H | EPJ built-in NTC | EPJ built-in humidity |
| `5` | CNU2 display (Epj Graph), T only | CNU2 built-in NTC | — (AI3 probe possible) |
| `6` | CNU2 display (Epj Graph), T + H **(factory default)** | CNU2 built-in NTC | CNU2 built-in humidity |

Required pairs (handbook §5.1, §8.1): with CNU2 [PH01](#ph01) = 1, [HA00](#ha00) = 6; without
CNU2 [PH01](#ph01) = 0, [HA00](#ha00) = 0. A real unit without a display shipped with
[HA00](#ha00) = 2.

### 14.3 Probe fault bits

| Alarm | Register | Addr DEC | Bit |
|-------|----------|----------|-----|
| AL28 — room temperature probe fault | `PackedAlarm_2` | [769](#reg-769) | 11 |
| AL34 — room humidity probe fault | `PackedAlarm_3` | [770](#reg-770) | 1 |

### 14.4 Unwired analog inputs read a sentinel, not a temperature

Observed on an HRDS+ 30 with no display and no external probes ([HA00](#ha00) = 2,
[PH01](#ph01) = 1): `AI_TreturnRoom` ([499](#reg-499)), `AI_Toutdoor` ([500](#reg-500)), `AI_Texhaust` ([502](#reg-502)),
`AI_Tdischarge` ([503](#reg-503)), `AI_HretRoom` ([505](#reg-505)) and `AI_AirQuality` ([506](#reg-506)) all read raw
`32772` (`0x8004`); register [507](#reg-507) read `32762` (`0x7FFA`). Decoded as INT16 ×0.1
that is **-3276.4 °C** (and -32764 %RH), which is never a real reading. The
factory-wired `AI_Twater` ([501](#reg-501)) and `AI_Tevaporation` ([511](#reg-511)) read normally.

This sentinel is empirical, not in the manufacturer tables. A window of
`0x7FF0..0x800F` covers both observed words and cannot collide with a real
reading (±3276 °C). Negative temperatures are fine (-1.0 °C = `0xFFF6`). What a
wired but broken probe reads is not known yet.

---

## 15. Control parameters worth reading

Extracted from `HRDS+_Modbus_RTU_RS485_DE.pdf` §6 (FULL MODBUS REGISTER LIST).
What the unit does with them: [UNIT_BEHAVIOUR §5](UNIT_BEHAVIOUR.md#5-decision-procedure-agent-readable);
what they mean for an external controller (minimum run times, [PU13](#pu13) vetoing a
dehumidify request, [PU07](#pu07) as the unit's own hysteresis):
[UNIT_BEHAVIOUR §3.3, §9, §10](UNIT_BEHAVIOUR.md#33-requests-deu-and-int).

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x069E` | 1694 | <a id="reg-1694"></a><a id="pu07"></a>`PU07_Dehumidity_Diff` | R/W | 0-100 %RH | Automatic DEU request on above [PU01](#pu01) + PU07, off below [PU01](#pu01). |
| `0x0761` | 1889 | <a id="reg-1889"></a><a id="pu13"></a>`PU13_MinTRoom_disableDEU` | R/W | 0-30.0 °C (×0.1) | Room temperature below which dehumidification (and the compressor) is disabled. |
| `0x0762` | 1890 | <a id="reg-1890"></a><a id="pu14"></a>`PU14_TRoomDIFF_enableDEU` | R/W | 0.1-20.0 °C (×0.1) | Differential above [PU13](#pu13) at which dehumidification is re-enabled. |
| `0x0666` | 1638 | <a id="reg-1638"></a><a id="pf01"></a>`PF01_MinTimeOnFan` | R/W | 0-999 s | Minimum fan run time. |
| `0x0668` | 1640 | <a id="reg-1640"></a><a id="pf03"></a>`PF03_MinTimePostFan` | R/W | 0-999 s | Fan run-on after the compressor stops (`0` disables it). |
| `0x0707` | 1799 | <a id="reg-1799"></a><a id="pg03"></a>`PG03_EnableFreeCoolingHeating` | R/W | `0=No`, `1=Yes` | Enables free cooling/heating; only then does `AI_Toutdoor` ([500](#reg-500)) drive anything. |

> The Modbus table does not state the [PF01](#pf01)/[PF03](#pf03) unit. Seconds: with
> [PF03](#pf03) = 30 the fan ran on for under a minute on the reference unit
> ([UNIT_BEHAVIOUR T19](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)).

---

## 16. Installer-menu parameters (installer device)

Every handbook parameter (§5.3) that has a Modbus address in the RTU
manual's parameter table and is not already listed above ([PA19](#pa19) is in §5,
[PM00](#pm00) and [PM01](#pm01) in §10). Scaling was checked against a real unit's raw
read-back, except for the rows marked *not exposed*, which take the scale of
their neighbours. Passwords (`PSd*`) and the other registers of the manual's
list are in §17. The manual's list ends at [1914](#reg-1914).

The *Access* column mixes two things: `R/W` / `R/O` is the register as the
Modbus manual defines it; "shown R/O", "disabled by default" and "not exposed"
record how the Home Assistant integration treats it ("not exposed": no
entity at all). It deliberately never writes link settings, I/O allocation,
refrigerant, safety bypass and test mode; source of truth for what is
exposed: `custom_components/innova_hrds/installer_params.py`.

| Addr HEX | Addr DEC | Code | Meaning | Scale | Range | Access |
|----------|----------|------|---------|-------|-------|--------|
| `0x0646` | 1606 | <a id="reg-1606"></a><a id="pm02"></a>PM02 | Return fan hours | x1 | 0…65535 h | shown R/O, disabled by default |
| `0x0648` | 1608 | <a id="pm03"></a><a id="reg-1608"></a>PM03 | Compressor hours alarm limit | x1 | 0…65535 h | R/W |
| `0x064A` | 1610 | <a id="pm04"></a><a id="reg-1610"></a>PM04 | Compressor hours | x1 | 0…65535 h | shown R/O |
| `0x064F` | 1615 | <a id="pm21"></a><a id="reg-1615"></a>PM21 | Compressor forced | x1 | 0…1  | shown R/O |
| `0x0650` | 1616 | <a id="reg-1616"></a><a id="pm80"></a>PM80 | Room temperature probe offset | x0.1 | -10…10 °C | R/W |
| `0x0651` | 1617 | <a id="reg-1617"></a><a id="pm81"></a>PM81 | Outdoor temperature probe offset | x0.1 | -10…10 °C | R/W |
| `0x0652` | 1618 | <a id="reg-1618"></a><a id="pm82"></a>PM82 | Water temperature probe offset | x0.1 | -10…10 °C | R/W |
| `0x0653` | 1619 | <a id="reg-1619"></a><a id="pm83"></a>PM83 | Exhaust temperature probe offset | x0.1 | -10…10 °C | R/W, disabled by default |
| `0x0654` | 1620 | <a id="reg-1620"></a><a id="pm84"></a>PM84 | Discharge temperature probe offset | x0.1 | -10…10 °C | R/W |
| `0x0655` | 1621 | <a id="reg-1621"></a><a id="pm85"></a>PM85 | Defrost probe offset | x0.1 | -10…10 °C | R/W, disabled by default |
| `0x0656` | 1622 | <a id="reg-1622"></a><a id="pm86"></a>PM86 | Room humidity probe offset | x1 | -10…10 % | R/W |
| `0x0657` | 1623 | <a id="reg-1623"></a><a id="pm87"></a>PM87 | Air quality probe offset | x1 | -100…100 ppm | R/W, disabled by default |
| `0x0658` | 1624 | <a id="reg-1624"></a><a id="pm88"></a>PM88 | Fan potentiometer offset | x1 | -10…10 % | R/W, disabled by default |
| `0x0659` | 1625 | <a id="reg-1625"></a><a id="pm89"></a>PM89 | Pressure probe offset | x0.1 | -20…20 bar | shown R/O, disabled by default |
| `0x065B` | 1627 | <a id="reg-1627"></a><a id="pc01"></a>PC01 | Room temperature sniffing cycles | x1 | 0…1  | R/W 0/1, disabled by default |
| `0x065C` | 1628 | <a id="reg-1628"></a><a id="pc02"></a>PC02 | Sniffing wait time | x1 | 0…999 min | R/W, disabled by default |
| `0x065D` | 1629 | <a id="reg-1629"></a><a id="pc03"></a>PC03 | Sniffing active time | x1 | 1…30 min | R/W, disabled by default |
| `0x065E` | 1630 | <a id="reg-1630"></a><a id="pc04"></a>PC04 | Both fans in sniffing cycle | x1 | 0…1  | R/W 0/1, disabled by default |
| `0x065F` | 1631 | <a id="pc05"></a><a id="reg-1631"></a>PC05 | Season change (0 manual, 1 manual+auto, 2 auto) | x1 | 0…2  | R/W |
| `0x0660` | 1632 | <a id="pc06"></a><a id="reg-1632"></a>PC06 | Auto season probe (0 water, 1 room) | x1 | 0…1  | R/W |
| `0x0661` | 1633 | <a id="pc07"></a><a id="reg-1633"></a>PC07 | Max water temperature for dehumidify / summer integration | x0.1 | 0…70 °C | R/W |
| `0x0662` | 1634 | <a id="pc08"></a><a id="reg-1634"></a>PC08 | Min water temperature for winter integration (below it AL04 blocks heating) | x0.1 | 0…70 °C | R/W |
| `0x0663` | 1635 | <a id="pc09"></a><a id="reg-1635"></a>PC09 | Auto summer above room temperature | x0.1 | 0…70 °C | R/W |
| `0x0664` | 1636 | <a id="pc10"></a><a id="reg-1636"></a>PC10 | Auto winter below room temperature | x0.1 | 0…70 °C | R/W |
| `0x0665` | 1637 | <a id="pf26"></a><a id="reg-1637"></a>PF26 | Supply fan post-run speed | x0.01 | 0…100 % | R/W |
| `0x0667` | 1639 | <a id="reg-1639"></a><a id="pf02"></a>PF02 | Delay between the two fans | x1 | 0…999 s | R/W, disabled by default |
| `0x0669` | 1641 | <a id="reg-1641"></a><a id="pf04"></a>PF04 | Stop supply fan during defrost | x1 | 0…1  | R/W 0/1, disabled by default |
| `0x066A` | 1642 | <a id="reg-1642"></a><a id="pf05"></a>PF05 | Supply fan speed on air quality probe fault | x0.01 | 0…100 % | R/W, disabled by default |
| `0x066D` | 1645 | <a id="pf08"></a><a id="reg-1645"></a>PF08 | Supply fan max speed (VMC) | x0.01 | 0…100 % | R/W |
| `0x0670` | 1648 | <a id="pf11"></a><a id="reg-1648"></a>PF11 | Fan speed step | x1 | 1…100 % | R/W |
| `0x0671` | 1649 | <a id="pf12"></a><a id="reg-1649"></a>PF12 | Room temperature dead band | x0.1 | 0…20 °C | R/W |
| `0x0672` | 1650 | <a id="pf13"></a><a id="reg-1650"></a>PF13 | Fan speed step interval (integration) | x1 | 1…100 s | R/W |
| `0x0674` | 1652 | <a id="reg-1652"></a><a id="pf15"></a>PF15 | Air quality setpoint min | x1 | 1…9999 ppm | R/W, disabled by default |
| `0x0675` | 1653 | <a id="reg-1653"></a><a id="pf16"></a>PF16 | Air quality setpoint max | x1 | 1…9999 ppm | R/W, disabled by default |
| `0x0676` | 1654 | <a id="reg-1654"></a><a id="pf17"></a>PF17 | Air quality setpoint | x1 | 1…9999 ppm | R/W, disabled by default |
| `0x0677` | 1655 | <a id="reg-1655"></a><a id="pf18"></a>PF18 | Air quality dead band | x1 | 0…1000 ppm | R/W, disabled by default |
| `0x0678` | 1656 | <a id="reg-1656"></a><a id="pf19"></a>PF19 | Air quality fan step interval | x1 | 1…100 s | R/W, disabled by default |
| `0x0679` | 1657 | <a id="reg-1657"></a><a id="pf20"></a>PF20 | Defrost fan speed step | x0.01 | 0…100 % | R/W, disabled by default |
| `0x067A` | 1658 | <a id="reg-1658"></a><a id="pf21"></a>PF21 | Defrost fan step interval | x1 | 1…100 s | R/W, disabled by default |
| `0x067B` | 1659 | <a id="reg-1659"></a><a id="pf22"></a>PF22 | Return fan delta in heat-exchanger defrost | x0.01 | 0…100 % | R/W, not exposed |
| `0x067C` | 1660 | <a id="pf23"></a><a id="reg-1660"></a>PF23 | Supply fan speed forced by DI | x0.01 | 0…100 % | R/W |
| `0x067F` | 1663 | <a id="pe01"></a><a id="reg-1663"></a>PE01 | Compressor minimum off time | x1 | 0…999 s | R/W |
| `0x0680` | 1664 | <a id="pe02"></a><a id="reg-1664"></a>PE02 | Compressor minimum on time | x1 | 0…999 s | R/W |
| `0x0681` | 1665 | <a id="pe03"></a><a id="reg-1665"></a>PE03 | Minimum time between compressor starts | x1 | 0…999 s | R/W |
| `0x0682` | 1666 | <a id="pe04"></a><a id="reg-1666"></a>PE04 | Delay fan start to compressor start | x1 | 0…999 s | R/W |
| `0x0683` | 1667 | <a id="pe05"></a><a id="reg-1667"></a>PE05 | Compressor safety-time bypass | x1 | 0…1  | shown R/O |
| `0x0684` | 1668 | <a id="pe06"></a><a id="reg-1668"></a>PE06 | Compressor min output (dehumidify) | x0.01 | 0…100 % | R/W |
| `0x0685` | 1669 | <a id="pe07"></a><a id="reg-1669"></a>PE07 | Compressor max output (dehumidify) | x0.01 | 0…100 % | R/W |
| `0x0686` | 1670 | <a id="pe08"></a><a id="reg-1670"></a>PE08 | Compressor output step | x0.01 | 1…100 % | R/W |
| `0x0687` | 1671 | <a id="pe09"></a><a id="reg-1671"></a>PE09 | Compressor output step interval | x1 | 1…100 s | R/W |
| `0x0688` | 1672 | <a id="reg-1672"></a><a id="pe10"></a>PE10 | Defrost interval | x1 | 1…99 h | R/W, disabled by default |
| `0x0689` | 1673 | <a id="reg-1673"></a><a id="pe11"></a>PE11 | End of defrost setpoint | x0.1 | -15…70 °C | R/W, disabled by default |
| `0x068A` | 1674 | <a id="reg-1674"></a><a id="pe12"></a>PE12 | Maximum defrost time | x1 | 1…99 min | R/W, disabled by default |
| `0x068B` | 1675 | <a id="reg-1675"></a><a id="pe13"></a>PE13 | Dripping time | x1 | 0…15 min | R/W, disabled by default |
| `0x068C` | 1676 | <a id="reg-1676"></a><a id="pe14"></a>PE14 | Defrost interval counting | x1 | 0…2  | R/W, disabled by default |
| `0x068D` | 1677 | <a id="reg-1677"></a><a id="pe15"></a>PE15 | Defrost counting setpoint | x0.1 | -15…70 °C | R/W, disabled by default |
| `0x068E` | 1678 | <a id="reg-1678"></a><a id="pe16"></a>PE16 | Condenser valve switch time | x1 | 0…999 s | R/W |
| `0x068F` | 1679 | <a id="reg-1679"></a><a id="pe17"></a>PE17 | High-pressure pre-alarm setpoint | x0.1 | 16…42 bar | R/W |
| `0x0690` | 1680 | <a id="reg-1680"></a><a id="pe18"></a>PE18 | High-pressure pre-alarm differential | x0.1 | 0.1…10 bar | R/W |
| `0x0691` | 1681 | <a id="reg-1681"></a><a id="pe19"></a>PE19 | Compressor step at high-pressure pre-alarm | x0.01 | 0…100 % | R/W |
| `0x0692` | 1682 | <a id="reg-1682"></a><a id="pe20"></a>PE20 | Step interval at high-pressure pre-alarm | x1 | 1…999 s | R/W |
| `0x0693` | 1683 | <a id="pb01"></a><a id="reg-1683"></a>Pb01 | Water valve close delay | x1 | 0…999 s | R/W |
| `0x0694` | 1684 | <a id="pb02"></a><a id="reg-1684"></a>Pb02 | Valve sniffing active time (temperature alarm) | x1 | 1…999 s | R/W |
| `0x0695` | 1685 | <a id="pb03"></a><a id="reg-1685"></a>Pb03 | Valve sniffing wait time (temperature alarm) | x1 | 1…99 min | R/W |
| `0x0696` | 1686 | <a id="reg-1686"></a><a id="pb04"></a>Pb04 | Preheating setpoint | x0.1 | 0…30 °C | R/W, disabled by default |
| `0x0697` | 1687 | <a id="reg-1687"></a><a id="pb05"></a>Pb05 | Preheating differential | x0.1 | 0.1…20 °C | R/W, disabled by default |
| `0x0698` | 1688 | <a id="reg-1688"></a><a id="pb06"></a>Pb06 | Preheating maximum time | x1 | 0…60 min | R/W, disabled by default |
| `0x069A` | 1690 | <a id="pu03"></a><a id="reg-1690"></a>PU03 | Dehumidify during high-temperature alarm | x1 | 0…1  | R/W 0/1 |
| `0x069B` | 1691 | <a id="reg-1691"></a><a id="pu04"></a>PU04 | Dehumidify during water-flow alarm | x1 | 0…1  | R/W 0/1 |
| `0x069F` | 1695 | <a id="pu08"></a><a id="reg-1695"></a>PU08 | Cold-water-only dehumidify below water temperature | x0.1 | 0…30 °C | R/W |
| `0x06A0` | 1696 | <a id="pu09"></a><a id="reg-1696"></a>PU09 | Compressor as second step | x1 | 0…1  | R/W 0/1 |
| `0x06A1` | 1697 | <a id="pu10"></a><a id="reg-1697"></a>PU10 | Delay before compressor second step | x1 | 0…240 min | R/W |
| `0x06A3` | 1699 | <a id="reg-1699"></a><a id="ps02"></a>PS02 | Outdoor damper pre-start time | x1 | 0…9999 s | R/W, disabled by default |
| `0x06A4` | 1700 | <a id="reg-1700"></a><a id="ps03"></a>PS03 | External damper OFF delay | x1 | 0…9999 s | R/W, not exposed |
| `0x06A5` | 1701 | <a id="reg-1701"></a><a id="ps04"></a>PS04 | External damper min opening | x0.01 | 0…100 % | R/W, disabled by default |
| `0x06A6` | 1702 | <a id="reg-1702"></a><a id="ps05"></a>PS05 | External damper max opening | x0.01 | 0…100 % | R/W, disabled by default |
| `0x06A7` | 1703 | <a id="reg-1703"></a><a id="ps06"></a>PS06 | Free-cooling/heating activation setpoint | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06A8` | 1704 | <a id="reg-1704"></a><a id="ps07"></a>PS07 | Free-cooling/heating differential | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06A9` | 1705 | <a id="reg-1705"></a><a id="ps08"></a>PS08 | External damper step at high humidity | x0.01 | 1…100 % | R/W, disabled by default |
| `0x06AA` | 1706 | <a id="reg-1706"></a><a id="ps09"></a>PS09 | External damper step interval | x1 | 1…100 s | R/W, disabled by default |
| `0x06AB` | 1707 | <a id="reg-1707"></a><a id="pr01"></a>Pr01 | Rotary exchanger setpoint differential | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06AC` | 1708 | <a id="reg-1708"></a><a id="pr02"></a>Pr02 | Rotary exchanger differential | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06AD` | 1709 | <a id="reg-1709"></a><a id="pr03"></a>Pr03 | Exchanger defrost setpoint | x0.1 | -15…70 °C | R/W, disabled by default |
| `0x06AE` | 1710 | <a id="reg-1710"></a><a id="pr04"></a>Pr04 | Exchanger defrost dead band | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06AF` | 1711 | <a id="reg-1711"></a><a id="pr05"></a>Pr05 | Cross-flow bypass cycle time | x1 | 1…99 s | R/W, disabled by default |
| `0x06B0` | 1712 | <a id="reg-1712"></a><a id="pr06"></a>Pr06 | Exchanger stop setpoint | x0.1 | -15…70 °C | R/W, disabled by default |
| `0x06B1` | 1713 | <a id="reg-1713"></a><a id="pr07"></a>Pr07 | Exchanger stop differential | x0.1 | 0…20 °C | R/W, disabled by default |
| `0x06B2` | 1714 | <a id="reg-1714"></a><a id="pr08"></a>Pr08 | Rotary exchanger defrost step | x0.01 | 0…100 % | R/W, disabled by default |
| `0x06B3` | 1715 | <a id="reg-1715"></a><a id="pr09"></a>Pr09 | Rotary exchanger defrost interval | x1 | 1…100 s | R/W, disabled by default |
| `0x06B4` | 1716 | <a id="reg-1716"></a><a id="pr10"></a>Pr10 | Rotary exchanger PWM frequency | x1 | 1…2000 Hz | R/W, disabled by default |
| `0x06B5` | 1717 | <a id="reg-1717"></a><a id="pa01"></a>PA01 | Fan hours alarm | x1 | 0…1  | R/W 0/1 |
| `0x06B6` | 1718 | <a id="reg-1718"></a><a id="pa02"></a>PA02 | Compressor hours alarm | x1 | 0…1  | R/W 0/1 |
| `0x06B7` | 1719 | <a id="reg-1719"></a><a id="pa03"></a>PA03 | Hours alarm relay (0 none, 1 light, 2 serious) | x1 | 0…2  | R/W |
| `0x06B8` | 1720 | <a id="reg-1720"></a><a id="pa04"></a>PA04 | Probe alarm delay | x1 | 0…240 s | R/W |
| `0x06B9` | 1721 | <a id="reg-1721"></a><a id="pa05"></a>PA05 | Probe alarm relay | x1 | 0…2  | R/W |
| `0x06BA` | 1722 | <a id="reg-1722"></a><a id="pa06"></a>PA06 | Air-flow alarm delay after reset | x1 | 0…999 s | R/W |
| `0x06BB` | 1723 | <a id="reg-1723"></a><a id="pa07"></a>PA07 | Air-flow alarm delay | x1 | 0…999 s | R/W |
| `0x06BC` | 1724 | <a id="reg-1724"></a><a id="pa08"></a>PA08 | Air-flow alarm relay | x1 | 0…2  | R/W |
| `0x06BD` | 1725 | <a id="reg-1725"></a><a id="pa09"></a>PA09 | Water-flow alarm delay after reset | x1 | 0…999 s | R/W |
| `0x06BE` | 1726 | <a id="reg-1726"></a><a id="pa10"></a>PA10 | Water-flow alarm delay | x1 | 0…999 s | R/W |
| `0x06BF` | 1727 | <a id="reg-1727"></a><a id="pa11"></a>PA11 | Water-flow alarms per hour before manual reset | x1 | 0…5  | R/W |
| `0x06C0` | 1728 | <a id="reg-1728"></a><a id="pa12"></a>PA12 | Water-flow alarm relay | x1 | 0…2  | R/W |
| `0x06C1` | 1729 | <a id="reg-1729"></a><a id="pa13"></a>PA13 | Filter alarm delay | x1 | 0…999 s | R/W |
| `0x06C2` | 1730 | <a id="reg-1730"></a><a id="pa14"></a>PA14 | Filter alarm reset type | x1 | 0…2  | R/W |
| `0x06C3` | 1731 | <a id="reg-1731"></a><a id="pa15"></a>PA15 | Filter alarm relay | x1 | 0…2  | R/W |
| `0x06C4` | 1732 | <a id="pa16"></a><a id="reg-1732"></a>PA16 | High/low water temperature alarm delay | x1 | 1…999 s | R/W |
| `0x06C5` | 1733 | <a id="pa17"></a><a id="reg-1733"></a>PA17 | High/low water temperature alarm differential | x0.1 | 0.1…10 °C | R/W |
| `0x06C6` | 1734 | <a id="reg-1734"></a><a id="pa18"></a>PA18 | High/low water temperature alarm relay | x1 | 0…2  | R/W |
| `0x06C8` | 1736 | <a id="reg-1736"></a><a id="pa20"></a>PA20 | High humidity warning differential | x1 | 0…100 % | R/W, not exposed |
| `0x06C9` | 1737 | <a id="pa21"></a><a id="reg-1737"></a>PA21 | High humidity time before alarm | x1 | 0…60 min | R/W |
| `0x06CA` | 1738 | <a id="reg-1738"></a><a id="pa22"></a>PA22 | High humidity events | x1 | 0…99  | R/W |
| `0x06CB` | 1739 | <a id="pa23"></a><a id="reg-1739"></a>PA23 | Fan speed sensor alarm delay after reset | x1 | 0…999 s | R/W |
| `0x06CC` | 1740 | <a id="reg-1740"></a><a id="pa24"></a>PA24 | Fan speed sensor alarm delay | x1 | 0…999 s | R/W |
| `0x06CD` | 1741 | <a id="pa25"></a><a id="reg-1741"></a>PA25 | Fan max speed for speed sensor alarm | x1 | 0…9999 rpm | R/W |
| `0x06CE` | 1742 | <a id="reg-1742"></a><a id="pa26"></a>PA26 | Fan alarm relay | x1 | 0…2  | R/W |
| `0x06CF` | 1743 | <a id="reg-1743"></a><a id="pa27"></a>PA27 | Compressor thermal switch alarm delay | x1 | 0…999 s | R/W |
| `0x06D0` | 1744 | <a id="reg-1744"></a><a id="pa28"></a>PA28 | Compressor thermal switch reset type | x1 | 0…2  | R/W |
| `0x06D1` | 1745 | <a id="reg-1745"></a><a id="pa29"></a>PA29 | Compressor thermal switch relay | x1 | 0…2  | R/W |
| `0x06D2` | 1746 | <a id="pa30"></a><a id="reg-1746"></a>PA30 | Low-pressure alarm bypass time | x1 | 0…999 s | R/W |
| `0x06D3` | 1747 | <a id="pa31"></a><a id="reg-1747"></a>PA31 | Low-pressure alarm delay | x1 | 0…999 s | R/W |
| `0x06D4` | 1748 | <a id="pa32"></a><a id="reg-1748"></a>PA32 | Low-pressure alarms per hour before manual reset | x1 | 0…5  | R/W |
| `0x06D5` | 1749 | <a id="reg-1749"></a><a id="pa33"></a>PA33 | High-pressure alarm setpoint | x0.1 | 16…45 bar | R/W |
| `0x06D6` | 1750 | <a id="reg-1750"></a><a id="pa34"></a>PA34 | High-pressure alarm differential | x0.1 | 0.1…10 bar | R/W |
| `0x06D7` | 1751 | <a id="pa35"></a><a id="reg-1751"></a>PA35 | High-pressure alarms per hour before manual reset | x1 | 0…5  | R/W |
| `0x06D8` | 1752 | <a id="reg-1752"></a><a id="pa36"></a>PA36 | Pressure alarm relay | x1 | 0…2  | R/W |
| `0x06D9` | 1753 | <a id="reg-1753"></a><a id="pa37"></a>PA37 | Discharge temperature alarm delay | x1 | 0…999 s | R/W |
| `0x06DA` | 1754 | <a id="reg-1754"></a><a id="pa38"></a>PA38 | Discharge temperature alarm setpoint | x0.1 | 70…140 °C | R/W |
| `0x06DB` | 1755 | <a id="reg-1755"></a><a id="pa39"></a>PA39 | Discharge temperature alarm differential | x0.1 | 10…30 °C | R/W |
| `0x06DC` | 1756 | <a id="reg-1756"></a><a id="pa40"></a>PA40 | Discharge temperature alarms per hour | x1 | 0…5  | R/W |
| `0x06DD` | 1757 | <a id="reg-1757"></a><a id="pa41"></a>PA41 | Discharge temperature alarm relay | x1 | 0…2  | R/W |
| `0x06DE` | 1758 | <a id="pa42"></a><a id="reg-1758"></a>PA42 | Antifreeze alarm delay | x1 | 0…999 s | R/W |
| `0x06DF` | 1759 | <a id="pa43"></a><a id="reg-1759"></a>PA43 | Antifreeze water temperature setpoint | x0.1 | 0…20 °C | R/W |
| `0x06E0` | 1760 | <a id="pa44"></a><a id="reg-1760"></a>PA44 | Antifreeze differential | x0.1 | 0.1…10 °C | R/W |
| `0x06E1` | 1761 | <a id="reg-1761"></a><a id="pa45"></a>PA45 | Antifreeze alarm relay | x1 | 0…2  | R/W |
| `0x06E2` | 1762 | <a id="reg-1762"></a><a id="pa46"></a>PA46 | Fire/smoke alarm type | x1 | 0…1  | R/W, disabled by default |
| `0x06E3` | 1763 | <a id="reg-1763"></a><a id="pa47"></a>PA47 | Fire/smoke alarm relay | x1 | 0…2  | R/W, disabled by default |
| `0x06E4` | 1764 | <a id="reg-1764"></a><a id="pa48"></a>PA48 | Generic warning delay | x1 | 0…999 s | R/W |
| `0x06E5` | 1765 | <a id="reg-1765"></a><a id="pa49"></a>PA49 | Generic warning reset type | x1 | 0…2  | R/W |
| `0x06E6` | 1766 | <a id="reg-1766"></a><a id="pa50"></a>PA50 | Generic alarm delay | x1 | 0…999 s | R/W |
| `0x06E7` | 1767 | <a id="reg-1767"></a><a id="pa51"></a>PA51 | Generic alarm reset type | x1 | 0…2  | R/W |
| `0x06E8` | 1768 | <a id="reg-1768"></a><a id="pa52"></a>PA52 | Clock (RTC) alarm | x1 | 0…1  | R/W 0/1 |
| `0x06E9` | 1769 | <a id="reg-1769"></a><a id="pa53"></a>PA53 | Clock alarm reset type | x1 | 0…2  | R/W |
| `0x06EA` | 1770 | <a id="reg-1770"></a><a id="pa54"></a>PA54 | RTC alarm signal type (0 none, 1 light, 2 serious) | x1 | 0…2  | R/W, not exposed |
| `0x06EB` | 1771 | <a id="reg-1771"></a><a id="pa55"></a>PA55 | Phase sequence alarm relay | x1 | 0…2  | R/W, disabled by default |
| `0x06EC` | 1772 | <a id="reg-1772"></a><a id="pa56"></a>PA56 | Expansion alarm relay | x1 | 0…2  | R/W, disabled by default |
| `0x06ED` | 1773 | <a id="ph11"></a><a id="reg-1773"></a>PH11 | Modbus address | x1 | 1…247  | shown R/O |
| `0x06EE` | 1774 | <a id="reg-1774"></a><a id="ph12"></a>PH12 | Modbus baud rate code | x1 | 0…7  | shown R/O |
| `0x06EF` | 1775 | <a id="reg-1775"></a><a id="ph13"></a>PH13 | Modbus parity code | x1 | 0…2  | shown R/O |
| `0x06F0` | 1776 | <a id="reg-1776"></a><a id="ph14"></a>PH14 | Modbus stop bits code | x1 | 0…1  | shown R/O |
| `0x06F4` | 1780 | <a id="reg-1780"></a><a id="ph04"></a>PH04 | Unit state on holiday (0 off, 1 on) | x1 | 0…1  | R/W |
| `0x06F6` | 1782 | <a id="reg-1782"></a><a id="ph06"></a>PH06 | Pressure unit (0 bar, 1 psi) | x1 | 0…1  | shown R/O |
| `0x06F7` | 1783 | <a id="ph07"></a><a id="reg-1783"></a>PH07 | Summer setpoint min | x0.1 | -15…70 °C | R/W |
| `0x06F8` | 1784 | <a id="ph08"></a><a id="reg-1784"></a>PH08 | Summer setpoint max | x0.1 | -15…70 °C | R/W |
| `0x06F9` | 1785 | <a id="ph09"></a><a id="reg-1785"></a>PH09 | Winter setpoint min | x0.1 | -15…70 °C | R/W |
| `0x06FA` | 1786 | <a id="ph10"></a><a id="reg-1786"></a>PH10 | Winter setpoint max (caps [SEtH](#seth)) | x0.1 | -15…70 °C | R/W |
| `0x06FB` | 1787 | <a id="reg-1787"></a><a id="ph15"></a>PH15 | Restore default | x1 | 0…1  | R/W 0/1, not exposed (restores the factory settings) |
| `0x06FC` | 1788 | <a id="reg-1788"></a><a id="ph16"></a>PH16 | CAN baud rate code | x1 | 1…4  | shown R/O, disabled by default |
| `0x06FD` | 1789 | <a id="ph17"></a><a id="reg-1789"></a>PH17 | CAN node | x1 | 1…127  | shown R/O, disabled by default |
| `0x06FE` | 1790 | <a id="reg-1790"></a><a id="ph18"></a>PH18 | History reset | x1 | 0…1  | R/W 0/1, not exposed (clears the alarm history) |
| `0x06FF` | 1791 | <a id="reg-1791"></a><a id="ph19"></a>PH19 | Air quality probe min | x1 | 0…9999  | shown R/O, disabled by default |
| `0x0700` | 1792 | <a id="reg-1792"></a><a id="ph20"></a>PH20 | Air quality probe max | x1 | 0…9999  | shown R/O, disabled by default |
| `0x0701` | 1793 | <a id="reg-1793"></a><a id="ph21"></a>PH21 | Pressure probe min | x0.1 | 0…87 bar | shown R/O, disabled by default |
| `0x0702` | 1794 | <a id="reg-1794"></a><a id="ph22"></a>PH22 | Pressure probe max | x0.1 | 0…87 bar | shown R/O, disabled by default |
| `0x0703` | 1795 | <a id="reg-1795"></a><a id="ph23"></a>PH23 | EVCO LED | x1 | 0…1  | R/W 0/1, disabled by default |
| `0x0708` | 1800 | <a id="reg-1800"></a><a id="pg04"></a>PG04 | Heat exchanger type | x1 | 0…2  | shown R/O, disabled by default |
| `0x0709` | 1801 | <a id="reg-1801"></a><a id="pg05"></a>PG05 | Expansion module | x1 | 0…1  | shown R/O, disabled by default |
| `0x070C` | 1804 | <a id="ha01"></a><a id="reg-1804"></a>HA01 | AI1 allocation (fan potentiometer) | x1 | 0…60  | shown R/O |
| `0x070F` | 1807 | <a id="ha04"></a><a id="reg-1807"></a>HA04 | AI4 allocation (evaporator temperature) | x1 | 0…52  | shown R/O |
| `0x0710` | 1808 | <a id="ha05"></a><a id="reg-1808"></a>HA05 | AI5 allocation (water temperature) | x1 | 0…52  | shown R/O |
| `0x0711` | 1809 | <a id="ha06"></a><a id="reg-1809"></a>HA06 | AI6 allocation (dehumidify request DI) | x1 | 0…52  | shown R/O |
| `0x0712` | 1810 | <a id="ha07"></a><a id="reg-1810"></a>HA07 | AI7 allocation (integration request DI) | x1 | 0…52  | shown R/O |
| `0x0713` | 1811 | <a id="ha08"></a><a id="reg-1811"></a>HA08 | AI1 Epj allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x0714` | 1812 | <a id="reg-1812"></a><a id="ha09"></a>HA09 | AI2 Epj allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x0715` | 1813 | <a id="reg-1813"></a><a id="ha10"></a>HA10 | AI1 expansion allocation | x1 | 0…60  | shown R/O, disabled by default |
| `0x0716` | 1814 | <a id="reg-1814"></a><a id="ha11"></a>HA11 | AI2 expansion allocation | x1 | 0…60  | shown R/O, disabled by default |
| `0x0717` | 1815 | <a id="reg-1815"></a><a id="ha12"></a>HA12 | AI3 expansion allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x0718` | 1816 | <a id="reg-1816"></a><a id="ha13"></a>HA13 | AI4 expansion allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x0719` | 1817 | <a id="reg-1817"></a><a id="ha14"></a>HA14 | AI5 expansion allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x071A` | 1818 | <a id="reg-1818"></a><a id="ha15"></a>HA15 | AI6 expansion allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x071B` | 1819 | <a id="reg-1819"></a><a id="ha16"></a>HA16 | AI7 expansion allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x071C` | 1820 | <a id="reg-1820"></a><a id="ha17"></a>HA17 | AI1 Evj allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x071D` | 1821 | <a id="ha18"></a><a id="reg-1821"></a>HA18 | AI2 Evj allocation | x1 | 0…52  | shown R/O, disabled by default |
| `0x071E` | 1822 | <a id="hb01"></a><a id="reg-1822"></a>HB01 | DI1 allocation (high pressure) | x1 | 0…46  | shown R/O |
| `0x071F` | 1823 | <a id="hb02"></a><a id="reg-1823"></a>HB02 | DI2 allocation (low pressure) | x1 | 0…46  | shown R/O |
| `0x0722` | 1826 | <a id="hb05"></a><a id="reg-1826"></a>HB05 | DI1 expansion allocation | x1 | 0…46  | shown R/O, disabled by default |
| `0x0723` | 1827 | <a id="reg-1827"></a><a id="hb06"></a>HB06 | DI2 expansion allocation | x1 | 0…46  | shown R/O, disabled by default |
| `0x0724` | 1828 | <a id="hb07"></a><a id="reg-1828"></a>HB07 | DI3 expansion allocation | x1 | 0…46  | shown R/O, disabled by default |
| `0x0725` | 1829 | <a id="reg-1829"></a><a id="hc01"></a>HC01 | AO1 allocation (compressor) | x1 | 0…7  | shown R/O |
| `0x0726` | 1830 | <a id="reg-1830"></a><a id="hc02"></a>HC02 | AO2 allocation | x1 | 0…7  | shown R/O |
| `0x0727` | 1831 | <a id="hc03"></a><a id="reg-1831"></a>HC03 | AO3 allocation | x1 | 0…7  | shown R/O |
| `0x0729` | 1833 | <a id="reg-1833"></a><a id="hc05"></a>HC05 | AO1 expansion allocation | x1 | 0…7  | shown R/O, disabled by default |
| `0x072A` | 1834 | <a id="reg-1834"></a><a id="hc06"></a>HC06 | AO2 expansion allocation | x1 | 0…7  | shown R/O, disabled by default |
| `0x072B` | 1835 | <a id="reg-1835"></a><a id="hcf1"></a>HCF1 | Supply fan PWM frequency | x1 | 10…2000 Hz | shown R/O, disabled by default |
| `0x072C` | 1836 | <a id="reg-1836"></a><a id="hcf2"></a>HCF2 | Return fan PWM frequency | x1 | 10…2000 Hz | shown R/O, disabled by default |
| `0x072D` | 1837 | <a id="reg-1837"></a><a id="hcf3"></a>HCF3 | Compressor PWM frequency | x1 | 10…2000 Hz | shown R/O, disabled by default |
| `0x072F` | 1839 | <a id="reg-1839"></a><a id="hd02"></a>HD02 | DO2 allocation (serious alarm) | x1 | 0…30  | shown R/O |
| `0x0730` | 1840 | <a id="reg-1840"></a><a id="hd03"></a>HD03 | DO3 allocation (VMC contact) | x1 | 0…30  | shown R/O |
| `0x0731` | 1841 | <a id="reg-1841"></a><a id="hd04"></a>HD04 | DO4 allocation (water condensation valve) | x1 | 0…30  | shown R/O |
| `0x0732` | 1842 | <a id="hd05"></a><a id="reg-1842"></a>HD05 | DO5 allocation (external water valve / pump) | x1 | 0…30  | shown R/O |
| `0x0733` | 1843 | <a id="reg-1843"></a><a id="hd06"></a>HD06 | DO6 allocation (compressor) | x1 | 0…30  | shown R/O |
| `0x0734` | 1844 | <a id="reg-1844"></a><a id="hd07"></a>HD07 | DO1 expansion allocation | x1 | 0…30  | shown R/O, disabled by default |
| `0x0735` | 1845 | <a id="reg-1845"></a><a id="hd08"></a>HD08 | DO2 expansion allocation | x1 | 0…30  | shown R/O, disabled by default |
| `0x0736` | 1846 | <a id="reg-1846"></a><a id="hd09"></a>HD09 | DO3 expansion allocation | x1 | 0…30  | shown R/O, disabled by default |
| `0x0737` | 1847 | <a id="reg-1847"></a><a id="hd10"></a>HD10 | DO4 expansion allocation | x1 | 0…30  | shown R/O, disabled by default |
| `0x0738` | 1848 | <a id="reg-1848"></a><a id="hd11"></a>HD11 | Open-collector expansion allocation | x1 | 0…30  | shown R/O, disabled by default |
| `0x0739` | 1849 | <a id="pb07"></a><a id="reg-1849"></a>Pb07 | Anti-stagnation valve active time | x1 | 1…999 s | R/W |
| `0x073A` | 1850 | <a id="pb08"></a><a id="reg-1850"></a>Pb08 | Anti-stagnation valve wait time | x1 | 1…99 min | R/W |
| `0x073B` | 1851 | <a id="pe21"></a><a id="reg-1851"></a>PE21 | Compressor min output (integration) | x0.01 | 0…100 % | R/W |
| `0x073E` | 1854 | <a id="reg-1854"></a><a id="pf29"></a>PF29 | Return fan min speed | x0.01 | 0…100 % | R/W, disabled by default |
| `0x073F` | 1855 | <a id="reg-1855"></a><a id="pf30"></a>PF30 | Return fan max speed | x0.01 | 0…100 % | R/W, disabled by default |
| `0x0740` | 1856 | <a id="pf31"></a><a id="reg-1856"></a>PF31 | Integration fan control (0 temperature, 1 max of manual/remote, 2 max of all) | x1 | 0…2  | R/W |
| `0x0741` | 1857 | <a id="reg-1857"></a><a id="pf32"></a>PF32 | Return fan speed forced by DI | x0.01 | 0…100 % | R/W, disabled by default |
| `0x0742` | 1858 | <a id="reg-1858"></a><a id="pm22"></a>PM22 | Return fan manual setpoint | x0.01 | 0…100 % | R/W, disabled by default |
| `0x0746` | 1862 | <a id="reg-1862"></a><a id="pf33"></a>PF33 | Return fan speed on air quality probe fault | x0.01 | 0…100 % | R/W, disabled by default |
| `0x0747` | 1863 | <a id="reg-1863"></a><a id="pf34"></a>PF34 | Return fan post-run speed | x0.01 | 0…100 % | R/W, disabled by default |
| `0x0748` | 1864 | <a id="reg-1864"></a><a id="pm91"></a>PM91 | Free-cooling probe offset | x0.1 | -10…10 °C | R/W, disabled by default |
| `0x0749` | 1865 | <a id="reg-1865"></a><a id="pm92"></a>PM92 | Evaporator probe offset | x0.1 | -10…10 °C | R/W |
| `0x074A` | 1866 | <a id="reg-1866"></a><a id="ph24"></a>PH24 | Evaporation pressure probe min | x0.1 | 0…87 bar | shown R/O, disabled by default |
| `0x074B` | 1867 | <a id="reg-1867"></a><a id="ph25"></a>PH25 | Evaporation pressure probe max | x0.1 | 0…87 bar | shown R/O, disabled by default |
| `0x074C` | 1868 | <a id="reg-1868"></a><a id="ph26"></a>PH26 | Refrigerant code | x1 | 0…19  | shown R/O |
| `0x074F` | 1871 | <a id="pe22"></a><a id="reg-1871"></a>PE22 | Compressor max output (integration) | x0.01 | 0…100 % | R/W |
| `0x0750` | 1872 | <a id="reg-1872"></a><a id="pe23"></a>PE23 | Modulating compressor integration differential | x0.1 | 0.1…36.0 | R/W, not exposed |
| `0x0751` | 1873 | <a id="pu11"></a><a id="reg-1873"></a>PU11 | Evaporator temperature setpoint | x0.1 | 0…68 °C | R/W |
| `0x0752` | 1874 | <a id="pu12"></a><a id="reg-1874"></a>PU12 | Evaporator dead band | x0.1 | 0.1…18 °C | R/W |
| `0x0754` | 1876 | <a id="pa57"></a><a id="reg-1876"></a>PA57 | High humidity alarm type (0 display, 1 blocking) | x1 | 0…1  | R/W |
| `0x0755` | 1877 | <a id="pa58"></a><a id="reg-1877"></a>PA58 | Max dehumidify time forced by DI | x1 | 0…999 min | R/W |
| `0x0757` | 1879 | <a id="pe24"></a><a id="reg-1879"></a>PE24 | Compressor speed ramp | x0.1 | 0…20 rps | R/W |
| `0x0758` | 1880 | <a id="pe25"></a><a id="reg-1880"></a>PE25 | Compressor ramp-down on alarm or off | x0.1 | 0…20 rps | R/W |
| `0x0759` | 1881 | <a id="pe26"></a><a id="reg-1881"></a>PE26 | Ramp to and from minimum step | x0.1 | 0…20 rps | R/W |
| `0x075A` | 1882 | <a id="pe27"></a><a id="reg-1882"></a>PE27 | Compressor max speed | x1 | 0…200 rps | R/W |
| `0x075B` | 1883 | <a id="pe28"></a><a id="reg-1883"></a>PE28 | Compressor step 1 speed | x1 | 0…200 rps | R/W |
| `0x075C` | 1884 | <a id="reg-1884"></a><a id="pe29"></a>PE29 | Compressor step 2 speed | x1 | 0…200 rps | R/W, not exposed |
| `0x075D` | 1885 | <a id="pe30"></a><a id="reg-1885"></a>PE30 | Minimum time at step 1 | x1 | 0…255 s | R/W |
| `0x075E` | 1886 | <a id="pe31"></a><a id="reg-1886"></a>PE31 | Minimum time at step 2 | x1 | 0…255 s | R/W |
| `0x075F` | 1887 | <a id="pe32"></a><a id="reg-1887"></a>PE32 | Maximum time below step 1 | x1 | 0…255 s | R/W |
| `0x0760` | 1888 | <a id="pe33"></a><a id="reg-1888"></a>PE33 | Compressor speed (rps) control | x1 | 0…1  | R/W 0/1 |
| `0x0763` | 1891 | <a id="reg-1891"></a><a id="pa59"></a>PA59 | Alarm relay (0 always, 1 summer only) | x1 | 0…1  | R/W |
| `0x0768` | 1896 | <a id="pa60"></a><a id="reg-1896"></a>PA60 | Auto-reset delay of high humidity block | x1 | 0…9999 s | R/W |
| `0x0769` | 1897 | <a id="reg-1897"></a><a id="pt01"></a>PT01 | Test mode enabled | x1 | 0…1  | shown R/O, disabled by default |
| `0x076A` | 1898 | <a id="reg-1898"></a><a id="pt02"></a>PT02 | Supply fan speed in test mode | x0.01 | 0…100 % | shown R/O, disabled by default |
| `0x076B` | 1899 | <a id="reg-1899"></a><a id="pt03"></a>PT03 | Return fan speed in test mode | x0.01 | 0…100 % | shown R/O, disabled by default |
| `0x076C` | 1900 | <a id="reg-1900"></a><a id="pt04"></a>PT04 | External damper in test mode | x0.01 | 0…100 % | shown R/O, disabled by default |
| `0x076D` | 1901 | <a id="reg-1901"></a><a id="pt05"></a>PT05 | Recirculation damper relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x076E` | 1902 | <a id="reg-1902"></a><a id="pt06"></a>PT06 | Serious alarm relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x076F` | 1903 | <a id="reg-1903"></a><a id="pt07"></a>PT07 | Free-cooling/heating bypass relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0770` | 1904 | <a id="reg-1904"></a><a id="pt08"></a>PT08 | Water condensation valve relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0771` | 1905 | <a id="reg-1905"></a><a id="pt09"></a>PT09 | Water valve relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0772` | 1906 | <a id="reg-1906"></a><a id="ph31"></a>PH31 | Epj Graph backlight mode (1 on, 2 timed) | x1 | 1…2  | R/W, not exposed |
| `0x0773` | 1907 | <a id="reg-1907"></a><a id="ph32"></a>PH32 | Epj Graph backlight timeout | x1 | 0…240  | R/W, not exposed |
| `0x0774` | 1908 | <a id="reg-1908"></a><a id="ph33"></a>PH33 | Epj Graph on/off LED | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0775` | 1909 | <a id="reg-1909"></a><a id="ph34"></a>PH34 | Epj Graph alarm LED | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0776` | 1910 | <a id="reg-1910"></a><a id="pa61"></a>PA61 | External damper limitation differential | x1 | 0…20  | R/W, not exposed |
| `0x0777` | 1911 | <a id="reg-1911"></a><a id="pa62"></a>PA62 | Maximum dehumidify time from DI/BMS for the external damper limitation | x1 | 0…999  | R/W, not exposed |
| `0x0778` | 1912 | <a id="reg-1912"></a><a id="pt10"></a>PT10 | Compressor relay in test mode | x1 | 0…1  | R/W 0/1, not exposed |
| `0x0779` | 1913 | <a id="reg-1913"></a><a id="pt11"></a>PT11 | Compressor percentage in test mode | x0.01 | 0…100 % | R/W, not exposed |
| `0x077A` | 1914 | <a id="reg-1914"></a><a id="ph35"></a>PH35 | Summer/winter icon (0 sun = summer, 1 sun = winter) | x1 | 0…1  | R/W 0/1, not exposed |

---

## 17. Other registers of the manual

The rest of the manual's register list. None of them has a Home Assistant
entity; they are here so that the reference is complete and every address in
the manual resolves. A date or time is a 32-bit value in two words (low word
at the lower address); the manual gives the range but not the encoding.

### 17.1 Clock, holiday and hour-counter words

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x044D` | 1101 | <a id="reg-1101"></a>`CLOCK_RTC (Low)` | R/W | 01.01.2000 … 19.01.2068 03:14:07 | Real-time clock, low word of a 32-bit value |
| `0x044E` | 1102 | <a id="reg-1102"></a>`CLOCK_RTC (High)` | R/W |  | Real-time clock, high word |
| `0x0453` | 1107 | <a id="reg-1107"></a>`StartHoliday_BMS` | R/W | 0–1 | Start the holiday period |
| `0x0454` | 1108 | <a id="reg-1108"></a>`Holiday_end (Low)` | R/O | 01.01.2000 … 19.01.2068 03:14:07 | Holiday end date, low word of a 32-bit value |
| `0x0455` | 1109 | <a id="reg-1109"></a>`Holiday_end (High)` | R/O |  | Holiday end date, high word |
| `0x05D9` | 1497 | <a id="reg-1497"></a>`Holiday_Days` | R/W | 0–255 | Holiday period, days |
| `0x05DA` | 1498 | <a id="reg-1498"></a>`Holiday_Hours` | R/W | 0–23 | Holiday period, hours |
| `0x0643` | 1603 | <a id="reg-1603"></a>`PM00_Limit_FansHours (High)` | R/W |  | High word of [PM00](#pm00) (hours, whole hours in one word on the reference unit) |
| `0x0645` | 1605 | <a id="reg-1605"></a>`PM01_SupplyFan_Hours (High)` | R/W |  | High word of [PM01](#pm01) |
| `0x0647` | 1607 | <a id="reg-1607"></a>`PM02_ReturnFan_Hours (High)` | R/W |  | High word of [PM02](#pm02) |
| `0x0649` | 1609 | <a id="reg-1609"></a>`PM03_Limit_CmpHours (High)` | R/W |  | High word of [PM03](#pm03) |
| `0x064B` | 1611 | <a id="reg-1611"></a>`PM04_Cmp_Hours (High)` | R/W |  | High word of [PM04](#pm04) |
| `0x064C` | 1612 | <a id="reg-1612"></a><a id="pm90"></a>`PM90_LastMaintainDate (Low)` | R/W | 01.01.2008 00:00:01 … 19.01.2068 03:14:07 | Last maintenance date, low word of a 32-bit value |
| `0x064D` | 1613 | <a id="reg-1613"></a>`PM90_LastMaintainDate (High)` | R/W |  | Last maintenance date, high word |

The manual lists every hour counter ([PM00](#pm00)–[PM04](#pm04)) as a 32-bit
value in two words with the unit "hours ×10"; on the reference unit the low
word holds whole hours and the odd neighbours read 0
([UNIT_BEHAVIOUR T29](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware)).

### 17.2 Time programs

Four daily time bands (F1 to F4) for each weekday. A mode register holds
`0=Disable`, `1=OFF`, `2=Comfort`, `3=Economy` or `4=Night`; a start time of
day takes two words (low word first). The time programs are enabled with
[PH03](#ph03). The active band is [1106](#reg-1106).

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x05DB` | 1499 | <a id="reg-1499"></a>`F1_Monday_p1` | R/W | 0–4 | Monday F1 mode |
| `0x05DC` | 1500 | <a id="reg-1500"></a>`F1_Monday_h1` (Low) | R/W | 0:00:00–23:59:59 | Monday F1 start time, low word |
| `0x05DD` | 1501 | <a id="reg-1501"></a>`F1_Monday_h1` (High) | R/W | | Monday F1 start time, high word |
| `0x05DE` | 1502 | <a id="reg-1502"></a>`F2_Monday_p2` | R/W | 0–4 | Monday F2 mode |
| `0x05DF` | 1503 | <a id="reg-1503"></a>`F2_Monday_h2` (Low) | R/W | 0:00:00–23:59:59 | Monday F2 start time, low word |
| `0x05E0` | 1504 | <a id="reg-1504"></a>`F2_Monday_h2` (High) | R/W | | Monday F2 start time, high word |
| `0x05E1` | 1505 | <a id="reg-1505"></a>`F3_Monday_p3` | R/W | 0–4 | Monday F3 mode |
| `0x05E2` | 1506 | <a id="reg-1506"></a>`F3_Monday_h3` (Low) | R/W | 0:00:00–23:59:59 | Monday F3 start time, low word |
| `0x05E3` | 1507 | <a id="reg-1507"></a>`F3_Monday_h3` (High) | R/W | | Monday F3 start time, high word |
| `0x05E4` | 1508 | <a id="reg-1508"></a>`F4_Monday_p4` | R/W | 0–4 | Monday F4 mode |
| `0x05E5` | 1509 | <a id="reg-1509"></a>`F4_Monday_h4` (Low) | R/W | 0:00:00–23:59:59 | Monday F4 start time, low word |
| `0x05E6` | 1510 | <a id="reg-1510"></a>`F4_Monday_h4` (High) | R/W | | Monday F4 start time, high word |
| `0x05E7` | 1511 | <a id="reg-1511"></a>`F1_Tuesday_p1` | R/W | 0–4 | Tuesday F1 mode |
| `0x05E8` | 1512 | <a id="reg-1512"></a>`F1_Tuesday_h1` (Low) | R/W | 0:00:00–23:59:59 | Tuesday F1 start time, low word |
| `0x05E9` | 1513 | <a id="reg-1513"></a>`F1_Tuesday_h1` (High) | R/W | | Tuesday F1 start time, high word |
| `0x05EA` | 1514 | <a id="reg-1514"></a>`F2_Tuesday_p2` | R/W | 0–4 | Tuesday F2 mode |
| `0x05EB` | 1515 | <a id="reg-1515"></a>`F2_Tuesday_h2` (Low) | R/W | 0:00:00–23:59:59 | Tuesday F2 start time, low word |
| `0x05EC` | 1516 | <a id="reg-1516"></a>`F2_Tuesday_h2` (High) | R/W | | Tuesday F2 start time, high word |
| `0x05ED` | 1517 | <a id="reg-1517"></a>`F3_Tuesday_p3` | R/W | 0–4 | Tuesday F3 mode |
| `0x05EE` | 1518 | <a id="reg-1518"></a>`F3_Tuesday_h3` (Low) | R/W | 0:00:00–23:59:59 | Tuesday F3 start time, low word |
| `0x05EF` | 1519 | <a id="reg-1519"></a>`F3_Tuesday_h3` (High) | R/W | | Tuesday F3 start time, high word |
| `0x05F0` | 1520 | <a id="reg-1520"></a>`F4_Tuesday_p4` | R/W | 0–4 | Tuesday F4 mode |
| `0x05F1` | 1521 | <a id="reg-1521"></a>`F4_Tuesday_h4` (Low) | R/W | 0:00:00–23:59:59 | Tuesday F4 start time, low word |
| `0x05F2` | 1522 | <a id="reg-1522"></a>`F4_Tuesday_h4` (High) | R/W | | Tuesday F4 start time, high word |
| `0x05F3` | 1523 | <a id="reg-1523"></a>`F1_Wednesday_p1` | R/W | 0–4 | Wednesday F1 mode |
| `0x05F4` | 1524 | <a id="reg-1524"></a>`F1_Wednesday_h1` (Low) | R/W | 0:00:00–23:59:59 | Wednesday F1 start time, low word |
| `0x05F5` | 1525 | <a id="reg-1525"></a>`F1_Wednesday_h1` (High) | R/W | | Wednesday F1 start time, high word |
| `0x05F6` | 1526 | <a id="reg-1526"></a>`F2_Wednesday_p2` | R/W | 0–4 | Wednesday F2 mode |
| `0x05F7` | 1527 | <a id="reg-1527"></a>`F2_Wednesday_h2` (Low) | R/W | 0:00:00–23:59:59 | Wednesday F2 start time, low word |
| `0x05F8` | 1528 | <a id="reg-1528"></a>`F2_Wednesday_h2` (High) | R/W | | Wednesday F2 start time, high word |
| `0x05F9` | 1529 | <a id="reg-1529"></a>`F3_Wednesday_p3` | R/W | 0–4 | Wednesday F3 mode |
| `0x05FA` | 1530 | <a id="reg-1530"></a>`F3_Wednesday_h3` (Low) | R/W | 0:00:00–23:59:59 | Wednesday F3 start time, low word |
| `0x05FB` | 1531 | <a id="reg-1531"></a>`F3_Wednesday_h3` (High) | R/W | | Wednesday F3 start time, high word |
| `0x05FC` | 1532 | <a id="reg-1532"></a>`F4_Wednesday_p4` | R/W | 0–4 | Wednesday F4 mode |
| `0x05FD` | 1533 | <a id="reg-1533"></a>`F4_Wednesday_h4` (Low) | R/W | 0:00:00–23:59:59 | Wednesday F4 start time, low word |
| `0x05FE` | 1534 | <a id="reg-1534"></a>`F4_Wednesday_h4` (High) | R/W | | Wednesday F4 start time, high word |
| `0x05FF` | 1535 | <a id="reg-1535"></a>`F1_Thursday_p1` | R/W | 0–4 | Thursday F1 mode |
| `0x0600` | 1536 | <a id="reg-1536"></a>`F1_Thursday_h1` (Low) | R/W | 0:00:00–23:59:59 | Thursday F1 start time, low word |
| `0x0601` | 1537 | <a id="reg-1537"></a>`F1_Thursday_h1` (High) | R/W | | Thursday F1 start time, high word |
| `0x0602` | 1538 | <a id="reg-1538"></a>`F2_Thursday_p2` | R/W | 0–4 | Thursday F2 mode |
| `0x0603` | 1539 | <a id="reg-1539"></a>`F2_Thursday_h2` (Low) | R/W | 0:00:00–23:59:59 | Thursday F2 start time, low word |
| `0x0604` | 1540 | <a id="reg-1540"></a>`F2_Thursday_h2` (High) | R/W | | Thursday F2 start time, high word |
| `0x0605` | 1541 | <a id="reg-1541"></a>`F3_Thursday_p3` | R/W | 0–4 | Thursday F3 mode |
| `0x0606` | 1542 | <a id="reg-1542"></a>`F3_Thursday_h3` (Low) | R/W | 0:00:00–23:59:59 | Thursday F3 start time, low word |
| `0x0607` | 1543 | <a id="reg-1543"></a>`F3_Thursday_h3` (High) | R/W | | Thursday F3 start time, high word |
| `0x0608` | 1544 | <a id="reg-1544"></a>`F4_Thursday_p4` | R/W | 0–4 | Thursday F4 mode |
| `0x0609` | 1545 | <a id="reg-1545"></a>`F4_Thursday_h4` (Low) | R/W | 0:00:00–23:59:59 | Thursday F4 start time, low word |
| `0x060A` | 1546 | <a id="reg-1546"></a>`F4_Thursday_h4` (High) | R/W | | Thursday F4 start time, high word |
| `0x060B` | 1547 | <a id="reg-1547"></a>`F1_Friday_p1` | R/W | 0–4 | Friday F1 mode |
| `0x060C` | 1548 | <a id="reg-1548"></a>`F1_Friday_h1` (Low) | R/W | 0:00:00–23:59:59 | Friday F1 start time, low word |
| `0x060D` | 1549 | <a id="reg-1549"></a>`F1_Friday_h1` (High) | R/W | | Friday F1 start time, high word |
| `0x060E` | 1550 | <a id="reg-1550"></a>`F2_Friday_p2` | R/W | 0–4 | Friday F2 mode |
| `0x060F` | 1551 | <a id="reg-1551"></a>`F2_Friday_h2` (Low) | R/W | 0:00:00–23:59:59 | Friday F2 start time, low word |
| `0x0610` | 1552 | <a id="reg-1552"></a>`F2_Friday_h2` (High) | R/W | | Friday F2 start time, high word |
| `0x0611` | 1553 | <a id="reg-1553"></a>`F3_Friday_p3` | R/W | 0–4 | Friday F3 mode |
| `0x0612` | 1554 | <a id="reg-1554"></a>`F3_Friday_h3` (Low) | R/W | 0:00:00–23:59:59 | Friday F3 start time, low word |
| `0x0613` | 1555 | <a id="reg-1555"></a>`F3_Friday_h3` (High) | R/W | | Friday F3 start time, high word |
| `0x0614` | 1556 | <a id="reg-1556"></a>`F4_Friday_p4` | R/W | 0–4 | Friday F4 mode |
| `0x0615` | 1557 | <a id="reg-1557"></a>`F4_Friday_h4` (Low) | R/W | 0:00:00–23:59:59 | Friday F4 start time, low word |
| `0x0616` | 1558 | <a id="reg-1558"></a>`F4_Friday_h4` (High) | R/W | | Friday F4 start time, high word |
| `0x0617` | 1559 | <a id="reg-1559"></a>`F1_Saturday_p1` | R/W | 0–4 | Saturday F1 mode |
| `0x0618` | 1560 | <a id="reg-1560"></a>`F1_Saturday_h1` (Low) | R/W | 0:00:00–23:59:59 | Saturday F1 start time, low word |
| `0x0619` | 1561 | <a id="reg-1561"></a>`F1_Saturday_h1` (High) | R/W | | Saturday F1 start time, high word |
| `0x061A` | 1562 | <a id="reg-1562"></a>`F2_Saturday_p2` | R/W | 0–4 | Saturday F2 mode |
| `0x061B` | 1563 | <a id="reg-1563"></a>`F2_Saturday_h2` (Low) | R/W | 0:00:00–23:59:59 | Saturday F2 start time, low word |
| `0x061C` | 1564 | <a id="reg-1564"></a>`F2_Saturday_h2` (High) | R/W | | Saturday F2 start time, high word |
| `0x061D` | 1565 | <a id="reg-1565"></a>`F3_Saturday_p3` | R/W | 0–4 | Saturday F3 mode |
| `0x061E` | 1566 | <a id="reg-1566"></a>`F3_Saturday_h3` (Low) | R/W | 0:00:00–23:59:59 | Saturday F3 start time, low word |
| `0x061F` | 1567 | <a id="reg-1567"></a>`F3_Saturday_h3` (High) | R/W | | Saturday F3 start time, high word |
| `0x0620` | 1568 | <a id="reg-1568"></a>`F4_Saturday_p4` | R/W | 0–4 | Saturday F4 mode |
| `0x0621` | 1569 | <a id="reg-1569"></a>`F4_Saturday_h4` (Low) | R/W | 0:00:00–23:59:59 | Saturday F4 start time, low word |
| `0x0622` | 1570 | <a id="reg-1570"></a>`F4_Saturday_h4` (High) | R/W | | Saturday F4 start time, high word |
| `0x0623` | 1571 | <a id="reg-1571"></a>`F1_Sunday_p1` | R/W | 0–4 | Sunday F1 mode |
| `0x0624` | 1572 | <a id="reg-1572"></a>`F1_Sunday_h1` (Low) | R/W | 0:00:00–23:59:59 | Sunday F1 start time, low word |
| `0x0625` | 1573 | <a id="reg-1573"></a>`F1_Sunday_h1` (High) | R/W | | Sunday F1 start time, high word |
| `0x0626` | 1574 | <a id="reg-1574"></a>`F2_Sunday_p2` | R/W | 0–4 | Sunday F2 mode |
| `0x0627` | 1575 | <a id="reg-1575"></a>`F2_Sunday_h2` (Low) | R/W | 0:00:00–23:59:59 | Sunday F2 start time, low word |
| `0x0628` | 1576 | <a id="reg-1576"></a>`F2_Sunday_h2` (High) | R/W | | Sunday F2 start time, high word |
| `0x0629` | 1577 | <a id="reg-1577"></a>`F3_Sunday_p3` | R/W | 0–4 | Sunday F3 mode |
| `0x062A` | 1578 | <a id="reg-1578"></a>`F3_Sunday_h3` (Low) | R/W | 0:00:00–23:59:59 | Sunday F3 start time, low word |
| `0x062B` | 1579 | <a id="reg-1579"></a>`F3_Sunday_h3` (High) | R/W | | Sunday F3 start time, high word |
| `0x062C` | 1580 | <a id="reg-1580"></a>`F4_Sunday_p4` | R/W | 0–4 | Sunday F4 mode |
| `0x062D` | 1581 | <a id="reg-1581"></a>`F4_Sunday_h4` (Low) | R/W | 0:00:00–23:59:59 | Sunday F4 start time, low word |
| `0x062E` | 1582 | <a id="reg-1582"></a>`F4_Sunday_h4` (High) | R/W | | Sunday F4 start time, high word |

### 17.3 Band setpoints

The comfort, economy and night bands of the time programs, and the supply-fan
and return-fan setpoints of each band. The summer and winter setpoints are
[SEtC](#setc) and [SEtH](#seth).

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x0633` | 1587 | <a id="reg-1587"></a><a id="scc"></a>`SCC_Comfort_SetpointCold` | R/W | −15.0…158.0 °C (×0.1) | Comfort band cooling setpoint |
| `0x0634` | 1588 | <a id="reg-1588"></a><a id="sch"></a>`SCH_Comfort_SetpointHot` | R/W | −15.0…158.0 °C (×0.1) | Comfort band heating setpoint |
| `0x0635` | 1589 | <a id="reg-1589"></a><a id="oec"></a>`OEC_Economy_OffsetCold` | R/W | −36.0…36.0 K (×0.1) | Economy band cooling offset |
| `0x0636` | 1590 | <a id="reg-1590"></a><a id="oeh"></a>`OEH_Economy_OffsetHot` | R/W | −36.0…36.0 K (×0.1) | Economy band heating offset |
| `0x0637` | 1591 | <a id="reg-1591"></a><a id="onc"></a>`ONC_Night_OffsetCold` | R/W | −36.0…36.0 K (×0.1) | Night band cooling offset |
| `0x0638` | 1592 | <a id="reg-1592"></a><a id="onh"></a>`ONH_Night_OffsetHot` | R/W | −36.0…36.0 K (×0.1) | Night band heating offset |
| `0x0639` | 1593 | <a id="reg-1593"></a><a id="sdc"></a>`SDC_SetpointCold_DI` | R/W | −15.0…158.0 °C (×0.1) | Cooling setpoint forced by a digital input |
| `0x063A` | 1594 | <a id="reg-1594"></a><a id="sdh"></a>`SDH_SetpointHot_DI` | R/W | −15.0…158.0 °C (×0.1) | Heating setpoint forced by a digital input |
| `0x063B` | 1595 | <a id="reg-1595"></a><a id="fsc"></a>`FSC_SupplyFan_Comfort` | R/W | 0–100 % (×0.01) | Comfort band supply-fan setpoint |
| `0x063C` | 1596 | <a id="reg-1596"></a><a id="fse"></a>`FSE_SupplyFan_Economy` | R/W | 0–100 % (×0.01) | Economy band supply-fan setpoint |
| `0x063D` | 1597 | <a id="reg-1597"></a><a id="fsn"></a>`FSN_SupplyFan_Night` | R/W | 0–100 % (×0.01) | Night band supply-fan setpoint |
| `0x0743` | 1859 | <a id="reg-1859"></a><a id="frc"></a>`FRC_ReturnFan_Comfort` | R/W | 0–100 % (×0.01) | Comfort band return-fan setpoint |
| `0x0744` | 1860 | <a id="reg-1860"></a><a id="fre"></a>`FRE_ReturnFan_Economy` | R/W | 0–100 % (×0.01) | Economy band return-fan setpoint |
| `0x0745` | 1861 | <a id="reg-1861"></a><a id="frn"></a>`FRN_ReturnFan_Night` | R/W | 0–100 % (×0.01) | Night band return-fan setpoint |

### 17.4 Display settings

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x063E` | 1598 | <a id="reg-1598"></a><a id="bkm"></a>`BKM_EvjBacklightMode` | R/W | 0–3 | Evj/Epj LCD backlight mode |
| `0x063F` | 1599 | <a id="reg-1599"></a><a id="bku"></a>`BKU_EvjBacklightPerc` | R/W | 0–100 % | Evj/Epj LCD backlight percentage |
| `0x0640` | 1600 | <a id="reg-1600"></a><a id="bkt"></a>`BKT_EvjBacklightTimeout` | R/W | 0–241 | Evj/Epj LCD backlight timeout |
| `0x0767` | 1895 | <a id="reg-1895"></a><a id="lng"></a>`LNG_Language` | R/W | 0–2 | Display language: `0=English`, `1=Italiano`, `2=Spanish` |

### 17.5 Passwords

| Addr HEX | Addr DEC | Name | R/W | Range | Meaning |
|----------|----------|------|-----|-------|---------|
| `0x0641` | 1601 | <a id="reg-1601"></a><a id="psd1"></a>`PSd1_UserPassword` | R/W | −999…9999 | User password |
| `0x065A` | 1626 | <a id="reg-1626"></a><a id="psd2"></a>`PSd2_MaintainPassword` | R/W | −999…9999 | Maintenance password |
| `0x0704` | 1796 | <a id="reg-1796"></a><a id="psd3"></a>`PSd3_InstallerPassword` | R/W | −999…9999 | Installer password |
| `0x070A` | 1802 | <a id="reg-1802"></a><a id="psd4"></a>`PSd4_CostructorPassword` | R/W | −999…9999 | Manufacturer password |
| `0x0753` | 1875 | <a id="reg-1875"></a><a id="psdm"></a>`PSdM_ImportExportPassword` | R/W | −999…9999 | Import/export parameters password |
