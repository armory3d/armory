package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Converts Std.* calls to C equivalents.
 * Handles: Std.int(), Std.parseFloat(), Std.string()
 */
class StdCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        switch (obj.expr) {
            case EConst(CIdent("Std")):
                return convert(method, args);
            default:
                return null;
        }
    }

    function convert(method:String, args:Array<IRNode>):IRNode {
        return switch (method) {
            case "int":
                { type: "cast_call", value: "(int32_t)", args: args };
            case "parseFloat":
                { type: "math_call", value: "strtof", args: args };
            case "string":
                // Std.string(value) - emit sprintf with format based on arg type
                if (args.length > 0) {
                    var argType = args[0].type;
                    var format = switch (argType) {
                        case "float": "%.2f";
                        case "int": "%d";
                        case "member": "%d";
                        default: "%d";
                    };
                    { type: "sprintf", value: format, args: args };
                } else {
                    { type: "string", value: "" };
                }
            default:
                { type: "skip" };
        };
    }
}

#end