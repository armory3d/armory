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
                    default_value: serializeIRNode(m.defaultValue)
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
                        ctype: p.ctype
                    });
                }
                functionsArr.push({
                    name: f.name,
                    c_name: f.cName,
                    return_type: f.returnType,
                    params: paramsArr,
                    body: [for (n in f.body) serializeIRNode(n)],
                    is_public: f.isPublic
                });
            }

            // Generate struct_type and struct_def for signals with 2+ args
            for (sig in ir.meta.signals) {
                var argCount = sig.arg_types.length;
                if (argCount >= 2) {
                    sig.struct_type = '${ir.cName}_${sig.name}_payload_t';
                    var lines:Array<String> = ['typedef struct {'];
                    for (i in 0...argCount) {
                        lines.push('    ${sig.arg_types[i]} arg$i;');
                    }
                    lines.push('} ${sig.struct_type};');
                    sig.struct_def = lines.join('\n');
                }
            }

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

        var json = Json.stringify(output, null, "  ");

        var defines = Context.getDefines();
        var buildDir = defines.get("arm_build_dir");
        if (buildDir == null) buildDir = "build";

        var outPath = buildDir + "/n64_autoloads.json";
        try {
            var dir = haxe.io.Path.directory(outPath);
            if (dir != "" && !FileSystem.exists(dir)) {
                FileSystem.createDirectory(dir);
            }
            File.saveContent(outPath, json);
        } catch (e:Dynamic) {
            Context.error('Failed to write n64_autoloads.json: $e', Context.currentPos());
        }
    }

    static function serializeIRNode(node:IRNode):Dynamic {
        if (node == null) return null;

        var obj:Dynamic = { type: node.type };

        if (node.value != null) obj.value = node.value;
        if (node.children != null && node.children.length > 0) {
            obj.children = [for (c in node.children) serializeIRNode(c)];
        }
        if (node.args != null && node.args.length > 0) {
            obj.args = [for (a in node.args) serializeIRNode(a)];
        }
        if (node.method != null) obj.method = node.method;
        if (node.object != null) obj.object = serializeIRNode(node.object);
        if (node.props != null) obj.props = node.props;
        if (node.c_code != null) obj.c_code = node.c_code;
        if (node.c_func != null) obj.c_func = node.c_func;

        return obj;
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

    // Call converters
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
                        var haxeType = t != null ? complexTypeToString(t) : "";
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
                case FVar(t, _): fieldType = t != null ? complexTypeToString(t) : null;
                case FProp(_, _, t, _): fieldType = t != null ? complexTypeToString(t) : null;
                default:
            }
            if (fieldType == className) continue;

            switch (field.kind) {
                case FVar(t, e):
                    var haxeType = t != null ? complexTypeToString(t) : "Dynamic";
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
                    var haxeType = t != null ? complexTypeToString(t) : "Dynamic";
                    memberTypes.set(field.name, haxeType);

                    var member = extractMember(field.name, t, e);
                    if (member != null) {
                        members.set(field.name, member);
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

        var haxeType = t != null ? complexTypeToString(t) : "Dynamic";
        if (!TypeMap.isSupported(haxeType)) return null;

        var defaultNode:IRNode = e != null ? exprToIR(e) : null;

        return {
            haxeType: haxeType,
            ctype: TypeMap.getCType(haxeType),
            defaultValue: defaultNode
        };
    }

    function extractFunction(name:String, func:Function, isPublic:Bool):AutoloadFunctionIR {
        // Extract parameters
        var params:Array<AutoloadParamIR> = [];
        for (arg in func.args) {
            var haxeType = arg.type != null ? complexTypeToString(arg.type) : "Dynamic";
            var ctype = TypeMap.getCType(haxeType);
            if (ctype == null) ctype = "void*"; // Unknown types become void*
            params.push({
                name: arg.name,
                haxeType: haxeType,
                ctype: ctype
            });
            // Track parameter types for local variable resolution
            localVarTypes.set(arg.name, haxeType);
        }

        // Extract return type
        var returnHaxeType = func.ret != null ? complexTypeToString(func.ret) : "Void";
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

    function complexTypeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): p.name;
            default: "Dynamic";
        };
    }

    // ========================================================================
    // Expression to IR conversion (shared with TraitExtractor)
    // ========================================================================

    public function exprToIR(e:Expr):IRNode {
        if (e == null) return { type: "skip" };

        switch (e.expr) {
            case EConst(c):
                return constToIR(c);

            case EBinop(op, e1, e2):
                return {
                    type: "binop",
                    value: binopToString(op),
                    children: [exprToIR(e1), exprToIR(e2)]
                };

            case EUnop(op, postFix, e1):
                return {
                    type: "unop",
                    value: unopToString(op),
                    props: { postfix: postFix },
                    children: [exprToIR(e1)]
                };

            case EField(obj, field):
                return {
                    type: "field_access",
                    value: field,
                    object: exprToIR(obj)
                };

            case ECall(callExpr, params):
                return convertCall(callExpr, params);

            case EArray(e1, e2):
                return {
                    type: "array_access",
                    children: [exprToIR(e1), exprToIR(e2)]
                };

            case EVars(vars):
                for (v in vars) {
                    localVarTypes.set(v.name, v.type != null ? complexTypeToString(v.type) : "Dynamic");
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
                var children = [exprToIR(econd), exprToIR(eif)];
                if (eelse != null) children.push(exprToIR(eelse));
                return {
                    type: "if",
                    children: children
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

            default:
                return { type: "skip" };
        }
    }

    function constToIR(c:Constant):IRNode {
        return switch (c) {
            case CInt(v): { type: "literal", value: v, props: { literal_type: "int" } };
            case CFloat(f): { type: "literal", value: f, props: { literal_type: "float" } };
            case CString(s): { type: "literal", value: s, props: { literal_type: "string" } };
            case CIdent(s):
                if (s == "true" || s == "false") {
                    { type: "literal", value: s, props: { literal_type: "bool" } };
                } else if (s == "null") {
                    { type: "literal", value: "NULL", props: { literal_type: "null" } };
                } else {
                    { type: "ident", value: s };
                }
            default: { type: "skip" };
        };
    }

    function binopToString(op:Binop):String {
        return switch (op) {
            case OpAdd: "+";
            case OpSub: "-";
            case OpMult: "*";
            case OpDiv: "/";
            case OpMod: "%";
            case OpAssign: "=";
            case OpEq: "==";
            case OpNotEq: "!=";
            case OpGt: ">";
            case OpGte: ">=";
            case OpLt: "<";
            case OpLte: "<=";
            case OpAnd: "&&";
            case OpOr: "||";
            case OpBoolAnd: "&&";
            case OpBoolOr: "||";
            case OpAssignOp(op): binopToString(op) + "=";
            default: "?";
        };
    }

    function unopToString(op:Unop):String {
        return switch (op) {
            case OpNot: "!";
            case OpNeg: "-";
            case OpIncrement: "++";
            case OpDecrement: "--";
            default: "?";
        };
    }

    function convertCall(callExpr:Expr, params:Array<Expr>):IRNode {
        var args = [for (p in params) exprToIR(p)];

        // Try converters first
        switch (callExpr.expr) {
            case EField(obj, method):
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
            case EConst(CIdent(s)): memberTypes.get(s);
            case EField(_, field): memberTypes.get(field);
            default: null;
        };
    }

    public function getMemberType(name:String):String {
        return memberTypes.get(name);
    }

    public function extractStringArg(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            default: null;
        };
    }

    public function addSignalHandler(handlerName:String, signalName:String):Void {
        meta.signal_handlers.push({
            handler_name: handlerName,
            signal_name: signalName
        });
    }

    public function updateSignalArgTypes(signalName:String, params:Array<Expr>):Void {
        for (sig in meta.signals) {
            if (sig.name == signalName && sig.arg_types.length == 0) {
                for (p in params) {
                    var ctype = inferExprType(p);
                    sig.arg_types.push(ctype);
                }
                break;
            }
        }
    }

    public function inferExprType(e:Expr):String {
        return switch (e.expr) {
            case EConst(CInt(_)): "int32_t";
            case EConst(CFloat(_)): "float";
            case EConst(CString(_)): "const char*";
            case EConst(CIdent(s)):
                if (s == "true" || s == "false") "bool";
                else {
                    var t = localVarTypes.get(s);
                    if (t == null) t = memberTypes.get(s);
                    t != null ? TypeMap.getCType(t) : "void*";
                }
            default: "void*";
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
            buttons_used: [],
            button_events: [],
            contact_events: [],
            signals: meta.signals,
            signal_handlers: meta.signal_handlers,
            global_signals: meta.global_signals
        };
    }

    public function getCName():String {
        return cName;
    }

    public function getMethod(name:String):Function {
        return methodMap.get(name);
    }

    public function getEvents():Map<String, Array<IRNode>> {
        // Autoloads don't have trait-style events, return empty map
        return new Map();
    }
}

#end
