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


# =============================================================================
# Constants
# =============================================================================

# Anchor enum values (matches Koui)
ANCHOR_TOP_LEFT = 0
ANCHOR_TOP_CENTER = 1
ANCHOR_TOP_RIGHT = 2
ANCHOR_MIDDLE_LEFT = 3
ANCHOR_MIDDLE_CENTER = 4
ANCHOR_MIDDLE_RIGHT = 5
ANCHOR_BOTTOM_LEFT = 6
ANCHOR_BOTTOM_CENTER = 7
ANCHOR_BOTTOM_RIGHT = 8

# Default UI values
DEFAULT_FONT_SIZE = 15
DEFAULT_TEXT_COLOR = (221, 221, 221, 255)  # #dddddd


def detect_ui_canvas(exporter):
    """Detect and parse Koui canvas JSON files referenced by scenes.

    Only parses canvases that are actually attached to scenes via UI Canvas trait.
    Sets exporter.has_ui = True if any canvas with labels or images is found.
    Stores parsed data in exporter.ui_canvas_data for code generation.
    Also parses Koui theme files to extract font size and text color per label.

    Layouts (RowLayout, ColLayout) are flattened at export time - their children
    are extracted with pre-computed absolute positions for N64's fixed resolution.

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
            canvas_width = canvas_info.get('width', 320)
            canvas_height = canvas_info.get('height', 240)

            labels = []
            images = []
            groups = []       # Groups with their child indices
            elements = []     # Unified elements array (maps Haxe index to image/group)

            for scene in canvas_data.get('scenes', []):
                scene_elements = scene.get('elements', [])

                # Build element lookup by key and parent-child relationships
                elem_by_key = {e['key']: e for e in scene_elements}
                children_by_parent = {}
                root_elements = []

                for elem in scene_elements:
                    parent_key = elem.get('parentKey')
                    if parent_key:
                        if parent_key not in children_by_parent:
                            children_by_parent[parent_key] = []
                        children_by_parent[parent_key].append(elem)
                    else:
                        root_elements.append(elem)

                # Process root elements recursively, flattening layouts
                # but tracking groups and unified elements array
                for elem in root_elements:
                    _flatten_element(
                        exporter, elem, elem_by_key, children_by_parent,
                        canvas_width, canvas_height,
                        0, 0,  # parent_abs_x, parent_abs_y
                        labels, images, groups, elements
                    )

            if labels or images or groups:
                exporter.ui_canvas_data[canvas_name] = {
                    'width': canvas_width,
                    'height': canvas_height,
                    'labels': labels,
                    'images': images,
                    'groups': groups,
                    'elements': elements
                }
                exporter.has_ui = True
                log.info(f'Found UI canvas: {canvas_name} with {len(labels)} label(s), {len(images)} image(s), {len(groups)} group(s), {len(elements)} element(s)')

        except Exception as e:
            log.warn(f'Failed to parse Koui canvas {json_path}: {e}')


def _calc_anchor_position(pos_x, pos_y, width, height, anchor, container_width, container_height):
    """Calculate absolute position based on anchor within a container.

    Args:
        pos_x, pos_y: Element's relative position
        width, height: Element's dimensions
        anchor: Anchor enum value (0-8)
        container_width, container_height: Parent container dimensions

    Returns:
        (abs_x, abs_y): Absolute position within container
    """
    # Calculate X based on anchor
    if anchor in (ANCHOR_TOP_LEFT, ANCHOR_MIDDLE_LEFT, ANCHOR_BOTTOM_LEFT):
        abs_x = pos_x
    elif anchor in (ANCHOR_TOP_CENTER, ANCHOR_MIDDLE_CENTER, ANCHOR_BOTTOM_CENTER):
        abs_x = (container_width // 2) - (width // 2) + pos_x
    elif anchor in (ANCHOR_TOP_RIGHT, ANCHOR_MIDDLE_RIGHT, ANCHOR_BOTTOM_RIGHT):
        abs_x = container_width - width + pos_x
    else:
        abs_x = pos_x

    # Calculate Y based on anchor
    if anchor in (ANCHOR_TOP_LEFT, ANCHOR_TOP_CENTER, ANCHOR_TOP_RIGHT):
        abs_y = pos_y
    elif anchor in (ANCHOR_MIDDLE_LEFT, ANCHOR_MIDDLE_CENTER, ANCHOR_MIDDLE_RIGHT):
        abs_y = (container_height // 2) - (height // 2) + pos_y
    elif anchor in (ANCHOR_BOTTOM_LEFT, ANCHOR_BOTTOM_CENTER, ANCHOR_BOTTOM_RIGHT):
        abs_y = container_height - height + pos_y
    else:
        abs_y = pos_y

    return abs_x, abs_y


# =============================================================================
# Element Flatten Helpers
# =============================================================================

def _build_full_path(parent_path: str, key: str) -> str:
    """Build full element path like 'parent/child' for Koui-style access."""
    if parent_path:
        return f"{parent_path}/{key}"
    return key


def _create_group_with_children(exporter, elem, children, final_x, final_y,
                                 elem_by_key, children_by_parent,
                                 labels, images, groups, elements,
                                 parent_path: str = ""):
    """Create a group element and process its children, tracking indices.

    Args:
        exporter: N64Exporter instance
        elem: Parent element dict
        children: List of child elements
        final_x, final_y: Absolute position
        elem_by_key, children_by_parent: Lookup dicts
        labels, images, groups, elements: Output lists (modified in place)
        parent_path: Path to parent for building full key paths
    """
    group_index = len(groups)
    elem_key = elem.get('key')
    full_path = _build_full_path(parent_path, elem_key)

    group_data = {
        'key': full_path,  # Use full path as key
        'visible': elem.get('visible', True),
        'child_image_indices': [],
        'child_label_indices': [],
    }

    # Add to elements array as a group
    elements.append({'type': 'group', 'index': group_index})

    container_width = elem['width']
    container_height = elem['height']

    # Process children - track their indices for the group
    for child in children:
        img_start = len(images)
        lbl_start = len(labels)
        _flatten_element(
            exporter, child, elem_by_key, children_by_parent,
            container_width, container_height,
            final_x, final_y,
            labels, images, groups, elements,
            is_root=False,
            parent_path=full_path  # Pass current path for children
        )
        # Track which images/labels were added
        for i in range(img_start, len(images)):
            group_data['child_image_indices'].append(i)
        for i in range(lbl_start, len(labels)):
            group_data['child_label_indices'].append(i)

    groups.append(group_data)


def _handle_row_col_layout(exporter, elem, elem_type, children, final_x, final_y,
                            elem_by_key, children_by_parent,
                            labels, images, groups, elements, is_root,
                            parent_path: str = ""):
    """Handle RowLayout and ColLayout - process children in cells.

    These layouts are treated as groups so their visibility can be toggled.
    """
    if not children:
        return

    elem_key = elem.get('key')
    full_path = _build_full_path(parent_path, elem_key)

    # Create a group for this layout so visibility can be controlled
    group_index = len(groups)
    group_data = {
        'key': full_path,
        'visible': elem.get('visible', True),
        'child_image_indices': [],
        'child_label_indices': [],
    }

    if is_root:
        elements.append({'type': 'group', 'index': group_index})

    layout_width = elem['width']
    layout_height = elem['height']
    num_children = len(children)

    if elem_type == 'RowLayout':
        cell_width = layout_width
        cell_height = layout_height // num_children
    else:  # ColLayout
        cell_width = layout_width // num_children
        cell_height = layout_height

    for idx, child in enumerate(children):
        if elem_type == 'RowLayout':
            cell_x, cell_y = 0, cell_height * idx
        else:
            cell_x, cell_y = cell_width * idx, 0

        img_start = len(images)
        lbl_start = len(labels)
        _flatten_element(
            exporter, child, elem_by_key, children_by_parent,
            cell_width, cell_height,
            final_x + cell_x, final_y + cell_y,
            labels, images, groups, elements,
            is_root=False,
            parent_path=full_path
        )
        # Track child indices for group
        for i in range(img_start, len(images)):
            group_data['child_image_indices'].append(i)
        for i in range(lbl_start, len(labels)):
            group_data['child_label_indices'].append(i)

    groups.append(group_data)


def _handle_grid_layout(exporter, elem, children, final_x, final_y,
                         elem_by_key, children_by_parent,
                         labels, images, groups, elements, is_root,
                         parent_path: str = ""):
    """Handle GridLayout - place children in grid cells.

    GridLayout is treated as a group so its visibility can be toggled.
    """
    if not children:
        return

    elem_key = elem.get('key')
    full_path = _build_full_path(parent_path, elem_key)

    # Create a group for this layout
    group_index = len(groups)
    group_data = {
        'key': full_path,
        'visible': elem.get('visible', True),
        'child_image_indices': [],
        'child_label_indices': [],
    }

    if is_root:
        elements.append({'type': 'group', 'index': group_index})

    layout_width = elem['width']
    layout_height = elem['height']
    props = elem.get('properties', {})

    num_rows = props.get('rows', 1)
    num_cols = props.get('cols', 1)

    cell_width = layout_width // num_cols if num_cols > 0 else layout_width
    cell_height = layout_height // num_rows if num_rows > 0 else layout_height

    for idx, child in enumerate(children):
        row = idx // num_cols
        col = idx % num_cols
        cell_x = cell_width * col
        cell_y = cell_height * row

        img_start = len(images)
        lbl_start = len(labels)
        _flatten_element(
            exporter, child, elem_by_key, children_by_parent,
            cell_width, cell_height,
            final_x + cell_x, final_y + cell_y,
            labels, images, groups, elements,
            is_root=False,
            parent_path=full_path
        )
        # Track child indices for group
        for i in range(img_start, len(images)):
            group_data['child_image_indices'].append(i)
        for i in range(lbl_start, len(labels)):
            group_data['child_label_indices'].append(i)

    groups.append(group_data)


def _handle_label(exporter, elem, final_x, final_y, labels, parent_path: str = ""):
    """Handle Label element - extract text, font, and color info."""
    props = elem.get('properties', {})
    tid = elem.get('tID', '_label')

    font_size = DEFAULT_FONT_SIZE
    text_color = DEFAULT_TEXT_COLOR

    if exporter.theme_parser:
        font_size = exporter.theme_parser.get_font_size(tid, DEFAULT_FONT_SIZE)
        color_hex = exporter.theme_parser.get_text_color(tid, '#dddddd')
        text_color = KouiThemeParser.parse_hex_color(color_hex)

    exporter.font_sizes.add(font_size)
    style_id = _get_or_create_color_style(exporter, text_color)

    # Build full path for key
    full_path = _build_full_path(parent_path, elem['key'])

    label_data = {
        'key': full_path,  # Use full path as key
        'text': props.get('text', ''),
        'pos_x': final_x,
        'pos_y': final_y,
        'width': elem['width'],
        'height': elem['height'],
        'anchor': ANCHOR_TOP_LEFT,
        'visible': elem.get('visible', True),
        'align_h': props.get('alignmentHor', 0),
        'align_v': props.get('alignmentVert', 0),
        'tID': tid,
        'font_size': font_size,
        'text_color': text_color,
        'style_id': style_id,
    }
    labels.append(label_data)


def _handle_image(exporter, elem, final_x, final_y, images, elements, is_root, parent_path: str = ""):
    """Handle ImagePanel element - track image for copying."""
    props = elem.get('properties', {})
    image_name = props.get('imageName', '')

    if not image_name:
        return

    if not hasattr(exporter, 'ui_images'):
        exporter.ui_images = set()
    exporter.ui_images.add(image_name)

    # Build full path for key
    full_path = _build_full_path(parent_path, elem['key'])

    image_index = len(images)
    image_data = {
        'key': full_path,  # Use full path as key
        'image_name': image_name,
        'pos_x': final_x,
        'pos_y': final_y,
        'width': elem['width'],
        'height': elem['height'],
        'anchor': ANCHOR_TOP_LEFT,
        'visible': elem.get('visible', True),
        'scale': props.get('scale', False),
    }
    images.append(image_data)

    if is_root:
        elements.append({'type': 'image', 'index': image_index})


# =============================================================================
# Main Flatten Function
# =============================================================================

def _flatten_element(exporter, elem, elem_by_key, children_by_parent,
                     container_width, container_height,
                     parent_abs_x, parent_abs_y,
                     labels, images, groups, elements,
                     is_root=True,
                     parent_path: str = ""):
    """Recursively flatten an element, computing absolute positions.

    Layout elements (RowLayout, ColLayout) are exported as groups so their
    visibility can be toggled. Their children are processed with adjusted positions.

    Groups (containers with children) are tracked for parent-child visibility.
    The elements array provides unified Haxe-compatible indexing.

    parent_path is used to build full keys like "parent/child" for Koui-style access.
    """
    elem_type = elem.get('type')
    elem_key = elem.get('key')
    anchor = elem.get('anchor', ANCHOR_TOP_LEFT)

    # Calculate final absolute position
    elem_abs_x, elem_abs_y = _calc_anchor_position(
        elem['posX'], elem['posY'],
        elem['width'], elem['height'],
        anchor,
        container_width, container_height
    )
    final_x = parent_abs_x + elem_abs_x
    final_y = parent_abs_y + elem_abs_y

    children = children_by_parent.get(elem_key, [])
    has_children = len(children) > 0

    # Dispatch to type-specific handlers
    if elem_type in ('RowLayout', 'ColLayout'):
        _handle_row_col_layout(exporter, elem, elem_type, children, final_x, final_y,
                                elem_by_key, children_by_parent,
                                labels, images, groups, elements, is_root,
                                parent_path=parent_path)
        return

    if elem_type == 'GridLayout':
        _handle_grid_layout(exporter, elem, children, final_x, final_y,
                             elem_by_key, children_by_parent,
                             labels, images, groups, elements, is_root,
                             parent_path=parent_path)
        return

    if elem_type == 'AnchorPane':
        if has_children:
            # AnchorPane with children - create group for visibility control
            _create_group_with_children(exporter, elem, children, final_x, final_y,
                                         elem_by_key, children_by_parent,
                                         labels, images, groups, elements,
                                         parent_path=parent_path)
        return

    if elem_type == 'Label':
        _handle_label(exporter, elem, final_x, final_y, labels, parent_path=parent_path)
        return

    if elem_type == 'ImagePanel':
        _handle_image(exporter, elem, final_x, final_y, images, elements, is_root, parent_path=parent_path)
        return

    # Generic container with children - create a group
    if has_children and is_root:
        _create_group_with_children(exporter, elem, children, final_x, final_y,
                                     elem_by_key, children_by_parent,
                                     labels, images, groups, elements,
                                     parent_path=parent_path)
        return

    # Non-root elements with children - just process children
    if has_children:
        # Build path for children
        current_path = _build_full_path(parent_path, elem_key)
        for child in children:
            _flatten_element(
                exporter, child, elem_by_key, children_by_parent,
                elem['width'], elem['height'],
                final_x, final_y,
                labels, images, groups, elements,
                is_root=False,
                parent_path=current_path
            )


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
    copy_canvas_images(exporter)


def copy_canvas_images(exporter):
    """Copy PNG images referenced by canvas ImagePanel elements to build/n64/assets.

    Images are searched recursively in the project Assets/ folder.
    The Makefile converts them to .sprite files.
    """
    if not hasattr(exporter, 'ui_images') or not exporter.ui_images:
        return

    n64_assets = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
    os.makedirs(n64_assets, exist_ok=True)

    # Build index of all PNG files in Assets folder (recursive)
    assets_dir = os.path.join(arm.utils.get_fp(), 'Assets')
    image_index = {}  # basename (without ext) -> full path

    if os.path.exists(assets_dir):
        for root, dirs, files in os.walk(assets_dir):
            for f in files:
                if f.lower().endswith('.png'):
                    basename = os.path.splitext(f)[0]
                    image_index[basename] = os.path.join(root, f)
                    # Also index lowercase version for case-insensitive matching
                    image_index[basename.lower()] = os.path.join(root, f)

    copied_count = 0
    for image_name in exporter.ui_images:
        # Try exact match first, then lowercase
        png_path = image_index.get(image_name) or image_index.get(image_name.lower())

        if png_path and os.path.exists(png_path):
            # Create safe filename (lowercase, no spaces)
            safe_name = image_name.lower().replace(' ', '_')
            dst_path = os.path.join(n64_assets, f'{safe_name}.png')

            if not os.path.exists(dst_path):
                shutil.copy(png_path, dst_path)
                log.info(f'Copied canvas image: {safe_name}.png')
                copied_count += 1
        else:
            log.warn(f'Canvas image not found: {image_name}.png')

    if copied_count > 0:
        log.info(f'Copied {copied_count} canvas image(s) to build/n64/assets/')


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
        for label in canvas.get('labels', []):
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

    # Build key-only image defines
    image_defines_lines = []
    total_image_count = 0
    seen_image_keys = {}

    for canvas_name, canvas in exporter.ui_canvas_data.items():
        images = canvas.get('images', [])
        if images:
            image_defines_lines.append(f'// Canvas: {canvas_name} images')
            image_idx = 0
            for image in images:
                safe_key = arm.utils.safesrc(image['key']).upper()
                define_name = f'UI_IMAGE_{safe_key}'

                if safe_key in seen_image_keys:
                    if seen_image_keys[safe_key] != image_idx:
                        log.warn(f'Image key "{image["key"]}" has different indices across canvases '
                                 f'(index {seen_image_keys[safe_key]} vs {image_idx}). '
                                 f'Traits using this image may not work correctly across scenes.')
                else:
                    image_defines_lines.append(f'#define {define_name} {image_idx}')
                    seen_image_keys[safe_key] = image_idx

                image_idx += 1
            total_image_count = max(total_image_count, image_idx)
            image_defines_lines.append('')

    # Build group defines (for containers with children)
    group_defines_lines = []
    total_group_count = 0
    seen_group_keys = {}

    for canvas_name, canvas in exporter.ui_canvas_data.items():
        groups = canvas.get('groups', [])
        if groups:
            group_defines_lines.append(f'// Canvas: {canvas_name} groups')
            group_idx = 0
            for group in groups:
                safe_key = arm.utils.safesrc(group['key']).upper()
                define_name = f'UI_GROUP_{safe_key}'

                if safe_key not in seen_group_keys:
                    group_defines_lines.append(f'#define {define_name} {group_idx}')
                    seen_group_keys[safe_key] = group_idx

                group_idx += 1
            total_group_count = max(total_group_count, group_idx)
            group_defines_lines.append('')

    # Count total elements (unified Haxe array)
    total_element_count = 0
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        elements = canvas.get('elements', [])
        total_element_count = max(total_element_count, len(elements))

    output = tmpl_content.format(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        label_defines='\n'.join(label_defines_lines),
        label_count=total_label_count,
        image_defines='\n'.join(image_defines_lines),
        image_count=total_image_count,
        group_defines='\n'.join(group_defines_lines) if group_defines_lines else '// No groups',
        group_count=total_group_count,
        element_count=total_element_count
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
        for label in canvas.get('labels', []):
            text_escaped = label['text'].replace('\\', '\\\\').replace('"', '\\"')
            visible = 'true' if label['visible'] else 'false'
            style_id = label.get('style_id', 0)
            font_id = label.get('font_id', 0)
            baseline_offset = label.get('baseline_offset', 12)
            lines.append(f'    {{ "{text_escaped}", {label["pos_x"]}, {label["pos_y"]}, {label["width"]}, {label["height"]}, {baseline_offset}, {label["anchor"]}, {style_id}, {font_id}, {visible} }},')
        canvas_label_defs[canvas_name] = {
            'defs': '\n'.join(lines),
            'count': len(canvas.get('labels', []))
        }

    # Build per-canvas image definitions
    canvas_image_defs = {}
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        lines = []
        for image in canvas.get('images', []):
            safe_name = image['image_name'].lower().replace(' ', '_')
            visible = 'true' if image['visible'] else 'false'
            scale = 'true' if image.get('scale', False) else 'false'
            lines.append(f'    {{ "{safe_name}", {image["pos_x"]}, {image["pos_y"]}, {image["width"]}, {image["height"]}, {image["anchor"]}, {scale}, {visible}, NULL }},')
        canvas_image_defs[canvas_name] = {
            'defs': '\n'.join(lines),
            'count': len(canvas.get('images', []))
        }

    # Build per-canvas static arrays (labels)
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

    # Build per-canvas static arrays (images)
    canvas_image_arrays = []
    for canvas_name, data in canvas_image_defs.items():
        safe_canvas = arm.utils.safesrc(canvas_name).lower()
        count = data['count']
        if count > 0:
            canvas_image_arrays.append(f'// Canvas: {canvas_name} images')
            canvas_image_arrays.append(f'#define {safe_canvas.upper()}_IMAGE_COUNT {count}')
            canvas_image_arrays.append(f'static UIImageDef g_{safe_canvas}_image_defs[{safe_canvas.upper()}_IMAGE_COUNT] = {{')
            canvas_image_arrays.append(data['defs'])
            canvas_image_arrays.append('};')
            canvas_image_arrays.append('')

    # Build per-canvas static arrays (groups)
    canvas_group_arrays = []
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        groups = canvas.get('groups', [])
        if groups:
            safe_canvas = arm.utils.safesrc(canvas_name).lower()
            canvas_group_arrays.append(f'// Canvas: {canvas_name} groups')
            canvas_group_arrays.append(f'#define {safe_canvas.upper()}_GROUP_COUNT {len(groups)}')
            canvas_group_arrays.append(f'static const UIGroupDef g_{safe_canvas}_group_defs[{safe_canvas.upper()}_GROUP_COUNT] = {{')
            for group in groups:
                # Format child indices arrays (pad to 8 elements each)
                img_indices = group.get('child_image_indices', [])
                lbl_indices = group.get('child_label_indices', [])
                # Build properly padded arrays
                img_padded = list(img_indices[:8]) + [0] * (8 - min(len(img_indices), 8))
                lbl_padded = list(lbl_indices[:8]) + [0] * (8 - min(len(lbl_indices), 8))
                img_str = ', '.join(str(i) for i in img_padded)
                lbl_str = ', '.join(str(i) for i in lbl_padded)
                visible = 'true' if group.get('visible', True) else 'false'
                canvas_group_arrays.append(f'    {{ {{ {img_str} }}, {{ {lbl_str} }}, {len(img_indices)}, {len(lbl_indices)}, {visible} }},')
            canvas_group_arrays.append('};')
            canvas_group_arrays.append('')

    # Build per-canvas static arrays (elements - Haxe elements[] mapping)
    canvas_element_arrays = []
    for canvas_name, canvas in exporter.ui_canvas_data.items():
        elements = canvas.get('elements', [])
        if elements:
            safe_canvas = arm.utils.safesrc(canvas_name).lower()
            canvas_element_arrays.append(f'// Canvas: {canvas_name} elements (Haxe elements[] mapping)')
            canvas_element_arrays.append(f'#define {safe_canvas.upper()}_ELEMENT_COUNT {len(elements)}')
            canvas_element_arrays.append(f'static const UIElementDef g_{safe_canvas}_element_defs[{safe_canvas.upper()}_ELEMENT_COUNT] = {{')
            for elem in elements:
                elem_type = elem.get('type', 'image')
                elem_index = elem.get('index', 0)
                if elem_type == 'group':
                    canvas_element_arrays.append(f'    {{ UI_ELEM_GROUP, {elem_index} }},')
                else:  # image
                    canvas_element_arrays.append(f'    {{ UI_ELEM_IMAGE, {elem_index} }},')
            canvas_element_arrays.append('};')
            canvas_element_arrays.append('')

    # Build switch cases for scene_id -> canvas loading
    scene_switch_cases = []
    for scene_name, data in exporter.scene_data.items():
        canvas_name = data.get('canvas')
        if canvas_name and canvas_name in exporter.ui_canvas_data:
            safe_scene = arm.utils.safesrc(scene_name).upper()
            safe_canvas = arm.utils.safesrc(canvas_name).lower()
            canvas = exporter.ui_canvas_data[canvas_name]
            label_count = len(canvas.get('labels', []))
            image_count = len(canvas.get('images', []))
            group_count = len(canvas.get('groups', []))
            element_count = len(canvas.get('elements', []))

            scene_switch_cases.append(f'        case SCENE_{safe_scene}:')
            if label_count > 0:
                scene_switch_cases.append(f'            load_labels(g_{safe_canvas}_label_defs, {safe_canvas.upper()}_LABEL_COUNT);')
            if image_count > 0:
                scene_switch_cases.append(f'            load_images(g_{safe_canvas}_image_defs, {safe_canvas.upper()}_IMAGE_COUNT);')
            if group_count > 0:
                scene_switch_cases.append(f'            load_groups(g_{safe_canvas}_group_defs, {safe_canvas.upper()}_GROUP_COUNT);')
            if element_count > 0:
                scene_switch_cases.append(f'            load_elements(g_{safe_canvas}_element_defs, {safe_canvas.upper()}_ELEMENT_COUNT);')
            # Apply initial group visibility to children (must be after all loading)
            if group_count > 0:
                scene_switch_cases.append(f'            apply_initial_group_visibility();')
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
    total_images = sum(d['count'] for d in canvas_image_defs.values())

    output = tmpl_content.format(
        canvas_label_arrays='\n'.join(canvas_arrays),
        canvas_image_arrays='\n'.join(canvas_image_arrays),
        canvas_group_arrays='\n'.join(canvas_group_arrays) if canvas_group_arrays else '// No groups defined',
        canvas_element_arrays='\n'.join(canvas_element_arrays) if canvas_element_arrays else '// No elements defined',
        scene_init_switch_cases='\n'.join(scene_switch_cases),
        total_label_count=total_labels,
        total_image_count=total_images,
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
