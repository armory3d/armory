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
 * N64 Trait Macro - Event-Driven Architecture
 *
 * Pipeline: Haxe AST → IR (JSON) → Python → C code
 *
 * This macro:
 * 1. Extracts trait members with ctype
 * 2. Detects event patterns (input, lifecycle) and extracts handlers
 * 3. Outputs clean JSON IR for Python to emit C code
 *
 * The macro is the SINGLE SOURCE OF TRUTH for semantics.
 * Python only does 1:1 IR→C translation.
 */
class N64TraitMacro {
    static var traitData:Map<String, TraitIR> = new Map();
    static var initialized:Bool = false;

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

        // Skip internal/engine traits
        if (modulePath.indexOf("iron.") == 0 || modulePath.indexOf("armory.") == 0) {
            return null;
        }

        var fields = Context.getBuildFields();

        // Extract trait IR
        var extractor = new TraitExtractor(className, modulePath, fields);
        var traitIR = extractor.extract();

        if (traitIR != null) {
            traitData.set(className, traitIR);
        }

        return null;
    }

    static function writeTraitJson():Void {
        if (traitData.keys().hasNext() == false) return;

        var traits:Dynamic = {};

        for (name in traitData.keys()) {
            var ir = traitData.get(name);

            // Skip empty traits
            var hasEvents = Lambda.count(ir.events) > 0;
            if (!hasEvents && !ir.needsData) continue;

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

            // Convert events
            var eventsObj:Dynamic = {};
            for (eventName in ir.events.keys()) {
                var eventNodes = ir.events.get(eventName);
                Reflect.setField(eventsObj, eventName, [for (n in eventNodes) serializeIRNode(n)]);
            }

            Reflect.setField(traits, name, {
                module: ir.module,
                c_name: ir.cName,
                members: membersArr,
                events: eventsObj,
                meta: ir.meta
            });
        }

        var output:Dynamic = {
            ir_version: 1,
            traits: traits
        };

        var json = Json.stringify(output, null, "  ");

        var defines = Context.getDefines();
        var buildDir = defines.get("arm_build_dir");
        if (buildDir == null) buildDir = "build";

        var outPath = buildDir + "/n64_traits.json";
        try {
            var dir = haxe.io.Path.directory(outPath);
            if (dir != "" && !FileSystem.exists(dir)) {
                FileSystem.createDirectory(dir);
            }
            File.saveContent(outPath, json);
        } catch (e:Dynamic) {
            Context.error('Failed to write n64_traits.json: $e', Context.currentPos());
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
        if (node.target != null) obj.target = node.target;
        if (node.method != null) obj.method = node.method;
        if (node.object != null) obj.object = serializeIRNode(node.object);
        if (node.props != null) obj.props = node.props;
        if (node.c_code != null) obj.c_code = node.c_code;

        return obj;
    }
}

// ============================================================================
// IR Types
// ============================================================================

typedef IRNode = {
    type: String,
    ?value: Dynamic,
    ?children: Array<IRNode>,
    ?args: Array<IRNode>,
    ?target: String,
    ?method: String,
    ?object: IRNode,
    ?props: Dynamic,
    ?c_code: String
}

typedef MemberIR = {
    haxeType: String,
    ctype: String,
    defaultValue: IRNode
}

typedef ButtonEventMeta = {
    event_name: String,      // e.g., "btn_a_started"
    button: String,          // normalized button name, e.g., "a"
    c_button: String,        // N64 constant, e.g., "N64_BTN_A"
    event_type: String       // "started", "released", or "down"
}

typedef TraitMeta = {
    uses_input: Bool,
    uses_transform: Bool,
    mutates_transform: Bool,   // True if trait modifies transform (translate, rotate, etc.)
    uses_time: Bool,
    uses_physics: Bool,
    buttons_used: Array<String>,
    button_events: Array<ButtonEventMeta>  // structured button event info
}

typedef TraitIR = {
    name: String,
    module: String,
    cName: String,
    needsData: Bool,
    members: Map<String, MemberIR>,
    events: Map<String, Array<IRNode>>,
    meta: TraitMeta
}

// ============================================================================
// Type Mapping (Haxe → C)
// ============================================================================

class TypeMap {
    public static var haxeToCType:Map<String, String> = [
        "Float" => "float",
        "float" => "float",
        "Int" => "int32_t",
        "int" => "int32_t",
        "Bool" => "bool",
        "bool" => "bool",
        "String" => "const char*",
        "SceneId" => "SceneId",
        "SceneFormat" => "SceneId",
        "TSceneFormat" => "SceneId",
        "Vec2" => "ArmVec2",
        "Vec3" => "ArmVec3",
        "Vec4" => "ArmVec4",
    ];

    public static function getCType(haxeType:String):String {
        return haxeToCType.exists(haxeType) ? haxeToCType.get(haxeType) : "void*";
    }

    public static function isSupported(haxeType:String):Bool {
        return haxeToCType.exists(haxeType);
    }
}

// ============================================================================
// Button Mapping (Armory → N64)
// ============================================================================

class ButtonMap {
    // Map common button names to N64 button identifiers
    // Matches config.py BUTTON_MAP
    public static var map:Map<String, String> = [
        // PlayStation-style
        "cross" => "a", "square" => "b", "circle" => "cright", "triangle" => "cleft",
        // Xbox-style
        "a" => "a", "b" => "cright", "x" => "b", "y" => "cleft",
        // Shoulders/Triggers
        "r1" => "cdown", "r2" => "r", "r3" => "cup",
        "l1" => "z", "l2" => "l", "l3" => "cup",
        // System
        "start" => "start", "options" => "start", "share" => "start",
        // D-Pad
        "up" => "dup", "down" => "ddown", "left" => "dleft", "right" => "dright",
        "dup" => "dup", "ddown" => "ddown", "dleft" => "dleft", "dright" => "dright",
        // C-Buttons direct
        "cup" => "cup", "cdown" => "cdown", "cleft" => "cleft", "cright" => "cright",
        // N64 native
        "l" => "l", "r" => "r", "z" => "z",
    ];

    // Map normalized button name to N64_BTN_* constant
    public static var n64Const:Map<String, String> = [
        "a" => "N64_BTN_A", "b" => "N64_BTN_B", "z" => "N64_BTN_Z",
        "start" => "N64_BTN_START", "l" => "N64_BTN_L", "r" => "N64_BTN_R",
        "dup" => "N64_BTN_DUP", "ddown" => "N64_BTN_DDOWN", "dleft" => "N64_BTN_DLEFT", "dright" => "N64_BTN_DRIGHT",
        "cup" => "N64_BTN_CUP", "cdown" => "N64_BTN_CDOWN", "cleft" => "N64_BTN_CLEFT", "cright" => "N64_BTN_CRIGHT",
    ];

    public static function normalize(button:String):String {
        var lower = button.toLowerCase();
        return map.exists(lower) ? map.get(lower) : lower;
    }

    public static function toN64Const(button:String):String {
        var normalized = normalize(button);
        return n64Const.exists(normalized) ? n64Const.get(normalized) : "N64_BTN_A";
    }
}

// ============================================================================
// Skip Lists
// ============================================================================

class SkipList {
    public static var members:Map<String, Bool> = [
        "object" => true, "transform" => true, "name" => true,
        "gamepad" => true, "keyboard" => true, "mouse" => true,
        "physics" => true, "rb" => true, "rigidBody" => true,
    ];

    public static var classes:Map<String, Bool> = [
        "PhysicsWorld" => true, "RigidBody" => true,
        "Tween" => true, "Audio" => true, "Network" => true,
    ];

    public static function shouldSkipMember(name:String):Bool {
        return members.exists(name);
    }

    public static function shouldSkipClass(name:String):Bool {
        return classes.exists(name);
    }
}

// ============================================================================
// Trait Extractor
// ============================================================================

class TraitExtractor {
    var className:String;
    var modulePath:String;
    var fields:Array<Field>;
    var members:Map<String, MemberIR>;
    var memberNames:Array<String>;
    var methodMap:Map<String, Function>;
    var events:Map<String, Array<IRNode>>;
    var meta:TraitMeta;
    var localVarTypes:Map<String, String>;  // Track local variable types

    public function new(className:String, modulePath:String, fields:Array<Field>) {
        this.className = className;
        this.modulePath = modulePath;
        this.fields = fields;
        this.members = new Map();
        this.memberNames = [];
        this.methodMap = new Map();
        this.events = new Map();
        this.localVarTypes = new Map();
        this.meta = {
            uses_input: false,
            uses_transform: false,
            mutates_transform: false,
            uses_time: false,
            uses_physics: false,
            buttons_used: [],
            button_events: []
        };
    }

    public function extract():TraitIR {
        // Pass 1: Extract members and methods
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    var member = extractMember(field.name, t, e);
                    if (member != null) {
                        members.set(field.name, member);
                        memberNames.push(field.name);
                    }
                case FFun(func):
                    methodMap.set(field.name, func);
                default:
            }
        }

        // Pass 2: Find lifecycle registrations and extract events
        var lifecycles = findLifecycles();

        // Pass 3: Convert lifecycle functions to events
        if (lifecycles.init != null) {
            extractEvents("on_ready", lifecycles.init);
        }
        if (lifecycles.update != null) {
            extractEvents("on_update", lifecycles.update);
        }
        if (lifecycles.fixed_update != null) {
            extractEvents("on_fixed_update", lifecycles.fixed_update);
        }
        if (lifecycles.late_update != null) {
            extractEvents("on_late_update", lifecycles.late_update);
        }
        if (lifecycles.remove != null) {
            extractEvents("on_remove", lifecycles.remove);
        }

        // Generate C-safe name
        // Avoid duplication if className is already the last part of modulePath
        // e.g., "arm.Rotator" + "Rotator" should become "arm_rotator", not "arm_rotator_rotator"
        var moduleParts = modulePath.split(".");
        var lastModulePart = moduleParts[moduleParts.length - 1];
        var cName:String;
        if (lastModulePart.toLowerCase() == className.toLowerCase()) {
            // Class name matches module name, just use module path
            cName = modulePath.replace(".", "_");
        } else {
            // Class name differs, append it
            cName = modulePath.replace(".", "_") + "_" + className;
        }

        return {
            name: className,
            module: modulePath,
            cName: cName.toLowerCase(),
            needsData: memberNames.length > 0,
            members: members,
            events: events,
            meta: meta
        };
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

    function complexTypeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): p.name;
            default: "Dynamic";
        };
    }

    function findLifecycles():{init:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr} {
        var result = {init: null, update: null, fixed_update: null, late_update: null, remove: null};
        var constructor = methodMap.get("new");
        if (constructor != null && constructor.expr != null) {
            scanForLifecycles(constructor.expr, result);
        }
        return result;
    }

    function scanForLifecycles(e:Expr, result:{init:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr}):Void {
        if (e == null) return;

        switch (e.expr) {
            case ECall(callExpr, params):
                var funcName = getFuncName(callExpr);
                if (params.length > 0) {
                    var body = resolveCallback(params[0]);
                    switch (funcName) {
                        case "notifyOnInit": result.init = body;
                        case "notifyOnUpdate": result.update = body;
                        case "notifyOnFixedUpdate": result.fixed_update = body;
                        case "notifyOnLateUpdate": result.late_update = body;
                        case "notifyOnRemove": result.remove = body;
                        default:
                    }
                }
                for (p in params) scanForLifecycles(p, result);
            case EBlock(exprs):
                for (expr in exprs) scanForLifecycles(expr, result);
            case EFunction(_, f):
                // Continue scanning inside function body to find nested lifecycle registrations
                // e.g., notifyOnUpdate(update) inside notifyOnInit(function() { ... })
                if (f.expr != null) scanForLifecycles(f.expr, result);
            default:
                e.iter(function(sub) scanForLifecycles(sub, result));
        }
    }

    function getFuncName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(s)): s;
            case EField(_, field): field;
            default: null;
        };
    }

    function resolveCallback(e:Expr):Expr {
        return switch (e.expr) {
            case EFunction(_, f): f.expr;
            case EField(_, methodName):
                var method = methodMap.get(methodName);
                method != null ? method.expr : null;
            case EConst(CIdent(methodName)):
                var method = methodMap.get(methodName);
                method != null ? method.expr : null;
            default: null;
        };
    }

    // ========================================================================
    // Event Extraction
    // ========================================================================

    function extractEvents(baseEventName:String, body:Expr):Void {
        var statements:Array<IRNode> = [];

        switch (body.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    processStatement(expr, statements);
                }
            default:
                processStatement(body, statements);
        }

        // If there are remaining statements after event extraction, add to base event
        if (statements.length > 0) {
            if (!events.exists(baseEventName)) events.set(baseEventName, []);
            for (stmt in statements) {
                events.get(baseEventName).push(stmt);
            }
        }
    }

    function processStatement(e:Expr, statements:Array<IRNode>):Void {
        if (e == null) return;

        switch (e.expr) {
            // Detect: if (gamepad.started("a")) { ... }
            case EIf(econd, eif, eelse):
                var inputEvent = detectInputEvent(econd);
                if (inputEvent != null && eelse == null) {
                    // Extract body as separate event
                    var eventName = inputEvent.eventName;
                    if (!events.exists(eventName)) events.set(eventName, []);
                    extractEventBody(eif, events.get(eventName));

                    // Track button and meta
                    if (!Lambda.has(meta.buttons_used, inputEvent.button)) {
                        meta.buttons_used.push(inputEvent.button);
                    }
                    // Add structured button event metadata
                    meta.button_events.push({
                        event_name: eventName,
                        button: inputEvent.button,
                        c_button: inputEvent.c_button,
                        event_type: inputEvent.eventType
                    });
                    meta.uses_input = true;
                    return; // Don't add to statements
                }
                // Regular if - add to statements
                statements.push(convertIfToIR(econd, eif, eelse));

            default:
                var node = exprToIR(e);
                if (node != null && node.type != "skip") {
                    statements.push(node);
                }
        }
    }

    function extractEventBody(body:Expr, eventNodes:Array<IRNode>):Void {
        switch (body.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var node = exprToIR(expr);
                    if (node != null && node.type != "skip") {
                        eventNodes.push(node);
                    }
                }
            default:
                var node = exprToIR(body);
                if (node != null && node.type != "skip") {
                    eventNodes.push(node);
                }
        }
    }

    function detectInputEvent(econd:Expr):{eventName:String, button:String, c_button:String, eventType:String} {
        switch (econd.expr) {
            case ECall(e, params):
                switch (e.expr) {
                    case EField(obj, method):
                        switch (obj.expr) {
                            case EConst(CIdent("gamepad")):
                                if (method == "started" || method == "released" || method == "down") {
                                    if (params.length > 0) {
                                        var rawButton = extractStringArg(params[0]);
                                        if (rawButton != null) {
                                            var button = ButtonMap.normalize(rawButton);
                                            var c_button = ButtonMap.toN64Const(rawButton);
                                            var eventName = 'btn_${button}_$method';
                                            return {
                                                eventName: eventName,
                                                button: button,
                                                c_button: c_button,
                                                eventType: method
                                            };
                                        }
                                    }
                                }
                            default:
                        }
                    default:
                }
            default:
        }
        return null;
    }

    function extractStringArg(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            case EConst(CIdent(s)): s;
            default: null;
        };
    }

    // ========================================================================
    // AST → IR Conversion
    // ========================================================================

    function convertIfToIR(econd:Expr, eif:Expr, eelse:Expr):IRNode {
        var thenNodes:Array<IRNode> = [];
        extractEventBody(eif, thenNodes);

        var elseNodes:Array<IRNode> = null;
        if (eelse != null) {
            elseNodes = [];
            extractEventBody(eelse, elseNodes);
        }

        return {
            type: "if",
            children: [exprToIR(econd)],
            props: {
                then: [for (n in thenNodes) n],
                else_: elseNodes != null ? [for (n in elseNodes) n] : null
            }
        };
    }

    function exprToIR(e:Expr):IRNode {
        if (e == null) return null;

        return switch (e.expr) {
            // Literals
            case EConst(CInt(v)): { type: "int", value: Std.parseInt(v) };
            case EConst(CFloat(v)): { type: "float", value: Std.parseFloat(v) };
            case EConst(CString(v)): { type: "string", value: v };
            case EConst(CIdent("true")): { type: "bool", value: true };
            case EConst(CIdent("false")): { type: "bool", value: false };
            case EConst(CIdent("null")): { type: "null" };
            case EConst(CIdent(name)): resolveIdent(name);

            // Binary ops
            case EBinop(op, e1, e2):
                var opStr = binopToString(op);
                if (op == OpAssign) {
                    // Check if assigning to transform.loc/rot/scale (mutating transform)
                    checkTransformMutation(e1);
                    { type: "assign", children: [exprToIR(e1), exprToIR(e2)] };
                } else {
                    { type: "binop", value: opStr, children: [exprToIR(e1), exprToIR(e2)] };
                }

            // Unary ops
            case EUnop(op, postFix, operand):
                { type: "unop", value: unopToString(op), children: [exprToIR(operand)], props: { postfix: postFix } };

            // Field access
            case EField(obj, field):
                convertFieldAccess(obj, field);

            // Call
            case ECall(callExpr, params):
                convertCall(callExpr, params);

            // Parentheses
            case EParenthesis(inner):
                exprToIR(inner);

            // New
            case ENew(tp, params):
                {
                    type: "new",
                    value: tp.name,
                    args: [for (p in params) exprToIR(p)]
                };

            // Block
            case EBlock(exprs):
                { type: "block", children: [for (expr in exprs) exprToIR(expr)] };

            // If statement (nested ifs)
            case EIf(econd, eif, eelse):
                convertIfToIR(econd, eif, eelse);

            // Local variable declaration: var x = value
            case EVars(vars):
                var varDecls:Array<IRNode> = [];
                for (v in vars) {
                    var varType = v.type != null ? complexTypeToString(v.type) : inferType(v.expr);
                    var ctype = TypeMap.getCType(varType);
                    if (ctype == null) ctype = "float"; // fallback for unknown types
                    // Track this local variable's type
                    localVarTypes.set(v.name, varType);
                    varDecls.push({
                        type: "var",
                        value: v.name,
                        props: { ctype: ctype, haxeType: varType },
                        children: v.expr != null ? [exprToIR(v.expr)] : null
                    });
                }
                if (varDecls.length == 1) varDecls[0];
                else { type: "block", children: varDecls };

            // Return statement
            case EReturn(retExpr):
                { type: "return", children: retExpr != null ? [exprToIR(retExpr)] : null };

            default:
                { type: "skip" };
        };
    }

    function inferType(e:Expr):String {
        if (e == null) return "Dynamic";
        switch (e.expr) {
            case ENew(tp, _): return tp.name;
            case EConst(CInt(_)): return "Int";
            case EConst(CFloat(_)): return "Float";
            case EConst(CString(_)): return "String";
            case EField(innerObj, field):
                // gamepad.leftStick / gamepad.rightStick -> Vec2
                switch (innerObj.expr) {
                    case EConst(CIdent("gamepad")):
                        if (field == "leftStick" || field == "rightStick") {
                            return "Vec2";
                        }
                    default:
                }
                return "Dynamic";
            case ECall(callExpr, _):
                // Try to infer return type from method calls
                switch (callExpr.expr) {
                    case EField(obj, method):
                        // Vec method calls return Vec
                        var objType = inferType(obj);
                        if (StringTools.startsWith(objType, "Vec")) {
                            if (method == "mult" || method == "add" || method == "sub" || method == "normalize") {
                                return objType;
                            }
                        }
                    default:
                }
                return "Dynamic";
            default: return "Dynamic";
        }
    }

    function resolveIdent(name:String):IRNode {
        if (name == "this" || name == "object") {
            meta.uses_transform = true;
            return { type: "ident", value: "object" };
        }
        if (name == "dt") {
            meta.uses_time = true;
            return { type: "ident", value: "dt" };
        }
        if (memberNames.indexOf(name) >= 0) {
            return { type: "member", value: name };
        }
        if (SkipList.shouldSkipMember(name) || SkipList.shouldSkipClass(name)) {
            return { type: "skip" };
        }
        return { type: "ident", value: name };
    }

    // Check if expression is an assignment to transform properties (loc, rot, scale, dirty)
    function checkTransformMutation(expr:Expr):Void {
        switch (expr.expr) {
            case EField(obj, field):
                switch (obj.expr) {
                    // transform.loc = ..., transform.rot = ..., transform.scale = ..., transform.dirty = ...
                    case EField(_, "transform"), EConst(CIdent("transform")):
                        if (field == "loc" || field == "rot" || field == "scale" || field == "dirty") {
                            meta.mutates_transform = true;
                        }
                    // transform.loc.x = ... (nested field access)
                    case EField(innerObj, innerField):
                        if (innerField == "loc" || innerField == "rot" || innerField == "scale") {
                            switch (innerObj.expr) {
                                case EField(_, "transform"), EConst(CIdent("transform")):
                                    meta.mutates_transform = true;
                                default:
                            }
                        }
                    default:
                }
            default:
        }
    }

    function convertFieldAccess(obj:Expr, field:String):IRNode {
        // Handle transform access
        switch (obj.expr) {
            case EField(innerObj, "transform"):
                meta.uses_transform = true;
                return { type: "field", object: { type: "ident", value: "object" }, value: "transform." + field };
            case EConst(CIdent("transform")):
                meta.uses_transform = true;
                return { type: "field", object: { type: "ident", value: "object" }, value: "transform." + field };
            case EConst(CIdent("Time")):
                if (field == "delta") {
                    meta.uses_time = true;
                    return { type: "ident", value: "dt" };
                }
            case EConst(CIdent("gamepad")):
                // gamepad.leftStick, gamepad.rightStick
                meta.uses_input = true;
                if (field == "leftStick" || field == "rightStick") {
                    return { type: "gamepad_stick", value: field };
                }
            default:
        }

        // Vec3 component access
        if (field == "x" || field == "y" || field == "z") {
            return { type: "field", object: exprToIR(obj), value: field };
        }

        return { type: "field", object: exprToIR(obj), value: field };
    }

    function getExprType(e:Expr):String {
        // Try to infer type from expression
        switch (e.expr) {
            case ENew(tp, _):
                return tp.name;  // new Vec3() -> "Vec3"
            case EConst(CIdent(name)):
                // Check local variables first
                if (localVarTypes.exists(name)) {
                    return localVarTypes.get(name);
                }
                // Check if it's a member with known type
                if (members.exists(name)) {
                    var m = members.get(name);
                    return m.haxeType;
                }
            case EField(innerObj, field):
                // gamepad.leftStick / gamepad.rightStick -> Vec2
                switch (innerObj.expr) {
                    case EConst(CIdent("gamepad")):
                        if (field == "leftStick" || field == "rightStick") {
                            return "Vec2";
                        }
                    // object.transform.loc/rot/scale -> Vec4 (Iron uses Vec4 for all transform components)
                    case EField(_, "transform"):
                        if (field == "loc" || field == "scale") {
                            return "Vec4";
                        }
                        if (field == "rot") {
                            return "Vec4";  // Quaternion as Vec4
                        }
                    default:
                }
                // Also check for transform.x where transform is accessed directly
                switch (innerObj.expr) {
                    case EConst(CIdent("transform")):
                        if (field == "loc" || field == "scale") {
                            return "Vec4";
                        }
                        if (field == "rot") {
                            return "Vec4";
                        }
                    default:
                }
            case ECall(callExpr, _):
                // Vec method calls return Vec type
                switch (callExpr.expr) {
                    case EField(obj, method):
                        var objType = getExprType(obj);
                        if (objType != null && StringTools.startsWith(objType, "Vec")) {
                            // mult, add, sub, normalize return the same Vec type
                            if (method == "mult" || method == "add" || method == "sub" || method == "normalize") {
                                return objType;
                            }
                        }
                    default:
                }
            default:
        }
        return null;
    }

    function convertCall(callExpr:Expr, params:Array<Expr>):IRNode {
        var args = [for (p in params) exprToIR(p)];

        switch (callExpr.expr) {
            case EField(obj, method):
                switch (obj.expr) {
                    // Scene.setActive("Level_02") -> scene_switch_to(SCENE_X)
                    case EConst(CIdent("Scene")):
                        return convertSceneCall(method, args);

                    // transform.translate(...) -> it_translate(...)
                    case EField(_, "transform"), EConst(CIdent("transform")):
                        meta.uses_transform = true;
                        return convertTransformCall(method, args);

                    // Math.sin(x) -> sinf(x)
                    case EConst(CIdent("Math")):
                        return convertMathCall(method, args);

                    // gamepad.started("a") or keyboard/mouse - should be extracted as event
                    case EConst(CIdent("gamepad")), EConst(CIdent("keyboard")), EConst(CIdent("mouse")), EConst(CIdent("Input")):
                        meta.uses_input = true;
                        if (params.length > 0) {
                            var btn = extractStringArg(params[0]);
                            if (btn != null) {
                                var normalized = ButtonMap.normalize(btn);
                                if (!Lambda.has(meta.buttons_used, normalized)) {
                                    meta.buttons_used.push(normalized);
                                }
                            }
                        }
                        return convertInputCall(method, args);

                    // object.physics.applyForce(...) -> emit ready C call
                    case EField(innerObj, "physics"):
                        meta.uses_physics = true;
                        var objIR = exprToIR(innerObj);
                        return convertPhysicsCall(method, objIR, args);

                    default:
                        // Check if it's a Vec method call
                        var objType = getExprType(obj);
                        if (objType != null && StringTools.startsWith(objType, "Vec")) {
                            var objIR = exprToIR(obj);
                            return convertVecCall(method, objIR, args, objType);
                        }
                        return {
                            type: "call",
                            target: "unknown",
                            method: method,
                            object: exprToIR(obj),
                            args: args
                        };
                }

            case EConst(CIdent(funcName)):
                // Skip lifecycle registration calls - they're handled by scanForLifecycles
                if (funcName == "notifyOnInit" || funcName == "notifyOnUpdate" ||
                    funcName == "notifyOnFixedUpdate" || funcName == "notifyOnLateUpdate" ||
                    funcName == "notifyOnRemove" || funcName == "notifyOnAdd") {
                    return { type: "skip" };
                }
                return { type: "call", method: funcName, args: args };

            default:
                return { type: "skip" };
        }
    }

    function binopToString(op:Binop):String {
        return switch (op) {
            case OpAdd: "+";
            case OpSub: "-";
            case OpMult: "*";
            case OpDiv: "/";
            case OpMod: "%";
            case OpEq: "==";
            case OpNotEq: "!=";
            case OpLt: "<";
            case OpLte: "<=";
            case OpGt: ">";
            case OpGte: ">=";
            case OpAnd: "&";      // Bitwise AND
            case OpOr: "|";       // Bitwise OR
            case OpBoolAnd: "&&"; // Logical AND
            case OpBoolOr: "||";  // Logical OR
            case OpXor: "^";      // Bitwise XOR
            case OpShl: "<<";     // Shift left
            case OpShr: ">>";     // Shift right
            case OpUShr: ">>>";   // Unsigned shift right
            case OpAssign: "=";
            case OpAssignOp(op): binopToString(op) + "=";
            default: "?";
        };
    }

    function unopToString(op:Unop):String {
        return switch (op) {
            case OpNeg: "-";
            case OpNot: "!";
            case OpIncrement: "++";
            case OpDecrement: "--";
            default: "?";
        };
    }

    // =========================================================================
    // Physics call conversion - emit ready-to-use C
    // =========================================================================

    function convertPhysicsCall(method:String, objIR:IRNode, args:Array<IRNode>):IRNode {
        // Physics calls become direct C function calls
        // The object's rigid_body field is accessed, and vec args are passed by pointer
        return {
            type: "physics_call",
            method: method,
            object: objIR,
            args: args
        };
    }

    // =========================================================================
    // Vec call conversion - emit ready-to-use C
    // =========================================================================

    function convertVecCall(method:String, objIR:IRNode, args:Array<IRNode>, vecType:String):IRNode {
        // Vec method calls become inline C expressions
        // Determine C type based on Haxe type
        var cType = switch (vecType) {
            case "Vec4": "ArmVec4";
            case "Vec3": "ArmVec3";
            default: "ArmVec2";
        };
        var is3D = (vecType == "Vec3" || vecType == "Vec4");

        return {
            type: "vec_call",
            method: method,
            object: objIR,
            args: args,
            props: {
                vecType: vecType,
                cType: cType,
                is3D: is3D
            }
        };
    }

    // =========================================================================
    // Scene call conversion - Scene.setActive() -> scene_switch_to()
    // =========================================================================

    function convertSceneCall(method:String, args:Array<IRNode>):IRNode {
        if (method == "setActive" && args.length > 0) {
            var arg = args[0];
            // If it's a string literal, convert to enum directly
            if (arg.type == "string") {
                var sceneName = Std.string(arg.value).toUpperCase();
                return {
                    type: "scene_call",
                    method: "setActive",
                    c_code: 'scene_switch_to(SCENE_$sceneName)'
                };
            }
            // For any other expression (variable, member, concatenation, etc.),
            // use runtime helper that maps string -> SceneId
            return {
                type: "scene_call",
                method: "setActive",
                args: args
            };
        }
        return { type: "skip" };
    }

    // =========================================================================
    // Transform call conversion - with coordinate swizzle Blender→N64
    // Blender: X=right, Y=forward, Z=up
    // N64/T3D: X=right, Y=up, Z=back (so Y→Z, Z→-Y)
    // =========================================================================

    function convertTransformCall(method:String, args:Array<IRNode>):IRNode {
        // Mark as mutating if it's a transform-modifying method
        if (method == "translate" || method == "rotate" || method == "move" ||
            method == "setMatrix" || method == "multMatrix" || method == "setRotation" ||
            method == "buildMatrix" || method == "applyParent" || method == "applyParentInverse" ||
            method == "reset") {
            meta.mutates_transform = true;
        }
        return {
            type: "transform_call",
            method: method,
            args: args
        };
    }

    // =========================================================================
    // Math call conversion - Math.sin() -> sinf(), etc.
    // =========================================================================

    function convertMathCall(method:String, args:Array<IRNode>):IRNode {
        // Map Haxe Math methods to C math.h functions
        var cFunc = switch (method) {
            case "sin": "sinf";
            case "cos": "cosf";
            case "tan": "tanf";
            case "asin": "asinf";
            case "acos": "acosf";
            case "atan": "atanf";
            case "atan2": "atan2f";
            case "sqrt": "sqrtf";
            case "pow": "powf";
            case "abs": "fabsf";
            case "floor": "floorf";
            case "ceil": "ceilf";
            case "round": "roundf";
            case "min": "fminf";
            case "max": "fmaxf";
            case "exp": "expf";
            case "log": "logf";
            default: method;
        };
        return {
            type: "math_call",
            value: cFunc,
            args: args
        };
    }

    // =========================================================================
    // Input call conversion - gamepad.started("a") -> input_started(N64_BTN_A)
    // =========================================================================

    function convertInputCall(method:String, args:Array<IRNode>):IRNode {
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
