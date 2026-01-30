// Time system - frame delta and elapsed time tracking
#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

extern float time_delta;  // Frame delta in seconds (Time.delta)
extern float time_scale;  // Time scale factor (Time.scale)

void time_init(void);
void time_update(void);
float time_get(void);        // Total elapsed seconds (Time.time())
uint64_t time_get_ms(void);
uint64_t time_get_us(void);

#ifdef __cplusplus
}
#endif
