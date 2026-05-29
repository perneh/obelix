/** Category route/motion helpers for the scenario builder. */

export const MOTION_CATEGORIES = new Set([15, 21, 34, 48, 62, 240]);

export function supportsMotion(category) {
  return MOTION_CATEGORIES.has(category);
}

export function stepDistanceLabel(category) {
  if (category === 48) return "Distance per message (NM)";
  if (category === 34 || category === 240) return "Azimuth change per message (°)";
  return "Distance per message (m)";
}

export function stepDistanceHint(category) {
  if (category === 48) return "Range increases each tick along the heading bearing";
  if (category === 34) return "Antenna azimuth increases by this amount each tick";
  if (category === 240) return "Video radial azimuth window sweeps by this amount each tick";
  return "Position moves this far each tick in the chosen direction";
}

export function motionFieldConfig(category, fields) {
  if (category === 15) {
    const positionType = Number(fields?.position_type ?? 2);
    if (positionType === 1) {
      return [
        { key: "latitude_deg", label: "End latitude", unit: "°" },
        { key: "longitude_deg", label: "End longitude", unit: "°" },
      ];
    }
    return [
      { key: "range_m", label: "End range", unit: "m" },
      { key: "azimuth", label: "End azimuth", unit: "°" },
    ];
  }
  if (category === 62) {
    const positionType = Number(fields?.position_type ?? 2);
    if (positionType === 1) {
      return [
        { key: "x_m", label: "End X", unit: "m" },
        { key: "y_m", label: "End Y", unit: "m" },
      ];
    }
    return [
      { key: "latitude_deg", label: "End latitude", unit: "°" },
      { key: "longitude_deg", label: "End longitude", unit: "°" },
    ];
  }
  if (category === 48) {
    return [
      { key: "rho_nm", label: "End range", unit: "NM" },
      { key: "theta_deg", label: "End azimuth", unit: "°" },
    ];
  }
  if (category === 34 || category === 240) {
    return [{ key: "azimuth", label: "End azimuth", unit: "°" }];
  }
  return [];
}

export function formatWaypointSummary(category, fields, waypoint) {
  if (!waypoint) return "—";
  const cfg = motionFieldConfig(category, fields);
  return cfg
    .map(({ key, unit }) => {
      const val = waypoint[key];
      return val == null ? null : `${key}=${Number(val).toFixed(4)}${unit ? unit : ""}`;
    })
    .filter(Boolean)
    .join(", ");
}

export function defaultStepDistance(category) {
  if (category === 48) return 1.0;
  if (category === 34) return 10.0;
  if (category === 240) return 2.0;
  if (category === 15) return 1000.0;
  return 1000.0;
}

export function ensureStepMotion(step) {
  if (!step.motion) {
    step.motion = {
      enabled: false,
      mode: "direction",
      waypoints: [{}, {}],
      heading_deg: 90.0,
      step_distance: defaultStepDistance(step.message.category),
      ticks: 10,
      tick_interval_ms: 1000,
      update_time: true,
      derive_velocity: step.message.category === 62,
    };
  }
  if (step.motion.mode == null) {
    step.motion.mode = "direction";
  }
  if (step.motion.heading_deg == null) {
    step.motion.heading_deg = 90.0;
  }
  if (step.motion.step_distance == null) {
    step.motion.step_distance = defaultStepDistance(step.message.category);
  }
  return step.motion;
}

export function motionMessageCount(step) {
  if (step.motion?.enabled) {
    return step.motion.ticks ?? 10;
  }
  return step.repeat ?? 1;
}

export function totalStepMessages(step) {
  return motionMessageCount(step);
}
