/**
 * Route waypoints for the Almaty → Taraz corridor.
 * These are static reference points used for map rendering and ETA calculation.
 * Actual position comes from the backend via telemetry frames.
 */
export const ROUTE_WAYPOINTS = [
  { lat: 43.238949, lng: 76.889709, km: 0,   name: 'Алматы' },
  { lat: 43.18,     lng: 76.52,     km: 45,  name: '' },
  { lat: 43.06,     lng: 76.10,     km: 92,  name: '' },
  { lat: 42.90,     lng: 75.68,     km: 141, name: '' },
  { lat: 42.72,     lng: 75.20,     km: 192, name: 'Чу' },
  { lat: 42.50,     lng: 74.80,     km: 240, name: '' },
  { lat: 42.30,     lng: 74.25,     km: 295, name: 'Луговая' },
  { lat: 42.18,     lng: 73.60,     km: 350, name: 'Тараз' },
];

export const ROUTE_MAX_KM = ROUTE_WAYPOINTS[ROUTE_WAYPOINTS.length - 1].km;
