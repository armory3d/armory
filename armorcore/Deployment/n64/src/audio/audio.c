#include <libdragon.h>
#include <string.h>

#include "audio.h"
#include "audio_config.h"

#define AUDIO_FREQUENCY     44100
#define AUDIO_BUFFERS       4
#define MAX_LOADED_SOUNDS   16

typedef struct {
    wav64_t *wav;
    char path[64];
    bool loop;
} SoundSlot;

// Channel state packed for cache efficiency
static struct {
    float mix_volumes[AUDIO_MIX_CHANNEL_COUNT];
    float channel_volumes[AUDIO_MIXER_CHANNELS];
    int8_t channel_mix_mapping[AUDIO_MIXER_CHANNELS];
    int8_t channel_sound_slot[AUDIO_MIXER_CHANNELS];
    uint32_t channel_in_use;       // Bitfield for up to 32 channels
    uint32_t channel_stereo_main;  // Bitfield: 1 = this channel is stereo primary (uses ch+1)
} state;

static SoundSlot sound_slots[MAX_LOADED_SOUNDS];

static int find_or_load_sound(const char *path);
static inline void apply_channel_volume(int ch);

void arm_audio_init(void)
{
    audio_init(AUDIO_FREQUENCY, AUDIO_BUFFERS);
    mixer_init(AUDIO_MIXER_CHANNELS);
    wav64_init_compression(3);

    // Opus uses 48kHz, need to raise channel frequency limits
    for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
        mixer_ch_set_limits(i, 0, 48000, 0);
    }

    memset(sound_slots, 0, sizeof(sound_slots));
    memset(&state, 0, sizeof(state));

    for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
        state.channel_mix_mapping[i] = -1;
        state.channel_sound_slot[i] = -1;
        state.channel_volumes[i] = 1.0f;
    }

    for (int i = 0; i < AUDIO_MIX_CHANNEL_COUNT; i++) {
        state.mix_volumes[i] = 1.0f;
    }

    mixer_set_vol(1.0f);
}

void arm_audio_shutdown(void)
{
    arm_audio_stop_all();

    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (sound_slots[i].wav) {
            wav64_close(sound_slots[i].wav);
        }
    }
    memset(sound_slots, 0, sizeof(sound_slots));

    mixer_close();
}

void arm_audio_update(void)
{
    uint32_t mask = state.channel_in_use;
    for (int ch = 0; mask; ch++, mask >>= 1) {
        if (!(mask & 1)) continue;

        // Skip stereo sub-channels (ch+1 of a stereo pair) - they're managed by primary
        if (ch > 0 && (state.channel_stereo_main & (1 << (ch - 1)))) {
            continue;
        }

        if (!mixer_ch_playing(ch)) {
            // Release this channel
            state.channel_in_use &= ~(1 << ch);
            state.channel_mix_mapping[ch] = -1;
            state.channel_sound_slot[ch] = -1;

            // If this was stereo primary, also release the sub-channel
            if (state.channel_stereo_main & (1 << ch)) {
                state.channel_stereo_main &= ~(1 << ch);
                if (ch + 1 < AUDIO_MIXER_CHANNELS) {
                    state.channel_in_use &= ~(1 << (ch + 1));
                    state.channel_mix_mapping[ch + 1] = -1;
                    state.channel_sound_slot[ch + 1] = -1;
                }
            }
        }
    }
}

void arm_audio_mixer_poll(void)
{
    mixer_try_play();
}

ArmSoundHandle arm_audio_load(const char *sound_path, int mix_channel, bool loop)
{
    ArmSoundHandle handle = { -1, mix_channel, -1, 1.0f, true };

    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) {
        return handle;
    }

    int slot = find_or_load_sound(sound_path);
    if (slot >= 0) {
        sound_slots[slot].loop = loop;
        handle.sound_slot = slot;
    }
    return handle;
}

ArmSoundHandle arm_audio_play(const char *sound_path, int mix_channel, bool loop)
{
    ArmSoundHandle handle = arm_audio_load(sound_path, mix_channel, loop);
    if (handle.sound_slot >= 0) {
        arm_audio_start(&handle);
    }
    return handle;
}

void arm_audio_start(ArmSoundHandle *handle)
{
    if (!handle || handle->sound_slot < 0 || handle->sound_slot >= MAX_LOADED_SOUNDS) return;

    SoundSlot *slot = &sound_slots[handle->sound_slot];
    if (!slot->wav) return;

    bool is_stereo = (slot->wav->wave.channels == 2);

    // Check if THIS handle's channel is still playing (not any channel with same sound)
    // This allows multiple handles with the same sound to play simultaneously (channel pooling)
    if (handle->channel >= 0 && handle->channel < AUDIO_MIXER_CHANNELS) {
        if ((state.channel_in_use & (1 << handle->channel)) &&
            state.channel_sound_slot[handle->channel] == handle->sound_slot &&
            mixer_ch_playing(handle->channel)) {
            // This specific handle's channel is still playing - don't restart
            handle->finished = false;
            return;
        }
    }

    // Find free channel(s)
    int ch = -1;
    if (is_stereo) {
        // Stereo needs TWO consecutive free channels
        for (int i = 0; i < AUDIO_MIXER_CHANNELS - 1; i++) {
            uint8_t pair_mask = (1 << i) | (1 << (i + 1));
            if ((state.channel_in_use & pair_mask) == 0) {
                ch = i;
                break;
            }
        }
    } else {
        // Mono needs one free channel
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if (!(state.channel_in_use & (1 << i))) {
                ch = i;
                break;
            }
        }
    }
    if (ch < 0) return;

    wav64_set_loop(slot->wav, slot->loop);
    wav64_play(slot->wav, ch);

    // Mark channel(s) as in use
    state.channel_in_use |= (1 << ch);
    state.channel_mix_mapping[ch] = handle->mix_channel;
    state.channel_sound_slot[ch] = handle->sound_slot;
    state.channel_volumes[ch] = handle->volume;
    apply_channel_volume(ch);

    if (is_stereo) {
        // Mark stereo primary and reserve the sub-channel
        state.channel_stereo_main |= (1 << ch);
        state.channel_in_use |= (1 << (ch + 1));
        state.channel_mix_mapping[ch + 1] = handle->mix_channel;
        state.channel_sound_slot[ch + 1] = handle->sound_slot;
    }

    handle->channel = ch;
    handle->finished = false;
}

void arm_audio_replay(ArmSoundHandle *handle)
{
    if (!handle || handle->sound_slot < 0 || handle->sound_slot >= MAX_LOADED_SOUNDS) return;

    SoundSlot *slot = &sound_slots[handle->sound_slot];
    if (!slot->wav) return;

    bool is_stereo = (slot->wav->wave.channels == 2);

    // Stop current playback
    if (handle->channel >= 0 && (state.channel_in_use & (1 << handle->channel))) {
        mixer_ch_stop(handle->channel);
        state.channel_in_use &= ~(1 << handle->channel);
        // If stereo, also release sub-channel
        if (state.channel_stereo_main & (1 << handle->channel)) {
            state.channel_stereo_main &= ~(1 << handle->channel);
            if (handle->channel + 1 < AUDIO_MIXER_CHANNELS) {
                state.channel_in_use &= ~(1 << (handle->channel + 1));
            }
        }
    }

    // Find free channel(s)
    int ch = -1;
    if (is_stereo) {
        for (int i = 0; i < AUDIO_MIXER_CHANNELS - 1; i++) {
            uint8_t pair_mask = (1 << i) | (1 << (i + 1));
            if ((state.channel_in_use & pair_mask) == 0) {
                ch = i;
                break;
            }
        }
    } else {
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if (!(state.channel_in_use & (1 << i))) {
                ch = i;
                break;
            }
        }
    }
    if (ch < 0) return;

    wav64_play(slot->wav, ch);

    state.channel_in_use |= (1 << ch);
    state.channel_mix_mapping[ch] = handle->mix_channel;
    state.channel_sound_slot[ch] = handle->sound_slot;
    state.channel_volumes[ch] = handle->volume;
    apply_channel_volume(ch);

    if (is_stereo) {
        state.channel_stereo_main |= (1 << ch);
        state.channel_in_use |= (1 << (ch + 1));
        state.channel_mix_mapping[ch + 1] = handle->mix_channel;
        state.channel_sound_slot[ch + 1] = handle->sound_slot;
    }

    handle->channel = ch;
    handle->finished = false;
}

void arm_audio_stop(ArmSoundHandle *handle)
{
    if (!handle || handle->sound_slot < 0) return;

    int ch = handle->channel;

    // Validate or find channel
    if (ch >= 0 && ch < AUDIO_MIXER_CHANNELS &&
        (state.channel_in_use & (1 << ch)) &&
        state.channel_sound_slot[ch] == handle->sound_slot) {
        // Channel is valid
    } else {
        // Search for channel
        ch = -1;
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if ((state.channel_in_use & (1 << i)) &&
                state.channel_sound_slot[i] == handle->sound_slot) {
                ch = i;
                break;
            }
        }
    }

    if (ch >= 0) {
        mixer_ch_stop(ch);
        state.channel_in_use &= ~(1 << ch);
        state.channel_mix_mapping[ch] = -1;
        state.channel_sound_slot[ch] = -1;

        // If stereo primary, also release sub-channel
        if (state.channel_stereo_main & (1 << ch)) {
            state.channel_stereo_main &= ~(1 << ch);
            if (ch + 1 < AUDIO_MIXER_CHANNELS) {
                state.channel_in_use &= ~(1 << (ch + 1));
                state.channel_mix_mapping[ch + 1] = -1;
                state.channel_sound_slot[ch + 1] = -1;
            }
        }
    }

    handle->finished = true;
    handle->channel = -1;
}

bool arm_audio_is_playing(ArmSoundHandle *handle)
{
    if (!handle || handle->channel < 0) return false;

    bool playing = mixer_ch_playing(handle->channel);
    if (!playing) handle->finished = true;
    return playing;
}

void arm_audio_set_volume(ArmSoundHandle *handle, float volume)
{
    if (!handle) return;

    if (volume < 0.0f) volume = 0.0f;
    else if (volume > 1.0f) volume = 1.0f;
    handle->volume = volume;

    int ch = handle->channel;
    if (ch < 0 && handle->sound_slot >= 0) {
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if ((state.channel_in_use & (1 << i)) &&
                state.channel_sound_slot[i] == handle->sound_slot) {
                ch = i;
                break;
            }
        }
    }

    if (ch >= 0) {
        state.channel_volumes[ch] = volume;
        apply_channel_volume(ch);
    }
}

void arm_audio_set_mix_volume(int mix_channel, float volume)
{
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) return;

    if (volume < 0.0f) volume = 0.0f;
    else if (volume > 1.0f) volume = 1.0f;
    state.mix_volumes[mix_channel] = volume;

    uint32_t mask = state.channel_in_use;
    for (int ch = 0; mask; ch++, mask >>= 1) {
        if ((mask & 1) && state.channel_mix_mapping[ch] == mix_channel) {
            apply_channel_volume(ch);
        }
    }
}

float arm_audio_get_mix_volume(int mix_channel)
{
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) return 0.0f;
    return state.mix_volumes[mix_channel];
}

void arm_audio_stop_all(void)
{
    uint32_t mask = state.channel_in_use;
    for (int ch = 0; mask; ch++, mask >>= 1) {
        if (mask & 1) {
            mixer_ch_stop(ch);
        }
    }
    state.channel_in_use = 0;
    state.channel_stereo_main = 0;
    memset(state.channel_mix_mapping, -1, sizeof(state.channel_mix_mapping));
    memset(state.channel_sound_slot, -1, sizeof(state.channel_sound_slot));
}

static int find_or_load_sound(const char *path)
{
    // Check if already loaded
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (sound_slots[i].wav && strcmp(sound_slots[i].path, path) == 0) {
            return i;
        }
    }

    // Find empty slot
    int slot = -1;
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (!sound_slots[i].wav) {
            slot = i;
            break;
        }
    }
    if (slot < 0) return -1;

    sound_slots[slot].wav = wav64_load(path, NULL);
    if (!sound_slots[slot].wav) return -1;

    strncpy(sound_slots[slot].path, path, sizeof(sound_slots[slot].path) - 1);
    sound_slots[slot].path[sizeof(sound_slots[slot].path) - 1] = '\0';
    sound_slots[slot].loop = false;

    return slot;
}

static inline void apply_channel_volume(int ch)
{
    int mix_ch = state.channel_mix_mapping[ch];
    if (mix_ch < 0) return;

    float vol = state.channel_volumes[ch] * state.mix_volumes[mix_ch];
    mixer_ch_set_vol(ch, vol, vol);
}
