package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import armory.n64.IRTypes;
import armory.n64.mapping.TypeMap;
import armory.n64.converters.ICallConverter;

/**
 * Converts Haxe Array operations to C arm_array functions.
 *
 * Handles:
 *   array.push(item)    -> arraytype_push(&array_expr, item)
 *   array.pop()         -> arraytype_pop(&array_expr)
 *   array.length        -> array_expr.count
 *   array[i]            -> arraytype_get(&array_expr, i)
 *   array[i] = x        -> arraytype_set(&array_expr, i, x)
 */
class ArrayCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if obj is an Array type
        var objType = ctx.getExprType(obj);
        if (!TypeMap.isArrayType(objType)) {
            return null;
        }

        var cType = TypeMap.getCType(objType);
        var arrayExpr = extractArrayExpr(obj, ctx);

        return switch (method) {
            case "push":
                convertPush(arrayExpr, cType, args);
            case "pop":
                convertPop(arrayExpr, cType);
            case "clear", "resize" if (args.length == 1 && isZeroArg(args[0])):
                convertClear(arrayExpr, cType);
            case "length":
                convertLength(arrayExpr, cType);
            default:
                null;
        };
    }

    /**
     * Extract the array expression (how to access the array variable in C).
     * For traits: data->arrayName (member) or arrayName (local)
     * For autoloads: c_name_arrayName (member) or arrayName (local)
     */
    function extractArrayExpr(e:Expr, ctx:IExtractorContext):String {
        return switch (e.expr) {
            case EConst(CIdent(name)):
                // Check if it's a member or local
                if (ctx.getMemberType(name) != null) {
                    if (ctx.isAutoload()) {
                        ctx.getCName() + "_" + name;
                    } else {
                        "data->" + name;
                    }
                } else {
                    name;
                }
            case EField(obj, field):
                // Member access: this.array -> data->array or c_name_array
                if (ctx.isAutoload()) {
                    ctx.getCName() + "_" + field;
                } else {
                    "data->" + field;
                }
            default:
                "array";
        };
    }

    function isZeroArg(arg:IRNode):Bool {
        return arg.type == "literal" && arg.value == "0";
    }

    function convertPush(arrayExpr:String, cType:String, args:Array<IRNode>):IRNode {
        return {
            type: "array_push",
            value: cType,
            props: {
                array_expr: arrayExpr
            },
            children: args
        };
    }

    function convertPop(arrayExpr:String, cType:String):IRNode {
        return {
            type: "array_pop",
            value: cType,
            props: {
                array_expr: arrayExpr
            }
        };
    }

    function convertLength(arrayExpr:String, cType:String):IRNode {
        return {
            type: "array_length",
            value: cType,
            props: {
                array_expr: arrayExpr
            }
        };
    }

    function convertClear(arrayExpr:String, cType:String):IRNode {
        return {
            type: "array_clear",
            value: cType,
            props: {
                array_expr: arrayExpr
            }
        };
    }
}

#end
