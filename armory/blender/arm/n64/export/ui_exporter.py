"""
UI Exporter - Handles canvas, fonts, and UI-related code generation for N64.

This module provides functions for detecting UI canvases, parsing themes,
and generating canvas and font C code files.
"""

import os
import json
import glob
import shutil

import arm.utils
import arm.log as log
from arm.n64.export.koui_theme_parser import KouiThemeParser


def detect_ui_canvas(exporter):
    """Detect and parse Koui canvas JSON files referenced by scenes.

    Only parses canvases that are actually attached to scenes via UI Canvas trait.
    Sets exporter.has_ui = True if any canvas with labels is found.
    Stores parsed data in exporter.ui_canvas_data for code generation.
    Also parses Koui theme files to extract font size and text color per label.

    Args:
        exporter: N64Exporter instance to update with UI state
    """
    bundled_dir = os.path.join(arm.utils.get_fp(), 'Bundled', 'koui_canvas')
    if not os.path.exists(bundled_dir):
        return

    # Collect canvas names referenced by scenes
    referenced_canvases = set()
    for scene_name, data in exporter.scene_data.items():
        canvas_name = data.get('canvas')
        if canvas_name:
            referenced_canvases.add(canvas_name)

    if not referenced_canvases:
        return  # No scenes use UI Canvas trait

    # Parse Koui theme files for style information
    _parse_koui_themes(exporter)

    for canvas_name in referenced_canvases:
        json_path = os.path.join(bundled_dir, f'{canvas_name}.json')
        if not os.path.exists(json_path):
            log.warn(f'UI Canvas "{canvas_name}" not found at {json_path}')
            continue

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                canvas_data = json.load(f)

            canvas_info = canvas_data.get('canvas', {})
            canvas_width = canvas_info.get('width')
            canvas_height = canvas_info.get('height')

            labels = []
            for scene in canvas_data.get('scenes', []):
                for elem in scene.get('elements', []):
                    if elem.get('type') == 'Label':
                        props = elem.get('properties', {})
                        tid = elem.get('tID', '_label')

                        # Get font size and text color from theme
                        font_size = 15
                        text_color = (221, 221, 221, 255)  # Default #dddddd

                        if exporter.theme_parser:
                            font_size = exporter.theme_parser.get_font_size(tid, 15)
                            color_hex = exporter.theme_parser.get_text_color(tid, '#dddddd')
                            text_color = KouiThemeParser.parse_hex_color(color_hex)

                        # Track unique font sizes needed
                        exporter.font_sizes.add(font_size)

                        # Get or create style_id for this color
                        style_id = _get_or_create_color_style(exporter, text_color)

                        label_data = {
                            'key': elem['key'],
                            'text': props.get('text', ''),
                            'pos_x': elem['posX'],
                            'pos_y': elem['posY'],
                            'width': elem['width'],
                            'height': elem['height'],
                            'anchor': elem['anchor'],
                            'visible': elem['visible'],
                            'align_h': props.get('alignmentHor', 0),
                            'align_v': props.get('alignmentVert', 0),
                            'tID': tid,
                            'font_size': font_size,
                            'text_color': text_color,
                            'style_id': style_id,
                        }
                        labels.append(label_data)

            if labels:
                exporter.ui_canvas_data[canvas_name] = {
                    'width': canvas_width,
                    'height': canvas_height,
                    'labels': labels
                }
                exporter.has_ui = True
                log.info(f'Found UI canvas: {canvas_name} with {len(labels)} label(s)')

        except Exception as e:
            log.warn(f'Failed to parse Koui canvas {json_path}: {e}')


def _parse_koui_themes(exporter):
    """Parse Koui base theme and project override files."""
    exporter.theme_parser = KouiThemeParser()

    # Base theme from Koui Subprojects
    base_theme_path = os.path.join(arm.utils.get_fp(), 'Subprojects', 'Koui', 'Assets', 'theme.ksn')
    if os.path.exists(base_theme_path):
        exporter.theme_parser.parse_file(base_theme_path)
        log.info(f'Parsed base Koui theme: {base_theme_path}')

    # Project override from Assets/koui_canvas
    override_path = os.path.join(arm.utils.get_fp(), 'Assets', 'koui_canvas', 'ui_override.ksn')
    if os.path.exists(override_path):
        exporter.theme_parser.parse_file(override_path)
        log.info(f'Parsed Koui theme override: {override_path}')

    # Resolve all inheritance chains
    exporter.theme_parser.resolve_all()


def _get_or_create_color_style(exporter, color: tuple) -> int:
    """Get or create a style_id for a given (r, g, b, a) color tuple."""
    if color in exporter.color_style_map:
        return exporter.color_style_map[color]

    style_id = len(exporter.color_style_map)
    exporter.color_style_map[color] = style_id
    return style_id


def write_canvas(exporter):
    """Generate canvas.c and canvas.h from templates using parsed Koui canvas data."""
    if not exporter.ui_canvas_data:
        return

    write_canvas_h(exporter)
    write_canvas_c(exporter)


def write_canvas_h(exporter):
    """Generate canvas.h from template with per-scene canvas support."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'canvas.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'canvas.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    # Get canvas dimensions from first canvas
    first_canvas = next(iter(exporter.ui_canvas_data.values()))
    canvas_width = first_canvas['width']
    canvas_height = first_canvas['height']

    # Build key-only label defines
    label_defines_lines = []
    total_label_count = 0
    seen_keys = {}

    for canvas_name, canvas in exporter.ui_canvas_data.items():
        label_defines_lines.append(f'// Canvas: {canvas_name} ({canvas["width"]}x{canvas["height"]})')
        label_idx = 0
        for label in canvas['labels']:
            safe_key = arm.utils.safesrc(label['key']).upper()
            define_name = f'UI_LABEL_{safe_key}'

            if safe_key in seen_keys:
                if seen_keys[safe_key] != label_idx:
                    log.warn(f'Label key "{label["key"]}" has different indices across canvases '
                             f'(index {seen_keys[safe_key]} vs {label_idx}). '
                             f'Traits using this label may not work correctly across scenes.')
            else:
                label_defines_lines.append(f'#define {define_name} {label_idx}')
                seen_keys[safe_key] = label_idx

            label_idx += 1
        total_label_count = max(total_label_count, label_idx)
        label_defines_lines.append('')

    output = tmpl_content.format(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        label_defines='\n'.join(label_defines_lines),
        label_count=total_label_count
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def write_canvas_c(exporter):
    """Generate canvas.c from template with per-scene canvas init functions."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'canvas.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'canvas.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    # Build per-canvas label definitions
    canvas_label_defs = {}
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        lines = []
        for label in canvas['labels']:
            text_escaped = label['text'].replace('\\', '\\\\').replace('"', '\\"')
            visible = 'true' if label['visible'] else 'false'
            style_id = label.get('style_id', 0)
            font_id = label.get('font_id', 0)
            baseline_offset = label.get('baseline_offset', 12)
            lines.append(f'    {{ "{text_escaped}", {label["pos_x"]}, {label["pos_y"]}, {label["width"]}, {label["height"]}, {baseline_offset}, {label["anchor"]}, {style_id}, {font_id}, {visible} }},')
        canvas_label_defs[canvas_name] = {
            'defs': '\n'.join(lines),
            'count': len(canvas['labels'])
        }

    # Build per-canvas static arrays
    canvas_arrays = []
    for canvas_name, data in canvas_label_defs.items():
        safe_canvas = arm.utils.safesrc(canvas_name).lower()
        count = data['count']
        if count > 0:
            canvas_arrays.append(f'// Canvas: {canvas_name}')
            canvas_arrays.append(f'#define {safe_canvas.upper()}_LABEL_COUNT {count}')
            canvas_arrays.append(f'static const UILabelDef g_{safe_canvas}_label_defs[{safe_canvas.upper()}_LABEL_COUNT] = {{')
            canvas_arrays.append(data['defs'])
            canvas_arrays.append('};')
            canvas_arrays.append('')

    # Build switch cases for scene_id -> canvas loading
    scene_switch_cases = []
    for scene_name, data in exporter.scene_data.items():
        canvas_name = data.get('canvas')
        if canvas_name and canvas_name in exporter.ui_canvas_data:
            safe_scene = arm.utils.safesrc(scene_name).upper()
            safe_canvas = arm.utils.safesrc(canvas_name).lower()
            scene_switch_cases.append(f'        case SCENE_{safe_scene}:')
            scene_switch_cases.append(f'            load_labels(g_{safe_canvas}_label_defs, {safe_canvas.upper()}_LABEL_COUNT);')
            scene_switch_cases.append('            break;')

    # Generate font style registration code
    style_registration_lines = []
    if exporter.exported_fonts:
        for font_key, font_info in sorted(exporter.exported_fonts.items(), key=lambda x: x[1]['font_id']):
            font_id = font_info['font_id']
            if font_id == 0:
                if exporter.color_style_map:
                    style_registration_lines.append(f'    // Font 0 styles (default font loaded above)')
                    for color, style_id in sorted(exporter.color_style_map.items(), key=lambda x: x[1]):
                        r, g, b, a = color
                        style_registration_lines.append(
                            f'    rdpq_font_style(font, {style_id}, &(rdpq_fontstyle_t){{ .color = RGBA32({r}, {g}, {b}, {a}) }});'
                        )
                continue

            style_registration_lines.append(f'    // Font {font_id}: {font_key}')
            style_registration_lines.append(f'    {{')
            style_registration_lines.append(f'        rdpq_font_t *font_{font_id} = fonts_get({font_id});')
            if exporter.color_style_map:
                style_registration_lines.append(f'        if (font_{font_id}) {{')
                for color, style_id in sorted(exporter.color_style_map.items(), key=lambda x: x[1]):
                    r, g, b, a = color
                    style_registration_lines.append(
                        f'            rdpq_font_style(font_{font_id}, {style_id}, &(rdpq_fontstyle_t){{ .color = RGBA32({r}, {g}, {b}, {a}) }});'
                    )
                style_registration_lines.append(f'        }}')
            style_registration_lines.append(f'    }}')

    if not style_registration_lines:
        style_registration_lines.append('    // No additional fonts or styles defined')

    total_labels = sum(d['count'] for d in canvas_label_defs.values())

    output = tmpl_content.format(
        canvas_label_arrays='\n'.join(canvas_arrays),
        scene_init_switch_cases='\n'.join(scene_switch_cases),
        total_label_count=total_labels,
        font_style_registration='\n'.join(style_registration_lines) if style_registration_lines else '        // No custom styles defined'
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def write_fonts(exporter):
    """Copy font files and generate fonts.c/fonts.h if UI is used.

    Creates separate .font64 files for each unique font size needed from the theme.
    """
    if not exporter.has_ui:
        return

    n64_assets = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
    os.makedirs(n64_assets, exist_ok=True)

    # Ensure we have at least the default size
    if not exporter.font_sizes:
        exporter.font_sizes.add(15)

    # Search order for fonts
    font_search_paths = [
        os.path.join(arm.utils.get_fp(), 'Assets'),
        os.path.join(arm.utils.get_fp(), 'Subprojects', 'Koui', 'Assets'),
    ]

    base_font_name = None
    base_font_path = None

    for search_path in font_search_paths:
        if os.path.exists(search_path):
            fonts = glob.glob(os.path.join(search_path, '**', '*.ttf'), recursive=True)
            for font_path in fonts:
                font_basename = os.path.splitext(os.path.basename(font_path))[0]
                if base_font_name is None:
                    base_font_name = font_basename
                    base_font_path = font_path
                    break
        if base_font_name:
            break

    if not base_font_name or not base_font_path:
        log.warn('No TTF fonts found for UI. Labels may not render correctly.')
        base_font_name = 'default'
        base_font_path = None

    # Create font entries for each unique size
    font_id = 0
    for size in sorted(exporter.font_sizes):
        font_key = f'{base_font_name}_{size}'

        if base_font_path:
            dst = os.path.join(n64_assets, f'{font_key}.ttf')
            if not os.path.exists(dst):
                shutil.copy(base_font_path, dst)
                log.info(f'Copied font: {font_key}.ttf (size {size})')

        exporter.exported_fonts[font_key] = {
            'name': base_font_name,
            'size': size,
            'font_id': font_id
        }
        exporter.font_id_map[size] = font_id
        font_id += 1
        log.info(f'Font registered: {font_key} (size {size}, id {font_id - 1})')

    write_fonts_c(exporter)
    write_fonts_h(exporter)
    _assign_font_ids_to_labels(exporter)


def write_fonts_c(exporter):
    """Generate fonts.c from template."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'fonts.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'fonts.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    lines = []
    sorted_fonts = sorted(exporter.exported_fonts.items(), key=lambda x: x[1]['font_id'])
    for font_key, font_info in sorted_fonts:
        lines.append(f'    "rom:/{font_key}.font64"')
    font_paths = ',\n'.join(lines)

    output = tmpl_content.format(
        font_paths=font_paths,
        font_count=len(exporter.exported_fonts)
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def write_fonts_h(exporter):
    """Generate fonts.h from template."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'ui', 'fonts.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'ui', 'fonts.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    lines = []
    sorted_fonts = sorted(exporter.exported_fonts.items(), key=lambda x: x[1]['font_id'])
    for font_key, font_info in sorted_fonts:
        enum_name = font_key.upper().replace('-', '_').replace(' ', '_')
        lines.append(f'    FONT_{enum_name} = {font_info["font_id"]},')
    font_enum_entries = '\n'.join(lines)

    output = tmpl_content.format(
        font_enum_entries=font_enum_entries,
        font_count=len(exporter.exported_fonts)
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def _assign_font_ids_to_labels(exporter):
    """Assign font_id and baseline_offset to each label based on its theme font size."""
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        for label in canvas.get('labels', []):
            kha_size = label.get('font_size', 15)
            font_id = exporter.font_id_map.get(kha_size, 0)
            label['font_id'] = font_id
            mkfont_size = max(8, int(kha_size * exporter.FONT_SIZE_SCALE))
            rendered_height = mkfont_size * 1.22
            baseline_offset = int(rendered_height * 0.80)
            label['baseline_offset'] = baseline_offset
            log.debug(f"Label '{label.get('key', 'unnamed')}': kha size {kha_size} -> mkfont {mkfont_size}, font_id {font_id}, baseline {baseline_offset}")


def generate_font_makefile_entries(exporter):
    """Generate Makefile entries for font conversion at different sizes.

    Returns:
        tuple: (font_targets_str, font_rules_str)
    """
    if not exporter.exported_fonts:
        return 'font_conv =', '# No fonts'

    targets = []
    rules = []

    for font_key, font_info in exporter.exported_fonts.items():
        font_name = font_info['name']
        kha_size = font_info['size']
        mkfont_size = max(8, int(kha_size * exporter.FONT_SIZE_SCALE))
        target = f'filesystem/{font_key}.font64'
        targets.append(target)

        rule = f'''{target}: assets/{font_key}.ttf
	@mkdir -p $(dir $@)
	@echo "    [FONT] $@ (kha size {kha_size} -> mkfont size {mkfont_size})"
	$(N64_MKFONT) $(MKFONT_FLAGS) --size {mkfont_size} -o filesystem "$<"'''
        rules.append(rule)

    font_targets = 'font_conv = ' + ' \\\n             '.join(targets)
    font_rules = '\n\n'.join(rules)

    return font_targets, font_rules
