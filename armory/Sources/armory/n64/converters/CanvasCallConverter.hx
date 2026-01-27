package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Canvas Call Converter
 *
 * Handles KouiCanvas method calls:
 * - getElementAs(Label, "key") -> canvas_get_label IR
 * - notifyOnReady(callback) -> flatten callback inline (N64 loads synchronously)
 */
class CanvasCallConverter implements ICallConverter {

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if object is KouiCanvas type
        var objType = ctx.getExprType(obj);
        if (objType != "KouiCanvas") {
            return null;
        }

        return convertCanvasCall(method, args, rawParams, ctx);
    }

    function convertCanvasCall(method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        if (method == "getElementAs" && rawParams.length >= 2) {
            // canvas.getElementAs(Label, "score_label")
            var elementType = extractTypeIdent(rawParams[0]);
            var labelKey = extractStringLiteral(rawParams[1]);

            if (elementType == "Label" && labelKey != null) {
                ctx.getMeta().uses_ui = true;
                return {
                    type: "canvas_get_label",
                    props: { key: labelKey }
                };
            }
        }
        else if (method == "notifyOnReady" && rawParams.length >= 1) {
            // canvas.notifyOnReady(function() { ... })
            // On N64, canvas is always ready (sync loading), so flatten callback inline
            switch (rawParams[0].expr) {
                case EFunction(_, func):
                    if (func.expr != null) {
                        return ctx.exprToIR(func.expr);
                    }
                default:
            }
        }
        return { type: "skip" };
    }

    function extractTypeIdent(e:Expr):String {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CIdent(name)): return name;
            default: return null;
        }
    }

    function extractStringLiteral(e:Expr):String {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CString(s)): return s;
            default: return null;
        }
    }
}
#end
