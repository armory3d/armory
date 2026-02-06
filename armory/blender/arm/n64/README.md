# N64 Exporter Architecture

This document provides an architectural overview of the Armory3D N64 exporter, which transpiles Armory/Iron Haxe traits to C code targeting the Nintendo 64 via libdragon and Tiny3D.

## Pipeline Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Blender Export │ ──► │  Haxe IR Macros  │ ──► │  Python Codegen │ ──► │  libdragon Build│
│  (Python)       │     │  (Compile-time)  │     │  (Templates)    │     │  (make/gcc)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                        │                       │
        ▼                       ▼                        ▼                       ▼
   Scene data            n64_traits.json            C source files           .z64 ROM
   GLTF meshes           n64_autoloads.json         Header files
   Audio assets                                     Makefile
```

## Key Design Principles

1. **Clean IR Separation**: Haxe macros perform semantic analysis and emit JSON IR. Python does mechanical 1:1 translation to C without re-analyzing semantics.

2. **Converter Plugin Pattern**: Each Haxe API domain (physics, audio, input, etc.) has a dedicated converter that can be extended independently.

3. **Template-Based Codegen**: Jinja2 templates separate C code structure from generated data.

## Module Responsibilities

### Python Side (`armory/blender/arm/n64/`)

| Module | Purpose |
|--------|---------|
| `exporter.py` | Main entry point, orchestrates pipeline |
| `utils.py` | Shared utilities, configuration, coordinate conversion |
| `codegen/trait_emitter.py` | IR → C code translation |
| `codegen/trait_generator.py` | Prepares template data, handles inheritance |
| `codegen/autoload_generator.py` | Autoload-specific code generation |
| `codegen/tween_helper.py` | Tween animation support |
| `export/scene_exporter.py` | Scene data extraction |
| `export/mesh_exporter.py` | GLTF mesh export |
| `export/audio_exporter.py` | Audio asset processing |
| `export/ui_exporter.py` | Canvas/font generation |
| `export/physics_exporter.py` | Physics engine files |
| `export/build_runner.py` | Makefile generation, build execution |

### Haxe Side (`armory/Sources/armory/n64/`)

| Module | Purpose |
|--------|---------|
| `N64TraitMacro.hx` | Extracts trait code to IR at compile-time |
| `N64AutoloadMacro.hx` | Extracts autoload code to IR |
| `IRTypes.hx` | IR node type definitions and documentation |
| `converters/*.hx` | Domain-specific call converters |
| `mapping/TypeMap.hx` | Haxe → C type mapping |
| `mapping/Constants.hx` | Shared constants (scale factors, limits) |

### C Templates (`armorcore/Deployment/n64/src/`)

Templates use Python `.format()` placeholders (`{variable}`):

| Directory | Contents |
|-----------|----------|
| `data/` | traits.c/h, autoloads.c/h, signals.c/h |
| `scenes/` | scene.c template |
| `ui/` | canvas.c/h, fonts.c/h |
| `autoloads/` | Per-autoload C files |

## IR Node Types

The IR (Intermediate Representation) is a JSON format that bridges Haxe semantics to C code. See `IRTypes.hx` for complete documentation.

**Key Categories:**
- **Literals**: `int`, `float`, `string`, `bool`, `null`, `c_literal`
- **Variables**: `member`, `ident`, `field_access`, `autoload_field`
- **Operators**: `assign`, `binop`, `unop`
- **Control Flow**: `if`, `while`, `for_range`, `return`, `break`, `continue`
- **Calls**: `call`, `method_call`, `transform_call`, `physics_call`, `audio_*`, etc.

## Adding Support for New Haxe APIs

### Step 1: Create a Converter (Haxe)

Create `armory/Sources/armory/n64/converters/MyCallConverter.hx`:

```haxe
class MyCallConverter implements ICallConverter {
    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>,
                               rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Return null if not handling this call
        if (!isMyApiCall(obj, method)) return null;

        // Return IR node with c_code template
        return {
            type: "my_call",
            c_code: "my_c_function({0}, {1})",
            args: args
        };
    }
}
```

### Step 2: Register the Converter (Haxe)

In `N64TraitMacro.hx`, add to the converter list in `TraitExtractor`:

```haxe
callConverters = [
    // ... existing converters ...
    new MyCallConverter()
];
```

### Step 3: Add Emitter (Python)

In `trait_emitter.py`, add an `emit_my_call` method:

```python
def emit_my_call(self, node: Dict) -> str:
    """Handle my_call IR nodes."""
    c_code = node.get("c_code", "")
    return self._substitute_placeholders(c_code, node.get("args", []))
```

## Configuration

### Python Configuration (`utils.py`)

```python
N64_CONFIG = {
    'max_physics_bodies': 32,      # See also: Constants.hx
    'max_button_subscribers': 16,
    'max_contact_subscribers': 4,
    'max_contact_bodies': 16,
}
```

### Haxe Metadata

- `@:n64MaxSubs(N)` - Set max signal subscribers
- `@:n64Autoload(order=N)` - Set autoload initialization order
- `@:n64SignalType("name")` - Declare global signal type

## Coordinate System

Armory uses Blender's Z-up coordinate system. The exporter converts to N64's Y-up system:

- Blender X → N64 X
- Blender Y → N64 -Z
- Blender Z → N64 Y

Position scale factor: `1/64` (64 Blender units = 1 N64 unit)

## Debugging

### IR Inspection

After export, check `build_<project>/n64_traits.json` and `n64_autoloads.json` to see the generated IR.

### Generated Code

C code is generated in `armorcore/Deployment/n64/src/data/traits.c` and related files.

### Build Errors

Build output appears in Blender's system console. Common issues:
- Missing includes: Check template files
- Type errors: Check TypeMap.hx mappings
- Link errors: Check that C functions exist in runtime

## Version Compatibility

The IR format includes a version number. If the Haxe macro IR version doesn't match what Python expects, export will warn. Update both sides when changing IR structure.

Current IR version: Check `ir_version` in `n64_traits.json` header.
