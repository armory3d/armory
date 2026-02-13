package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Converts kha.graphics2.Graphics calls to N64 render2d functions.
 * Supports: g2.fillRect, g2.drawRect, g2.color
 */
class Graphics2CallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        switch (obj.expr) {
            case EConst(CIdent(name)):
                var objType = ctx.getExprType(obj);
                if (objType == "kha.graphics2.Graphics" || objType == "Graphics" || name == "g" || name == "g2") {
                    return convertGraphics2Call(method, args, rawParams, ctx);
                }
            default:
        }
        return null;
    }

    function convertGraphics2Call(method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        switch (method) {
            case "fillRect":
                if (args.length >= 4) {
                    return {
                        type: "render2d_fill_rect",
                        props: {
                            x: args[0],
                            y: args[1],
                            width: args[2],
                            height: args[3]
                        }
                    };
                }
            default:
                return { type: "skip" };
        }
        return null;
    }
}
#end
