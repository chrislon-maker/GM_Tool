# GM Tool -- Projektspezifikation

## Projekt

Ich entwickle ein plattformübergreifendes **Game Master Tool für Das
Schwarze Auge 5 (DSA5)**.

-   **Programmiersprache:** Python
-   **IDE:** Visual Studio Code
-   **GUI:** PySide6 (Qt)
-   **Versionsverwaltung:** Git + GitHub
-   **Zielplattformen:** Windows und Linux

Repository: https://github.com/chrislon-maker/GM_Tool

------------------------------------------------------------------------

## Grundidee

Das Tool soll einen Spielleiter bei DSA5 unterstützen.

Geplante Funktionen:

-   Spielercharaktere aus PDF laden
-   Kreaturen aus der Ulisses-Regelwiki importieren
-   Kampfverwaltung
-   Proben würfeln
-   Lebenspunkte verwalten
-   Zustände verwalten
-   Initiative verwalten
-   Später: Zauber, Sonderfertigkeiten, Kampfautomation usw.

------------------------------------------------------------------------

## Datenquellen

### Spieler

Spieler werden aus offiziellen DSA5-PDFs geladen.

Importer:

`services/pdf_loader.py`

Der bestehende Parser aus `Role_checks.py` soll später refaktoriert
werden.

### Kreaturen

Kreaturen stammen aus:

https://dsa.ulisses-regelwiki.de/

Importer:

`services/regelwiki_scraper.py`

Der Scraper erzeugt JSON-Dateien.

Diese JSON-Dateien werden anschließend geladen.

------------------------------------------------------------------------

# Wichtigste Designentscheidung

Es gibt **keine Enemy-Klasse**.

Es existiert nur

`Creature`

Egal ob

-   Held
-   NSC
-   Tier
-   Dämon
-   Untoter
-   Monster

alles wird durch dieselbe Klasse beschrieben.

Der Unterschied liegt ausschließlich im jeweiligen Importer.

------------------------------------------------------------------------

# Projektstruktur

``` text
GM_Tool/

    models/

        creature.py
        resource.py
        weapon.py
        armor.py
        status_effect.py

    services/

        regelwiki_scraper.py
        creature_repository.py
        pdf_loader.py

    ui/

    data/

    docs/
```

------------------------------------------------------------------------

# Creature

Creature enthält **keine Importlogik**.

Keine Website.

Keine PDFs.

Keine JSON-Dateien.

Nur Daten und Methoden.

Geplante Bestandteile:

-   name
-   attributes
-   resources
-   derived_values
-   talents
-   weapons
-   armor
-   advantages
-   disadvantages
-   special_abilities
-   spells
-   liturgies
-   status_effects

## Attributes

MU, KL, IN, CH, FF, GE, KO, KK

werden gespeichert als

``` python
attributes: dict[str, int]
```

------------------------------------------------------------------------

## Resources

LeP, AsP, KaP und Schicksalspunkte werden gespeichert als

``` python
dict[str, Resource]
```

Die Klasse `Resource` besitzt:

-   current
-   maximum

sowie Methoden wie

-   lose()
-   restore()

------------------------------------------------------------------------

## Derived Values

Abgeleitete Werte:

-   SK
-   ZK
-   AW
-   GS
-   INI

werden getrennt von den Resources gespeichert.

------------------------------------------------------------------------

# Weapon

Aktuelles Modell:

``` text
Weapon
├── MeleeWeapon
└── RangedWeapon
```

Eine `NaturalWeapon` soll eventuell später ergänzt werden.

Die Klasse besitzt u.a.:

-   name
-   damage_formula
-   weight
-   price
-   complexity
-   weapon_advantage
-   weapon_disadvantage

Die Methode

``` python
roll_damage()
```

wertet zunächst einfache Formeln wie

-   1W6
-   2W6+4

aus.

Später kann daraus eine allgemeine `DiceFormula`-Klasse entstehen.

------------------------------------------------------------------------

# Status-System

Basisklasse:

`StatusEffect`

Spätere Spezialisierungen:

-   Pain
-   Encumbrance
-   Fear
-   Stupor
-   ...

Mehrere Instanzen desselben Zustands sollen gleichzeitig möglich sein.

Beispiel:

``` text
Pain()
Pain(remaining_rounds=3)
```

Dadurch entsteht effektiv Schmerz II.

Status besitzen:

-   remaining_rounds

Creature besitzt:

``` python
next_round()
```

welches alle Status herunterzählt und abgelaufene Effekte entfernt.

Status verändern **nicht dauerhaft** die Basiswerte.

Berechnete Werte berücksichtigen lediglich die aktiven Status.

------------------------------------------------------------------------

# Architekturprinzip

Basiswerte werden niemals direkt verändert.

``` text
Basiswert
    +
aktive Status
    +
temporäre Effekte
    =
aktueller Wert
```

Dadurch entfällt jedes "Rückgängigmachen" von Effekten.

------------------------------------------------------------------------

# Importer

## Regelwiki

`regelwiki_scraper.py`

liefert `Creature`-Objekte oder JSON.

## PDF

`pdf_loader.py`

liefert ebenfalls `Creature`-Objekte.

Creature kennt weder PDFs noch Webseiten.

------------------------------------------------------------------------

# Zielarchitektur

``` text
PDF
        ↓

     Creature

        ↑

 Regelwiki
```

GUI, Kampfverwaltung und Würfelsystem arbeiten ausschließlich mit
`Creature`-Objekten.

------------------------------------------------------------------------

# Arbeitsweise

Ich möchte gemeinsam eine saubere Softwarearchitektur entwickeln und
nicht möglichst schnell Code erzeugen.

Bitte:

-   erkläre Architekturentscheidungen,
-   begründe Verbesserungen,
-   vermeide unnötige Umbauten,
-   behalte die bestehende Architektur möglichst bei,
-   schlage Refactorings nur vor, wenn sie einen klaren langfristigen
    Vorteil bringen.
