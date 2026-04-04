# Reference Copies

These are the original complex component implementations saved here for reference.

Use them to copy specific logic (SVG gauges, ECharts charts, computed formulas)
back into the clean base components when implementing each module manually.

## Contents

| File | What it contains |
|---|---|
| `App.vue` | Original 3-column layout before router was added |
| `layout/TopBar.vue` | Full TopBar with live clock, highload toggle, CSV export |
| `cabin/HealthIndexCard.vue` | SVG arc gauge, top-5 factor bars, glow border |
| `cabin/SpeedPanel.vue` | Speedometer SVG with needle, danger zone arc |
| `cabin/FuelEnergyPanel.vue` | Tank SVG graphic, range estimation |
| `cabin/PressureTempPanel.vue` | 4 sensor bars with OK-zone overlay |
| `cabin/ElectricalPanel.vue` | Voltage/current bars, circuit diagram SVG |
| `cabin/AlertsPanel.vue` | Animated alert list with severity badges |
| `cabin/TrendsPanel.vue` | ECharts line chart, window selector, replay scrubber |
| `cabin/RouteMapPanel.vue` | SVG route map with animated train marker |

## Do not import from here

These files are not part of the active application.
They are documentation only — copy-paste the pieces you need.
