package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;
import armory.n64.util.ExprUtils;
import armory.n64.mapping.TypeMap;

using StringTools;

/**
 * Converts armory.system.Tween API calls to N64 C tween functions.
 *
 * Handles patterns like:
 *   tween.float(from, to, duration, onUpdate, onDone) -> tween_float(...)
 *   tween.vec4(from, to, duration, onUpdate, onDone) -> tween_vec4(...)
 *   tween.delay(duration, onDone) -> tween_delay(...)
 *   tween.start() -> tween_start(tween)
 *   tween.pause() -> tween_pause(tween)
 *   tween.stop() -> tween_stop(tween)
 *
 * Lambda callbacks are extracted and converted to named C functions with captures.
 * Captured variables from outer scope are passed via the data pointer.
 */
class TweenCallConverter implements ICallConverter {
    // Counter for generating unique callback names
    static var callbackCounter:Int = 0;

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if the object is a Tween type
        var objType = getExprTypeSafe(obj, ctx);
        var isPotentiallyInherited = false;

        // If objType is null or Dynamic (unresolved), check if it's a member or inherited member
        if (objType == null || objType == "Dynamic") {
            switch (obj.expr) {
                case EConst(CIdent(name)):
                    // Check local member types first
                    objType = ctx.getMemberType(name);
                    // Then check inherited (may return null if not loaded)
                    if (objType == null) {
                        objType = ctx.getInheritedMemberType(name);
                    }
                    // If still null and we have a parent, the identifier would become
                    // potentially_inherited - optimistically assume it could be a Tween
                    // and let Python resolve it correctly
                    if (objType == null && ctx.getParentName() != null) {
                        isPotentiallyInherited = true;
                    }
                default:
            }
        }

        // Proceed if we know it's a Tween OR if it's potentially inherited
        // (for inherited members we can't resolve type at macro time)
        if (!isPotentiallyInherited && (objType == null || objType == "Dynamic" || objType.indexOf("Tween") < 0)) {
            return null;
        }

        // Get the object IR (the tween variable)
        var objIR = ctx.exprToIR(obj);

        switch (method) {
            case "float":
                return convertTweenFloat(objIR, args, rawParams, ctx);
            case "vec4":
                return convertTweenVec4(objIR, args, rawParams, ctx);
            case "delay":
                return convertTweenDelay(objIR, args, rawParams, ctx);
            case "start":
                return convertTweenStart(objIR, ctx);
            case "pause":
                return convertTweenPause(objIR, ctx);
            case "stop":
                return convertTweenStop(objIR, ctx);
            default:
                return null;
        }
    }

    /**
     * Convert tween.float(from, to, duration, onUpdate, onDone, ease).start()
     *
     * Haxe signature: float(from:Float, to:Float, duration:Float, onUpdate:Float->Void, onDone:Void->Void, ?ease:Ease):Tween
     *
     * We need to:
     * 1. Extract the lambda for onUpdate and onDone
     * 2. Analyze captured variables
     * 3. Generate a tween_float IR node with callback info
     */
    function convertTweenFloat(tweenObj:IRNode, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Args: from, to, duration, onUpdate, onDone, [ease]
        var from = args.length > 0 ? args[0] : { type: "float", value: 0.0 };
        var to = args.length > 1 ? args[1] : { type: "float", value: 0.0 };
        var duration = args.length > 2 ? args[2] : { type: "float", value: 1.0 };

        // Extract callbacks
        var onUpdate = extractCallback(rawParams, 3, "float", ctx);
        var onDone = extractCallback(rawParams, 4, "done", ctx);

        // Extract ease (optional, defaults to linear)
        var ease = "EASE_LINEAR";
        if (args.length > 5 && args[5] != null) {
            ease = convertEase(args[5]);
        }

        // Mark that we're using tweens
        var meta = ctx.getMeta();
        meta.uses_tween = true;

        return {
            type: "tween_float",
            object: tweenObj,
            args: [from, to, duration],
            props: {
                ease: ease,
                on_update: onUpdate,
                on_done: onDone
            }
        };
    }

    function convertTweenVec4(tweenObj:IRNode, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Args: from, to, duration, onUpdate, onDone, [ease]
        var from = args.length > 0 ? args[0] : null;
        var to = args.length > 1 ? args[1] : null;
        var duration = args.length > 2 ? args[2] : { type: "float", value: 1.0 };

        var onUpdate = extractCallback(rawParams, 3, "vec4", ctx);
        var onDone = extractCallback(rawParams, 4, "done", ctx);

        var ease = "EASE_LINEAR";
        if (args.length > 5 && args[5] != null) {
            ease = convertEase(args[5]);
        }

        var meta = ctx.getMeta();
        meta.uses_tween = true;

        return {
            type: "tween_vec4",
            object: tweenObj,
            args: [from, to, duration],
            props: {
                ease: ease,
                on_update: onUpdate,
                on_done: onDone
            }
        };
    }

    function convertTweenDelay(tweenObj:IRNode, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Args: duration, onDone
        var duration = args.length > 0 ? args[0] : { type: "float", value: 1.0 };
        var onDone = extractCallback(rawParams, 1, "done", ctx);

        var meta = ctx.getMeta();
        meta.uses_tween = true;

        return {
            type: "tween_delay",
            object: tweenObj,
            args: [duration],
            props: {
                on_done: onDone
            }
        };
    }

    function convertTweenStart(tweenObj:IRNode, ctx:IExtractorContext):IRNode {
        // If tweenObj is itself a tween_float/tween_vec4/tween_delay, extract the original tween
        // and return a block with both the setup call and the start call
        var tweenType = tweenObj.type;
        if (tweenType == "tween_float" || tweenType == "tween_vec4" || tweenType == "tween_delay") {
            var originalTween = tweenObj.object;
            return {
                type: "block",
                children: [
                    tweenObj,  // The tween_float/vec4/delay call
                    { type: "tween_start", object: originalTween }  // Then start
                ]
            };
        }
        return {
            type: "tween_start",
            object: tweenObj
        };
    }

    function convertTweenPause(tweenObj:IRNode, ctx:IExtractorContext):IRNode {
        return {
            type: "tween_pause",
            object: tweenObj
        };
    }

    function convertTweenStop(tweenObj:IRNode, ctx:IExtractorContext):IRNode {
        return {
            type: "tween_stop",
            object: tweenObj
        };
    }

    /**
     * Extract a callback function from a lambda expression.
     * Returns an IR structure with:
     *   - callback_name: unique name for the generated C function
     *   - callback_type: "float", "vec4", or "done"
     *   - body: IR nodes for the function body
     *   - captures: list of captured variables with their types
     *   - param_name: name of the callback parameter (for float/vec4 callbacks)
     */
    function extractCallback(rawParams:Array<Expr>, index:Int, callbackType:String, ctx:IExtractorContext):Dynamic {
        if (rawParams == null || index >= rawParams.length) {
            return null;
        }

        var param = rawParams[index];
        if (param == null) return null;

        // Check for null literal
        switch (param.expr) {
            case EConst(CIdent("null")):
                return null;
            case EFunction(kind, func):
                // Anonymous function: function(v) { ... }
                return extractFunctionBody(func, callbackType, ctx);
            case EConst(CIdent(name)):
                // Declared function reference: onUpdate
                return extractMethodRef(name, callbackType, ctx, param.pos);
            case EField(_, fieldName):
                // Field access function reference: this.onUpdate
                return extractMethodRef(fieldName, callbackType, ctx, param.pos);
            default:
                Context.error('Tween callback must be a function or method reference, got: ${param.expr}', param.pos);
                return null;
        }
    }

    /**
     * Extract a callback from a declared method reference.
     * Looks up the method in the current class and extracts its body.
     */
    function extractMethodRef(methodName:String, callbackType:String, ctx:IExtractorContext, pos:Position):Dynamic {
        var func = ctx.getMethod(methodName);
        if (func == null) {
            Context.error('Tween callback method "$methodName" not found in class. Make sure it is defined as a static or instance method.', pos);
            return null;
        }
        return extractFunctionBody(func, callbackType, ctx);
    }

    function extractFunctionBody(func:Function, callbackType:String, ctx:IExtractorContext):Dynamic {
        if (func == null || func.expr == null) return null;

        // Generate unique callback name
        var cName = ctx.getCName();
        var callbackName = '${cName}_tween_cb_${callbackCounter++}';

        // Get parameter name (for float/vec4 callbacks)
        var paramName:String = null;
        if (func.args != null && func.args.length > 0) {
            paramName = func.args[0].name;
        }

        // Convert function body to IR
        var bodyNodes:Array<IRNode> = [];
        switch (func.expr.expr) {
            case EBlock(exprs):
                for (e in exprs) {
                    var node = ctx.exprToIR(e);
                    if (node != null && node.type != "skip") {
                        bodyNodes.push(node);
                    }
                }
            default:
                var node = ctx.exprToIR(func.expr);
                if (node != null && node.type != "skip") {
                    bodyNodes.push(node);
                }
        }

        // Analyze captures - find variables referenced in body that are:
        // 1. Not local to the callback
        // 2. Not the callback parameter
        // 3. Members of the autoload class OR function parameters
        var captures = analyzeCaptures(bodyNodes, paramName, ctx);

        return {
            callback_name: callbackName,
            callback_type: callbackType,
            body: bodyNodes,
            captures: captures,
            param_name: paramName
        };
    }

    /**
     * Analyze IR nodes to find captured variables.
     * Returns array of {name, type, is_member, is_param}
     */
    function analyzeCaptures(nodes:Array<IRNode>, excludeParam:String, ctx:IExtractorContext):Array<Dynamic> {
        var captures:Map<String, Dynamic> = new Map();

        for (node in nodes) {
            findCaptures(node, excludeParam, ctx, captures);
        }

        return Lambda.array(captures);
    }

    function findCaptures(node:IRNode, excludeParam:String, ctx:IExtractorContext, captures:Map<String, Dynamic>):Void {
        if (node == null) return;

        switch (node.type) {
            case "ident":
                var name = Std.string(node.value);
                if (name != excludeParam && name != "null" && name != "true" && name != "false") {
                    // Check if it's a member or needs to be captured
                    var memberType = ctx.getMemberType(name);
                    if (memberType != null) {
                        // It's a class member - accessible via data pointer
                        if (!captures.exists(name)) {
                            captures.set(name, {
                                name: name,
                                type: memberType,
                                ctype: TypeMap.getCType(memberType),
                                is_member: true,
                                is_param: false
                            });
                        }
                    } else {
                        // Check if it's a local variable / parameter
                        var localType = ctx.getLocalVarType(name);
                        if (localType != null) {
                            // It's a local/param - needs to be captured
                            if (!captures.exists(name)) {
                                captures.set(name, {
                                    name: name,
                                    type: localType,
                                    ctype: TypeMap.getCType(localType),
                                    is_member: false,
                                    is_param: true
                                });
                            }
                        }
                    }
                }

            case "field_access":
                // Check object and recurse
                if (node.object != null) {
                    findCaptures(node.object, excludeParam, ctx, captures);
                }

            case "method_call", "call":
                // Check object
                if (node.object != null) {
                    findCaptures(node.object, excludeParam, ctx, captures);
                }
                // Check args
                if (node.args != null) {
                    for (arg in node.args) {
                        findCaptures(arg, excludeParam, ctx, captures);
                    }
                }

            case "binop", "assign":
                if (node.children != null) {
                    for (child in node.children) {
                        findCaptures(child, excludeParam, ctx, captures);
                    }
                }

            case "callback_param_call":
                // Calling a callback parameter like finishedCallback()
                // The callback parameter name needs to be captured
                var name = Std.string(node.name);
                if (name != null && name != "" && !captures.exists(name)) {
                    var localType = ctx.getLocalVarType(name);
                    if (localType != null) {
                        // Convert Haxe function type to C function pointer type
                        var ctype = functionTypeToCType(localType);
                        captures.set(name, {
                            name: name,
                            type: localType,
                            ctype: ctype,
                            is_member: false,
                            is_param: true
                        });
                    }
                }

            case "if":
                if (node.children != null) {
                    for (child in node.children) {
                        findCaptures(child, excludeParam, ctx, captures);
                    }
                }

            default:
                // Recurse into children and args
                if (node.children != null) {
                    for (child in node.children) {
                        findCaptures(child, excludeParam, ctx, captures);
                    }
                }
                if (node.args != null) {
                    for (arg in node.args) {
                        findCaptures(arg, excludeParam, ctx, captures);
                    }
                }
        }
    }

    function convertEase(easeNode:IRNode):String {
        if (easeNode == null) return "EASE_LINEAR";

        var value = Std.string(easeNode.value);

        // Handle enum values like Ease.Linear, Ease.QuadIn, etc.
        switch (value) {
            case "Linear": return "EASE_LINEAR";
            case "QuadIn": return "EASE_QUAD_IN";
            case "QuadOut": return "EASE_QUAD_OUT";
            case "QuadInOut": return "EASE_QUAD_IN_OUT";
            case "CubicIn": return "EASE_CUBIC_IN";
            case "CubicOut": return "EASE_CUBIC_OUT";
            case "CubicInOut": return "EASE_CUBIC_IN_OUT";
            case "SineIn": return "EASE_SINE_IN";
            case "SineOut": return "EASE_SINE_OUT";
            case "SineInOut": return "EASE_SINE_IN_OUT";
            default: return "EASE_LINEAR";
        }
    }

    /**
     * Convert a Haxe function type like "Void->Void" or "Float->Void"
     * to a C function pointer typedef name.
     *
     * In the N64 C code, we use typedefs for callback types that include obj/data:
     * - Void->Void becomes ArmCallback (typedef void (*ArmCallback)(void*, void*))
     * - Float->Void becomes ArmFloatObjCallback (typedef void (*ArmFloatObjCallback)(float, void*, void*))
     *
     * The obj/data parameters allow callbacks to access trait members through the data pointer.
     */
    function functionTypeToCType(haxeType:String):String {
        // Parse the function type: ParamType->ReturnType
        var parts = haxeType.split("->");
        if (parts.length < 2) {
            return "ArmCallback";  // Default fallback
        }

        var paramType = parts[0].trim();

        // Map to our callback typedefs (all include obj/data for trait access)
        switch (paramType) {
            case "Void", "": return "ArmCallback";
            case "Float": return "ArmFloatObjCallback";
            default: return "ArmCallback";
        }
    }

    function getExprTypeSafe(e:Expr, ctx:IExtractorContext):String {
        try {
            return ctx.getExprType(e);
        } catch (err:Dynamic) {
            return null;
        }
    }
}
#end
