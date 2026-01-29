#pragma once

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int channel;        // Mixer channel (-1 if not playing)
    int mix_channel;
    int sound_slot;     // For replay
    bool finished;
} ArmSoundHandle;

// Helper for comparing sound handles (compares channel and sound_slot)
static inline bool arm_sound_handle_equals(ArmSoundHandle a, ArmSoundHandle b) {
    return a.channel == b.channel && a.sound_slot == b.sound_slot;
}

void arm_audio_init(void);
void arm_audio_shutdown(void);
void arm_audio_update(void);

ArmSoundHandle arm_audio_play(const char *path, int mix_channel, bool loop);
void arm_audio_replay(ArmSoundHandle *handle);
void arm_audio_stop(ArmSoundHandle *handle);
bool arm_audio_is_playing(ArmSoundHandle *handle);

void arm_audio_set_volume(ArmSoundHandle *handle, float volume);
void arm_audio_set_mix_volume(int mix_channel, float volume);
float arm_audio_get_mix_volume(int mix_channel);
void arm_audio_stop_all(void);

#ifdef __cplusplus
}
#endif
