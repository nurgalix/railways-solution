<template>
  <div class="card">
    <div class="card-title">Давления / Температуры</div>

    <div class="sensor-grid">
      <div v-for="s in sensors" :key="s.key" class="sensor-item">
        <div class="sensor-header">
          <span class="sensor-name">{{ s.name }}</span>
          <span class="sensor-value font-mono" :style="{ color: s.color }">
            {{ s.value.toFixed(s.dec) }} {{ s.unit }}
          </span>
        </div>
        <div class="bar-track" style="position:relative">
          <!-- ok zone highlight -->
          <div :style="{
            position:'absolute', top:0, bottom:0, borderRadius:'3px',
            background:'rgba(16,185,129,0.12)',
            left: s.okLeft + '%',
            width: s.okWidth + '%',
          }"></div>
          <div class="bar-fill" :style="{ width: s.ratio + '%', background: s.color }"></div>
        </div>
        <div class="sensor-range-row">
          <span>{{ s.min }}</span>
          <span :style="{ color: s.color, fontSize:'0.58rem', fontWeight:600 }">{{ s.status }}</span>
          <span>{{ s.max }}</span>
        </div>
      </div>
    </div>

    <!-- TODO: add thermometer / gauge visuals from _reference/cabin/PressureTempPanel.vue -->
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t     = computed(() => store.current);

function makeSensor({ key, name, unit, dec, min, max, okMin, okMax, warnMin, warnMax }) {
  return computed(() => {
    const raw   = t.value?.[key] ?? 0;
    const ratio = Math.min(100, Math.max(0, ((raw - min) / (max - min)) * 100));
    const okLeft  = ((okMin - min) / (max - min)) * 100;
    const okWidth = ((okMax - okMin) / (max - min)) * 100;
    let color  = 'var(--ok)';
    let status = 'норма';
    if (raw < warnMin || raw > warnMax) { color = 'var(--crit)'; status = 'критично'; }
    else if (raw < okMin || raw > okMax) { color = 'var(--warn)'; status = 'внимание'; }
    return { key, name, unit, dec, min, max, value: raw, ratio, okLeft, okWidth, color, status };
  });
}

const pressureBrakeS = makeSensor({ key:'pressure_brake', name:'Тормозная',  unit:'бар', dec:2, min:0, max:8,   okMin:4.5, okMax:5.5, warnMin:4.0, warnMax:6.0 });
const pressureMainS  = makeSensor({ key:'pressure_main',  name:'Главная',    unit:'бар', dec:2, min:0, max:12,  okMin:7.5, okMax:9.5, warnMin:6.5, warnMax:10.5 });
const tempEngineS    = makeSensor({ key:'temp_engine',    name:'Двигатель',  unit:'°C',  dec:1, min:0, max:120, okMin:60,  okMax:88,  warnMin:50,  warnMax:100 });
const tempOilS       = makeSensor({ key:'temp_oil',       name:'Масло',      unit:'°C',  dec:1, min:0, max:110, okMin:55,  okMax:85,  warnMin:45,  warnMax:95 });

const sensors = computed(() => [
  pressureBrakeS.value,
  pressureMainS.value,
  tempEngineS.value,
  tempOilS.value,
]);
</script>
