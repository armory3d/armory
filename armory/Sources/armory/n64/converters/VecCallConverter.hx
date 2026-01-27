package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.ds.StringMap;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

using StringTools;

/**
 * Converts Vec2/Vec3/Vec4 method calls to C struct operations.
 * Handles: mult, add, sub, dot, normalize, length, clone, cross, set, setFrom
 */
class VecCallConverter implements ICallConverter {
    static var vecMethods = ["mult", "add", "sub", "dot", "normalize", "length", "clone", "cross", "set", "setFrom"];

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if this is a known Vec method
        if (!Lambda.has(vecMethods, method)) return null;

        // Check if the object type is a Vec type
        var objType = ctx.getExprType(obj);
        if (objType == null || !objType.startsWith("Vec")) return null;

        var objIR = ctx.exprToIR(obj);
        return convert(method, objIR, args, objType);
    }

    function convert(method:String, objIR:IRNode, args:Array<IRNode>, vecType:String):IRNode {
        // Determine C type based on Haxe type
        var cType = switch (vecType) {
            case "Vec4": "ArmVec4";
            case "Vec3": "ArmVec3";
            default: "ArmVec2";
        };
        var is3D = (vecType == "Vec3" || vecType == "Vec4");

        // Template uses {v} for vector, {0} for first arg
        var c_code = switch (method) {
            case "length":
                is3D ? "sqrtf({v}.x*{v}.x + {v}.y*{v}.y + {v}.z*{v}.z)"
                     : "sqrtf({v}.x*{v}.x + {v}.y*{v}.y)";
            case "mult":
                is3D ? "(" + cType + "){{v}.x*({0}), {v}.y*({0}), {v}.z*({0})}"
                     : "(" + cType + "){{v}.x*({0}), {v}.y*({0})}";
            case "add":
                is3D ? "(" + cType + "){{v}.x+({0}).x, {v}.y+({0}).y, {v}.z+({0}).z}"
                     : "(" + cType + "){{v}.x+({0}).x, {v}.y+({0}).y}";
            case "sub":
                is3D ? "(" + cType + "){{v}.x-({0}).x, {v}.y-({0}).y, {v}.z-({0}).z}"
                     : "(" + cType + "){{v}.x-({0}).x, {v}.y-({0}).y}";
            case "dot":
                is3D ? "({v}.x*({0}).x + {v}.y*({0}).y + {v}.z*({0}).z)"
                     : "({v}.x*({0}).x + {v}.y*({0}).y)";
            case "normalize":
                // Note: normalize modifies in-place, needs the original var name
                // We use {vraw} placeholder for unparenthesized var
                is3D ? "{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y+{v}.z*{v}.z); if(_l>0.0f){ {vraw}.x/=_l; {vraw}.y/=_l; {vraw}.z/=_l; } }"
                     : "{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y); if(_l>0.0f){ {vraw}.x/=_l; {vraw}.y/=_l; } }";
            case "clone":
                // Clone creates a copy - type depends on target
                // Special case: transform.scale is stored with SCALE_FACTOR (1/64), so multiply by 64 to get Blender values
                var isScaleClone = (objIR.type == "field" && objIR.value == "transform.scale");
                if (isScaleClone) {
                    // Inverse of SCALE_FACTOR (0.015625 = 1/64) = 64
                    if (cType == "ArmVec4") "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f, {v}.z*64.0f, 1.0f}";
                    else if (cType == "ArmVec3") "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f, {v}.z*64.0f}";
                    else "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f}";
                } else {
                    if (cType == "ArmVec4") "(" + cType + "){{v}.x, {v}.y, {v}.z, 1.0f}";
                    else if (cType == "ArmVec3") "(" + cType + "){{v}.x, {v}.y, {v}.z}";
                    else "(" + cType + "){{v}.x, {v}.y}";
                }
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "vec_call",
            c_code: c_code,
            object: objIR,
            args: args,
            props: {
                vecType: vecType,
                cType: cType,
                is3D: is3D
            }
        };
    }
}

#end