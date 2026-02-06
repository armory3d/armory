#pragma once

// Total number of mixer channels (hardware channels for libdragon)
#define AUDIO_MIXER_CHANNELS 8

// Number of mix channels defined in Aura
#define AUDIO_MIX_CHANNEL_COUNT 3

// Mix channel indices (generated from Aura.mixChannels keys)
#define AUDIO_MIX_MASTER 0
#define AUDIO_MIX_MUSIC  1
#define AUDIO_MIX_SFX    2
