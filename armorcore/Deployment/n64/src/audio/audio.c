#include <libdragon.h>
#include <string.h>

#include "audio.h"
#include "audio_config.h"

// Audio configuration
#define AUDIO_FREQUENCY     32000   // 32kHz - good balance of quality/performance for N64
#define AUDIO_BUFFERS       4       // Number of audio buffers

// Maximum number of simultaneously loaded WAV64 files
#define MAX_LOADED_SOUNDS   16

typedef struct {
    wav64_t *wav;       // Pointer returned by wav64_load
    char path[64];
    bool in_use;
} LoadedSound;

// Mix channel volumes (indexed by mix channel id)
static float mix_volumes[AUDIO_MIX_CHANNEL_COUNT];

// Loaded sounds cache
static LoadedSound loaded_sounds[MAX_LOADED_SOUNDS];

// Track which mixer channels are in use
static bool channel_in_use[AUDIO_MIXER_CHANNELS];

// Track which mix channel each mixer channel belongs to
static int channel_mix_mapping[AUDIO_MIXER_CHANNELS];

// Forward declarations
static LoadedSound* find_or_load_sound(const char *path);
static int allocate_channel(int mix_channel);
static void apply_channel_volume(int ch);

void arm_audio_init(void)
{
    // Initialize libdragon audio subsystem
    audio_init(AUDIO_FREQUENCY, AUDIO_BUFFERS);

    // Initialize mixer with total channel count
    mixer_init(AUDIO_MIXER_CHANNELS);

    // Reset state
    memset(loaded_sounds, 0, sizeof(loaded_sounds));
    memset(channel_in_use, 0, sizeof(channel_in_use));

    // Initialize channel to mix channel mapping
    for (int i = 0; i < AUDIO_MIXER_CHANNELS; i++) {
        channel_mix_mapping[i] = -1;
    }

    // Set default volumes (all at 1.0)
    for (int i = 0; i < AUDIO_MIX_CHANNEL_COUNT; i++) {
        mix_volumes[i] = 1.0f;
    }

    // Apply master volume
    mixer_set_vol(1.0f);
}

void arm_audio_shutdown(void)
{
    // Stop all sounds
    arm_audio_stop_all();

    // Close all loaded sounds
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (loaded_sounds[i].in_use && loaded_sounds[i].wav) {
            wav64_close(loaded_sounds[i].wav);
            loaded_sounds[i].wav = NULL;
            loaded_sounds[i].in_use = false;
        }
    }

    // Shutdown mixer and audio
    mixer_close();
    audio_close();
}

void arm_audio_update(void)
{
    // Use libdragon's recommended helper for audio mixing
    // This handles streaming from ROM and mixing efficiently
    mixer_try_play();

    // Update channel_in_use flags based on actual playback state
    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (channel_in_use[ch] && !mixer_ch_playing(ch)) {
            channel_in_use[ch] = false;
            channel_mix_mapping[ch] = -1;
        }
    }
}

ArmSoundHandle arm_audio_play(const char *sound_path, int mix_channel, bool loop)
{
    ArmSoundHandle handle = { .channel = -1, .mix_channel = mix_channel, .finished = true };

    // Validate mix channel
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) {
        debugf("audio: invalid mix channel %d\n", mix_channel);
        return handle;
    }

    LoadedSound *sound = find_or_load_sound(sound_path);
    if (!sound || !sound->wav) return handle;

    // Find available mixer channel
    int ch = allocate_channel(mix_channel);
    if (ch < 0) {
        debugf("audio: no channels available for mix channel %d\n", mix_channel);
        return handle;
    }

    // Configure looping
    wav64_set_loop(sound->wav, loop);

    // Play on allocated channel
    wav64_play(sound->wav, ch);
    channel_in_use[ch] = true;
    channel_mix_mapping[ch] = mix_channel;

    // Apply volume
    apply_channel_volume(ch);

    handle.channel = ch;
    handle.finished = false;
    return handle;
}

void arm_audio_stop(ArmSoundHandle *handle)
{
    if (!handle || handle->channel < 0) return;

    mixer_ch_stop(handle->channel);
    channel_in_use[handle->channel] = false;
    channel_mix_mapping[handle->channel] = -1;
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
    if (!handle || handle->channel < 0) return;

    // Clamp
    if (volume < 0.0f) volume = 0.0f;
    if (volume > 1.0f) volume = 1.0f;

    // Apply with mix channel attenuation
    float effective = volume * mix_volumes[handle->mix_channel];
    mixer_ch_set_vol(handle->channel, effective, effective);
}

void arm_audio_set_mix_volume(int mix_channel, float volume)
{
    if (mix_channel < 0 || mix_channel >= AUDIO_MIX_CHANNEL_COUNT) return;

    // Clamp volume
    if (volume < 0.0f) volume = 0.0f;
    if (volume > 1.0f) volume = 1.0f;

    mix_volumes[mix_channel] = volume;

    // Update all playing channels that belong to this mix channel
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

// --- Internal functions ---

static LoadedSound* find_or_load_sound(const char *path)
{
    // Check if already loaded
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (loaded_sounds[i].in_use && strcmp(loaded_sounds[i].path, path) == 0) {
            return &loaded_sounds[i];
        }
    }

    // Find empty slot
    int slot = -1;
    for (int i = 0; i < MAX_LOADED_SOUNDS; i++) {
        if (!loaded_sounds[i].in_use) {
            slot = i;
            break;
        }
    }

    if (slot < 0) {
        debugf("audio: no slots available for %s\n", path);
        return NULL;
    }

    // Load the sound using wav64_load (returns pointer, handles allocation)
    loaded_sounds[slot].wav = wav64_load(path, NULL);
    if (!loaded_sounds[slot].wav) {
        debugf("audio: failed to load %s\n", path);
        return NULL;
    }

    strncpy(loaded_sounds[slot].path, path, sizeof(loaded_sounds[slot].path) - 1);
    loaded_sounds[slot].path[sizeof(loaded_sounds[slot].path) - 1] = '\0';
    loaded_sounds[slot].in_use = true;

    return &loaded_sounds[slot];
}

static int allocate_channel(int mix_channel)
{
    // Simple allocation: find any free channel
    // Could be extended to prefer channels or limit per mix channel
    for (int ch = 0; ch < AUDIO_MIXER_CHANNELS; ch++) {
        if (!channel_in_use[ch]) {
            return ch;
        }
    }
    return -1;
}

static void apply_channel_volume(int ch)
{
    int mix_ch = channel_mix_mapping[ch];
    if (mix_ch < 0) return;

    float vol = mix_volumes[mix_ch];
    mixer_ch_set_vol(ch, vol, vol);
}
