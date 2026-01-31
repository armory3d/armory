"""
Audio Exporter - Handles audio file scanning, conversion, and configuration.

This module provides functions for exporting audio assets to N64 format,
including WAV/MP3 scanning, audioconv64 integration, and mix channel configuration.
"""

import os
import shutil
import json

import arm.utils
import arm.log as log
import arm.n64.utils as n64_utils


def scan_and_copy_audio(exporter):
    """Scan for audio files and copy them to the build assets folder.

    Searches for .wav and .mp3 files in the project's Assets folder
    (and subdirectories like audio/, music/, sfx/).
    Sets exporter.has_audio = True if any audio files are found.

    Args:
        exporter: N64Exporter instance to update with audio state
    """
    n64_assets = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
    os.makedirs(n64_assets, exist_ok=True)

    # Search for audio files in Assets folder and subdirectories
    assets_dir = os.path.join(arm.utils.get_fp(), 'Assets')
    audio_extensions = ('.wav', '.mp3', '.aiff')
    audio_files = []

    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for f in files:
                if f.lower().endswith(audio_extensions):
                    audio_files.append(os.path.join(root, f))

    if not audio_files:
        log.info('No audio files found in Assets folder.')
        return

    exporter.has_audio = True
    log.info(f'Found {len(audio_files)} audio file(s)')

    # Copy audio files to build/n64/assets
    for src_path in audio_files:
        filename = os.path.basename(src_path)
        # Create a safe filename (lowercase, replace spaces)
        safe_name = filename.lower().replace(' ', '_')
        dst_path = os.path.join(n64_assets, safe_name)

        # Determine if this is likely music (in music/ folder or long duration)
        # For now, simple heuristic: files in 'music' subfolder are music
        rel_path = os.path.relpath(src_path, assets_dir).lower()
        is_music = 'music' in rel_path

        if not os.path.exists(dst_path):
            shutil.copy(src_path, dst_path)
            log.info(f'Copied audio: {safe_name} (music={is_music})')

        # Store audio info (without extension, as audioconv64 changes it)
        audio_name = os.path.splitext(safe_name)[0]
        exporter.exported_audio[audio_name] = {
            'source_path': src_path,
            'dest_name': safe_name,
            'is_music': is_music,
            'loop': is_music  # Music loops by default
        }

    # Copy audio module source files
    n64_utils.copy_dir('audio', 'src')

    # Generate audio_config.h from template
    write_audio_config(exporter)


def write_audio_config(exporter):
    """Generate audio_config.h from template with mix channel configuration.

    Parses trait IR files to find Aura.mixChannels usage and generates
    the appropriate AUDIO_MIX_* constants. Falls back to default channels
    if no audio usage is detected.

    Args:
        exporter: N64Exporter instance (used for IR access)
    """
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'audio', 'audio_config.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'audio', 'audio_config.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    # Collect mix channel names from trait IR
    mix_channel_names = collect_mix_channels_from_ir()

    # Ensure we have at least the default Aura channels
    default_channels = ['master', 'music', 'fx']
    for ch in default_channels:
        if ch not in mix_channel_names:
            mix_channel_names.append(ch)

    # Generate mix channel defines: AUDIO_MIX_MASTER, AUDIO_MIX_MUSIC, etc.
    mix_channel_defines = []
    for i, name in enumerate(mix_channel_names):
        const_name = f'AUDIO_MIX_{name.upper()}'
        mix_channel_defines.append(f'#define {const_name} {i}')

    output = tmpl_content.format(
        audio_mixer_channels=8,  # Total hardware channels
        audio_mix_channel_count=len(mix_channel_names),
        mix_channel_defines='\n'.join(mix_channel_defines)
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def collect_mix_channels_from_ir():
    """Scan trait IR files to find Aura.mixChannels usage.

    Returns:
        list: List of mix channel names found (e.g., ['music', 'sfx'])
    """
    mix_channels = []
    ir_dir = os.path.join(arm.utils.build_dir(), 'n64', 'trait_ir')

    if not os.path.exists(ir_dir):
        return mix_channels

    # Scan all IR JSON files for audio_mix_volume nodes
    for filename in os.listdir(ir_dir):
        if not filename.endswith('.json'):
            continue

        ir_path = os.path.join(ir_dir, filename)
        try:
            with open(ir_path, 'r', encoding='utf-8') as f:
                ir_data = json.load(f)

            # Recursively search for audio-related IR nodes
            _find_mix_channels_in_ir(ir_data, mix_channels)
        except (json.JSONDecodeError, IOError):
            continue

    return mix_channels


def _find_mix_channels_in_ir(node, channels):
    """Recursively search IR for mix channel references.

    Args:
        node: IR node (dict or list) to search
        channels: List to append found channel names to
    """
    if isinstance(node, dict):
        # Check for audio_mix_volume type with channel prop
        if node.get('type') == 'audio_mix_volume':
            props = node.get('props', {})
            channel = props.get('channel', '')
            # Extract channel name from AUDIO_MIX_NAME format
            if channel.startswith('AUDIO_MIX_'):
                name = channel[10:].lower()  # Remove prefix and lowercase
                if name and name not in channels:
                    channels.append(name)

        # Recurse into all values
        for v in node.values():
            _find_mix_channels_in_ir(v, channels)

    elif isinstance(node, list):
        for item in node:
            _find_mix_channels_in_ir(item, channels)


def generate_audio_makefile_entries(exported_audio):
    """Generate Makefile entries for audio conversion.

    Uses audioconv64 to convert .wav/.mp3 files to .wav64 format.
    All audio uses VADPCM compression (--wav-compress 1) for stability with t3d.
    Opus (level 3) has known RSP conflicts with t3d rendering on real hardware.

    Args:
        exported_audio: Dict of {audio_name: {dest_name, is_music, loop, ...}}

    Returns:
        tuple: (audio_targets_str, audio_rules_str)
    """
    if not exported_audio:
        return 'audio_conv =', '# No audio'

    targets = []
    rules = []

    for audio_name, audio_info in exported_audio.items():
        dest_name = audio_info['dest_name']
        is_music = audio_info['is_music']

        # Target: filesystem/audio_name.wav64
        target = f'filesystem/{audio_name}.wav64'
        targets.append(target)

        # Use VADPCM (level 1) for all audio - stable with t3d
        # Opus (level 3) causes RSP conflicts with t3d rendering
        if is_music:
            compress_flag = '--wav-compress 1 --wav-loop true'
        else:
            compress_flag = '--wav-compress 1'

        rule = f'''{target}: assets/{dest_name}
	@mkdir -p $(dir $@)
	@echo "    [AUDIO] $@"
	@$(N64_AUDIOCONV) {compress_flag} -o filesystem "$<"'''
        rules.append(rule)

    audio_targets = 'audio_conv = ' + ' \\\n             '.join(targets)
    audio_rules = '\n\n'.join(rules)

    return audio_targets, audio_rules
