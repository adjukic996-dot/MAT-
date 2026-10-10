#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seitengenerator — MAT Elektrotechnik
====================================
Erzeugt alle .html-Dateien des Projekts aus einer Quelle.

ACHTUNG: Die erzeugten .html-Dateien werden bei jedem Lauf UEBERSCHRIEBEN.
Aenderungen bitte hier im Skript machen, nicht in den HTML-Dateien —
sonst sind sie beim naechsten Lauf weg.

Aufruf aus dem Projektordner:   python3 _werkzeug/seiten-bauen.py

Grundregel: Es steht nichts auf den Seiten, was nicht belegt ist.
Texte stammen von der Bestandsseite des Kunden, Firmendaten aus dem
Handelsregister. Fehlende Angaben werden WEGGELASSEN, nicht erfunden.
Die Liste der Luecken steht in BRIEF.md Teil 4.
"""

import pathlib, re, html, json

WURZEL = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://adjukic996-dot.github.io/MAT-"

TEL_ROH = "+498923750352"
TEL = "089 23750352"
MAIL = "info@mat-elektrotechnik.de"

# --------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------
NAV = [
    ("start",       "index.html",        "Start"),
    ("leistungen",  "leistungen.html",   "Leistungen"),
    ("unternehmen", "unternehmen.html",  "Unternehmen"),
    ("referenzen",  "referenzen.html",   "Referenzen"),
    ("karriere",    "karriere.html",     "Karriere"),
    ("kontakt",     "kontakt.html",      "Kontakt"),
]

# --------------------------------------------------------------------------
# Die acht Leistungen
# --------------------------------------------------------------------------
LEISTUNGEN = [
    dict(slug="elektroinstallation", nr="01", titel="Elektroinstallation",
         kurz="Neubau, Umbau, Sanierung — Rohbau-, Haus- und Betriebsinstallation, "
              "Verteiler, Licht und Kraft, Sprech- und Alarmanlagen.",
         bild="bild-04", alt="Geöffneter Sicherungskasten mit beschrifteten Leitungen"),
    dict(slug="verteilerbau", nr="02", titel="Verteilerbau und Schaltschrankbau",
         kurz="Planung in E-Plan, typengeprüfte Schaltanlagen nach VDE, Stückprüfung "
              "vor der Auslieferung.",
         bild="schaltschrank-10", alt="Geöffneter Schaltschrank mit Reihenklemmen und Automaten"),
    dict(slug="ladeinfrastruktur", nr="03", titel="Ladeinfrastruktur",
         kurz="Wallbox für zu Hause oder Ladepunkte für den Betrieb — mit vorheriger "
              "Prüfung der bestehenden Anlage.",
         bild="bild4-4", alt="Zwei Personen bei einer Beratung, im Hintergrund ein Tesla-Schild"),
    dict(slug="photovoltaik", nr="04", titel="Photovoltaik",
         kurz="Beratung, Auslegung, Installation und Inbetriebnahme aus einer Hand. "
              "Schwerpunkt Gewerbe und Industrie.",
         bild="original-d406c9b1-c57d-4c30-a53f-d22e52db7b4f", alt="Photovoltaikmodule auf einem Ziegeldach"),
    dict(slug="blitzschutz", nr="05", titel="Blitz- und Überspannungsschutz",
         kurz="Äußerer Blitzschutz, Erdung und innerer Überspannungsschutz für "
              "Wohnhäuser und Betriebsanlagen.",
         bild="referenz-38", alt="Monteur bei Arbeiten auf einem Dach"),
    dict(slug="netzwerktechnik", nr="06", titel="Netzwerk- und IT-Infrastruktur",
         kurz="Strukturierte Gebäudeverkabelung nach Norm — sternförmig, mit Reserve, "
              "vollständig dokumentiert.",
         bild="bild-18", alt="Patchfeld mit farbig sortierten Netzwerkleitungen"),
    dict(slug="pruefung-wartung", nr="07", titel="Prüfung und Wartung",
         kurz="Sicherheitsprüfung elektrischer Anlagen und Geräte, mit Prüfprotokoll.",
         bild="installation-wohnung-65",
         alt="Wohnungsverteiler mit Prüfprotokoll an der Innenseite der Tür"),
    dict(slug="antennentechnik", nr="08", titel="Antennen- und Empfangstechnik",
         kurz="TV- und SAT-Anlagen: Beratung zum Montageort, Montage, Einmessung.",
         bild="bild-12", alt="Satellitenschüssel auf einem Ziegeldach"),
]
L_NACH_SLUG = {l["slug"]: l for l in LEISTUNGEN}

# --------------------------------------------------------------------------
# Team — Namen und Rollen aus der Bestandsseite
# --------------------------------------------------------------------------
TEAM = [
    ("miodrag-manojlovic",  "Miodrag Manojlovic",  "Geschäftsführer, Elektrotechnikermeister"),
    ("andjelina-manojlovic","Andjelina Manojlovic", "Assistenz der Geschäftsführung"),
    ("srdjana-tomasic",     "Srdjana Tomasic",      "Projektmanagerin"),
    ("borislav-terzic",     "Borislav Terzic",      "Obermonteur"),
    ("andreja-sulejic",     "Andreja Sulejic",      "Obermonteur"),
    ("sadik-sadiku",        "Sadik Sadiku",         "Monteur"),
    ("mohammad-nimrozi",    "Mohammad Nimrozi",     "Monteur"),
    ("ahmed-demic",         "Ahmed Demic",          "Monteur"),
    ("muhamed-demic",       "Muhamed Demic",        "Monteur"),
    ("drazen-valcic",       "Drazen Valcic",        "Monteur"),
    ("veljko-stefanovic",   "Veljko Stefanovic",    "Auszubildender"),
    ("johannes-burger",     "Johannes Burger",      "Auszubildender"),
    ("rahim-hosseini",      "Rahim Hosseini",       "Auszubildender"),
]

# --------------------------------------------------------------------------
# Kundenstimmen — woertlich von der Referenzseite des Kunden
# --------------------------------------------------------------------------
STIMMEN = [
    ("Margit Riepertinger",
     "Die Firma MAT-Elektrotechnik haben wir anhand der vorherigen guten Bewertungen "
     "und der Ortsnähe ausgewählt. Die Mitarbeiter sind sehr freundlich, super "
     "zuverlässig und vor allem kompetent. Alles wurde schnell und sauber installiert "
     "und das alles zu einem sehr fairen Preis."),
    ("Thomas Fuchsbichler",
     "Wir haben eine über 50 Jahre alte Hauptverteilung im Keller auf den aktuellen "
     "Stand inkl. Aufbau einer Wallbox-Stromversorgung durchführen lassen. Vom ersten "
     "Vorgespräch, über die Planung und bis zur Ausführung der Arbeiten bin ich sehr "
     "zufrieden! Hier fühlt man sich rundum sorglos betreut."),
    ("Kerstin Dausel",
     "Wir haben komplett neu saniert und alles musste neu gemacht werden — auch die "
     "Elektrik. Super kompetente Beratung mit viel Engagement. Wir haben uns jederzeit "
     "gut betreut gefühlt und es war immer jemand erreichbar!"),
    ("Florian Bogner",
     "Sehr professionell, freundlicher Kontakt, alle Arbeiten zur vollsten "
     "Zufriedenheit ausgeführt — gerne wieder!"),
    ("Thomas Fischer",
     "Sehr kompetent und absolut zuverlässig. Nettes Team und absolut empfehlenswert. "
     "Die Arbeit wurde immer sauber erledigt. Deshalb arbeiten wir schon viele Jahre "
     "zusammen."),
    ("M. Urban",
     "Schnelle unkomplizierte Projektierung, zeitnahe mängelfreie Ausführung — "
     "nur zu empfehlen!"),
]

# --------------------------------------------------------------------------
# Referenzgalerie
# --------------------------------------------------------------------------
GALERIE_GRUPPEN = [
 ("Verteiler und Schaltanlagen", [
   ("schaltschrank-10", "Schaltschrank mit Reihenklemmen und Sicherungsautomaten"),
   ("bild-04", "Verteiler mit beschrifteten Abgängen"),
   ("bild10-10", "Zählerverteiler im Hausanschlussraum"),
   ("referenz-25", "Unterverteilung in einer Wandnische"),
   ("installation-wohnung-65", "Wohnungsverteiler mit Prüfprotokoll an der Innenseite"),
   ("bild8-8", "Verteilerschränke in einem Technikraum"),
 ]),
 ("Netzwerk und EDV", [
   ("bild-18", "Patchfeld mit farbig sortierten Netzwerkleitungen"),
   ("bild-09", "Rangierfeld einer strukturierten Verkabelung"),
   ("bild-01", "Arbeiten an einem Serverschrank"),
   ("bild-08", "Netzwerkverteilung in einem Serverraum"),
   ("multimedia-schrank-03", "Multimediaverteiler mit Netzwerk- und Antennentechnik"),
 ]),
 ("Beleuchtung", [
   ("treppenspots-03", "Treppenbeleuchtung mit eingelassenen Spots"),
   ("treppenspots-09", "Stufenbeleuchtung in einem Treppenhaus"),
   ("kuechen-beleuchtung", "Küchenbeleuchtung mit Unterschrankleuchten"),
   ("led-beleuchtung", "Indirekte LED-Beleuchtung in einem Flur"),
   ("lampen-installation", "Montierte Pendelleuchten in einem Wohnraum"),
   ("beleuchtung-2", "Wandleuchten mit Lichtkegel nach oben und unten"),
   ("beleuchtung-4", "Beleuchteter Flur mit Deckenleuchte"),
   ("beleuchtung3", "Indirekte Beleuchtung einer Wandnische"),
   ("schlafzimmer-beleuchtung", "Indirekte Deckenbeleuchtung im Schlafzimmer"),
   ("referenz-34", "Wandfluter in einem Innenraum"),
   ("referenz-50", "Küchenzeile mit Arbeitsplatzbeleuchtung"),
   ("referenz-13", "Außenleuchte an einer Natursteinwand"),
   ("installation-terrassenbeleuchtung", "Terrassenbeleuchtung an einer Dachkante"),
   ("bild-10", "Wegebeleuchtung mit Pollerleuchten bei Dämmerung"),
   ("referenz-14", "Beleuchteter Flur mit Blick in den Garten"),
 ]),
 ("Sprechanlagen", [
   ("sprechanlage", "Innenstation einer Video-Sprechanlage"),
   ("sprechanlage1", "Außenstation einer Sprechanlage mit Kamera"),
 ]),
 ("Photovoltaik", [
   ("original-d406c9b1-c57d-4c30-a53f-d22e52db7b4f", "Photovoltaikmodule auf einem Ziegeldach"),
   ("original-8f303208-bec4-4374-92df-bdcf119328bd", "Baustelle mit Gerüst und Bauschild"),
   ("img-0055", "Wechselrichter einer Photovoltaikanlage"),
   ("img-1906", "Batteriespeicher in einem Technikraum"),
 ]),
 ("Dach, Blitzschutz und Baustelle", [
   ("referenz-38", "Monteur bei Arbeiten auf einem Dach"),
   ("bild-12", "Satellitenschüssel auf einem Ziegeldach"),
   ("bild6-6", "Flachdach mit Lichtkuppeln"),
   ("bild7-7", "Dachfläche im Winter"),
   ("baustelle-3", "Verlegearbeiten auf einer Rohbaudecke"),
   ("referenz-46", "Erdarbeiten für eine Außeninstallation"),
 ]),
]

# ==========================================================================
# Bausteine
# ==========================================================================

def bilddaten():
    p = WURZEL / "bilder" / "_bilder.json"
    if not p.exists():
        return {}
    return {b["datei"].rsplit(".", 1)[0]: b for b in json.loads(p.read_text()) if b.get("typ") == "webp"}

BILD = bilddaten()


def img(name, alt, klasse="", lazy=True, sizes=None):
    """Bild mit width/height gegen Layoutspruenge.

    Wird `sizes` uebergeben und existiert eine kleine Variante, liefert das Bild
    ein srcset aus. Der Browser laedt dann auf Kacheln und in der Galerie die
    560-px-Fassung statt der grossen — das spart auf der Referenzseite rund 1,9 MB.
    """
    d = BILD.get(name)
    if not d:
        # Frueher wurde hier nur ein HTML-Kommentar ausgegeben. Das Ergebnis war eine
        # leere Bildflaeche auf der Photovoltaik-Seite, die niemandem auffiel.
        # Ein fehlendes Bild ist ein Baufehler und bricht den Lauf ab.
        raise SystemExit(f"\nABBRUCH: Bild '{name}' liegt nicht in bilder/.\n"
                         f"         Vorhandene aehnliche: "
                         + ", ".join(sorted(b for b in BILD if b.startswith(name[:14])) or ["keine"]))
    k = f' class="{klasse}"' if klasse else ""
    l = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    srcset = ""
    sz = ""
    if sizes and d.get("sm"):
        srcset = (f' srcset="{{P}}bilder/{name}-sm.webp {d["sm"]["w"]}w,'
                  f' {{P}}bilder/{name}.webp {d["w"]}w"')
        sz = f' sizes="{sizes}"'
    elif sizes:
        sz = f' sizes="{sizes}"'
    return (f'<img src="{{P}}bilder/{name}.webp"{srcset}{sz}'
            f' width="{d["w"]}" height="{d["h"]}"'
            f' alt="{html.escape(alt, quote=True)}"{k}{l}>')



def baue_jsonld(pfad, titel, krumenpfad=None):
    """Strukturierte Daten. Nur belegte Angaben — Handelsregister und Bestandsseite.
    Keine Oeffnungszeiten, keine Preise, keine Bewertungen: liegen nicht vor."""
    import json as _json
    betrieb = {
        "@context": "https://schema.org",
        "@type": "Electrician",
        "@id": SITE + "/#betrieb",
        "name": "Mat-Elektrotechnik GmbH",
        "legalName": "Mat-Elektrotechnik GmbH",
        "url": SITE + "/",
        "logo": SITE + "/bilder/logo-mat.svg",
        "image": SITE + "/bilder/og-start.jpg",
        "telephone": "+49 89 23750352",
        "email": MAIL,
        "foundingDate": "2010",
        "vatID": "DE323580611",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Industriestraße 12",
            "postalCode": "82110",
            "addressLocality": "Germering",
            "addressRegion": "Bayern",
            "addressCountry": "DE",
        },
        "founder": {"@type": "Person", "name": "Miodrag Manojlovic"},
        "areaServed": {"@type": "Place", "name": "Großraum München"},
        "award": "Markenpreis ELMAR 2023",
        "knowsAbout": [l["titel"] for l in LEISTUNGEN],
    }
    bloecke = [betrieb]
    if krumenpfad:
        bloecke.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": t,
                 "item": SITE + "/" + (z or "")}
                for i, (t, z) in enumerate(krumenpfad)
            ],
        })
    return "".join('<script type="application/ld+json">' +
                   _json.dumps(b, ensure_ascii=False, separators=(",", ":")) +
                   "</script>\n" for b in bloecke)


def kopf(seite, titel, beschreibung, pfad, tiefe=0, og_bild="og-start.jpg", krumenpfad=None):
    P = "../" * tiefe
    jsonld = baue_jsonld(pfad, titel, krumenpfad)
    # Startseite kanonisch ohne Dateinamen
    url = SITE + "/" if pfad == "index.html" else SITE + "/" + pfad
    zeilen = []
    for k, ziel, text in NAV:
        aktuell = ' aria-current="page"' if k == seite else ""
        zeilen.append(f'        <li><a href="{P}{ziel}"{aktuell}>{text}</a></li>')
    nav = "\n".join(zeilen)
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(beschreibung, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Mat-Elektrotechnik GmbH">
<meta property="og:title" content="{html.escape(titel, quote=True)}">
<meta property="og:description" content="{html.escape(beschreibung, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/bilder/{og_bild}">
<meta name="twitter:card" content="summary_large_image">
<!-- VORSCHAU: Die Seite ist noch nicht freigegeben (Impressum nicht
     gegengezeichnet, Fotoeinwilligungen offen) und sie wuerde in der Suche
     mit der echten Kundenseite mat-elektrotechnik.de konkurrieren.
     ZUM LIVEGANG: diese Zeile loeschen und robots.txt anpassen. -->
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{P}bilder/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{P}bilder/apple-touch-icon.png">
<link rel="preload" href="{P}fonts/ibm-plex-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}stil.css">
{jsonld}</head>
<body>

<a class="skip" href="#inhalt">Zum Inhalt springen</a>

<header class="header">
  <div class="wrap header__inner">
    <div class="header__top">
      <a class="logo" href="{P}index.html" aria-label="Mat-Elektrotechnik, zur Startseite">
        <img src="{P}bilder/logo-mat.svg" alt="Mat-Elektrotechnik" width="118" height="34">
      </a>
      <a class="header__tel" href="tel:{TEL_ROH}">{TEL}</a>
    </div>
    <nav class="nav" aria-label="Hauptnavigation">
      <ul>
{nav}
      </ul>
    </nav>
  </div>
</header>

<main id="inhalt">
"""


def krumen(items, tiefe=0):
    P = "../" * tiefe
    teile = []
    for i, (text, ziel) in enumerate(items):
        if ziel and i < len(items) - 1:
            teile.append(f'<li><a href="{P}{ziel}">{text}</a></li>')
        else:
            teile.append(f'<li aria-current="page">{text}</li>')
    return ('<nav class="krumen" aria-label="Sie sind hier"><div class="wrap"><ol>'
            + "".join(teile) + "</ol></div></nav>")


def weiter_zu(links, tiefe=0, titel="Weiter zu"):
    P = "../" * tiefe
    li = "".join(f'<li><a href="{P}{z}">{t}</a></li>' for t, z in links)
    return f"""<section class="weiter"><div class="wrap">
  <p class="label">{titel}</p>
  <ul>{li}</ul>
</div></section>"""


def cta_band(tiefe=0):
    P = "../" * tiefe
    return f"""<section class="on-dark">
  <div class="wrap">
    <div class="prose stack-lg">
      <p class="label">Kontakt</p>
      <h2>Sprechen wir darüber.</h2>
      <p>Ob eine defekte Steckdose, ein überfälliger Prüftermin oder eine Halle, die neu
        verkabelt werden muss — schildern Sie uns kurz Ihr Anliegen. Wir sagen Ihnen
        offen, ob wir der richtige Betrieb dafür sind.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="{P}kontakt.html">Anfrage senden</a>
        <a class="btn btn--secondary" href="tel:{TEL_ROH}">{TEL}</a>
      </div>
    </div>
  </div>
</section>"""


def fuss(tiefe=0, skript=""):
    P = "../" * tiefe
    leist = "".join(
        f'<li><a href="{P}leistungen/{l["slug"]}.html">{l["titel"]}</a></li>'
        for l in LEISTUNGEN[:4])
    return f"""</main>

<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <img src="{P}bilder/logo-mat.svg" alt="Mat-Elektrotechnik" width="118" height="34" style="margin-bottom:var(--s-05)">
        <address class="small muted" style="font-style:normal">
          Mat-Elektrotechnik GmbH<br>
          Industriestraße 12, 82110 Germering<br>
          <a href="tel:{TEL_ROH}">{TEL}</a><br>
          <a href="mailto:{MAIL}">{MAIL}</a>
        </address>
      </div>
      <nav aria-label="Leistungen">
        <p class="label">Leistungen</p>
        <ul>{leist}
          <li><a href="{P}leistungen.html">Alle Leistungen</a></li>
        </ul>
      </nav>
      <nav aria-label="Unternehmen">
        <p class="label">Unternehmen</p>
        <ul>
          <li><a href="{P}unternehmen.html">Der Betrieb</a></li>
          <li><a href="{P}referenzen.html">Referenzen</a></li>
          <li><a href="{P}karriere.html">Karriere</a></li>
          <li><a href="{P}kontakt.html">Kontakt</a></li>
        </ul>
      </nav>
      <nav aria-label="Rechtliches">
        <p class="label">Rechtliches</p>
        <ul>
          <li><a href="{P}impressum.html">Impressum</a></li>
          <li><a href="{P}datenschutz.html">Datenschutz</a></li>
        </ul>
      </nav>
    </div>
    <p class="footer__legal small">
      © <span id="jahr">2026</span> Mat-Elektrotechnik GmbH · Amtsgericht München HRB 246899
    </p>
  </div>
</footer>
<script>var j=document.getElementById("jahr");if(j)j.textContent=new Date().getFullYear();</script>
{skript}
</body>
</html>
"""


def schreibe(pfad, inhalt):
    p = WURZEL / pfad
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(inhalt.replace("{P}", "../" * (len(pathlib.Path(pfad).parts) - 1)), encoding="utf-8")
    return len(inhalt)


# ==========================================================================
# Volltexte der acht Leistungsseiten
# Quelle: Bestandsseite des Kunden, sprachlich bereinigt, inhaltlich unveraendert.
# ==========================================================================

INHALT = {
"elektroinstallation": dict(
  vorzeile="Ihr Elektroinstallateur vor Ort",
  h1="Elektroinstallation",
  lead="Als elektrotechnischer Allrounder befassen wir uns mit jeder Art von "
       "Elektroinstallation. Ob komplette Neuinstallation oder Erweiterung und Prüfung "
       "einer vorhandenen Anlage — wir begleiten Sie von der Planung bis zur Ausführung.",
  body=[
    ("Rohbau, Haus, Betrieb",
     ["Je nachdem, ob es sich um eine Rohbau-, Haus- oder Betriebsinstallation handelt, "
      "stehen wir Ihnen mit unserem Know-how und langjähriger Erfahrung zur Verfügung. "
      "Wir arbeiten für Privatwohnungen ebenso wie für Hausverwaltungen, Büros und "
      "Produktionshallen."]),
    ("Smart Home und KNX",
     ["Neue Technologien wie EIB/KNX-Bussysteme machen Schalter programmierbar und "
      "ermöglichen die Steuerung von Alarmanlagen, Jalousien oder Licht über Internet "
      "oder Telefon. Intelligente Hauslösungen bringen Beschattung, Heizung und "
      "Beleuchtung in Einklang.",
      "Wir beraten Sie und finden eine Lösung, die auf Ihre Bedürfnisse und Ihr Budget "
      "zugeschnitten ist."]),
  ],
  liste_titel="Unser Installationsangebot",
  liste=["Elektro-Neuinstallation (Rohbau-, Haus- und Betriebsinstallation)",
         "Verteileranlagen", "EIB/KNX-Bussystem", "Sprechanlagen", "EDV-Netzwerke",
         "Alarmsysteme", "Notbeleuchtungssysteme",
         "Beleuchtung und Sicherheitsbeleuchtung"],
  galerie=[("referenz-25","Unterverteilung in einer Wandnische"),
           ("installation-wohnung-65","Wohnungsverteiler mit Prüfprotokoll"),
           ("lampen-installation","Montierte Pendelleuchten"),
           ("treppenspots-03","Treppenbeleuchtung mit eingelassenen Spots")]),

"verteilerbau": dict(
  vorzeile="Perfekt dimensionierte Steuerungsanlagen",
  h1="Verteilerbau und Schaltschrankbau",
  lead="Je nach Bedarf planen, fertigen und montieren wir neue Verteileranlagen und "
       "installieren sämtliche Steuerungen — von der Heizung über die elektrische "
       "Jalousie bis zur Torsteuerung.",
  body=[
    ("Maßgeschneiderte Schaltschranksysteme",
     ["Wir konstruieren und bauen Schaltschränke in unterschiedlichen Bauformen, ganz "
      "nach Ihren Anforderungen und Betriebsnormen. Jeder Schaltschrank wird von uns "
      "vor der Auslieferung gemäß den entsprechenden nationalen und internationalen "
      "Normen geprüft."]),
    ("Sanierung statt Ersatz",
     ["Bestehende Verteiler sanieren und modernisieren wir, statt sie pauschal zu "
      "ersetzen. Als elektrotechnischer Komplettanbieter begleiten wir die gesamte "
      "Prozesskette von der Planung über den Bau des Schaltschranks bis zur Ausführung "
      "der gesamten elektrischen Anlage."]),
  ],
  liste_titel="Bauformen, die wir fertigen",
  liste=["Typengeprüfte Schaltanlagenkombinationen nach VDE-Norm",
         "Wandler- und Zählerverteiler vom Einfamilienhaus bis zur Firmeneinspeisung",
         "Motor Control Center", "Steuerverteiler"],
  galerie=[("schaltschrank-10","Geöffneter Schaltschrank mit Reihenklemmen"),
           ("bild8-8","Verteilerschränke in einem Technikraum"),
           ("bild10-10","Zählerverteiler im Hausanschlussraum"),
           ("bild-04","Verteiler mit beschrifteten Abgängen")]),

"ladeinfrastruktur": dict(
  vorzeile="Elektromobilität",
  h1="Ladeinfrastruktur",
  lead="Bei der Umstellung auf Elektromobilität unterstützen wir Sie als "
       "Elektrofachbetrieb bei der Installation Ihrer Wallbox — zu Hause wie im Betrieb.",
  body=[
    ("Erst prüfen, dann montieren",
     ["Wir garantieren nicht nur eine fachgerechte Montage, sondern prüfen auch, ob "
      "Ihre bestehende Elektroinstallation für diese Aufgabe geeignet ist, und führen "
      "bei Bedarf alle erforderlichen Anpassungen durch.",
      "Eine Wallbox an eine zu schwache Leitung zu hängen ist kein Sparen. Deshalb steht "
      "die Prüfung von Hausanschluss und Verteilung bei uns am Anfang, nicht am Ende."]),
  ],
  galerie=[("bild4-4","Beratungsgespräch zur Ladeinfrastruktur"),
           ("img-0055","Technikinstallation an einer Wand")]),

"photovoltaik": dict(
  vorzeile="Photovoltaikanlagen",
  h1="Photovoltaik",
  lead="Als Ihr Ansprechpartner rund um Photovoltaik bieten wir umfassende Beratung, "
       "Planung und Umsetzung inklusive Installation — alles aus einer Hand.",
  body=[
    ("Schwerpunkt Gewerbe und Industrie",
     ["Wir verfügen über langjährige Erfahrung in der Umsetzung von Großprojekten für "
      "Industrie- und Gewerbekunden im Bereich PV-Großanlagen. Wir wissen, dass jedes "
      "Projekt einzigartig ist, und entwickeln ein maßgeschneidertes Konzept für Ihre "
      "Anlage.",
      "Dabei legen wir Wert auf Effizienz und Nachhaltigkeit, um Ihnen langfristige "
      "Einsparungen zu ermöglichen. Im Anschluss organisieren wir die komplette "
      "Umsetzung Ihres Projekts."]),
  ],
  galerie=[("original-d406c9b1-c57d-4c30-a53f-d22e52db7b4f","Photovoltaikmodule auf einem Ziegeldach"),
           ("original-8f303208-bec4-4374-92df-bdcf119328bd","Baustelle mit Gerüst und Bauschild"),
           ("img-0055","Wechselrichter einer Photovoltaikanlage"),
           ("img-1906","Batteriespeicher in einem Technikraum")]),

"blitzschutz": dict(
  vorzeile="Damit nicht plötzlich der Blitz einschlägt",
  h1="Blitz- und Überspannungsschutz",
  lead="Blitzschläge stellen nicht nur eine Gefahr für Gebäude dar, sondern können "
       "sämtliche im Stromkreis befindlichen Geräte zerstören. Eine professionelle "
       "Blitzschutzanlage ist die geeignete Sicherheitsmaßnahme.",
  body=[
    ("Überspannungen — unterschätzte Gefahr",
     ["Überspannungen werden noch immer häufig unterschätzt. Es handelt sich dabei um "
      "Spannungsimpulse, sogenannte Transienten, die nur für Sekundenbruchteile "
      "auftreten. Gründe hierfür können direkte, nahe oder ferne Blitzeinschläge sowie "
      "Schalthandlungen eines Elektrizitätswerks sein."]),
    ("Direkte und nahe Blitzeinschläge",
     ["Direkt- oder Naheinschläge sind Blitzeinschläge in das Gebäude, in dessen "
      "unmittelbare Umgebung oder in die eingeführten Versorgungsleitungen — etwa "
      "Niederspannungsstromversorgung, Telekommunikations- und Datenleitungen. Die "
      "entstehenden Stoßströme und das zugehörige elektromagnetische Feld stellen eine "
      "besondere Bedrohung für das zu schützende System dar.",
      "Ein direkter Blitzeinschlag verursacht durch den fließenden Blitzstrom eine "
      "Potenzialanhebung von mehreren 100.000 Volt an allen geerdeten Geräten. Das ist "
      "die stärkste Beanspruchung elektrischer Anlagen in Gebäuden.",
      "Zusätzlich entstehen Überspannungen in der Gebäudeanlage durch die "
      "Induktionswirkung des elektromagnetischen Blitzfeldes. Deren Energie ist geringer "
      "als die des direkten Blitzstoßstromes, für empfindliche Elektronik aber "
      "ausreichend zerstörerisch."]),
  ],
  galerie=[("referenz-38","Monteur bei Arbeiten auf einem Dach"),
           ("bild6-6","Flachdach mit Lichtkuppeln"),
           ("bild7-7","Dachfläche im Winter")]),

"netzwerktechnik": dict(
  vorzeile="Strukturierte Verkabelung und mehr",
  h1="Netzwerk- und IT-Infrastruktur",
  lead="Eine strukturierte Verkabelung ist Ihr einheitlicher Aufbauplan für eine "
       "zukunftsorientierte und anwendungsunabhängige Netzwerkinfrastruktur, auf der "
       "Sprache und Daten übertragen werden.",
  body=[
    ("Allgemeingültige Strukturen",
     ["Eine strukturierte Verkabelung berücksichtigt die Anforderungen mehrerer Jahre, "
      "enthält Reserven und kann unabhängig von der Anwendung genutzt werden. So ist es "
      "üblich, dieselbe Verkabelung für das lokale Netzwerk und die Telefonie zu nutzen. "
      "Damit werden teure Fehlinstallationen vermieden und die Installation neuer "
      "Komponenten erleichtert."]),
  ],
  liste_titel="Ziele einer strukturierten Verkabelung",
  liste=["Unterstützung aller heutigen und zukünftigen Kommunikationssysteme",
         "Kapazitätsreserve hinsichtlich der Grenzfrequenz",
         "Neutrales Verhalten gegenüber Übertragungsprotokoll und Endgeräten",
         "Flexible Erweiterbarkeit",
         "Ausfallsicherheit durch sternförmige Verkabelung",
         "Datenschutz und Datensicherheit müssen realisierbar sein",
         "Einhaltung existierender Standards",
         "Standardisierte Mess-, Prüf- und Dokumentationsverfahren"],
  galerie=[("bild-18","Patchfeld mit farbig sortierten Netzwerkleitungen"),
           ("bild-09","Rangierfeld einer strukturierten Verkabelung"),
           ("bild-01","Arbeiten an einem Serverschrank"),
           ("multimedia-schrank-03","Multimediaverteiler")]),

"pruefung-wartung": dict(
  vorzeile="Es geht immer um die Sicherheit",
  h1="Prüfung und Wartung",
  lead="Wir führen Sicherheitsprüfungen an Ihrer elektrischen Anlage durch. Treten "
       "dabei Sicherheitslücken zutage, kann sofort durch ein Update auf neueste "
       "Standards reagiert werden.",
  body=[
    ("Warum geprüft wird",
     ["Die langjährige Erfahrung bei Wartung und Erweiterung elektrischer Anlagen hat "
      "uns gezeigt, wie wichtig regelmäßige Prüfung ist. Auch in einer auf den ersten "
      "Blick sicheren Elektroinstallation haben wir oft gravierende Fehler entdeckt. "
      "Vielfach lassen sich diese Mängel durch geringfügige Änderungen beheben, bevor "
      "etwas passiert.",
      "Nach der Prüfung erstellen wir ein elektrotechnisches Sicherheitsprotokoll."]),
  ],
  liste_titel="Wir prüfen Anlagen und Geräte in",
  liste=["Wohnhäusern", "Gewerbebetrieben", "Geschäftslokalen", "Gastronomieobjekten",
         "Landwirtschaftlichen Objekten", "Schulen und öffentlichen Objekten"],
  galerie=[("bild8-8","Verteilerschränke in einem Technikraum"),
           ("installation-wohnung-65","Wohnungsverteiler mit Prüfprotokoll"),
           ("bild10-10","Zählerverteiler im Hausanschlussraum")]),

"antennentechnik": dict(
  vorzeile="Von der Planung bis zur Montage",
  h1="Antennen- und Empfangstechnik",
  lead="Damit HD nicht nur ein Schlagwort bleibt, sorgen wir für optimale "
       "Datenausbeute — und damit für ein scharfes Bild und guten Ton.",
  body=[
    ("Die Montage entscheidet",
     ["Für optimale Ergebnisse ist nicht nur das Modell entscheidend, sondern vor allem "
      "die präzise, millimetergenaue Montage. Deshalb berät Sie unser Team zum optimalen "
      "Montageplatz und führt die Arbeiten anschließend zügig und genau aus.",
      "Wir liefern und installieren die gesamte Anlage bis zum finalen Knopfdruck auf "
      "der Fernbedienung."]),
  ],
  galerie=[("bild-12","Satellitenschüssel auf einem Ziegeldach"),
           ("multimedia-schrank-03","Multimediaverteiler mit Antennentechnik")]),
}


# ==========================================================================
# Wiederverwendbare Bloecke
# ==========================================================================

def teaser_raster(tiefe=0, nur=None):
    P = "../" * tiefe
    teile = []
    for l in LEISTUNGEN:
        if nur and l["slug"] not in nur:
            continue
        teile.append(
            '<a class="teaser" href="' + P + 'leistungen/' + l["slug"] + '.html">'
            '<div class="teaser__bild">' + img(l["bild"], l["alt"], sizes="(min-width:60rem) 22rem, 100vw") + '</div>'
            '<div class="teaser__text">'
            '<p class="label card__num">' + l["nr"] + '</p>'
            '<h3>' + l["titel"] + '</h3>'
            '<p class="small muted">' + l["kurz"] + '</p>'
            '<span class="teaser__mehr">Mehr dazu</span>'
            '</div></a>')
    return '<div class="grid-rule">' + "".join(teile) + '</div>'


def ablauf_block():
    schritte = [
        ("Sie melden sich",
         "Telefon, E-Mail oder Formular — alle drei landen beim selben Team. Schildern "
         "Sie kurz, worum es geht; ein Foto hilft oft mehr als eine lange Beschreibung."),
        ("Wir melden uns zurück",
         "Wir rufen zurück und klären, worum es genau geht. Bei kleinen Sachen lässt "
         "sich am Telefon schon sagen, ob sich ein Termin überhaupt lohnt."),
        ("Wir sehen es uns an",
         "Bei allem, was über eine einfache Reparatur hinausgeht, kommen wir vorbei und "
         "nehmen die Gegebenheiten auf — Hausanschluss, Verteilung, Leitungswege."),
        ("Sie bekommen ein Angebot",
         "Schriftlich und mit Positionen, damit Sie sehen, wofür Sie bezahlen."),
        ("Wir führen aus",
         "Von der Kundenbedarfserfassung über die Planung bis zur Ausführung — und auf "
         "Wunsch weiter in die dauerhafte Wartung."),
        ("Abnahme und Dokumentation",
         "Wir gehen die Arbeiten mit Ihnen durch und übergeben die Unterlagen — "
         "Prüfprotokolle, Schaltpläne, Messprotokolle, je nach Auftrag."),
    ]
    li = "".join('<li><h3>' + t + '</h3><p>' + b + '</p></li>' for t, b in schritte)
    return '<ol class="steps prose">' + li + '</ol>'


def galerie_block(eintraege, klasse="galerie"):
    """Jedes Bild ist ein Link auf die grosse Fassung — ohne JavaScript."""
    figs = "".join(
        '<figure><a href="{P}bilder/' + n + '.webp" target="_blank" rel="noopener"'
        ' aria-label="' + html.escape(a, quote=True) + ' — groesser anzeigen">' +
        img(n, a, sizes="(min-width:60rem) 20rem, 50vw") + '</a>'
        '<figcaption>' + html.escape(a) + '</figcaption></figure>'
        for n, a in eintraege)
    return '<div class="' + klasse + '">' + figs + '</div>'


def galerie_gruppen(gruppen):
    teile = []
    for titel, eintraege in gruppen:
        # Kein stilles Weglassen mehr: img() bricht ab, wenn ein Bild fehlt.
        teile.append('<div class="galerie-gruppe"><h3>' + titel + '</h3>' +
                     galerie_block(eintraege) + '</div>')
    return "".join(teile)


# ==========================================================================
# Seiten
# ==========================================================================

def seite_start():
    s = kopf("start",
             "Mat-Elektrotechnik GmbH — Elektrofachbetrieb in Germering bei München",
             "Elektroinstallation, Verteilerbau, Wallbox, Photovoltaik, Blitzschutz, "
             "Netzwerktechnik und Anlagenprüfung. Mat-Elektrotechnik GmbH, Germering "
             "bei München, seit 2010.",
             "index.html", 0, og_bild="og-start.jpg",
             krumenpfad=[("Start","")])
    s += """
<section class="hero">
  <div class="wrap hero__text">
    <p class="label">Elektrofachbetrieb · Germering bei München</p>
    <h1>Elektrotechnik für den Großraum München. Seit 2010.</h1>
    <p class="lead">Mat-Elektrotechnik ist Ihr Elektrofachbetrieb aus Germering. Von der
      einzelnen Steckdose bis zur Photovoltaik-Großanlage: Wir planen, bauen und warten
      Elektroanlagen — mit demselben Team, von Anfang bis Abnahme.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="kontakt.html">Anfrage senden</a>
      <a class="btn btn--secondary" href="tel:""" + TEL_ROH + """\">""" + TEL + """</a>
    </div>
  </div>
  <div class="hero__bild">""" + img("start3", "Blick durch eine Reihe von Schaltanlagen in einer Industriehalle", lazy=False) + """</div>
</section>

<section>
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Leistungen</p>
      <h2>Acht Bereiche, ein Team.</h2>
      <p class="lead">Sie brauchen für ein Projekt keine drei Firmen. Von der
        Kundenbedarfserfassung über die Planung bis zur Installation, Ausführung und
        dauerhaften Wartung.</p>
    </div>
    """ + teaser_raster(0) + """
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Woran Sie bei uns sind</p>
      <h2>Sie wissen, wie es sonst läuft.</h2>
    </div>
    <div class="prose stack-lg">
      <p>Sie rufen an und erreichen eine Mailbox. Jemand kommt, sieht sich die Sache an —
        und auf das Angebot warten Sie dann noch einmal drei Wochen. Am Ende steht auf
        der Rechnung mehr, als besprochen war.</p>
      <p>Elektroarbeiten sind kein Bereich, in dem man das hinnehmen sollte. Eine
        Verteilung, die vierzig Jahre alt ist, eine Wallbox an einer Leitung, die sie
        nicht trägt, ein Prüftermin, der seit Jahren überfällig ist — das sind keine
        Schönheitsfragen.</p>
      <div class="promise">
        <p><strong>Deshalb halten wir uns an das, was nachprüfbar ist:</strong></p>
        <ul>
          <li>Jeder Schaltschrank wird vor der Auslieferung nach den geltenden
            nationalen und internationalen Normen geprüft.</li>
          <li>Nach jeder Anlagenprüfung erhalten Sie ein elektrotechnisches
            Sicherheitsprotokoll.</li>
          <li>Planung, Ausführung und Wartung kommen aus demselben Betrieb — wir sind
            elektrotechnischer Komplettanbieter, kein Vermittler.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Ablauf</p>
      <h2>Wie eine Anfrage bei uns läuft.</h2>
    </div>
    """ + ablauf_block() + """
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Belege</p>
      <h2>Woran Sie uns messen können.</h2>
    </div>
    <div class="grid-rule">
      <div class="card">
        <h3>Markenpreis ELMAR 2023</h3>
        <p class="small">Am 7. Dezember 2023 wurde Mat-Elektrotechnik mit dem Markenpreis
          ELMAR in Kategorie 1 ausgezeichnet, vergeben von „Elektromarken. Starke
          Partner." Das Unternehmen setzte sich gegen Mitbewerber aus ganz Deutschland
          durch.</p>
      </div>
      <div class="card">
        <h3>Meisterbetrieb</h3>
        <p class="small">Geführt von Miodrag Manojlovic, Elektrotechnikermeister, der den
          Betrieb 2010 gegründet hat und bis heute selbst führt.</p>
      </div>
      <div class="card">
        <h3>Wir bilden selbst aus</h3>
        <p class="small">Zum Elektroniker für Energie- und Gebäudetechnik. In einem
          Handwerk, in dem Fachkräfte fehlen, ist das die einzige Art, Qualität
          langfristig zu sichern.</p>
      </div>
    </div>
    <figure class="bild-breit">""" + img("elmar-foto-2", "Preisverleihung des Markenpreises ELMAR 2023") + """
      <figcaption>Verleihung des Markenpreises ELMAR 2023 im Rahmen des Markenforums der
        Elektrobranche.</figcaption></figure>
  </div>
</section>
""" + cta_band(0) + fuss(0)
    return s


def seite_leistungen():
    s = kopf("leistungen",
             "Leistungen — Mat-Elektrotechnik GmbH, Germering",
             "Elektroinstallation, Verteilerbau, Ladeinfrastruktur, Photovoltaik, "
             "Blitzschutz, Netzwerktechnik, Prüfung und Antennentechnik.",
             "leistungen.html", 0, og_bild="og-leistungen.jpg",
             krumenpfad=[("Start",""),("Leistungen","leistungen.html")])
    s += krumen([("Start", "index.html"), ("Leistungen", None)], 0)
    s += """
<section class="hero">
  <div class="wrap hero__text">
    <p class="label">Unser Serviceportfolio</p>
    <h1>Was wir machen.</h1>
    <p class="lead">Die Firma Mat-Elektrotechnik mit Sitz in Germering bei München bietet
      Gebäude- und Elektrotechnik, Blitzschutz, Antennen- und Netzwerktechnik sowie
      Prüfungen — von der Planung über die Ausführung bis zum Service.</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <h2 class="label" style="margin-bottom:var(--s-06)">Unsere acht Bereiche</h2>
    """ + teaser_raster(0) + """
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Vielseitigkeit</p>
      <h2>Unser wichtigster Erfolgsfaktor.</h2>
      <p>Von der Kundenbedarfserfassung über die Planung und von der Installation bis zur
        Ausführung und dauerhaften Wartung. Unser Kundenkreis reicht von kleinen
        Privatwohnungen über große Hausverwaltungen bis zu Büros und vom Privathaus bis
        zur Produktionshalle.</p>
    </div>
    """ + ablauf_block() + """
  </div>
</section>
""" + cta_band(0) + fuss(0)
    return s


def seite_leistung(slug):
    l = L_NACH_SLUG[slug]
    c = INHALT[slug]
    s = kopf("leistungen",
             l["titel"] + " — Mat-Elektrotechnik GmbH, Germering bei München",
             c["lead"][:160],
             "leistungen/" + slug + ".html", 1,
             og_bild="og-" + slug + ".jpg",
             krumenpfad=[("Start", ""), ("Leistungen", "leistungen.html"),
                         (l["titel"], "leistungen/" + slug + ".html")])
    s += krumen([("Start", "index.html"), ("Leistungen", "leistungen.html"), (l["titel"], None)], 1)
    s += """
<section class="hero hero--klein">
  <div class="wrap hero__text">
    <p class="label">""" + c["vorzeile"] + """</p>
    <h1>""" + c["h1"] + """</h1>
    <p class="lead">""" + c["lead"] + """</p>
  </div>
  <div class="hero__bild">""" + img(l["bild"], l["alt"], lazy=False) + """</div>
</section>

<section>
  <div class="wrap">
    <div class="prose stack-lg">"""
    for titel, absaetze in c["body"]:
        s += '<div><h2 style="font-size:var(--t-h3);font-weight:600">' + titel + '</h2>'
        for a in absaetze:
            s += '<p style="margin-top:var(--s-05)">' + a + '</p>'
        s += '</div>'
    s += """</div>"""
    if c.get("liste"):
        s += """
    <div class="prose" style="margin-top:var(--s-10)">
      <h2 style="font-size:var(--t-h3);font-weight:600;margin-bottom:var(--s-05)">""" + c["liste_titel"] + """</h2>
      <ul class="liste">""" + "".join("<li>" + x + "</li>" for x in c["liste"]) + """</ul>
    </div>"""
    s += """
  </div>
</section>"""
    if c.get("galerie"):
        s += """
<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose"><p class="label">Aus unserer Arbeit</p>
      <h2 style="font-size:var(--t-h3);font-weight:600">Beispiele</h2></div>
    """ + galerie_block(c["galerie"]) + """
  </div>
</section>"""
    andere = [(x["titel"], "leistungen/" + x["slug"] + ".html") for x in LEISTUNGEN if x["slug"] != slug][:4]
    s += weiter_zu(andere + [("Alle Leistungen", "leistungen.html")], 1, "Weitere Leistungen")
    s += cta_band(1) + fuss(1)
    return s


def seite_unternehmen():
    s = kopf("unternehmen",
             "Der Betrieb — Mat-Elektrotechnik GmbH, Germering",
             "Mat-Elektrotechnik wurde 2010 von Miodrag Manojlovic gegründet. Heute "
             "arbeitet ein Team aus Monteuren, Projektleitung und Auszubildenden in "
             "Germering bei München.",
             "unternehmen.html", 0, og_bild="og-unternehmen.jpg",
             krumenpfad=[("Start",""),("Unternehmen","unternehmen.html")])
    s += krumen([("Start", "index.html"), ("Unternehmen", None)], 0)
    team = "".join(
        '<figure>' + img(d, n + ", " + r, sizes="(min-width:48rem) 12rem, 45vw") +
        '<figcaption><span class="name">' + n + '</span>'
        '<span class="rolle">' + r + '</span></figcaption></figure>'
        for d, n, r in TEAM if d in BILD)
    s += """
<section class="hero hero--klein">
  <div class="wrap hero__text">
    <p class="label">Über uns</p>
    <h1>Mat-Elektrotechnik. Wie alles begann.</h1>
    <p class="lead">Am Anfang war die Idee, gemixt mit Enthusiasmus und Energie. Deshalb
      entschloss sich Miodrag Manojlovic im Jahr 2010, seiner Vision eines eigenen
      Unternehmens zu folgen.</p>
  </div>
  <div class="hero__bild">""" + img("210515-334-final-k-2", "Das Team von Mat-Elektrotechnik vor dem Firmengebäude", lazy=False) + """</div>
</section>

<section>
  <div class="wrap">
    <div class="prose stack-lg">
      <p>Die Firma Mat-Elektrotechnik wurde 2010 von Herrn Miodrag Manojlovic gegründet.
        Nach kurzer Anlaufzeit begann das Unternehmen zu wachsen. Aus dem
        Einzelunternehmen wurde eine GmbH.</p>
      <p>Heute umfasst das Team neben Herrn Manojlovic, der als Geschäftsführer und
        Elektrotechnikermeister fungiert, top ausgebildete Elektroinstallateure,
        Elektrohelfer und Auszubildende sowie Rechnungswesen und Buchhaltung.</p>
      <p>Der Name steht für Manojlovic Anlagen Technik.</p>
      <p>Innovation ist genauso wie das Vertrauen auf traditionelle Werte ein wichtiger
        Eckpfeiler unserer Firmenphilosophie. Deshalb schulen und entwickeln wir unser
        Team ständig weiter. Zu unserem Kundenkreis zählen viele Gewerbekunden sowie
        unzählige Privatkunden.</p>
    </div>
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Know-how hat viele Gesichter</p>
      <h2>Ihre Ansprechpartner.</h2>
      <p>Wir sind nicht nur für unser Know-how und unsere Technologiekompetenz bekannt,
        sondern vor allem für persönliches Engagement, Flexibilität und Dynamik. Denken
        in Lösungen liegt uns im Blut.</p>
    </div>
    <div class="team">""" + team + """</div>
  </div>
</section>

<section>
  <div class="wrap">
    <figure class="bild-breit" style="margin-top:0">""" + img("facebook-04", "Firmenfahrzeug von Mat-Elektrotechnik") + """
      <figcaption>Unterwegs im Großraum München und in der angrenzenden Region.</figcaption>
    </figure>
  </div>
</section>
""" + weiter_zu([("Referenzen", "referenzen.html"), ("Karriere", "karriere.html"),
                 ("Leistungen", "leistungen.html")], 0)
    s += cta_band(0) + fuss(0)
    return s


def seite_referenzen():
    s = kopf("referenzen",
             "Referenzen — Mat-Elektrotechnik GmbH, Germering",
             "Projekte aus Elektroinstallation, Beleuchtung, Netzwerktechnik, "
             "Sprechanlagen und Photovoltaik im Großraum München.",
             "referenzen.html", 0, og_bild="og-referenzen.jpg",
             krumenpfad=[("Start",""),("Referenzen","referenzen.html")])
    s += krumen([("Start", "index.html"), ("Referenzen", None)], 0)
    stimmen = "".join(
        '<figure class="card" style="margin:0"><blockquote style="margin:0">'
        '<p>„' + t + '"</p></blockquote>'
        '<figcaption class="small muted" style="margin-top:var(--s-05)">' + n + '</figcaption></figure>'
        for n, t in STIMMEN)
    s += """
<section class="hero hero--klein">
  <div class="wrap hero__text">
    <p class="label">Referenzen</p>
    <h1>Zufriedene Kunden sind die beste Werbung.</h1>
    <p class="lead">Seit 2010 vertrauen Kunden aus dem Privat-, Gewerbe- und
      Industriebereich aus dem Großraum München auf unsere Service- und
      Leistungspalette — von der einfachen Reparatur bis zum Smart Home und von der
      Einzelinstallation bis zum elektrotechnischen Komplettservice.</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <h2 class="label" style="margin-bottom:var(--s-07)">Projekte nach Gewerken</h2>
    """ + galerie_gruppen(GALERIE_GRUPPEN) + """
    <p class="small muted" style="margin-top:var(--s-07)">Ein Klick auf ein Bild
      öffnet es in voller Größe.</p>
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose">
      <p class="label">Kundenmeinungen</p>
      <h2>Was Kunden über uns sagen.</h2>
    </div>
    <div class="grid-rule">""" + stimmen + """</div>
    <p class="small muted" style="margin-top:var(--s-06);max-width:var(--measure)">
      Die Zitate stammen von Kundinnen und Kunden der Mat-Elektrotechnik GmbH.</p>
  </div>
</section>
""" + cta_band(0) + fuss(0)
    return s


def seite_karriere():
    s = kopf("karriere",
             "Karriere — Mat-Elektrotechnik GmbH, Germering",
             "Elektroinstallateur, Projektleiter und Elektromeister sowie Ausbildung zum "
             "Elektroniker für Energie- und Gebäudetechnik in Germering bei München.",
             "karriere.html", 0, og_bild="og-karriere.jpg",
             krumenpfad=[("Start",""),("Karriere","karriere.html")])
    s += krumen([("Start", "index.html"), ("Karriere", None)], 0)
    stellen = [
        ("Elektroinstallateur (m/w/d)",
         "Sie bringen elektrotechnisches Know-how mit und mögen den persönlichen Kontakt "
         "mit Kunden. Sie arbeiten an Projekten rund um Elektroinstallationen, "
         "Antennentechnik und Blitzschutz."),
        ("Projektleiter / Elektromeister (m/w/d)",
         "Sie planen und verantworten Projekte von der Aufnahme bis zur Abnahme und "
         "führen ein Team auf der Baustelle."),
        ("Auszubildender zum Elektroniker für Energie- und Gebäudetechnik (m/w/d)",
         "Sie lernen das Handwerk von Grund auf — Installation, Verteilerbau, "
         "Netzwerktechnik und Prüfung, in einem Betrieb, der selbst ausbildet."),
    ]
    liste = "".join('<div class="card"><h3>' + t + '</h3><p class="small">' + b +
                    '</p></div>' for t, b in stellen)
    s += """
<section class="hero hero--klein">
  <div class="wrap hero__text">
    <p class="label">Karriere</p>
    <h1>Gemeinsam sind wir stark.</h1>
    <p class="lead">Jedes Unternehmen ist so erfolgreich wie die Menschen, die
      dahinterstehen. Deshalb suchen wir Mitstreiter, die mit uns weiterarbeiten
      wollen.</p>
  </div>
  <div class="hero__bild">""" + img("210515-377-final", "Das Team von Mat-Elektrotechnik vor den Firmenfahrzeugen", lazy=False) + """</div>
</section>

<section>
  <div class="wrap">
    <div class="prose stack-lg">
      <p>Wenn Sie elektrotechnisches Know-how mitbringen, aber auch den persönlichen
        Kontakt mit Kunden schätzen, dann sind Sie bei uns richtig. Sie sind flexibel,
        freundlich und wendig im Denken?</p>
      <p>Dann laden wir Sie ein, in einem Team mitzuarbeiten und vielfältige Projekte
        rund um Elektroinstallationen, Antennentechnik, Blitzschutz und mehr
        mitzugestalten. Dabei unterscheidet sich jedes Projekt vom anderen.</p>
    </div>
  </div>
</section>

<section class="flaeche">
  <div class="wrap">
    <div class="section-head prose"><p class="label">Offene Stellen</p>
      <h2>Wen wir suchen.</h2></div>
    <div class="grid-rule">""" + liste + """</div>
    <div class="prose" style="margin-top:var(--s-09)">
      <p>Wir freuen uns auf Ihre Bewerbung — per E-Mail an
        <a href="mailto:""" + MAIL + """">""" + MAIL + """</a> oder telefonisch unter
        <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a>.</p>
    </div>
  </div>
</section>
""" + cta_band(0) + fuss(0)
    return s


FORM_JS = """
<script>
(function(){"use strict";
var form=document.getElementById("anfrage"); if(!form) return;
var DRAFT="mat-anfrage-entwurf";
var okBox=document.getElementById("status-ok"), errBox=document.getElementById("status-err");
var fallback=document.getElementById("fallback");
var felder=["name","email","telefon","ort","thema","nachricht"];

function speichern(){try{var d={};felder.forEach(function(k){var el=document.getElementById(k);if(el)d[k]=el.value;});localStorage.setItem(DRAFT,JSON.stringify(d));}catch(e){}}
function laden(){try{var raw=localStorage.getItem(DRAFT);if(!raw)return;var d=JSON.parse(raw);Object.keys(d).forEach(function(k){var el=document.getElementById(k);if(el&&d[k])el.value=d[k];});}catch(e){}}
function verwerfen(){try{localStorage.removeItem(DRAFT);}catch(e){}}
laden(); form.addEventListener("input",speichern);

function markiere(id,ungueltig){var f=document.getElementById("f-"+id),e=document.getElementById(id);
  if(!f||!e)return; f.setAttribute("data-invalid",ungueltig?"true":"false");
  e.setAttribute("aria-invalid",ungueltig?"true":"false");}
function mailOk(v){return /^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(v.trim());}
function pruefe(){var fehler=[];
  var name=document.getElementById("name").value.trim();
  var mail=document.getElementById("email").value.trim();
  var text=document.getElementById("nachricht").value.trim();
  markiere("name",!name); if(!name)fehler.push("name");
  markiere("email",!mailOk(mail)); if(!mailOk(mail))fehler.push("email");
  markiere("nachricht",!text); if(!text)fehler.push("nachricht");
  return fehler;}
felder.forEach(function(id){var el=document.getElementById(id);
  if(el)el.addEventListener("blur",function(){if(el.getAttribute("aria-invalid")==="true")pruefe();});});

form.addEventListener("submit",function(ev){ev.preventDefault();
  if(document.getElementById("webseite").value!==""){okBox.hidden=false;return;}
  var fehler=pruefe();
  if(fehler.length){errBox.hidden=false;okBox.hidden=true;
    var erstes=document.getElementById(fehler[0]); if(erstes)erstes.focus(); return;}
  errBox.hidden=true;
  function v(id){var e=document.getElementById(id);return e?e.value.trim():"";}
  var text=["Anfrage über die Website","",
    "Name:      "+v("name"),"E-Mail:    "+v("email"),
    "Telefon:   "+(v("telefon")||"—"),"PLZ/Ort:   "+(v("ort")||"—"),
    "Thema:     "+(v("thema")||"—"),"","Anliegen:",v("nachricht")].join("\\n");
  var betreff="Anfrage: "+(v("thema")||"Elektrotechnik")+" — "+v("name");
  fallback.value=text; okBox.hidden=false; verwerfen();
  okBox.scrollIntoView({block:"nearest"});
  var mailto="mailto:MAILADRESSE?subject="+encodeURIComponent(betreff)+"&body="+encodeURIComponent(text);
  window.setTimeout(function(){window.location.href=mailto;},80);
});

var copy=document.getElementById("copy");
if(copy)copy.addEventListener("click",function(){fallback.select();var ok=false;
  try{ok=document.execCommand("copy");}catch(e){}
  if(navigator.clipboard&&!ok){navigator.clipboard.writeText(fallback.value).then(function(){copy.textContent="Kopiert";});return;}
  copy.textContent=ok?"Kopiert":"Bitte von Hand markieren";});
})();
</script>
""".replace("MAILADRESSE", MAIL)


def seite_kontakt():
    s = kopf("kontakt",
             "Kontakt — Mat-Elektrotechnik GmbH, Industriestraße 12, 82110 Germering",
             "Mat-Elektrotechnik GmbH, Industriestraße 12, 82110 Germering. "
             "Telefon 089 23750352, info@mat-elektrotechnik.de.",
             "kontakt.html", 0, og_bild="og-kontakt.jpg",
             krumenpfad=[("Start",""),("Kontakt","kontakt.html")])
    s += krumen([("Start", "index.html"), ("Kontakt", None)], 0)
    themen = ["Elektroinstallation", "Verteilerbau / Schaltschrank",
              "Wallbox / Ladeinfrastruktur", "Photovoltaik",
              "Blitz- und Überspannungsschutz", "Netzwerk / IT-Infrastruktur",
              "Prüfung und Wartung", "Antennen- und Empfangstechnik",
              "Reparatur / Störung", "Etwas anderes"]
    opts = "".join("<option>" + t + "</option>" for t in themen)
    s += """
<section class="on-dark">
  <div class="wrap">
    <div class="split">
      <div>
        <div class="section-head prose">
          <p class="label">Kontakt</p>
          <h1>Wir sind für Sie da.</h1>
        </div>
        <div class="prose stack-lg">
          <p>Falls Sie Fragen haben, können Sie das Formular verwenden, um Ihre Anfrage
            an uns zu stellen. Natürlich sind wir auch telefonisch von Montag bis Freitag
            für Sie erreichbar.</p>
          <ul class="direkt">
            <li><p class="label">Telefon</p>
              <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a></li>
            <li><p class="label">E-Mail</p>
              <a href="mailto:""" + MAIL + """">""" + MAIL + """</a></li>
            <li><p class="label">Vor Ort</p>
              <address style="font-style:normal">Mat-Elektrotechnik GmbH<br>
                Industriestraße 12<br>82110 Germering</address>
              <p class="small" style="margin-top:var(--s-04)">
                <a href="https://www.openstreetmap.org/search?query=Industriestra%C3%9Fe%2012%2C%2082110%20Germering"
                   rel="noopener">Adresse auf der Karte öffnen</a></p>
              <p class="small muted" style="margin-top:var(--s-03)">Der Link öffnet eine
                fremde Seite. Wir binden hier keine Karte ein, damit beim Besuch dieser
                Seite keine Daten an Kartenanbieter gehen.</p></li>
          </ul>
        </div>
      </div>

      <div class="form-panel">
        <h2 style="font-size:var(--t-h3);font-weight:600;margin-bottom:var(--s-06)">Ihre Anfrage</h2>
        <noscript><div class="noscript"><p><strong>Das Formular braucht JavaScript.</strong>
          Ohne JavaScript können wir Ihre Nachricht nicht übergeben. Bitte rufen Sie an
          unter <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a> oder schreiben Sie an
          <a href="mailto:""" + MAIL + """">""" + MAIL + """</a>.</p></div></noscript>

        <form id="anfrage" novalidate>
          <div class="hp" aria-hidden="true">
            <label for="webseite">Webseite (bitte frei lassen)</label>
            <input type="text" id="webseite" name="webseite" tabindex="-1" autocomplete="off">
          </div>
          <div class="field" id="f-name">
            <label for="name">Name <span class="req" aria-hidden="true">*</span></label>
            <input type="text" id="name" name="name" autocomplete="name" required aria-required="true" aria-describedby="e-name">
            <span class="err" id="e-name" role="alert">Bitte tragen Sie Ihren Namen ein.</span>
          </div>
          <div class="field" id="f-email">
            <label for="email">E-Mail <span class="req" aria-hidden="true">*</span></label>
            <input type="email" id="email" name="email" autocomplete="email" required aria-required="true" aria-describedby="e-email">
            <span class="err" id="e-email" role="alert">Bitte tragen Sie eine gültige E-Mail-Adresse ein, zum Beispiel name@beispiel.de</span>
          </div>
          <div class="field" id="f-tel">
            <label for="telefon">Telefon</label>
            <input type="tel" id="telefon" name="telefon" autocomplete="tel" aria-describedby="h-tel">
            <span class="hint" id="h-tel">Freiwillig. Beschleunigt die Rückmeldung bei Rückfragen.</span>
          </div>
          <div class="field" id="f-ort">
            <label for="ort">PLZ und Ort</label>
            <input type="text" id="ort" name="ort" autocomplete="postal-code" aria-describedby="h-ort">
            <span class="hint" id="h-ort">Damit wir gleich sagen können, ob der Ort in unserem Einzugsgebiet liegt.</span>
          </div>
          <div class="field" id="f-thema">
            <label for="thema">Worum geht es?</label>
            <select id="thema" name="thema"><option value="">Bitte wählen</option>""" + opts + """</select>
          </div>
          <div class="field" id="f-nachricht">
            <label for="nachricht">Ihr Anliegen <span class="req" aria-hidden="true">*</span></label>
            <textarea id="nachricht" name="nachricht" required aria-required="true" aria-describedby="e-nachricht h-nachricht"></textarea>
            <span class="hint" id="h-nachricht">Je konkreter, desto schneller können wir einschätzen, was nötig ist.</span>
            <span class="err" id="e-nachricht" role="alert">Bitte beschreiben Sie kurz Ihr Anliegen.</span>
          </div>
          <p class="small muted" style="margin:var(--s-06) 0">Mit dem Absenden öffnet sich Ihr
            E-Mail-Programm mit der fertigen Nachricht. Die Daten werden dabei
            <strong>nicht an diese Website übertragen</strong> und hier nicht gespeichert.
            Näheres in der <a href="datenschutz.html">Datenschutzerklärung</a>.</p>
          <button class="btn btn--primary" type="submit" style="width:100%">Anfrage senden</button>
        </form>

        <div class="status status--ok" id="status-ok" role="status" aria-live="polite" hidden>
          <h3>&#10003; Ihre Nachricht ist fertig</h3>
          <p>Ihr E-Mail-Programm sollte sich geöffnet haben. <strong>Bitte senden Sie die
            Mail dort noch ab</strong> — erst dann erreicht sie uns.</p>
          <p>Falls sich nichts geöffnet hat, kopieren Sie den Text und schicken ihn an
            <a href="mailto:""" + MAIL + """">""" + MAIL + """</a> — oder rufen Sie an:
            <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a>.</p>
          <label class="label" for="fallback">Ihre Nachricht zum Kopieren</label>
          <textarea id="fallback" readonly rows="10"></textarea>
          <div class="btn-row">
            <button class="btn btn--secondary" type="button" id="copy">Text kopieren</button>
            <a class="btn btn--secondary" href="tel:""" + TEL_ROH + """">Stattdessen anrufen</a>
          </div>
        </div>
        <div class="status status--warn" id="status-err" role="alert" aria-live="assertive" hidden>
          <h3>Bitte prüfen Sie Ihre Eingaben</h3>
          <p>Einige Pflichtfelder sind noch nicht ausgefüllt. Die betroffenen Felder sind
            rot markiert und beschriftet.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head prose"><p class="label">Häufige Fragen</p>
      <h2>Was Kunden uns vorher fragen.</h2></div>
    <div class="faq">
      <details><summary>Kommen Sie auch zu mir?</summary><div class="answer">
        <p>Wir arbeiten im Großraum München und in der angrenzenden Region. Rufen Sie
          kurz an — dann sagen wir Ihnen sofort, ob Ihr Ort dabei ist.</p></div></details>
      <details><summary>Machen Sie auch kleine Aufträge?</summary><div class="answer">
        <p>Ja. Eine einzelne Steckdose, ein defekter Schalter, eine Lampe, die hängen
          soll — das gehört genauso dazu wie der Hallenumbau.</p></div></details>
      <details><summary>Arbeiten Sie für Privat- oder für Gewerbekunden?</summary><div class="answer">
        <p>Für beide. Unser Kundenkreis reicht von kleinen Privatwohnungen über große
          Hausverwaltungen bis zu Büros und vom Privathaus bis zur
          Produktionshalle.</p></div></details>
      <details><summary>Ich will eine Wallbox. Was muss ich wissen?</summary><div class="answer">
        <p>Zuerst muss geklärt werden, ob Ihre vorhandene Installation und Ihr
          Hausanschluss die zusätzliche Last tragen. Das prüfen wir vor der Montage und
          sagen Ihnen vorher, was gegebenenfalls nachgerüstet werden muss.</p></div></details>
      <details><summary>Bauen Sie auch Photovoltaik auf Einfamilienhäusern?</summary><div class="answer">
        <p>Ja, auch wenn unser Schwerpunkt bei größeren Anlagen für Gewerbe und
          Industrie liegt.</p></div></details>
      <details><summary>Bilden Sie aus?</summary><div class="answer">
        <p>Ja, zum Elektroniker für Energie- und Gebäudetechnik. Mehr dazu auf der
          <a href="karriere.html">Karriereseite</a>.</p></div></details>
    </div>
  </div>
</section>
""" + fuss(0, FORM_JS)
    return s


def seite_impressum():
    s = kopf("", "Impressum — Mat-Elektrotechnik GmbH",
             "Impressum der Mat-Elektrotechnik GmbH, Industriestraße 12, 82110 Germering.",
             "impressum.html", 0)
    s += krumen([("Start", "index.html"), ("Impressum", None)], 0)
    s += """
<section>
  <div class="wrap recht">
    <p class="label">Rechtliches</p>
    <h1 style="font-size:var(--t-h2);margin-top:var(--s-05)">Impressum</h1>

    <h2>Angaben gemäß § 5 DDG</h2>
    <dl>
      <dt>Anbieter</dt>
      <dd>Mat-Elektrotechnik GmbH<br>Industriestraße 12<br>82110 Germering<br>Deutschland</dd>
      <dt>Vertreten durch</dt>
      <dd>Miodrag Manojlovic, Geschäftsführer</dd>
      <dt>Kontakt</dt>
      <dd>Telefon: <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a><br>
          E-Mail: <a href="mailto:""" + MAIL + """">""" + MAIL + """</a></dd>
      <dt>Registereintrag</dt>
      <dd>Handelsregister des Amtsgerichts München, HRB 246899</dd>
      <dt>Umsatzsteuer-Identifikationsnummer gemäß § 27a UStG</dt>
      <dd>DE 323 580 611</dd>
      <dt>Unternehmensgegenstand</dt>
      <dd>Elektroinstallationen, insbesondere Planung, Beratung, Blitzschutz, Geräte- und
          Anlagenprüfung, Netzwerk-, Antennen- und Sprechanlagentechnik</dd>
    </dl>

    <h2>Angaben zur Berufsausübung</h2>
    <dl>
      <dt>Gesetzliche Berufsbezeichnung</dt>
      <dd>Elektrotechnikermeister</dd>
      <dt>Verliehen in</dt>
      <dd>Bundesrepublik Deutschland</dd>
      <dt>Zuständige Kammer</dt>
      <dd>Handwerkskammer für München und Oberbayern<br>
          Max-Joseph-Straße 4, 80333 München<br>
          <a href="https://www.hwk-muenchen.de" rel="noopener">www.hwk-muenchen.de</a></dd>
      <dt>Berufsrechtliche Regelungen</dt>
      <dd>Gesetz zur Ordnung des Handwerks (Handwerksordnung, HwO), einsehbar unter
          <a href="https://www.gesetze-im-internet.de/hwo/" rel="noopener">gesetze-im-internet.de/hwo</a></dd>
    </dl>

    <h2>Verbraucherstreitbeilegung</h2>
    <p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor
      einer Verbraucherschlichtungsstelle teilzunehmen.</p>

    <h2>Haftung für Inhalte</h2>
    <p>Die Inhalte dieser Seiten wurden mit größter Sorgfalt erstellt. Für die
      Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine
      Gewähr übernehmen. Als Diensteanbieter sind wir für eigene Inhalte auf diesen
      Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind als Diensteanbieter
      jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu
      überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit
      hinweisen.</p>
    <p>Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach
      den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist
      jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich.
      Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte
      umgehend entfernen.</p>

    <h2>Haftung für Links</h2>
    <p>Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir
      keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine
      Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige
      Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum
      Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Bei Bekanntwerden
      von Rechtsverletzungen werden wir derartige Links umgehend entfernen.</p>

    <h2>Urheberrecht</h2>
    <p>Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten
      unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung,
      Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes
      bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
      Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen
      Gebrauch gestattet. Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt
      wurden, werden die Urheberrechte Dritter beachtet.</p>
  </div>
</section>
""" + fuss(0)
    return s


def seite_datenschutz():
    s = kopf("", "Datenschutzerklärung — Mat-Elektrotechnik GmbH",
             "Wie diese Website mit personenbezogenen Daten umgeht: keine Cookies, keine "
             "Analysedienste, keine externen Einbindungen.",
             "datenschutz.html", 0)
    s += krumen([("Start", "index.html"), ("Datenschutz", None)], 0)
    s += """
<section>
  <div class="wrap recht">
    <p class="label">Rechtliches</p>
    <h1 style="font-size:var(--t-h2);margin-top:var(--s-05)">Datenschutzerklärung</h1>

    <p class="lead" style="margin-top:var(--s-06)">Diese Website kommt ohne Cookies,
      ohne Analysedienste und ohne Einbindungen von Drittanbietern aus. Deshalb gibt es
      hier auch kein Einwilligungsbanner.</p>

    <h2>1. Verantwortlicher</h2>
    <p>Mat-Elektrotechnik GmbH<br>Industriestraße 12, 82110 Germering<br>
      Vertreten durch Miodrag Manojlovic<br>
      Telefon: <a href="tel:""" + TEL_ROH + """">""" + TEL + """</a><br>
      E-Mail: <a href="mailto:""" + MAIL + """">""" + MAIL + """</a></p>

    <h2>2. Was diese Website NICHT tut</h2>
    <p>Wir halten das für die wichtigste Auskunft, deshalb steht sie am Anfang:</p>
    <ul>
      <li>Es werden <strong>keine Cookies</strong> gesetzt.</li>
      <li>Es findet <strong>keine Webanalyse</strong> statt — kein Google Analytics, kein
        Tag Manager, kein Zählpixel.</li>
      <li>Es werden <strong>keine Inhalte von fremden Servern nachgeladen</strong>. Die
        Schriftarten liegen auf demselben Server wie die Website; es findet keine
        Verbindung zu Google Fonts oder einem anderen Dienst statt.</li>
      <li>Es sind <strong>keine Karten, Videos oder Social-Media-Schaltflächen</strong>
        eingebettet.</li>
      <li>Es findet <strong>kein Profiling</strong> und keine automatisierte
        Entscheidungsfindung statt.</li>
    </ul>

    <h2>3. Hosting und Server-Protokolldateien</h2>
    <p>Diese Website wird bei GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco,
      CA 94107, USA gehostet (GitHub Pages). Beim Abruf der Website verarbeitet der
      Hoster technisch notwendige Zugriffsdaten, insbesondere die IP-Adresse des
      aufrufenden Geräts, Datum und Uhrzeit des Zugriffs, die abgerufene Datei sowie die
      übermittelte Browserkennung.</p>
    <p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Unser berechtigtes Interesse
      liegt in der technisch fehlerfreien Bereitstellung und der Sicherheit der Website.
      Die Verarbeitung erfolgt auch in den USA. GitHub stützt die Übermittlung auf die
      Standardvertragsklauseln der EU-Kommission. Einzelheiten finden Sie in der
      Datenschutzerklärung von GitHub unter
      <a href="https://docs.github.com/privacy" rel="noopener">docs.github.com/privacy</a>.</p>

    <h2>4. Kontaktformular</h2>
    <p>Das Kontaktformular auf dieser Website überträgt <strong>keine Daten an unseren
      Server</strong>. Wenn Sie auf „Anfrage senden" klicken, setzt Ihr Browser aus Ihren
      Eingaben eine E-Mail zusammen und öffnet damit Ihr E-Mail-Programm. Erst wenn Sie
      die Nachricht dort selbst absenden, erreicht sie uns — auf demselben Weg wie eine
      E-Mail, die Sie von Hand schreiben würden.</p>
    <p>Die so an uns gesendete E-Mail verarbeiten wir ausschließlich, um Ihre Anfrage zu
      bearbeiten. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, soweit die Anfrage auf
      einen Vertrag abzielt, sonst Art. 6 Abs. 1 lit. f DSGVO. Wir löschen die Anfragen,
      sobald sie erledigt sind und keine gesetzlichen Aufbewahrungsfristen
      entgegenstehen.</p>
    <p>Unser E-Mail-Postfach wird über Microsoft 365 betrieben (Microsoft Ireland
      Operations Ltd.). Microsoft verarbeitet die eingehenden Nachrichten als
      Auftragsverarbeiter für uns.</p>

    <h2>5. Zwischenspeicherung Ihrer Eingaben im Browser</h2>
    <p>Während Sie das Kontaktformular ausfüllen, speichert die Website Ihre Eingaben im
      lokalen Speicher Ihres Browsers (<em>localStorage</em>), damit nichts verloren
      geht, falls die Seite versehentlich geschlossen wird. Diese Daten verlassen Ihr
      Gerät nicht und sind für uns nicht einsehbar. Sie werden gelöscht, sobald Sie die
      Anfrage abschicken, und können jederzeit über die Einstellungen Ihres Browsers
      entfernt werden.</p>
    <p>Es handelt sich um eine Funktion, die Sie durch das Ausfüllen des Formulars selbst
      auslösen; die Speicherung ist für diesen von Ihnen gewünschten Dienst unbedingt
      erforderlich im Sinne des § 25 Abs. 2 Nr. 2 TDDDG.</p>

    <h2>6. Ihre Rechte</h2>
    <p>Sie haben uns gegenüber das Recht auf Auskunft über die zu Ihrer Person
      gespeicherten Daten (Art. 15 DSGVO), auf Berichtigung (Art. 16 DSGVO), auf Löschung
      (Art. 17 DSGVO), auf Einschränkung der Verarbeitung (Art. 18 DSGVO) und auf
      Datenübertragbarkeit (Art. 20 DSGVO).</p>
    <p>Soweit wir eine Verarbeitung auf ein berechtigtes Interesse stützen, haben Sie das
      Recht, dieser Verarbeitung aus Gründen, die sich aus Ihrer besonderen Situation
      ergeben, zu widersprechen (Art. 21 DSGVO).</p>
    <p>Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu
      beschweren (Art. 77 DSGVO). Für uns zuständig ist das Bayerische Landesamt für
      Datenschutzaufsicht, Promenade 18, 91522 Ansbach.</p>

    <h2>7. Änderungen dieser Erklärung</h2>
    <p>Wir passen diese Datenschutzerklärung an, sobald sich die Funktionen der Website
      ändern. Es gilt jeweils die hier abrufbare Fassung.</p>
  </div>
</section>
""" + fuss(0)
    return s



def seite_404():
    """GitHub Pages liefert diese Datei bei jeder unbekannten Adresse aus.
    Absolute Pfade, weil die Seite auch unter /leistungen/xyz erscheinen kann."""
    s = kopf("", "Seite nicht gefunden — Mat-Elektrotechnik GmbH",
             "Diese Seite gibt es nicht. Hier geht es zurück zur Startseite.",
             "404.html", 0)
    s = s.replace('href="index.html"', 'href="/index.html"')
    s = s.replace('href="leistungen.html"', 'href="/leistungen.html"')
    s = s.replace('href="unternehmen.html"', 'href="/unternehmen.html"')
    s = s.replace('href="referenzen.html"', 'href="/referenzen.html"')
    s = s.replace('href="karriere.html"', 'href="/karriere.html"')
    s = s.replace('href="kontakt.html"', 'href="/kontakt.html"')
    s = s.replace('src="bilder/', 'src="/bilder/')
    s = s.replace('href="bilder/', 'href="/bilder/')
    s = s.replace('href="fonts/', 'href="/fonts/')
    s = s.replace('href="stil.css"', 'href="/stil.css"')
    s += """
<section class="fehler">
  <div class="wrap prose">
    <p class="nr">404</p>
    <h1 style="font-size:var(--t-h2);margin-top:var(--s-05)">Diese Seite gibt es nicht.</h1>
    <p class="lead" style="margin-top:var(--s-06)">Vielleicht hat sich ein Tippfehler in
      die Adresse geschlichen, oder die Seite ist umgezogen. Wenn Sie etwas Bestimmtes
      suchen, rufen Sie uns einfach an — das geht meistens schneller.</p>
    <ul>
      <li><a href="/index.html">Zur Startseite</a></li>
      <li><a href="/leistungen.html">Alle Leistungen</a></li>
      <li><a href="/kontakt.html">Kontakt</a></li>
      <li><a href="tel:""" + TEL_ROH + """">""" + TEL + """</a></li>
    </ul>
  </div>
</section>
""" + fuss(0).replace('href="index.html"','href="/index.html"') \
              .replace('href="leistungen','href="/leistungen') \
              .replace('href="unternehmen.html"','href="/unternehmen.html"') \
              .replace('href="referenzen.html"','href="/referenzen.html"') \
              .replace('href="karriere.html"','href="/karriere.html"') \
              .replace('href="kontakt.html"','href="/kontakt.html"') \
              .replace('href="impressum.html"','href="/impressum.html"') \
              .replace('href="datenschutz.html"','href="/datenschutz.html"') \
              .replace('src="bilder/','src="/bilder/')
    return s


# ==========================================================================
# Lauf
# ==========================================================================

def main():
    erzeugt = []
    erzeugt.append(("index.html", schreibe("index.html", seite_start())))
    erzeugt.append(("leistungen.html", schreibe("leistungen.html", seite_leistungen())))
    for l in LEISTUNGEN:
        p = "leistungen/" + l["slug"] + ".html"
        erzeugt.append((p, schreibe(p, seite_leistung(l["slug"]))))
    erzeugt.append(("unternehmen.html", schreibe("unternehmen.html", seite_unternehmen())))
    erzeugt.append(("referenzen.html", schreibe("referenzen.html", seite_referenzen())))
    erzeugt.append(("karriere.html", schreibe("karriere.html", seite_karriere())))
    erzeugt.append(("kontakt.html", schreibe("kontakt.html", seite_kontakt())))
    erzeugt.append(("impressum.html", schreibe("impressum.html", seite_impressum())))
    erzeugt.append(("datenschutz.html", schreibe("datenschutz.html", seite_datenschutz())))
    erzeugt.append(("404.html", schreibe("404.html", seite_404())))

    for p, n in erzeugt:
        print(f"{n:>8} B  {p}")
    print(f"\n{len(erzeugt)} Seiten erzeugt.")


if __name__ == "__main__":
    main()
