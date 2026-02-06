package armory.n64.mapping;

/**
 * Shared Constants for N64 Code Generation
 *
 * Coordinate system conversion constants and factors used by both
 * the Haxe macro and Python codegen.
 *
 * Blender coordinate system: X right, Y forward, Z up
 * N64 coordinate system:     X right, Y up, Z forward (negated)
 *
 * Swizzle: Blender (X, Y, Z) → N64 (X, Z, -Y)
 */
class Constants {
    // ==========================================================================
    // Scale Conversion
    // ==========================================================================

    /**
     * Scale factor for Blender → N64 conversion.
     * Blender scale 1.0 becomes N64 scale 0.015625 (1/64).
     *
     * This matches the scale at which models are exported via GLTF.
     */
    public static inline var SCALE_FACTOR:Float = 0.015625;  // 1/64

    /**
     * Inverse scale factor for N64 → Blender conversion.
     * Used when reading transform.scale back into Blender-space values.
     */
    public static inline var SCALE_FACTOR_INV:Float = 64.0;  // 64/1

    /**
     * String representation of SCALE_FACTOR for C code generation.
     */
    public static inline var SCALE_FACTOR_C:String = "0.015625f";

    /**
     * String representation of SCALE_FACTOR_INV for C code generation.
     */
    public static inline var SCALE_FACTOR_INV_C:String = "64.0f";

    // ==========================================================================
    // N64 Config Limits
    // IMPORTANT: These values must match arm.n64.utils.N64_CONFIG in Python.
    // If you change these, update utils.py to maintain parity.
    // ==========================================================================

    /** Maximum physics bodies in a scene */
    public static inline var MAX_PHYSICS_BODIES:Int = 32;

    /** Maximum button event subscribers */
    public static inline var MAX_BUTTON_SUBSCRIBERS:Int = 16;

    /** Maximum contact handlers per rigid body */
    public static inline var MAX_CONTACT_SUBSCRIBERS:Int = 4;

    /** Maximum rigid bodies with contact subscriptions */
    public static inline var MAX_CONTACT_BODIES:Int = 16;
}
