#pragma once

// TimeStep holds simulation timing information
typedef struct OimoTimeStep {
    float dt;        // Time step of simulation
    float invDt;     // Inverse time step (simulation FPS)
    float dtRatio;   // Ratio: current dt / previous dt
} OimoTimeStep;

static inline OimoTimeStep oimo_time_step_create(void) {
    OimoTimeStep ts;
    ts.dt = 0.0f;
    ts.invDt = 0.0f;
    ts.dtRatio = 1.0f;
    return ts;
}

