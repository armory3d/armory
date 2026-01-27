package armory.n64;

/**
 * IR Types for N64 Trait Macro
 *
 * These types define the intermediate representation (IR) format
 * that the macro emits and Python consumes.
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
    uses_ui: Bool,             // True if trait uses UI labels (canvas.getElementAs, label.text)
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
