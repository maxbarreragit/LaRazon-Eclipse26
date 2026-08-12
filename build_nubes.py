#!/usr/bin/env python3
"""
Descarga la nubosidad prevista para la hora del eclipse y la empotra en index.html.

Fuente: Open-Meteo (https://open-meteo.com), modelo ECMWF IFS.
Licencia de los datos: CC BY 4.0 -> hay que citar la fuente (ya va en el pie del mapa).

Uso:
    python3 build_nubes.py                 # hora del eclipse (20:30 CEST)
    python3 build_nubes.py --hora 20       # otra hora peninsular
    python3 build_nubes.py --modelo best   # mejor modelo disponible en vez de ECMWF

Vuelve a ejecutarlo cada pocas horas: cuanto mas cerca del eclipse, mejor la prevision.
No necesita clave de API ni instalar nada (solo la libreria estandar de Python).
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "datos.json")
HTML = os.path.join(AQUI, "index.html")

PASO = 0.55          # resolucion de la malla en grados (~50 km)
FECHA = "2026-08-12"


def malla(municipios):
    """Puntos de malla sobre tierra: solo donde hay municipios cerca."""
    pts = [(la, lo) for la, lo in municipios]
    out = []
    cajas = [(35.8, 44.0, -9.6, 4.6), (27.5, 29.6, -18.4, -13.2)]  # peninsula+baleares, canarias
    for lat0, lat1, lon0, lon1 in cajas:
        la = lat0
        while la <= lat1:
            lo = lon0
            while lo <= lon1:
                if any(abs(p[0] - la) < 0.42 and abs(p[1] - lo) < 0.52 for p in pts):
                    out.append((round(la, 2), round(lo, 2)))
                lo += PASO
            la += PASO
    return out


def descargar(pts, hora, modelo):
    base = ("https://api.open-meteo.com/v1/ecmwf" if modelo == "ecmwf"
            else "https://api.open-meteo.com/v1/forecast")
    q = {
        "latitude": ",".join(str(p[0]) for p in pts),
        "longitude": ",".join(str(p[1]) for p in pts),
        "hourly": "cloud_cover",
        "start_hour": f"{FECHA}T{hora:02d}:00",
        "end_hour": f"{FECHA}T{hora:02d}:00",
        "timezone": "Europe/Madrid",
    }
    url = base + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"User-Agent": "larazon-eclipse/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hora", type=int, default=20, help="hora peninsular (por defecto 20)")
    ap.add_argument("--modelo", default="ecmwf", choices=["ecmwf", "best"])
    a = ap.parse_args()

    if not os.path.exists(DATOS):
        sys.exit(f"No encuentro {DATOS}. Ejecuta el script en la carpeta del mapa.")

    d = json.load(open(DATOS))
    muni = list(zip([x / 1e4 for x in d["lat"]], [x / 1e4 for x in d["lon"]]))
    pts = malla(muni)
    print(f"Malla de {len(pts)} puntos. Descargando nubosidad ({a.modelo.upper()})...")

    res = descargar(pts, a.hora, a.modelo)
    if isinstance(res, dict):
        res = [res]
    if len(res) != len(pts):
        print(f"  aviso: la API devolvio {len(res)} puntos de {len(pts)}")

    lat, lon, cob = [], [], []
    for p, r in zip(pts, res):
        try:
            v = r["hourly"]["cloud_cover"][0]
        except (KeyError, IndexError, TypeError):
            continue
        if v is None:
            continue
        lat.append(p[0])
        lon.append(p[1])
        cob.append(int(round(v)))

    if not cob:
        sys.exit("La API no ha devuelto datos de nubosidad. Revisa la conexion.")

    nubes = {
        "lat": lat,
        "lon": lon,
        "c": cob,
        "gen": datetime.now().strftime("%d/%m %H:%M"),
        "hora": f"{a.hora:02d}:00",
        "modelo": a.modelo.upper(),
    }
    json.dump(nubes, open(os.path.join(AQUI, "nubes.json"), "w"), separators=(",", ":"))

    media = sum(cob) / len(cob)
    claros = sum(1 for c in cob if c < 25)
    print(f"OK  {len(cob)} puntos | nubosidad media {media:.0f} %"
          f" | {claros} puntos por debajo del 25 %")

    # Empotrar en el HTML para que siga siendo un unico archivo desplegable
    if os.path.exists(HTML):
        h = open(HTML, encoding="utf-8").read()
        nuevo = "<script>var NUBES=" + json.dumps(nubes, separators=(",", ":")) + ";</script>"
        h2, n = re.subn(r"<script>var NUBES=.*?;</script>", nuevo, h, count=1, flags=re.S)
        if n:
            open(HTML, "w", encoding="utf-8").write(h2)
            print(f"index.html actualizado ({len(h2)/1024:.0f} KB). Ya puedes desplegar.")
        else:
            print("No he encontrado el hueco de NUBES en index.html; queda nubes.json aparte.")
    else:
        print("No hay index.html en esta carpeta; queda nubes.json aparte.")


if __name__ == "__main__":
    main()
