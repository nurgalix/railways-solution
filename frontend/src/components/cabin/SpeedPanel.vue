<template>
  <div class="card">
    <div class="card-title">Скорость</div>

    <div class="flex items-baseline gap-2">
      <span class="speed-big" :style="{ color: speedColor }">{{ Math.round(speed) }}</span>
      <span class="speed-unit">км/ч</span>
      <span v-if="overLimit" class="badge badge-crit" style="margin-left:auto">ПРЕВЫШЕНИЕ</span>
    </div>

    <!-- Speed bar: 0–140, danger zone marker at 120 -->
    <div class="bar-track" style="margin-top:0.6rem; height:8px; position:relative">
      <div style="position:absolute; left:85.7%; top:0; bottom:0; width:1px; background:var(--crit); opacity:0.5"></div>
      <div class="bar-fill" :style="{ width: Math.min(speed / 140 * 100, 100) + '%', background: speedColor }"></div>
    </div>
    <div class="flex justify-between text-xs text-muted" style="margin-top:0.2rem">
      <span>0</span>
      <span style="color:var(--crit); font-size:0.58rem">120</span>
      <span>140</span>
    </div>

    <div class="card-divider"></div>

    <div class="speed-meta">
      <div>
        <div class="label">Позиция</div>
        <div class="font-mono" style="font-weight:600">{{ posKm }} км</div>
      </div>
      <div>
        <div class="label">Направление</div>
        <div style="font-weight:600">→ Тараз</div>
      </div>
      <div>
        <div class="label">Лимит</div>
        <div style="font-weight:600">120 км/ч</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();

const speed     = computed(() => store.data?.speed       ?? 0);
const posKm     = computed(() => store.data?.position?.km_marker ?? '–');
const overLimit = computed(() => speed.value > 120);

const speedColor = computed(() =>
  speed.value > 120 ? 'var(--crit)'
  : speed.value > 100 ? 'var(--warn)'
  : 'var(--text)'
);
</script>
