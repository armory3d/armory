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

            // Skip empty traits (no events and doesn't need data struct)
            // But include if trait has contact_events or button_events in meta
            var hasEvents = Lambda.count(ir.events) > 0;
            var hasContactEvents = ir.meta.contact_events.length > 0;
            var hasButtonEvents = ir.meta.button_events.length > 0;
            if (!hasEvents && !hasContactEvents && !hasButtonEvents && !ir.needsData) continue;

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

            // Generate struct_type and struct_def for signals with 2+ args
            for (sig in ir.meta.signals) {
                var argCount = sig.arg_types.length;
                if (argCount >= 2) {
                    sig.struct_type = '${ir.cName}_${sig.name}_payload_t';
                    // Generate full struct definition
                    var lines:Array<String> = ['typedef struct {'];
                    for (i in 0...argCount) {
                        lines.push('    ${sig.arg_types[i]} arg$i;');
                    }
                    lines.push('} ${sig.struct_type};');
                    sig.struct_def = lines.join('\n');
                }
            }

            for (sh in ir.meta.signal_handlers) {
                // Find the signal this handler connects to
                for (sig in ir.meta.signals) {
                    if (sig.name == sh.signal_name) {
                        var argTypes = sig.arg_types;
                        var argCount = argTypes.length;

                        // Always cast ctx to data pointer so handler body can use 'data'
                        var dataType = '${ir.name}Data';
                        var dataCast = '$dataType* data = ($dataType*)ctx;';

                        if (argCount == 0) {
                            sh.preamble = '$dataCast (void)payload;';
                        } else if (argCount == 1) {
                            sh.preamble = '$dataCast ${argTypes[0]} arg0 = (${argTypes[0]})(uintptr_t)payload; (void)arg0;';
                        } else {
                            // Multiple args - cast to struct (use sig.struct_type)
                            var structType = sig.struct_type;
                            var lines:Array<String> = [];
                            lines.push(dataCast);
                            lines.push('$structType* p = ($structType*)payload;');
                            for (i in 0...argCount) {
                                lines.push('${argTypes[i]} arg$i = p->arg$i; (void)arg$i;');
                            }
                            sh.preamble = lines.join(" ");
                        }
                        break;
                    }
                }
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
        if (node.method != null) obj.method = node.method;
        if (node.object != null) obj.object = serializeIRNode(node.object);
        if (node.props != null) obj.props = node.props;
        if (node.c_code != null) obj.c_code = node.c_code;
        if (node.c_func != null) obj.c_func = node.c_func;

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
    ?method: String,
    ?object: IRNode,
    ?props: Dynamic,
    ?c_code: String,
    ?c_func: String  // Direct C function name for 1:1 translation
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

typedef ContactEventMeta = {
    event_name: String,      // Handler function name, e.g., "onContact"
    handler_name: String,    // Full C handler name, e.g., "arm_player_player_contact_onContact"
    subscribe: Bool          // true for notifyOnContact, false for removeContact
}

typedef SignalMeta = {
    name: String,            // Signal member name, e.g., "onDeath"
    arg_types: Array<String>, // C types for emit args, e.g., ["int32_t", "ArmObject*"]
    max_subs: Int,           // Max subscribers, default 16, configurable via @:n64MaxSubs(N)
    ?struct_type: String,    // Payload struct type name for 2+ args
    ?struct_def: String      // Full C struct definition for 2+ args
}

typedef SignalHandlerMeta = {
    handler_name: String,    // Function name used as callback, e.g., "onEnemyDeath"
    signal_name: String,     // Which signal it connects to, e.g., "onDeath"
    ?preamble: String        // C code for payload unpacking, generated after arg_types known
}

typedef TraitMeta = {
    uses_input: Bool,
    uses_transform: Bool,
    mutates_transform: Bool,   // True if trait modifies transform (translate, rotate, etc.)
    uses_time: Bool,
    uses_physics: Bool,
    buttons_used: Array<String>,
    button_events: Array<ButtonEventMeta>,  // structured button event info
    contact_events: Array<ContactEventMeta>, // physics contact subscriptions
    signals: Array<SignalMeta>, // per-instance signal declarations
    signal_handlers: Array<SignalHandlerMeta>, // functions used as signal callbacks
    global_signals: Array<String> // global signals used (e.g., "g_gameevents_gemCollected")
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
        "Graphics" => true,  // kha.graphics2.Graphics - not available on N64
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
    var memberTypes:Map<String, String>;    // Track member types for signal detection
    var cName:String;  // C-safe name for this trait

    public function new(className:String, modulePath:String, fields:Array<Field>) {
        this.className = className;
        this.modulePath = modulePath;
        this.fields = fields;
        this.members = new Map();
        this.memberNames = [];
        this.methodMap = new Map();
        this.events = new Map();
        this.localVarTypes = new Map();
        this.memberTypes = new Map();
        this.meta = {
            uses_input: false,
            uses_transform: false,
            mutates_transform: false,
            uses_time: false,
            uses_physics: false,
            buttons_used: [],
            button_events: [],
            contact_events: [],
            signals: [],
            signal_handlers: [],
            global_signals: []
        };

        // Generate C-safe name early so it's available during extraction
        var moduleParts = modulePath.split(".");
        var lastModulePart = moduleParts[moduleParts.length - 1];
        if (lastModulePart.toLowerCase() == className.toLowerCase()) {
            this.cName = modulePath.replace(".", "_").toLowerCase();
        } else {
            this.cName = (modulePath.replace(".", "_") + "_" + className).toLowerCase();
        }
    }

    public function extract():TraitIR {
        // Pass 1: Extract members and methods
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    var haxeType = t != null ? complexTypeToString(t) : "Dynamic";
                    memberTypes.set(field.name, haxeType);

                    // Signal members are tracked separately, not as regular data members
                    if (haxeType == "Signal") {
                        // Check for @:n64MaxSubs(N) metadata, default to 16
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
                            arg_types: [],  // Will be populated when emit() is detected
                            max_subs: maxSubs
                        });
                    } else {
                        var member = extractMember(field.name, t, e);
                        if (member != null) {
                            members.set(field.name, member);
                            memberNames.push(field.name);
                        }
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

        // Generate C-safe name is now done in constructor
        // cName is available as this.cName

        return {
            name: className,
            module: modulePath,
            cName: cName,
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

                    // Special case: transform.scale = value -> emit transform_call with it_set_scale()
                    if (isTransformScaleAssign(e1)) {
                        var valueIR = exprToIR(e2);
                        // Swizzle: Blender (x, y, z) → N64 (x, z, y) and multiply by SCALE_FACTOR (0.015625 = 1/64)
                        {
                            type: "transform_call",
                            c_code: "it_set_scale(&((ArmObject*)obj)->transform, ({0}).x * 0.015625f, ({0}).z * 0.015625f, ({0}).y * 0.015625f);",
                            args: [valueIR]
                        };
                    } else {
                        { type: "assign", children: [exprToIR(e1), exprToIR(e2)] };
                    }
                } else if (op == OpAdd) {
                    // Check if this is string concatenation
                    var leftType = getExprType(e1);
                    var rightType = getExprType(e2);
                    if (leftType == "String" || rightType == "String") {
                        // String concatenation - use helper class
                        var builder = new StringConcatBuilder(members, localVarTypes, exprToIR, getExprType);
                        builder.build(e1, e2);
                    } else {
                        { type: "binop", value: opStr, children: [exprToIR(e1), exprToIR(e2)] };
                    }
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
                convertNew(tp, params);

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
                    var varType = v.type != null ? complexTypeToString(v.type) : getExprType(v.expr);
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

    // Check if expression is assignment to transform.scale (needs special handling)
    function isTransformScaleAssign(expr:Expr):Bool {
        switch (expr.expr) {
            case EField(obj, "scale"):
                switch (obj.expr) {
                    case EField(_, "transform"), EConst(CIdent("transform")):
                        return true;
                    default:
                }
            default:
        }
        return false;
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
                    // Emit inline C struct with input functions
                    return { type: "c_literal", c_code: "(ArmVec2){input_stick_x(), input_stick_y()}" };
                }
            default:
        }

        // Vec3 component access
        if (field == "x" || field == "y" || field == "z") {
            return { type: "field", object: exprToIR(obj), value: field };
        }

        return { type: "field", object: exprToIR(obj), value: field };
    }

    /**
     * Unified type inference from Haxe expressions.
     * Returns the Haxe type name (Int, Float, String, Vec2, Label, Signal, etc.) or "Dynamic" if unknown.
     */
    function getExprType(e:Expr):String {
        if (e == null) return "Dynamic";

        switch (e.expr) {
            // Literals
            case EConst(CInt(_)): return "Int";
            case EConst(CFloat(_)): return "Float";
            case EConst(CString(_)): return "String";

            // Constructor: new Vec3() -> "Vec3"
            case ENew(tp, _):
                return tp.name;

            // Identifier: variable or member
            case EConst(CIdent(name)):
                if (localVarTypes.exists(name)) {
                    return localVarTypes.get(name);
                }
                // Check memberTypes first (includes Signal and all member types)
                if (memberTypes.exists(name)) {
                    return memberTypes.get(name);
                }
                if (members.exists(name)) {
                    return members.get(name).haxeType;
                }
                return "Dynamic";

            // Field access
            case EField(innerObj, field):
                // this.member or object.member
                switch (innerObj.expr) {
                    case EConst(CIdent("this")), EConst(CIdent("object")):
                        // Check memberTypes first (includes Signal)
                        if (memberTypes.exists(field)) {
                            return memberTypes.get(field);
                        }
                        if (members.exists(field)) {
                            return members.get(field).haxeType;
                        }
                    default:
                }

                // gamepad.leftStick / gamepad.rightStick -> Vec2
                switch (innerObj.expr) {
                    case EConst(CIdent("gamepad")):
                        if (field == "leftStick" || field == "rightStick") return "Vec2";
                    // transform.loc/rot/scale -> Vec4
                    case EField(_, "transform"), EConst(CIdent("transform")):
                        if (field == "loc" || field == "scale" || field == "rot") return "Vec4";
                    default:
                }
                return "Dynamic";

            // Method calls
            case ECall(callExpr, _):
                switch (callExpr.expr) {
                    case EField(obj, method):
                        // Std.string/int/parseFloat
                        switch (obj.expr) {
                            case EConst(CIdent("Std")):
                                if (method == "string") return "String";
                                if (method == "int") return "Int";
                                if (method == "parseFloat") return "Float";
                            default:
                        }
                        // Vec method calls return same Vec type
                        var objType = getExprType(obj);
                        if (objType != null && StringTools.startsWith(objType, "Vec")) {
                            if (method == "mult" || method == "add" || method == "sub" ||
                                method == "normalize" || method == "clone" || method == "cross") {
                                return objType;
                            }
                        }
                    default:
                }
                return "Dynamic";

            // Binary operations
            case EBinop(OpAdd, e1, e2):
                var t1 = getExprType(e1);
                var t2 = getExprType(e2);
                if (t1 == "String" || t2 == "String") return "String";
                if (t1 == "Float" || t2 == "Float") return "Float";
                return "Int";

            // Parentheses
            case EParenthesis(inner):
                return getExprType(inner);

            default:
                return "Dynamic";
        }
    }

    function convertCall(callExpr:Expr, params:Array<Expr>):IRNode {
        var args = [for (p in params) exprToIR(p)];

        switch (callExpr.expr) {
            case EField(obj, method):
                // FIRST: Check if this is a Vec method call (before specific object checks)
                // This handles cases like gamepad.leftStick.mult() where the object
                // is a complex expression that getExprType can resolve
                var vecMethods = ["mult", "add", "sub", "dot", "normalize", "length", "clone", "cross", "set", "setFrom"];
                if (Lambda.has(vecMethods, method)) {
                    var objType = getExprType(obj);
                    if (objType != null && StringTools.startsWith(objType, "Vec")) {
                        var objIR = exprToIR(obj);
                        return convertVecCall(method, objIR, args, objType);
                    }
                }

                // SECOND: Check for physics contact subscription methods
                // rb.notifyOnContact(handler) or rb.removeContact(handler)
                if (method == "notifyOnContact" || method == "removeContact") {
                    meta.uses_physics = true;
                    return convertContactSubscription(method, args, params);
                }

                // THIRD: Check if this is a physics method call on any object (rigid_body.applyForce, body.applyForce, etc.)
                var physicsMethods = ["applyForce", "applyImpulse", "setLinearVelocity", "getLinearVelocity",
                                      "setAngularVelocity", "getAngularVelocity", "setLinearFactor", "setAngularFactor"];
                if (Lambda.has(physicsMethods, method)) {
                    meta.uses_physics = true;
                    // For N64, physics always applies to the current object
                    return convertPhysicsCall(method, { type: "ident", value: "object" }, args);
                }

                switch (obj.expr) {
                    // Scene.setActive("Level_02") -> scene_switch_to(SCENE_X)
                    case EConst(CIdent("Scene")):
                        return convertSceneCall(method, args, params);

                    // transform.translate(...) -> it_translate(...)
                    case EField(_, "transform"), EConst(CIdent("transform")):
                        meta.uses_transform = true;
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

                    // object.physics.applyForce(...) -> physics call on object
                    case EField(innerObj, "physics"):
                        meta.uses_physics = true;
                        var objIR = exprToIR(innerObj);
                        return convertPhysicsCall(method, objIR, args);

                    // physics.applyForce(...) -> physics call on self (this.physics)
                    case EConst(CIdent("physics")):
                        meta.uses_physics = true;
                        return convertPhysicsCall(method, { type: "ident", value: "object" }, args);

                    // Std.int(), Std.parseFloat(), etc. -> type casts
                    case EConst(CIdent("Std")):
                        return convertStdCall(method, args);

                    // object.remove(), object.getTrait(), etc. -> object lifecycle
                    case EConst(CIdent("object")), EConst(CIdent("this")):
                        return convertObjectCall(method, args);

                    // Unsupported APIs - explicitly skip with no codegen fallback
                    case EConst(CIdent("Audio")), EConst(CIdent("Tween")), EConst(CIdent("Network")), EConst(CIdent("canvas")), EConst(CIdent("Koui")):
                        return { type: "skip" };

                    default:
                        // Check if this is a Signal method call (connect/disconnect/emit)
                        // First try getExprType, then check memberTypes directly
                        var objType = getExprType(obj);
                        if (objType == "Signal") {
                            return convertSignalCall(method, obj, args, params);
                        }
                        // Direct check: if method is connect/disconnect/emit and obj is a member
                        if (method == "connect" || method == "disconnect" || method == "emit") {
                            var memberName = switch (obj.expr) {
                                case EConst(CIdent(name)): name;
                                case EField(_, fieldName): fieldName;
                                default: null;
                            };
                            if (memberName != null && memberTypes.exists(memberName) && memberTypes.get(memberName) == "Signal") {
                                return convertSignalCall(method, obj, args, params);
                            }
                            // Check for global signal pattern: GameEvents.signalName.method()
                            // or SomeClass.signalName.method()
                            switch (obj.expr) {
                                case EField(classExpr, signalName):
                                    switch (classExpr.expr) {
                                        case EConst(CIdent(className)):
                                            // This is ClassName.signalName.method() - global signal
                                            return convertGlobalSignalCall(method, className, signalName, args, params);
                                        default:
                                    }
                                default:
                            }
                        }
                        // Fallback: generic call with object
                        return {
                            type: "call",
                            method: method,
                            object: exprToIR(obj),
                            args: args
                        };
                }

            case EConst(CIdent(funcName)):
                // Skip lifecycle registration calls - they're handled by scanForLifecycles
                // notifyOnRender2D is skipped entirely - N64 doesn't have 2D graphics layer
                if (funcName == "notifyOnInit" || funcName == "notifyOnUpdate" ||
                    funcName == "notifyOnFixedUpdate" || funcName == "notifyOnLateUpdate" ||
                    funcName == "notifyOnRemove" || funcName == "notifyOnAdd" ||
                    funcName == "notifyOnRender2D" || funcName == "notifyOnRender") {
                    return { type: "skip" };
                }

                // trace() -> debugf() for N64 debug output
                if (funcName == "trace") {
                    return { type: "debug_call", args: args };
                }

                // Physics methods called directly (applyForce, applyImpulse, etc.)
                var physicsMethods = ["applyForce", "applyImpulse", "setLinearVelocity", "getLinearVelocity",
                                      "setAngularVelocity", "getAngularVelocity", "setLinearFactor", "setAngularFactor"];
                if (Lambda.has(physicsMethods, funcName)) {
                    meta.uses_physics = true;
                    return convertPhysicsCall(funcName, { type: "ident", value: "object" }, args);
                }

                return { type: "call", method: funcName, args: args };

            default:
                return { type: "skip" };
        }
    }

    // =========================================================================
    // New expression conversion - handles constructor calls
    // =========================================================================

    function convertNew(tp:TypePath, params:Array<Expr>):IRNode {
        var typeName = tp.name;
        var args = [for (p in params) exprToIR(p)];

        // Vec constructors: emit C struct literal with placeholders
        if (typeName == "Vec4") {
            // {0}, {1}, {2}, {3} will be substituted by Python
            var argCount = args.length;
            if (argCount >= 4) {
                return { type: "new_vec", c_code: "(ArmVec4){{0}, {1}, {2}, {3}}", args: args };
            } else if (argCount >= 3) {
                return { type: "new_vec", c_code: "(ArmVec4){{0}, {1}, {2}, 1.0f}", args: args };
            }
            return { type: "c_literal", c_code: "(ArmVec4){0, 0, 0, 1.0f}" };
        }
        if (typeName == "Vec3") {
            if (args.length >= 3) {
                return { type: "new_vec", c_code: "(ArmVec3){{0}, {1}, {2}}", args: args };
            }
            return { type: "c_literal", c_code: "(ArmVec3){0, 0, 0}" };
        }
        if (typeName == "Vec2") {
            if (args.length >= 2) {
                return { type: "new_vec", c_code: "(ArmVec2){{0}, {1}}", args: args };
            }
            return { type: "c_literal", c_code: "(ArmVec2){0, 0}" };
        }

        // Default: generic new expression
        return {
            type: "new",
            value: typeName,
            args: args
        };
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
    // Physics call conversion - emit ready-to-use C with placeholders
    // Placeholders: {obj} = object, {0}, {1}, etc. = args
    // Coord conversion: Blender (X,Y,Z) → N64 (X,Z,-Y)
    // =========================================================================

    function convertPhysicsCall(method:String, objIR:IRNode, args:Array<IRNode>):IRNode {
        // Physics calls use OimoVec3 which needs coordinate swizzle
        // Template uses {obj} for object and {0} for first arg (vec)
        var c_code = switch (method) {
            case "applyForce":
                "{ OimoVec3 _f = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_force({obj}->rigid_body, &_f); }";
            case "applyImpulse":
                "{ OimoVec3 _i = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_impulse({obj}->rigid_body, &_i); }";
            case "setLinearVelocity":
                "{ OimoVec3 _v = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_set_linear_velocity({obj}->rigid_body, &_v); }";
            case "getLinearVelocity":
                "physics_get_linear_velocity({obj}->rigid_body)";
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "physics_call",
            c_code: c_code,
            object: objIR,
            args: args
        };
    }

    // =========================================================================
    // Contact subscription - notifyOnContact(handler), removeContact(handler)
    // Records metadata for Python to emit subscription calls at init time
    // =========================================================================

    function convertContactSubscription(method:String, args:Array<IRNode>, params:Array<Expr>):IRNode {
        // Extract handler function name from first argument
        // e.g., rb.notifyOnContact(onContact) -> handler = "onContact"
        if (params.length == 0) return { type: "skip" };

        var handlerName:String = null;
        switch (params[0].expr) {
            case EConst(CIdent(name)):
                handlerName = name;
            case EField(_, name):
                handlerName = name;
            default:
        }

        if (handlerName == null) return { type: "skip" };

        // Record the handler method for extraction
        // The handler will be extracted as a contact event (similar to button events)
        var isSubscribe = (method == "notifyOnContact");

        // Build full C handler name: {c_name}_contact_{handlerName}
        var fullHandlerName = cName + "_contact_" + handlerName;

        meta.contact_events.push({
            event_name: handlerName,
            handler_name: fullHandlerName,
            subscribe: isSubscribe
        });

        // If subscribing, extract the handler method body as an event
        if (isSubscribe && methodMap.exists(handlerName)) {
            var func = methodMap.get(handlerName);
            if (!events.exists("contact_" + handlerName)) {
                events.set("contact_" + handlerName, []);
                extractContactHandler(handlerName, func, events.get("contact_" + handlerName));
            }
        }

        // Return a no-op - the actual subscription is done at init time by Python
        return { type: "skip" };
    }

    function extractContactHandler(name:String, func:Function, eventNodes:Array<IRNode>):Void {
        // Contact handlers have signature: function onContact(body: RigidBody)
        // We need to convert this to the C handler signature: (obj, data, other)
        // The "body" parameter becomes "other" ArmObject in C

        if (func.expr == null) return;

        switch (func.expr.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var node = exprToIR(expr);
                    if (node != null && node.type != "skip") {
                        eventNodes.push(node);
                    }
                }
            default:
                var node = exprToIR(func.expr);
                if (node != null && node.type != "skip") {
                    eventNodes.push(node);
                }
        }
    }

    // =========================================================================
    // Vec call conversion - emit ready-to-use C with placeholders
    // Placeholders: {v} = vector object, {0}, {1} = args
    // =========================================================================

    function convertVecCall(method:String, objIR:IRNode, args:Array<IRNode>, vecType:String):IRNode {
        // Determine C type based on Haxe type
        var cType = switch (vecType) {
            case "Vec4": "ArmVec4";
            case "Vec3": "ArmVec3";
            default: "ArmVec2";
        };
        var is3D = (vecType == "Vec3" || vecType == "Vec4");

        // Template uses {v} for vector, {0} for first arg
        var c_code = switch (method) {
            case "length":
                is3D ? "sqrtf({v}.x*{v}.x + {v}.y*{v}.y + {v}.z*{v}.z)"
                     : "sqrtf({v}.x*{v}.x + {v}.y*{v}.y)";
            case "mult":
                is3D ? "(" + cType + "){{v}.x*({0}), {v}.y*({0}), {v}.z*({0})}"
                     : "(" + cType + "){{v}.x*({0}), {v}.y*({0})}";
            case "add":
                is3D ? "(" + cType + "){{v}.x+({0}).x, {v}.y+({0}).y, {v}.z+({0}).z}"
                     : "(" + cType + "){{v}.x+({0}).x, {v}.y+({0}).y}";
            case "sub":
                is3D ? "(" + cType + "){{v}.x-({0}).x, {v}.y-({0}).y, {v}.z-({0}).z}"
                     : "(" + cType + "){{v}.x-({0}).x, {v}.y-({0}).y}";
            case "dot":
                is3D ? "({v}.x*({0}).x + {v}.y*({0}).y + {v}.z*({0}).z)"
                     : "({v}.x*({0}).x + {v}.y*({0}).y)";
            case "normalize":
                // Note: normalize modifies in-place, needs the original var name
                // We use {vraw} placeholder for unparenthesized var
                is3D ? "{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y+{v}.z*{v}.z); if(_l>0.0f){ {vraw}.x/=_l; {vraw}.y/=_l; {vraw}.z/=_l; } }"
                     : "{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y); if(_l>0.0f){ {vraw}.x/=_l; {vraw}.y/=_l; } }";
            case "clone":
                // Clone creates a copy - type depends on target
                // Special case: transform.scale is stored with SCALE_FACTOR (1/64), so multiply by 64 to get Blender values
                var isScaleClone = (objIR.type == "field" && objIR.value == "transform.scale");
                if (isScaleClone) {
                    // Inverse of SCALE_FACTOR (0.015625 = 1/64) = 64
                    if (cType == "ArmVec4") "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f, {v}.z*64.0f, 1.0f}";
                    else if (cType == "ArmVec3") "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f, {v}.z*64.0f}";
                    else "(" + cType + "){{v}.x*64.0f, {v}.y*64.0f}";
                } else {
                    if (cType == "ArmVec4") "(" + cType + "){{v}.x, {v}.y, {v}.z, 1.0f}";
                    else if (cType == "ArmVec3") "(" + cType + "){{v}.x, {v}.y, {v}.z}";
                    else "(" + cType + "){{v}.x, {v}.y}";
                }
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "vec_call",
            c_code: c_code,
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

    function convertSceneCall(method:String, args:Array<IRNode>, rawParams:Array<Expr>):IRNode {
        if (method == "setActive" && rawParams.length > 0) {
            // Try to extract constant scene name first
            var result = analyzeSceneArg(rawParams[0]);

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
                    // Runtime lookup by name - pass member node so Python emits correctly
                    return {
                        type: "scene_call",
                        method: "setActive",
                        args: [{ type: "member", value: result.value }]
                    };

                case "expression":
                    // Fallback: convert the expression to IR and let codegen handle it
                    // This generates scene_switch_to_by_name with the expression
                    return {
                        type: "scene_call",
                        method: "setActive",
                        args: args  // Pass the converted argument
                    };
            }
        }
        return { type: "skip" };
    }

    /**
     * Analyze Scene.setActive argument and classify it:
     * - "constant": compile-time string literal, value = the scene name
     * - "current_scene": Scene.active.raw.name pattern
     * - "member_string": identifier that's a String member variable, value = member name
     * - "expression": anything else, needs runtime lookup
     */
    function analyzeSceneArg(expr:Expr):{ kind:String, value:String } {
        if (expr == null) return { kind: "expression", value: null };

        switch (expr.expr) {
            // Direct string literal: "Level_01"
            case EConst(CString(s)):
                return { kind: "constant", value: s };

            // Identifier - could be a member variable
            case EConst(CIdent(name)):
                if (members.exists(name)) {
                    var member = members.get(name);
                    // Check type - String members use runtime lookup
                    if (member.haxeType == "String") {
                        return { kind: "member_string", value: name };
                    }
                    // SceneId type might have constant default
                    if (member.haxeType == "SceneId" || member.haxeType == "TSceneFormat" || member.haxeType == "SceneFormat") {
                        var sceneName = extractSceneFromIRNode(member.defaultValue);
                        if (sceneName != null) {
                            return { kind: "constant", value: sceneName };
                        }
                    }
                }
                return { kind: "expression", value: null };

            // Field access chain: Scene.active.raw.name, myScene.raw.name, etc.
            case EField(innerExpr, fieldName):
                if (fieldName == "name") {
                    // Check for .raw.name pattern
                    switch (innerExpr.expr) {
                        case EField(innerInner, "raw"):
                            // Could be Scene.active.raw or memberVar.raw
                            switch (innerInner.expr) {
                                case EField(sceneExpr, "active"):
                                    // Check if it's Scene.active
                                    switch (sceneExpr.expr) {
                                        case EConst(CIdent("Scene")):
                                            return { kind: "current_scene", value: null };
                                        default:
                                    }
                                case EConst(CIdent(memberName)):
                                    // memberVar.raw.name - check if it's a member
                                    if (members.exists(memberName)) {
                                        var member = members.get(memberName);
                                        var sceneName = extractSceneFromIRNode(member.defaultValue);
                                        if (sceneName != null) {
                                            return { kind: "constant", value: sceneName };
                                        }
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

    function extractSceneFromIRNode(node:IRNode):Null<String> {
        if (node == null) return null;
        if (node.type == "string" && node.value != null) {
            return Std.string(node.value);
        }
        if (node.type == "ident" && node.value != null) {
            // Could be a scene enum like Level_01
            return Std.string(node.value);
        }
        return null;
    }

    // =========================================================================
    // Signal call conversion - signal.connect(), signal.disconnect(), signal.emit()
    // Per-instance signals with max 4 subscribers
    // =========================================================================

    function convertSignalCall(method:String, signalExpr:Expr, args:Array<IRNode>, params:Array<Expr>):IRNode {
        // Get the signal member name from the expression
        var signalName = switch (signalExpr.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, fieldName): fieldName;
            default: null;
        };

        if (signalName == null) {
            return { type: "skip" };
        }

        switch (method) {
            case "connect":
                // signal.connect(callback) -> signal_connect(&data->signalName, callback_func, data)
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        addSignalHandler(callbackName, signalName);
                        // c_code with {signal_ptr} and {handler} placeholders
                        return {
                            type: "signal_call",
                            value: "connect",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                signal_name: signalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "disconnect":
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        return {
                            type: "signal_call",
                            value: "disconnect",
                            c_code: 'signal_disconnect({signal_ptr}, {handler});',
                            props: {
                                signal_name: signalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "emit":
                updateSignalArgTypes(signalName, params);
                var argCount = params.length;

                // Generate c_code based on arg count
                var c_code:String;
                if (argCount == 0) {
                    c_code = 'signal_emit({signal_ptr}, NULL);';
                } else if (argCount == 1) {
                    c_code = 'signal_emit({signal_ptr}, (void*)(uintptr_t)({0}));';
                } else {
                    // Multiple args - generate struct init + emit
                    // {struct_type} _p = {{0}, {1}, ...}; signal_emit({signal_ptr}, &_p);
                    var argPlaceholders = [for (i in 0...argCount) '{$i}'];
                    c_code = '{struct_type} _p = {' + argPlaceholders.join(', ') + '}; signal_emit({signal_ptr}, &_p);';
                }

                return {
                    type: "signal_call",
                    value: "emit",
                    c_code: c_code,
                    props: {
                        signal_name: signalName,
                        arg_count: argCount
                    },
                    args: args
                };

            default:
                return { type: "skip" };
        }
    }

    function convertGlobalSignalCall(method:String, className:String, signalName:String, args:Array<IRNode>, params:Array<Expr>):IRNode {
        // Handle global/static signals: GameEvents.gemCollected.emit()
        // These are stored as global ArmSignal structs: g_classname_signalname

        var globalSignalName = 'g_${className.toLowerCase()}_$signalName';

        // Track this global signal for declaration generation
        if (!Lambda.has(meta.global_signals, globalSignalName)) {
            meta.global_signals.push(globalSignalName);
        }

        switch (method) {
            case "connect":
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        addSignalHandler(callbackName, signalName);
                        return {
                            type: "global_signal_call",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                global_signal: globalSignalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "disconnect":
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        return {
                            type: "global_signal_call",
                            c_code: 'signal_disconnect({signal_ptr}, {handler});',
                            props: {
                                global_signal: globalSignalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "emit":
                var argCount = params.length;
                var c_code:String;
                if (argCount == 0) {
                    c_code = 'signal_emit({signal_ptr}, NULL);';
                } else if (argCount == 1) {
                    c_code = 'signal_emit({signal_ptr}, (void*)(uintptr_t)({0}));';
                } else {
                    // Multiple args - for global signals, user should pass a struct pointer
                    c_code = 'signal_emit({signal_ptr}, (void*){0});';
                }
                return {
                    type: "global_signal_call",
                    c_code: c_code,
                    props: {
                        global_signal: globalSignalName
                    },
                    args: args
                };

            default:
                return { type: "skip" };
        }
    }

    function extractFunctionRef(e:Expr):String {
        // Extract function name from expression like `onEnemyDeath` or `this.onEnemyDeath`
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, fieldName): fieldName;
            default: null;
        };
    }

    function updateSignalArgTypes(signalName:String, params:Array<Expr>):Void {
        // Find the signal in meta and update its arg_types based on emit() call
        for (signal in meta.signals) {
            if (signal.name == signalName) {
                // Only update if not already populated (first emit() wins)
                if (signal.arg_types.length == 0) {
                    for (param in params) {
                        var haxeType = inferExprType(param);
                        var cType = TypeMap.getCType(haxeType);
                        signal.arg_types.push(cType);
                    }
                }
                break;
            }
        }
    }

    function inferExprType(e:Expr):String {
        // Infer the Haxe type of an expression for signal arg typing
        return switch (e.expr) {
            case EConst(CInt(_)): "Int";
            case EConst(CFloat(_)): "Float";
            case EConst(CString(_)): "String";
            case EConst(CIdent("true")), EConst(CIdent("false")): "Bool";
            case EConst(CIdent("object")), EConst(CIdent("this")): "ArmObject";
            case EConst(CIdent(name)):
                // Check local vars first, then members
                if (localVarTypes.exists(name)) localVarTypes.get(name);
                else if (members.exists(name)) members.get(name).haxeType;
                else "Dynamic";
            case EField(obj, field):
                // Could be object.transform, etc. - simplified for now
                "Dynamic";
            default: "Dynamic";
        };
    }

    function addSignalHandler(handlerName:String, signalName:String):Void {
        // Check if already tracked
        for (h in meta.signal_handlers) {
            if (h.handler_name == handlerName) return;
        }

        // Track this handler
        meta.signal_handlers.push({
            handler_name: handlerName,
            signal_name: signalName
        });

        // Extract the handler method body as an event
        if (methodMap.exists(handlerName)) {
            var func = methodMap.get(handlerName);
            if (!events.exists("signal_" + handlerName)) {
                events.set("signal_" + handlerName, []);
                extractSignalHandler(handlerName, func, events.get("signal_" + handlerName));
            }
        }
    }

    function extractSignalHandler(name:String, func:Function, eventNodes:Array<IRNode>):Void {
        // Signal handlers have signature matching ArmSignalHandler:
        // void (*)(void* ctx, void* payload)
        // ctx = the trait data pointer passed to signal_connect
        // payload = the data pointer passed to signal_emit

        if (func.expr == null) return;

        switch (func.expr.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var node = exprToIR(expr);
                    if (node != null && node.type != "skip") {
                        eventNodes.push(node);
                    }
                }
            default:
                var node = exprToIR(func.expr);
                if (node != null && node.type != "skip") {
                    eventNodes.push(node);
                }
        }
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

        // Template uses {0}, {1}, {2} for args
        // Coord conversion: Blender (X,Y,Z) → N64 (X,Z,-Y)
        var c_code = switch (method) {
            case "translate":
                // translate(x, y, z) -> it_translate(transform, x, z, -y)
                "it_translate(&((ArmObject*)obj)->transform, {0}, {2}, -({1}));";
            case "rotate":
                // rotate(axis, angle) -> it_rotate_axis_global(transform, axis.x, axis.z, -axis.y, angle)
                "it_rotate_axis_global(&((ArmObject*)obj)->transform, ({0}).x, ({0}).z, -({0}).y, {1});";
            case "move":
                // move(axis, ?scale) -> it_move(transform, axis.x, axis.z, -axis.y, scale)
                "it_move(&((ArmObject*)obj)->transform, ({0}).x, ({0}).z, -({0}).y, {1});";
            case "setRotation":
                // setRotation(x, y, z) -> it_set_rot_euler(transform, x, z, -y)
                "it_set_rot_euler(&((ArmObject*)obj)->transform, {0}, {2}, -({1}));";
            case "look":
                "{ T3DVec3 _dir; it_look(&((ArmObject*)obj)->transform, &_dir); _dir; }";
            case "right":
                "{ T3DVec3 _dir; it_right(&((ArmObject*)obj)->transform, &_dir); _dir; }";
            case "up":
                "{ T3DVec3 _dir; it_up(&((ArmObject*)obj)->transform, &_dir); _dir; }";
            case "worldx":
                "it_world_x(&((ArmObject*)obj)->transform)";
            case "worldy":
                // Blender Y -> N64 Z
                "it_world_z(&((ArmObject*)obj)->transform)";
            case "worldz":
                // Blender Z -> N64 -Y
                "(-it_world_y(&((ArmObject*)obj)->transform))";
            case "reset":
                "it_reset(&((ArmObject*)obj)->transform);";
            case "buildMatrix":
                // N64 uses dirty flag system - just mark as dirty, matrix rebuilds automatically
                "((ArmObject*)obj)->transform.dirty = 1;";
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "transform_call",
            c_code: c_code,
            args: args
        };
    }

    // =========================================================================
    // Math call conversion - Math.sin() -> fm_sinf(), etc.
    // Uses libdragon's fast math functions where available (16x faster)
    // =========================================================================

    function convertMathCall(method:String, args:Array<IRNode>):IRNode {
        // Map Haxe Math methods to C math.h functions
        // Use libdragon's fm_* functions for sin/cos/atan2 (much faster on N64)
        var cFunc = switch (method) {
            case "sin": "fm_sinf";      // ~50 ticks vs ~800 ticks for sinf
            case "cos": "fm_cosf";      // ~50 ticks vs ~800 ticks for cosf
            case "tan": "tanf";
            case "asin": "asinf";
            case "acos": "acosf";
            case "atan": "atanf";
            case "atan2": "fm_atan2f";  // libdragon fast version
            case "sqrt": "sqrtf";
            case "pow": "powf";
            case "abs": "fabsf";
            case "floor": "fm_floorf"; // libdragon fast version
            case "ceil": "ceilf";
            case "round": "roundf";
            case "min": "fminf";
            case "max": "fmaxf";
            case "exp": "fm_exp";       // libdragon fast version (~3% error)
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

    // =========================================================================
    // Std call conversion - Std.int() -> (int32_t), Std.parseFloat() -> strtof()
    // =========================================================================

    function convertStdCall(method:String, args:Array<IRNode>):IRNode {
        return switch (method) {
            case "int":
                { type: "cast_call", value: "(int32_t)", args: args };
            case "parseFloat":
                { type: "math_call", value: "strtof", args: args };  // Note: strtof needs NULL as 2nd arg
            case "string":
                // Std.string(value) used standalone (not in concatenation)
                // In a + expression, StringConcatBuilder handles this
                // For standalone use, emit sprintf with single arg
                if (args.length > 0) {
                    var argType = args[0].type;
                    var format = switch (argType) {
                        case "float": "%.2f";
                        case "int": "%d";
                        case "member": "%d";  // Assume int for members
                        default: "%d";
                    };
                    { type: "sprintf", value: format, args: args };
                } else {
                    { type: "string", value: "" };
                }
            default:
                { type: "skip" };
        };
    }

    // =========================================================================
    // Object call conversion - object.remove(), object.getTrait(), etc.
    // =========================================================================

    function convertObjectCall(method:String, args:Array<IRNode>):IRNode {
        return switch (method) {
            case "remove":
                // object.remove() -> object_remove((ArmObject*)obj)
                { type: "object_call", c_code: "object_remove((ArmObject*)obj)" };
            case "getTrait", "addTrait", "removeTrait":
                // Trait system not supported on N64 - skip silently
                { type: "skip" };
            case "getChildren", "getChild":
                // Children access not yet supported - skip
                { type: "skip" };
            default:
                // Unknown object method - skip to avoid codegen fallback
                { type: "skip" };
        };
    }
}

#end
