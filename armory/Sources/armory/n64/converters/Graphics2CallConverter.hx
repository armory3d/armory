package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

/**
 * Converts kha.graphics2.Graphics calls to N64 render2d helper functions.
 *
 * Handles:
 * - g2.fillRect(x, y, w, h) -> render2d_fill_rect_kha(x, y, x+w, y+h, _g2_color)
 * - g2.color = value -> _g2_color = kha_color_value
 * - kha.Window.get(0).width -> render2d_get_width()
 * - kha.Window.get(0).height -> render2d_get_height()
 *
 * Note: g2.color property is stored as a local variable in the generated function
 * since N64 fill commands take color as a parameter rather than state.
 */
class Graphics2CallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check for Graphics2 method calls (g2.fillRect, etc.)
        switch (obj.expr) {
            case EConst(CIdent(name)):
                // Check if the identifier is a Graphics2 parameter (typically "g" or "g2")
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
                // g2.fillRect(x, y, width, height)
                // -> render2d_fill_rect_kha(x, y, x+width, y+height, _g2_color)
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

            case "drawRect":
                // For now, treat drawRect same as fillRect (N64 doesn't easily do unfilled)
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
                // Unsupported graphics2 method - skip
                return { type: "skip" };
        }

        return null;
    }
}
#end
