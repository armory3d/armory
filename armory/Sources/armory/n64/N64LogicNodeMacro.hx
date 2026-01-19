package armory.n64;

#if macro
import haxe.macro.Expr;
import armory.n64.N64TraitMacro.IRNode;
import armory.n64.N64TraitMacro.TraitMeta;
import armory.n64.N64TraitMacro.TraitIR;

using haxe.macro.ExprTools;
using StringTools;
using Lambda;

/**
 * N64 Logic Node Macro - Interprets Armory logic node graphs at compile time
 *
 * This macro interprets visual logic node graphs and converts them to the same
 * IR format as regular Haxe traits, so Python codegen handles them identically.
 *
 * Pipeline: Logic Node Graph → AST parsing → IR (JSON) → Python → C code
 */

// ============================================================================
// Types
// ============================================================================

typedef LogicNode = {
    name: String,
    type: String,
    props: Map<String, Dynamic>,
    inputs: Array<{socket: Int, sourceNode: String, sourceSocket: Int}>,
    outputs: Array<{socket: Int, targetNode: String, targetSocket: Int}>
}

// ============================================================================
// Logic Node Interpreter - Parses and interprets logic node graphs
// ============================================================================

class LogicNodeInterpreter {
    var className:String;
    var modulePath:String;
    var fields:Array<Field>;
    var cName:String;
    var events:Map<String, Array<IRNode>>;
    var meta:TraitMeta;

    // Node graph state
    var nodes:Map<String, LogicNode>;

    // Node converters
    var converter:LogicNodeConverter;

    // Counter for generating unique inline node names
    var inlineNodeCounter:Int;

    public function new(className:String, modulePath:String, fields:Array<Field>) {
        this.className = className;
        this.modulePath = modulePath;
        this.fields = fields;

        // Generate C-safe name
        var moduleParts = modulePath.split(".");
        var lastModulePart = moduleParts[moduleParts.length - 1];
        if (lastModulePart.toLowerCase() == className.toLowerCase()) {
            this.cName = modulePath.replace(".", "_").toLowerCase();
        } else {
            this.cName = (modulePath.replace(".", "_") + "_" + className).toLowerCase();
        }

        this.events = new Map();
        this.nodes = new Map();
        this.inlineNodeCounter = 0;
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

        this.converter = new LogicNodeConverter(this);
    }

    public function interpret():TraitIR {
        // Parse the logic node graph from add() function
        parseNodeGraph();

        // Find entry point nodes (lifecycle nodes) and simulate execution
        for (nodeName in nodes.keys()) {
            var node = nodes.get(nodeName);
            if (isLifecycleNode(node)) {
                executeLifecycleNode(node);
            }
        }

        return {
            name: className,
            module: modulePath,
            cName: cName,
            needsData: false,
            members: new Map(),
            events: events,
            meta: meta
        };
    }

    function parseNodeGraph():Void {
        for (field in fields) {
            switch (field.kind) {
                case FFun(func):
                    if (field.name == "add" && func.expr != null) {
                        parseAddFunction(func.expr);
                    }
                default:
            }
        }
    }

    function parseAddFunction(expr:Expr):Void {
        if (expr == null) return;

        switch (expr.expr) {
            case EBlock(exprs):
                for (e in exprs) parseAddFunction(e);

            case EVars(vars):
                for (v in vars) {
                    if (v.expr != null) {
                        switch (v.expr.expr) {
                            case ENew(tp, params):
                                var nodeType = tp.name;
                                nodes.set(v.name, {
                                    name: v.name,
                                    type: nodeType,
                                    props: new Map(),
                                    inputs: [],
                                    outputs: []
                                });
                            default:
                        }
                    }
                }

            case EBinop(OpAssign, left, right):
                parsePropertyAssignment(left, right);

            case ECall(callExpr, params):
                parseLinkCreation(callExpr, params);
                for (p in params) parseAddFunction(p);

            default:
                expr.iter(function(sub) parseAddFunction(sub));
        }
    }

    function parsePropertyAssignment(left:Expr, right:Expr):Void {
        switch (left.expr) {
            case EField(obj, fieldName):
                switch (obj.expr) {
                    case EConst(CIdent(nodeName)):
                        if (nodes.exists(nodeName)) {
                            var node = nodes.get(nodeName);
                            node.props.set(fieldName, exprToValue(right));
                        }
                    default:
                }
            default:
        }
    }

    function parseLinkCreation(callExpr:Expr, params:Array<Expr>):Void {
        var funcName = switch (callExpr.expr) {
            case EField(_, field): field;
            default: null;
        };

        if (funcName == "addLink" && params.length >= 4) {
            var fromName = extractOrCreateNode(params[0]);
            var toName = extractOrCreateNode(params[1]);
            var fromIdx = extractInt(params[2]);
            var toIdx = extractInt(params[3]);

            if (fromName != "" && toName != "" && nodes.exists(fromName) && nodes.exists(toName)) {
                var fromNode = nodes.get(fromName);
                var toNode = nodes.get(toName);

                fromNode.outputs.push({socket: fromIdx, targetNode: toName, targetSocket: toIdx});
                toNode.inputs.push({socket: toIdx, sourceNode: fromName, sourceSocket: fromIdx});
            }
        }
    }

    /**
     * Extract node name from expression, or create an inline node if it's a `new` expression.
     * Handles cases like: addLink(new armory.logicnode.FloatNode(this, 10.0), _Vector, 0, 2)
     */
    function extractOrCreateNode(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, fieldName): fieldName;
            case ENew(tp, params):
                // Inline node creation - extract type and constructor params
                var nodeType = tp.name;
                var uniqueName = "__inline_" + nodeType + "_" + (inlineNodeCounter++);

                var props = new Map<String, Dynamic>();

                // Constructor params after 'this' are property values
                // e.g., FloatNode(this, 10.0) -> property0 = 10.0
                //       VectorNode(this, 1.0, 2.0, 3.0) -> property0=1.0, property1=2.0, property2=3.0
                if (params.length > 1) {
                    for (i in 1...params.length) {
                        props.set("property" + (i - 1), exprToValue(params[i]));
                    }
                }

                nodes.set(uniqueName, {
                    name: uniqueName,
                    type: nodeType,
                    props: props,
                    inputs: [],
                    outputs: []
                });

                uniqueName;
            default: "";
        };
    }

    function isLifecycleNode(node:LogicNode):Bool {
        return node.type == "OnUpdateNode" ||
               node.type == "OnInitNode" ||
               node.type == "OnRemoveNode";
    }

    function executeLifecycleNode(node:LogicNode):Void {
        var eventName = switch (node.type) {
            case "OnUpdateNode":
                var updateType = node.props.get("property0");
                if (updateType == "Late Update") "on_late_update";
                else if (updateType == "Physics Pre-Update") "on_fixed_update";
                else "on_update";
            case "OnInitNode": "on_ready";
            case "OnRemoveNode": "on_remove";
            default: null;
        };

        if (eventName == null) return;

        if (!events.exists(eventName)) {
            events.set(eventName, []);
        }

        for (output in node.outputs) {
            if (output.socket == 0) {
                executeNodeChain(output.targetNode, events.get(eventName));
            }
        }
    }

    public function executeNodeChain(nodeName:String, statements:Array<IRNode>):Void {
        if (!nodes.exists(nodeName)) return;

        var node = nodes.get(nodeName);
        var irNode = converter.convert(node, statements);

        if (irNode != null && irNode.type != "skip") {
            statements.push(irNode);
        }

        // Follow execution outputs (socket 0 for most action nodes)
        // Skip for branching nodes that handle their own flow
        if (node.type != "BranchNode" && node.type != "IsTrueNode") {
            for (output in node.outputs) {
                if (output.socket == 0) {
                    executeNodeChain(output.targetNode, statements);
                }
            }
        }
    }

    // ========================================================================
    // Input Value Resolution
    // ========================================================================

    public function getInputValue(node:LogicNode, socketIndex:Int):IRNode {
        for (input in node.inputs) {
            if (input.socket == socketIndex) {
                var sourceNode = nodes.get(input.sourceNode);
                if (sourceNode != null) {
                    return converter.evaluateValue(sourceNode, input.sourceSocket);
                }
            }
        }
        // No connection - return a proper default (0.0f for floats, 0 for ints)
        return { type: "float", value: 0.0 };
    }

    // Returns null if no connection exists (for optional inputs)
    public function getInputValueOrNull(node:LogicNode, socketIndex:Int):Null<IRNode> {
        for (input in node.inputs) {
            if (input.socket == socketIndex) {
                var sourceNode = nodes.get(input.sourceNode);
                if (sourceNode != null) {
                    return converter.evaluateValue(sourceNode, input.sourceSocket);
                }
            }
        }
        return null;
    }

    public function getNode(name:String):LogicNode {
        return nodes.get(name);
    }

    public function getMeta():TraitMeta {
        return meta;
    }

    // ========================================================================
    // AST Helpers
    // ========================================================================

    function extractNodeName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, fieldName): fieldName;
            default: "";
        };
    }

    function extractInt(e:Expr):Int {
        return switch (e.expr) {
            case EConst(CInt(v)): Std.parseInt(v);
            default: 0;
        };
    }

    function exprToValue(e:Expr):Dynamic {
        if (e == null) return null;
        return switch (e.expr) {
            case EConst(CInt(v)): Std.parseInt(v);
            case EConst(CFloat(v)): Std.parseFloat(v);
            case EConst(CString(s)): s;
            case EConst(CIdent("true")): true;
            case EConst(CIdent("false")): false;
            case EArrayDecl(values): [for (v in values) exprToValue(v)];
            default: ExprTools.toString(e);
        };
    }
}

// ============================================================================
// Logic Node Converter - Converts individual logic nodes to IR
// ============================================================================

class LogicNodeConverter {
    var interpreter:LogicNodeInterpreter;

    public function new(interpreter:LogicNodeInterpreter) {
        this.interpreter = interpreter;
    }

    // ========================================================================
    // Main Conversion Entry Point
    // ========================================================================

    public function convert(node:LogicNode, statements:Array<IRNode>):IRNode {
        return switch (node.type) {
            // === Output/Debug ===
            case "PrintNode": convertPrint(node);

            // === Control Flow ===
            case "BranchNode": convertBranch(node, statements);
            case "IsTrueNode": convertIsTrue(node, statements);
            case "GateNode": convertGate(node);

            // === Variables ===
            case "SetVariableNode": convertSetVariable(node);
            case "SetPropertyNode": convertSetProperty(node);
            case "CallFunctionNode": convertCallFunction(node);

            // === Physics ===
            case "ApplyForceNode": convertApplyForce(node);
            case "ApplyImpulseNode": convertApplyImpulse(node);

            // === Transform ===
            case "TranslateObjectNode": convertTranslate(node);
            case "RotateObjectNode": convertRotate(node);
            case "SetLocationNode": convertSetLocation(node);
            case "SetRotationNode": convertSetRotation(node);

            // === Sink nodes (not actions, just graph endpoints) ===
            case "NullNode": { type: "skip" };

            default:
                trace('[N64] Unsupported logic node type: ${node.type}');
                { type: "skip" };
        };
    }

    // ========================================================================
    // Value Node Evaluation
    // ========================================================================

    public function evaluateValue(node:LogicNode, socketIndex:Int):IRNode {
        return switch (node.type) {
            // === Constants (with optional input override) ===
            case "IntegerNode":
                // IntegerNode: if has input, use it; otherwise use property
                var inputVal = interpreter.getInputValueOrNull(node, 0);
                if (inputVal != null) {
                    inputVal;
                } else {
                    var val = node.props.get("property0");
                    { type: "int", value: val != null ? Std.parseInt(Std.string(val)) : 0 };
                }
            case "FloatNode":
                // FloatNode: if has input, use it; otherwise use property
                var inputVal = interpreter.getInputValueOrNull(node, 0);
                if (inputVal != null) {
                    inputVal;
                } else {
                    var val = node.props.get("property0");
                    { type: "float", value: val != null ? Std.parseFloat(Std.string(val)) : 0.0 };
                }
            case "BooleanNode":
                // BooleanNode: if has input, use it; otherwise use property
                var inputVal = interpreter.getInputValueOrNull(node, 0);
                if (inputVal != null) {
                    inputVal;
                } else {
                    { type: "bool", value: node.props.get("property0") == true };
                }
            case "StringNode":
                // StringNode: if has input, use it; otherwise use property
                var inputVal = interpreter.getInputValueOrNull(node, 0);
                if (inputVal != null) {
                    inputVal;
                } else {
                    var val = node.props.get("property0");
                    { type: "string", value: val != null ? Std.string(val) : "" };
                }
            case "VectorNode":
                // VectorNode can have both properties AND input connections
                // Input connections override properties
                // Check for input connections first (they override properties)
                var xInput = interpreter.getInputValueOrNull(node, 0);
                var yInput = interpreter.getInputValueOrNull(node, 1);
                var zInput = interpreter.getInputValueOrNull(node, 2);

                // Fall back to properties if no input connection
                if (xInput == null) {
                    var xVal = node.props.get("property0");
                    var x = xVal != null ? Std.parseFloat(Std.string(xVal)) : 0.0;
                    if (Math.isNaN(x)) x = 0.0;
                    xInput = { type: "float", value: x };
                }
                if (yInput == null) {
                    var yVal = node.props.get("property1");
                    var y = yVal != null ? Std.parseFloat(Std.string(yVal)) : 0.0;
                    if (Math.isNaN(y)) y = 0.0;
                    yInput = { type: "float", value: y };
                }
                if (zInput == null) {
                    var zVal = node.props.get("property2");
                    var z = zVal != null ? Std.parseFloat(Std.string(zVal)) : 0.0;
                    if (Math.isNaN(z)) z = 0.0;
                    zInput = { type: "float", value: z };
                }

                // Output Blender coordinates - swizzle happens at consumption (physics_call, transform_call)
                { type: "new_vec", c_code: "(ArmVec3){{0}, {1}, {2}}", args: [xInput, yInput, zInput] };

            // === Object References ===
            // Use { type: "ident", value: "object" } to match TraitExtractor output
            case "SelfNode", "GetObjectNode":
                { type: "ident", value: "object" };
            case "ObjectNode":
                // ObjectNode with empty string means "self", otherwise it's a named object lookup
                var objectName = node.props.get("property0");
                if (objectName == null || objectName == "") {
                    { type: "ident", value: "object" };
                } else {
                    // TODO: Named object lookup - for now just use self
                    { type: "ident", value: "object" };
                };
            case "NullNode":
                // NullNode is used as a sink - just return skip
                { type: "skip" };

            // === Transform Getters ===
            case "GetLocationNode":
                var objInput = interpreter.getInputValue(node, 0);
                interpreter.getMeta().uses_transform = true;
                { type: "field", object: objInput, value: "pos" };
            case "GetRotationNode":
                var objInput = interpreter.getInputValue(node, 0);
                interpreter.getMeta().uses_transform = true;
                { type: "field", object: objInput, value: "rot" };

            // === Vector Decomposition/Composition ===
            case "SeparateXYZNode", "SeparateVectorNode":
                var vecInput = interpreter.getInputValue(node, 0);
                // Returns the component based on which output socket is requested
                switch (socketIndex) {
                    case 0: { type: "field", object: vecInput, value: "x" };
                    case 1: { type: "field", object: vecInput, value: "y" };
                    case 2: { type: "field", object: vecInput, value: "z" };
                    default: { type: "field", object: vecInput, value: "x" };
                };
            case "CombineXYZNode", "CombineVectorNode":
                var xInput = interpreter.getInputValue(node, 0);
                var yInput = interpreter.getInputValue(node, 1);
                var zInput = interpreter.getInputValue(node, 2);
                // Output Blender coordinates - swizzle happens at consumption
                // Use single { for C compound literal - Python replaces {0}, {1}, {2} with args
                { type: "new_vec", c_code: "(ArmVec3){{0}, {1}, {2}}", args: [xInput, yInput, zInput] };

            // === Math Operations ===
            case "MathNode":
                var value1 = interpreter.getInputValue(node, 0);
                var value2 = interpreter.getInputValue(node, 1);
                var op = switch (Std.string(node.props.get("property0"))) {
                    case "Add": "+";
                    case "Subtract": "-";
                    case "Multiply": "*";
                    case "Divide": "/";
                    default: "+";
                };
                { type: "binop", value: op, children: [value1, value2] };

            case "VectorMathNode":
                // Use vec_call IR type matching TraitExtractor.convertVecCall()
                var vec1 = interpreter.getInputValue(node, 0);
                var vec2 = interpreter.getInputValueOrNull(node, 1);
                var operation = Std.string(node.props.get("property0"));
                var separatorOut = node.props.get("property1") == true;

                // VectorMathNode has multiple outputs:
                // socket 0: vector result
                // socket 1: if separatorOut, x component; else scalar result (Length, Distance, etc.)
                // socket 2: if separatorOut, y component; else scalar result
                // socket 3: if separatorOut, z component; else scalar result
                // socket 4: if separatorOut, scalar result

                // For scalar-returning operations (Length, Distance), socket 1+ returns the scalar
                var isScalarOp = (operation == "Length" || operation == "Distance" || operation == "Dot Product");

                if (socketIndex == 0) {
                    // Return vector result
                    var result:IRNode = switch (operation) {
                        case "Add":
                            { type: "vec_call", c_code: "(ArmVec3){{v}.x+({0}).x, {v}.y+({0}).y, {v}.z+({0}).z}", object: vec1, args: vec2 != null ? [vec2] : [] };
                        case "Subtract":
                            { type: "vec_call", c_code: "(ArmVec3){{v}.x-({0}).x, {v}.y-({0}).y, {v}.z-({0}).z}", object: vec1, args: vec2 != null ? [vec2] : [] };
                        case "Multiply":
                            { type: "vec_call", c_code: "(ArmVec3){{v}.x*({0}).x, {v}.y*({0}).y, {v}.z*({0}).z}", object: vec1, args: vec2 != null ? [vec2] : [] };
                        case "Divide":
                            { type: "vec_call", c_code: "(ArmVec3){{v}.x/({0}).x, {v}.y/({0}).y, {v}.z/({0}).z}", object: vec1, args: vec2 != null ? [vec2] : [] };
                        case "Normalize":
                            { type: "vec_call", c_code: "{ float _l=sqrtf({v}.x*{v}.x+{v}.y*{v}.y+{v}.z*{v}.z); if(_l>0.0f){ {vraw}.x/=_l; {vraw}.y/=_l; {vraw}.z/=_l; } }", object: vec1, args: [] };
                        case "Length":
                            // For socket 0 on Length, just return the input vector
                            vec1;
                        case "Cross Product":
                            { type: "vec_call", c_code: "(ArmVec3){{v}.y*({0}).z - {v}.z*({0}).y, {v}.z*({0}).x - {v}.x*({0}).z, {v}.x*({0}).y - {v}.y*({0}).x}", object: vec1, args: vec2 != null ? [vec2] : [] };
                        default:
                            vec1;
                    };
                    result;
                } else if (isScalarOp && !separatorOut) {
                    // Return scalar result for Length, Distance, Dot Product
                    switch (operation) {
                        case "Length":
                            { type: "vec_call", c_code: "sqrtf({v}.x*{v}.x + {v}.y*{v}.y + {v}.z*{v}.z)", object: vec1, args: [] };
                        case "Distance":
                            { type: "vec_call", c_code: "sqrtf(({v}.x-({0}).x)*({v}.x-({0}).x) + ({v}.y-({0}).y)*({v}.y-({0}).y) + ({v}.z-({0}).z)*({v}.z-({0}).z))", object: vec1, args: vec2 != null ? [vec2] : [] };
                        case "Dot Product":
                            { type: "vec_call", c_code: "({v}.x*({0}).x + {v}.y*({0}).y + {v}.z*({0}).z)", object: vec1, args: vec2 != null ? [vec2] : [] };
                        default:
                            { type: "float", value: 0.0 };
                    };
                } else if (separatorOut) {
                    // Return vector component
                    switch (socketIndex) {
                        case 1: { type: "field", object: vec1, value: "x" };
                        case 2: { type: "field", object: vec1, value: "y" };
                        case 3: { type: "field", object: vec1, value: "z" };
                        default: { type: "float", value: 0.0 };
                    };
                } else {
                    { type: "float", value: 0.0 };
                }

            // === Comparisons ===
            case "GateNode":
                convertGate(node);
            case "CompareNode":
                var value1 = interpreter.getInputValue(node, 0);
                var value2 = interpreter.getInputValue(node, 1);
                var op = switch (Std.string(node.props.get("property0"))) {
                    case "Equal": "==";
                    case "Not Equal": "!=";
                    case "Greater": ">";
                    case "Greater Equal": ">=";
                    case "Less": "<";
                    case "Less Equal": "<=";
                    default: "==";
                };
                { type: "binop", value: op, children: [value1, value2] };

            // === Input ===
            case "GamepadCoordsNode":
                interpreter.getMeta().uses_input = true;
                // N64 only has one analog stick - map left stick outputs to it
                // GamepadCoordsNode outputs:
                // 0 = left stick (Vec4 with x,y)
                // 1 = right stick (Vec4 with x,y)
                // 2 = left stick movement
                // 3 = right stick movement
                // 4 = L2 trigger (float)
                // 5 = R2 trigger (float)
                // Return ArmVec3 with z=0 for compatibility with VectorMathNode operations
                switch (socketIndex) {
                    case 0, 1, 2, 3:
                        // All stick outputs map to the N64 analog stick
                        // Use ArmVec3 for compatibility with 3D vector math operations
                        { type: "c_literal", c_code: "(ArmVec3){input_stick_x(), input_stick_y(), 0.0f}" };
                    case 4:
                        // L2 trigger - map to Z button on N64
                        { type: "c_literal", c_code: "(input_down(N64_BTN_Z) ? 1.0f : 0.0f)" };
                    case 5:
                        // R2 trigger - map to Z button on N64 (only one trigger)
                        { type: "c_literal", c_code: "(input_down(N64_BTN_Z) ? 1.0f : 0.0f)" };
                    default:
                        { type: "c_literal", c_code: "(ArmVec3){input_stick_x(), input_stick_y(), 0.0f}" };
                };

            default:
                trace('[N64] Unsupported value node: ${node.type}');
                { type: "float", value: 0.0 };
        };
    }

    // ========================================================================
    // Action Node Converters
    // ========================================================================

    function convertPrint(node:LogicNode):IRNode {
        var valueInput = interpreter.getInputValue(node, 1);
        return {
            type: "debug_call",
            args: [valueInput]
        };
    }

    function convertSetVariable(node:LogicNode):IRNode {
        // TODO: Implement variable assignment
        return { type: "skip" };
    }

    function convertSetProperty(node:LogicNode):IRNode {
        // TODO: Implement property setter
        return { type: "skip" };
    }

    function convertCallFunction(node:LogicNode):IRNode {
        // TODO: Implement function call
        return { type: "skip" };
    }

    // ========================================================================
    // Control Flow Converters
    // ========================================================================

    function convertBranch(node:LogicNode, parentStatements:Array<IRNode>):IRNode {
        var condition = interpreter.getInputValue(node, 1);

        var thenStatements:Array<IRNode> = [];
        var elseStatements:Array<IRNode> = [];

        for (output in node.outputs) {
            if (output.socket == 0) {
                interpreter.executeNodeChain(output.targetNode, thenStatements);
            } else if (output.socket == 1) {
                interpreter.executeNodeChain(output.targetNode, elseStatements);
            }
        }

        return {
            type: "if",
            children: [condition],
            props: {
                then: thenStatements,
                else_: elseStatements.length > 0 ? elseStatements : null
            }
        };
    }

    function convertIsTrue(node:LogicNode, statements:Array<IRNode>):IRNode {
        var condition = interpreter.getInputValue(node, 1);

        var thenStatements:Array<IRNode> = [];

        for (output in node.outputs) {
            if (output.socket == 0) {
                interpreter.executeNodeChain(output.targetNode, thenStatements);
            }
        }

        return {
            type: "if",
            children: [condition],
            props: {
                then: thenStatements,
                else_: null
            }
        };
    }

    function convertGate(node:LogicNode):IRNode {
        var value1 = interpreter.getInputValue(node, 1);
        var value2 = interpreter.getInputValue(node, 2);
        var property0 = node.props.get("property0");

        var op = switch (property0) {
            case "Equal": "==";
            case "Not Equal": "!=";
            case "Greater": ">";
            case "Greater Or Equal": ">=";
            case "Less": "<";
            case "Less Or Equal": "<=";
            default: "==";
        };

        return {
            type: "binop",
            value: op,
            children: [value1, value2]
        };
    }

    // ========================================================================
    // Physics Converters
    // ========================================================================

    function convertApplyForce(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var forceInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_physics = true;

        // Match N64TraitMacro format: coordinate swizzle and rigid_body access
        return {
            type: "physics_call",
            c_code: "{ OimoVec3 _f = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_force({obj}->rigid_body, &_f); }",
            object: objInput,
            args: [forceInput]
        };
    }

    function convertApplyImpulse(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var impulseInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_physics = true;

        // Match N64TraitMacro format: coordinate swizzle and rigid_body access
        return {
            type: "physics_call",
            c_code: "{ OimoVec3 _i = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_impulse({obj}->rigid_body, &_i); }",
            object: objInput,
            args: [impulseInput]
        };
    }

    // ========================================================================
    // Transform Converters
    // ========================================================================

    function convertTranslate(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var vecInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_transform = true;
        interpreter.getMeta().mutates_transform = true;

        return {
            type: "transform_call",
            c_code: "t3d_vec3_add(&{obj}->pos, &{0})",
            object: objInput,
            args: [vecInput]
        };
    }

    function convertRotate(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var vecInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_transform = true;
        interpreter.getMeta().mutates_transform = true;

        return {
            type: "transform_call",
            c_code: "arm_rotate({obj}, {0}.x, {0}.y, {0}.z)",
            object: objInput,
            args: [vecInput]
        };
    }

    function convertSetLocation(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var vecInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_transform = true;
        interpreter.getMeta().mutates_transform = true;

        return {
            type: "transform_call",
            c_code: "{obj}->pos = {0}",
            object: objInput,
            args: [vecInput]
        };
    }

    function convertSetRotation(node:LogicNode):IRNode {
        var objInput = interpreter.getInputValue(node, 1);
        var vecInput = interpreter.getInputValue(node, 2);

        interpreter.getMeta().uses_transform = true;
        interpreter.getMeta().mutates_transform = true;

        return {
            type: "transform_call",
            c_code: "arm_set_rotation({obj}, {0}.x, {0}.y, {0}.z)",
            object: objInput,
            args: [vecInput]
        };
    }
}

#end
