# hej.luft parameter values: HRDS+

hej.luft's value for every HRDS+ parameter, per firmware and size, the
parameter files that hold them, and how to load them. Registers (address,
scale, range) are in [`MODBUS_REGISTERS.md`](MODBUS_REGISTERS.md), what the unit does with them in
[`UNIT_BEHAVIOUR.md`](UNIT_BEHAVIOUR.md), and where a handbook default differs in
[§15](UNIT_BEHAVIOUR.md#15-parameters-source-default-and-shipped-value) there. Cited as `[FW]` (provided by hej.luft) and `[VC]` (confirmed by
the vendor).

## Parameter files

| Firmware | HRDS+ 30 | HRDS+ 50 |
|----------|----------|----------|
| 9.3 / 9.4 | [with display](parameter-files/fw9.3/HRDS+30_CNU2_May2026.map), [without](parameter-files/fw9.3/HRDS+30_noDisplay_May2026.map) | [with display](parameter-files/fw9.3/HRDS+50_CNU2_May2026.map), [without](parameter-files/fw9.3/HRDS+50_noDisplay_May2026.map) |
| 9.2 | [with display](parameter-files/fw9.2/HRDS+30_CNU2_FW9.2.map), [without](parameter-files/fw9.2/HRDS+30_noDisplay_FW9.2.map) | [with display](parameter-files/fw9.2/HRDS+50_CNU2_FW9.2.map), [without](parameter-files/fw9.2/HRDS+50_noDisplay_FW9.2.map) |

* The 9.3 files are hej.luft's (May 2026) [FW]. The 9.2 files are made here from
  them by setting [Pb01](MODBUS_REGISTERS.md#pb01) to 30 s, hej.luft's 9.2 value; nothing else differs between
  the two firmware versions. Both use the same parameter definitions, so the
  9.2 files should load on 9.2 [INFERRED].
* "Without display" sets [PH01](MODBUS_REGISTERS.md#ph01) to Disabled and [HA00](MODBUS_REGISTERS.md#ha00) to None; otherwise the
  files with and without display are the same.
* Two values in hej.luft's 9.3 files differ from the table below: [Pb01](MODBUS_REGISTERS.md#pb01) is
  255 s (table: 250 s), and [PH19](MODBUS_REGISTERS.md#ph19) is 16 in the HRDS+ 50 files (table: 18).
* The files are for the EVCO Parameters Manager, which also needs hej.luft's
  parameter definitions (`Drv970AA09`). Both, and the firmware, come from
  hej.luft.

## Loading the values

A firmware update resets every parameter to the controller's generic defaults,
which do not suit the HRDS+, so the parameters must be loaded afterwards [FW],
either:

* with the EVCO Parameters Manager over USB: connect with "USBAdapter", open
  the file for the size and display, Device → Program [FW]; or
* over Modbus: every parameter is a holding register at the address in the
  table, so the values can be written one by one [VC]. Write the Modbus
  address and baud rate last, if at all: changing them cuts the connection.
  Written values are kept across a power cycle
  ([`UNIT_BEHAVIOUR.md` §3.6](UNIT_BEHAVIOUR.md#36-persistence-across-a-power-cycle)).

If the display loops on "checking 20k, 50k, 125k, 500k …" after the update,
loading a parameter file fixes it [FW].

## Sizes

* The HRDS+ 30 and 50 differ only in [PE07](MODBUS_REGISTERS.md#pe07) / [PE22](MODBUS_REGISTERS.md#pe22), the maximum compressor
  output (55 % and 68 %), and in [PH19](MODBUS_REGISTERS.md#ph19), which hej.luft uses as size code
  (16 = HRDS+ 30, 18 = HRDS+ 50; the HRDS+ has no air-quality probe) [FW, VC].
* ¹ Older units can carry the set of an earlier size: [PE07](MODBUS_REGISTERS.md#pe07) / [PE22](MODBUS_REGISTERS.md#pe22) 50 % or
  62 %, size code 15 or 17. Same hardware; current units should carry the
  HRDS+ 30 or 50 set [VC].
* There are no values for the HRDS with an on/off compressor [VC].

## Firmware 9.2 and 9.3 / 9.4

* The values differ only in [Pb01](MODBUS_REGISTERS.md#pb01), the valve off delay: 30 s on 9.2, 250 s on
  9.3 / 9.4 [FW, VC]. Why, and a workaround for 9.2:
  [`UNIT_BEHAVIOUR.md` §1.2](UNIT_BEHAVIOUR.md#12-what-differs-between-the-variants).
* In every file [PH02](MODBUS_REGISTERS.md#ph02) is Disabled and [PH27](MODBUS_REGISTERS.md#ph27) / [PH28](MODBUS_REGISTERS.md#ph28) are Enabled: after loading
  one, on/off over Modbus is off.
* [PF27](MODBUS_REGISTERS.md#pf27) / [PF28](MODBUS_REGISTERS.md#pf28), the minimum fan speed, are 50 %; 30 % has been used at
  commissioning without problems [VC].

## Parameter definitions

The parameter definitions (`Drv970`) exist in several revisions; the values and
files here are for revision `AA09` [FW].

## Every parameter

Values as the Parameters Manager shows them. "(30)" / "(50)": HRDS+ 30 /
HRDS+ 50. Run-time values (working hours, last maintenance, manual requests)
are not parameters and not part of the files, so they are not listed.

| Address | Parameter | FW 9.2 | FW 9.3 / 9.4 | Note |
|---------|-----------|--------|--------------|------|
| [1497](MODBUS_REGISTERS.md#reg-1497) | Holiday period days | 7 | 7 |  |
| [1498](MODBUS_REGISTERS.md#reg-1498) | Holiday period hours | 0 | 0 |  |
| [1499](MODBUS_REGISTERS.md#reg-1499) | F1 mode | Comfort | Comfort |  |
| [1500](MODBUS_REGISTERS.md#reg-1500) | F1 starting hours | 06:00 | 06:00 |  |
| [1502](MODBUS_REGISTERS.md#reg-1502) | F2 mode | Economy | Economy |  |
| [1503](MODBUS_REGISTERS.md#reg-1503) | F2 starting hours | 07:30 | 07:30 |  |
| [1505](MODBUS_REGISTERS.md#reg-1505) | F3 mode | Comfort | Comfort |  |
| [1506](MODBUS_REGISTERS.md#reg-1506) | F3 starting hours | 17:00 | 17:00 |  |
| [1508](MODBUS_REGISTERS.md#reg-1508) | F4 mode | Night | Night |  |
| [1509](MODBUS_REGISTERS.md#reg-1509) | F4 starting hours | 21:00 | 21:00 |  |
| [1511](MODBUS_REGISTERS.md#reg-1511) | F1 mode | Comfort | Comfort |  |
| [1512](MODBUS_REGISTERS.md#reg-1512) | F1 starting hours | 06:00 | 06:00 |  |
| [1514](MODBUS_REGISTERS.md#reg-1514) | F2 mode | Economy | Economy |  |
| [1515](MODBUS_REGISTERS.md#reg-1515) | F2 starting hours | 07:30 | 07:30 |  |
| [1517](MODBUS_REGISTERS.md#reg-1517) | F3 mode | Comfort | Comfort |  |
| [1518](MODBUS_REGISTERS.md#reg-1518) | F3 starting hours | 17:00 | 17:00 |  |
| [1520](MODBUS_REGISTERS.md#reg-1520) | F4 mode | Night | Night |  |
| [1521](MODBUS_REGISTERS.md#reg-1521) | F4 starting hours | 21:00 | 21:00 |  |
| [1523](MODBUS_REGISTERS.md#reg-1523) | F1 mode | Comfort | Comfort |  |
| [1524](MODBUS_REGISTERS.md#reg-1524) | F1 starting hours | 06:00 | 06:00 |  |
| [1526](MODBUS_REGISTERS.md#reg-1526) | F2 mode | Economy | Economy |  |
| [1527](MODBUS_REGISTERS.md#reg-1527) | F2 starting hours | 07:30 | 07:30 |  |
| [1529](MODBUS_REGISTERS.md#reg-1529) | F3 mode | Comfort | Comfort |  |
| [1530](MODBUS_REGISTERS.md#reg-1530) | F3 starting hours | 17:00 | 17:00 |  |
| [1532](MODBUS_REGISTERS.md#reg-1532) | F4 mode | Night | Night |  |
| [1533](MODBUS_REGISTERS.md#reg-1533) | F4 starting hours | 21:00 | 21:00 |  |
| [1535](MODBUS_REGISTERS.md#reg-1535) | F1 mode | Comfort | Comfort |  |
| [1536](MODBUS_REGISTERS.md#reg-1536) | F1 starting hours | 06:00 | 06:00 |  |
| [1538](MODBUS_REGISTERS.md#reg-1538) | F2 mode | Economy | Economy |  |
| [1539](MODBUS_REGISTERS.md#reg-1539) | F2 starting hours | 07:30 | 07:30 |  |
| [1541](MODBUS_REGISTERS.md#reg-1541) | F3 mode | Comfort | Comfort |  |
| [1542](MODBUS_REGISTERS.md#reg-1542) | F3 starting hours | 17:00 | 17:00 |  |
| [1544](MODBUS_REGISTERS.md#reg-1544) | F4 mode | Night | Night |  |
| [1545](MODBUS_REGISTERS.md#reg-1545) | F4 starting hours | 21:00 | 21:00 |  |
| [1547](MODBUS_REGISTERS.md#reg-1547) | F1 mode | Comfort | Comfort |  |
| [1548](MODBUS_REGISTERS.md#reg-1548) | F1 starting hours | 06:00 | 06:00 |  |
| [1550](MODBUS_REGISTERS.md#reg-1550) | F2 mode | Economy | Economy |  |
| [1551](MODBUS_REGISTERS.md#reg-1551) | F2 starting hours | 07:30 | 07:30 |  |
| [1553](MODBUS_REGISTERS.md#reg-1553) | F3 mode | Comfort | Comfort |  |
| [1554](MODBUS_REGISTERS.md#reg-1554) | F3 starting hours | 17:00 | 17:00 |  |
| [1556](MODBUS_REGISTERS.md#reg-1556) | F4 mode | Night | Night |  |
| [1557](MODBUS_REGISTERS.md#reg-1557) | F4 starting hours | 21:00 | 21:00 |  |
| [1559](MODBUS_REGISTERS.md#reg-1559) | F1 mode | Comfort | Comfort |  |
| [1560](MODBUS_REGISTERS.md#reg-1560) | F1 starting hours | 06:00 | 06:00 |  |
| [1562](MODBUS_REGISTERS.md#reg-1562) | F2 mode | Economy | Economy |  |
| [1563](MODBUS_REGISTERS.md#reg-1563) | F2 starting hours | 07:30 | 07:30 |  |
| [1565](MODBUS_REGISTERS.md#reg-1565) | F3 mode | Comfort | Comfort |  |
| [1566](MODBUS_REGISTERS.md#reg-1566) | F3 starting hours | 12:00 | 12:00 |  |
| [1568](MODBUS_REGISTERS.md#reg-1568) | F4 mode | Night | Night |  |
| [1569](MODBUS_REGISTERS.md#reg-1569) | F4 starting hours | 21:00 | 21:00 |  |
| [1571](MODBUS_REGISTERS.md#reg-1571) | F1 mode | Economy | Economy |  |
| [1572](MODBUS_REGISTERS.md#reg-1572) | F1 starting hours | 04:00 | 04:00 |  |
| [1574](MODBUS_REGISTERS.md#reg-1574) | F2 mode | Comfort | Comfort |  |
| [1575](MODBUS_REGISTERS.md#reg-1575) | F2 starting hours | 06:00 | 06:00 |  |
| [1577](MODBUS_REGISTERS.md#reg-1577) | F3 mode | Economy | Economy |  |
| [1578](MODBUS_REGISTERS.md#reg-1578) | F3 starting hours | 20:00 | 20:00 |  |
| [1580](MODBUS_REGISTERS.md#reg-1580) | F4 mode | Night | Night |  |
| [1581](MODBUS_REGISTERS.md#reg-1581) | F4 starting hours | 21:00 | 21:00 |  |
| [1583](MODBUS_REGISTERS.md#reg-1583) | `MOdE` Summer/Winter mode | Summer | Summer |  |
| [1584](MODBUS_REGISTERS.md#reg-1584) | `SEtC` Summer setpoint | 24.0 °C | 24.0 °C |  |
| [1585](MODBUS_REGISTERS.md#reg-1585) | `SEtH` Winter setpoint | 14.0 °C | 14.0 °C |  |
| [1586](MODBUS_REGISTERS.md#reg-1586) | [PU01](MODBUS_REGISTERS.md#pu01) Humidity setpoint | 55 % | 55 % |  |
| [1587](MODBUS_REGISTERS.md#reg-1587) | `SCC` Comfort band cooling setpoint | 24.0 °C | 24.0 °C |  |
| [1588](MODBUS_REGISTERS.md#reg-1588) | `SCH` Comfort band heating setpoint | 14.0 °C | 14.0 °C |  |
| [1589](MODBUS_REGISTERS.md#reg-1589) | `OEC` Economy band cooling offset | 1.0 °C | 1.0 °C |  |
| [1590](MODBUS_REGISTERS.md#reg-1590) | `OEH` Economy band heating offset | -1.0 °C | -1.0 °C |  |
| [1591](MODBUS_REGISTERS.md#reg-1591) | `ONC` Night band cooling offset | 2.0 °C | 2.0 °C |  |
| [1592](MODBUS_REGISTERS.md#reg-1592) | `ONH` Night band heating offset | -2.0 °C | -2.0 °C |  |
| [1593](MODBUS_REGISTERS.md#reg-1593) | `SDC` Cooling setpoint forced by DI | 26.0 °C | 26.0 °C |  |
| [1594](MODBUS_REGISTERS.md#reg-1594) | `SDH` Heating setpoint forced by DI | 14.0 °C | 14.0 °C |  |
| [1595](MODBUS_REGISTERS.md#reg-1595) | `FSC` Comfort band supply fan setpoint | 60.00 % | 60.00 % |  |
| [1596](MODBUS_REGISTERS.md#reg-1596) | `FSE` Economy band supply fan setpoint | 50.00 % | 50.00 % |  |
| [1597](MODBUS_REGISTERS.md#reg-1597) | `FSN` Night band supply fan setpoint | 40.00 % | 40.00 % |  |
| [1598](MODBUS_REGISTERS.md#reg-1598) | `BKM` Evj/Epj LCD backlight mode | 2 | 2 |  |
| [1599](MODBUS_REGISTERS.md#reg-1599) | `BKU` Evj/Epj LCD backlight percentage | 15 % | 15 % |  |
| [1600](MODBUS_REGISTERS.md#reg-1600) | `BKT` Evj/Epj LCD backlight timeout | 30 s | 30 s |  |
| [1601](MODBUS_REGISTERS.md#reg-1601) | `PSd1` User password | 0 | 0 |  |
| [1602](MODBUS_REGISTERS.md#reg-1602) | [PM00](MODBUS_REGISTERS.md#pm00) Supply fan working hours limit | 20000 h | 20000 h |  |
| [1608](MODBUS_REGISTERS.md#reg-1608) | [PM03](MODBUS_REGISTERS.md#pm03) Compressor working hours limit | 20000 h | 20000 h |  |
| [1616](MODBUS_REGISTERS.md#reg-1616) | [PM80](MODBUS_REGISTERS.md#pm80) Return/Room T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1617](MODBUS_REGISTERS.md#reg-1617) | [PM81](MODBUS_REGISTERS.md#pm81) Outdoor T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1618](MODBUS_REGISTERS.md#reg-1618) | [PM82](MODBUS_REGISTERS.md#pm82) Water T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1619](MODBUS_REGISTERS.md#reg-1619) | [PM83](MODBUS_REGISTERS.md#pm83) Exhaust T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1620](MODBUS_REGISTERS.md#reg-1620) | [PM84](MODBUS_REGISTERS.md#pm84) Discharge T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1621](MODBUS_REGISTERS.md#reg-1621) | [PM85](MODBUS_REGISTERS.md#pm85) Compressor defrost T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1622](MODBUS_REGISTERS.md#reg-1622) | [PM86](MODBUS_REGISTERS.md#pm86) Room/return H. probe calibration | 0 % | 0 % |  |
| [1623](MODBUS_REGISTERS.md#reg-1623) | [PM87](MODBUS_REGISTERS.md#pm87) Air quality probe calibration | 0 ppm | 0 ppm |  |
| [1624](MODBUS_REGISTERS.md#reg-1624) | [PM88](MODBUS_REGISTERS.md#pm88) Fans potentiometer calibration | 0.00 % | 0.00 % |  |
| [1625](MODBUS_REGISTERS.md#reg-1625) | [PM89](MODBUS_REGISTERS.md#pm89) High pressure probe calibration | 0.0 bar | 0.0 bar |  |
| [1626](MODBUS_REGISTERS.md#reg-1626) | `PSd2` Maintenance password | 1 | 1 |  |
| [1627](MODBUS_REGISTERS.md#reg-1627) | [PC01](MODBUS_REGISTERS.md#pc01) Enable sniffing mode | Disabled | Disabled |  |
| [1628](MODBUS_REGISTERS.md#reg-1628) | [PC02](MODBUS_REGISTERS.md#pc02) Sniffing cycle wait time | 15 min | 15 min |  |
| [1629](MODBUS_REGISTERS.md#reg-1629) | [PC03](MODBUS_REGISTERS.md#pc03) Sniffing cycle active time | 1 min | 1 min |  |
| [1630](MODBUS_REGISTERS.md#reg-1630) | [PC04](MODBUS_REGISTERS.md#pc04) Enable both fans for sniffing cycle | Enabled | Enabled |  |
| [1631](MODBUS_REGISTERS.md#reg-1631) | [PC05](MODBUS_REGISTERS.md#pc05) Operating mode change type | Manual | Manual |  |
| [1632](MODBUS_REGISTERS.md#reg-1632) | [PC06](MODBUS_REGISTERS.md#pc06) Changeover probe | T. water | T. water |  |
| [1633](MODBUS_REGISTERS.md#reg-1633) | [PC07](MODBUS_REGISTERS.md#pc07) Summer commutation setpoint water probe | 30.0 °C | 30.0 °C |  |
| [1634](MODBUS_REGISTERS.md#reg-1634) | [PC08](MODBUS_REGISTERS.md#pc08) Winter commutation setpoint water probe | 20.0 °C | 20.0 °C |  |
| [1635](MODBUS_REGISTERS.md#reg-1635) | [PC09](MODBUS_REGISTERS.md#pc09) Summer commutation setpoint room probe | 20.0 °C | 20.0 °C |  |
| [1636](MODBUS_REGISTERS.md#reg-1636) | [PC10](MODBUS_REGISTERS.md#pc10) Winter commutation setpoint room probe | 10.0 °C | 10.0 °C |  |
| [1637](MODBUS_REGISTERS.md#reg-1637) | [PF26](MODBUS_REGISTERS.md#pf26) Supply fan post-ventilation speed | 40.00 % | 40.00 % |  |
| [1638](MODBUS_REGISTERS.md#reg-1638) | [PF01](MODBUS_REGISTERS.md#pf01) Minimum time fans ON | 10 s | 10 s | Changed with FW 9.2 |
| [1639](MODBUS_REGISTERS.md#reg-1639) | [PF02](MODBUS_REGISTERS.md#pf02) Minimum time between fans startup | 5 s | 5 s |  |
| [1640](MODBUS_REGISTERS.md#reg-1640) | [PF03](MODBUS_REGISTERS.md#pf03) Post-ventilation time | 0 s | 0 s | Changed with FW 9.2. The fan keeps running while the water valve is open, whatever this says |
| [1641](MODBUS_REGISTERS.md#reg-1641) | [PF04](MODBUS_REGISTERS.md#pf04) Stop supply fan on compressor defrost | Disabled | Disabled |  |
| [1642](MODBUS_REGISTERS.md#reg-1642) | [PF05](MODBUS_REGISTERS.md#pf05) Force supply fan in error probe | 30.00 % | 30.00 % |  |
| [1644](MODBUS_REGISTERS.md#reg-1644) | [PF07](MODBUS_REGISTERS.md#pf07) Supply fan minimum speed in VMC mode | 20.00 % | 20.00 % |  |
| [1645](MODBUS_REGISTERS.md#reg-1645) | [PF08](MODBUS_REGISTERS.md#pf08) Supply fan maximum speed in VMC mode | 60.00 % | 60.00 % |  |
| [1646](MODBUS_REGISTERS.md#reg-1646) | [PF09](MODBUS_REGISTERS.md#pf09) Supply fan maximum speed in integration mode | 85.00 % | 85.00 % |  |
| [1647](MODBUS_REGISTERS.md#reg-1647) | [PF10](MODBUS_REGISTERS.md#pf10) Supply fan maximum speed in dehumidify | 85.00 % | 85.00 % |  |
| [1648](MODBUS_REGISTERS.md#reg-1648) | [PF11](MODBUS_REGISTERS.md#pf11) Fans speed increase/decrease step number | 7 | 7 |  |
| [1649](MODBUS_REGISTERS.md#reg-1649) | [PF12](MODBUS_REGISTERS.md#pf12) Integration dead zone | 0.5 °C | 0.5 °C |  |
| [1650](MODBUS_REGISTERS.md#reg-1650) | [PF13](MODBUS_REGISTERS.md#pf13) Integration inc/dec time | 5 s | 5 s |  |
| [1652](MODBUS_REGISTERS.md#reg-1652) | [PF15](MODBUS_REGISTERS.md#pf15) Air quality setpoint minimum value | 1 ppm | 1 ppm |  |
| [1653](MODBUS_REGISTERS.md#reg-1653) | [PF16](MODBUS_REGISTERS.md#pf16) Air quality setpoint maximum value | 9999 ppm | 9999 ppm |  |
| [1654](MODBUS_REGISTERS.md#reg-1654) | [PF17](MODBUS_REGISTERS.md#pf17) Air quality setpoint | 800 ppm | 800 ppm |  |
| [1655](MODBUS_REGISTERS.md#reg-1655) | [PF18](MODBUS_REGISTERS.md#pf18) Air quality dead zone | 200 ppm | 200 ppm |  |
| [1656](MODBUS_REGISTERS.md#reg-1656) | [PF19](MODBUS_REGISTERS.md#pf19) Air quality inc/dec time | 5 s | 5 s |  |
| [1657](MODBUS_REGISTERS.md#reg-1657) | [PF20](MODBUS_REGISTERS.md#pf20) Heat exchanger defrost inc/dec speed | 5.00 % | 5.00 % |  |
| [1658](MODBUS_REGISTERS.md#reg-1658) | [PF21](MODBUS_REGISTERS.md#pf21) Heat exchanger defrost inc/dec time | 5 s | 5 s |  |
| [1659](MODBUS_REGISTERS.md#reg-1659) | [PF22](MODBUS_REGISTERS.md#pf22) Return fan delta perc. in heat exchanger defrost | 10.00 % | 10.00 % |  |
| [1660](MODBUS_REGISTERS.md#reg-1660) | [PF23](MODBUS_REGISTERS.md#pf23) Supply fan speed forced by DI | 70.00 % | 70.00 % |  |
| [1663](MODBUS_REGISTERS.md#reg-1663) | [PE01](MODBUS_REGISTERS.md#pe01) Compressor minimum off time | 300 s | 300 s |  |
| [1664](MODBUS_REGISTERS.md#reg-1664) | [PE02](MODBUS_REGISTERS.md#pe02) Compressor minimum on time | 20 s | 20 s |  |
| [1665](MODBUS_REGISTERS.md#reg-1665) | [PE03](MODBUS_REGISTERS.md#pe03) Compressor minimum switch-ons time | 420 s | 420 s |  |
| [1666](MODBUS_REGISTERS.md#reg-1666) | [PE04](MODBUS_REGISTERS.md#pe04) Minimum time between fan in dehumidify and compressor start | 120 s | 120 s |  |
| [1667](MODBUS_REGISTERS.md#reg-1667) | [PE05](MODBUS_REGISTERS.md#pe05) Enable security bypass | Disabled | Disabled |  |
| [1668](MODBUS_REGISTERS.md#reg-1668) | [PE06](MODBUS_REGISTERS.md#pe06) Modulating compressor minimum percentage | 20.00 % | 20.00 % |  |
| [1669](MODBUS_REGISTERS.md#reg-1669) | [PE07](MODBUS_REGISTERS.md#pe07) Modulating compressor maximum percentage | 55.00 % (30) / 68.00 % (50) ¹ | 55.00 % (30) / 68.00 % (50) ¹ | Changed with FW 9.2 |
| [1670](MODBUS_REGISTERS.md#reg-1670) | [PE08](MODBUS_REGISTERS.md#pe08) Modulating compressor inc/dec percentage | 1.00 % | 1.00 % |  |
| [1671](MODBUS_REGISTERS.md#reg-1671) | [PE09](MODBUS_REGISTERS.md#pe09) Modulating compressor inc/dec time | 10 s | 10 s |  |
| [1672](MODBUS_REGISTERS.md#reg-1672) | [PE10](MODBUS_REGISTERS.md#pe10) Defrost timeout | 8 h | 8 h |  |
| [1673](MODBUS_REGISTERS.md#reg-1673) | [PE11](MODBUS_REGISTERS.md#pe11) End defrost setpoint | 10.0 °C | 10.0 °C |  |
| [1674](MODBUS_REGISTERS.md#reg-1674) | [PE12](MODBUS_REGISTERS.md#pe12) Defrost maximum time | 1 min | 1 min |  |
| [1675](MODBUS_REGISTERS.md#reg-1675) | [PE13](MODBUS_REGISTERS.md#pe13) Dripping time | 0 min | 0 min |  |
| [1676](MODBUS_REGISTERS.md#reg-1676) | [PE14](MODBUS_REGISTERS.md#pe14) Defrost counting type | T.defrost < set | T.defrost < set |  |
| [1677](MODBUS_REGISTERS.md#reg-1677) | [PE15](MODBUS_REGISTERS.md#pe15) Defrost counting setpoint | 8.0 °C | 8.0 °C |  |
| [1678](MODBUS_REGISTERS.md#reg-1678) | [PE16](MODBUS_REGISTERS.md#pe16) Condensation valves switch time | 10 ×0.1 s | 10 ×0.1 s |  |
| [1679](MODBUS_REGISTERS.md#reg-1679) | [PE17](MODBUS_REGISTERS.md#pe17) High pressure prealarm setpoint | 37.0 bar | 37.0 bar |  |
| [1680](MODBUS_REGISTERS.md#reg-1680) | [PE18](MODBUS_REGISTERS.md#pe18) High pressure prealarm differential | 5.0 bar | 5.0 bar |  |
| [1681](MODBUS_REGISTERS.md#reg-1681) | [PE19](MODBUS_REGISTERS.md#pe19) High pressure prealarm inc/dec percentage | 5.00 % | 5.00 % |  |
| [1682](MODBUS_REGISTERS.md#reg-1682) | [PE20](MODBUS_REGISTERS.md#pe20) High pressure prealarm inc/dec time | 10 s | 10 s |  |
| [1683](MODBUS_REGISTERS.md#reg-1683) | [Pb01](MODBUS_REGISTERS.md#pb01) Water valve off delay | 30 s | 250 s | 9.3 files: 255 s. Why: [`UNIT_BEHAVIOUR.md` §1.2](UNIT_BEHAVIOUR.md#12-what-differs-between-the-variants) |
| [1684](MODBUS_REGISTERS.md#reg-1684) | [Pb02](MODBUS_REGISTERS.md#pb02) Sniffing cycle temperature alarm active time | 60 s | 60 s |  |
| [1685](MODBUS_REGISTERS.md#reg-1685) | [Pb03](MODBUS_REGISTERS.md#pb03) Sniffing cycle temperature alarm wait time | 3 min | 3 min |  |
| [1686](MODBUS_REGISTERS.md#reg-1686) | [Pb04](MODBUS_REGISTERS.md#pb04) Preheating setpoint | 10.0 °C | 10.0 °C |  |
| [1687](MODBUS_REGISTERS.md#reg-1687) | [Pb05](MODBUS_REGISTERS.md#pb05) Preheating differential | 10.0 °C | 10.0 °C |  |
| [1688](MODBUS_REGISTERS.md#reg-1688) | [Pb06](MODBUS_REGISTERS.md#pb06) Preheating maximum time | 0 min | 0 min |  |
| [1689](MODBUS_REGISTERS.md#reg-1689) | [PU02](MODBUS_REGISTERS.md#pu02) Enable winter dehumidification | No | No |  |
| [1690](MODBUS_REGISTERS.md#reg-1690) | [PU03](MODBUS_REGISTERS.md#pu03) Enable dehumidify with high temperature alarm | Disabled | Disabled |  |
| [1691](MODBUS_REGISTERS.md#reg-1691) | [PU04](MODBUS_REGISTERS.md#pu04) Enable dehumidify with water flow alarm | Disabled | Disabled |  |
| [1692](MODBUS_REGISTERS.md#reg-1692) | [PU05](MODBUS_REGISTERS.md#pu05) Force duhumidify with cooling request | Enabled | Enabled |  |
| [1694](MODBUS_REGISTERS.md#reg-1694) | [PU07](MODBUS_REGISTERS.md#pu07) Dehumidify differential | 5 % | 5 % |  |
| [1695](MODBUS_REGISTERS.md#reg-1695) | [PU08](MODBUS_REGISTERS.md#pu08) Only cold water dehumidify setpoint | 10.0 °C | 10.0 °C |  |
| [1696](MODBUS_REGISTERS.md#reg-1696) | [PU09](MODBUS_REGISTERS.md#pu09) Enable compressor as dehumidify second step | Enabled | Enabled |  |
| [1697](MODBUS_REGISTERS.md#reg-1697) | [PU10](MODBUS_REGISTERS.md#pu10) Dehumidify out band time | 120 min | 120 min |  |
| [1698](MODBUS_REGISTERS.md#reg-1698) | [PS01](MODBUS_REGISTERS.md#ps01) Recirculation damper pre-start time | 20 s | 20 s |  |
| [1699](MODBUS_REGISTERS.md#reg-1699) | [PS02](MODBUS_REGISTERS.md#ps02) External damper pre-start time | 20 s | 20 s |  |
| [1700](MODBUS_REGISTERS.md#reg-1700) | [PS03](MODBUS_REGISTERS.md#ps03) External damper delay off | 15 s | 15 s |  |
| [1701](MODBUS_REGISTERS.md#reg-1701) | [PS04](MODBUS_REGISTERS.md#ps04) Modulating external damper minimum opening | 20.00 % | 20.00 % |  |
| [1702](MODBUS_REGISTERS.md#reg-1702) | [PS05](MODBUS_REGISTERS.md#ps05) Modulating external damper maximum opening | 100.00 % | 100.00 % |  |
| [1703](MODBUS_REGISTERS.md#reg-1703) | [PS06](MODBUS_REGISTERS.md#ps06) Free-Cooling/Heating setpoint | 4.0 °C | 4.0 °C |  |
| [1704](MODBUS_REGISTERS.md#reg-1704) | [PS07](MODBUS_REGISTERS.md#ps07) Free-Cooling/Heating differential | 2.0 °C | 2.0 °C |  |
| [1705](MODBUS_REGISTERS.md#reg-1705) | [PS08](MODBUS_REGISTERS.md#ps08) External damper inc/dec perc in high humidity | 5.00 % | 5.00 % |  |
| [1706](MODBUS_REGISTERS.md#reg-1706) | [PS09](MODBUS_REGISTERS.md#ps09) External damper inc/dec time in high humidity | 60 s | 60 s |  |
| [1707](MODBUS_REGISTERS.md#reg-1707) | [Pr01](MODBUS_REGISTERS.md#pr01) Heat exchanger differential setpoint | 5.0 °C | 5.0 °C |  |
| [1708](MODBUS_REGISTERS.md#reg-1708) | [Pr02](MODBUS_REGISTERS.md#pr02) Heat exchanger differential | 3.0 °C | 3.0 °C |  |
| [1709](MODBUS_REGISTERS.md#reg-1709) | [Pr03](MODBUS_REGISTERS.md#pr03) Heat exchanger defrost setpoint | 4.0 °C | 4.0 °C |  |
| [1710](MODBUS_REGISTERS.md#reg-1710) | [Pr04](MODBUS_REGISTERS.md#pr04) Heat exchanger defrost dead zone | 2.0 °C | 2.0 °C |  |
| [1711](MODBUS_REGISTERS.md#reg-1711) | [Pr05](MODBUS_REGISTERS.md#pr05) Heat exchanger by-pass waiting time | 5 min | 5 min |  |
| [1712](MODBUS_REGISTERS.md#reg-1712) | [Pr06](MODBUS_REGISTERS.md#pr06) Setpoint heat exchanger stop for defrost | 2.0 °C | 2.0 °C |  |
| [1713](MODBUS_REGISTERS.md#reg-1713) | [Pr07](MODBUS_REGISTERS.md#pr07) Differential heat exchanger stop for defrost | 3.0 °C | 3.0 °C |  |
| [1714](MODBUS_REGISTERS.md#reg-1714) | [Pr08](MODBUS_REGISTERS.md#pr08) Heat wheel defrost inc/dec percentage | 5.00 % | 5.00 % |  |
| [1715](MODBUS_REGISTERS.md#reg-1715) | [Pr09](MODBUS_REGISTERS.md#pr09) Heat wheel defrost inc/dec time | 5 s | 5 s |  |
| [1716](MODBUS_REGISTERS.md#reg-1716) | [Pr10](MODBUS_REGISTERS.md#pr10) Heat wheel defrost PWM period | 10 Hz | 10 Hz |  |
| [1717](MODBUS_REGISTERS.md#reg-1717) | [PA01](MODBUS_REGISTERS.md#pa01) Enable supply fan working hours alarm | Enabled | Enabled |  |
| [1718](MODBUS_REGISTERS.md#reg-1718) | [PA02](MODBUS_REGISTERS.md#pa02) Enable compressor working hours alarm | Disabled | Disabled |  |
| [1719](MODBUS_REGISTERS.md#reg-1719) | [PA03](MODBUS_REGISTERS.md#pa03) Working hours alarm signal type | Light | Light |  |
| [1720](MODBUS_REGISTERS.md#reg-1720) | [PA04](MODBUS_REGISTERS.md#pa04) Probe alarm delay | 10 s | 10 s |  |
| [1721](MODBUS_REGISTERS.md#reg-1721) | [PA05](MODBUS_REGISTERS.md#pa05) Probe alarm signal type | Light | Light |  |
| [1722](MODBUS_REGISTERS.md#reg-1722) | [PA06](MODBUS_REGISTERS.md#pa06) Air flow switch alarm delay from reset | 30 s | 30 s |  |
| [1723](MODBUS_REGISTERS.md#reg-1723) | [PA07](MODBUS_REGISTERS.md#pa07) Air flow switch alarm delay | 5 s | 5 s |  |
| [1724](MODBUS_REGISTERS.md#reg-1724) | [PA08](MODBUS_REGISTERS.md#pa08) Air flow switch alarm signal type | Serious | Serious |  |
| [1725](MODBUS_REGISTERS.md#reg-1725) | [PA09](MODBUS_REGISTERS.md#pa09) Water flow switch alarm delay from reset | 30 s | 30 s |  |
| [1726](MODBUS_REGISTERS.md#reg-1726) | [PA10](MODBUS_REGISTERS.md#pa10) Water flow switch alarm delay | 5 s | 5 s |  |
| [1727](MODBUS_REGISTERS.md#reg-1727) | [PA11](MODBUS_REGISTERS.md#pa11) Number water flow switch alarm/hour for manual reset | 3 | 3 |  |
| [1728](MODBUS_REGISTERS.md#reg-1728) | [PA12](MODBUS_REGISTERS.md#pa12) Water flow switch alarm signal type | Serious | Serious |  |
| [1729](MODBUS_REGISTERS.md#reg-1729) | [PA13](MODBUS_REGISTERS.md#pa13) Air filter pressure switch alarm delay | 2 s | 2 s |  |
| [1730](MODBUS_REGISTERS.md#reg-1730) | [PA14](MODBUS_REGISTERS.md#pa14) Air filter pressure switch alarm reset type | MANU | MANU |  |
| [1731](MODBUS_REGISTERS.md#reg-1731) | [PA15](MODBUS_REGISTERS.md#pa15) Air filter pressure switch alarm signal type | Light | Light |  |
| [1732](MODBUS_REGISTERS.md#reg-1732) | [PA16](MODBUS_REGISTERS.md#pa16) High/Low temperature alarm delay | 600 s | 600 s |  |
| [1733](MODBUS_REGISTERS.md#reg-1733) | [PA17](MODBUS_REGISTERS.md#pa17) High/Low temperature alarm differential | 2.0 °C | 2.0 °C |  |
| [1734](MODBUS_REGISTERS.md#reg-1734) | [PA18](MODBUS_REGISTERS.md#pa18) High/Low temperature alarm signal type | Light | Light |  |
| [1735](MODBUS_REGISTERS.md#reg-1735) | [PA19](MODBUS_REGISTERS.md#pa19) High humidity warning setpoint | 70 % | 70 % |  |
| [1736](MODBUS_REGISTERS.md#reg-1736) | [PA20](MODBUS_REGISTERS.md#pa20) High humidity warning differential | 5 % | 5 % |  |
| [1737](MODBUS_REGISTERS.md#reg-1737) | [PA21](MODBUS_REGISTERS.md#pa21) High humidity warning outband time | 60 min | 60 min |  |
| [1739](MODBUS_REGISTERS.md#reg-1739) | [PA23](MODBUS_REGISTERS.md#pa23) Fan tacho alarm delay from reset | 30 s | 30 s |  |
| [1740](MODBUS_REGISTERS.md#reg-1740) | [PA24](MODBUS_REGISTERS.md#pa24) Fan tacho alarm delay | 5 s | 5 s |  |
| [1741](MODBUS_REGISTERS.md#reg-1741) | [PA25](MODBUS_REGISTERS.md#pa25) Fan tacho alarm maximum RPM | 1400 rpm | 1400 rpm |  |
| [1742](MODBUS_REGISTERS.md#reg-1742) | [PA26](MODBUS_REGISTERS.md#pa26) Fans alarm signal type | Serious | Serious |  |
| [1743](MODBUS_REGISTERS.md#reg-1743) | [PA27](MODBUS_REGISTERS.md#pa27) Compressor thermal alarm delay | 2 s | 2 s |  |
| [1744](MODBUS_REGISTERS.md#reg-1744) | [PA28](MODBUS_REGISTERS.md#pa28) Compressor thermal alarm reset type | MANU | MANU |  |
| [1745](MODBUS_REGISTERS.md#reg-1745) | [PA29](MODBUS_REGISTERS.md#pa29) Compressor thermal alarm signal type | Serious | Serious |  |
| [1746](MODBUS_REGISTERS.md#reg-1746) | [PA30](MODBUS_REGISTERS.md#pa30) Low pressure alarm bypass time | 120 s | 120 s |  |
| [1747](MODBUS_REGISTERS.md#reg-1747) | [PA31](MODBUS_REGISTERS.md#pa31) Low pressure alarm delay | 30 s | 30 s |  |
| [1748](MODBUS_REGISTERS.md#reg-1748) | [PA32](MODBUS_REGISTERS.md#pa32) Number low pressure alarm/hour for manual reset | 5 | 5 |  |
| [1749](MODBUS_REGISTERS.md#reg-1749) | [PA33](MODBUS_REGISTERS.md#pa33) High pressure alarm setpoint | 42.0 bar | 42.0 bar |  |
| [1750](MODBUS_REGISTERS.md#reg-1750) | [PA34](MODBUS_REGISTERS.md#pa34) High pressure alarm differential | 7.0 bar | 7.0 bar |  |
| [1751](MODBUS_REGISTERS.md#reg-1751) | [PA35](MODBUS_REGISTERS.md#pa35) Number high pressure alarm/hour for manual reset | 5 | 5 |  |
| [1752](MODBUS_REGISTERS.md#reg-1752) | [PA36](MODBUS_REGISTERS.md#pa36) High/Low pressure alarm signal type | Serious | Serious |  |
| [1753](MODBUS_REGISTERS.md#reg-1753) | [PA37](MODBUS_REGISTERS.md#pa37) Discharge high temperature alarm delay | 30 s | 30 s |  |
| [1754](MODBUS_REGISTERS.md#reg-1754) | [PA38](MODBUS_REGISTERS.md#pa38) Discharge high temperature alarm setpoint | 90.0 °C | 90.0 °C |  |
| [1755](MODBUS_REGISTERS.md#reg-1755) | [PA39](MODBUS_REGISTERS.md#pa39) Discharge high temperature alarm differential | 20.0 °C | 20.0 °C |  |
| [1756](MODBUS_REGISTERS.md#reg-1756) | [PA40](MODBUS_REGISTERS.md#pa40) Number discharge high temp alarm/hour for manual reset | 3 | 3 |  |
| [1757](MODBUS_REGISTERS.md#reg-1757) | [PA41](MODBUS_REGISTERS.md#pa41) Discharge high temperature alarm signal type | Serious | Serious |  |
| [1758](MODBUS_REGISTERS.md#reg-1758) | [PA42](MODBUS_REGISTERS.md#pa42) Antifreeze alarm delay | 5 s | 5 s |  |
| [1759](MODBUS_REGISTERS.md#reg-1759) | [PA43](MODBUS_REGISTERS.md#pa43) Antifreeze alarm setpoint | 3.0 °C | 3.0 °C |  |
| [1760](MODBUS_REGISTERS.md#reg-1760) | [PA44](MODBUS_REGISTERS.md#pa44) Antifreeze alarm differential | 2.0 °C | 2.0 °C |  |
| [1761](MODBUS_REGISTERS.md#reg-1761) | [PA45](MODBUS_REGISTERS.md#pa45) Antifreeze alarm signal type | Serious | Serious |  |
| [1762](MODBUS_REGISTERS.md#reg-1762) | [PA46](MODBUS_REGISTERS.md#pa46) Fire/Smoke alarm type | Smoke evacuation | Smoke evacuation |  |
| [1763](MODBUS_REGISTERS.md#reg-1763) | [PA47](MODBUS_REGISTERS.md#pa47) Fire/Smoke alarm signal type | Serious | Serious |  |
| [1764](MODBUS_REGISTERS.md#reg-1764) | [PA48](MODBUS_REGISTERS.md#pa48) Generic warning delay | 30 s | 30 s |  |
| [1765](MODBUS_REGISTERS.md#reg-1765) | [PA49](MODBUS_REGISTERS.md#pa49) Generic warning reset type | AUTO | AUTO |  |
| [1766](MODBUS_REGISTERS.md#reg-1766) | [PA50](MODBUS_REGISTERS.md#pa50) Generic alarm delay | 30 s | 30 s |  |
| [1767](MODBUS_REGISTERS.md#reg-1767) | [PA51](MODBUS_REGISTERS.md#pa51) Generic alarm reset type | MANU | MANU |  |
| [1768](MODBUS_REGISTERS.md#reg-1768) | [PA52](MODBUS_REGISTERS.md#pa52) Enable RTC alarm | Disabled | Disabled |  |
| [1769](MODBUS_REGISTERS.md#reg-1769) | [PA53](MODBUS_REGISTERS.md#pa53) RTC alarm reset type | AUTO | AUTO |  |
| [1770](MODBUS_REGISTERS.md#reg-1770) | [PA54](MODBUS_REGISTERS.md#pa54) RTC alarm signal type | Light | Light |  |
| [1771](MODBUS_REGISTERS.md#reg-1771) | [PA55](MODBUS_REGISTERS.md#pa55) Phases sequence alarm signal type | Serious | Serious |  |
| [1772](MODBUS_REGISTERS.md#reg-1772) | [PA56](MODBUS_REGISTERS.md#pa56) Expansion alarm signal type | Light | Light |  |
| [1773](MODBUS_REGISTERS.md#reg-1773) | [PH11](MODBUS_REGISTERS.md#ph11) Modbus address | 1 | 1 |  |
| [1774](MODBUS_REGISTERS.md#reg-1774) | [PH12](MODBUS_REGISTERS.md#ph12) Modbus baud rate | 9600 | 9600 |  |
| [1775](MODBUS_REGISTERS.md#reg-1775) | [PH13](MODBUS_REGISTERS.md#ph13) Modbus parity | None | None |  |
| [1776](MODBUS_REGISTERS.md#reg-1776) | [PH14](MODBUS_REGISTERS.md#ph14) Modbus stopBit | 1 stop bit | 1 stop bit |  |
| [1777](MODBUS_REGISTERS.md#reg-1777) | [PH01](MODBUS_REGISTERS.md#ph01) Enable on/off by key | Enabled | Enabled | Without a CNU2 display: Disabled |
| [1778](MODBUS_REGISTERS.md#reg-1778) | [PH02](MODBUS_REGISTERS.md#ph02) Enable on/off by BMS | Disabled | Disabled |  |
| [1779](MODBUS_REGISTERS.md#reg-1779) | [PH03](MODBUS_REGISTERS.md#ph03) Enable scheduler | Disabled | Disabled |  |
| [1780](MODBUS_REGISTERS.md#reg-1780) | [PH04](MODBUS_REGISTERS.md#ph04) Holiday unit status | Unit ON | Unit ON |  |
| [1781](MODBUS_REGISTERS.md#reg-1781) | [PH05](MODBUS_REGISTERS.md#ph05) Temperature measurement unit | °C | °C |  |
| [1782](MODBUS_REGISTERS.md#reg-1782) | [PH06](MODBUS_REGISTERS.md#ph06) Pressure measurement unit | Bar | Bar |  |
| [1783](MODBUS_REGISTERS.md#reg-1783) | [PH07](MODBUS_REGISTERS.md#ph07) Cooling setpoint minimum value | 14.0 °C | 14.0 °C |  |
| [1784](MODBUS_REGISTERS.md#reg-1784) | [PH08](MODBUS_REGISTERS.md#ph08) Cooling setpoint maximum value | 28.0 °C | 28.0 °C |  |
| [1785](MODBUS_REGISTERS.md#reg-1785) | [PH09](MODBUS_REGISTERS.md#ph09) Heating setpoint minimum value | 14.0 °C | 14.0 °C |  |
| [1786](MODBUS_REGISTERS.md#reg-1786) | [PH10](MODBUS_REGISTERS.md#ph10) Heating setpoint maximum value | 14.0 °C | 14.0 °C |  |
| [1787](MODBUS_REGISTERS.md#reg-1787) | [PH15](MODBUS_REGISTERS.md#ph15) Restore default | Disabled | Disabled |  |
| [1788](MODBUS_REGISTERS.md#reg-1788) | [PH16](MODBUS_REGISTERS.md#ph16) CAN baud rate | 125 KBaud | 125 KBaud |  |
| [1789](MODBUS_REGISTERS.md#reg-1789) | [PH17](MODBUS_REGISTERS.md#ph17) CAN node | 1 | 1 |  |
| [1790](MODBUS_REGISTERS.md#reg-1790) | [PH18](MODBUS_REGISTERS.md#ph18) History reset | Disabled | Disabled |  |
| [1791](MODBUS_REGISTERS.md#reg-1791) | [PH19](MODBUS_REGISTERS.md#ph19) Air quality probe minimum value | 16 (30) / 18 (50) ¹ | 16 (30) / 18 (50) ¹ | Size code. 9.3 files for the HRDS+ 50: 16 |
| [1792](MODBUS_REGISTERS.md#reg-1792) | [PH20](MODBUS_REGISTERS.md#ph20) Air quality probe maximum value | 2000 ppm | 2000 ppm |  |
| [1793](MODBUS_REGISTERS.md#reg-1793) | [PH21](MODBUS_REGISTERS.md#ph21) High pressure probe minimum value | 5.0 bar | 5.0 bar |  |
| [1794](MODBUS_REGISTERS.md#reg-1794) | [PH22](MODBUS_REGISTERS.md#ph22) High pressure probe maximum value | 50.0 bar | 50.0 bar |  |
| [1795](MODBUS_REGISTERS.md#reg-1795) | [PH23](MODBUS_REGISTERS.md#ph23) Enable Evco led | Enabled | Enabled |  |
| [1796](MODBUS_REGISTERS.md#reg-1796) | `PSd3` Installer password | 2 | 2 |  |
| [1797](MODBUS_REGISTERS.md#reg-1797) | [PG01](MODBUS_REGISTERS.md#pg01) Machine type | Only dehumidifier | Only dehumidifier |  |
| [1798](MODBUS_REGISTERS.md#reg-1798) | [PG02](MODBUS_REGISTERS.md#pg02) Enable integration | Enabled | Enabled |  |
| [1799](MODBUS_REGISTERS.md#reg-1799) | [PG03](MODBUS_REGISTERS.md#pg03) Enable Free-Cooling/Heating | Disabled | Disabled | Changed with FW 9.2 |
| [1800](MODBUS_REGISTERS.md#reg-1800) | [PG04](MODBUS_REGISTERS.md#pg04) Heat exchanger type | Disable | Disable |  |
| [1801](MODBUS_REGISTERS.md#reg-1801) | [PG05](MODBUS_REGISTERS.md#pg05) Enable expansion | Disabled | Disabled |  |
| [1802](MODBUS_REGISTERS.md#reg-1802) | `PSd4` Manufacturer password | 10 | 10 |  |
| [1803](MODBUS_REGISTERS.md#reg-1803) | [HA00](MODBUS_REGISTERS.md#ha00) Remote display probes | EPJ Graph TH | EPJ Graph TH | Without a CNU2 display: None |
| [1804](MODBUS_REGISTERS.md#reg-1804) | [HA01](MODBUS_REGISTERS.md#ha01) AI1 configuration | Remote fans 0-10V | Remote fans 0-10V |  |
| [1805](MODBUS_REGISTERS.md#reg-1805) | [HA02](MODBUS_REGISTERS.md#ha02) AI2 configuration | --- | --- |  |
| [1806](MODBUS_REGISTERS.md#reg-1806) | [HA03](MODBUS_REGISTERS.md#ha03) AI3 configuration | --- | --- |  |
| [1807](MODBUS_REGISTERS.md#reg-1807) | [HA04](MODBUS_REGISTERS.md#ha04) AI4 configuration | T.evaporation | T.evaporation |  |
| [1808](MODBUS_REGISTERS.md#reg-1808) | [HA05](MODBUS_REGISTERS.md#ha05) AI5 configuration | T.water | T.water |  |
| [1809](MODBUS_REGISTERS.md#reg-1809) | [HA06](MODBUS_REGISTERS.md#ha06) AI6 configuration | DI Dehum request NO | DI Dehum request NO |  |
| [1810](MODBUS_REGISTERS.md#reg-1810) | [HA07](MODBUS_REGISTERS.md#ha07) AI7 configuration | DI Thermo request NO | DI Thermo request NO |  |
| [1811](MODBUS_REGISTERS.md#reg-1811) | [HA08](MODBUS_REGISTERS.md#ha08) AI1 Epj configuration | --- | --- |  |
| [1812](MODBUS_REGISTERS.md#reg-1812) | [HA09](MODBUS_REGISTERS.md#ha09) AI2 Epj configuration | --- | --- |  |
| [1813](MODBUS_REGISTERS.md#reg-1813) | [HA10](MODBUS_REGISTERS.md#ha10) AI1 expansion configuration | --- | --- |  |
| [1814](MODBUS_REGISTERS.md#reg-1814) | [HA11](MODBUS_REGISTERS.md#ha11) AI2 expansion configuration | --- | --- |  |
| [1815](MODBUS_REGISTERS.md#reg-1815) | [HA12](MODBUS_REGISTERS.md#ha12) AI3 expansion configuration | --- | --- |  |
| [1816](MODBUS_REGISTERS.md#reg-1816) | [HA13](MODBUS_REGISTERS.md#ha13) AI4 expansion configuration | --- | --- |  |
| [1817](MODBUS_REGISTERS.md#reg-1817) | [HA14](MODBUS_REGISTERS.md#ha14) AI5 expansion configuration | --- | --- |  |
| [1818](MODBUS_REGISTERS.md#reg-1818) | [HA15](MODBUS_REGISTERS.md#ha15) AI6 expansion configuration | --- | --- |  |
| [1819](MODBUS_REGISTERS.md#reg-1819) | [HA16](MODBUS_REGISTERS.md#ha16) AI7 expansion configuration | --- | --- |  |
| [1820](MODBUS_REGISTERS.md#reg-1820) | [HA17](MODBUS_REGISTERS.md#ha17) AI1 Evj configuration | --- | --- |  |
| [1821](MODBUS_REGISTERS.md#reg-1821) | [HA18](MODBUS_REGISTERS.md#ha18) AI2 Evj configuration | --- | --- |  |
| [1822](MODBUS_REGISTERS.md#reg-1822) | [HB01](MODBUS_REGISTERS.md#hb01) DI1 configuration | High pressure NC | High pressure NC |  |
| [1823](MODBUS_REGISTERS.md#reg-1823) | [HB02](MODBUS_REGISTERS.md#hb02) DI2 configuration | Low pressure NO | Low pressure NO |  |
| [1824](MODBUS_REGISTERS.md#reg-1824) | [HB03](MODBUS_REGISTERS.md#hb03) DI3 configuration | On/Off remote NO | On/Off remote NO |  |
| [1825](MODBUS_REGISTERS.md#reg-1825) | [HB04](MODBUS_REGISTERS.md#hb04) DI4 configuration | Summer/Winter NO | Summer/Winter NO |  |
| [1826](MODBUS_REGISTERS.md#reg-1826) | [HB05](MODBUS_REGISTERS.md#hb05) DI1 expansion configuration | --- | --- |  |
| [1827](MODBUS_REGISTERS.md#reg-1827) | [HB06](MODBUS_REGISTERS.md#hb06) DI2 expansion configuration | --- | --- |  |
| [1828](MODBUS_REGISTERS.md#reg-1828) | [HB07](MODBUS_REGISTERS.md#hb07) DI3 expansion configuration | --- | --- |  |
| [1829](MODBUS_REGISTERS.md#reg-1829) | [HC01](MODBUS_REGISTERS.md#hc01) AO1 configuration | Compressor 0-10V | Compressor 0-10V |  |
| [1830](MODBUS_REGISTERS.md#reg-1830) | [HC02](MODBUS_REGISTERS.md#hc02) AO2 configuration | --- | --- |  |
| [1831](MODBUS_REGISTERS.md#reg-1831) | [HC03](MODBUS_REGISTERS.md#hc03) AO3 configuration | --- | --- |  |
| [1832](MODBUS_REGISTERS.md#reg-1832) | [HC04](MODBUS_REGISTERS.md#hc04) AO4 configuration | Supply fan 0-10V | Supply fan 0-10V |  |
| [1833](MODBUS_REGISTERS.md#reg-1833) | [HC05](MODBUS_REGISTERS.md#hc05) AO1 expansion configuration | --- | --- |  |
| [1834](MODBUS_REGISTERS.md#reg-1834) | [HC06](MODBUS_REGISTERS.md#hc06) AO2 expansion configuration | --- | --- |  |
| [1835](MODBUS_REGISTERS.md#reg-1835) | `HCF1` Supply fan PWM frequency | 10 Hz | 10 Hz |  |
| [1836](MODBUS_REGISTERS.md#reg-1836) | `HCF2` Return fan PWM frequency | 10 Hz | 10 Hz |  |
| [1837](MODBUS_REGISTERS.md#reg-1837) | `HCF3` Compressor PWM frequency | 10 Hz | 10 Hz |  |
| [1838](MODBUS_REGISTERS.md#reg-1838) | [HD01](MODBUS_REGISTERS.md#hd01) DO1 configuration | Recirculation damper NO | Recirculation damper NO |  |
| [1839](MODBUS_REGISTERS.md#reg-1839) | [HD02](MODBUS_REGISTERS.md#hd02) DO2 configuration | Serious alarm NO | Serious alarm NO |  |
| [1840](MODBUS_REGISTERS.md#reg-1840) | [HD03](MODBUS_REGISTERS.md#hd03) DO3 configuration | Recirculation damper NO | Recirculation damper NO |  |
| [1841](MODBUS_REGISTERS.md#reg-1841) | [HD04](MODBUS_REGISTERS.md#hd04) DO4 configuration | Water condensation NC | Water condensation NC |  |
| [1842](MODBUS_REGISTERS.md#reg-1842) | [HD05](MODBUS_REGISTERS.md#hd05) DO5 configuration | Water valve NO | Water valve NO |  |
| [1843](MODBUS_REGISTERS.md#reg-1843) | [HD06](MODBUS_REGISTERS.md#hd06) DO6 configuration | Compressor NO | Compressor NO |  |
| [1844](MODBUS_REGISTERS.md#reg-1844) | [HD07](MODBUS_REGISTERS.md#hd07) DO1 expansion configuration | --- | --- |  |
| [1845](MODBUS_REGISTERS.md#reg-1845) | [HD08](MODBUS_REGISTERS.md#hd08) DO2 expansion configuration | --- | --- |  |
| [1846](MODBUS_REGISTERS.md#reg-1846) | [HD09](MODBUS_REGISTERS.md#hd09) DO3 expansion configuration | --- | --- |  |
| [1847](MODBUS_REGISTERS.md#reg-1847) | [HD10](MODBUS_REGISTERS.md#hd10) DO4 expansion configuration | --- | --- |  |
| [1848](MODBUS_REGISTERS.md#reg-1848) | [HD11](MODBUS_REGISTERS.md#hd11) OC expansion configuration | --- | --- |  |
| [1849](MODBUS_REGISTERS.md#reg-1849) | [Pb07](MODBUS_REGISTERS.md#pb07) Sniffing cycle active time | 60 s | 60 s |  |
| [1850](MODBUS_REGISTERS.md#reg-1850) | [Pb08](MODBUS_REGISTERS.md#pb08) Sniffing cycle wait time | 99 min | 99 min | Changed with FW 9.2 |
| [1851](MODBUS_REGISTERS.md#reg-1851) | [PE21](MODBUS_REGISTERS.md#pe21) Modulating compressor minimum percentage in integration | 20.00 % | 20.00 % |  |
| [1852](MODBUS_REGISTERS.md#reg-1852) | [PF27](MODBUS_REGISTERS.md#pf27) Supply fan minimum speed in integration mode | 50.00 % | 50.00 % | Changed with FW 9.2. 30 % also works |
| [1853](MODBUS_REGISTERS.md#reg-1853) | [PF28](MODBUS_REGISTERS.md#pf28) Supply fan minimum speed in dehumidify | 50.00 % | 50.00 % | Changed with FW 9.2. 30 % also works |
| [1854](MODBUS_REGISTERS.md#reg-1854) | [PF29](MODBUS_REGISTERS.md#pf29) Return fan minimum speed | 20.00 % | 20.00 % |  |
| [1855](MODBUS_REGISTERS.md#reg-1855) | [PF30](MODBUS_REGISTERS.md#pf30) Return fan maximum speed | 75.00 % | 75.00 % |  |
| [1856](MODBUS_REGISTERS.md#reg-1856) | [PF31](MODBUS_REGISTERS.md#pf31) Integration type | Higher manual and remote | Higher manual and remote |  |
| [1857](MODBUS_REGISTERS.md#reg-1857) | [PF32](MODBUS_REGISTERS.md#pf32) Return fan speed forced by DI | 70.00 % | 70.00 % |  |
| [1859](MODBUS_REGISTERS.md#reg-1859) | `FRC` Comfort band return fan setpoint | 60.00 % | 60.00 % |  |
| [1860](MODBUS_REGISTERS.md#reg-1860) | `FRE` Economy band return fan setpoint | 50.00 % | 50.00 % |  |
| [1861](MODBUS_REGISTERS.md#reg-1861) | `FRN` Night band return fan setpoint | 40.00 % | 40.00 % |  |
| [1862](MODBUS_REGISTERS.md#reg-1862) | [PF33](MODBUS_REGISTERS.md#pf33) Force return fan in error probe | 30.00 % | 30.00 % |  |
| [1863](MODBUS_REGISTERS.md#reg-1863) | [PF34](MODBUS_REGISTERS.md#pf34) Return fan post-ventilation speed | 40.00 % | 40.00 % |  |
| [1864](MODBUS_REGISTERS.md#reg-1864) | [PM91](MODBUS_REGISTERS.md#pm91) Free-Cooling T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1865](MODBUS_REGISTERS.md#reg-1865) | [PM92](MODBUS_REGISTERS.md#pm92) Evaporation T. probe calibration | 0.0 °C | 0.0 °C |  |
| [1866](MODBUS_REGISTERS.md#reg-1866) | [PH24](MODBUS_REGISTERS.md#ph24) Evaporation pressure probe minimum value | 5.0 bar | 5.0 bar |  |
| [1867](MODBUS_REGISTERS.md#reg-1867) | [PH25](MODBUS_REGISTERS.md#ph25) Evaporation pressure probe maximum value | 50.0 bar | 50.0 bar |  |
| [1868](MODBUS_REGISTERS.md#reg-1868) | [PH26](MODBUS_REGISTERS.md#ph26) Refrigeration gas | R-410A | R-410A |  |
| [1869](MODBUS_REGISTERS.md#reg-1869) | [PH27](MODBUS_REGISTERS.md#ph27) Enable integration request by BMS | Enabled | Enabled |  |
| [1870](MODBUS_REGISTERS.md#reg-1870) | [PH28](MODBUS_REGISTERS.md#ph28) Enable dehumidify request by BMS | Enabled | Enabled |  |
| [1871](MODBUS_REGISTERS.md#reg-1871) | [PE22](MODBUS_REGISTERS.md#pe22) Modulating compressor maximum percentage in integration | 55.00 % (30) / 68.00 % (50) ¹ | 55.00 % (30) / 68.00 % (50) ¹ | Changed with FW 9.2 |
| [1873](MODBUS_REGISTERS.md#reg-1873) | [PU11](MODBUS_REGISTERS.md#pu11) Evaporation setpoint | 6.0 °C | 6.0 °C |  |
| [1874](MODBUS_REGISTERS.md#reg-1874) | [PU12](MODBUS_REGISTERS.md#pu12) Evaporation dead zone | 1.0 °C | 1.0 °C | Changed with FW 9.2 |
| [1875](MODBUS_REGISTERS.md#reg-1875) | `PSdM` Import/Export parameters password | -10 | -10 |  |
| [1876](MODBUS_REGISTERS.md#reg-1876) | [PA57](MODBUS_REGISTERS.md#pa57) High humidity alarm type | Only display | Only display |  |
| [1877](MODBUS_REGISTERS.md#reg-1877) | [PA58](MODBUS_REGISTERS.md#pa58) Dehumidify by DI maximum time for warning | 999 min | 999 min |  |
| [1878](MODBUS_REGISTERS.md#reg-1878) | [PC11](MODBUS_REGISTERS.md#pc11) Change mode priority with display connected | Display | Display |  |
| [1879](MODBUS_REGISTERS.md#reg-1879) | [PE24](MODBUS_REGISTERS.md#pe24) Compressor ramp speed | 2 (raw) | 2 (raw) | Scale open: [MODBUS_REGISTERS.md](MODBUS_REGISTERS.md#pe24) |
| [1880](MODBUS_REGISTERS.md#reg-1880) | [PE25](MODBUS_REGISTERS.md#pe25) Compressor ramp speed in alarm/unit OFF | 12 (raw) | 12 (raw) | Scale open: [MODBUS_REGISTERS.md](MODBUS_REGISTERS.md#pe24) |
| [1881](MODBUS_REGISTERS.md#reg-1881) | [PE26](MODBUS_REGISTERS.md#pe26) Compressor minimum step ramp speed | 8 (raw) | 8 (raw) | Scale open: [MODBUS_REGISTERS.md](MODBUS_REGISTERS.md#pe24) |
| [1882](MODBUS_REGISTERS.md#reg-1882) | [PE27](MODBUS_REGISTERS.md#pe27) Compressor maximum RPS | 115 rps | 115 rps |  |
| [1883](MODBUS_REGISTERS.md#reg-1883) | [PE28](MODBUS_REGISTERS.md#pe28) Compressor level 1 frequency | 52 rps | 52 rps |  |
| [1884](MODBUS_REGISTERS.md#reg-1884) | [PE29](MODBUS_REGISTERS.md#pe29) Compressor level 2 frequency | 80 rps | 80 rps |  |
| [1885](MODBUS_REGISTERS.md#reg-1885) | [PE30](MODBUS_REGISTERS.md#pe30) Compressor level 1 time | 60 s | 60 s |  |
| [1886](MODBUS_REGISTERS.md#reg-1886) | [PE31](MODBUS_REGISTERS.md#pe31) Compressor level 2 time | 60 s | 60 s |  |
| [1887](MODBUS_REGISTERS.md#reg-1887) | [PE32](MODBUS_REGISTERS.md#pe32) Compressor maximum time below level 1 | 255 min | 255 min | Changed with FW 9.2 |
| [1888](MODBUS_REGISTERS.md#reg-1888) | [PE33](MODBUS_REGISTERS.md#pe33) Enable compressor RPS control | Enabled | Enabled |  |
| [1889](MODBUS_REGISTERS.md#reg-1889) | [PU13](MODBUS_REGISTERS.md#pu13) Minimum temperature setpoint to disable dehumidification | 22.0 °C | 22.0 °C |  |
| [1890](MODBUS_REGISTERS.md#reg-1890) | [PU14](MODBUS_REGISTERS.md#pu14) Minimum temperature differential to enable dehumidification | 0.5 °C | 0.5 °C |  |
| [1891](MODBUS_REGISTERS.md#reg-1891) | [PA59](MODBUS_REGISTERS.md#pa59) Alarm relay signaling mode | Always | Always |  |
| [1892](MODBUS_REGISTERS.md#reg-1892) | [PH29](MODBUS_REGISTERS.md#ph29) Humidity setpoint minimum value | 0 % | 0 % |  |
| [1893](MODBUS_REGISTERS.md#reg-1893) | [PH30](MODBUS_REGISTERS.md#ph30) Humidity setpoint maximum value | 100 % | 100 % |  |
| [1894](MODBUS_REGISTERS.md#reg-1894) | [PC12](MODBUS_REGISTERS.md#pc12) Enable on/off by DI thermo/dehumidify request | Disabled | Disabled |  |
| [1895](MODBUS_REGISTERS.md#reg-1895) | `LNG` Language | English | English |  |
| [1896](MODBUS_REGISTERS.md#reg-1896) | [PA60](MODBUS_REGISTERS.md#pa60) Automatic reset delay for high humidity block alarm | 60 s | 60 s |  |
| [1897](MODBUS_REGISTERS.md#reg-1897) | [PT01](MODBUS_REGISTERS.md#pt01) Enable test mode | Disabled | Disabled |  |
| [1898](MODBUS_REGISTERS.md#reg-1898) | [PT02](MODBUS_REGISTERS.md#pt02) Supply fan speed in test mode | 0 % | 0 % |  |
| [1899](MODBUS_REGISTERS.md#reg-1899) | [PT03](MODBUS_REGISTERS.md#pt03) Return fan speed in test mode | 0 % | 0 % |  |
| [1900](MODBUS_REGISTERS.md#reg-1900) | [PT04](MODBUS_REGISTERS.md#pt04) External damper percentage in test mode | 0 % | 0 % |  |
| [1901](MODBUS_REGISTERS.md#reg-1901) | [PT05](MODBUS_REGISTERS.md#pt05) Recirculation damper relay status in test mode | Off | Off |  |
| [1902](MODBUS_REGISTERS.md#reg-1902) | [PT06](MODBUS_REGISTERS.md#pt06) Serious alarm relay status in test mode | Off | Off |  |
| [1903](MODBUS_REGISTERS.md#reg-1903) | [PT07](MODBUS_REGISTERS.md#pt07) Free-Coooling/Free-Heating bypass relay status in test mode | Off | Off |  |
| [1904](MODBUS_REGISTERS.md#reg-1904) | [PT08](MODBUS_REGISTERS.md#pt08) Water condensation valve relay status in test mode | Off | Off |  |
| [1905](MODBUS_REGISTERS.md#reg-1905) | [PT09](MODBUS_REGISTERS.md#pt09) Water flow valve relay status in test mode | Off | Off |  |
| [1906](MODBUS_REGISTERS.md#reg-1906) | [PH31](MODBUS_REGISTERS.md#ph31) Epj Graph backlight mode | Timed | Timed |  |
| [1907](MODBUS_REGISTERS.md#reg-1907) | [PH32](MODBUS_REGISTERS.md#ph32) Epj Graph backlight timeout | 180 s | 180 s |  |
| [1908](MODBUS_REGISTERS.md#reg-1908) | [PH33](MODBUS_REGISTERS.md#ph33) Enable Epj Graph On/Off led | Enabled | Enabled |  |
| [1909](MODBUS_REGISTERS.md#reg-1909) | [PH34](MODBUS_REGISTERS.md#ph34) Enable Epj Graph alarm led | Enabled | Enabled |  |
| [1910](MODBUS_REGISTERS.md#reg-1910) | [PA61](MODBUS_REGISTERS.md#pa61) External damper limitation differential | 15 % | 15 % |  |
| [1911](MODBUS_REGISTERS.md#reg-1911) | [PA62](MODBUS_REGISTERS.md#pa62) Dehumidification by DI/BMS max time for external damper limitation | 90 min | 90 min |  |
| [1912](MODBUS_REGISTERS.md#reg-1912) | [PT10](MODBUS_REGISTERS.md#pt10) Compressor relay status in test mode | Off | Off |  |
| [1913](MODBUS_REGISTERS.md#reg-1913) | [PT11](MODBUS_REGISTERS.md#pt11) Compressor percentage in test mode | 0 % | 0 % |  |
| [1914](MODBUS_REGISTERS.md#reg-1914) | [PH35](MODBUS_REGISTERS.md#ph35) Summer/Winter icon type | Sun = summer | Sun = summer |  |

¹ Older units: see [Sizes](#sizes).
