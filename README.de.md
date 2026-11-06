# hej.luft HRDS+ — Home-Assistant-Integration

[![Release](https://img.shields.io/github/v/release/mikopp/homeassistant-innova-hrds)](https://github.com/mikopp/homeassistant-innova-hrds/releases)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![HACS](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hacs.yaml/badge.svg)](https://github.com/mikopp/homeassistant-innova-hrds/actions/workflows/hacs.yaml)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

[![Dieses Repository in HACS öffnen.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mikopp&repository=homeassistant-innova-hrds&category=integration)

**Deutsch** · [English](README.md) (vollständige Dokumentation)

Diese Seite ist eine **Kurzfassung auf Deutsch**: Einleitung, Geräte,
Schnellstart und Funktionsumfang. Alles Weitere steht im
[englischen README](README.md); das Inhaltsverzeichnis unten verweist auf jeden
Abschnitt dort, damit Sie alles finden.

Home-Assistant-Integration (per **HACS** installierbar) für das
Entfeuchtungs- und Kühlmodul **hej.luft HRDS+ 30 / 50**:
Taupunktentfeuchtung mit Lüftung und Flächenkühlung. Die Integration steuert und überwacht das Gerät
**lokal über Modbus TCP, ganz ohne Cloud**.

## Kompatible Geräte

Das **[hej.luft HRDS+ 30 / HRDS+ 50](https://www.hejluft.at/hrds)** ist ein
Entfeuchtungs- und Kühlmodul für die Zuluftleitung einer zentralen
Wohnraumlüftung (KWL). Es wird von **INNOVA S.r.l.** (Storo, Italien) mit einer
EVCO-Steuerung gebaut und von hej.luft (Österreich) vertrieben, die in
Österreich und in ausgewählte EU-Länder liefert, darunter Deutschland. Es gibt das Gerät „mit
Umluft“ (`R`, eigener Umluftventilator und Klappe) oder „nur Zuluft“, in den
Größen 30 und 50; der Typenschild-Code ist im Technischen Handbuch erklärt
(Download-Seite oben, Kopie in [`doc/references/`](doc/references/README.md)),
zum Beispiel *HRDS+ 30 H R K DC*. Welche Geräte und Anlagen bekannt
funktionieren: [Getestete Geräte und Anlagen](doc/tested-setups.md).

> *Verhält sich Ihr HRDS+ anders, oder meldet ein anderes Gerät eine
> EVCO-`EPB9`-Steuerung? Eröffnen Sie ein Issue.*

## Release 0.9.6

Die Integration ist veröffentlicht und nutzbar.

* **Entwickelt und getestet** wurde sie an **einem HRDS+ 30 mit Umluft
  (`R`-Variante)**, ohne Display und ohne externe Fühler, hinter einem
  Modbus-RTU-zu-TCP-Gateway, im Solekreis einer Erdwärmepumpe. Welche Geräte und
  Installationen bekanntermaßen funktionieren und was jeweils beobachtet wurde:
  [Getestete Geräte und Installationen](doc/tested-setups.md) (EN).
* **Auf echter Hardware nicht getestet:** das HRDS+ 50, Geräte ohne Umluft,
  Geräte mit Display oder Fühlern (einschließlich des Klima-Modus *Auto*, den
  die CI nur gegen ein simuliertes Gerät prüft), Winterbetrieb und
  Freikühlung. Offene Punkte: [`plans/todo.md`](plans/todo.md).
* **Die Lüfterdrehzahl bestimmt das Gerät:** Home Assistant kann keine Drehzahl
  direkt vorgeben; es kann den Lüfter über sein Drehzahlband anheben, und ein
  0–10-V-Signal am Gerät stellt sie frei ein ([Fan speed](README.md#fan-speed), EN).

Berichte von anderen Geräten sind sehr willkommen, siehe
[Reporting issues](README.md#reporting-issues) (EN). Der Weg zu 1.0:
[Road to 1.0](README.md#road-to-10) (EN). Details: der
[englische Abschnitt](README.md#release-096).

## Schnellstart

Die Einzelheiten stehen im englischen README; die Links führen dorthin.

1. **[Installieren](README.md#1-install)** (EN): die Integration mit HACS
   installieren und Home Assistant neu starten.
2. **[Hinzufügen](README.md#2-add-the-integration)** (EN) unter
   *Einstellungen → Geräte & Dienste*, mit der Adresse Ihres Modbus-TCP-Gateways.
3. **[Einrichtung prüfen](README.md#3-check-the-setup)** (EN): das Gerät
   **HRDS+ setup** öffnen und sicherstellen, dass [*Setup check*](doc/entity-reference.md#setup-check) den Wert `ok`
   zeigt.
4. **[Festlegen, was Home Assistant steuern darf](README.md#4-choose-what-home-assistant-may-control)** (EN):
   die **Modbus-Freigaben** für die gewünschten Funktionen einschalten (Ein/Aus,
   Entfeuchten, Integration) und danach [*Allow operational requests*](doc/entity-reference.md#allow-operational-requests). Beides
   ist nach einer Neuinstallation **aus**, und die Integration schaltet sie nie
   von selbst ein. Ohne sie beobachtet die Integration nur: Messwerte und
   Einstellungen funktionieren.
5. **[Erster Betrieb](README.md#5-first-run)** (EN) und
   **[Wie das Gerät arbeitet](README.md#how-the-unit-works)** (EN): was
   *Dry* und *Cool* tun.

## Was die Integration kann

Sie spricht über Modbus TCP mit der Steuerplatine des Geräts und stellt bereit:

* **Klima-Entität** mit Raumtemperatur und -feuchte, der aktuellen Aktion
  (aus / Leerlauf / Lüfter / Entfeuchten / Kühlen / Heizen) und einem
  einstellbaren Modus: **Aus**, **Standby** (nichts angefordert),
  **Entfeuchten**, **Kühlen** (Sommer), **Heizen** (Winter, nur wenn in den
  Optionen erlaubt, nie bei Sole) und, nur mit Display oder Raumfühler,
  **Auto**. Keine Lüfterstufe: die Drehzahl ist nur ablesbar.
* **Sensoren, Binärsensoren, Schalter, Zahlen und Auswahlfelder**: Messwerte,
  Betriebszustand, Alarme, Anforderungen (Entfeuchten, Integration), Sollwerte
  und Lüfterbänder, Saison, dazu drei berechnete Luftmengen-Sensoren.
* **Lüfter und Wasserkreis nur als Messwerte**: Das Gerät steuert Lüfter
  (Umluftlüfter der `R`-Variante), Ventil und Pumpe selbst; Home Assistant zeigt
  sie nur an, samt einer Zusammenfassung [*Water circuit check*](doc/entity-reference.md#water-circuit-check).
* **Setup-Gerät** mit einer Einrichtungsprüfung und den Freigaben, und auf
  Wunsch ein **Installateur-Gerät** mit dem gesamten Installateurmenü
  (rund 240 Parameter, standardmäßig aus).

Jede Entität steht, nach Gerät gegliedert und mit Begründung, in der
**[Entitätsreferenz](doc/entity-reference.md)** (Englisch). Wie sich das Gerät
selbst verhält und was auf echter Hardware getestet wurde, steht in
[`doc/references/UNIT_BEHAVIOUR.md`](doc/references/UNIT_BEHAVIOUR.md) (Englisch).

## Inhaltsverzeichnis des englischen README

Die Abschnitte sind auf Englisch (EN); die deutsche Zeile nennt, was dort
steht.

* [Install and set up](README.md#install-and-set-up) (EN): Installation und Einrichtung
  * [Before you start](README.md#before-you-start) (EN): Was Sie brauchen (Gerät, Gateway, Adresse, HACS)
  * [1. Install](README.md#1-install) (EN): Installation mit HACS
  * [2. Add the integration](README.md#2-add-the-integration) (EN): Integration hinzufügen (Modbus-TCP-Adresse)
  * [3. Check the setup](README.md#3-check-the-setup) (EN): Einrichtung prüfen (Setup-Check)
    * [First-use checklist](README.md#first-use-checklist) (EN): Checkliste für die erste Benutzung
  * [4. Choose what Home Assistant may control](README.md#4-choose-what-home-assistant-may-control) (EN): Festlegen, was Home Assistant steuern darf
    * [Which enable gives which function](README.md#which-enable-gives-which-function) (EN): Welche Freigabe welche Funktion bringt
    * [Allow operational requests](README.md#allow-operational-requests) (EN): Betriebsanforderungen erlauben
  * [5. First run](README.md#5-first-run) (EN): Erster Betrieb
* [How the unit works](README.md#how-the-unit-works) (EN): Wie das Gerät arbeitet
  * [What is inside](README.md#what-is-inside) (EN): Aufbau des Geräts
  * [Two requests](README.md#two-requests) (EN): Die zwei Anforderungen (DEU und INT)
  * [Operating modes in summer](README.md#operating-modes-in-summer) (EN): Betriebsarten im Sommer
  * [Operating modes in winter](README.md#operating-modes-in-winter) (EN): Betriebsarten im Winter
  * [How to use it](README.md#how-to-use-it) (EN): Bedienung
* [Using the integration](README.md#using-the-integration) (EN): Die Integration nutzen
  * [Season and winter heating](README.md#season-and-winter-heating) (EN): Saison und Winterbetrieb (Heizen)
  * [The unit heats on its own](README.md#the-unit-heats-on-its-own) (EN): Das Gerät heizt von selbst
  * [Water circuit and brine](README.md#water-circuit-and-brine) (EN): Wasserkreis und Sole
    * [Brine temperature guard](README.md#brine-temperature-guard) (EN): Solewächter (Temperaturschutz)
  * [Setting target humidity and target temperature](README.md#setting-target-humidity-and-target-temperature) (EN): Soll-Feuchte und Soll-Temperatur einstellen
  * [Fan and recirculation](README.md#fan-and-recirculation) (EN): Lüfter und Umluft
  * [Airflow sensors](README.md#airflow-sensors) (EN): Luftmengen-Sensoren und ihre Kalibrierung
  * [Fan speed](README.md#fan-speed) (EN): Lüfterdrehzahl
* [Entity reference](doc/entity-reference.md) (EN): Alle Entitäten, nach Gerät gegliedert (eigene Datei)
* [Probe requirements](README.md#probe-requirements) (EN): Anforderungen an Temperatur- und Feuchtefühler
* [Requirements](README.md#requirements) (EN): Mindestversionen (Home Assistant, pymodbus)
  * [Availability](README.md#availability) (EN): Verhalten bei Ausfall: Entitäten werden „nicht verfügbar“
* [Disclaimer](README.md#disclaimer) (EN): Haftungsausschluss
* [Reporting issues](README.md#reporting-issues) (EN): Fehler und Testberichte melden
* [Road to 1.0](README.md#road-to-10) (EN): Weg zu Version 1.0
* [Design decisions](README.md#design-decisions) (EN): Architekturentscheidungen (ADRs)
* [Credits](README.md#credits) (EN): Quellen und Danksagung

Weitere Dokumente (Englisch):
[Modbus-Register](doc/references/MODBUS_REGISTERS.md),
[Verhalten des Geräts](doc/references/UNIT_BEHAVIOUR.md),
[Entitätsreferenz](doc/entity-reference.md),
[getestete Geräte und Installationen](doc/tested-setups.md),
[Architekturentscheidungen](doc/adr/README.md),
[Änderungsprotokoll](CHANGELOG.md).
