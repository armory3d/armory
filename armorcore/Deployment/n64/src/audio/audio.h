#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int channel;
    int mix_channel;
    int sound_slot;
    float volume;
    bool finished;
} ArmSoundHandle;

// Compare handles by sound_slot only (identifies the logical sound).
// The channel field is a runtime assignment that changes, not part of identity.
static inline bool arm_sound_handle_equals(ArmSoundHandle a, ArmSoundHandle b) {
    return a.sound_slot == b.sound_slot;
}

void arm_audio_init(void);
void arm_audio_shutdown(void);
void arm_audio_update(void);
void arm_audio_mixer_poll(void);

ArmSoundHandle arm_audio_load(const char *path, int mix_channel, bool loop);
ArmSoundHandle arm_audio_play(const char *path, int mix_channel, bool loop);
void arm_audio_start(ArmSoundHandle *handle);
void arm_audio_replay(ArmSoundHandle *handle);
void arm_audio_stop(ArmSoundHandle *handle);
bool arm_audio_is_playing(ArmSoundHandle *handle);

void arm_audio_set_volume(ArmSoundHandle *handle, float volume);
void arm_audio_set_mix_volume(int mix_channel, float volume);
float arm_audio_get_mix_volume(int mix_channel);
void arm_audio_stop_all(void);

// ============================================================================
// Sound Handle Array and Map types for channel pooling
// ============================================================================
#include "../system/arm_array.h"
#include "../system/arm_map.h"

// Array of sound handles (for channel pooling, max 8 channels per sound)
ARM_ARRAY_DECLARE(ArmSoundHandle, ArmSoundHandleArray, 8)

// Map from string key to sound handle array (for named channel groups)
ARM_MAP_DECLARE(ArmSoundHandleArray, ArmSoundChannelMap, 16)

#ifdef __cplusplus
}
#endif
