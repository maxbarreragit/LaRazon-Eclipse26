# Mapa del eclipse — 12 agosto 2026

Mapa interactivo estático. Sin backend, sin build, sin dependencias externas en runtime
(Leaflet va vendorizado; solo Google Fonts se carga de fuera).

## Desplegar

```bash
cd eclipse-mapa
npx vercel --prod
```

Cuando pregunte el framework: **Other**. Output directory: **.** (la raíz).
No hay build step.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Todo el mapa (HTML + CSS + JS, 25 KB) |
| `datos.json` | 8.184 municipios, formato columnar (650 KB → ~200 KB gzip) |
| `leaflet.js` / `leaflet.css` / `images/` | Leaflet 1.9.4 vendorizado |
| `vercel.json` | Cache headers |
| `build_data.py` | Regenera `datos.json` desde `eclipse_municipios.json` |

## Qué hace

- **Resumen**: franja de totalidad. El brillo del blanco codifica la duración
  de la totalidad → la línea central se ve.
- **Directo**: la umbra cruzando España en tiempo real. Si abres la página
  entre las 19:00 y las 21:36 del 12/08 arranca sola en modo directo y va
  al segundo. El slider permite rebobinar.
- **Buscador** de municipio (sin acentos, teclado ↑↓/Enter) y **geolocalización**.
- **Ficha**: veredicto, C1, C2–C3, C4, altura del Sol, ocaso, aviso de horizonte
  y aviso de seguridad ISO 12312-2.

## El modelo de interpolación

Las horas de contacto (C1–C4) y la magnitud máxima vienen del cálculo exacto
(JPL DE421 + ERFA). Para pintar los instantes intermedios el cliente interpola
la separación angular con el modelo estándar de aproximación:

```
sep(t)² = sep_min² + (v·Δt)²
```

con `v` distinta en la rama de entrada y la de salida (el eclipse es asimétrico
porque el Sol está bajando). Validado contra el dataset exacto:
**error medio en la duración de la totalidad: 3,1 s; p95: 5,5 s** sobre
duraciones de 25–111 s. La bandera `v` del dataset sigue siendo la autoridad
sobre si un municipio está o no en totalidad; el modelo solo interpola.

`K = rm/rs = 1,03344` (desviación típica 0,0006 en toda España — constante).

## Regenerar datos

```bash
python3 build_data.py   # lee eclipse_municipios.json, escribe datos.json
```

## Créditos obligatorios (ya están en el pie del mapa)

Efemérides JPL DE421 (NASA/JPL, dominio público) · IAU SOFA/ERFA ·
Cartografía municipal es-atlas (INE/IGN), licencia ISC.
