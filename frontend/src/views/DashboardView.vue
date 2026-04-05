<template>
  <div class="app-content">
    <div class="dashboard-layout">

      <!-- Left column: Speed, Fuel -->
      <div class="dash-col">
        <SpeedPanel />
        <FuelEnergyPanel />
        <PressureTempPanel />
      </div>

      <!-- Right column: Health, Sensors, Alerts -->
      <div class="dash-col">
        <HealthIndexCard />
        <RouteMapPanel />
        <AlertsPanel />
      </div>

    </div>
  </div>
</template>

<script setup>
import HealthIndexCard   from '@/components/cabin/HealthIndexCard.vue';
import AlertsPanel       from '@/components/cabin/AlertsPanel.vue';
import SpeedPanel        from '@/components/cabin/SpeedPanel.vue';
import FuelEnergyPanel   from '@/components/cabin/FuelEnergyPanel.vue';
import PressureTempPanel from '@/components/cabin/PressureTempPanel.vue';
import RouteMapPanel     from '@/components/cabin/RouteMapPanel.vue';
</script>
