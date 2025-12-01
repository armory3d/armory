package armory.n64;

#if macro
import haxe.macro.Expr;

using haxe.macro.ExprTools;
using StringTools;

/**
 * N64 Physics Macro - Centralizes all physics-related code generation for N64 target.
 *
 * Responsibilities:
 * - Convert Blender Z-up to N64 Y-up coordinate system for physics vectors
 * - Emit C code for RigidBody method calls (applyForce, applyImpulse, etc.)
 * - Emit C code for PhysicsWorld method calls
 * - Provide helpers for Vec3/Vec4 extraction from Haxe expressions
 *
 * This macro acts as the single source of truth for physics code emission,
 * decoupling the main N64CEmitter from oimo API knowledge.
 */
class N64PhysicsMacro {

    // =========================================
    // Coordinate Conversion
    // =========================================

    /**
     * Convert a Vec3 from Blender coords (Z-up) to N64 coords (Y-up).
     * Formula: (x, y, z) -> (x, z, -y)
     */
    public static function blenderToN64Vec3(vec:{x:String, y:String, z:String}):{x:String, y:String, z:String} {
        return {x: vec.x, y: vec.z, z: '-(${vec.y})'};
    }

    /**
     * Emit a Vec3 in N64 coordinates from Blender components.
     */
    public static function emitN64Vec3(x:String, y:String, z:String):String {
        return 'oimo_vec3($x, $z, -($y))';
    }

    // =========================================
    // Vector Extraction Helpers
    // =========================================

    /**
     * Try to extract x, y, z string components from a Vec4/Vec3 constructor expression.
     * Returns null if the expression is not a simple Vec3/Vec4 constructor.
     */
    public static function tryExtractVec3(e:Expr, emitter:N64CEmitter):Null<{x:String, y:String, z:String}> {
        return switch (e.expr) {
            case ENew(tp, params):
                if ((tp.name == "Vec4" || tp.name == "Vec3") && params.length >= 3) {
                    {x: emitter.emitExpr(params[0]), y: emitter.emitExpr(params[1]), z: emitter.emitExpr(params[2])};
                } else null;

            case ECall(callE, callParams):
                // Check for vec.mult(scalar) pattern: Vec4(...).mult(s)
                switch (callE.expr) {
                    case EField(base, method):
                        if (method == "mult" && callParams.length > 0) {
                            var baseVec = tryExtractVec3(base, emitter);
                            if (baseVec != null) {
                                var scalar = emitter.emitExpr(callParams[0]);
                                {
                                    x: '(${baseVec.x}) * ($scalar)',
                                    y: '(${baseVec.y}) * ($scalar)',
                                    z: '(${baseVec.z}) * ($scalar)'
                                };
                            } else null;
                        } else null;
                    default: null;
                }

            default: null;
        };
    }

    // =========================================
    // RigidBody Method Emission
    // =========================================

    /**
     * Emit C code for a RigidBody method call.
     * Handles: applyForce, applyImpulse, setLinearVelocity, setAngularVelocity, etc.
     */
    public static function emitRigidBodyCall(method:String, params:Array<Expr>, emitter:N64CEmitter):String {
        return switch (method) {
            case "applyForce":
                emitForceOrImpulse("oimo_rigidbody_apply_force", "_force", params, emitter);

            case "applyImpulse":
                emitForceOrImpulse("oimo_rigidbody_apply_impulse_center", "_imp", params, emitter);

            case "setLinearVelocity":
                emitVelocitySetter("oimo_rigidbody_set_linear_velocity", "_vel", params, emitter);

            case "setAngularVelocity":
                emitVelocitySetter("oimo_rigidbody_set_angular_velocity", "_angvel", params, emitter);

            case "getLinearVelocity":
                emitVelocityGetter("oimo_rigidbody_get_linear_velocity", emitter);

            case "getAngularVelocity":
                emitVelocityGetter("oimo_rigidbody_get_angular_velocity", emitter);

            case "activate":
                '{ if (((ArmObject*)obj)->rigid_body) { oimo_rigidbody_wake_up(((ArmObject*)obj)->rigid_body); } }';

            case "disableDeactivation":
                '{ if (((ArmObject*)obj)->rigid_body) { ((ArmObject*)obj)->rigid_body->auto_sleep = 0; } }';

            case "setFriction":
                if (params.length > 0) {
                    var friction = emitter.emitExpr(params[0]);
                    '/* N64_TODO: setFriction($friction) - oimo friction is per-shape */';
                } else {
                    '/* N64_UNSUPPORTED: setFriction needs arg */';
                }

            case "setMass":
                if (params.length > 0) {
                    var mass = emitter.emitExpr(params[0]);
                    '{ if (((ArmObject*)obj)->rigid_body) { ((ArmObject*)obj)->rigid_body->mass = $mass; oimo_rigidbody_update_mass(((ArmObject*)obj)->rigid_body); } }';
                } else {
                    '/* N64_UNSUPPORTED: setMass needs arg */';
                }

            default:
                emitter.warn('Unsupported RigidBody method: $method');
                '/* N64_UNSUPPORTED: rb.$method */';
        };
    }

    /**
     * Emit code for force/impulse application with coordinate conversion.
     */
    static function emitForceOrImpulse(cFunc:String, varName:String, params:Array<Expr>, emitter:N64CEmitter):String {
        if (params.length == 0) {
            emitter.warn('$cFunc needs a vector argument');
            return '/* N64_UNSUPPORTED: $cFunc needs arg */';
        }

        var forceExpr = params[0];
        var vec = tryExtractVec3(forceExpr, emitter);

        if (vec != null) {
            // Static vector - convert at compile time
            var n64vec = blenderToN64Vec3(vec);
            return '{ if (((ArmObject*)obj)->rigid_body) { OimoVec3 $varName = oimo_vec3(${n64vec.x}, ${n64vec.y}, ${n64vec.z}); $cFunc(((ArmObject*)obj)->rigid_body, &$varName); } }';
        } else {
            // Dynamic vector - emit runtime swizzle
            var emitted = emitter.emitExpr(forceExpr);
            return '{ if (((ArmObject*)obj)->rigid_body) { OimoVec3 $varName = oimo_vec3($emitted.x, $emitted.z, -$emitted.y); $cFunc(((ArmObject*)obj)->rigid_body, &$varName); } }';
        }
    }

    /**
     * Emit code for velocity setters with coordinate conversion.
     */
    static function emitVelocitySetter(cFunc:String, varName:String, params:Array<Expr>, emitter:N64CEmitter):String {
        if (params.length == 0) {
            return '/* N64_UNSUPPORTED: $cFunc needs arg */';
        }

        var vec = tryExtractVec3(params[0], emitter);

        if (vec != null) {
            var n64vec = blenderToN64Vec3(vec);
            return '{ if (((ArmObject*)obj)->rigid_body) { OimoVec3 $varName = oimo_vec3(${n64vec.x}, ${n64vec.y}, ${n64vec.z}); $cFunc(((ArmObject*)obj)->rigid_body, &$varName); } }';
        } else {
            var emitted = emitter.emitExpr(params[0]);
            return '{ if (((ArmObject*)obj)->rigid_body) { OimoVec3 $varName = oimo_vec3($emitted.x, $emitted.z, -$emitted.y); $cFunc(((ArmObject*)obj)->rigid_body, &$varName); } }';
        }
    }

    /**
     * Emit code for velocity getters (returns Vec3 in Blender coords).
     * Note: This returns a pointer to internal data, user code shouldn't store it.
     */
    static function emitVelocityGetter(cFunc:String, emitter:N64CEmitter):String {
        // TODO: Need to convert back from N64 to Blender coords if user code expects that
        // For now, return as-is (N64 coords)
        return '(((ArmObject*)obj)->rigid_body ? $cFunc(((ArmObject*)obj)->rigid_body) : oimo_vec3_zero())';
    }

    // =========================================
    // PhysicsWorld Method Emission
    // =========================================

    /**
     * Emit C code for PhysicsWorld method calls.
     */
    public static function emitPhysicsWorldCall(method:String, params:Array<Expr>, emitter:N64CEmitter):String {
        return switch (method) {
            case "active":
                // PhysicsWorld.active -> physics_get_world()
                "physics_get_world()";

            case "pause":
                "physics_pause()";

            case "resume":
                "physics_resume()";

            case "setGravity":
                if (params.length >= 3) {
                    var x = emitter.emitExpr(params[0]);
                    var y = emitter.emitExpr(params[1]);
                    var z = emitter.emitExpr(params[2]);
                    // Convert Blender (X,Y,Z) to N64 (X,Z,-Y)
                    'physics_set_gravity($x, $z, -($y))';
                } else if (params.length == 1) {
                    var vec = tryExtractVec3(params[0], emitter);
                    if (vec != null) {
                        var n64vec = blenderToN64Vec3(vec);
                        'physics_set_gravity(${n64vec.x}, ${n64vec.y}, ${n64vec.z})';
                    } else {
                        var emitted = emitter.emitExpr(params[0]);
                        'physics_set_gravity($emitted.x, $emitted.z, -$emitted.y)';
                    }
                } else {
                    '/* N64_UNSUPPORTED: setGravity needs vector arg */';
                }

            case "rayCast":
                // TODO: Implement raycast with coordinate conversion
                emitter.warn('PhysicsWorld.rayCast not yet implemented for N64');
                '/* N64_TODO: rayCast */';

            default:
                emitter.warn('Unsupported PhysicsWorld method: $method');
                '/* N64_UNSUPPORTED: PhysicsWorld.$method */';
        };
    }

    // =========================================
    // Physics Data Extraction (for JSON export)
    // =========================================

    /**
     * Physics configuration for JSON export to Python exporter.
     * This ensures Python codegen uses the same coordinate conversion rules.
     */
    public static function getPhysicsConfigForJson():Dynamic {
        return {
            // Coordinate conversion: Blender (X,Y,Z) -> N64 (X,Z,-Y)
            coord_conversion: {
                x: "x",
                y: "z",
                z: "-y"
            },
            // Supported shape types
            shapes: ["sphere", "box"],
            // Supported body types
            body_types: ["static", "dynamic", "kinematic"],
            // Default physics values
            defaults: {
                gravity: [0.0, -9.81, 0.0],  // N64 coords (Y-down)
                friction: 0.5,
                restitution: 0.0,
                collision_group: 1,
                collision_mask: 1
            }
        };
    }
}
#end
