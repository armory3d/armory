package armory.n64;

/**
 * IR Types for N64 Trait/Autoload Macros
 *
 * These types define the intermediate representation (IR) format
 * that the macros emit and Python consumes.
 *
 * IR Node Types Reference:
 * ========================
 *
 * LITERALS:
 *   int, float, string, bool, null   - TraitMacro direct types
 *   literal                          - AutoloadMacro uses props.literal_type
 *   skip                             - No-op, filtered out
 *   c_literal                        - Raw C code passthrough
 *
 * VARIABLES:
 *   member                           - Trait data member: data->name
 *   ident                            - Identifier: local var, dt, object, this
 *   field_access                     - Field access: object.field, vec.x, this.field
 *   autoload_field                   - Access to another autoload's member
 *   autoload_trait_object            - Get object pointer from autoload trait member
 *
 * OPERATORS:
 *   assign                           - Assignment: target = value
 *   binop                            - Binary operator: a + b
 *   unop                             - Unary operator: !a, -a, ++a
 *
 * CONTROL FLOW:
 *   if                               - Conditional: if/else
 *   block                            - Code block { ... }
 *   var, var_decl                    - Local variable declaration
 *   return                           - Return statement
 *   while, do_while                  - Loop constructs
 *   for_range                        - For loop with range
 *   break, continue                  - Loop control
 *   ternary                          - Ternary operator a ? b : c
 *   paren                            - Parenthesized expression
 *
 * CALLS:
 *   call, method_call                - Generic function/method calls
 *   scene_call, transform_call       - Domain-specific calls
 *   math_call, input_call            - Domain-specific calls
 *   physics_call, vec_call           - Domain-specific calls
 *   signal_call, global_signal_call  - Signal system calls
 *   canvas_get_label, label_set_text - UI calls
 *   autoload_call                    - Call to autoload function
 *   object_call                      - Object method call
 *   cast_call                        - Type cast
 *   debug_call                       - trace() -> debugf()
 *   sprintf                          - String formatting
 *   remove_object                    - Object removal
 *
 * AUDIO:
 *   audio_play, audio_mix_*          - Audio playback calls
 *   audio_handle_*                   - Audio handle operations
 *
 * CONSTRUCTORS:
 *   new, new_vec                     - Object/vector creation
 */

typedef IRNode = {
    type: String,
    ?value: Dynamic,
    ?children: Array<IRNode>,
    ?args: Array<IRNode>,
    ?method: String,
    ?object: IRNode,
    ?props: Dynamic,
    ?c_code: String,
    ?c_func: String,   // Direct C function name for 1:1 translation
    ?cName: String,    // C function name for trait_method_call
    ?trait: String,    // Trait name for trait_method_call
    ?parent: String,   // Parent trait name for inherited_method_call
    ?warn: String,     // Warning message to emit as C comment (for skip nodes)
    // Inherited member fields
    ?memberType: String,  // Haxe type of inherited member
    ?owner: String,       // Parent trait that owns this member
    // Callback parameter call fields
    ?name: String,        // Name of callback parameter
    ?paramType: String,   // Type of callback parameter (e.g., "Void->Void")
    // Callback wrapper fields (for inherited method callbacks)
    ?callback_name: String,  // Generated C function name for callback
    ?body: Array<IRNode>,    // Callback body IR nodes
    ?captures: Array<Dynamic>,  // Captured variables
    ?param_name: String,     // Parameter name in callback
    ?param_type: String,     // Haxe type of callback parameter
    ?param_ctype: String     // C type of callback parameter
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

/**
 * Method parameter definition for callable methods.
 */
typedef MethodParamIR = {
    name: String,            // Parameter name
    haxeType: String,        // Haxe type (Int, Float, SceneId, etc.)
    ctype: String            // C type (int32_t, float, SceneId, etc.)
}

/**
 * Method definition for callable trait methods.
 * All non-lifecycle methods are generated as callable C functions.
 */
typedef MethodIR = {
    name: String,            // Method name, e.g., "init", "loadScene"
    cName: String,           // Full C function name, e.g., "arm_gamescene_init"
    params: Array<MethodParamIR>,  // Parameters (not including obj/data which are implicit)
    returnType: String,      // C return type ("void", "int32_t", etc.)
    body: Array<IRNode>,     // Method body as IR nodes
    ?isVirtual: Bool         // True if method is public (can be overridden by children)
}

typedef TraitMeta = {
    uses_input: Bool,
    uses_transform: Bool,
    mutates_transform: Bool,   // True if trait modifies transform (translate, rotate, etc.)
    uses_time: Bool,
    uses_physics: Bool,
    uses_ui: Bool,             // True if trait uses UI labels (canvas.getElementAs, label.text)
    uses_tween: Bool,          // True if trait uses Tween (tween.float, tween.delay, etc.)
    uses_autoload: Bool,       // True if trait accesses autoload fields/methods
    buttons_used: Array<String>,
    button_events: Array<ButtonEventMeta>,  // structured button event info
    contact_events: Array<ContactEventMeta>, // physics contact subscriptions
    signals: Array<SignalMeta>, // per-instance signal declarations
    signal_handlers: Array<SignalHandlerMeta>, // functions used as signal callbacks
    global_signals: Array<String>, // global signals used (e.g., "g_gameevents_gemCollected")
    has_remove_update: Bool,       // True if trait calls removeUpdate() - adds _update_enabled guard
    has_remove_late_update: Bool,  // True if trait calls removeLateUpdate()
    has_remove_render2d: Bool,     // True if trait calls removeRender2D() - adds _render2d_enabled guard
    ?dynamic_updates: Array<String> // Names of dynamically registered update functions (e.g., ["update", "winUpdate"])
}

/**
 * Super call metadata - tracks super() and super.method() calls for inheritance.
 */
typedef SuperCallMeta = {
    type: String,            // "super_new" for super() or "super_method" for super.method()
    method: String,          // Method name (empty for super_new)
    args: Array<IRNode>      // Arguments to pass
}

typedef TraitIR = {
    name: String,
    module: String,
    cName: String,
    needsData: Bool,
    ?parent: String,         // Parent trait name (null if none or base Trait class)
    members: Map<String, MemberIR>,
    methods: Map<String, MethodIR>,  // All callable methods (non-lifecycle)
    events: Map<String, Array<IRNode>>,  // Lifecycle events (on_ready, on_update, etc.)
    meta: TraitMeta
}

// ============================================================================
// Autoload IR Types
// ============================================================================

typedef AutoloadFunctionIR = {
    name: String,            // Haxe function name, e.g., "doSomething"
    cName: String,           // C function name, e.g., "myautoload_doSomething"
    returnType: String,      // C return type, e.g., "float" or "void"
    params: Array<AutoloadParamIR>,  // Function parameters
    body: Array<IRNode>,     // Function body as IR nodes
    isPublic: Bool           // Whether function is public (exported) or private (internal)
}

typedef AutoloadParamIR = {
    name: String,            // Parameter name
    haxeType: String,        // Haxe type
    ctype: String            // C type
}

typedef AutoloadMeta = {
    order: Int,              // Initialization order (lower = earlier)
    signals: Array<SignalMeta>,           // Static signal declarations
    signal_handlers: Array<SignalHandlerMeta>, // Functions used as signal callbacks
    global_signals: Array<String>         // Global signals used by this autoload
}

typedef AutoloadIR = {
    name: String,            // Class name, e.g., "GameEvents"
    module: String,          // Full module path, e.g., "arm.autoload.GameEvents"
    cName: String,           // C-safe prefix, e.g., "gameevents"
    order: Int,              // Initialization order
    members: Map<String, MemberIR>,       // Static members (non-Signal)
    functions: Map<String, AutoloadFunctionIR>,  // Static functions
    hasInit: Bool,           // Whether class has init() function
    meta: AutoloadMeta
}
