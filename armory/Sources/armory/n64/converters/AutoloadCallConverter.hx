package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import haxe.macro.Type;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

using haxe.macro.TypeTools;
using StringTools;

/**
 * Converts calls to autoload classes (static functions and variables).
 *
 * Handles patterns like:
 *   GameEvents.resetScore() -> gameevents_resetScore()
 *   GameEvents.score -> gameevents_score
 *   GameEvents.score = 10 -> gameevents_score = 10
 *
 * Autoload classes are detected by checking for @:n64Autoload metadata.
 */
class AutoloadCallConverter implements ICallConverter {
    // Cache of known autoload class names -> c_names
    static var autoloadCache:Map<String, String> = new Map();

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if this is a static call on an autoload class: ClassName.method()
        switch (obj.expr) {
            case EConst(CIdent(className)):
                // Check if className is an autoload
                var cName = getAutoloadCName(className);
                if (cName != null) {
                    return convertAutoloadCall(cName, method, args, ctx);
                }
            default:
        }
        return null;
    }

    function convertAutoloadCall(cName:String, method:String, args:Array<IRNode>, ctx:IExtractorContext):IRNode {
        // Generate: autoload_method(args...)
        return {
            type: "autoload_call",
            value: method,
            c_code: '${cName}_${method}',
            args: args,
            props: {
                c_name: cName,
                method: method
            }
        };
    }

    /**
     * Check if a class name is an autoload and return its C name.
     * Returns null if not an autoload.
     */
    public static function getAutoloadCName(className:String):String {
        // Check cache first
        if (autoloadCache.exists(className)) {
            return autoloadCache.get(className);
        }

        // Try to resolve the type and check for @:n64Autoload metadata
        try {
            var type = Context.getType(className);
            if (type == null) {
                // Try with common package prefixes
                for (prefix in ["arm.", "arm.node.", ""]) {
                    try {
                        type = Context.getType(prefix + className);
                        if (type != null) break;
                    } catch (e:Dynamic) {}
                }
            }

            if (type != null) {
                var classType = type.getClass();
                if (classType != null) {
                    var meta = classType.meta.get();
                    if (meta != null) {
                        for (m in meta) {
                            if (m.name == ":n64Autoload" || m.name == "n64Autoload") {
                                // Found an autoload - compute c_name (just class name, lowercased)
                                var cName = classType.name.toLowerCase();
                                autoloadCache.set(className, cName);
                                return cName;
                            }
                        }
                    }
                }
            }
        } catch (e:Dynamic) {
            // Type resolution failed, not an autoload
        }

        // Cache negative result
        autoloadCache.set(className, null);
        return null;
    }
}
#end
