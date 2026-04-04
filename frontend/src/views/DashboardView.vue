<template>
  <div class="app-content">
    <div class="dashboard-layout">

      <!-- LEFT column -->
      <div class="dash-col dash-col-left">
        <HealthIndexCard />
        <AlertsPanel />
      </div>

      <!-- CENTER column -->
      <div class="dash-col dash-col-center">
        <SpeedPanel />
        <TrendsPanel />
      </div>

      <!-- RIGHT column -->
      <div class="dash-col dash-col-right">
        <FuelEnergyPanel />
        <PressureTempPanel />
        <ElectricalPanel />
        <RouteMapPanel />
      </div>

    </div>
  </div>
</template>

<script setup>
import HealthIndexCard   from '@/components/cabin/HealthIndexCard.vue';
import AlertsPanel       from '@/components/cabin/AlertsPanel.vue';
import SpeedPanel        from '@/components/cabin/SpeedPanel.vue';
import TrendsPanel       from '@/components/cabin/TrendsPanel.vue';
import FuelEnergyPanel   from '@/components/cabin/FuelEnergyPanel.vue';
import PressureTempPanel from '@/components/cabin/PressureTempPanel.vue';
import ElectricalPanel   from '@/components/cabin/ElectricalPanel.vue';
import RouteMapPanel     from '@/components/cabin/RouteMapPanel.vue';
</script>
