package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Converts transform method calls to C it_* operations.
 * Handles: translate, rotate, move, setRotation, look, right, up, worldx/y/z, reset, buildMatrix
 */
class TransformCallConverter implements ICallConverter {
    static var transformMethods = [
        "translate", "rotate", "move", "setMatrix", "multMatrix", "setRotation",
        "buildMatrix", "applyParent", "applyParentInverse", "reset",
        "look", "right", "up", "worldx", "worldy", "worldz"
    ];

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check for transform.method() or owner.transform.method() pattern
        switch (obj.expr) {
            case EField(owner, "transform"):
                if (Lambda.has(transformMethods, method)) {
                    // Extract owner expression for {obj} substitution
                    var ownerNode = ctx.exprToIR(owner);
                    return convert(method, args, ctx, ownerNode);
                }
            case EConst(CIdent("transform")):
                if (Lambda.has(transformMethods, method)) {
                    return convert(method, args, ctx, null);
                }
            default:
        }

        return null;
    }

    function convert(method:String, args:Array<IRNode>, ctx:IExtractorContext, ownerNode:IRNode):IRNode {
        var meta = ctx.getMeta();

        // Mark as mutating if it's a transform-modifying method
        if (method == "translate" || method == "rotate" || method == "move" ||
            method == "setMatrix" || method == "multMatrix" || method == "setRotation" ||
            method == "buildMatrix" || method == "applyParent" || method == "applyParentInverse" ||
            method == "reset") {
            meta.mutates_transform = true;
        }

        meta.uses_transform = true;

        // Template uses {0}, {1}, {2} for args and {obj} for the transform owner
        // Coord conversion: Blender (X,Y,Z) → N64 (X,Z,-Y)
        var c_code = switch (method) {
            case "translate":
                // translate(x, y, z) -> it_translate(transform, x, z, -y)
                "it_translate(&((ArmObject*){obj})->transform, {0}, {2}, -({1}));";
            case "rotate":
                // rotate(axis, angle) -> it_rotate_axis_global(transform, axis.x, axis.z, -axis.y, angle)
                "it_rotate_axis_global(&((ArmObject*){obj})->transform, ({0}).x, ({0}).z, -({0}).y, {1});";
            case "move":
                // move(axis, ?scale) -> it_move(transform, axis.x, axis.z, -axis.y, scale)
                "it_move(&((ArmObject*){obj})->transform, ({0}).x, ({0}).z, -({0}).y, {1});";
            case "setRotation":
                // setRotation(x, y, z) -> it_set_rot_euler(transform, x, z, -y)
                "it_set_rot_euler(&((ArmObject*){obj})->transform, {0}, {2}, -({1}));";
            case "look":
                "{ T3DVec3 _dir; it_look(&((ArmObject*){obj})->transform, &_dir); _dir; }";
            case "right":
                "{ T3DVec3 _dir; it_right(&((ArmObject*){obj})->transform, &_dir); _dir; }";
            case "up":
                "{ T3DVec3 _dir; it_up(&((ArmObject*){obj})->transform, &_dir); _dir; }";
            case "worldx":
                "it_world_x(&((ArmObject*){obj})->transform)";
            case "worldy":
                // Scene data is already in N64 coordinates - no conversion needed
                "it_world_y(&((ArmObject*){obj})->transform)";
            case "worldz":
                // Scene data is already in N64 coordinates - no conversion needed
                "it_world_z(&((ArmObject*){obj})->transform)";
            case "reset":
                "it_reset(&((ArmObject*){obj})->transform);";
            case "buildMatrix":
                // N64 uses dirty flag system - just mark as dirty, matrix rebuilds automatically
                "((ArmObject*){obj})->transform.dirty = 1;";
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "transform_call",
            c_code: c_code,
            args: args,
            object: ownerNode  // Owner of transform for {obj} substitution (null = self)
        };
    }
}

#end