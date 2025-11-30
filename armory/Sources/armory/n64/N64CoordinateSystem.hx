package armory.n64;

#if macro
import haxe.macro.Expr;

/**
 * N64 Coordinate System Conversion
 *
 * Handles Blender Z-up to N64/T3D Y-up coordinate system conversion.
 * All conversion rules are embedded as static dictionaries.
 */
class N64CoordinateSystem {

    // =========================================
    // Coordinate System Definition
    // =========================================
    // Blender: X=right, Y=forward, Z=up
    // N64/T3D: X=right, Y=up,      Z=back
    //
    // Conversion formulas:
    //   Position:  (X, Y, Z) -> (X, Z, -Y)
    //   Scale:     (X, Y, Z) -> (X, Z, Y) * factor
    //   Direction: (X, Y, Z) -> (X, Z, -Y)
    //   Euler:     (X, Y, Z) -> (-X, Y, -Z)  [order: YZX]

    /** Default scale factor for Blender -> N64 */
    public static inline var DEFAULT_SCALE_FACTOR:Float = 0.015;

    // =========================================
    // Conversion Functions
    // =========================================

    /**
     * Convert position components to N64 coordinates.
     * (X, Y, Z) -> (X, Z, -Y)
     */
    public static function convertPosition(x:String, y:String, z:String):String {
        return '{$x, $z, -($y)}';
    }

    /**
     * Convert scale components to N64 coordinates.
     * (X, Y, Z) -> (X, Z, Y) * factor
     */
    public static function convertScale(x:String, y:String, z:String, factor:Float = 1.0):String {
        if (factor != 1.0) {
            return '{$x * ${factor}f, $z * ${factor}f, $y * ${factor}f}';
        }
        return '{$x, $z, $y}';
    }

    /**
     * Convert direction vector to N64 coordinates.
     * (X, Y, Z) -> (X, Z, -Y)
     */
    public static function convertDirection(x:String, y:String, z:String):String {
        return '{$x, $z, -($y)}';
    }

    /**
     * Generate runtime conversion code for a ArmVec3 variable.
     */
    public static function emitRuntimePositionConversion(varName:String):String {
        return '(ArmVec3){${varName}.x, ${varName}.z, -(${varName}.y)}';
    }

    /**
     * Generate runtime conversion code for scale from a ArmVec3 variable.
     */
    public static function emitRuntimeScaleConversion(varName:String):String {
        return '$varName.x, $varName.z, $varName.y';
    }

    // =========================================
    // C Code Emission Helpers (for N64CEmitter)
    // =========================================

    /**
     * Emit position-swizzled arguments for a C function call.
     * Blender (X, Y, Z) -> N64 (X, Z, -Y)
     */
    public static function emitPositionArgs(x:String, y:String, z:String):String {
        return '$x, $z, -($y)';
    }

    /**
     * Emit scale-swizzled arguments for a C function call.
     * Blender (X, Y, Z) -> N64 (X, Z, Y) - no negation for scale
     */
    public static function emitScaleArgs(x:String, y:String, z:String):String {
        return '$x, $z, $y';
    }

    /**
     * Emit direction-swizzled arguments for a C function call.
     * Same as position: Blender (X, Y, Z) -> N64 (X, Z, -Y)
     */
    public static function emitDirectionArgs(x:String, y:String, z:String):String {
        return '$x, $z, -($y)';
    }

    /**
     * Convert Blender axis values to N64 axis values (for rotation axes).
     * Returns the converted {x, y, z} floats.
     */
    public static function convertAxisValues(bx:Float, by:Float, bz:Float):{x:Float, y:Float, z:Float} {
        // Blender (X,Y,Z) -> N64 (X, Z, -Y)
        return {x: bx, y: bz, z: -by};
    }

    /**
     * Check if expression is a Vec3/Vec4 constructor.
     */
    public static function isStaticVec3Constructor(e:Expr):Bool {
        switch (e.expr) {
            case ENew(tp, _):
                return tp.name == "Vec4" || tp.name == "Vec3";
            case ECall(func, params):
                switch (func.expr) {
                    case EField(obj, "create"):
                        switch (obj.expr) {
                            case EConst(CIdent(name)):
                                return (name == "Vec4" || name == "Vec3") && params.length >= 3;
                            default:
                        }
                    default:
                }
            default:
        }
        return false;
    }

    /**
     * Extract x, y, z from a Vec3/Vec4 constructor.
     */
    public static function extractVec3Components(e:Expr, emitter:N64CEmitter):Null<{x:String, y:String, z:String}> {
        switch (e.expr) {
            case ENew(_, params):
                if (params.length >= 3) {
                    return {
                        x: emitter.emitExpr(params[0]),
                        y: emitter.emitExpr(params[1]),
                        z: emitter.emitExpr(params[2])
                    };
                }
            case ECall(func, params):
                switch (func.expr) {
                    case EField(_, "create"):
                        if (params.length >= 3) {
                            return {
                                x: emitter.emitExpr(params[0]),
                                y: emitter.emitExpr(params[1]),
                                z: emitter.emitExpr(params[2])
                            };
                        }
                    default:
                }
            default:
        }
        return null;
    }

    // =========================================
    // JSON Export for Python Exporter
    // =========================================

    /**
     * Get coordinate system config as a dynamic object for JSON export.
     * Python exporter reads this and applies conversions mechanically.
     */
    public static function getConfigForJson():Dynamic {
        return {
            position: { out_x: "x", out_y: "z", out_z: "-y" },
            scale: { out_x: "x", out_y: "z", out_z: "y", factor: DEFAULT_SCALE_FACTOR },
            direction: { out_x: "x", out_y: "z", out_z: "-y" },
            euler: { order: "YZX", out_x: "-x", out_y: "y", out_z: "-z" }
        };
    }
}
#end
