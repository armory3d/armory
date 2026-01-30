#include <libdragon.h>
#include <string.h>
#include <malloc.h>

#include "audio.h"
#include "audio_config.h"

#define AUDIO_FREQUENCY     44100
#define AUDIO_BUFFERS       4
#define MAX_LOADED_SOUNDS   16

typedef struct {
    wav64_t wav;
    char path[64];
    bool in_use;
    bool loop;
} LoadedSound;

static float mix_volumes[AUDIO_MIX_CHANNEL_COUNT];
static float channel_volumes[AUDIO_MIXER_CHANNELS];
static LoadedSound loaded_sounds[MAX_LOADED_SOUNDS];
static bool channel_in_use[AUDIO_MIXER_CHANNELS];
static int channel_mix_mapping[AUDIO_MIXER_CHANNELS];
static int channel_sound_slot[AUDIO_MIXER_CHANNELS];

static LoadedSound* find_or_load_sound(const char *path);
static int allocate_channel(int mix_channel);
static void apply_channel_volume(int ch);
static int find_sound_slot(const char *path);

void arm_audio_init(void)
{
    audio_init(AUDIO_FREQUENCY, AUDIO_BUFFERS);
    mixer_init(AUDIO_MIXER_CHANNELS);
    wav64_init_compression(3);  // Required for opus

    memset(loaded_sounds, 0, sizeof(loaded_sounds));
    memset(channel_in_use, 0, sizeof(channel_in_use));

    for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
        channel_mix_mapping[i] = -1;
        channel_sound_slot[i] = -1;
        channel_volumes[i] = 1.0f;
    }

    for (int i = 0; i < AUDIO_MIX_CHANNEL_COUNT; i++) {
        mix_volumes[i] = 1.0f;
    }

    mixer_set_vol(1.0f);
}

void arm_audio_shutdown(void)
{
    arm_audio_stop_all();

    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (loaded_sounds[i].in_use) {
            wav64_close(&loaded_sounds[i].wav);
            loaded_sounds[i].in_use = false;
        }
    }

    mixer_close();
}

void arm_audio_update(void)
{
    mixer_try_play();

    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (channel_in_use[ch] && !mixer_ch_playing(ch)) {
            channel_in_use[ch] = false;
            channel_mix_mapping[ch] = -1;
        }
    }
}

ArmSoundHandle arm_audio_load(const char *sound_path, int mix_channel, bool loop)
{
    ArmSoundHandle handle = { .channel = -1, .mix_channel = mix_channel, .sound_slot = -1, .volume = 1.0f, .finished = true };

    // Validate mix channel
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) {
        debugf("audio: invalid mix channel %d\n", mix_channel);
        return handle;
    }

    LoadedSound *sound = find_or_load_sound(sound_path);
    if (!sound) return handle;

    int slot = find_sound_slot(sound_path);
    sound->loop = loop;  // Store loop setting for later playback
    handle.sound_slot = slot;
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
    if (!handle || handle->sound_slot < 0) return;
    if (handle->sound_slot >= MAX_LOADED_SOUNDS) return;
    if (!loaded_sounds[handle->sound_slot].in_use) return;

    // Check if this sound_slot is already playing on a channel
    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (channel_in_use[ch] && channel_sound_slot[ch] == handle->sound_slot) {
            // Already playing this exact sound, update handle and return
            handle->channel = ch;
            handle->finished = false;
            // Apply handle's volume to the channel
            channel_volumes[ch] = handle->volume;
            apply_channel_volume(ch);
            return;
        }
    }

    int ch = allocate_channel(handle->mix_channel);
    if (ch < 0) {
        debugf("audio: no channels available\n");
        return;
    }

    LoadedSound *sound = &loaded_sounds[handle->sound_slot];
    wav64_set_loop(&sound->wav, sound->loop);
    wav64_play(&sound->wav, ch);

    channel_in_use[ch] = true;
    channel_mix_mapping[ch] = handle->mix_channel;
    channel_sound_slot[ch] = handle->sound_slot;
    // Apply handle's volume to the channel
    channel_volumes[ch] = handle->volume;
    apply_channel_volume(ch);

    handle->channel = ch;
    handle->finished = false;
}

void arm_audio_replay(ArmSoundHandle *handle)
{
    if (!handle || handle->sound_slot < 0) return;
    if (handle->sound_slot >= MAX_LOADED_SOUNDS) return;
    if (!loaded_sounds[handle->sound_slot].in_use) return;

    // Stop current playback if any
    if (handle->channel >= 0 && channel_in_use[handle->channel]) {
        mixer_ch_stop(handle->channel);
    }

    int ch = allocate_channel(handle->mix_channel);
    if (ch < 0) return;

    LoadedSound *sound = &loaded_sounds[handle->sound_slot];
    wav64_play(&sound->wav, ch);

    channel_in_use[ch] = true;
    channel_mix_mapping[ch] = handle->mix_channel;
    channel_sound_slot[ch] = handle->sound_slot;
    apply_channel_volume(ch);

    handle->channel = ch;
    handle->finished = false;
}

void arm_audio_stop(ArmSoundHandle *handle)
{
    if (!handle || handle->sound_slot < 0) return;

    // Find channel by sound_slot since handle might be a copy with stale channel info
    int ch = -1;
    if (handle->channel >= 0 && handle->channel < AUDIO_MIXER_CHANNELS &&
        channel_in_use[handle->channel] && channel_sound_slot[handle->channel] == handle->sound_slot) {
        ch = handle->channel;
    } else {
        // Look up channel by sound_slot
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if (channel_in_use[i] && channel_sound_slot[i] == handle->sound_slot) {
                ch = i;
                break;
            }
        }
    }

    if (ch >= 0) {
        mixer_ch_stop(ch);
        channel_in_use[ch] = false;
        channel_mix_mapping[ch] = -1;
        channel_sound_slot[ch] = -1;
    }

    handle->finished = true;
    handle->channel = -1;
}

bool arm_audio_is_playing(ArmSoundHandle *handle)
{
    if (!handle || handle->channel < 0) return false;

    bool playing = mixer_ch_playing(handle->channel);
    if (!playing) {
        handle->finished = true;
    }
    return playing;
}

void arm_audio_set_volume(ArmSoundHandle *handle, float volume)
{
    if (!handle) return;
    if (volume < 0.0f) volume = 0.0f;
    if (volume > 1.0f) volume = 1.0f;

    // Always store volume in handle (for use when starting)
    handle->volume = volume;

    // If channel is -1, try to find it from sound_slot
    int ch = handle->channel;
    if (ch < 0 && handle->sound_slot >= 0) {
        for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
            if (channel_in_use[i] && channel_sound_slot[i] == handle->sound_slot) {
                ch = i;
                break;
            }
        }
    }

    // If we found a channel, apply volume immediately
    if (ch >= 0) {
        channel_volumes[ch] = volume;
        apply_channel_volume(ch);
    }
}

void arm_audio_set_mix_volume(int mix_channel, float volume)
{
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) return;
    if (volume < 0.0f) volume = 0.0f;
    if (volume > 1.0f) volume = 1.0f;

    mix_volumes[mix_channel] = volume;

    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (channel_in_use[ch] && channel_mix_mapping[ch] == mix_channel) {
            apply_channel_volume(ch);
        }
    }
}

float arm_audio_get_mix_volume(int mix_channel)
{
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) return 0.0f;
    return mix_volumes[mix_channel];
}

void arm_audio_stop_all(void)
{
    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (channel_in_use[ch]) {
            mixer_ch_stop(ch);
            channel_in_use[ch] = false;
            channel_mix_mapping[ch] = -1;
        }
    }
}

static LoadedSound* find_or_load_sound(const char *path)
{
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (loaded_sounds[i].in_use && strcmp(loaded_sounds[i].path, path) == 0) {
            return &loaded_sounds[i];
        }
    }

    int slot = -1;
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (!loaded_sounds[i].in_use) {
            slot = i;
            break;
        }
    }

    if (slot < 0) {
        debugf("audio: no slots for %s\n", path);
        return NULL;
    }

    wav64_open(&loaded_sounds[slot].wav, path);
    strncpy(loaded_sounds[slot].path, path, sizeof(loaded_sounds[slot].path) - 1);
    loaded_sounds[slot].path[sizeof(loaded_sounds[slot].path) - 1] = '\0';
    loaded_sounds[slot].in_use = true;

    return &loaded_sounds[slot];
}

static int find_sound_slot(const char *path)
{
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (loaded_sounds[i].in_use && strcmp(loaded_sounds[i].path, path) == 0) {
            return i;
        }
    }
    return -1;
}

static int allocate_channel(int mix_channel)
{
    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (!channel_in_use[ch]) {
            // Allow playback of audio files up to 48000 Hz
            mixer_ch_set_limits(ch, 0, 48000, 0);
            return ch;
        }
    }
    return -1;
}

static void apply_channel_volume(int ch)
{
    int mix_ch = channel_mix_mapping[ch];
    if (mix_ch < 0) return;

    float vol = channel_volumes[ch] * mix_volumes[mix_ch];
    mixer_ch_set_vol(ch, vol, vol);
}
