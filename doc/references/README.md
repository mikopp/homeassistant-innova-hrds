# References — HRDS+

Manufacturer documentation for the **hej.luft HRDS+** air-dehumidification
module for residential ventilation systems (made by INNOVA S.r.l.), plus the
repository's own distilled references.

## Which file answers what

Each topic has exactly one home. Other files link to it instead of repeating
it.

| Topic | File |
|-------|------|
| **How the unit behaves**: variants, states, start/stop sequences, summer/winter, display/probe configurations, fan, compressor, water circuit, alarm effects, display and Modbus actions, what was tested on real hardware | [`UNIT_BEHAVIOUR.md`](UNIT_BEHAVIOUR.md) |
| **Which registers exist**: addresses, names, encodings, ranges, value meanings, write recipes | [`MODBUS_REGISTERS.md`](MODBUS_REGISTERS.md) |
| Technical data (airflow, capacity, power) and the fan-speed → airflow estimate | this file, below |
| What the Home Assistant integration does on top of the unit, and why | [`../adr/`](../adr/README.md) (decisions), [`../../README.md`](../../README.md) (users) |
| Open hardware questions and test plans | [`../../plans/todo.md`](../../plans/todo.md) |

## Source documents

| File | What it is | Cited as |
|------|------------|----------|
| [HRDS+_Technisches_Handbuch_DE.pdf](HRDS+_Technisches_Handbuch_DE.pdf) | Technical handbook (German, 89 pp, Stand Sept. 2026): operating modes (§2.7), terminals (§4.4–4.5), parameter list with defaults (§5.3), control logic (§6), alarms (§7), commissioning (§8), technical data (§10). Search the `.txt`, check tables here. | `[HB n]` |
| [HRDS+_Technisches_Handbuch_DE.txt](HRDS+_Technisches_Handbuch_DE.txt) | Full text of the handbook (`pdftotext`), for searching. Tables are flattened; check the PDF for column alignment. | `[HB n]` |
| [HRDS+_Modbus_RTU_RS485_DE.pdf](HRDS+_Modbus_RTU_RS485_DE.pdf) | Modbus RTU/RS-485 connection and register manual (German, Stand Mai 2026). Source of every register address. | `[MB p.n]` |
| [HRDS+_Benutzerhandbuch_DE.pdf](HRDS+_Benutzerhandbuch_DE.pdf) | End-user handbook (German, 12 pp, Stand August 2026); a subset of the technical handbook. | `[HB n]` |
| [HRDS+_Hydraulikplaene_DE.pdf](HRDS+_Hydraulikplaene_DE.pdf) | Hydraulic plans (German, 13 pp, Stand Aug. 2026): decision tree and the integration variants 1–9 (heating/cooling circuit, brine circuit, special cases); the same variants as HB §3.8. | `[HB 3.8]` |
| [HRDS_CE_Konformitaetserklaerung_Innova.pdf](HRDS_CE_Konformitaetserklaerung_Innova.pdf) | EU declaration of conformity by INNOVA S.r.l. (Storo, 20 Jan 2024) for the dehumidification units HRDS (codes DHAD…) and HRDS+ (codes DHAI…). | — |
| [Vortice_HRDS_Libretto_IT-EN_2024.pdf](Vortice_HRDS_Libretto_IT-EN_2024.pdf), [Vortice_CNU_21607_Libretto_IT-EN_2019.pdf](Vortice_CNU_21607_Libretto_IT-EN_2019.pdf) | Vortice HRDS 30 / 50 (R) DC instruction booklet (Italian/English, 23 Feb 2024) and the manual of its CNU wall panel, code 21607 (2019). The same unit with an on/off compressor, see [the same unit under other names](../tested-setups.md#the-same-unit-under-other-names). Background only. | — |
| [VMCGroup_MDR_K_Manuale_IT_2020.pdf](VMCGroup_MDR_K_Manuale_IT_2020.pdf) | VMC Group MDR K / MDR K R manual (Italian, 2020): type code, terminals, CNU menus and alarm list of the same on/off unit. Background only. | — |

All manuals come from the hej.luft download page,
[hejluft.at/hrds](https://www.hejluft.at/hrds).
The file links there change with every new edition, so the copies here carry
the edition (Stand) instead. The Vortice and VMC Group manuals come from
[vortice.it](https://www.vortice.it/it/vmc_recupero_calore/moduli-aggiuntivi-da-condotto/per-deumidificazione)
and [vmcgroup.it/download](https://www.vmcgroup.it/download). Online EVCO controller manuals do not match the
Innova firmware of the unit and are not used.

The vendor's and other users' statements from the energiesparhaus.at HRDS+
forum thread are quoted with their post numbers in
[`UNIT_BEHAVIOUR.md` §13](UNIT_BEHAVIOUR.md#13-evidence-log-what-was-seen-on-real-hardware).

## Technical data (airflow, capacity, power)

From the technical handbook §10, p.80 ("Leistungsdaten Luftaufbereitung" /
"Elektrische Daten"). The two columns are the **30** and **50** variants.

| Spec | HRDS+ 30 | HRDS+ 50 |
|------|---------:|---------:|
| **Nominal total airflow (supply + recirc)** | **300 m³/h** | **500 m³/h** |
| External share (supply from the MVHR) | 0–300 m³/h | 0–500 m³/h |
| **Recirculation share (room air via own fan)** | **130–300 m³/h** | **190–500 m³/h** |
| Register-pack pressure drop @ nominal | 31 Pa | 38 Pa |
| Usable dehumidification capacity ¹ | 56 L/24h | 89 L/24h |
| Total cooling capacity ¹ | 2.59 kW | 3.95 kW |
| Compressor frequency range | 23–63 Hz | 23–78 Hz |
| **Max. electrical power (operating)** | **800 W** | **1110 W** |
| — compressor max. | 690 W | 950 W |
| — **recirc fan max.** | **90 W** | **150 W** |
| Sound pressure @ 3 m | 39.5 dB(A) | 40.8 dB(A) |
| Weight (with recirc / without) | 46 / 43 kg | 57 / 54 kg |

¹ At nominal airflow and the reference conditions footnoted in the handbook.

The handbook table prints the pressure drop as kPa; its curve (§10.3.1, p.83)
shows about 31 Pa at 300 m³/h and 38 Pa at 500 m³/h, so the unit is Pa.

The 130–300 / 190–500 m³/h recirculation band is the **tested operating
range** from the performance spec, not a firmware floor: the fan minimum during
dehumidification and integration is [PF28](MODBUS_REGISTERS.md#pf28) / [PF27](MODBUS_REGISTERS.md#pf27), factory 50 %, settable
down to 0 % (HB 5.3, §6.2). The total flow (supply + recirc) should not exceed
the nominal 300 / 500 m³/h; above it efficiency drops, noise rises and the
supply ducts must be sized for it (HB 3.7.1, p.24).

### Dehumidification capacity vs. airflow

From the per-flow performance tables (HB §10.1 / §10.2, p.81 / p.82, reference inlet
conditions):

| Airflow | HRDS+ 30 dehum. | HRDS+ 50 dehum. |
|--------:|----------------:|----------------:|
| 150 m³/h | 31.2 L/d | — |
| 200 m³/h | 41.1 L/d | 42.6 L/d |
| 250 m³/h | 50.7 L/d | — |
| 300 m³/h | 54.4 L/d | 62.4 L/d |
| 400 m³/h | — | 81.1 L/d |
| 500 m³/h | — | 83.2 L/d |

## Translating fan speed to airflow

The unit has **no airflow register**; it cannot measure its own m³/h. It
reports the fan's analog output `outAO_SupplyFan` ([639](MODBUS_REGISTERS.md#reg-639), %) and its speed
`actRPMsupplyFan` ([1117](MODBUS_REGISTERS.md#reg-1117), rpm) [MB p.8, p.15].

The handbook's performance curves (§10.3, p.83–84) are pressure-vs-flow system
curves, not an RPM-vs-flow table, so there is no published conversion. An
estimate with the **fan affinity law** (for a centrifugal EC fan on a fixed
duct, flow is proportional to speed, `Q ∝ N`) [our derivation, not from the
handbook]:

```
m³/h  ≈  (RPM / RPM_max) × Q_max  ≈  (output% / 100) × Q_max
```

* `Q_max` = the variant's recirculation maximum, 300 (HRDS+ 30) / [500](MODBUS_REGISTERS.md#reg-500) (HRDS+ 50).
* `RPM_max` = the speed at 100 % output; not published, calibrate once.
* When the fan is off (`SupplyFan_Status` reads OFF), its share is 0 m³/h;
  only the MVHR's passive flow passes, which the unit cannot see.

Accuracy: the affinity law only holds at constant duct resistance. A loaded
filter or long, narrow ducts move less air at the same speed (see the
available-pressure curves, p.81). For better accuracy, fit a line through two
known balanced flows from the MVHR commissioning report. Treat the result as
indicative, not metered.
