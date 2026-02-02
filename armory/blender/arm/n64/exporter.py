"""
N64 Exporter - Orchestrates the N64 export pipeline.

This is the main entry point for exporting Armory projects to N64.
It coordinates the various export modules to generate C code, assets,
and build the final ROM.

Export Modules:
- mesh_exporter: GLTF mesh export
- scene_exporter: Scene data extraction and C generation
- traits_exporter: Trait and autoload C code generation
- ui_exporter: Canvas, fonts, and UI code generation
- physics_exporter: Physics engine file generation
- audio_exporter: Audio asset processing
- build_runner: Makefile generation and build execution
"""

import os
import bpy

import arm
import arm.utils
import arm.log as log

# Use direct module imports to avoid circular imports through arm.n64.__init__
import arm.n64.codegen as codegen
import arm.n64.utils as n64_utils

# Import export submodules directly (not through arm.n64.export.__init__)
from arm.n64.export import mesh_exporter
from arm.n64.export import scene_exporter
from arm.n64.export import traits_exporter
from arm.n64.export import ui_exporter
from arm.n64.export import physics_exporter
from arm.n64.export import audio_exporter
from arm.n64.export import build_runner
from arm.n64.export import linked_export

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    log = arm.reload_module(log)
    codegen = arm.reload_module(codegen)
    n64_utils = arm.reload_module(n64_utils)
else:
    arm.enable_reload(__name__)


class N64Exporter:
    """N64 Exporter - Orchestrates export of Armory scenes to N64 C code."""

    # Font size conversion factor: Kha pixel height -> mkfont point size
    FONT_SIZE_SCALE = 0.82

    def __init__(self):
        # Export state
        self.scene_data = {}
        self.exported_meshes = {}
        self.exported_fonts = {}
        self.font_sizes = set()
        self.trait_info = {}
        self.exported_audio = {}
        self.autoload_info = {}
        self.linked_objects = []  # (local_obj_name, original_mesh_name) tuples

        # Feature flags (set during export)
        self.has_physics = False
        self.has_ui = False
        self.has_audio = False

        # UI state
        self.ui_canvas_data = {}
        self.theme_parser = None
        self.color_style_map = {}
        self.font_id_map = {}

    # -------------------------------------------------------------------------
    # Class Methods (Entry Points)
    # -------------------------------------------------------------------------

    @classmethod
    def export_project(cls):
        """Export project without building."""
        exporter = cls()
        exporter.export()

    @classmethod
    def publish_project(cls):
        """Export and build project to ROM."""
        exporter = cls()
        exporter.publish()

    @classmethod
    def play_project(cls):
        """Export, build, and run in emulator."""
        exporter = cls()
        exporter.play()

    # -------------------------------------------------------------------------
    # Main Export Pipeline
    # -------------------------------------------------------------------------

    def export(self):
        """Run the complete export pipeline."""
        log.info('Starting N64 export...')

        # Load trait metadata from Haxe macro output
        self.trait_info = codegen.get_trait_info()
        if not self.trait_info.get('traits'):
            log.warn("No traits found in n64_traits.json. Make sure arm_target_n64 is defined during build.")

        # Phase 0: Prepare linked objects (create temp local copies for Fast64)
        self.linked_objects = linked_export.prepare_linked_for_export()
        if self.linked_objects:
            log.info(f'Prepared {len(self.linked_objects)} linked object(s) for export')

        try:
            # Phase 1: Prepare materials and directories
            self._convert_materials_to_f3d()
            self._make_directories()

            # Phase 2: Export meshes to GLTF/T3D
            mesh_exporter.export_meshes(self)

            # Phase 3: Build scene data (sets has_physics flag)
            for scene in bpy.data.scenes:
                if scene.library:
                    continue
                # Skip temp scene used for linked object export
                if linked_export.is_temp_scene(scene):
                    continue
                scene_exporter.build_scene_data(self, scene)

            # Compute static flags after trait_info is loaded
            n64_utils.compute_static_flags(self.scene_data, self.trait_info)

            # Phase 4: Detect UI canvas (sets has_ui flag)
            ui_exporter.detect_ui_canvas(self)

            # Phase 5: Generate trait code (may set has_ui/has_physics from traits)
            features = traits_exporter.write_traits(self)
            if features.get('has_ui'):
                self.has_ui = True
            if features.get('has_physics'):
                self.has_physics = True

            # Phase 6: Generate autoload code (may set has_audio)
            autoload_features = traits_exporter.write_autoloads(self)
            if autoload_features.get('has_audio'):
                self.has_audio = True

            # Phase 7: Generate engine and system files
            traits_exporter.write_types(self)
            traits_exporter.write_engine(self)
            physics_exporter.write_physics(self)

            # Phase 8: Generate audio files (must be before makefile)
            audio_exporter.scan_and_copy_audio(self)
            audio_exporter.write_audio_config(self)

            # Phase 9: Generate UI files (must be before makefile)
            ui_exporter.write_fonts(self)

            # Phase 10: Generate Makefile (uses exported_fonts, exported_audio)
            build_runner.write_makefile(self)

            # Phase 11: Generate canvas after fonts
            ui_exporter.write_canvas(self)

            # Phase 12: Generate scene files
            scene_exporter.write_main(self)
            scene_exporter.write_models(self)
            self._write_renderer()
            scene_exporter.write_scenes(self)

            # Phase 13: Generate Iron runtime files
            self._write_iron()
            self._write_signal()
            self._write_time()
            self._write_tween()

            # Phase 14: Cleanup materials
            self._reset_materials_to_bsdf()

        finally:
            # Phase 15: Cleanup linked object temp data (always runs)
            if self.linked_objects:
                linked_export.cleanup_linked_export()
                log.info('Cleaned up linked object temp data')

        log.info('N64 export completed.')

    def publish(self):
        """Export and build the project."""
        self.export()
        return build_runner.run_make()

    def play(self):
        """Export, build, and run in emulator."""
        if not self.publish():
            return
        build_runner.run_emulator()

    # -------------------------------------------------------------------------
    # Directory Setup
    # -------------------------------------------------------------------------

    def _make_directories(self):
        """Create the N64 build directory structure."""
        build_dir = arm.utils.build_dir()
        dirs = [
            'n64',
            'n64/assets',
            'n64/src',
            'n64/src/data',
            'n64/src/events',
            'n64/src/iron',
            'n64/src/iron/object',
            'n64/src/iron/system',
            'n64/src/oimo',
            'n64/src/scenes',
            'n64/src/system',
            'n64/src/ui',
        ]
        for d in dirs:
            os.makedirs(os.path.join(build_dir, d), exist_ok=True)

    # -------------------------------------------------------------------------
    # Material Conversion
    # -------------------------------------------------------------------------

    def _convert_materials_to_f3d(self):
        """Convert materials to F3D format (requires Fast64 addon)."""
        try:
            if not hasattr(bpy.ops.scene, 'f3d_convert_to_bsdf'):
                log.warn('Fast64 addon not found - skipping F3D material conversion')
                return False

            bpy.ops.scene.f3d_convert_to_bsdf(
                direction='F3D',
                converter_type='All',
                backup=False,
                put_alpha_into_color=False,
                use_recommended=True,
                lights_for_colors=False,
                default_to_fog=False,
                set_rendermode_without_fog=False
            )
            return True
        except Exception as e:
            log.warn(f'F3D material conversion failed: {e}')
            return False

    def _reset_materials_to_bsdf(self):
        """Reset materials back to BSDF format (requires Fast64 addon)."""
        try:
            if not hasattr(bpy.ops.scene, 'f3d_convert_to_bsdf'):
                return False

            bpy.ops.scene.f3d_convert_to_bsdf(
                direction='BSDF',
                converter_type='All',
                backup=False,
                put_alpha_into_color=False,
                use_recommended=True,
                lights_for_colors=False,
                default_to_fog=False,
                set_rendermode_without_fog=False
            )
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True,
                do_linked_ids=True,
                do_recursive=True
            )
            return True
        except Exception as e:
            log.warn(f'BSDF material reset failed: {e}')
            return False

    # -------------------------------------------------------------------------
    # Static File Copying (Renderer, Iron, System)
    # -------------------------------------------------------------------------

    def _write_renderer(self):
        """Copy renderer files."""
        n64_utils.copy_src('renderer.c', 'src')
        n64_utils.copy_src('renderer.h', 'src')
        n64_utils.copy_src('utils.h', 'src')
        n64_utils.copy_src('render2d.h', 'src')

    def _write_iron(self):
        """Copy Iron runtime files."""
        # Render trait_events.h template
        tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'events', 'trait_events.h.j2')
        out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'events', 'trait_events.h')

        with open(tmpl_path, 'r', encoding='utf-8') as f:
            tmpl_content = f.read()

        max_button_subscribers = n64_utils.get_config('max_button_subscribers', 16)
        output = tmpl_content.format(max_button_subscribers=max_button_subscribers)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

        n64_utils.copy_src('events/trait_events.c', 'src')
        n64_utils.copy_src('iron/object/transform.h', 'src')
        n64_utils.copy_src('iron/object/transform.c', 'src')
        n64_utils.copy_src('iron/object/object.h', 'src')
        n64_utils.copy_src('iron/object/object.c', 'src')
        n64_utils.copy_src('iron/system/input.c', 'src')
        n64_utils.copy_src('iron/system/input.h', 'src')

    def _write_signal(self):
        """Copy signal system files."""
        n64_utils.copy_src('signal.c', 'src/system')
        n64_utils.copy_src('signal.h', 'src/system')

    def _write_time(self):
        """Copy time system files."""
        n64_utils.copy_src('time.c', 'src/system')
        n64_utils.copy_src('time.h', 'src/system')

    def _write_tween(self):
        """Copy tween system files."""
        n64_utils.copy_src('tween.c', 'src/system')
        n64_utils.copy_src('tween.h', 'src/system')
