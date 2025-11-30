package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;
import haxe.macro.Type;
import haxe.Json;
import sys.io.File;
import sys.FileSystem;

using haxe.macro.ExprTools;
using haxe.macro.TypeTools;
using StringTools;
using Lambda;

/**
 * N64 Smart Trait Macro
 *
 * This macro outputs RESOLVED C CODE directly.
 * The output JSON contains ready-to-emit C strings.
 *
 * Architecture:
 * - N64Config: Button/type/API mappings (internal dictionaries)
 * - N64CEmitter: Converts Haxe AST to C strings
 * - N64TraitMacro: Orchestrates extraction and JSON output
 *
 * Output format (n64_traits.json):
 * {
 *   "version": 3,
 *   "traits": [{
 *     "name": "MyTrait",
 *     "members": [{"name": "speed", "type": "float", "default": "1.0f"}],
 *     "init": ["tdata->speed = 1.0f;"],
 *     "update": ["if (input_down(N64_BTN_B)) { obj->transform.rot[1] += tdata->speed * dt; }"],
 *     "remove": [],
 *     "flags": {"needs_obj": true, "needs_dt": true}
 *   }]
 * }
 */
class N64TraitMacro {
    static var traitData:Map<String, TraitIR> = new Map();
    static var initialized:Bool = false;

    /**
     * Build macro entry point
     */
    macro public static function build():Array<Field> {
        var defines = Context.getDefines();
        if (!defines.exists("arm_target_n64")) {
            return null;
        }

        if (!initialized) {
            initialized = true;
            Context.onAfterTyping(function(_) {
                writeTraitJson();
            });
        }

        var localClass = Context.getLocalClass();
        if (localClass == null) return null;

        var cls = localClass.get();
        var className = cls.name;
        var modulePath = cls.module;

        // Skip internal traits
        if (modulePath.indexOf("iron.") == 0 || modulePath.indexOf("armory.trait.internal") == 0) {
            return null;
        }

        var fields = Context.getBuildFields();

        // Extract trait IR
        var extractor = new TraitExtractor(className, fields);
        var traitIR = extractor.extract();

        if (traitIR != null) {
            traitData.set(className, traitIR);
        }

        return null;
    }

    /**
     * Write the final JSON with resolved C code
     */
    static function writeTraitJson():Void {
        if (traitData.keys().hasNext() == false) return;

        var traits:Array<Dynamic> = [];
        var allButtons:Array<String> = [];
        var anyTransform = false;
        var anyScene = false;
        var sceneNames:Array<String> = [];

        for (name in traitData.keys()) {
            var ir = traitData.get(name);

            // Convert members map to object for JSON
            var membersObj:Dynamic = {};
            for (memberName in ir.members.keys()) {
                var m = ir.members.get(memberName);
                Reflect.setField(membersObj, memberName, {
                    type: m.type,
                    default_value: m.default_value
                });
            }

            traits.push({
                name: ir.name,
                skip: ir.skip,
                needs_data: ir.needs_data,
                members: membersObj,
                init: ir.initCode,
                update: ir.updateCode,
                remove: ir.removeCode,
                flags: {
                    needs_obj: ir.needsObj,
                    needs_dt: ir.needsDt
                },
                input_buttons: ir.inputButtons
            });

            // Aggregate summary info
            for (btn in ir.inputButtons) {
                if (!Lambda.has(allButtons, btn)) allButtons.push(btn);
            }
            anyTransform = anyTransform || ir.hasTransform;
            anyScene = anyScene || ir.hasScene;
        }

        var output:Dynamic = {
            version: 5,
            generated: "N64TraitMacro",
            coordinate_system: N64CoordinateSystem.getConfigForJson(),
            traits: traits,
            summary: {
                input_buttons: allButtons,
                has_transform: anyTransform,
                has_scene: anyScene,
                scene_names: sceneNames
            }
        };

        var json = Json.stringify(output, null, "  ");

        // Write to build directory
        var defines = Context.getDefines();
        var buildDir = defines.get("arm_build_dir");
        if (buildDir == null) buildDir = "build";

        var outPath = buildDir + "/n64_traits.json";
        try {
            // Ensure directory exists
            var dir = haxe.io.Path.directory(outPath);
            if (dir != "" && !FileSystem.exists(dir)) {
                FileSystem.createDirectory(dir);
            }
            File.saveContent(outPath, json);
        } catch (e:Dynamic) {
            Context.warning('Failed to write n64_traits.json: $e', Context.currentPos());
        }
    }
}

/**
 * Trait IR - the resolved output
 */
typedef TraitIR = {
    name:String,
    skip:Bool,                            // True if trait has no code or data
    needs_data:Bool,
    members:Map<String, MemberIR>,       // name -> {type, default}
    initCode:Array<String>,
    updateCode:Array<String>,
    removeCode:Array<String>,
    needsObj:Bool,
    needsDt:Bool,
    inputButtons:Array<String>,          // Buttons used (e.g., ["N64_BTN_A", "N64_BTN_B"])
    hasTransform:Bool,
    hasScene:Bool
}

typedef MemberIR = {
    type:String,
    default_value:String
}

/**
 * Extracts trait information and converts to C code
 */
class TraitExtractor {
    var className:String;
    var fields:Array<Field>;
    var members:Map<String, MemberIR>;
    var memberNames:Array<String>;
    var methodMap:Map<String, Function>;
    var vec4Exprs:Map<String, Expr>;  // Store Vec4 member init expressions for axis resolution

    public function new(className:String, fields:Array<Field>) {
        this.className = className;
        this.fields = fields;
        this.members = new Map();
        this.memberNames = [];
        this.methodMap = new Map();
        this.vec4Exprs = new Map();
    }

    public function extract():TraitIR {
        // Pass 1: Extract members and build method map
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    var member = extractMember(field.name, t, e);
                    if (member != null) {
                        members.set(field.name, member);
                        memberNames.push(field.name);
                        // Store Vec4 init expressions for axis resolution in rotate()
                        if (member.type == "Vec3" && e != null) {
                            vec4Exprs.set(field.name, e);
                        }
                    }
                case FFun(func):
                    methodMap.set(field.name, func);
                default:
            }
        }

        // Pass 2: Find lifecycle registrations in constructor
        var lifecycles = findLifecycles();

        // Pass 3: Convert lifecycle functions to C code
        var initCode:Array<String> = [];
        var updateCode:Array<String> = [];
        var removeCode:Array<String> = [];
        var needsObj = false;
        var needsDt = false;
        var inputButtons:Array<String> = [];
        var hasTransform = false;
        var hasScene = false;
        var needsInitialScale = false;

        if (lifecycles.init != null) {
            var result = emitFunction(lifecycles.init);
            initCode = result.code;
            needsObj = needsObj || result.needsObj;
            needsDt = needsDt || result.needsDt;
            for (btn in result.inputButtons) if (!Lambda.has(inputButtons, btn)) inputButtons.push(btn);
            hasTransform = hasTransform || result.hasTransform;
            hasScene = hasScene || result.hasScene;
            needsInitialScale = needsInitialScale || result.needsInitialScale;
            // Add hardcoded scene as a member
            if (result.targetScene != null) {
                var sceneEnum = 'SCENE_${result.targetScene.toUpperCase()}';
                members.set("target_scene", {type: "SceneId", default_value: sceneEnum});
                if (!Lambda.has(memberNames, "target_scene")) memberNames.push("target_scene");
            }
        }

        if (lifecycles.update != null) {
            var result = emitFunction(lifecycles.update);
            updateCode = result.code;
            needsObj = needsObj || result.needsObj;
            needsDt = needsDt || result.needsDt;
            for (btn in result.inputButtons) if (!Lambda.has(inputButtons, btn)) inputButtons.push(btn);
            hasTransform = hasTransform || result.hasTransform;
            hasScene = hasScene || result.hasScene;
            needsInitialScale = needsInitialScale || result.needsInitialScale;
            // Add hardcoded scene as a member
            if (result.targetScene != null) {
                var sceneEnum = 'SCENE_${result.targetScene.toUpperCase()}';
                members.set("target_scene", {type: "SceneId", default_value: sceneEnum});
                if (!Lambda.has(memberNames, "target_scene")) memberNames.push("target_scene");
            }
        }

        if (lifecycles.remove != null) {
            var result = emitFunction(lifecycles.remove);
            removeCode = result.code;
            needsObj = needsObj || result.needsObj;
            needsDt = needsDt || result.needsDt;
            for (btn in result.inputButtons) if (!Lambda.has(inputButtons, btn)) inputButtons.push(btn);
            hasTransform = hasTransform || result.hasTransform;
            hasScene = hasScene || result.hasScene;
            needsInitialScale = needsInitialScale || result.needsInitialScale;
            // Add hardcoded scene as a member
            if (result.targetScene != null) {
                var sceneEnum = 'SCENE_${result.targetScene.toUpperCase()}';
                members.set("target_scene", {type: "SceneId", default_value: sceneEnum});
                if (!Lambda.has(memberNames, "target_scene")) memberNames.push("target_scene");
            }
        }

        // If scale assignment is used, add _initialScale member and init code
        if (needsInitialScale) {
            members.set("_initialScale", {type: "Vec3", default_value: "{1, 1, 1}"});
            if (!Lambda.has(memberNames, "_initialScale")) memberNames.push("_initialScale");
            // Add init code to capture object's initial scale (semicolon included)
            var captureCode = '((' + className + 'Data*)data)->_initialScale = (Vec3){((ArmObject*)obj)->transform.scale[0], ((ArmObject*)obj)->transform.scale[1], ((ArmObject*)obj)->transform.scale[2]};';
            initCode.insert(0, captureCode);
            needsObj = true;  // Need obj to read initial scale
        }

        // Determine if trait needs per-instance data
        var needsData = memberNames.length > 0;

        // Determine if trait should be skipped (no code and no data)
        var hasCode = initCode.length > 0 || updateCode.length > 0 || removeCode.length > 0;
        var shouldSkip = !hasCode && !needsData;

        return {
            name: className,
            skip: shouldSkip,
            needs_data: needsData,
            members: members,
            initCode: initCode,
            updateCode: updateCode,
            removeCode: removeCode,
            needsObj: needsObj,
            needsDt: needsDt,
            inputButtons: inputButtons,
            hasTransform: hasTransform,
            hasScene: hasScene
        };
    }

    /**
     * Extract a member variable
     */
    function extractMember(name:String, t:ComplexType, e:Expr):MemberIR {
        // Skip API objects
        if (N64Config.shouldSkipMember(name)) return null;

        var typeName = t != null ? complexTypeToString(t) : "Dynamic";

        // Skip unsupported types
        if (!N64Config.isSupportedType(typeName)) return null;

        var cType = N64Config.mapType(typeName);
        var defaultVal = e != null ? exprToDefault(e, cType) : defaultForType(cType);

        // Detect scene-related string members and convert to SceneId
        if (cType == "const char*" && isSceneMemberName(name)) {
            cType = "SceneId";
            // Convert string default to scene enum
            if (e != null) {
                var sceneName = extractStringValue(e);
                if (sceneName != null) {
                    defaultVal = 'SCENE_${sceneName.toUpperCase()}';
                } else {
                    defaultVal = "SCENE_COUNT";  // Invalid/no scene
                }
            } else {
                defaultVal = "SCENE_COUNT";
            }
        }

        return {
            type: cType,
            default_value: defaultVal
        };
    }

    /**
     * Check if member name suggests it's used for scene switching
     */
    function isSceneMemberName(name:String):Bool {
        var lower = name.toLowerCase();
        return lower.indexOf("scene") >= 0 ||
               lower.indexOf("level") >= 0 ||
               lower == "nextscene" ||
               lower == "targetscene";
    }

    /**
     * Extract string value from expression
     */
    function extractStringValue(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            default: null;
        };
    }

    function complexTypeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): p.name;
            default: "Dynamic";
        }
    }

    function exprToDefault(e:Expr, cType:String):String {
        return switch (e.expr) {
            case EConst(CInt(v)):
                // For Vec3, convert single int to {v, v, v}
                if (cType == "Vec3") '{$v, $v, $v}' else v;
            case EConst(CFloat(f)):
                // For Vec3, convert single float to {f, f, f}
                if (cType == "Vec3") '{${f}f, ${f}f, ${f}f}' else '${f}f';
            case EConst(CString(s)): '"$s"';
            case EConst(CIdent("true")): "true";
            case EConst(CIdent("false")): "false";
            case EConst(CIdent("null")): "NULL";
            case EUnop(OpNeg, false, inner): '-${exprToDefault(inner, cType)}';
            case ENew(_, params), ECall(_, params):
                // Vec4/Vec3 constructor: new Vec4(x, y, z)
                if (cType == "Vec3" && params.length >= 3) {
                    var x = exprToDefault(params[0], "float");
                    var y = exprToDefault(params[1], "float");
                    var z = exprToDefault(params[2], "float");
                    '{$x, $y, $z}';
                } else {
                    defaultForType(cType);
                }
            default: defaultForType(cType);
        }
    }

    function defaultForType(cType:String):String {
        return switch (cType) {
            case "float": "0.0f";
            case "int32_t": "0";
            case "bool": "false";
            case "Vec3": "{0, 0, 0}";
            case "const char*": "NULL";
            case "SceneId": "SCENE_COUNT";
            default: "0";
        }
    }

    /**
     * Find lifecycle method registrations in constructor
     */
    function findLifecycles():{init:Expr, update:Expr, remove:Expr} {
        var result = {init: null, update: null, remove: null};

        var constructor = methodMap.get("new");
        if (constructor == null || constructor.expr == null) return result;

        scanForLifecycles(constructor.expr, result);
        return result;
    }

    function scanForLifecycles(e:Expr, result:{init:Expr, update:Expr, remove:Expr}):Void {
        if (e == null) return;

        switch (e.expr) {
            case ECall(func, params):
                // Look for notifyOnInit, notifyOnUpdate, notifyOnRemove
                var funcName = getFuncName(func);
                if (funcName != null && params.length > 0) {
                    var callback = params[0];
                    var body = resolveCallback(callback);

                    switch (funcName) {
                        case "notifyOnInit", "notifyOnReady":
                            result.init = body;
                        case "notifyOnUpdate":
                            result.update = body;
                        case "notifyOnRemove":
                            result.remove = body;
                    }
                }
                // Recurse into call arguments
                for (p in params) scanForLifecycles(p, result);

            case EBlock(exprs):
                for (expr in exprs) scanForLifecycles(expr, result);

            case EIf(_, eif, eelse):
                scanForLifecycles(eif, result);
                if (eelse != null) scanForLifecycles(eelse, result);

            case EFunction(_, f):
                // Don't recurse into nested functions here
                return;

            default:
                e.iter(function(sub) scanForLifecycles(sub, result));
        }
    }

    function getFuncName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(s)): s;
            case EField(_, field): field;
            default: null;
        }
    }

    /**
     * Resolve a callback to its body expression
     */
    function resolveCallback(e:Expr):Expr {
        return switch (e.expr) {
            // Inline function: function() { ... }
            case EFunction(_, f):
                f.expr;

            // Method reference: this.onUpdate or onUpdate
            case EField(_, methodName):
                var method = methodMap.get(methodName);
                method != null ? method.expr : null;

            case EConst(CIdent(methodName)):
                var method = methodMap.get(methodName);
                method != null ? method.expr : null;

            default: null;
        }
    }

    /**
     * Emit a function body as C code
     */
    function emitFunction(body:Expr):{code:Array<String>, needsObj:Bool, needsDt:Bool, inputButtons:Array<String>, hasTransform:Bool, hasScene:Bool, targetScene:String, needsInitialScale:Bool} {
        var emitter = new N64CEmitter(className, memberNames, vec4Exprs);
        var code:Array<String> = [];

        // Process statements
        switch (body.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var stmt = emitStatement(emitter, expr);
                    if (stmt != null && stmt != "") {
                        code.push(stmt);
                    }
                }
            default:
                var stmt = emitStatement(emitter, body);
                if (stmt != null && stmt != "") {
                    code.push(stmt);
                }
        }

        return {
            code: code,
            needsObj: emitter.requiresObj(),
            needsDt: emitter.requiresDt(),
            inputButtons: emitter.getInputButtons(),
            hasTransform: emitter.hasTransformOps(),
            hasScene: emitter.hasSceneOps(),
            targetScene: emitter.getTargetScene(),
            needsInitialScale: emitter.requiresInitialScale()
        };
    }

    /**
     * Emit a single statement as C code
     */
    function emitStatement(emitter:N64CEmitter, e:Expr):String {
        if (e == null) return null;

        // Handle control flow specially for proper formatting
        switch (e.expr) {
            case EIf(econd, eif, eelse):
                return emitIfStatement(emitter, econd, eif, eelse);

            case EWhile(econd, body, normalWhile):
                return emitWhileStatement(emitter, econd, body, normalWhile);

            case EFor(it, body):
                return emitForStatement(emitter, it, body);

            case EBlock(exprs):
                var stmts:Array<String> = [];
                for (expr in exprs) {
                    var s = emitStatement(emitter, expr);
                    if (s != null && s != "") stmts.push(s);
                }
                return stmts.join(" ");

            default:
                var code = emitter.emitExpr(e);
                if (code != "" && code != "/* unsupported expr */") {
                    // Add semicolon if not already a block statement
                    if (!code.endsWith("}") && !code.endsWith(";")) {
                        code += ";";
                    }
                    return code;
                }
                return null;
        }
    }

    function emitIfStatement(emitter:N64CEmitter, econd:Expr, eif:Expr, eelse:Expr):String {
        var cond = emitter.emitExpr(econd);
        var thenCode = emitStatement(emitter, eif);

        var result = 'if ($cond) { ${thenCode != null ? thenCode : ""} }';

        if (eelse != null) {
            var elseCode = emitStatement(emitter, eelse);
            result += ' else { ${elseCode != null ? elseCode : ""} }';
        }

        return result;
    }

    function emitWhileStatement(emitter:N64CEmitter, econd:Expr, body:Expr, normalWhile:Bool):String {
        var cond = emitter.emitExpr(econd);
        var bodyCode = emitStatement(emitter, body);

        if (normalWhile) {
            return 'while ($cond) { ${bodyCode != null ? bodyCode : ""} }';
        } else {
            return 'do { ${bodyCode != null ? bodyCode : ""} } while ($cond);';
        }
    }

    function emitForStatement(emitter:N64CEmitter, it:Expr, body:Expr):String {
        // Haxe for loops are complex - emit as comment + body for now
        var bodyCode = emitStatement(emitter, body);
        return '/* for loop */ { ${bodyCode != null ? bodyCode : ""} }';
    }
}
#end
