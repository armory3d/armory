package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Converts Math.* calls to C math functions.
 * Uses libdragon's fm_* fast math functions where available (16x faster on N64).
 * Handles: sin, cos, tan, sqrt, abs, floor, ceil, min, max, pow, exp, log, etc.
 */
class MathCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        switch (obj.expr) {
            case EConst(CIdent("Math")):
                return convert(method, args);
            default:
                return null;
        }
    }

    function convert(method:String, args:Array<IRNode>):IRNode {
        // Map Haxe Math methods to C math.h functions
        // Use libdragon's fm_* functions for sin/cos/atan2 (much faster on N64)
        var cFunc = switch (method) {
            case "sin": "fm_sinf";      // ~50 ticks vs ~800 ticks for sinf
            case "cos": "fm_cosf";      // ~50 ticks vs ~800 ticks for cosf
            case "tan": "tanf";
            case "asin": "asinf";
            case "acos": "acosf";
            case "atan": "atanf";
            case "atan2": "fm_atan2f";  // libdragon fast version
            case "sqrt": "sqrtf";
            case "pow": "powf";
            case "abs": "fabsf";
            case "floor": "fm_floorf"; // libdragon fast version
            case "ceil": "ceilf";
            case "round": "roundf";
            case "min": "fminf";
            case "max": "fmaxf";
            case "exp": "fm_exp";       // libdragon fast version (~3% error)
            case "log": "logf";
            default: method;
        };

        return {
            type: "math_call",
            value: cFunc,
            args: args
        };
    }
}

#end