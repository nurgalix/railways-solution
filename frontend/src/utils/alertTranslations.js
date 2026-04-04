/**
 * Alert translations (EN → RU)
 */

// Alert code translations
const ALERT_CODES = {
  'SPEED_WARNING': 'СКОРОСТЬ_ВНИМАНИЕ',
  'SPEED_CRITICAL': 'СКОРОСТЬ_КРИТИЧНО',
  'FUEL_LEVEL_WARNING': 'ТОПЛИВО_ВНИМАНИЕ',
  'FUEL_LEVEL_CRITICAL': 'ТОПЛИВО_КРИТИЧНО',
  'PRESSURE_WARNING': 'ДАВЛЕНИЕ_ВНИМАНИЕ',
  'PRESSURE_CRITICAL': 'ДАВЛЕНИЕ_КРИТИЧНО',
  'TEMPERATURE_WARNING': 'ТЕМПЕРАТУРА_ВНИМАНИЕ',
  'TEMPERATURE_CRITICAL': 'ТЕМПЕРАТУРА_КРИТИЧНО',
};

// Parameter labels
const PARAM_LABELS = {
  speed: 'Скорость',
  fuel_level: 'Уровень топлива',
  pressure: 'Давление',
  temperature: 'Температура',
};

// Recommendations
const RECOMMENDATIONS = {
  // Speed
  'Reduce speed to within operational limits': 'Снизьте скорость до рабочих пределов',
  'EMERGENCY: Apply brakes immediately, speed dangerously high': 'АВАРИЙНАЯ СИТУАЦИЯ: Немедленно затормозить, опасно высокая скорость',
  
  // Fuel
  'Plan refueling stop at next station': 'Запланируйте заправку на следующей станции',
  'URGENT: Fuel critically low, stop at nearest point': 'СРОЧНО: Критически низкий уровень топлива, остановитесь в ближайшей точке',
  
  // Pressure
  'Pressure below normal — monitor closely': 'Давление ниже нормы — внимательно наблюдайте',
  'CRITICAL: Pressure dangerously low, risk of failure': 'КРИТИЧНО: Опасно низкое давление, риск отказа системы',
  
  // Temperature
  'Overheating — reduce load, check system': 'Перегрев — снизьте нагрузку, проверьте систему',
  'CRITICAL: Severe overheating, stop engine if safe to do so': 'КРИТИЧНО: Сильный перегрев, остановите двигатель при возможности',
};

// Message pattern translations
function translateMessage(message) {
  if (!message) return message;
  
  // Replace parameter labels
  let translated = message;
  Object.entries(PARAM_LABELS).forEach(([en, ru]) => {
    const label = en.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    translated = translated.replace(label, ru);
  });
  
  // Replace keywords
  translated = translated
    .replace(/is above/gi, 'выше')
    .replace(/is below/gi, 'ниже')
    .replace(/threshold/gi, 'порога')
    .replace(/limit/gi, 'предел')
    .replace(/Speed/g, 'Скорость')
    .replace(/Fuel Level/g, 'Уровень топлива')
    .replace(/Pressure/g, 'Давление')
    .replace(/Temperature/g, 'Температура')
    .replace(/warning/gi, 'предупреждение')
    .replace(/critical/gi, 'критический');
  
  return translated;
}

/**
 * Translate alert object to Russian
 */
export function translateAlert(alert) {
  if (!alert) return alert;
  
  return {
    ...alert,
    code: ALERT_CODES[alert.code] || alert.code,
    message: translateMessage(alert.message),
    recommendation: RECOMMENDATIONS[alert.recommendation] || alert.recommendation,
  };
}

/**
 * Translate array of alerts
 */
export function translateAlerts(alerts) {
  if (!Array.isArray(alerts)) return alerts;
  return alerts.map(translateAlert);
}
