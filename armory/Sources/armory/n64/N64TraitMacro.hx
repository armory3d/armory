package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;
import haxe.macro.Type;
import haxe.Json;
import sys.io.File;
import sys.FileSystem;

// Import modular components
import armory.n64.IRTypes;
import armory.n64.N64MacroBase;
import armory.n64.mapping.Constants;
import armory.n64.mapping.TypeMap;
import armory.n64.mapping.ButtonMap;
import armory.n64.mapping.SkipList;
import armory.n64.converters.ICallConverter;
import armory.n64.converters.SceneCallConverter;
import armory.n64.converters.CanvasCallConverter;
import armory.n64.converters.VecCallConverter;
import armory.n64.converters.PhysicsCallConverter;
import armory.n64.converters.TransformCallConverter;
import armory.n64.converters.MathCallConverter;
import armory.n64.converters.InputCallConverter;
import armory.n64.converters.SignalCallConverter;
import armory.n64.converters.StdCallConverter;
import armory.n64.converters.ObjectCallConverter;
import armory.n64.converters.AutoloadCallConverter;
import armory.n64.converters.AudioCallConverter;

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
                    default_value: N64MacroBase.serializeIRNode(m.defaultValue)
                });
            }

            // Convert events
            var eventsObj:Dynamic = {};
            for (eventName in ir.events.keys()) {
                var eventNodes = ir.events.get(eventName);
                Reflect.setField(eventsObj, eventName, [for (n in eventNodes) N64MacroBase.serializeIRNode(n)]);
            }

            // Generate struct_type and struct_def for signals with 2+ args
            N64MacroBase.generateSignalStructs(ir.meta.signals, ir.cName);

            // Generate preambles for signal handlers
            N64MacroBase.generateSignalHandlerPreambles(
                ir.meta.signal_handlers,
                ir.meta.signals,
                '${ir.name}Data'
            );

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

        N64MacroBase.writeJsonFile("n64_traits.json", output);
    }
}

// ============================================================================
// Trait Extractor
// ============================================================================

class TraitExtractor implements IExtractorContext {
    var className:String;
    var modulePath:String;
    var fields:Array<Field>;
    var members:Map<String, MemberIR>;
    var memberNames:Array<String>;
    var methodMap:Map<String, Function>;
    var events:Map<String, Array<IRNode>>;
    public var meta(default, null):TraitMeta;
    var localVarTypes:Map<String, String>;  // Track local variable types
    var memberTypes:Map<String, String>;    // Track member types for signal detection
    public var cName(default, null):String;  // C-safe name for this trait

    // Call converters for modular method call handling
    var converters:Array<ICallConverter>;

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
            uses_ui: false,
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

        // Initialize call converters
        this.converters = [
            new VecCallConverter(),
            new PhysicsCallConverter(),
            new TransformCallConverter(),
            new MathCallConverter(),
            new InputCallConverter(),
            new SignalCallConverter(),
            new StdCallConverter(),
            new ObjectCallConverter(),
            new SceneCallConverter(),
            new CanvasCallConverter(),
            new AutoloadCallConverter(),
            new AudioCallConverter(),
        ];
    }

    public function extract():TraitIR {
        // Pass 1: Extract members and methods
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "Dynamic";
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

        var haxeType = t != null ? N64MacroBase.complexTypeToString(t) : "Dynamic";
        if (!TypeMap.isSupported(haxeType)) return null;

        var defaultNode:IRNode = e != null ? exprToIR(e) : null;

        return {
            haxeType: haxeType,
            ctype: TypeMap.getCType(haxeType),
            defaultValue: defaultNode
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

    // IExtractorContext interface implementation
    public function extractStringArg(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            case EConst(CIdent(s)): s;
            default: null;
        };
    }

    public function getMemberType(name:String):String {
        return memberTypes.exists(name) ? memberTypes.get(name) : null;
    }

    public function getMethod(name:String):Function {
        return methodMap.exists(name) ? methodMap.get(name) : null;
    }

    // Interface methods for converters
    public function getMeta():TraitMeta {
        return meta;
    }

    public function getCName():String {
        return cName;
    }

    public function getEvents():Map<String, Array<IRNode>> {
        return events;
    }

    // Signal handler support for SignalCallConverter
    public function addSignalHandler(handlerName:String, signalName:String):Void {
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

    public function updateSignalArgTypes(signalName:String, params:Array<Expr>):Void {
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

    public function inferExprType(e:Expr):String {
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

    public function exprToIR(e:Expr):IRNode {
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
                var opStr = N64MacroBase.binopToString(op);
                if (op == OpAssign) {
                    // Check if assigning to transform.loc/rot/scale (mutating transform)
                    checkTransformMutation(e1);

                    // Special case: transform.scale = value -> emit transform_call with it_set_scale()
                    if (isTransformScaleAssign(e1)) {
                        var valueIR = exprToIR(e2);
                        // Swizzle: Blender (x, y, z) → N64 (x, z, y) and multiply by SCALE_FACTOR
                        var sf = Constants.SCALE_FACTOR_C;
                        {
                            type: "transform_call",
                            c_code: 'it_set_scale(&((ArmObject*)obj)->transform, ({0}).x * $sf, ({0}).z * $sf, ({0}).y * $sf);',
                            args: [valueIR]
                        };
                    }
                    // Special case: label.text = value -> emit label_set_text
                    else if (isLabelTextAssign(e1)) {
                        var labelName = extractLabelFromTextAssign(e1);
                        var valueIR = exprToIR(e2);
                        meta.uses_ui = true;
                        {
                            type: "label_set_text",
                            props: { label: labelName },
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
                { type: "unop", value: N64MacroBase.unopToString(op), children: [exprToIR(operand)], props: { postfix: postFix } };

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
                    var varType = v.type != null ? N64MacroBase.complexTypeToString(v.type) : getExprType(v.expr);
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

    // Check if expression is assignment to label.text (Label type variable)
    function isLabelTextAssign(expr:Expr):Bool {
        switch (expr.expr) {
            case EField(obj, "text"):
                // Check if the object is a Label-typed variable
                var objType = getExprType(obj);
                if (objType == "Label") return true;
            default:
        }
        return false;
    }

    // Extract the label variable name from label.text assignment
    function extractLabelFromTextAssign(expr:Expr):String {
        switch (expr.expr) {
            case EField(obj, "text"):
                switch (obj.expr) {
                    case EConst(CIdent(name)): return name;
                    default:
                }
            default:
        }
        return null;
    }

    function convertFieldAccess(obj:Expr, field:String):IRNode {
        // Handle Scene.active.raw.name -> scene_get_name(scene_get_current_id())
        if (field == "name") {
            switch (obj.expr) {
                case EField(innerObj, "raw"):
                    switch (innerObj.expr) {
                        case EField(sceneExpr, "active"):
                            switch (sceneExpr.expr) {
                                case EConst(CIdent("Scene")):
                                    return { type: "c_literal", c_code: "scene_get_name(scene_get_current_id())" };
                                default:
                            }
                        default:
                    }
                default:
            }
        }

        // Handle Assets.sounds.sound_name -> "rom:/sound_name.wav64"
        switch (obj.expr) {
            case EField(innerObj, "sounds"):
                switch (innerObj.expr) {
                    case EConst(CIdent("Assets")):
                        var soundPath = 'rom:/${field}.wav64';
                        return { type: "string", value: soundPath, c_code: '"$soundPath"' };
                    default:
                }
            default:
        }

        // Handle transform access
        switch (obj.expr) {
            case EField(innerObj, "transform"):
                meta.uses_transform = true;
                return { type: "field_access", object: { type: "ident", value: "object" }, value: "transform." + field };
            case EConst(CIdent("transform")):
                meta.uses_transform = true;
                return { type: "field_access", object: { type: "ident", value: "object" }, value: "transform." + field };
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
            return { type: "field_access", object: exprToIR(obj), value: field };
        }

        return { type: "field_access", object: exprToIR(obj), value: field };
    }

    /**
     * Unified type inference from Haxe expressions.
     * Returns the Haxe type name (Int, Float, String, Vec2, Label, Signal, etc.) or "Dynamic" if unknown.
     */
    public function getExprType(e:Expr):String {
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

        // Try modular converters first (handles Vec, Physics, Transform, Math, Input, Signal, Std, Object, Scene, Canvas)
        switch (callExpr.expr) {
            case EField(obj, method):
                for (conv in converters) {
                    var result = conv.tryConvert(obj, method, args, params, this);
                    if (result != null) return result;
                }

                // Unsupported APIs - explicitly skip
                switch (obj.expr) {
                    case EConst(CIdent("Audio")), EConst(CIdent("Tween")), EConst(CIdent("Network")), EConst(CIdent("Koui")):
                        return { type: "skip" };
                    default:
                }

                // Fallback: generic call with object (for unknown method calls)
                return {
                    type: "call",
                    method: method,
                    object: exprToIR(obj),
                    args: args
                };
            default:
        }

        switch (callExpr.expr) {
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
}

#end
