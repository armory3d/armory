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
import armory.n64.converters.TweenCallConverter;
import armory.n64.converters.Graphics2CallConverter;
import armory.n64.converters.MapCallConverter;
import armory.n64.converters.ArrayCallConverter;
import armory.n64.converters.StringCallConverter;

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

        // Detect parent class for inheritance support
        var parentName:String = null;
        if (cls.superClass != null) {
            var superClass = cls.superClass.t.get();
            var superModule = superClass.module;
            // Only track user traits as parents (not iron.Trait or armory.* classes)
            if (superModule.indexOf("iron.") != 0 && superModule.indexOf("armory.") != 0) {
                parentName = superClass.name;
            }
        }

        var fields = Context.getBuildFields();

        // Extract trait IR
        var extractor = new TraitExtractor(className, modulePath, fields, parentName);
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
            // Also include if trait has a parent (needed for inheritance chain)
            var hasEvents = Lambda.count(ir.events) > 0;
            var hasContactEvents = ir.meta.contact_events.length > 0;
            var hasButtonEvents = ir.meta.button_events.length > 0;
            var hasParent = ir.parent != null;
            if (!hasEvents && !hasContactEvents && !hasButtonEvents && !ir.needsData && !hasParent) continue;

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

            // Convert methods (non-lifecycle callable functions)
            var methodsObj:Dynamic = {};
            for (methodName in ir.methods.keys()) {
                var method = ir.methods.get(methodName);
                var paramsArr = [for (p in method.params) {
                    name: p.name,
                    haxeType: p.haxeType,
                    ctype: p.ctype
                }];
                var methodObj:Dynamic = {
                    name: method.name,
                    cName: method.cName,
                    params: paramsArr,
                    returnType: method.returnType,
                    body: [for (n in method.body) N64MacroBase.serializeIRNode(n)]
                };
                Reflect.setField(methodsObj, methodName, methodObj);
            }

            // Generate struct_type and struct_def for signals with 2+ args
            N64MacroBase.generateSignalStructs(ir.meta.signals, ir.cName);

            // Generate preambles for signal handlers
            N64MacroBase.generateSignalHandlerPreambles(
                ir.meta.signal_handlers,
                ir.meta.signals,
                '${ir.name}Data'
            );

            // Build trait JSON object
            var traitObj:Dynamic = {
                module: ir.module,
                c_name: ir.cName,
                members: membersArr,
                methods: methodsObj,  // All callable methods (non-lifecycle)
                events: eventsObj,
                meta: ir.meta
            };

            // Add parent if this trait inherits from another user trait
            if (ir.parent != null) {
                Reflect.setField(traitObj, "parent", ir.parent);
            }

            Reflect.setField(traits, name, traitObj);
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
    var methodIRMap:Map<String, MethodIR>;   // Extracted methods as IR for C generation
    var publicMethods:Map<String, Bool>;     // Track which methods are public (potentially virtual)
    var events:Map<String, Array<IRNode>>;
    public var meta(default, null):TraitMeta;
    var localVarTypes:Map<String, String>;  // Track local variable types
    var memberTypes:Map<String, String>;    // Track member types for signal detection
    public var cName(default, null):String;  // C-safe name for this trait

    // Lifecycle method names that are handled specially (not as callable methods)
    static var lifecycleMethodNames:Array<String> = ["new", "__onInit", "__onUpdate", "__onFixedUpdate", "__onLateUpdate", "__onRemove", "__onRender2D"];

    // Call converters for modular method call handling
    var converters:Array<ICallConverter>;

    /**
     * Input handling mode:
     * - true (default, Armory style): Keep input checks inline in update() as regular if-statements.
     *   The InputCallConverter converts `gamepad.started("a")` to `input_started(N64_BTN_A)`.
     *   This means guards like `if (!active) return;` naturally block all subsequent code including input checks.
     *
     * - false (event extraction): Extract `if (gamepad.started("a"))` as separate btn_a_started event handlers.
     *   This matches libdragon's event-driven style but means guards in update() won't block button events.
     */
    static var useInlineInputMode:Bool = true;

    // Inheritance support
    var parentName:String;  // Parent trait name (null if none)

    public function new(className:String, modulePath:String, fields:Array<Field>, parentName:String = null) {
        this.className = className;
        this.modulePath = modulePath;
        this.fields = fields;
        this.parentName = parentName;
        this.members = new Map();
        this.memberNames = [];
        this.methodMap = new Map();
        this.methodIRMap = new Map();
        this.publicMethods = new Map();  // Track which methods are public (potentially virtual)
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
            uses_tween: false,
            uses_autoload: false,
            buttons_used: [],
            button_events: [],
            contact_events: [],
            signals: [],
            signal_handlers: [],
            global_signals: [],
            has_remove_update: false,
            has_remove_fixed_update: false,
            has_remove_late_update: false,
            has_remove_render2d: false,
            dynamic_updates: [],
            dynamic_fixed_updates: []
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
            new TweenCallConverter(),
            new Graphics2CallConverter(),
            new MapCallConverter(),
            new ArrayCallConverter(),
            new StringCallConverter(),
        ];

        // NOTE: We do NOT load inherited member types here to avoid triggering
        // early type resolution. Instead, inherited member checks happen lazily
        // when the parent trait's IR is available (during Python code generation).
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
                    // Check if method is public (has APublic access)
                    var isPublic = field.access != null && Lambda.has(field.access, APublic);
                    publicMethods.set(field.name, isPublic);
                default:
            }
        }

        // Pass 2: Find lifecycle registrations and extract events
        // This finds ALL registered lifecycles (for code extraction)
        var lifecycles = findLifecycles();
        // This finds only STATICALLY registered lifecycles (for initial enabled state)
        var staticLifecycles = findStaticLifecycles();

        // Pass 3: Convert lifecycle functions to events
        // on_add runs BEFORE on_ready - used for setting up autoload references
        if (lifecycles.add != null) {
            extractEvents("on_add", lifecycles.add);
        }
        if (lifecycles.init != null) {
            extractEvents("on_ready", lifecycles.init);
        }

        // Handle multiple update functions - each gets its own event
        // Collect keys first to avoid iterator issues
        var updateCallbackNames = [for (k in lifecycles.updates.keys()) k];
        if (updateCallbackNames.length > 0) {
            // We have named update functions - generate separate events for each
            for (callbackName in updateCallbackNames) {
                var body = lifecycles.updates.get(callbackName);
                if (body != null) {
                    // Use format: on_update_functionName (e.g., on_update_update, on_update_winUpdate)
                    extractEvents("on_update_" + callbackName, body);
                    meta.dynamic_updates.push(callbackName);
                }
            }
        } else if (lifecycles.update != null) {
            // Fallback for inline/anonymous update functions
            extractEvents("on_update", lifecycles.update);
        }

        // Handle multiple fixed update functions - each gets its own event
        var fixedUpdateCallbackNames = [for (k in lifecycles.fixed_updates.keys()) k];
        if (fixedUpdateCallbackNames.length > 0) {
            // We have named fixed update functions - generate separate events for each
            for (callbackName in fixedUpdateCallbackNames) {
                var body = lifecycles.fixed_updates.get(callbackName);
                if (body != null) {
                    // Use format: on_fixed_update_functionName
                    extractEvents("on_fixed_update_" + callbackName, body);
                    meta.dynamic_fixed_updates.push(callbackName);
                }
            }
        } else if (lifecycles.fixed_update != null) {
            // Fallback for inline/anonymous fixed update functions
            extractEvents("on_fixed_update", lifecycles.fixed_update);
        }
        if (lifecycles.late_update != null) {
            extractEvents("on_late_update", lifecycles.late_update);
        }
        if (lifecycles.remove != null) {
            extractEvents("on_remove", lifecycles.remove);
        }
        if (lifecycles.render2d != null) {
            extractEvents("on_render2d", lifecycles.render2d);
        }

        // Auto-add per-callback _update_<name>_enabled members if trait has multiple update functions
        // Each update function gets its own enabled flag for independent enable/disable
        if (meta.dynamic_updates.length > 0) {
            for (callbackName in meta.dynamic_updates) {
                var flagName = "_update_" + callbackName + "_enabled";
                var isStaticallyRegistered = staticLifecycles.static_updates.exists(callbackName);
                members.set(flagName, {
                    haxeType: "Bool",
                    ctype: "bool",
                    defaultValue: { type: "bool", value: isStaticallyRegistered }
                });
                memberNames.push(flagName);
            }
        } else if (meta.has_remove_update) {
            // Fallback: single _update_enabled for anonymous/inline update functions
            var hasStaticUpdate = staticLifecycles.update != null;
            members.set("_update_enabled", {
                haxeType: "Bool",
                ctype: "bool",
                defaultValue: { type: "bool", value: hasStaticUpdate }
            });
            memberNames.push("_update_enabled");
        }

        // Auto-add _late_update_enabled member if trait uses removeLateUpdate()
        // Initial value: true if trait has STATIC late_update function, false if only dynamic registration
        if (meta.has_remove_late_update) {
            var hasStaticLateUpdate = staticLifecycles.late_update != null;
            members.set("_late_update_enabled", {
                haxeType: "Bool",
                ctype: "bool",
                defaultValue: { type: "bool", value: hasStaticLateUpdate }
            });
            memberNames.push("_late_update_enabled");
        }

        // Auto-add per-callback _fixed_update_<name>_enabled members if trait has multiple fixed update functions
        // Each fixed update function gets its own enabled flag for independent enable/disable
        if (meta.dynamic_fixed_updates.length > 0) {
            for (callbackName in meta.dynamic_fixed_updates) {
                var flagName = "_fixed_update_" + callbackName + "_enabled";
                var isStaticallyRegistered = staticLifecycles.static_fixed_updates.exists(callbackName);
                members.set(flagName, {
                    haxeType: "Bool",
                    ctype: "bool",
                    defaultValue: { type: "bool", value: isStaticallyRegistered }
                });
                memberNames.push(flagName);
            }
        } else if (meta.has_remove_fixed_update) {
            // Fallback: single _fixed_update_enabled for anonymous/inline fixed update functions
            var hasStaticFixedUpdate = staticLifecycles.fixed_update != null;
            members.set("_fixed_update_enabled", {
                haxeType: "Bool",
                ctype: "bool",
                defaultValue: { type: "bool", value: hasStaticFixedUpdate }
            });
            memberNames.push("_fixed_update_enabled");
        }

        // Auto-add _render2d_enabled member if trait uses removeRender2D() or notifyOnRender2D() at runtime
        // Initial value: true if trait has STATIC render2d function, false if only dynamic registration
        if (meta.has_remove_render2d) {
            var hasStaticRender2d = staticLifecycles.render2d != null;
            members.set("_render2d_enabled", {
                haxeType: "Bool",
                ctype: "bool",
                defaultValue: { type: "bool", value: hasStaticRender2d }
            });
            memberNames.push("_render2d_enabled");
        }

        // Pass 4: Extract ALL non-lifecycle methods as callable C functions
        extractMethods();

        // Generate C-safe name is now done in constructor
        // cName is available as this.cName

        return {
            name: className,
            module: modulePath,
            cName: cName,
            needsData: memberNames.length > 0,
            parent: parentName,  // Parent trait name for inheritance (null if none)
            members: members,
            methods: methodIRMap,  // All callable methods (non-lifecycle)
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

    /**
     * Extract ALL non-lifecycle methods as callable C functions.
     * Each method becomes a MethodIR with its parameters and body converted to IR.
     */
    function extractMethods():Void {
        for (methodName in methodMap.keys()) {
            // Skip lifecycle methods - they're handled as events
            if (Lambda.has(lifecycleMethodNames, methodName)) continue;

            // Skip internal/inherited Haxe methods
            if (methodName.charAt(0) == '_' && methodName != "new") continue;

            var method = methodMap.get(methodName);
            if (method == null || method.expr == null) continue;

            // Extract parameter info and add to localVarTypes for capture detection
            var params:Array<MethodParamIR> = [];
            if (method.args != null) {
                for (arg in method.args) {
                    var haxeType = arg.type != null ? N64MacroBase.complexTypeToString(arg.type) : "Dynamic";
                    params.push({
                        name: arg.name,
                        haxeType: haxeType,
                        ctype: TypeMap.getCType(haxeType)
                    });
                    // Track parameter as local variable for capture detection
                    localVarTypes.set(arg.name, haxeType);
                }
            }

            // Determine return type
            var returnType = "void";
            if (method.ret != null) {
                var retHaxeType = N64MacroBase.complexTypeToString(method.ret);
                returnType = TypeMap.getCType(retHaxeType);
            }

            // Convert method body to IR
            var bodyNodes:Array<IRNode> = [];
            switch (method.expr.expr) {
                case EBlock(exprs):
                    for (e in exprs) {
                        var node = exprToIR(e);
                        if (node != null && node.type != "skip") {
                            bodyNodes.push(node);
                        }
                    }
                default:
                    var node = exprToIR(method.expr);
                    if (node != null && node.type != "skip") {
                        bodyNodes.push(node);
                    }
            }

            // Generate C function name: arm_<traitname>_<methodname>
            var methodCName = "arm_" + cName.substring(4) + "_" + methodName.toLowerCase();  // cName already starts with "arm_"

            // Virtual Method Detection (Haxe side):
            // Public methods are marked as potentially virtual because they can be overridden
            // by child traits. The Python generator will use this flag to:
            // 1. Generate vtable function pointers in the data struct
            // 2. Initialize vtable pointers in on_ready
            // 3. Emit vtable dispatch calls instead of direct calls
            //
            // If this flag is missing (older IR), Python has fallback detection that
            // scans the inheritance hierarchy to identify virtual methods.
            var isVirtual = publicMethods.exists(methodName) && publicMethods.get(methodName);

            methodIRMap.set(methodName, {
                name: methodName,
                cName: methodCName,
                params: params,
                returnType: returnType,
                body: bodyNodes,
                isVirtual: isVirtual
            });

            // Clear method-specific local variables (parameters) after processing
            if (method.args != null) {
                for (arg in method.args) {
                    localVarTypes.remove(arg.name);
                }
            }
        }
    }

    function findLifecycles():{init:Expr, add:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr, render2d:Expr, updates:Map<String, Expr>, fixed_updates:Map<String, Expr>} {
        var result = {init: null, add: null, update: null, fixed_update: null, late_update: null, remove: null, render2d: null, updates: new Map<String, Expr>(), fixed_updates: new Map<String, Expr>()};

        // Scan ALL methods for lifecycle registrations (for code extraction)
        for (methodName in methodMap.keys()) {
            var method = methodMap.get(methodName);
            if (method != null && method.expr != null) {
                scanForLifecycles(method.expr, result, true);
            }
        }

        return result;
    }

    // Find only STATICALLY registered lifecycles (called from constructor/init path)
    // Used to determine initial enabled state for dynamic toggle flags
    function findStaticLifecycles():{init:Expr, add:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr, render2d:Expr, static_updates:Map<String, Bool>, static_fixed_updates:Map<String, Bool>} {
        var result = {init: null, add: null, update: null, fixed_update: null, late_update: null, remove: null, render2d: null, static_updates: new Map<String, Bool>(), static_fixed_updates: new Map<String, Bool>()};

        // Only scan constructor - lifecycle registrations elsewhere are "dynamic"
        var ctor = methodMap.get("new");
        if (ctor != null && ctor.expr != null) {
            scanForStaticLifecycles(ctor.expr, result, true);
        }

        return result;
    }

    // Scan for lifecycle registrations (finds all, for code extraction)
    function scanForLifecycles(e:Expr, result:{init:Expr, add:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr, render2d:Expr, updates:Map<String, Expr>, fixed_updates:Map<String, Expr>}, inInitPath:Bool):Void {
        if (e == null) return;

        switch (e.expr) {
            case ECall(callExpr, params):
                var funcName = getFuncName(callExpr);
                if (params.length > 0) {
                    var body = resolveCallback(params[0]);
                    switch (funcName) {
                        case "notifyOnInit": result.init = body;
                        case "notifyOnAdd": result.add = body;
                        case "notifyOnUpdate":
                            // Track update callbacks by their function name
                            var callbackName = getCallbackName(params[0]);
                            if (callbackName != null && body != null) {
                                result.updates.set(callbackName, body);
                            }
                            // Also keep backward compatibility with single update field
                            result.update = body;
                        case "notifyOnFixedUpdate":
                            // Track fixed update callbacks by their function name
                            var callbackName = getCallbackName(params[0]);
                            if (callbackName != null && body != null) {
                                result.fixed_updates.set(callbackName, body);
                            }
                            // Also keep backward compatibility with single fixed_update field
                            result.fixed_update = body;
                        case "notifyOnLateUpdate": result.late_update = body;
                        case "notifyOnRemove": result.remove = body;
                        case "notifyOnRender2D": result.render2d = body;
                        default:
                    }
                }
                // Scan parameters AND the callExpr (for chained calls like tween.float(...).start())
                scanForLifecycles(callExpr, result, inInitPath);
                for (p in params) scanForLifecycles(p, result, inInitPath);
            case EBlock(exprs):
                for (expr in exprs) scanForLifecycles(expr, result, inInitPath);
            case EFunction(_, f):
                // Preserve inInitPath - if we're scanning a function passed to notifyOnInit,
                // the body is still part of the init path. The path only breaks when
                // scanning params of non-init callbacks (handled in ECall case above).
                if (f.expr != null) scanForLifecycles(f.expr, result, inInitPath);
            default:
                e.iter(function(sub) scanForLifecycles(sub, result, inInitPath));
        }
    }

    // Scan for STATIC lifecycle registrations only (for initial enabled state)
    function scanForStaticLifecycles(e:Expr, result:{init:Expr, add:Expr, update:Expr, fixed_update:Expr, late_update:Expr, remove:Expr, render2d:Expr, static_updates:Map<String, Bool>, static_fixed_updates:Map<String, Bool>}, inInitPath:Bool):Void {
        if (e == null) return;

        switch (e.expr) {
            case ECall(callExpr, params):
                var funcName = getFuncName(callExpr);
                if (params.length > 0) {
                    var body = resolveCallback(params[0]);
                    // Only record lifecycle registrations if we're in the init path
                    if (inInitPath) {
                        switch (funcName) {
                            case "notifyOnInit": result.init = body;
                            case "notifyOnAdd": result.add = body;
                            case "notifyOnUpdate":
                                // Track static update callbacks by name
                                var callbackName = getCallbackName(params[0]);
                                if (callbackName != null) {
                                    result.static_updates.set(callbackName, true);
                                }
                                result.update = body;
                            case "notifyOnFixedUpdate":
                                // Track static fixed update callbacks by name
                                var callbackName = getCallbackName(params[0]);
                                if (callbackName != null) {
                                    result.static_fixed_updates.set(callbackName, true);
                                }
                                result.fixed_update = body;
                            case "notifyOnLateUpdate": result.late_update = body;
                            case "notifyOnRemove": result.remove = body;
                            case "notifyOnRender2D": result.render2d = body;
                            default:
                        }
                    }
                    // Determine if we should continue in init path
                    var isInitCallback = funcName == "notifyOnInit" || funcName == "notifyOnAdd";
                    for (p in params) scanForStaticLifecycles(p, result, inInitPath && isInitCallback);
                }
                // Scan the callExpr for chained calls - stay in init path
                scanForStaticLifecycles(callExpr, result, inInitPath);
            case EBlock(exprs):
                for (expr in exprs) scanForStaticLifecycles(expr, result, inInitPath);
            case EFunction(_, f):
                // Preserve inInitPath through function bodies
                if (f.expr != null) scanForStaticLifecycles(f.expr, result, inInitPath);
            default:
                e.iter(function(sub) scanForStaticLifecycles(sub, result, inInitPath));
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

    // Get the name of the callback function (for dynamic update tracking)
    function getCallbackName(e:Expr):String {
        return switch (e.expr) {
            case EFunction(_, _): null; // Inline function - no name
            case EField(_, methodName): methodName;
            case EConst(CIdent(methodName)): methodName;
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
                // Only extract as separate event if NOT in inline input mode
                if (inputEvent != null && eelse == null && !useInlineInputMode) {
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
                // Regular if (or inline input mode) - add to statements as normal if
                // When useInlineInputMode=true, InputCallConverter handles the conversion
                // of gamepad.started("a") -> input_started(N64_BTN_A) as the condition
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

    // Check if expression is 'super' keyword
    function isSuperExpr(e:Expr):Bool {
        return switch (e.expr) {
            case EConst(CIdent("super")): true;
            default: false;
        };
    }

    public function getMemberType(name:String):String {
        return memberTypes.exists(name) ? memberTypes.get(name) : null;
    }

    public function getInheritedMemberType(name:String):String {
        // Inherited member types are resolved at Python code generation time
        // to avoid triggering early type resolution during macro expansion
        return null;
    }

    public function getLocalVarType(name:String):String {
        return localVarTypes.exists(name) ? localVarTypes.get(name) : null;
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

    public function getParentName():String {
        return parentName;
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

    public function isAutoload():Bool {
        return false;  // Traits are not autoloads
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
                    }
                    // Special case: g2.color = value -> emit render2d_set_color
                    else if (isGraphics2ColorAssign(e1)) {
                        var valueIR = exprToIR(e2);
                        {
                            type: "render2d_set_color",
                            args: [valueIR]
                        };
                    }
                    // Skip other g2 property assignments (imageScaleQuality, etc.)
                    else if (isGraphics2PropertyAssign(e1)) {
                        { type: "skip" };
                    }
                    // Special case: AutoloadClass.member = this where member is a trait type
                    // e.g., MainInstances.player = this -> maininstances_player = data
                    else if (isAutoloadTraitAssign(e1, e2)) {
                        var autoloadInfo = getAutoloadFieldInfo(e1);
                        meta.uses_autoload = true;
                        {
                            type: "autoload_trait_assign",
                            props: {
                                autoload: autoloadInfo.c_name,
                                member: autoloadInfo.field
                            }
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

            // While loop
            case EWhile(econd, ebody, normalWhile):
                { type: normalWhile ? "while" : "do_while", children: [exprToIR(econd), exprToIR(ebody)] };

            // For loop (range-based)
            case EFor(it, ebody):
                convertForLoop(it, ebody);

            // Break statement
            case EBreak:
                { type: "break" };

            // Continue statement
            case EContinue:
                { type: "continue" };

            // Ternary operator
            case ETernary(econd, eif, eelse):
                { type: "ternary", children: [exprToIR(econd), exprToIR(eif), exprToIR(eelse)] };

            // Array access
            case EArray(e1, e2):
                { type: "array_access", children: [exprToIR(e1), exprToIR(e2)] };

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
        // Check for local variables (including method parameters)
        if (localVarTypes.exists(name)) {
            return { type: "ident", value: name };
        }
        // Check if this is a method reference (function pointer)
        // e.g., fadeOut(initTransitionDone) -> fadeOut(arm_gamescene_inittransitiondone)
        if (methodMap.exists(name)) {
            // Generate C function name for this method
            var methodCName = "arm_" + cName.substring(4) + "_" + name.toLowerCase();
            return {
                type: "method_ref",
                method: name,
                cName: methodCName,
                trait: className
            };
        }
        if (SkipList.shouldSkipMember(name) || SkipList.shouldSkipClass(name)) {
            return { type: "skip" };
        }
        // If we have a parent and this isn't a known local/member, it might be inherited
        // Emit as potentially_inherited - Python will resolve using parent IR
        if (parentName != null) {
            return {
                type: "potentially_inherited",
                value: name,
                parent: parentName
            };
        }
        return { type: "ident", value: name };
    }

    // Convert for loop: for (i in 0...10) pattern
    function convertForLoop(it:Expr, body:Expr):IRNode {
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

    // Check if expression is assignment to g2.color (Graphics2 color property)
    function isGraphics2ColorAssign(expr:Expr):Bool {
        switch (expr.expr) {
            case EField(obj, "color"):
                switch (obj.expr) {
                    case EConst(CIdent(name)):
                        // Check for common graphics2 parameter names or type
                        if (name == "g" || name == "g2") return true;
                        var objType = getExprType(obj);
                        if (objType == "kha.graphics2.Graphics" || objType == "Graphics") return true;
                    default:
                }
            default:
        }
        return false;
    }

    // Check if expression is assignment to any g2 property (for skipping unsupported ones)
    function isGraphics2PropertyAssign(expr:Expr):Bool {
        switch (expr.expr) {
            case EField(obj, _):
                switch (obj.expr) {
                    case EConst(CIdent(name)):
                        if (name == "g" || name == "g2") return true;
                        var objType = getExprType(obj);
                        if (objType == "kha.graphics2.Graphics" || objType == "Graphics") return true;
                    default:
                }
            default:
        }
        return false;
    }

    // Check if this is an assignment to an autoload trait member with `this` on the right side
    // e.g., MainInstances.player = this
    function isAutoloadTraitAssign(lhs:Expr, rhs:Expr):Bool {
        // Check if rhs is `this`
        switch (rhs.expr) {
            case EConst(CIdent("this")):
                // Check if lhs is AutoloadClass.field
                switch (lhs.expr) {
                    case EField(obj, _):
                        switch (obj.expr) {
                            case EConst(CIdent(className)):
                                return AutoloadCallConverter.getAutoloadCName(className) != null;
                            default:
                        }
                    default:
                }
            default:
        }
        return false;
    }

    // Get autoload field info from expression (for autoload trait assignments)
    function getAutoloadFieldInfo(expr:Expr):{c_name:String, field:String} {
        switch (expr.expr) {
            case EField(obj, field):
                switch (obj.expr) {
                    case EConst(CIdent(className)):
                        var cName = AutoloadCallConverter.getAutoloadCName(className);
                        if (cName != null) {
                            return { c_name: cName, field: field.toLowerCase() };
                        }
                    default:
                }
            default:
        }
        return { c_name: "", field: "" };
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
        // Check if accessing a field on a skipped class (like Gamepad.buttons)
        switch (obj.expr) {
            case EConst(CIdent(className)):
                if (SkipList.shouldSkipClass(className)) {
                    return { type: "skip" };
                }
            default:
        }

        // Handle autoloadVar.object -> get object pointer from trait data
        // Pattern: EField(EField(AutoloadClass, traitMember), "object")
        if (field == "object") {
            switch (obj.expr) {
                case EField(innerObj, memberName):
                    switch (innerObj.expr) {
                        case EConst(CIdent(className)):
                            var cName = AutoloadCallConverter.getAutoloadCName(className);
                            if (cName != null) {
                                // Found AutoloadClass.traitMember.object pattern
                                meta.uses_autoload = true;
                                return {
                                    type: "autoload_trait_object",
                                    value: field,
                                    props: {
                                        autoload: cName,
                                        member: memberName
                                    }
                                };
                            }
                        default:
                    }
                default:
            }
        }

        // Handle AutoloadClass.member field access
        switch (obj.expr) {
            case EConst(CIdent(className)):
                var cName = AutoloadCallConverter.getAutoloadCName(className);
                if (cName != null) {
                    meta.uses_autoload = true;
                    return {
                        type: "autoload_field",
                        value: field,
                        props: {
                            autoload: cName,
                            member: field
                        }
                    };
                }
            default:
        }

        // Handle kha.Window.get(0).width/height -> render2d_get_width()/height()
        if (field == "width" || field == "height") {
            switch (obj.expr) {
                case ECall(callExpr, _):
                    // Check if this is kha.Window.get(0) or Window.get(0)
                    switch (callExpr.expr) {
                        case EField(windowExpr, "get"):
                            switch (windowExpr.expr) {
                                case EConst(CIdent("Window")):
                                    // Window.get(0).width/height
                                    var funcName = field == "width" ? "render2d_get_width()" : "render2d_get_height()";
                                    return { type: "c_literal", c_code: funcName };
                                case EField(khaExpr, "Window"):
                                    // kha.Window.get(0).width/height
                                    switch (khaExpr.expr) {
                                        case EConst(CIdent("kha")):
                                            var funcName = field == "width" ? "render2d_get_width()" : "render2d_get_height()";
                                            return { type: "c_literal", c_code: funcName };
                                        default:
                                    }
                                default:
                            }
                        default:
                    }
                default:
            }
        }

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

        // Handle Scene.active.getGroup(groupName).length -> scene_get_group_count(groupName)
        if (field == "length") {
            switch (obj.expr) {
                case ECall(callExpr, params):
                    // Check for getGroup call
                    switch (callExpr.expr) {
                        case EField(sceneActiveExpr, "getGroup"):
                            // Check for Scene.active
                            switch (sceneActiveExpr.expr) {
                                case EField(sceneExpr, "active"):
                                    switch (sceneExpr.expr) {
                                        case EConst(CIdent("Scene")):
                                            // Found Scene.active.getGroup(x).length
                                            if (params.length > 0) {
                                                var groupArg = exprToIR(params[0]);
                                                return { type: "scene_get_group_count", args: [groupArg] };
                                            }
                                        default:
                                    }
                                default:
                            }
                        default:
                    }
                default:
            }
        }

        // Handle Color.Black, Color.White, etc. -> RGBA32 for N64
        switch (obj.expr) {
            case EConst(CIdent("Color")):
                var colorValue = switch (field) {
                    case "Black": "RGBA32(0, 0, 0, 255)";
                    case "White": "RGBA32(255, 255, 255, 255)";
                    case "Red": "RGBA32(255, 0, 0, 255)";
                    case "Green": "RGBA32(0, 255, 0, 255)";
                    case "Blue": "RGBA32(0, 0, 255, 255)";
                    case "Transparent": "RGBA32(0, 0, 0, 0)";
                    default: "RGBA32(0, 0, 0, 255)";
                };
                return { type: "c_literal", c_code: colorValue };
            default:
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
                // Check if innerObj is a specific object (not `this` or `object`)
                var ownerNode:IRNode = switch (innerObj.expr) {
                    case EConst(CIdent("this")), EConst(CIdent("object")):
                        // Self-reference - use "object"
                        { type: "ident", value: "object" };
                    default:
                        // External object (e.g., target.transform.loc)
                        exprToIR(innerObj);
                };
                return { type: "field_access", object: ownerNode, value: "transform." + field };
            case EConst(CIdent("transform")):
                meta.uses_transform = true;
                return { type: "field_access", object: { type: "ident", value: "object" }, value: "transform." + field };
            case EConst(CIdent("Time")):
                if (field == "delta") {
                    meta.uses_time = true;
                    return { type: "ident", value: "dt" };
                } else if (field == "scale") {
                    meta.uses_time = true;
                    return { type: "ident", value: "time_scale" };
                } else if (field == "fixedStep") {
                    meta.uses_time = true;
                    return { type: "ident", value: "time_fixed_step" };
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
                        var objType = getExprType(obj);
                        // Vec method calls return same Vec type
                        if (objType != null && StringTools.startsWith(objType, "Vec")) {
                            if (method == "mult" || method == "add" || method == "sub" ||
                                method == "normalize" || method == "clone" || method == "cross") {
                                return objType;
                            }
                        }
                        // Tween method calls return Tween (for chaining)
                        if (objType != null && objType.indexOf("Tween") >= 0) {
                            if (method == "float" || method == "vec4" || method == "delay" ||
                                method == "start" || method == "pause" || method == "stop") {
                                return "Tween";
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
                // Check for super.method() first
                if (isSuperExpr(obj)) {
                    if (parentName == null) {
                        // No parent - skip (shouldn't happen in valid Haxe code)
                        return { type: "skip" };
                    }
                    return {
                        type: "super_call",
                        value: parentName,    // Parent trait name
                        method: method,       // Method name (e.g., "onReady", "onUpdate")
                        args: args
                    };
                }

                // Check for Time.time() special case
                switch (obj.expr) {
                    case EConst(CIdent("Time")):
                        if (method == "time") {
                            meta.uses_time = true;
                            // Time.time() -> time_get()
                            return { type: "call", value: "time_get", args: [] };
                        }
                    // Handle Color.fromFloats(r, g, b, a) -> ARGB uint32 construction
                    case EConst(CIdent("Color")):
                        if (method == "fromFloats") {
                            // Color.fromFloats(r, g, b, a) -> RGBA32 macro inverted to ARGB for storage
                            // We'll emit a helper that constructs the uint32 at runtime
                            return {
                                type: "color_from_floats",
                                args: args
                            };
                        }
                    // Check for this.method() - call to local method on this object
                    case EConst(CIdent("this")):
                        // Check if this is a call to a local method
                        if (methodMap.exists(method)) {
                            var methodFunc = methodMap.get(method);
                            if (methodFunc != null && methodFunc.expr != null) {
                                // Inline the method body
                                var bodyNodes:Array<IRNode> = [];
                                switch (methodFunc.expr.expr) {
                                    case EBlock(exprs):
                                        for (e in exprs) {
                                            var node = exprToIR(e);
                                            if (node != null && node.type != "skip") {
                                                bodyNodes.push(node);
                                            }
                                        }
                                    default:
                                        var node = exprToIR(methodFunc.expr);
                                        if (node != null && node.type != "skip") {
                                            bodyNodes.push(node);
                                        }
                                }
                                return { type: "block", children: bodyNodes };
                            }
                        }
                        // Not a local method - emit as method_call (might be from parent)
                        return {
                            type: "method_call",
                            method: method,
                            object: { type: "ident", value: "this" },
                            args: args
                        };
                    default:
                }

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
                // Use method_call type to match autoload behavior and ensure proper handling
                return {
                    type: "method_call",
                    method: method,
                    object: exprToIR(obj),
                    args: args
                };

            default:
        }

        switch (callExpr.expr) {
            // super() - call parent constructor (on_ready)
            case EConst(CIdent("super")):
                if (parentName == null) {
                    // No parent - skip (shouldn't happen in valid Haxe code)
                    return { type: "skip" };
                }
                return {
                    type: "super_call",
                    value: parentName,    // Parent trait name
                    method: "new",        // Constructor - maps to on_ready
                    args: args
                };

            case EConst(CIdent(funcName)):
                // Skip lifecycle registration calls - they're handled by scanForLifecycles
                // Note: notifyOnRender2D is now handled separately, not skipped
                if (funcName == "notifyOnInit" ||
                    funcName == "notifyOnFixedUpdate" || funcName == "notifyOnLateUpdate" ||
                    funcName == "notifyOnRemove" || funcName == "notifyOnAdd" ||
                    funcName == "notifyOnRender") {
                    return { type: "skip" };
                }

                // removeFixedUpdate(callback) -> set _fixed_update_enabled = false
                if (funcName == "removeFixedUpdate") {
                    meta.has_remove_fixed_update = true;
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "remove_fixed_update", value: callbackName };
                }

                // removeUpdate(callback) -> set _update_enabled = false
                // On N64, we only have one update per trait, so we just disable it
                // The callback parameter is for Haxe compatibility
                if (funcName == "removeUpdate") {
                    meta.has_remove_update = true;
                    // Extract callback name for documentation/debugging (optional)
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "remove_update", value: callbackName };
                }

                // removeLateUpdate(callback) -> set _late_update_enabled = false
                if (funcName == "removeLateUpdate") {
                    meta.has_remove_late_update = true;
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "remove_late_update", value: callbackName };
                }

                // removeRender2D(callback) -> set _render2d_enabled = false
                if (funcName == "removeRender2D") {
                    meta.has_remove_render2d = true;
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "remove_render2d", value: callbackName };
                }

                // notifyOnUpdate(callback) outside constructor -> re-enable updates
                // In constructor it's handled by scanForLifecycles, but runtime calls enable updates
                if (funcName == "notifyOnUpdate") {
                    // Always enable the toggle mechanism when runtime notifyOnUpdate is used
                    meta.has_remove_update = true;
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "notify_update", value: callbackName };
                }

                // notifyOnRender2D(callback) outside init -> re-enable render2D
                if (funcName == "notifyOnRender2D") {
                    // Always enable the toggle mechanism when runtime notifyOnRender2D is used
                    meta.has_remove_render2d = true;
                    var callbackName:String = null;
                    if (params.length > 0) {
                        callbackName = extractStringArg(params[0]);
                    }
                    return { type: "notify_render2d", value: callbackName };
                }

                // trace() -> debugf() for N64 debug output
                if (funcName == "trace") {
                    return { type: "debug_call", args: args };
                }

                // Check if this is a call to a local method - emit as C function call
                if (methodMap.exists(funcName)) {
                    var method = methodMap.get(funcName);
                    if (method != null && method.expr != null) {
                        // Generate C function name: arm_<traitname>_<methodname>
                        var methodCName = "arm_" + cName.substring(4) + "_" + funcName.toLowerCase();
                        // Use extractCallbackArgs to properly handle lambda parameters
                        var processedArgs = extractCallbackArgs(params, funcName);
                        return {
                            type: "trait_method_call",
                            cName: methodCName,
                            method: funcName,
                            trait: className,
                            args: processedArgs
                        };
                    }
                }

                // Check if this is a call to a function-type parameter (callback invocation)
                // e.g., finishedCallback() where finishedCallback: Void->Void
                var localType = localVarTypes.get(funcName);
                if (localType != null && (localType.indexOf("->") >= 0 || localType == "Void->Void")) {
                    // This is a callback parameter being invoked
                    return {
                        type: "callback_param_call",
                        name: funcName,
                        paramType: localType,
                        args: args
                    };
                }

                // If method not found locally but we have a parent, assume it's inherited
                // The Python emitter will check if the method exists in parent chain
                if (parentName != null) {
                    // Extract callbacks from raw params - function args become callback wrappers
                    var processedArgs = extractCallbackArgs(params, funcName);
                    return {
                        type: "inherited_method_call",
                        parent: parentName,
                        method: funcName,
                        args: processedArgs
                    };
                }

                return { type: "call", method: funcName, args: args };

            default:
                return { type: "skip" };
        }
    }

    // =========================================================================
    // New expression conversion - handles constructor calls
    // =========================================================================

    /**
     * Counter for generating unique callback names for inherited method callbacks
     */
    static var inheritedCallbackCounter:Int = 0;

    /**
     * Extract callback arguments from raw params for inherited method calls.
     * Function arguments are converted to callback wrapper structures.
     * Non-function arguments are converted via exprToIR as usual.
     */
    function extractCallbackArgs(params:Array<Expr>, methodName:String):Array<IRNode> {
        var result:Array<IRNode> = [];

        for (i in 0...params.length) {
            var param = params[i];
            switch (param.expr) {
                case EFunction(_, func):
                    // Anonymous function - extract as callback wrapper
                    var callback = extractInheritedCallback(func, methodName, i);
                    if (callback != null) {
                        result.push(callback);
                    } else {
                        result.push({ type: "skip" });
                    }
                default:
                    // Non-function arg - convert normally
                    result.push(exprToIR(param));
            }
        }

        return result;
    }

    /**
     * Extract an anonymous function as a callback for an inherited method.
     * Returns a callback_wrapper IR node that will be emitted as a C function.
     */
    function extractInheritedCallback(func:Function, methodName:String, argIndex:Int):IRNode {
        if (func == null || func.expr == null) return null;

        // Generate unique callback name
        var callbackName = '${cName}_${methodName}_cb_${inheritedCallbackCounter++}';

        // Get parameter name if any (for callbacks like Float->Void)
        var paramName:String = null;
        var paramType:String = "Void";
        if (func.args != null && func.args.length > 0) {
            paramName = func.args[0].name;
            paramType = func.args[0].type != null ? N64MacroBase.complexTypeToString(func.args[0].type) : "Dynamic";
            // Track the callback parameter as a local variable during body extraction
            localVarTypes.set(paramName, paramType);
        }

        // Convert function body to IR
        var bodyNodes:Array<IRNode> = [];
        switch (func.expr.expr) {
            case EBlock(exprs):
                for (e in exprs) {
                    var node = exprToIR(e);
                    if (node != null && node.type != "skip") {
                        bodyNodes.push(node);
                    }
                }
            default:
                var node = exprToIR(func.expr);
                if (node != null && node.type != "skip") {
                    bodyNodes.push(node);
                }
        }

        // Clean up local variable tracking
        if (paramName != null) {
            localVarTypes.remove(paramName);
        }

        // Analyze captures - variables from outer scope that need to be passed via data
        var captures = analyzeCallbackCaptures(bodyNodes, paramName);

        // Return callback wrapper with all required fields
        // Type as IRNode so serializeIRNode can access all fields
        var cbWrapper:IRNode = {
            type: "callback_wrapper",
            callback_name: callbackName,
            param_name: paramName,
            param_type: paramType,
            param_ctype: TypeMap.getCType(paramType),
            body: bodyNodes,
            captures: captures
        };
        return cbWrapper;
    }

    /**
     * Analyze IR nodes to find captured variables (members and params from outer scope).
     */
    function analyzeCallbackCaptures(nodes:Array<IRNode>, excludeParam:String):Array<Dynamic> {
        var captures:Map<String, Dynamic> = new Map();
        for (node in nodes) {
            findCallbackCaptures(node, excludeParam, captures);
        }
        return Lambda.array(captures);
    }

    function findCallbackCaptures(node:IRNode, excludeParam:String, captures:Map<String, Dynamic>):Void {
        if (node == null) return;

        switch (node.type) {
            case "ident":
                var name = Std.string(node.value);
                if (name != excludeParam && name != "null" && name != "true" && name != "false" && name != "object" && name != "dt") {
                    // First check if it's a class member
                    var memberType = memberTypes.get(name);
                    if (memberType != null && !captures.exists(name)) {
                        captures.set(name, {
                            name: name,
                            type: memberType,
                            ctype: TypeMap.getCType(memberType),
                            is_member: true
                        });
                    } else if (!captures.exists(name)) {
                        // Check if it's a local variable (including method parameters)
                        var localType = localVarTypes.get(name);
                        if (localType != null) {
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
            case "member":
                var name = Std.string(node.value);
                if (!captures.exists(name)) {
                    var memberType = memberTypes.get(name);
                    captures.set(name, {
                        name: name,
                        type: memberType != null ? memberType : "Dynamic",
                        ctype: TypeMap.getCType(memberType != null ? memberType : "Dynamic"),
                        is_member: true
                    });
                }
            case "inherited_member":
                var name = Std.string(node.value);
                if (!captures.exists(name)) {
                    var memberType = Std.string(node.memberType);
                    captures.set(name, {
                        name: name,
                        type: memberType,
                        ctype: TypeMap.getCType(memberType),
                        is_inherited: true,
                        owner: node.owner
                    });
                }
            default:
                // Recurse into children and args
                if (node.children != null) {
                    for (child in node.children) {
                        findCallbackCaptures(child, excludeParam, captures);
                    }
                }
                if (node.args != null) {
                    for (arg in node.args) {
                        findCallbackCaptures(arg, excludeParam, captures);
                    }
                }
        }
    }

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
