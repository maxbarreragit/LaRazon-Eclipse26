"""Compacta eclipse_municipios.json en un payload columnar para el mapa."""
import json, unicodedata

SRC = "/mnt/user-data/uploads/eclipse_municipios.json"
DST = "/home/claude/eclipse/public/datos.json"

d = json.load(open(SRC))
d.sort(key=lambda x: (x["p"], x["n"]))

provs = sorted({x["p"] for x in d})
pidx = {p: i for i, p in enumerate(provs)}

VER = {"total": 0, "parcial_extrema": 1, "parcial": 2}


def secs(t):
    """HH:MM:SS local -> segundos desde 19:00 local (int)."""
    if not t:
        return -1
    h, m, s = (int(v) for v in t.split(":"))
    return h * 3600 + m * 60 + s - 19 * 3600


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


cols = {
    "prov": provs,
    # nombres separados por | para minimizar overhead JSON
    "n": "|".join(x["n"] for x in d),
    "p": [pidx[x["p"]] for x in d],
    "lat": [round(x["lat"] * 1e4) for x in d],
    "lon": [round(x["lon"] * 1e4) for x in d],
    "c1": [secs(x["c1"]) for x in d],
    "mx": [secs(x["max"]) for x in d],
    "c4": [secs(x["c4"]) for x in d],
    "c2": [secs(x["c2"]) for x in d],
    "c3": [secs(x["c3"]) for x in d],
    "os": [secs(x["ocaso"]) for x in d],             # ocaso
    "d": [round(x["dur"] * 10) for x in d],          # duracion totalidad, decimas de s
    "o": [round(x["obsc_vis"] * 100) for x in d],    # % ocultacion visible x100
    "a": [round(x["alt"] * 10) for x in d],          # altura del Sol x10
    "m": [round(x["mag"] * 1e4) for x in d],         # magnitud x10000
    "tz": [x["tz"] for x in d],
    "v": [VER[x["v"]] for x in d],
}

json.dump(cols, open(DST, "w"), ensure_ascii=False, separators=(",", ":"))

import os
print("municipios:", len(d))
print("provincias:", len(provs))
print("tamano:", round(os.path.getsize(DST) / 1024), "KB")
