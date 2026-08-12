# Mapa del eclipse v2 — fondo claro, sombreado y nubes

## Orden de trabajo (5 minutos)

```bash
# 1. Deja los tres archivos en una carpeta y entra en ella
cd eclipse-v2

# 2. Trae las nubes reales (ECMWF). Las empotra dentro de index.html
python3 build_nubes.py

# 3. Despliega
npx vercel --prod
```

En el paso 2, si la carpeta está vacía de `datos.json` el script avisa. Necesita
los tres archivos juntos, aunque para desplegar solo hace falta `index.html`.

**Vuelve a ejecutar `build_nubes.py` sobre las 18:00** y redespliega: la previsión
a dos horas vista es mucho mejor que la de ahora.

## Qué cambia respecto a v1

| | v1 | v2 |
|---|---|---|
| Fondo | negro | papel claro |
| Franja | blanca (brillo) | sombra oscura sobre tierra clara |
| Nubes | no | capa ECMWF, activable |
| Etiquetas | no | nombres de provincia a partir de zoom 6 |
| Tiempo | Resumen / Directo | botón play que reproduce el paso de la sombra |

El sombreado está calibrado para que la franja de totalidad destaque sin oscurecer
media España: por debajo del 90 % de ocultación el mapa apenas se tiñe, y la
totalidad es casi negra con la intensidad graduada por la duración, de modo que
la línea central se distingue.

## Sobre los datos de nubes

`build_nubes.py` construye una malla de 279 puntos sobre tierra (~50 km) y pide a
Open-Meteo la cobertura nubosa total del modelo **ECMWF IFS** para las 20:00 CEST.
Sin clave de API, sin instalar nada, una sola petición.

Opciones:

```bash
python3 build_nubes.py --hora 21        # otra hora peninsular
python3 build_nubes.py --modelo best    # el mejor modelo disponible por zona
```

`--modelo best` usa modelos de alta resolución donde los hay, que a pocas horas
vista suelen ser mejores que el global. Merece la pena probar los dos y comparar.

**Atribución obligatoria.** Los datos de Open-Meteo son CC BY 4.0. El pie del mapa
la incluye automáticamente en cuanto hay nubes cargadas, con la hora de
actualización. No la quites.

## Verificación antes de publicar

- El mapa carga con fondo claro y la franja oscura cruzando el norte.
- Buscas **Oviedo** → Totalidad · 1 min 50 s.
- El botón **play** reproduce la sombra de Asturias a Baleares.
- El interruptor **Nubes previstas** está activo (si sale gris, `build_nubes.py` no
  llegó a empotrar nada).
- En la ficha de un municipio aparece la fila «Nubes previstas».

## Pendiente y deliberadamente fuera

- **Capa de relieve.** elDiario calcula con un modelo de elevaciones dónde las
  montañas tapan el Sol. Es la mejor idea de su mapa y no es replicable en unas
  horas: necesita el DEM de Copernicus y un cálculo de sombras. Queda para 2027,
  que hay otro eclipse.
- **Enlace al directo.** Sigue faltando. Es la pieza que convierte tráfico en
  navegación; ponla antes de publicar.
