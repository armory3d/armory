package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

using StringTools;

/**
 * Scene Call Converter
 *
 * Handles Scene.setActive() calls for scene transitions.
 * Converts to scene_switch_to() with either compile-time or runtime scene lookup.
 */
class SceneCallConverter implements ICallConverter {

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Only handle Scene.* calls
        switch (obj.expr) {
            case EConst(CIdent("Scene")):
                return convertSceneCall(method, args, rawParams, ctx);
            default:
                return null;
        }
    }

    function convertSceneCall(method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        if (method == "setActive" && rawParams.length > 0) {
            var result = analyzeSceneArg(rawParams[0], ctx);

            switch (result.kind) {
                case "constant":
                    // Compile-time known scene: Scene.setActive("Level_01")
                    var sceneNameUpper = result.value.toUpperCase();
                    return {
                        type: "scene_call",
                        method: "setActive",
                        c_code: 'scene_switch_to(SCENE_$sceneNameUpper)'
                    };

                case "current_scene":
                    // Scene.active.raw.name -> restart current scene
                    return {
                        type: "scene_call",
                        method: "setActive",
                        c_code: 'scene_switch_to(scene_get_current_id())'
                    };

                case "member_string":
                    // Member variable of type String: Scene.setActive(nextLevel)
                    // Runtime lookup by name
                    return {
                        type: "scene_call",
                        method: "setActive",
                        args: [{ type: "member", value: result.value }]
                    };

                case "expression":
                    // Fallback: runtime lookup
                    return {
                        type: "scene_call",
                        method: "setActive",
                        args: args
                    };
            }
        }
        return { type: "skip" };
    }

    /**
     * Analyze Scene.setActive argument and classify it:
     * - "constant": compile-time string literal
     * - "current_scene": Scene.active.raw.name pattern
     * - "member_string": String member variable
     * - "expression": anything else (runtime lookup)
     */
    function analyzeSceneArg(expr:Expr, ctx:IExtractorContext):{ kind:String, value:String } {
        if (expr == null) return { kind: "expression", value: null };

        switch (expr.expr) {
            case EConst(CString(s)):
                return { kind: "constant", value: s };

            case EConst(CIdent(name)):
                var memberType = ctx.getMemberType(name);
                if (memberType == "String") {
                    return { kind: "member_string", value: name };
                }
                return { kind: "expression", value: null };

            case EField(innerExpr, fieldName):
                if (fieldName == "name") {
                    switch (innerExpr.expr) {
                        case EField(innerInner, "raw"):
                            switch (innerInner.expr) {
                                case EField(sceneExpr, "active"):
                                    switch (sceneExpr.expr) {
                                        case EConst(CIdent("Scene")):
                                            return { kind: "current_scene", value: null };
                                        default:
                                    }
                                default:
                            }
                        default:
                    }
                }
                return { kind: "expression", value: null };

            default:
                return { kind: "expression", value: null };
        }
    }
}
#end
