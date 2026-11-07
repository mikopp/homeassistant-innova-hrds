# Vendor parameter sets: HRDS+

The parameter values hej.luft (the vendor) sent for the HRDS+ in November 2026,
as sent, and which firmware each belongs to. It repeats nothing from the other
references: what a register is, its scale, unit and range are in
[`MODBUS_REGISTERS.md`](MODBUS_REGISTERS.md); what the unit does with a
parameter is in [`UNIT_BEHAVIOUR.md`](UNIT_BEHAVIOUR.md); this file only holds
what the vendor's files say. They are cited as `[FW]` (files) and `[VM]`
(the vendor's e-mail of 7 Nov 2026).

## Sources

None of these files is stored in the repository. The vendor makes them
available on request; their download links change with each edition.

| Source | What it is | Cited as |
|--------|------------|----------|
| "Final settings" table | Spreadsheet `HRDS_Hejluft_final-Parameter-Default-Settings_request_25Feb2026.xlsx`: one row per parameter (378 rows), with a column "Final Settings for next release" and four columns "FW 9.2" (see [Models in the table](#models-in-the-table)). The last rows are reserved import/export space. | `[FW]` |
| Firmware 9.3 parameter files | Four EVCO Parameters Manager files (May 2026): `HRDS+30_CNU2`, `HRDS+30_noDisplay`, `HRDS+50_CNU2`, `HRDS+50_noDisplay` (`.map`). Each holds 372 entries (370 of them are rows of the settings table) for driver `drv970AA09`. | `[FW]` |
| EVCO driver `Drv970` | The parameter definitions the Parameters Manager needs (names, Modbus addresses, ranges): files `Drv970AA01` to `AA04`, `AA07`, `AA08` and `AA09` (`.vtp`). See [Parameter driver revisions](#parameter-driver-revisions). | `[FW]` |
| Update guide | "Anleitung: Firmware- und Parameter-Update am HRDS+" (German, Aug. 2026). See [Updating the firmware](#updating-the-firmware). | `[FW]` |
| Firmware 9.3 image | `work.ucjb` and `work.ucje` (folder dated 23 Mar 2026). Its text contains the product code `EPB9ORSINDEU`. | `[FW]` |
| EVCO Parameters Manager | Windows software, version 2.24.4, to load the files above onto the controller over USB. | `[FW]` |

## Which firmware has which parameter set

| Firmware | Parameter set sent |
|----------|--------------------|
| 4.7 and lower | None |
| 9.2 | The four "FW 9.2" columns of the table |
| 9.3 | The four `.map` files, and the "Final Settings" column ("for next release" read as 9.3 [INFERRED]) |
| 9.4 | None; the vendor says it has the same functions as 9.3 [VM] |

The firmware versions and the units they belong to are in
[`UNIT_BEHAVIOUR.md` §1.2](UNIT_BEHAVIOUR.md#12-what-differs-between-the-variants).
The vendor writes that Innova implemented the final parameter adjustments in
9.3 and 9.4 [VM].

## Models in the table

The table has these columns [FW]:

| Column header in the table | Read as |
|----------------------------|---------|
| Final Settings for next release | The final values; `PE07`, `PE22` and `PH19` are given per model as text |
| 30 FW 9.2 | HRDS 30 [INFERRED] |
| 40 (=HRDS+30) FW 9.2 | HRDS+ 30 |
| 50 FW 9.2 | HRDS 50 [INFERRED] |
| 60 (=HRDS+50) FW 9.2 | HRDS+ 50 |

Only columns 40 and 60 are labelled in the table. Columns 30 and 50 are read
as the on/off HRDS 30 and 50, because the vendor's e-mail and Innova's
declaration of conformity name two products, HRDS and HRDS+ (the part numbers
are in [`README.md`](README.md#who-makes-and-sells-the-unit)).

## Where the sets differ

The four 9.2 columns, the final column and the four 9.3 files are identical
in every other row: the 9.3 files hold the same raw register value as the
column of their model (checked register by register after converting the
files' display values with the scale of the driver, 370 registers). The 8 rows
the 9.3 files do not contain are run-time values (working hours, last
maintenance date, manual fan and compressor requests, holiday command).

| Parameter | Final | FW 9.2 columns 30 / 40 / 50 / 60 | FW 9.3 files |
|-----------|-------|----------------------------------|--------------|
| [PE07](MODBUS_REGISTERS.md#pe07) | 5500 (HRDS+30), 6800 (HRDS+50) | 5000 / 5500 / 6200 / 6800 | 5500 in the HRDS+ 30 files, 6800 in the HRDS+ 50 files |
| [PE22](MODBUS_REGISTERS.md#pe22) | 5500 (HRDS+30), 6800 (HRDS+50) | 5000 / 5500 / 6200 / 6800 | 5500 in the HRDS+ 30 files, 6800 in the HRDS+ 50 files |
| [PH19](MODBUS_REGISTERS.md#ph19) | 16 (HRDS+30), 18 (HRDS+50) | 15 / 16 / 17 / 18 | 16 in all four files |
| [Pb01](MODBUS_REGISTERS.md#pb01) | 250 | 30 in all four | 255 in all four files |
| [PH01](MODBUS_REGISTERS.md#ph01) | 1 | 1 | 1 in the CNU2 files, 0 in the noDisplay files |
| [HA00](MODBUS_REGISTERS.md#ha00) | 6 | 6 | 6 in the CNU2 files, 0 in the noDisplay files |

* [PE07](MODBUS_REGISTERS.md#pe07) and [PE22](MODBUS_REGISTERS.md#pe22) are the maximum compressor output (50 / 55 / 62 / 68 % in the four
  FW 9.2 columns). They and the [PH19](MODBUS_REGISTERS.md#ph19) label are the only rows that differ by model.
  The sheet marks both "Change implemented with FW 9.2 release".
* [PH19](MODBUS_REGISTERS.md#ph19) is the air-quality probe minimum, which the HRDS+ does not use. The sheet
  notes it is "used for model type recognition: 16 = HRDS+ 30, 18 = HRDS+ 50",
  but the HRDS+ 50 files hold 16.
* [PH02](MODBUS_REGISTERS.md#ph02) is 0 and [PH27](MODBUS_REGISTERS.md#ph27) / [PH28](MODBUS_REGISTERS.md#ph28) are 1 in every column and file.
* The noDisplay files differ from the CNU2 files only in [PH01](MODBUS_REGISTERS.md#ph01) and [HA00](MODBUS_REGISTERS.md#ha00): no
  display, no on/off key.

## Notes the vendor wrote in the table

Quoted as sent, from the name cells of the rows (the first line follows the
arrow in the name).

1. [Pb01](MODBUS_REGISTERS.md#pb01) (valve off delay):
   > change default to 250
   > (Required to maintain water flow long enough to cover all possible compressor ramp-down phases.)
   >
   > once DEU/INT requests are satisfied, the water valve remains open for the set time. Consequently, the recirculation fan also remains active, independent of the PF03 setting.
   >
   > up to FW 9.2: the recirculation damper closes immediately, which could lead to situations where the fan is still running while the damper is already closed.
   > new with FW 9.3: the damper closes only once all requests are satisfied, the compressor is off, and the water valve is closed.
2. [PF03](MODBUS_REGISTERS.md#pf03) (post-ventilation time):
   > Independent of this setting, the fan post-run remains active as long as the external water valve is open (see Pb01).

## Updating the firmware

Update guide, in short [FW]:

1. **Firmware.** Copy `work.ucjb` and `work.ucje` to the root of an empty
   FAT32 USB stick. With the unit powered and in mode OFF, plug the stick into
   the controller's USB port (under the top cover, or behind the terminal
   plate after removing the side service cover). The update starts by itself.
   The display shows progress; without a display, all three red LEDs on the back
   of the controller light and blink five times, the ALARM and CAN LEDs blink
   during the upload, and the L1 LED also blinks when it is done.
2. **Parameters.** Install the EVCO Parameters Manager (language English),
   copy the `Drv970` folder into its `Vtp\Cpro\vendor1` folder, connect the
   controller by a USB-A cable (unit in mode OFF; 230 V is optional), connect
   with "USBAdapter", open the `.map` file for the model, and use Device →
   Program.

* After the firmware update all parameters are reset to the defaults of the
  freely programmable controller, which do not suit the HRDS+ (alarms,
  functions not working). Step 2 is therefore required.
* The display may restart in a loop showing "checking 20k, 50k, 125k, 500k,
  20k …". Loading a parameter file resets the display and fixes it.

## Parameter driver revisions

Compared file by file [FW]. "Entries" counts every keyed entry, not only
parameters. Files `AA05` and `AA06` were not sent. Which firmware uses which
driver revision is not stated; the 9.3 files name `AA09`.

| Driver file | Internal date | Entries | What it adds or changes |
|-------------|---------------|--------:|-------------------------|
| `Drv970AA01` | 19 Dec 2018 | 388 | First file |
| `Drv970AA02` | 19 Dec 2018 | 401 | New: [PF27](MODBUS_REGISTERS.md#pf27) to [PF34](MODBUS_REGISTERS.md#pf34), [PM22](MODBUS_REGISTERS.md#pm22). Gone: PF06, PF14, PF24, PF25 |
| `Drv970AA03` | 9 Nov 2020 | 435 | New: [PH27](MODBUS_REGISTERS.md#ph27) and [PH28](MODBUS_REGISTERS.md#ph28) (Modbus enables for the INT and DEU requests) with the two registers that hold those requests, [PU11](MODBUS_REGISTERS.md#pu11), [PU12](MODBUS_REGISTERS.md#pu12), [PE22](MODBUS_REGISTERS.md#pe22), [PE23](MODBUS_REGISTERS.md#pe23), [PH24](MODBUS_REGISTERS.md#ph24) to [PH26](MODBUS_REGISTERS.md#ph26), [PM91](MODBUS_REGISTERS.md#pm91), [PM92](MODBUS_REGISTERS.md#pm92), and registers to reset alarms over Modbus. Gone: PU06 |
| `Drv970AA04` | 12 Feb 2021 | 448 | New: [PE24](MODBUS_REGISTERS.md#pe24) to [PE33](MODBUS_REGISTERS.md#pe33), [PC11](MODBUS_REGISTERS.md#pc11), [PA57](MODBUS_REGISTERS.md#pa57), [PA58](MODBUS_REGISTERS.md#pa58) |
| `Drv970AA07` | 26 Feb 2025 | 467 | New: [PC12](MODBUS_REGISTERS.md#pc12), [PU13](MODBUS_REGISTERS.md#pu13), [PU14](MODBUS_REGISTERS.md#pu14), [PH29](MODBUS_REGISTERS.md#ph29) to [PH34](MODBUS_REGISTERS.md#ph34), [PT01](MODBUS_REGISTERS.md#pt01) to [PT09](MODBUS_REGISTERS.md#pt09), [PA59](MODBUS_REGISTERS.md#pa59), [PA60](MODBUS_REGISTERS.md#pa60), the language setting. Gone: [PE23](MODBUS_REGISTERS.md#pe23), [PA22](MODBUS_REGISTERS.md#pa22) |
| `Drv970AA08` | 26 Feb 2025 | 472 | New: [PA61](MODBUS_REGISTERS.md#pa61), [PA62](MODBUS_REGISTERS.md#pa62), [PH35](MODBUS_REGISTERS.md#ph35), [PT10](MODBUS_REGISTERS.md#pt10), [PT11](MODBUS_REGISTERS.md#pt11) |
| `Drv970AA09` | 10 Jul 2025 | 472 | [HA00](MODBUS_REGISTERS.md#ha00) takes the values 5 and 6 (EPJ Graph T / TH) besides 0 to 4. Used by the 9.3 files |

* No parameter code has more than one Modbus address across the seven files.
  The parameters of [`MODBUS_REGISTERS.md`](MODBUS_REGISTERS.md) that a file contains are at the documented
  address in it (checked for `AA09`: 392 parameters, and `AA01`: 315).
* The only documented parameters `AA09` lacks are [PE23](MODBUS_REGISTERS.md#pe23) and [PA22](MODBUS_REGISTERS.md#pa22).
* The two oldest files lack [PH27](MODBUS_REGISTERS.md#ph27), [PH28](MODBUS_REGISTERS.md#ph28) and [PU11](MODBUS_REGISTERS.md#pu11), `AA03` lacks [PE24](MODBUS_REGISTERS.md#pe24) to [PE33](MODBUS_REGISTERS.md#pe33).
* [PE24](MODBUS_REGISTERS.md#pe24), [PE25](MODBUS_REGISTERS.md#pe25), [PE26](MODBUS_REGISTERS.md#pe26) are ranged 0 to 200 in "rps" without a decimal in every file that has them.

## Addressing

The table numbers registers from 1: its "Dec" column and the number before
the colon in each value are one higher than the address of this repository
([PH02](MODBUS_REGISTERS.md#ph02) is 1779 in the table, `0x06F2` = 1778 here). Its "HEX" column is the
address used here, and so are the driver's. The vendor's e-mail says the same
("registers are shifted by one") [VM]. In four rows ([PF05](MODBUS_REGISTERS.md#pf05), [PF13](MODBUS_REGISTERS.md#pf13), [PF23](MODBUS_REGISTERS.md#pf23),
[PU05](MODBUS_REGISTERS.md#pu05)) the "Dec" column is one higher than that rule; the hex column and the
number before the colon are right.

## Every parameter as sent

One row per row of the table, in its order. Values are the raw register
values, as in the table (signed where it shows a sign); scale, unit and range
are at the linked address in [`MODBUS_REGISTERS.md`](MODBUS_REGISTERS.md). "Value" is the same in the
final column, the four 9.2 columns and the 9.3 files unless it says
otherwise; the differences are the six rows of
[Where the sets differ](#where-the-sets-differ). Names are the table's, with
the "→" remarks moved to the last column.

| Address | Name as sent | Value | Firmware |
|---------|--------------|-------|----------|
| [0x0453](MODBUS_REGISTERS.md#reg-1107) | Start holiday command | 0 | Not in the 9.3 files |
| [0x05D9](MODBUS_REGISTERS.md#reg-1497) | Holiday period days | 7 |  |
| [0x05DA](MODBUS_REGISTERS.md#reg-1498) | Holiday period hours | 0 |  |
| [0x05DB](MODBUS_REGISTERS.md#reg-1499) | Monday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05DC](MODBUS_REGISTERS.md#reg-1500) | Monday F1 starting hours | 21600 |  |
| [0x05DE](MODBUS_REGISTERS.md#reg-1502) | Monday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x05DF](MODBUS_REGISTERS.md#reg-1503) | Monday F2 starting hours | 27000 |  |
| [0x05E1](MODBUS_REGISTERS.md#reg-1505) | Monday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05E2](MODBUS_REGISTERS.md#reg-1506) | Monday F3 starting hours | 61200 |  |
| [0x05E4](MODBUS_REGISTERS.md#reg-1508) | Monday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x05E5](MODBUS_REGISTERS.md#reg-1509) | Monday F4 starting hours | 75600 |  |
| [0x05E7](MODBUS_REGISTERS.md#reg-1511) | Tuesday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05E8](MODBUS_REGISTERS.md#reg-1512) | Tuesday F1 starting hours | 21600 |  |
| [0x05EA](MODBUS_REGISTERS.md#reg-1514) | Tuesday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x05EB](MODBUS_REGISTERS.md#reg-1515) | Tuesday F2 starting hours | 27000 |  |
| [0x05ED](MODBUS_REGISTERS.md#reg-1517) | Tuesday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05EE](MODBUS_REGISTERS.md#reg-1518) | Tuesday F3 starting hours | 61200 |  |
| [0x05F0](MODBUS_REGISTERS.md#reg-1520) | Tuesday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x05F1](MODBUS_REGISTERS.md#reg-1521) | Tuesday F4 starting hours | 75600 |  |
| [0x05F3](MODBUS_REGISTERS.md#reg-1523) | Wednesday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05F4](MODBUS_REGISTERS.md#reg-1524) | Wednesday F1 starting hours | 21600 |  |
| [0x05F6](MODBUS_REGISTERS.md#reg-1526) | Wednesday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x05F7](MODBUS_REGISTERS.md#reg-1527) | Wednesday F2 starting hours | 27000 |  |
| [0x05F9](MODBUS_REGISTERS.md#reg-1529) | Wednesday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x05FA](MODBUS_REGISTERS.md#reg-1530) | Wednesday F3 starting hours | 61200 |  |
| [0x05FC](MODBUS_REGISTERS.md#reg-1532) | Wednesday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x05FD](MODBUS_REGISTERS.md#reg-1533) | Wednesday F4 starting hours | 75600 |  |
| [0x05FF](MODBUS_REGISTERS.md#reg-1535) | Thursday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x0600](MODBUS_REGISTERS.md#reg-1536) | Thursday F1 starting hours | 21600 |  |
| [0x0602](MODBUS_REGISTERS.md#reg-1538) | Thursday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x0603](MODBUS_REGISTERS.md#reg-1539) | Thursday F2 starting hours | 27000 |  |
| [0x0605](MODBUS_REGISTERS.md#reg-1541) | Thursday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x0606](MODBUS_REGISTERS.md#reg-1542) | Thursday F3 starting hours | 61200 |  |
| [0x0608](MODBUS_REGISTERS.md#reg-1544) | Thursday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x0609](MODBUS_REGISTERS.md#reg-1545) | Thursday F4 starting hours | 75600 |  |
| [0x060B](MODBUS_REGISTERS.md#reg-1547) | Friday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x060C](MODBUS_REGISTERS.md#reg-1548) | Friday F1 starting hours | 21600 |  |
| [0x060E](MODBUS_REGISTERS.md#reg-1550) | Friday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x060F](MODBUS_REGISTERS.md#reg-1551) | Friday F2 starting hours | 27000 |  |
| [0x0611](MODBUS_REGISTERS.md#reg-1553) | Friday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x0612](MODBUS_REGISTERS.md#reg-1554) | Friday F3 starting hours | 61200 |  |
| [0x0614](MODBUS_REGISTERS.md#reg-1556) | Friday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x0615](MODBUS_REGISTERS.md#reg-1557) | Friday F4 starting hours | 75600 |  |
| [0x0617](MODBUS_REGISTERS.md#reg-1559) | Saturday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x0618](MODBUS_REGISTERS.md#reg-1560) | Saturday F1 starting hours | 21600 |  |
| [0x061A](MODBUS_REGISTERS.md#reg-1562) | Saturday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x061B](MODBUS_REGISTERS.md#reg-1563) | Saturday F2 starting hours | 27000 |  |
| [0x061D](MODBUS_REGISTERS.md#reg-1565) | Saturday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x061E](MODBUS_REGISTERS.md#reg-1566) | Saturday F3 starting hours | 43200 |  |
| [0x0620](MODBUS_REGISTERS.md#reg-1568) | Saturday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x0621](MODBUS_REGISTERS.md#reg-1569) | Saturday F4 starting hours | 75600 |  |
| [0x0623](MODBUS_REGISTERS.md#reg-1571) | Sunday F1 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x0624](MODBUS_REGISTERS.md#reg-1572) | Sunday F1 starting hours | 14400 |  |
| [0x0626](MODBUS_REGISTERS.md#reg-1574) | Sunday F2 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 2 |  |
| [0x0627](MODBUS_REGISTERS.md#reg-1575) | Sunday F2 starting hours | 21600 |  |
| [0x0629](MODBUS_REGISTERS.md#reg-1577) | Sunday F3 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 3 |  |
| [0x062A](MODBUS_REGISTERS.md#reg-1578) | Sunday F3 starting hours | 72000 |  |
| [0x062C](MODBUS_REGISTERS.md#reg-1580) | Sunday F4 mode (0=Disable, 1=OFF, 2=Comfort, 3=Economy, 4=Night) | 4 |  |
| [0x062D](MODBUS_REGISTERS.md#reg-1581) | Sunday F4 starting hours | 75600 |  |
| [0x062F](MODBUS_REGISTERS.md#reg-1583) | MOdE - Summer/Winter mode (0=Summer, 1=Winter, 2=Auto) | 0 |  |
| [0x0630](MODBUS_REGISTERS.md#reg-1584) | SEtC - Summer setpoint | 240 |  |
| [0x0631](MODBUS_REGISTERS.md#reg-1585) | SEtH - Winter setpoint | 140 |  |
| [0x0632](MODBUS_REGISTERS.md#reg-1586) | PU01 - Humidity setpoint | 55 |  |
| [0x0633](MODBUS_REGISTERS.md#reg-1587) | SCC - Comfort band cooling setpoint | 240 |  |
| [0x0634](MODBUS_REGISTERS.md#reg-1588) | SCH - Comfort band heating setpoint | 140 |  |
| [0x0635](MODBUS_REGISTERS.md#reg-1589) | OEC - Economy band cooling offset | 10 |  |
| [0x0636](MODBUS_REGISTERS.md#reg-1590) | OEH - Economy band heating offset | -10 |  |
| [0x0637](MODBUS_REGISTERS.md#reg-1591) | ONC - Night band cooling offset | 20 |  |
| [0x0638](MODBUS_REGISTERS.md#reg-1592) | ONH - Night band heating offset | -20 |  |
| [0x0639](MODBUS_REGISTERS.md#reg-1593) | SDC - Cooling setpoint forced by DI | 260 |  |
| [0x063A](MODBUS_REGISTERS.md#reg-1594) | SDH - Heating setpoint forced by DI | 140 |  |
| [0x063B](MODBUS_REGISTERS.md#reg-1595) | FSC - Comfort band supply fan setpoint | 6000 |  |
| [0x063C](MODBUS_REGISTERS.md#reg-1596) | FSE - Economy band supply fan setpoint | 5000 |  |
| [0x063D](MODBUS_REGISTERS.md#reg-1597) | FSN - Night band supply fan setpoint | 4000 |  |
| [0x063E](MODBUS_REGISTERS.md#reg-1598) | BKM - Evj/Epj LCD backlight mode | 2 |  |
| [0x063F](MODBUS_REGISTERS.md#reg-1599) | BKU - Evj/Epj LCD backlight percentage | 15 |  |
| [0x0640](MODBUS_REGISTERS.md#reg-1600) | BKT - Evj/Epj LCD backlight timeout | 30 |  |
| [0x0641](MODBUS_REGISTERS.md#reg-1601) | PSd1 - User password | 0 |  |
| [0x0642](MODBUS_REGISTERS.md#reg-1602) | PM00 - Fans working hours limit (h x10) | 20000 |  |
| [0x0644](MODBUS_REGISTERS.md#reg-1604) | PM01 - Supply fan working hours (h x10) | 0 | Not in the 9.3 files |
| [0x0646](MODBUS_REGISTERS.md#reg-1606) | PM02 - Return fan working hours (h x10) | 0 | Not in the 9.3 files |
| [0x0648](MODBUS_REGISTERS.md#reg-1608) | PM03 - Compressor working hours limit (h x10) | 20000 |  |
| [0x064A](MODBUS_REGISTERS.md#reg-1610) | PM04 - Compressor working hours | 0 | Not in the 9.3 files |
| [0x064C](MODBUS_REGISTERS.md#reg-1612) | PM90 - Last maintenance date | 252460801 | Not in the 9.3 files |
| [0x064E](MODBUS_REGISTERS.md#reg-1614) | PM20 - Supply fan manual setpoint | 3000 | Not in the 9.3 files |
| [0x064F](MODBUS_REGISTERS.md#reg-1615) | PM21 - Forcing compressor | 0 | Not in the 9.3 files |
| [0x0650](MODBUS_REGISTERS.md#reg-1616) | PM80 - Return/Room temperature probe calibration | 0 |  |
| [0x0651](MODBUS_REGISTERS.md#reg-1617) | PM81 - Outdoor temperature probe calibration | 0 |  |
| [0x0652](MODBUS_REGISTERS.md#reg-1618) | PM82 - Water temperature probe calibration | 0 |  |
| [0x0653](MODBUS_REGISTERS.md#reg-1619) | PM83 - Exhaust temperature probe calibration | 0 |  |
| [0x0654](MODBUS_REGISTERS.md#reg-1620) | PM84 - Discharge temperature probe calibration | 0 |  |
| [0x0655](MODBUS_REGISTERS.md#reg-1621) | PM85 - Compressor defrost temperature probe calibration | 0 |  |
| [0x0656](MODBUS_REGISTERS.md#reg-1622) | PM86 - Room/Return humidity probe calibration | 0 |  |
| [0x0657](MODBUS_REGISTERS.md#reg-1623) | PM87 - Air quality probe calibration | 0 |  |
| [0x0658](MODBUS_REGISTERS.md#reg-1624) | PM88 - Fans potentiometer calibration | 0 |  |
| [0x0659](MODBUS_REGISTERS.md#reg-1625) | PM89 - High pressure probe calibration | 0 |  |
| [0x065A](MODBUS_REGISTERS.md#reg-1626) | PSd2 - Maintenance password | 1 |  |
| [0x065B](MODBUS_REGISTERS.md#reg-1627) | PC01 - Enable sniffing mode | 0 |  |
| [0x065C](MODBUS_REGISTERS.md#reg-1628) | PC02 - Sniffing cycle wait time | 15 |  |
| [0x065D](MODBUS_REGISTERS.md#reg-1629) | PC03 - Sniffing cycle active time | 1 |  |
| [0x065E](MODBUS_REGISTERS.md#reg-1630) | PC04 - Enable both fans for sniffing cycle | 1 |  |
| [0x065F](MODBUS_REGISTERS.md#reg-1631) | PC05 - Operating mode change type (0=Manual, 1=Manual+Auto, 2=Auto) | 0 |  |
| [0x0660](MODBUS_REGISTERS.md#reg-1632) | PC06 - Changeover probe (0=T.water, 1=T.return) | 0 |  |
| [0x0661](MODBUS_REGISTERS.md#reg-1633) | PC07 - Summer commutation setpoint water probe | 300 |  |
| [0x0662](MODBUS_REGISTERS.md#reg-1634) | PC08 - Winter commutation setpoint water probe | 200 |  |
| [0x0663](MODBUS_REGISTERS.md#reg-1635) | PC09 - Summer commutation setpoint room probe | 200 |  |
| [0x0664](MODBUS_REGISTERS.md#reg-1636) | PC10 - Winter commutation setpoint room probe | 100 |  |
| [0x0665](MODBUS_REGISTERS.md#reg-1637) | PF26 - Supply fan post-ventilation speed | 4000 |  |
| [0x0666](MODBUS_REGISTERS.md#reg-1638) | PF01 - Min time fans ON | 10 | Change implemented with FW 9.2 release |
| [0x0667](MODBUS_REGISTERS.md#reg-1639) | PF02 - Min time between fans start-up | 5 |  |
| [0x0668](MODBUS_REGISTERS.md#reg-1640) | PF03 - Post-ventilation time | 0 | Change implemented with FW 9.2 release (note 2) |
| [0x0669](MODBUS_REGISTERS.md#reg-1641) | PF04 - Stop supply fan on compressor defrost | 0 |  |
| [0x066A](MODBUS_REGISTERS.md#reg-1642) | PF05 - Force supply fan in error probe | 3000 |  |
| [0x066C](MODBUS_REGISTERS.md#reg-1644) | PF07 - Supply fan min speed in VMC mode | 2000 |  |
| [0x066D](MODBUS_REGISTERS.md#reg-1645) | PF08 - Supply fan max speed in VMC mode | 6000 |  |
| [0x066E](MODBUS_REGISTERS.md#reg-1646) | PF09 - Supply fan max speed in integration mode | 8500 |  |
| [0x066F](MODBUS_REGISTERS.md#reg-1647) | PF10 - Supply fan max speed in dehumidify | 8500 |  |
| [0x0670](MODBUS_REGISTERS.md#reg-1648) | PF11 - Fans speed increase/decrease step value | 7 |  |
| [0x0671](MODBUS_REGISTERS.md#reg-1649) | PF12 - Integration dead zone | 5 |  |
| [0x0672](MODBUS_REGISTERS.md#reg-1650) | PF13 - Integration inc/dec time | 5 |  |
| [0x0674](MODBUS_REGISTERS.md#reg-1652) | PF15 - Air quality setpoint min value | 1 |  |
| [0x0675](MODBUS_REGISTERS.md#reg-1653) | PF16 - Air quality setpoint max value | 9999 |  |
| [0x0676](MODBUS_REGISTERS.md#reg-1654) | PF17 - Air quality setpoint | 800 |  |
| [0x0677](MODBUS_REGISTERS.md#reg-1655) | PF18 - Air quality dead zone | 200 |  |
| [0x0678](MODBUS_REGISTERS.md#reg-1656) | PF19 - Air quality inc/dec time | 5 |  |
| [0x0679](MODBUS_REGISTERS.md#reg-1657) | PF20 - Heat exchanger defrost inc/dec speed | 500 |  |
| [0x067A](MODBUS_REGISTERS.md#reg-1658) | PF21 - Heat exchanger defrost inc/dec time | 5 |  |
| [0x067B](MODBUS_REGISTERS.md#reg-1659) | PF22 - Return fan delta perc. in heat exchanger defrost | 1000 |  |
| [0x067C](MODBUS_REGISTERS.md#reg-1660) | PF23 - Supply fan speed forced by DI | 7000 |  |
| [0x067F](MODBUS_REGISTERS.md#reg-1663) | PE01 - Compressor min OFF time | 300 |  |
| [0x0680](MODBUS_REGISTERS.md#reg-1664) | PE02 - Compressor min ON time | 20 |  |
| [0x0681](MODBUS_REGISTERS.md#reg-1665) | PE03 - Compressor min switch-ons time | 420 |  |
| [0x0682](MODBUS_REGISTERS.md#reg-1666) | PE04 - Min time between fan in dehumidify and compressor start | 120 |  |
| [0x0683](MODBUS_REGISTERS.md#reg-1667) | PE05 - Enable compressor security bypass | 0 |  |
| [0x0684](MODBUS_REGISTERS.md#reg-1668) | PE06 - Modulating compressor min percentage | 2000 |  |
| [0x0685](MODBUS_REGISTERS.md#reg-1669) | PE07 - Modulating compressor max percentage | FW 9.2: 5000 / 5500 / 6200 / 6800 (columns 30 / 40 / 50 / 60); final: 5500 (HRDS+30), 6800 (HRDS+50) | Change implemented with FW 9.2 release. 9.3 files: 5500 in the HRDS+ 30 files, 6800 in the HRDS+ 50 files |
| [0x0686](MODBUS_REGISTERS.md#reg-1670) | PE08 - Modulating compressor inc/dec percentage | 100 |  |
| [0x0687](MODBUS_REGISTERS.md#reg-1671) | PE09 - Modulating compressor inc/dec time | 10 |  |
| [0x0688](MODBUS_REGISTERS.md#reg-1672) | PE10 - Defrost timeout | 8 |  |
| [0x0689](MODBUS_REGISTERS.md#reg-1673) | PE11 - End defrost setpoint | 100 |  |
| [0x068A](MODBUS_REGISTERS.md#reg-1674) | PE12 - Defrost max time | 1 |  |
| [0x068B](MODBUS_REGISTERS.md#reg-1675) | PE13 - Dripping time | 0 |  |
| [0x068C](MODBUS_REGISTERS.md#reg-1676) | PE14 - Defrost counting type (0=Device ON, 1=Compressor ON, 2=T. defrost&lt;set) | 2 |  |
| [0x068D](MODBUS_REGISTERS.md#reg-1677) | PE15 - Defrost counting setpoint | 80 |  |
| [0x068E](MODBUS_REGISTERS.md#reg-1678) | PE16 - Condensation valves switch time | 10 |  |
| [0x068F](MODBUS_REGISTERS.md#reg-1679) | PE17 - High pressure pre-alarm setpoint | 370 |  |
| [0x0690](MODBUS_REGISTERS.md#reg-1680) | PE18 - High pressure pre-alarm differential | 50 |  |
| [0x0691](MODBUS_REGISTERS.md#reg-1681) | PE19 - High pressure pre-alarm inc/dec percentage | 500 |  |
| [0x0692](MODBUS_REGISTERS.md#reg-1682) | PE20 - High pressure pre-alarm inc/dec time | 10 |  |
| [0x0693](MODBUS_REGISTERS.md#reg-1683) | Pb01 - Water valve OFF delay | FW 9.2: 30; final: 250 | Sheet: change default to 250 (note 1). 9.3 files: 255 in all four files |
| [0x0694](MODBUS_REGISTERS.md#reg-1684) | Pb02 - Sniffing cycle temperature alarm active time | 60 |  |
| [0x0695](MODBUS_REGISTERS.md#reg-1685) | Pb03 - Sniffing cycle temperature alarm wait time | 3 |  |
| [0x0696](MODBUS_REGISTERS.md#reg-1686) | Pb04 - Pre-heating setpoint | 100 |  |
| [0x0697](MODBUS_REGISTERS.md#reg-1687) | Pb05 - Pre-heating differential | 100 |  |
| [0x0698](MODBUS_REGISTERS.md#reg-1688) | Pb06 - Pre-heating max time | 0 |  |
| [0x0699](MODBUS_REGISTERS.md#reg-1689) | PU02 – Enable winter dehumidification (0=No, 1=With water, 2=Without water) | 0 |  |
| [0x069A](MODBUS_REGISTERS.md#reg-1690) | PU03 - Enable dehumidify with high temperature alarm | 0 |  |
| [0x069B](MODBUS_REGISTERS.md#reg-1691) | PU04 - Enable dehumidify with water flow alarm | 0 |  |
| [0x069C](MODBUS_REGISTERS.md#reg-1692) | PU05 - Force dehumidify with cooling request | 1 |  |
| [0x069E](MODBUS_REGISTERS.md#reg-1694) | PU07 - Dehumidify differential | 5 |  |
| [0x069F](MODBUS_REGISTERS.md#reg-1695) | PU08 - Only cold water dehumidify setpoint | 100 |  |
| [0x06A0](MODBUS_REGISTERS.md#reg-1696) | PU09 - Enable compressor as dehumidify second step | 1 |  |
| [0x06A1](MODBUS_REGISTERS.md#reg-1697) | PU10 - Dehumidify out band time | 120 |  |
| [0x06A2](MODBUS_REGISTERS.md#reg-1698) | PS01 - Recirculation damper pre-start time | 20 |  |
| [0x06A3](MODBUS_REGISTERS.md#reg-1699) | PS02 - External damper pre-start time | 20 |  |
| [0x06A4](MODBUS_REGISTERS.md#reg-1700) | PS03 - External damper OFF delay | 15 |  |
| [0x06A5](MODBUS_REGISTERS.md#reg-1701) | PS04 - Modulating external damper min opening | 2000 |  |
| [0x06A6](MODBUS_REGISTERS.md#reg-1702) | PS05 - Modulating external damper max opening | 10000 |  |
| [0x06A7](MODBUS_REGISTERS.md#reg-1703) | PS06 - Free-Cooling/Heating setpoint | 40 |  |
| [0x06A8](MODBUS_REGISTERS.md#reg-1704) | PS07 - Free-Cooling/Heating differential | 20 |  |
| [0x06A9](MODBUS_REGISTERS.md#reg-1705) | PS08 - External damper inc/dec perc in high humidity | 500 |  |
| [0x06AA](MODBUS_REGISTERS.md#reg-1706) | PS09 - External damper inc/dec time in high humidity | 60 |  |
| [0x06AB](MODBUS_REGISTERS.md#reg-1707) | Pr01 - Heat exchanger differential setpoint | 50 |  |
| [0x06AC](MODBUS_REGISTERS.md#reg-1708) | Pr02 - Heat exchanger differential | 30 |  |
| [0x06AD](MODBUS_REGISTERS.md#reg-1709) | Pr03 - Heat exchanger defrost setpoint | 40 |  |
| [0x06AE](MODBUS_REGISTERS.md#reg-1710) | Pr04 - Heat exchanger defrost dead zone | 20 |  |
| [0x06AF](MODBUS_REGISTERS.md#reg-1711) | Pr05 - Heat exchanger by-pass waiting time | 5 |  |
| [0x06B0](MODBUS_REGISTERS.md#reg-1712) | Pr06 - Setpoint heat exchanger stop for defrost | 20 |  |
| [0x06B1](MODBUS_REGISTERS.md#reg-1713) | Pr07 - Differential heat exchanger stop for defrost | 30 |  |
| [0x06B2](MODBUS_REGISTERS.md#reg-1714) | Pr08 - Heat wheel defrost inc/dec percentage | 500 |  |
| [0x06B3](MODBUS_REGISTERS.md#reg-1715) | Pr09 - Heat wheel defrost inc/dec time | 5 |  |
| [0x06B4](MODBUS_REGISTERS.md#reg-1716) | Pr10 - Heat wheel defrost PWM period | 10 |  |
| [0x06B5](MODBUS_REGISTERS.md#reg-1717) | PA01 - Enable fans working hours alarm | 1 |  |
| [0x06B6](MODBUS_REGISTERS.md#reg-1718) | PA02 - Enable compressor working hours alarm | 0 |  |
| [0x06B7](MODBUS_REGISTERS.md#reg-1719) | PA03 - Working hours alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06B8](MODBUS_REGISTERS.md#reg-1720) | PA04 - Probe alarm delay | 10 |  |
| [0x06B9](MODBUS_REGISTERS.md#reg-1721) | PA05 – Probe alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06BA](MODBUS_REGISTERS.md#reg-1722) | PA06 - Air flow switch alarm delay from reset | 30 |  |
| [0x06BB](MODBUS_REGISTERS.md#reg-1723) | PA07 - Air flow switch alarm delay | 5 |  |
| [0x06BC](MODBUS_REGISTERS.md#reg-1724) | PA08 - Air flow switch alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06BD](MODBUS_REGISTERS.md#reg-1725) | PA09 - Water flow switch alarm delay from reset | 30 |  |
| [0x06BE](MODBUS_REGISTERS.md#reg-1726) | PA10 - Water flow switch alarm delay | 5 |  |
| [0x06BF](MODBUS_REGISTERS.md#reg-1727) | PA11 - Number water flow switch alarm/hour for manual reset | 3 |  |
| [0x06C0](MODBUS_REGISTERS.md#reg-1728) | PA12 - Water flow switch alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06C1](MODBUS_REGISTERS.md#reg-1729) | PA13 - Air filter pressure switch alarm delay | 2 |  |
| [0x06C2](MODBUS_REGISTERS.md#reg-1730) | PA14 - Air filter pressure switch reset type (0=Auto, 1=Manu) | 1 |  |
| [0x06C3](MODBUS_REGISTERS.md#reg-1731) | PA15 - Air filter pressure switch alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06C4](MODBUS_REGISTERS.md#reg-1732) | PA16 - High/Low temperature alarm delay | 600 |  |
| [0x06C5](MODBUS_REGISTERS.md#reg-1733) | PA17 - High/Low temperature alarm differential | 20 |  |
| [0x06C6](MODBUS_REGISTERS.md#reg-1734) | PA18 - High/Low temperature alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06C7](MODBUS_REGISTERS.md#reg-1735) | PA19 - High humidity warning setpoint | 70 |  |
| [0x06C8](MODBUS_REGISTERS.md#reg-1736) | PA20 - High humidity warning differential | 5 |  |
| [0x06C9](MODBUS_REGISTERS.md#reg-1737) | PA21 - High humidity warning outband time | 60 |  |
| [0x06CB](MODBUS_REGISTERS.md#reg-1739) | PA23 - Fan tacho alarm delay from reset | 30 |  |
| [0x06CC](MODBUS_REGISTERS.md#reg-1740) | PA24 - Fan tacho alarm delay | 5 |  |
| [0x06CD](MODBUS_REGISTERS.md#reg-1741) | PA25 - Fan tacho alarm max rpm | 1400 |  |
| [0x06CE](MODBUS_REGISTERS.md#reg-1742) | PA26 - Fans alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06CF](MODBUS_REGISTERS.md#reg-1743) | PA27 - Compressor thermal alarm delay | 2 |  |
| [0x06D0](MODBUS_REGISTERS.md#reg-1744) | PA28 - Compressor thermal alarm reset type (0=Auto, 1=Manu) | 1 |  |
| [0x06D1](MODBUS_REGISTERS.md#reg-1745) | PA29 - Compressor thermal alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06D2](MODBUS_REGISTERS.md#reg-1746) | PA30 - Low pressure alarm bypass time | 120 |  |
| [0x06D3](MODBUS_REGISTERS.md#reg-1747) | PA31 - Low pressure alarm delay | 30 |  |
| [0x06D4](MODBUS_REGISTERS.md#reg-1748) | PA32 - Number low pressure alarm/hour for manual reset | 5 |  |
| [0x06D5](MODBUS_REGISTERS.md#reg-1749) | PA33 - High pressure alarm setpoint | 420 |  |
| [0x06D6](MODBUS_REGISTERS.md#reg-1750) | PA34 - High pressure alarm differential | 70 |  |
| [0x06D7](MODBUS_REGISTERS.md#reg-1751) | PA35 - Number high pressure alarm/hour for manual reset | 5 |  |
| [0x06D8](MODBUS_REGISTERS.md#reg-1752) | PA36 - High/Low pressure alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06D9](MODBUS_REGISTERS.md#reg-1753) | PA37 - Discharge high temperature alarm delay | 30 |  |
| [0x06DA](MODBUS_REGISTERS.md#reg-1754) | PA38 - Discharge high temperature alarm setpoint | 900 |  |
| [0x06DB](MODBUS_REGISTERS.md#reg-1755) | PA39 - Discharge high temperature alarm differential | 200 |  |
| [0x06DC](MODBUS_REGISTERS.md#reg-1756) | PA40 - Number discharge high temp alarm/hour for manual reset | 3 |  |
| [0x06DD](MODBUS_REGISTERS.md#reg-1757) | PA41 - Discharge high temperature alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06DE](MODBUS_REGISTERS.md#reg-1758) | PA42 - Antifreeze alarm delay | 5 |  |
| [0x06DF](MODBUS_REGISTERS.md#reg-1759) | PA43 - Antifreeze alarm setpoint | 30 |  |
| [0x06E0](MODBUS_REGISTERS.md#reg-1760) | PA44 - Antifreeze alarm differential | 20 |  |
| [0x06E1](MODBUS_REGISTERS.md#reg-1761) | PA45 - Antifreeze alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06E2](MODBUS_REGISTERS.md#reg-1762) | PA46 - Fire/Smoke alarm type (0=Fire extinguishing, 1=Smoke evacuation) | 1 |  |
| [0x06E3](MODBUS_REGISTERS.md#reg-1763) | PA47 - Fire/Smoke alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06E4](MODBUS_REGISTERS.md#reg-1764) | PA48 - Generic warning delay | 30 |  |
| [0x06E5](MODBUS_REGISTERS.md#reg-1765) | PA49 - Generic warning reset type (0=Auto, 1=Manu) | 0 |  |
| [0x06E6](MODBUS_REGISTERS.md#reg-1766) | PA50 - Generic alarm delay | 30 |  |
| [0x06E7](MODBUS_REGISTERS.md#reg-1767) | PA51 - Generic alarm reset type (0=Auto, 1=Manu) | 1 |  |
| [0x06E8](MODBUS_REGISTERS.md#reg-1768) | PA52 - Enable RTC alarm | 0 |  |
| [0x06E9](MODBUS_REGISTERS.md#reg-1769) | PA53 - RTC alarm reset type (0=Auto, 1=Manu) | 0 |  |
| [0x06EA](MODBUS_REGISTERS.md#reg-1770) | PA54 - RTC alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06EB](MODBUS_REGISTERS.md#reg-1771) | PA55 - Phases sequence alarm signal type (0=No, 1=Light, 2=Serious) | 2 |  |
| [0x06EC](MODBUS_REGISTERS.md#reg-1772) | PA56 - Expansion alarm signal type (0=No, 1=Light, 2=Serious) | 1 |  |
| [0x06ED](MODBUS_REGISTERS.md#reg-1773) | PH11 - Modbus address | 1 |  |
| [0x06EE](MODBUS_REGISTERS.md#reg-1774) | PH12 - Modbus baud rate (0=1200, 1=2400, 2=4800, 3=9600, 4=19200, 5=28800, 6=38400, 7=57600) | 3 |  |
| [0x06EF](MODBUS_REGISTERS.md#reg-1775) | PH13 - Modbus parity (0=None, 1=Odd, 2=Even) | 0 |  |
| [0x06F0](MODBUS_REGISTERS.md#reg-1776) | PH14 - Modbus stop bit (0=1 stop bit, 1=2 stop bits) | 0 |  |
| [0x06F1](MODBUS_REGISTERS.md#reg-1777) | PH01 - Enable On/Off by key | 1 | 9.3 files: 0 in the two noDisplay files |
| [0x06F2](MODBUS_REGISTERS.md#reg-1778) | PH02 - Enable On/Off by BMS | 0 |  |
| [0x06F3](MODBUS_REGISTERS.md#reg-1779) | PH03 - Enable scheduler | 0 |  |
| [0x06F4](MODBUS_REGISTERS.md#reg-1780) | PH04 - Holiday unit status (0=Unit off, 1=Unit On) | 1 |  |
| [0x06F5](MODBUS_REGISTERS.md#reg-1781) | PH05 - Temperature UM (0=°C, 1=°F) | 0 |  |
| [0x06F6](MODBUS_REGISTERS.md#reg-1782) | PH06 - Pressure UM (0=Bar, 1=psi) | 0 |  |
| [0x06F7](MODBUS_REGISTERS.md#reg-1783) | PH07 - Cooling setpoint min value | 140 |  |
| [0x06F8](MODBUS_REGISTERS.md#reg-1784) | PH08 - Cooling setpoint max value | 280 |  |
| [0x06F9](MODBUS_REGISTERS.md#reg-1785) | PH09 - Heating setpoint min value | 140 |  |
| [0x06FA](MODBUS_REGISTERS.md#reg-1786) | PH10 - Heating setpoint max value | 140 |  |
| [0x06FB](MODBUS_REGISTERS.md#reg-1787) | PH15 - Restore default | 0 |  |
| [0x06FC](MODBUS_REGISTERS.md#reg-1788) | PH16 - CAN baud rate (1=20K, 2=50K, 3=125K, 4=500K) | 3 |  |
| [0x06FD](MODBUS_REGISTERS.md#reg-1789) | PH17 - CAN node | 1 |  |
| [0x06FE](MODBUS_REGISTERS.md#reg-1790) | PH18 - History reset | 0 |  |
| [0x06FF](MODBUS_REGISTERS.md#reg-1791) | PH19 - Air quality probe min value (Used for model type recognition: 16= HRDS+ 30 18=HRDS+ 50) | FW 9.2: 15 / 16 / 17 / 18 (columns 30 / 40 / 50 / 60); final: 16 (HRDS+30), 18 (HRDS+50) | 9.3 files: 16 in all four files |
| [0x0700](MODBUS_REGISTERS.md#reg-1792) | PH20 - Air quality probe max value | 2000 |  |
| [0x0701](MODBUS_REGISTERS.md#reg-1793) | PH21 - High pressure probe min value | 50 |  |
| [0x0702](MODBUS_REGISTERS.md#reg-1794) | PH22 - High pressure probe max value | 500 |  |
| [0x0703](MODBUS_REGISTERS.md#reg-1795) | PH23 - Enable Evco led | 1 |  |
| [0x0704](MODBUS_REGISTERS.md#reg-1796) | PSd3 - Installer password | 2 |  |
| [0x0705](MODBUS_REGISTERS.md#reg-1797) | PG01 - Machine type (0=Only dehumidifier, 1=Dehumidifier + VMC) | 0 |  |
| [0x0706](MODBUS_REGISTERS.md#reg-1798) | PG02 - Enable integration | 1 |  |
| [0x0707](MODBUS_REGISTERS.md#reg-1799) | PG03 - Enable Free-Cooling/Free-Heating | 0 | Change implemented with FW 9.2 release |
| [0x0708](MODBUS_REGISTERS.md#reg-1800) | PG04 - Heat exchanger type (0=Disable, 1=Cross flow, 2=Rotating) | 0 |  |
| [0x0709](MODBUS_REGISTERS.md#reg-1801) | PG05 - Enable expansion | 0 |  |
| [0x070A](MODBUS_REGISTERS.md#reg-1802) | PSd4 - Manufacturer password | 10 |  |
| [0x070B](MODBUS_REGISTERS.md#reg-1803) | HA00 - Display remote probe (0=None, 1=Evj T, 2=Evj TH, 3=Epj T, 4=Epj TH, 5=Epj graph T, 6=Epj graph TH ) | 6 | 9.3 files: 0 in the two noDisplay files |
| [0x070C](MODBUS_REGISTERS.md#reg-1804) | HA01 - AI1 configuration | 58 |  |
| [0x070D](MODBUS_REGISTERS.md#reg-1805) | HA02 - AI2 configuration | 0 |  |
| [0x070E](MODBUS_REGISTERS.md#reg-1806) | HA03 - AI3 configuration | 0 |  |
| [0x070F](MODBUS_REGISTERS.md#reg-1807) | HA04 - AI4 configuration | 52 |  |
| [0x0710](MODBUS_REGISTERS.md#reg-1808) | HA05 - AI5 configuration | 47 |  |
| [0x0711](MODBUS_REGISTERS.md#reg-1809) | HA06 - AI6 configuration | 6 |  |
| [0x0712](MODBUS_REGISTERS.md#reg-1810) | HA07 - AI7 configuration | 8 |  |
| [0x0713](MODBUS_REGISTERS.md#reg-1811) | HA08 - AI1 Epj configuration | 0 |  |
| [0x0714](MODBUS_REGISTERS.md#reg-1812) | HA09 - AI2 Epj configuration | 0 |  |
| [0x0715](MODBUS_REGISTERS.md#reg-1813) | HA10 - AI1 expansion configuration | 0 |  |
| [0x0716](MODBUS_REGISTERS.md#reg-1814) | HA11 - AI2 expansion configuration | 0 |  |
| [0x0717](MODBUS_REGISTERS.md#reg-1815) | HA12 - AI3 expansion configuration | 0 |  |
| [0x0718](MODBUS_REGISTERS.md#reg-1816) | HA13 - AI4 expansion configuration | 0 |  |
| [0x0719](MODBUS_REGISTERS.md#reg-1817) | HA14 - AI5 expansion configuration | 0 |  |
| [0x071A](MODBUS_REGISTERS.md#reg-1818) | HA15 - AI6 expansion configuration | 0 |  |
| [0x071B](MODBUS_REGISTERS.md#reg-1819) | HA16 - AI7 expansion configuration | 0 |  |
| [0x071C](MODBUS_REGISTERS.md#reg-1820) | HA17 - AI1 Evj configuration | 0 |  |
| [0x071D](MODBUS_REGISTERS.md#reg-1821) | HA18 - AI2 Evj configuration | 0 |  |
| [0x071E](MODBUS_REGISTERS.md#reg-1822) | HB01 - DI1 configuration | 27 |  |
| [0x071F](MODBUS_REGISTERS.md#reg-1823) | HB02 - DI2 configuration | 26 |  |
| [0x0720](MODBUS_REGISTERS.md#reg-1824) | HB03 - DI3 configuration | 2 |  |
| [0x0721](MODBUS_REGISTERS.md#reg-1825) | HB04 - DI4 configuration | 4 |  |
| [0x0722](MODBUS_REGISTERS.md#reg-1826) | HB05 - DI1 expansion configuration | 0 |  |
| [0x0723](MODBUS_REGISTERS.md#reg-1827) | HB06 - DI2 expansion configuration | 0 |  |
| [0x0724](MODBUS_REGISTERS.md#reg-1828) | HB07 - DI3 expansion configuration | 0 |  |
| [0x0725](MODBUS_REGISTERS.md#reg-1829) | HC01 - AO1 configuration | 5 |  |
| [0x0726](MODBUS_REGISTERS.md#reg-1830) | HC02 - AO2 configuration | 0 |  |
| [0x0727](MODBUS_REGISTERS.md#reg-1831) | HC03 - AO3 configuration | 0 |  |
| [0x0728](MODBUS_REGISTERS.md#reg-1832) | HC04 - AO4 configuration | 1 |  |
| [0x0729](MODBUS_REGISTERS.md#reg-1833) | HC05 - AO1 expansion configuration | 0 |  |
| [0x072A](MODBUS_REGISTERS.md#reg-1834) | HC06 - AO2 expansion configuration | 0 |  |
| [0x072B](MODBUS_REGISTERS.md#reg-1835) | HCF1 - Supply fan PWM frequency | 10 |  |
| [0x072C](MODBUS_REGISTERS.md#reg-1836) | HCF2 - Return fan PWM frequency | 10 |  |
| [0x072D](MODBUS_REGISTERS.md#reg-1837) | HCF3 - Compressor PWM frequency | 10 |  |
| [0x072E](MODBUS_REGISTERS.md#reg-1838) | HD01 - DO1 configuration | 10 |  |
| [0x072F](MODBUS_REGISTERS.md#reg-1839) | HD02 - DO2 configuration | 26 |  |
| [0x0730](MODBUS_REGISTERS.md#reg-1840) | HD03 - DO3 configuration | 10 |  |
| [0x0731](MODBUS_REGISTERS.md#reg-1841) | HD04 - DO4 configuration | 13 |  |
| [0x0732](MODBUS_REGISTERS.md#reg-1842) | HD05 - DO5 configuration | 12 |  |
| [0x0733](MODBUS_REGISTERS.md#reg-1843) | HD06 - DO6 configuration | 6 |  |
| [0x0734](MODBUS_REGISTERS.md#reg-1844) | HD07 - DO1 expansion configuration | 0 |  |
| [0x0735](MODBUS_REGISTERS.md#reg-1845) | HD08 - DO2 expansion configuration | 0 |  |
| [0x0736](MODBUS_REGISTERS.md#reg-1846) | HD09 - DO3 expansion configuration | 0 |  |
| [0x0737](MODBUS_REGISTERS.md#reg-1847) | HD10 - DO4 expansion configuration | 0 |  |
| [0x0738](MODBUS_REGISTERS.md#reg-1848) | HD11 - OC expansion configuration | 0 |  |
| [0x0739](MODBUS_REGISTERS.md#reg-1849) | Pb07 - Water valve sniffing cycle active time | 60 |  |
| [0x073A](MODBUS_REGISTERS.md#reg-1850) | Pb08 - Water valve sniffing cycle wait time | 99 | Change implemented with FW 9.2 release |
| [0x073B](MODBUS_REGISTERS.md#reg-1851) | PE21 - Modulating compressor min percentage in integration | 2000 |  |
| [0x073C](MODBUS_REGISTERS.md#reg-1852) | PF27 - Supply fan min speed in integration mode | 5000 | Change implemented with FW 9.2 release |
| [0x073D](MODBUS_REGISTERS.md#reg-1853) | PF28 - Supply fan min speed in dehumidify | 5000 | Change implemented with FW 9.2 release |
| [0x073E](MODBUS_REGISTERS.md#reg-1854) | PF29 - Return fan min speed | 2000 |  |
| [0x073F](MODBUS_REGISTERS.md#reg-1855) | PF30 - Return fan max speed | 7500 |  |
| [0x0740](MODBUS_REGISTERS.md#reg-1856) | PF31 - Integration type (0=Only temp, 1=Higher manual, remote, 2=Higher temp, manual, remote) | 1 |  |
| [0x0741](MODBUS_REGISTERS.md#reg-1857) | PF32 - Return fan speed forced by DI | 7000 |  |
| [0x0742](MODBUS_REGISTERS.md#reg-1858) | PM22 - Return fan manual setpoint | 2000 | Not in the 9.3 files |
| [0x0743](MODBUS_REGISTERS.md#reg-1859) | FRC - Comfort band return fan setpoint | 6000 |  |
| [0x0744](MODBUS_REGISTERS.md#reg-1860) | FRE - Economy band return fan setpoint | 5000 |  |
| [0x0745](MODBUS_REGISTERS.md#reg-1861) | FRN - Night band return fan setpoint | 4000 |  |
| [0x0746](MODBUS_REGISTERS.md#reg-1862) | PF33 - Force return fan in error probe | 3000 |  |
| [0x0747](MODBUS_REGISTERS.md#reg-1863) | PF34 - Return fan post-ventilation speed | 4000 |  |
| [0x0748](MODBUS_REGISTERS.md#reg-1864) | PM91 - Free-Cooling temperature probe calibration | 0 |  |
| [0x0749](MODBUS_REGISTERS.md#reg-1865) | PM92 - Evaporation temperature probe calibration | 0 |  |
| [0x074A](MODBUS_REGISTERS.md#reg-1866) | PH24 - Evaporation pressure probe min value | 50 |  |
| [0x074B](MODBUS_REGISTERS.md#reg-1867) | PH25 - Evaporation pressure probe max value | 500 |  |
| [0x074C](MODBUS_REGISTERS.md#reg-1868) | PH26 - Refrigeration gas (0=R-22, 1=R- 134A, 2=R-402A, 3=R-404A, 4=R-407A, 5=R-407C, 6=R-410A, 7=R-417A, 8=R- 422A, 9=R-422D, 10=R-507A, 11=R-744, 12=R-438A, 13=R-401B, 14=R-290, 15=R-717, 16=R-1270, 17=R-32, 18=R-407F, 19=R-1234ZE) | 6 |  |
| [0x074D](MODBUS_REGISTERS.md#reg-1869) | PH27 - Enable integration request by BMS | 1 |  |
| [0x074E](MODBUS_REGISTERS.md#reg-1870) | PH28 - Enable dehumidify request by BMS | 1 |  |
| [0x074F](MODBUS_REGISTERS.md#reg-1871) | PE22 - Modulating compressor max percentage in integration | FW 9.2: 5000 / 5500 / 6200 / 6800 (columns 30 / 40 / 50 / 60); final: 5500 (HRDS+30), 6800 (HRDS+50) | Change implemented with FW 9.2 release. 9.3 files: 5500 in the HRDS+ 30 files, 6800 in the HRDS+ 50 files |
| [0x0751](MODBUS_REGISTERS.md#reg-1873) | PU11 - Evaporation setpoint | 60 |  |
| [0x0752](MODBUS_REGISTERS.md#reg-1874) | PU12 – Evaporation dead zone | 10 | Change implemented with FW 9.2 release |
| [0x0753](MODBUS_REGISTERS.md#reg-1875) | PSdM – Import/Export parameters password | -10 |  |
| [0x0754](MODBUS_REGISTERS.md#reg-1876) | PA57 – High humidity alarm type (0=Only display, 1=Block alarm) | 0 |  |
| [0x0755](MODBUS_REGISTERS.md#reg-1877) | PA58 - Max time dehumidify by DI for warning | 999 |  |
| [0x0756](MODBUS_REGISTERS.md#reg-1878) | PC11 - Change operating mode priority with display connected (0=Display, 1=DI) | 0 |  |
| [0x0757](MODBUS_REGISTERS.md#reg-1879) | PE24 - Compressor ramp speed | 2 |  |
| [0x0758](MODBUS_REGISTERS.md#reg-1880) | PE25 - Compressor ramp speed in alarm/unit OFF | 12 |  |
| [0x0759](MODBUS_REGISTERS.md#reg-1881) | PE26 - Compressor min step ramp speed | 8 |  |
| [0x075A](MODBUS_REGISTERS.md#reg-1882) | PE27 - Compressor max RPS | 115 |  |
| [0x075B](MODBUS_REGISTERS.md#reg-1883) | PE28 - Compressor level 1 frequency | 52 |  |
| [0x075C](MODBUS_REGISTERS.md#reg-1884) | PE29 - Compressor level 2 frequency | 80 |  |
| [0x075D](MODBUS_REGISTERS.md#reg-1885) | PE30 - Compressor level 1 time | 60 |  |
| [0x075E](MODBUS_REGISTERS.md#reg-1886) | PE31 - Compressor level 2 time | 60 |  |
| [0x075F](MODBUS_REGISTERS.md#reg-1887) | PE32 - Compressor max time under level 1 | 255 | Change implemented with FW 9.2 release |
| [0x0760](MODBUS_REGISTERS.md#reg-1888) | PE33 - Enable RPS control | 1 |  |
| [0x0761](MODBUS_REGISTERS.md#reg-1889) | PU13 - Minimum room temperature to disable dehumidification | 220 |  |
| [0x0762](MODBUS_REGISTERS.md#reg-1890) | PU14 - Minimum room temperature differential to enable dehumidification | 5 |  |
| [0x0763](MODBUS_REGISTERS.md#reg-1891) | PA59 - Alarm Relay Signaling Mode: 0: Always (both summer and winter) 1: Only in summer | 0 |  |
| [0x0764](MODBUS_REGISTERS.md#reg-1892) | PH29 - Minimum humidity setpoint value | 0 |  |
| [0x0765](MODBUS_REGISTERS.md#reg-1893) | PH30 - Maximum humidity setpoint value | 100 |  |
| [0x0766](MODBUS_REGISTERS.md#reg-1894) | PC12 - Enable Unit On/Off with integration /dehumidification request | 0 |  |
| [0x0767](MODBUS_REGISTERS.md#reg-1895) | LNG - Language: 0: English 1: Italiano 2: Spanish | 0 |  |
| [0x0768](MODBUS_REGISTERS.md#reg-1896) | PA60 - Automatic reset delay for high humidity blocking alarm | 60 |  |
| [0x0769](MODBUS_REGISTERS.md#reg-1897) | PT01 - Testmode ability | 0 |  |
| [0x076A](MODBUS_REGISTERS.md#reg-1898) | PT02 - Discharge Fan Speed in Test Mode | 0 |  |
| [0x076B](MODBUS_REGISTERS.md#reg-1899) | PT03 - Return Fan Speed in Test Mode | 0 |  |
| [0x076C](MODBUS_REGISTERS.md#reg-1900) | PT04 - External damper percentage in Test Mode | 0 |  |
| [0x076D](MODBUS_REGISTERS.md#reg-1901) | PT05 - Recirculation damper relay status in Test Mode | 0 |  |
| [0x076E](MODBUS_REGISTERS.md#reg-1902) | PT06 - Severe Alarm Relay Status in Test Mode | 0 |  |
| [0x076F](MODBUS_REGISTERS.md#reg-1903) | PT07 - Free-Cooling/Free-Heating bypass relay status in Test Mode | 0 |  |
| [0x0770](MODBUS_REGISTERS.md#reg-1904) | PT08 - Water Condensing Valve Relay Status in Test Mode | 0 |  |
| [0x0771](MODBUS_REGISTERS.md#reg-1905) | PT09 - Water Valve Relay Status in Test Mode | 0 |  |
| [0x0772](MODBUS_REGISTERS.md#reg-1906) | PH31 - Epj Graph Backlight Mode: 1: ON 2: Timed | 2 |  |
| [0x0773](MODBUS_REGISTERS.md#reg-1907) | PH32 - Timeout backlight Epj Graph | 180 |  |
| [0x0774](MODBUS_REGISTERS.md#reg-1908) | PH33 - Enable Epj Graph On/Off LED | 1 |  |
| [0x0775](MODBUS_REGISTERS.md#reg-1909) | PH34 - Enable Epj Graph Alarm LED | 1 |  |
| [0x0776](MODBUS_REGISTERS.md#reg-1910) | PA61 - External Damper Limitation Differential | 15 |  |
| [0x0777](MODBUS_REGISTERS.md#reg-1911) | PA62 - Maximum dehumidification time from DI/BMS for external damper limitation | 90 |  |
| [0x0778](MODBUS_REGISTERS.md#reg-1912) | PT10 - Compressor Relay Status in Test Mode | 0 |  |
| [0x0779](MODBUS_REGISTERS.md#reg-1913) | PT11 - Compressor Percentage in Test mode | 0 |  |
| [0x077A](MODBUS_REGISTERS.md#reg-1914) | PH35 - Summer/Winter Icon Type 0: Sun = Summer 1: Sun = Winter (Heating) | 0 |  |
