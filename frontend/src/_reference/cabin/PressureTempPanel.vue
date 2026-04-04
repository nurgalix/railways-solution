<template>
  <div class="card" role="region" aria-label="Давление и температуры">
    <div class="card-title">Давления / Температуры</div>

    <div class="sensors-grid">
      <!-- Brake pressure -->
      <SensorGauge
        label="Тормозная маг."
        :value="pressureBrake"
        unit="бар"
        :min="0" :max="8"
        :ok-min="4.5" :ok-max="5.5"
        :warn-min="4.0" :warn-max="6.0"
        :decimals="2"
      />
      <!-- Main pressure -->
      <SensorGauge
        label="Главная маг."
        :value="pressureMain"
        unit="бар"
        :min="0" :max="12"
        :ok-min="7.5" :ok-max="9.5"
        :warn-min="6.5" :warn-max="10.5"
        :decimals="2"
      />
      <!-- Engine temperature -->
      <SensorGauge
        label="Двигатель"
        :value="tempEngine"
        unit="°C"
        :min="0" :max="120"
        :ok-min="60" :ok-max="88"
        :warn-min="50" :warn-max="100"
        :decimals="1"
      />
      <!-- Oil temperature -->
      <SensorGauge
        label="Масло"
        :value="tempOil"
        unit="°C"
        :min="0" :max="110"
        :ok-min="55" :ok-max="85"
        :warn-min="45" :warn-max="95"
        :decimals="1"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue';
import { useTelemetryStore } from '@/stores/telemetry.js';

const store = useTelemetryStore();
const t = computed(() => store.current);

const pressureBrake = computed(() => t.value?.pressure_brake ?? 0);
const pressureMain  = computed(() => t.value?.pressure_main  ?? 0);
const tempEngine    = computed(() => t.value?.temp_engine    ?? 0);
const tempOil       = computed(() => t.value?.temp_oil       ?? 0);

// ─── Inline sensor gauge component ──────────────────────────────
const SensorGauge = defineComponent({
  props: {
    label:    String,
    value:    Number,
    unit:     String,
    min:      Number,
    max:      Number,
    okMin:    Number,
    okMax:    Number,
    warnMin:  Number,
    warnMax:  Number,
    decimals: { type: Number, default: 1 },
  },
  setup(props) {
    const ratio = computed(() =>
      Math.min(1, Math.max(0, (props.value - props.min) / (props.max - props.min)))
    );

    const color = computed(() => {
      const v = props.value;
      if (v >= props.okMin && v <= props.okMax)    return 'var(--color-normal)';
      if (v >= props.warnMin && v <= props.warnMax) return 'var(--color-warning)';
      return 'var(--color-critical)';
    });

    const statusLabel = computed(() => {
      const v = props.value;
      if (v >= props.okMin && v <= props.okMax) return 'норма';
      if (v >= props.warnMin && v <= props.warnMax) return 'внимание';
      return 'критично';
    });

    return () => h('div', { class: 'sensor-item' }, [
      h('div', { class: 'sensor-header' }, [
        h('span', { class: 'sensor-label' }, props.label),
        h('span', {
          class: 'sensor-value font-mono',
          style: { color: color.value },
        }, `${props.value.toFixed(props.decimals)} ${props.unit}`),
      ]),
      h('div', { class: 'sensor-track' }, [
        // OK zone indicator
        h('div', {
          class: 'sensor-ok-zone',
          style: {
            left:  ((props.okMin - props.min) / (props.max - props.min) * 100) + '%',
            width: ((props.okMax - props.okMin) / (props.max - props.min) * 100) + '%',
          },
        }),
        // Fill bar
        h('div', {
          class: 'sensor-fill',
          style: { width: (ratio.value * 100) + '%', background: color.value },
        }),
      ]),
      h('div', { class: 'sensor-range' }, [
        h('span', {}, props.min),
        h('span', { style: { color: color.value, fontSize: '0.65rem' } }, statusLabel.value),
        h('span', {}, props.max),
      ]),
    ]);
  },
});
</script>

<style scoped>
.sensors-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.sensor-item { display: flex; flex-direction: column; gap: 0.25rem; }

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.25rem;
}

.sensor-label {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.sensor-value {
  font-size: 0.9rem;
  font-weight: 700;
  transition: color 0.3s;
}

.sensor-track {
  position: relative;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  overflow: hidden;
}

.sensor-ok-zone {
  position: absolute;
  top: 0;
  height: 100%;
  background: rgba(16, 185, 129, 0.15);
  border-radius: 3px;
}

.sensor-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease, background 0.3s;
}

.sensor-range {
  display: flex;
  justify-content: space-between;
  font-size: 0.62rem;
  color: var(--color-text-muted);
}
</style>
