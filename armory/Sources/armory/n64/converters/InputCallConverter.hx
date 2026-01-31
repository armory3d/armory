package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.mapping.ButtonMap;
import armory.n64.converters.ICallConverter;

/**
 * Converts input API calls to C N64 input functions.
 * Handles: gamepad.started("a"), keyboard.down("w"), mouse.released("left"), etc.
 * Maps buttons to N64_BTN_* constants and tracks buttons for polling.
 *
 * This converter supports two input handling modes:
 *
 * 1. Event extraction mode: Input checks like `if (gamepad.started("a"))`
 *    are extracted as separate button event handlers in processStatement().
 *    This converter is not called for those top-level conditions.
 *
 * 2. Inline mode (Armory style - default): When useInlineInputMode=true, input checks
 *    remain in update() as regular if-statements. This converter handles converting
 *    `gamepad.started("a")` to `input_started(N64_BTN_A)` as the if condition.
 *    This allows guards like `if (!active) return;` to naturally block input checks.
 */
class InputCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        switch (obj.expr) {
            case EConst(CIdent("gamepad")), EConst(CIdent("keyboard")), EConst(CIdent("mouse")), EConst(CIdent("Input")):
                return convert(method, args, rawParams, ctx);
            default:
                return null;
        }
    }

    function convert(method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        var meta = ctx.getMeta();
        meta.uses_input = true;

        // Track button for input polling
        if (rawParams.length > 0) {
            var btn = ctx.extractStringArg(rawParams[0]);
            if (btn != null) {
                var normalized = ButtonMap.normalize(btn);
                if (!Lambda.has(meta.buttons_used, normalized)) {
                    meta.buttons_used.push(normalized);
                }
            }
        }

        // Map button to N64_BTN_* constant
        var n64Button = "N64_BTN_A"; // default button
        if (args.length > 0) {
            var btnArg = args[0];
            if (btnArg.type == "string") {
                var btnName = btnArg.value;
                n64Button = ButtonMap.toN64Const(btnName);
            }
        }

        // Emit ready-to-use C code
        // Note: down() returns float (intensity 0.0-1.0), started/released return bool
        var cCode = switch(method) {
            case "started": 'input_started($n64Button)';
            case "released": 'input_released($n64Button)';
            case "down": 'input_down($n64Button)';
            case "getStickX": 'input_stick_x()';
            case "getStickY": 'input_stick_y()';
            default: '0'; // unsupported input method - return neutral value
        };

        return {
            type: "input_call",
            c_code: cCode,
            method: method
        };
    }
}

#end