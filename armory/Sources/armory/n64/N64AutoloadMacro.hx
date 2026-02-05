package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;
import haxe.macro.Expr.Function;
import haxe.macro.Type;
import haxe.Json;
import sys.io.File;
import sys.FileSystem;

// Import shared components
import armory.n64.IRTypes;
import armory.n64.N64MacroBase;
import armory.n64.mapping.Constants;
import armory.n64.mapping.TypeMap;
import armory.n64.mapping.SkipList;
import armory.n64.converters.ICallConverter;
import armory.n64.converters.VecCallConverter;
import armory.n64.converters.MathCallConverter;
import armory.n64.converters.SignalCallConverter;
import armory.n64.converters.StdCallConverter;
import armory.n64.converters.AutoloadCallConverter;
import armory.n64.converters.AudioCallConverter;
import armory.n64.converters.TweenCallConverter;
import armory.n64.converters.MapCallConverter;
import armory.n64.converters.ArrayCallConverter;

using haxe.macro.ExprTools;
using haxe.macro.TypeTools;
using StringTools;
using Lambda;

/**
 * N64 Autoload Macro
 *
 * Processes classes marked with @:n64Autoload metadata.
 * Autoloads are singleton-like classes that:
 * - Initialize once at engine startup (before scenes)
 * - Persist across scene changes
 * - Are globally accessible from traits and other autoloads
 *
 * Usage:
 *   @:n64Autoload(order=0)
 *   class GameEvents {
 *       public static var sceneLoaded: Signal = new Signal();
 *       public static function init() { ... }
 *   }
 */
class N64AutoloadMacro {
    static var autoloadData:Map<String, AutoloadIR> = new Map();
    static var initialized:Bool = false;

    /**
     * Called via --macro from khafile to register autoload processing.
     * This adds @:build metadata to the user's arm package where autoloads live.
     */
    public static function register():Void {
        #if macro
        // Add build macro to all types in the 'arm' package (user code)
        // The build() function will then check for @:n64Autoload metadata
        haxe.macro.Compiler.addGlobalMetadata(
            "arm",  // user package
            "@:build(armory.n64.N64AutoloadMacro.build())",
            true,   // recursive
            true,   // toTypes
            false   // toFields
        );
        #end
    }

    macro public static function build():Array<Field> {
        var defines = Context.getDefines();
        if (!defines.exists("arm_target_n64")) {
            return null;
        }

        if (!initialized) {
            initialized = true;
            Context.onAfterTyping(function(_) {
                writeAutoloadJson();
            });
        }

        var localClass = Context.getLocalClass();
        if (localClass == null) return null;

        var cls = localClass.get();
        var className = cls.name;
        var modulePath = cls.module;

        // Skip internal/engine classes
        if (modulePath.indexOf("iron.") == 0 || modulePath.indexOf("armory.") == 0) {
            return null;
        }

        // Check for @:n64Autoload metadata
        var order = getAutoloadOrder(cls.meta.get());
        if (order == null) {
            return null; // Not an autoload class
        }

        var fields = Context.getBuildFields();

        // Extract autoload IR
        var extractor = new AutoloadExtractor(className, modulePath, fields, order);
        var autoloadIR = extractor.extract();

        if (autoloadIR != null) {
            autoloadData.set(className, autoloadIR);
        }

        return null;
    }

    static function getAutoloadOrder(meta:Array<MetadataEntry>):Null<Int> {
        for (m in meta) {
            if (m.name == ":n64Autoload" || m.name == "n64Autoload") {
                // Default order is 100 if not specified
                var order = 100;
                if (m.params != null) {
                    for (param in m.params) {
                        switch (param.expr) {
                            case EBinop(OpAssign, e1, e2):
                                // order=N syntax
                                switch (e1.expr) {
                                    case EConst(CIdent("order")):
                                        switch (e2.expr) {
                                            case EConst(CInt(v)): order = Std.parseInt(v);
                                            default:
                                        }
                                    default:
                                }
                            case EConst(CInt(v)):
                                // Just a number: @:n64Autoload(5)
                                order = Std.parseInt(v);
                            default:
                        }
                    }
                }
                return order;
            }
        }
        return null;
    }

    static function writeAutoloadJson():Void {
        if (!autoloadData.keys().hasNext()) return;

        var autoloads:Dynamic = {};

        for (name in autoloadData.keys()) {
            var ir = autoloadData.get(name);

            // Convert members
            var membersArr:Array<Dynamic> = [];
            for (memberName in ir.members.keys()) {
                var m = ir.members.get(memberName);
                membersArr.push({
                    name: memberName,
                    type: m.haxeType,
                    ctype: m.ctype,
                    default_value: N64MacroBase.serializeIRNode(m.defaultValue)
                });
            }

            // Convert functions
            var functionsArr:Array<Dynamic> = [];
            for (funcName in ir.functions.keys()) {
                var f = ir.functions.get(funcName);
                var paramsArr:Array<Dynamic> = [];
                for (p in f.params) {
                    paramsArr.push({
                        name: p.name,
                        type: p.haxeType,
                        ctype: p.ctype,
                        optional: p.optional,
                        default_value: p.defaultValue != null ? N64MacroBase.serializeIRNode(p.defaultValue) : null
                    });
                }
                functionsArr.push({
                    name: f.name,
                    c_name: f.cName,
                    return_type: f.returnType,
                    params: paramsArr,
                    body: [for (n in f.body) N64MacroBase.serializeIRNode(n)],
                    is_public: f.isPublic
                });
            }

            // Generate struct_type and struct_def for signals with 2+ args
            N64MacroBase.generateSignalStructs(ir.meta.signals, ir.cName);

            // Generate preambles for signal handlers
            N64MacroBase.generateSignalHandlerPreambles(
                ir.meta.signal_handlers,
                ir.meta.signals,
                '${ir.name}Data'
            );

            Reflect.setField(autoloads, name, {
                module: ir.module,
                c_name: ir.cName,
                order: ir.order,
                members: membersArr,
                functions: functionsArr,
                has_init: ir.hasInit,
                meta: ir.meta
            });
        }

        var output:Dynamic = {
            ir_version: 1,
            autoloads: autoloads
        };

        N64MacroBase.writeJsonFile("n64_autoloads.json", output);
    }
}

// ============================================================================
// Autoload Extractor
// ============================================================================

class AutoloadExtractor implements IExtractorContext {
    var className:String;
    var modulePath:String;
    var fields:Array<Field>;
    var order:Int;
    var members:Map<String, MemberIR>;
    var functions:Map<String, AutoloadFunctionIR>;
    var methodMap:Map<String, Function>;
    public var meta(default, null):AutoloadMeta;
    var localVarTypes:Map<String, String>;
    var memberTypes:Map<String, String>;
    public var cName(default, null):String;
    var hasInit:Bool;

    // Call converters - subset for autoloads
    // Autoloads don't need: Physics, Transform, Input, Object, Scene, Canvas converters
    // because they don't have access to 'object' or game loop context.
    // Add converters here if autoloads need to call those APIs in the future.
    var converters:Array<ICallConverter>;

    public function new(className:String, modulePath:String, fields:Array<Field>, order:Int) {
        this.className = className;
        this.modulePath = modulePath;
        this.fields = fields;
        this.order = order;
        this.members = new Map();
        this.functions = new Map();
        this.methodMap = new Map();
        this.localVarTypes = new Map();
        this.memberTypes = new Map();
        this.hasInit = false;
        this.meta = {
            order: order,
            signals: [],
            signal_handlers: [],
            global_signals: []
        };

        // Generate C-safe name
        this.cName = className.toLowerCase();

        // Initialize call converters (subset relevant for autoloads)
        this.converters = [
            new VecCallConverter(),
            new MathCallConverter(),
            new SignalCallConverter(),
            new StdCallConverter(),
            new AutoloadCallConverter(),
            new AudioCallConverter(),
            new TweenCallConverter(),
            new MapCallConverter(),
            new ArrayCallConverter(),
        ];
    }

    public function extract():AutoloadIR {
        // Pass 1: Collect all methods and detect singleton pattern
        var isSingleton = false;
        for (field in fields) {
            switch (field.kind) {
                case FFun(func):
                    methodMap.set(field.name, func);
                case FVar(t, e):
                    // Detect singleton pattern: static field of the same type as the class
                    if (hasAccess(field.access, AStatic)) {
                        var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "";
                        if (haxeType == className) {
                            isSingleton = true;
                        }
                    }
                default:
            }
        }

        // Pass 2: Extract static members and functions
        for (field in fields) {
            var isStatic = hasAccess(field.access, AStatic);

            // For singletons, also process instance members/methods
            // Skip fields of the same type as the class (singleton instance) and constructor
            if (!isStatic && !isSingleton) continue;
            if (field.name == "new") continue;

            // Skip fields whose type matches the class itself (e.g., singleton instance fields)
            var fieldType:String = null;
            switch (field.kind) {
                case FVar(t, _): fieldType = t != null ? N64MacroBase.complexTypeToString(t) : null;
                case FProp(_, _, t, _): fieldType = t != null ? N64MacroBase.complexTypeToString(t) : null;
                default:
            }
            if (fieldType == className) continue;

            switch (field.kind) {
                case FVar(t, e):
                    var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "Dynamic";
                    memberTypes.set(field.name, haxeType);

                    // Signal members tracked separately
                    if (haxeType == "Signal") {
                        var maxSubs = 16;
                        if (field.meta != null) {
                            for (m in field.meta) {
                                if (m.name == ":n64MaxSubs" || m.name == "n64MaxSubs") {
                                    if (m.params != null && m.params.length > 0) {
                                        switch (m.params[0].expr) {
                                            case EConst(CInt(v)): maxSubs = Std.parseInt(v);
                                            default:
                                        }
                                    }
                                }
                            }
                        }
                        meta.signals.push({
                            name: field.name,
                            arg_types: [],
                            max_subs: maxSubs
                        });
                    } else {
                        var member = extractMember(field.name, t, e);
                        if (member != null) {
                            members.set(field.name, member);
                        }
                    }

                case FProp(get, set, t, e):
                    // Haxe property with getter/setter (e.g., public var volume(default, set): Float)
                    // These have a backing field that we need to track as a member
                    var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "Dynamic";
                    memberTypes.set(field.name, haxeType);

                    // Signal properties should be tracked separately like FVar signals
                    if (haxeType == "Signal") {
                        var maxSubs = 16;
                        if (field.meta != null) {
                            for (m in field.meta) {
                                if (m.name == ":n64MaxSubs" || m.name == "n64MaxSubs") {
                                    if (m.params != null && m.params.length > 0) {
                                        switch (m.params[0].expr) {
                                            case EConst(CInt(v)): maxSubs = Std.parseInt(v);
                                            default:
                                        }
                                    }
                                }
                            }
                        }
                        meta.signals.push({
                            name: field.name,
                            arg_types: [],
                            max_subs: maxSubs
                        });
                    } else {
                        var member = extractMember(field.name, t, e);
                        if (member != null) {
                            members.set(field.name, member);
                        }
                    }

                case FFun(func):
                    var isPublic = hasAccess(field.access, APublic);
                    var funcIR = extractFunction(field.name, func, isPublic);
                    if (funcIR != null) {
                        functions.set(field.name, funcIR);
                        if (field.name == "init") {
                            hasInit = true;
                        }
                    }
                default:
            }
        }

        return {
            name: className,
            module: modulePath,
            cName: cName,
            order: order,
            members: members,
            functions: functions,
            hasInit: hasInit,
            meta: meta
        };
    }

    function hasAccess(access:Array<Access>, target:Access):Bool {
        if (access == null) return false;
        for (a in access) {
            if (Type.enumEq(a, target)) return true;
        }
        return false;
    }

    function extractMember(name:String, t:ComplexType, e:Expr):MemberIR {
        if (SkipList.shouldSkipMember(name)) return null;

        var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "Dynamic";

        // First check standard type map
        if (TypeMap.isSupported(haxeType)) {
            var defaultNode:IRNode = e != null ? exprToIR(e) : null;
            return {
                haxeType: haxeType,
                ctype: TypeMap.getCType(haxeType),
                defaultValue: defaultNode
            };
        }

        // Check if it's a trait type (extends iron.Trait)
        // Use ComplexType directly for better type resolution
        var traitCType = resolveTraitCTypeFromComplexType(t);
        if (traitCType != null) {
            var defaultNode:IRNode = e != null ? exprToIR(e) : null;
            return {
                haxeType: haxeType,
                ctype: traitCType,
                defaultValue: defaultNode
            };
        }

        // Unknown type - skip
        return null;
    }

    /**
     * Resolve trait C type from ComplexType - uses proper type resolution
     */
    function resolveTraitCTypeFromComplexType(ct:ComplexType):String {
        if (ct == null) return null;

        try {
            // Convert ComplexType to Type using the compiler's type resolution
            var type = Context.resolveType(ct, Context.currentPos());
            if (type == null) return null;

            var classType = type.getClass();
            if (classType == null) return null;

            if (extendsIronTrait(classType)) {
                // Found a trait - compute c_name
                var modulePath = classType.module;
                var className = classType.name;
                var moduleParts = modulePath.split(".");
                var lastModulePart = moduleParts[moduleParts.length - 1];

                var c_name:String;
                if (lastModulePart.toLowerCase() == className.toLowerCase()) {
                    c_name = modulePath.replace(".", "_").toLowerCase();
                } else {
                    c_name = (modulePath.replace(".", "_") + "_" + className).toLowerCase();
                }
                return c_name + "Data*";
            }
        } catch (e:Dynamic) {
            // Type resolution failed
        }
        return null;
    }

    /**
     * Check if a type name is a trait (extends iron.Trait) and return its C type.
     * Returns null if not a trait.
     *
     * Example: "Player" or "arm.player.Player" -> "arm_player_playerData*"
     */
    function resolveTraitCType(typeName:String):String {
        try {
            var type = Context.getType(typeName);
            if (type == null) {
                // Try with common package prefixes
                for (prefix in ["arm.", "arm.node.", "arm.player.", "arm.level.", "arm.autoload.", ""]) {
                    try {
                        type = Context.getType(prefix + typeName);
                        if (type != null) break;
                    } catch (e:Dynamic) {}
                }
            }

            if (type != null) {
                var classType = type.getClass();
                if (classType != null && extendsIronTrait(classType)) {
                    // Found a trait - compute c_name
                    var modulePath = classType.module;
                    var className = classType.name;
                    var moduleParts = modulePath.split(".");
                    var lastModulePart = moduleParts[moduleParts.length - 1];

                    var c_name:String;
                    if (lastModulePart.toLowerCase() == className.toLowerCase()) {
                        c_name = modulePath.replace(".", "_").toLowerCase();
                    } else {
                        c_name = (modulePath.replace(".", "_") + "_" + className).toLowerCase();
                    }
                    return c_name + "Data*";
                }
            }
        } catch (e:Dynamic) {
            // Type resolution failed
        }
        return null;
    }

    /**
     * Check if a class extends iron.Trait (directly or indirectly)
     */
    function extendsIronTrait(classType:ClassType):Bool {
        if (classType == null) return false;

        var superClass = classType.superClass;
        while (superClass != null) {
            var superClassType = superClass.t.get();
            // For iron.Trait: module="iron.Trait", name="Trait"
            // Check: module ends with "iron.Trait" OR (module=="iron" and name=="Trait")
            if ((superClassType.module == "iron.Trait" && superClassType.name == "Trait") ||
                (superClassType.module == "iron" && superClassType.name == "Trait")) {
                return true;
            }
            superClass = superClassType.superClass;
        }
        return false;
    }

    function extractFunction(name:String, func:Function, isPublic:Bool):AutoloadFunctionIR {
        // Extract parameters
        var params:Array<AutoloadParamIR> = [];
        for (arg in func.args) {
            var haxeType = arg.type != null ? N64MacroBase.complexTypeToString(arg.type) : "Dynamic";
            var ctype = TypeMap.getCType(haxeType);
            if (ctype == null) ctype = "void*"; // Unknown types become void*

            // Handle optional parameters with default values
            var defaultVal:IRNode = null;
            if (arg.value != null) {
                defaultVal = exprToIR(arg.value);
            }

            params.push({
                name: arg.name,
                haxeType: haxeType,
                ctype: ctype,
                optional: arg.opt || arg.value != null,
                defaultValue: defaultVal
            });
            // Track parameter types for local variable resolution
            localVarTypes.set(arg.name, haxeType);
        }

        // Extract return type
        var returnHaxeType = func.ret != null ? N64MacroBase.complexTypeToString(func.ret) : "Void";
        var returnType = returnHaxeType == "Void" ? "void" : TypeMap.getCType(returnHaxeType);
        if (returnType == null) returnType = "void";

        // Extract body
        var body:Array<IRNode> = [];
        if (func.expr != null) {
            extractFunctionBody(func.expr, body);
        }

        return {
            name: name,
            cName: '${cName}_$name',
            returnType: returnType,
            params: params,
            body: body,
            isPublic: isPublic
        };
    }

    function extractFunctionBody(e:Expr, statements:Array<IRNode>):Void {
        if (e == null) return;

        switch (e.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var node = exprToIR(expr);
                    if (node != null && node.type != "skip") {
                        statements.push(node);
                    }
                }
            default:
                var node = exprToIR(e);
                if (node != null && node.type != "skip") {
                    statements.push(node);
                }
        }
    }

    // ========================================================================
    // Expression to IR conversion (shared with TraitExtractor)
    // ========================================================================

    public function exprToIR(e:Expr):IRNode {
        if (e == null) return { type: "skip" };

        switch (e.expr) {
            case EConst(c):
                return N64MacroBase.constToIR(c);

            case EBinop(op, e1, e2):
                return {
                    type: "binop",
                    value: N64MacroBase.binopToString(op),
                    children: [exprToIR(e1), exprToIR(e2)]
                };

            case EUnop(op, postFix, e1):
                return {
                    type: "unop",
                    value: N64MacroBase.unopToString(op),
                    props: { postfix: postFix },
                    children: [exprToIR(e1)]
                };

            case EField(obj, field):
                // Check for Time.delta / Time.scale special cases
                switch (obj.expr) {
                    case EConst(CIdent("Time")):
                        if (field == "delta") {
                            // Time.delta -> time_delta (global variable from system/time.h)
                            return { type: "ident", value: "time_delta" };
                        } else if (field == "scale") {
                            // Time.scale -> time_scale (global variable from system/time.h)
                            return { type: "ident", value: "time_scale" };
                        } else if (field == "fixedStep") {
                            // Time.fixedStep -> time_fixed_step (global variable from system/time.h)
                            return { type: "ident", value: "time_fixed_step" };
                        }
                    default:
                }

                // Check for Array.length on typed array expressions
                if (field == "length") {
                    var objType = getExprType(obj);
                    if (TypeMap.isArrayType(objType)) {
                        // Convert obj to IR first, then wrap with length access
                        return {
                            type: "field_access",
                            value: "count",  // .length -> .count for C arrays
                            object: exprToIR(obj)
                        };
                    }
                }

                return {
                    type: "field_access",
                    value: field,
                    object: exprToIR(obj)
                };

            case ECall(callExpr, params):
                return convertCall(callExpr, params);

            case EArray(e1, e2):
                // Check if this is a Map or Array access on a typed member
                var objType = getExprType(e1);
                if (TypeMap.isMapType(objType)) {
                    var cType = TypeMap.getCType(objType);
                    var mapExpr = getExprAccessPath(e1);
                    return {
                        type: "map_get",
                        value: cType,
                        props: { map_expr: mapExpr },
                        children: [exprToIR(e2)]
                    };
                } else if (TypeMap.isArrayType(objType)) {
                    var cType = TypeMap.getCType(objType);
                    var arrayExpr = getExprAccessPath(e1);
                    if (arrayExpr != "") {
                        // Simple member/local array
                        return {
                            type: "array_get",
                            value: cType,
                            props: { array_expr: arrayExpr },
                            children: [exprToIR(e2)]
                        };
                    } else {
                        // Nested expression (e.g., channels[key][i])
                        // Pass the inner expression as IR node
                        return {
                            type: "array_get_nested",
                            value: cType,
                            children: [exprToIR(e1), exprToIR(e2)]
                        };
                    }
                }
                return {
                    type: "array_access",
                    children: [exprToIR(e1), exprToIR(e2)]
                };

            case EVars(vars):
                for (v in vars) {
                    localVarTypes.set(v.name, v.type != null ? N64MacroBase.complexTypeToString(v.type) : "Dynamic");
                }
                if (vars.length == 1) {
                    var v = vars[0];
                    return {
                        type: "var_decl",
                        value: v.name,
                        props: { var_type: TypeMap.getCType(localVarTypes.get(v.name)) },
                        children: v.expr != null ? [exprToIR(v.expr)] : null
                    };
                } else {
                    var varDecls:Array<IRNode> = [];
                    for (v in vars) {
                        varDecls.push({
                            type: "var_decl",
                            value: v.name,
                            props: { var_type: TypeMap.getCType(localVarTypes.get(v.name)) },
                            children: v.expr != null ? [exprToIR(v.expr)] : null
                        });
                    }
                    return { type: "block", children: varDecls };
                }

            case EIf(econd, eif, eelse):
                // Use same IR format as traits: condition in children[0], bodies in props
                var thenNodes:Array<IRNode> = [];
                extractFunctionBody(eif, thenNodes);

                var elseNodes:Array<IRNode> = null;
                if (eelse != null) {
                    elseNodes = [];
                    extractFunctionBody(eelse, elseNodes);
                }

                return {
                    type: "if",
                    children: [exprToIR(econd)],
                    props: {
                        then: thenNodes,
                        else_: elseNodes
                    }
                };

            case EWhile(econd, ebody, normalWhile):
                return {
                    type: normalWhile ? "while" : "do_while",
                    children: [exprToIR(econd), exprToIR(ebody)]
                };

            case EFor(it, ebody):
                return convertForLoop(it, ebody);

            case EBlock(exprs):
                return {
                    type: "block",
                    children: [for (ex in exprs) exprToIR(ex)]
                };

            case EReturn(retExpr):
                return {
                    type: "return",
                    children: retExpr != null ? [exprToIR(retExpr)] : null
                };

            case EBreak:
                return { type: "break" };

            case EContinue:
                return { type: "continue" };

            case EParenthesis(inner):
                return {
                    type: "paren",
                    children: [exprToIR(inner)]
                };

            case ETernary(econd, eif, eelse):
                return {
                    type: "ternary",
                    children: [exprToIR(econd), exprToIR(eif), exprToIR(eelse)]
                };

            case EArrayDecl(values):
                // Empty array declaration: [] -> empty_array
                // Non-empty array with values not yet supported
                if (values.length == 0) {
                    return { type: "empty_array" };
                }
                // For now, skip non-empty array literals
                return { type: "skip" };

            case ENew(typePath, params):
                // Handle constructor calls
                var typeName = typePath.name;
                if (typeName == "Tween") {
                    // Tween allocation from pool
                    return { type: "tween_alloc" };
                }
                // Generic new - skip for now
                return { type: "skip" };

            default:
                return { type: "skip" };
        }
    }

    function convertCall(callExpr:Expr, params:Array<Expr>):IRNode {
        var args = [for (p in params) exprToIR(p)];

        // Try converters first
        switch (callExpr.expr) {
            case EField(obj, method):
                // Check for Time.time() special case
                switch (obj.expr) {
                    case EConst(CIdent("Time")):
                        if (method == "time") {
                            // Time.time() -> time_get()
                            return { type: "call", value: "time_get", args: [] };
                        }
                    default:
                }
                for (conv in converters) {
                    var result = conv.tryConvert(obj, method, args, params, this);
                    if (result != null) return result;
                }
                // Default field call
                return {
                    type: "method_call",
                    method: method,
                    object: exprToIR(obj),
                    args: args
                };

            case EConst(CIdent(funcName)):
                // Direct function call
                return {
                    type: "call",
                    value: funcName,
                    args: args
                };

            default:
                return { type: "skip" };
        }
    }

    function convertForLoop(it:Expr, body:Expr):IRNode {
        // Handle for (i in 0...10) pattern
        switch (it.expr) {
            case EBinop(OpIn, e1, e2):
                var varName = switch (e1.expr) {
                    case EConst(CIdent(s)): s;
                    default: "_i";
                };
                localVarTypes.set(varName, "Int");

                switch (e2.expr) {
                    case EBinop(OpInterval, start, end):
                        return {
                            type: "for_range",
                            value: varName,
                            children: [exprToIR(start), exprToIR(end), exprToIR(body)]
                        };
                    default:
                }
            default:
        }
        return { type: "skip" };
    }

    // ========================================================================
    // IExtractorContext implementation
    // ========================================================================

    public function getExprType(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(s)):
                // Check local vars first, then members
                if (localVarTypes.exists(s)) localVarTypes.get(s);
                else memberTypes.get(s);
            case EField(_, field): memberTypes.get(field);
            case EArray(obj, _):
                // For array access, get the element type
                var objType = getExprType(obj);
                if (TypeMap.isMapType(objType)) {
                    var mapTypes = TypeMap.getMapTypes(objType);
                    if (mapTypes != null) return mapTypes.value;
                } else if (TypeMap.isArrayType(objType)) {
                    return TypeMap.getArrayElementType(objType);
                }
                null;
            default: null;
        };
    }

    /**
     * Get the C access path for an expression (for member vs local).
     * For autoloads, members become "c_name_member" (global variable).
     * Locals remain just "member".
     */
    function getExprAccessPath(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)):
                if (memberTypes.exists(name)) cName + "_" + name;
                else name;
            case EField(_, field):
                cName + "_" + field;
            default:
                "";
        };
    }

    public function getMemberType(name:String):String {
        return memberTypes.get(name);
    }

    public function getInheritedMemberType(name:String):String {
        // Autoloads don't have inheritance - always return null
        return null;
    }

    public function getLocalVarType(name:String):String {
        return localVarTypes.exists(name) ? localVarTypes.get(name) : null;
    }

    public function extractStringArg(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            default: null;
        };
    }

    public function addSignalHandler(handlerName:String, signalName:String):Void {
        // Check if already tracked (avoid duplicates)
        for (h in meta.signal_handlers) {
            if (h.handler_name == handlerName) return;
        }

        meta.signal_handlers.push({
            handler_name: handlerName,
            signal_name: signalName
        });
    }

    public function updateSignalArgTypes(signalName:String, params:Array<Expr>):Void {
        for (sig in meta.signals) {
            if (sig.name == signalName && sig.arg_types.length == 0) {
                for (p in params) {
                    var haxeType = inferExprType(p);
                    var cType = TypeMap.getCType(haxeType);
                    sig.arg_types.push(cType);
                }
                break;
            }
        }
    }

    public function inferExprType(e:Expr):String {
        // Return Haxe types (consistent with N64TraitMacro)
        // Caller uses TypeMap.getCType() to convert to C types
        return switch (e.expr) {
            case EConst(CInt(_)): "Int";
            case EConst(CFloat(_)): "Float";
            case EConst(CString(_)): "String";
            case EConst(CIdent(s)):
                if (s == "true" || s == "false") "Bool";
                else {
                    var t = localVarTypes.get(s);
                    if (t == null) t = memberTypes.get(s);
                    t != null ? t : "Dynamic";
                }
            case EField(obj, field):
                // Could be object.transform, etc. - simplified for now
                "Dynamic";
            default: "Dynamic";
        };
    }

    public function getMeta():TraitMeta {
        // Return a TraitMeta-compatible structure
        // AutoloadMeta is a subset, so we create a compatible wrapper
        return {
            uses_input: false,
            uses_transform: false,
            mutates_transform: false,
            uses_time: false,
            uses_physics: false,
            uses_ui: false,
            uses_tween: false,
            uses_autoload: false,
            buttons_used: [],
            button_events: [],
            contact_events: [],
            signals: meta.signals,
            signal_handlers: meta.signal_handlers,
            global_signals: meta.global_signals,
            has_remove_update: false,
            has_remove_fixed_update: false,
            has_remove_late_update: false,
            has_remove_render2d: false
        };
    }

    public function getCName():String {
        return cName;
    }

    public function getParentName():String {
        // Autoloads don't have parent traits
        return null;
    }

    public function getMethod(name:String):Function {
        return methodMap.get(name);
    }

    public function getEvents():Map<String, Array<IRNode>> {
        // Autoloads don't have trait-style events, return empty map
        return new Map();
    }

    public function isAutoload():Bool {
        return true;
    }
}

#end