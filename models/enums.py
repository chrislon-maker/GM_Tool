from enum import Enum, IntEnum, auto

class WeaponType(Enum):
    CROSSBOW = "Armbrust"
    BLOWGUN = "Blasrohr"
    BOW = "Bogen"
    DISCUS = "Diskus"
    FIREBREATH = "Feuerspucken"
    SPIN = "Schleuder"
    THROW = "Wurfwaffe"

    DAGGERS = "Dolche"
    FAN = "Fächer"
    FENCING = "Fechtwaffe"
    BLUNT = "Hiebwaffe"
    CHAIN = "Kettenwaffe"
    LANCE = "Lanze"
    WHIP = "Peitsche"
    BRAWL = "Raufen"
    SHIELD = "Schild"
    SWORD = "Schwert"
    SKEWER = "Spießwaffe"
    POLEARMS = "Stangenwaffen"
    BLUNT_2H = "Zweihandhiebwaffe"
    SWORD_2H = "Zweihandschwert"


class MeeleWeaponRange(IntEnum):
    SHORT = 0
    MEDIUM = 1
    LONG = 2
    OVERLONG = 3

    @property
    def label(self):
        return {
            MeeleWeaponRange.SHORT: "kurz",
            MeeleWeaponRange.MEDIUM: "mittel",
            MeeleWeaponRange.LONG: "lang",
            MeeleWeaponRange.OVERLONG: "überlang",
        }[self]
    

class ShieldSize(IntEnum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2

    @property
    def label(self):
        return {
            MeeleWeaponRange.SMALL: "kleiner Schild",
            MeeleWeaponRange.MEDIUM: "mittelerer Schild",
            MeeleWeaponRange.LARGE: "großer Schild",
        }[self]

class WhereEquipped(Enum):
    OFFHAND = "Nebenhand"
    MAINHAND = "Haupthand"
    TWO_HANDED = "Beidhändig"

class Attribute(Enum):
    MU = "MU"
    KL = "KL"
    IN = "IN"
    CH = "CH"
    FF = "FF"
    GE = "GE"
    KO = "KO"
    KK = "KK"

class SizeCategory(IntEnum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    HUGE = 4

    @property
    def label(self):
        return {
            SizeCategory.TINY: "winzig",
            SizeCategory.SMALL: "klein",
            SizeCategory.MEDIUM: "mittel",
            SizeCategory.LARGE: "groß",
            SizeCategory.HUGE: "riesig",
        }[self]


class TalentTag(Enum):
    FLYING = "Fliegen"
    JUGGLING = "Gaukeleien"
    CLIMBING = "Klettern"
    BODY_CONTROL = "Körperbeherrschung"
    FEAT_OF_STRENGTH = "Kraftakt"
    RIDING = "Reiten"
    SWIMMING = "Schwimmen"
    SELF_CONTROL = "Selbstbeherrschung"
    SINGING = "Singen"
    PERCEPTION = "Sinnesschärfe"
    DANCING = "Tanzen"
    PICKPOCKETING = "Taschendiebstahl"
    STEALTH = "Verbergen"
    DRINKING = "Zechen"

    CONVINCE = "Bekehren & Überzeugen"
    SEDUCTION = "Betören"
    INTIMIDATION = "Einschüchtern"
    ETIQUETTE = "Etikette"
    STREET_WISDOM = "Gassenwissen"
    HUMAN_NATURE = "Menschenkenntnis"
    PERSUADE = "Überreden"
    DISGUISE = "Verkleiden"
    WILLPOWER = "Willenskraft"

    TRACKING = "Fährtensuchen"
    CAPTIVATE = "Fesseln"
    FISCHING = "Fischen & Angeln"
    ORIENTATION = "Orientierung"
    BOTANICS = "Pflanzenkunde"
    ZOOLOGY = "Tierkunde"
    SURVIVAL = "Wildnisleben"

    GAMBLE = "Brett- & Glücksspiel"
    GEOGRAPHY = "Geographie"
    HISTORY = "Geschichtswissen"
    RELIGION = "Götter & Kulte"
    WARFARE = "Kriegskunst"
    MAGIC = "Magiekunde"
    MECHANICS = "Mechanik"
    MATH = "Rechnen"
    LAW = "Rechtskunde"
    LEGENDS = "Sagen & Legenden"
    SPHERES = "Sphärenkunde"
    ASTRONOMY = "Sternenkunde"

    ALCHEMY = "Alchemie"
    SEEFARING = "Boote & Schiffe"
    VEHICLES = "Fahrzeuge"
    TRADE = "Handel"
    MEDICINE_POISSON = "Heilkunde Gift"
    MEDICINE_DISEASE = "Heilkunde Krankheiten"
    MEDICINE_MIND = "Heilkunde Seele"
    MEDICINE_WOUNDS = "Heilkunde Wunden" 
    WOOD_CRAFTING = "Hoilzbearbeitung"
    COOKING = "Lebensmittelbearbeitung"
    FURRIER = "Lederbearbeitung"
    PAINTING = "Malen & Zeichnen"
    BLACKSMITHING = "Metallbearbeitung"
    MUSIC = "Musizieren"
    LOCKPICKING = "Schlösserknacken"
    STONE_MASONRY = "Steinbearbeitung"
    TAYLORING = "Stoffbearbeitung"

class SpellTag(Enum):
    IGNIFAXIUS = "Ignifaxius"

class ValueType(Enum):
    MOVEMENT_SPEED = auto()
    SOUL_POWER = auto()
    TOUGHNESS = auto()
    INITIATIVE = auto()
    EVASION = auto()

    TALENT_CHECK = auto()

    MELEE_ATTACK = auto()
    RANGED_ATTACK = auto()
    PARRY = auto()

    DAMAGE = auto()


class ModifierTag(Enum):
    PHYSICAL = auto()
    MENTAL = auto()
    SOCIAL = auto()

    COMBAT = auto()
    ATTACK = auto()
    DEFENSE = auto()
    MELEE = auto()
    RANGED = auto()

    MOVEMENT = auto()
    SPEECH = auto()
    CRAFT = auto()
    NATURE = auto()
