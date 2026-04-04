<template>
  <div class="app-shell">
    <TopBar />

    <main class="cabin-grid">
      <section class="cabin-left">
        <HealthIndexCard />
        <AlertsPanel class="mt-4" />
      </section>

      <section class="cabin-center">
        <SpeedPanel />
        <TrendsPanel class="mt-4" />
      </section>

      <section class="cabin-right">
        <FuelEnergyPanel />
        <PressureTempPanel class="mt-4" />
        <ElectricalPanel class="mt-4" />
        <RouteMapPanel class="mt-4" />
      </section>
    </main>
  </div>
</template>

<script setup>
import TopBar from './components/layout/TopBar.vue';
import HealthIndexCard from './components/cabin/HealthIndexCard.vue';
import SpeedPanel from './components/cabin/SpeedPanel.vue';
import FuelEnergyPanel from './components/cabin/FuelEnergyPanel.vue';
import PressureTempPanel from './components/cabin/PressureTempPanel.vue';
import ElectricalPanel from './components/cabin/ElectricalPanel.vue';
import AlertsPanel from './components/cabin/AlertsPanel.vue';
import TrendsPanel from './components/cabin/TrendsPanel.vue';
import RouteMapPanel from './components/cabin/RouteMapPanel.vue';
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.cabin-grid {
  display: grid;
  grid-template-columns: 1.2fr 2fr 1.2fr;
  gap: 1rem;
  padding: 1rem;
}

.cabin-left,
.cabin-center,
.cabin-right {
  display: flex;
  flex-direction: column;
}

.mt-4 {
  margin-top: 1rem;
}
</style>