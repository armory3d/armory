package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;

using StringTools;
using Lambda;

/**
 * Converts Haxe expressions to C code strings for N64.
 * Handles API mapping, coordinate conversion (Blender Z-up → N64 Y-up), and feature tracking.
 */
class N64CEmitter {
    // Context for the current trait
    var traitName:String;
    var memberNames:Map<String, Bool>;
    var localVars:Map<String, Bool>;
    var vec4Exprs:Map<String, Expr>;  // Vec4 member init expressions for axis resolution
    var vec2Vars:Map<String, {x:String, y:String}>;  // Vec2 local variables with their x,y expressions
    var chainCounter:Int = 0;  // Counter for unique Vec2 chain temp names
    var needsObj:Bool = false;
    var needsDt:Bool = false;
    var needsMath:Bool = false;  // True if sqrtf is used
    var currentPos:haxe.macro.Expr.Position = null;  // Current expression position for warnings

    // Feature tracking
    var inputButtons:Array<String>;
    var hasTransform:Bool = false;
    var hasScene:Bool = false;
    var targetScene:String = null;
    var needsInitialScale:Bool = false;  // True if trait assigns object.transform.scale

    public function new(traitName:String, members:Array<String>, ?vec4Exprs:Map<String, Expr>) {
        this.traitName = traitName;
        memberNames = new Map();
        localVars = new Map();
        vec2Vars = new Map();
        inputButtons = [];
        this.vec4Exprs = vec4Exprs != null ? vec4Exprs : new Map();
        for (m in members) {
            memberNames.set(m, true);
        }
    }

    public function warn(msg:String):Void {
        if (currentPos != null) {
            Context.warning('N64: $msg', currentPos);
        }
    }

    function error(msg:String):Void {
        if (currentPos != null) {
            Context.error('N64: $msg', currentPos);
        }
    }

    public function emitExpr(expr:Expr):String {
        if (expr == null) return "";

        // Track position for warnings
        var prevPos = currentPos;
        currentPos = expr.pos;

        var result = switch (expr.expr) {
            case EConst(c): emitConst(c);
            case EBinop(op, e1, e2): emitBinop(op, e1, e2);
            case EUnop(op, postFix, e): emitUnop(op, postFix, e);
            case ETernary(econd, eif, eelse): '(${emitExpr(econd)} ? ${emitExpr(eif)} : ${emitExpr(eelse)})';
            case EField(e, field): emitField(e, field);
            case EArray(e1, e2): '${emitExpr(e1)}[${emitExpr(e2)}]';
            case ECall(e, params): emitCall(e, params);
            case ENew(tp, params): emitNew(tp, params);
            case EArrayDecl(values): emitArrayDecl(values);
            case EObjectDecl(fields): emitObjectDecl(fields);
            case EVars(vars): emitVars(vars);
            case EFunction(_, func): emitLocalFunction(func);
            case EBlock(exprs): emitBlock(exprs);
            case EIf(econd, eif, eelse): emitIf(econd, eif, eelse);
            case EWhile(econd, ebody, normalWhile): emitWhile(econd, ebody, normalWhile);
            case EFor(it, body): emitFor(it, body);
            case ESwitch(esw, cases, edef): emitSwitch(esw, cases, edef);
            case ETry(etry, catches): emitTry(etry, catches);
            case EReturn(eret): emitReturn(eret);
            case EBreak: "break";
            case EContinue: "continue";
            case EThrow(eth): emitThrow(eth);
            case ECast(ecast, t): emitCast(ecast, t);
            case ECheckType(ect, t): emitExpr(ect);
            case EIs(eis, t): emitIs(eis, t);
            case EParenthesis(ep): '(${emitExpr(ep)})';
            case EMeta(_, em): emitExpr(em);
            case EUntyped(eu):
                warn("untyped expressions not supported");
                emitExpr(eu);
            case EDisplay(_, _):
                warn("display expressions not supported");
                "";
            case EDisplayNew(_):
                warn("display expressions not supported");
                "";
            default:
                warn("Unsupported expression type");
                "";
        }

        currentPos = prevPos;
        return result;
    }

    function emitConst(c:Constant):String {
        return switch (c) {
            case CInt(v): v;
            case CFloat(f): '${f}f';
            case CString(s): '"$s"';
            case CIdent(s): resolveIdent(s);
            case CRegexp(_, _):
                error("Regular expressions not supported");
                "";
        }
    }

    function resolveIdent(name:String):String {
        // Check if it's a member variable
        if (memberNames.exists(name)) {
            return '((${traitName}Data*)data)->$name';
        }
        // Skip Armory-internal variables that have no N64 equivalent
        if (isSkippedVariable(name)) {
            return "";
        }
        // Input objects (gamepad, keyboard, mouse) - these are always available on N64
        // so null checks like `if (gamepad != null)` should become `if (true)`
        if (isInputVariable(name)) {
            return "true";  // Input is always available on N64
        }
        // Check special identifiers
        return switch (name) {
            case "this": "((ArmObject*)obj)";
            case "object": "((ArmObject*)obj)";
            case "true": "true";
            case "false": "false";
            case "null": "NULL";
            default: name;  // local or param
        }
    }

    function isSkippedVariable(name:String):Bool {
        // Check against config skip list
        if (N64Config.shouldSkipMember(name)) return true;
        return switch (name) {
            case "camera": true;  // Camera casting not supported
            case "msg", "error": true;  // try/catch variables
            default: false;
        };
    }

    function isInputVariable(name:String):Bool {
        return switch (name) {
            case "gamepad", "keyboard", "mouse": true;
            default: false;
        };
    }

    function emitBinop(op:Binop, e1:Expr, e2:Expr):String {
        // Check for transform.scale/loc/rot = new Vec4(...) pattern BEFORE emitExpr
        // because ENew falls through to "unsupported expr"
        if (op == OpAssign) {
            var scaleAssign = tryEmitScaleAssign(e1, e2);
            if (scaleAssign != null) return scaleAssign;
        }

        var left = emitExpr(e1);
        var right = emitExpr(e2);

        // Handle input device null checks: `gamepad != null` -> always true on N64
        if ((op == OpNotEq || op == OpEq) && (right == "NULL" || left == "NULL")) {
            if (left == "true" || right == "true") {
                // Input device compared to null - always available on N64
                return (op == OpNotEq) ? "true" : "false";
            }
        }

        // Simplify input function comparisons with zero
        // N64's input functions return bool, so comparison to 0 is redundant
        var simplified = trySimplifyInputComparison(op, left, right);
        if (simplified != null) return simplified;

        // Skip operations where either side is empty (skipped variable)
        if (left == "" || right == "") {
            return "";
        }

        // Skip assignments where right side is unsupported
        if (op == OpAssign && right == "/* N64_UNSUPPORTED: expr */") {
            return "";
        }

        var opStr = switch (op) {
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
            case OpAnd: "&&";
            case OpOr: "||";
            case OpBoolAnd: "&&";
            case OpBoolOr: "||";
            case OpShl: "<<";
            case OpShr: ">>";
            case OpUShr: ">>";
            case OpXor: "^";
            case OpAssign: "=";
            case OpAssignOp(subOp): emitAssignOp(subOp);
            case OpInterval: "/* interval */";
            case OpArrow: "/* arrow */";
            case OpIn: "/* in */";
        }
        return '$left $opStr $right';
    }

    /** Handle: object.transform.scale = new Vec4(x, y, z) */
    function tryEmitScaleAssign(lhs:Expr, rhs:Expr):Null<String> {
        // LHS must end with .scale, .loc, or .rot on a transform
        var chain = getFieldChain(lhs);
        if (chain.length < 3) return null;

        // Look for ["object"|"this", "transform", "scale"|"loc"|"rot"]
        var lastTwo = [chain[chain.length - 2], chain[chain.length - 1]];
        if (lastTwo[0] != "transform") return null;

        var prop = lastTwo[1];
        if (prop != "scale" && prop != "loc" && prop != "rot") return null;

        // RHS must be new Vec4(...)
        switch (rhs.expr) {
            case ENew(tp, params):
                if (tp.name != "Vec4") return null;

                var x:String, y:String, z:String;
                if (params.length >= 3) {
                    x = emitExpr(params[0]);
                    y = emitExpr(params[1]);
                    z = emitExpr(params[2]);
                } else if (params.length == 2) {
                    // Vec4(x, y) -> (x, y, 0)
                    x = emitExpr(params[0]);
                    y = emitExpr(params[1]);
                    z = "0.0f";
                } else if (params.length == 1) {
                    // Vec4(v) -> (v, v, v)
                    var v = emitExpr(params[0]);
                    x = v; y = v; z = v;
                } else {
                    // Vec4() -> (0, 0, 0)
                    x = "0.0f"; y = "0.0f"; z = "0.0f";
                }

                if (x == "" || y == "" || z == "") return null;

                needsObj = true;
                hasTransform = true;

                var fn = 'it_set_$prop';

                if (prop == "scale") {
                    // Scale values are relative to initial scale (1.0 = original size)
                    // Multiply by _initialScale which is auto-captured in on_ready
                    // Apply coordinate swizzle via N64CoordinateSystem
                    needsInitialScale = true;
                    var data = '((' + traitName + 'Data*)data)';
                    // Scale swizzle: (X,Y,Z) -> (X,Z,Y) applied to initial scale components
                    return '$fn(&((ArmObject*)obj)->transform, ($x) * $data->_initialScale.x, ($z) * $data->_initialScale.y, ($y) * $data->_initialScale.z)';
                } else if (prop == "loc") {
                    // Position swizzle: (X,Y,Z) -> (X,Z,-Y)
                    var args = N64CoordinateSystem.emitPositionArgs(x, y, z);
                    return '$fn(&((ArmObject*)obj)->transform, $args)';
                } else {
                    return '$fn(&((ArmObject*)obj)->transform, $x, $y, $z)';
                }

            default:
                return null;
        }
    }

    function isZeroLiteral(s:String):Bool {
        return s == "0" || s == "0.0" || s == "0.0f";
    }
    function isInputCall(s:String):Bool {
        return StringTools.startsWith(s, "input_down(") ||
               StringTools.startsWith(s, "input_started(") ||
               StringTools.startsWith(s, "input_released(");
    }

    /** Simplify input comparisons: `input_down(x) != 0` -> `input_down(x)` */
    function trySimplifyInputComparison(op:Binop, left:String, right:String):Null<String> {
        // Check for "truthy" comparison: != 0, > 0, >= 1
        var isTruthyOp = (op == OpNotEq || op == OpGt || op == OpGte);
        // Check for "falsy" comparison: == 0
        var isFalsyOp = (op == OpEq);
        // Reversed truthy: 0 < x, 0 <= x, 0 != x
        var isReversedTruthyOp = (op == OpNotEq || op == OpLt || op == OpLte);

        // input_call != 0 / > 0 / >= 0 -> input_call
        if (isTruthyOp && isZeroLiteral(right) && isInputCall(left)) {
            return left;
        }
        // 0 != input_call / 0 < input_call -> input_call
        if (isReversedTruthyOp && isZeroLiteral(left) && isInputCall(right)) {
            return right;
        }
        // input_call == 0 -> !input_call
        if (isFalsyOp && isZeroLiteral(right) && isInputCall(left)) {
            return '!$left';
        }
        // 0 == input_call -> !input_call
        if (isFalsyOp && isZeroLiteral(left) && isInputCall(right)) {
            return '!$right';
        }

        return null;
    }

    function emitAssignOp(op:Binop):String {
        return switch (op) {
            case OpAdd: "+=";
            case OpSub: "-=";
            case OpMult: "*=";
            case OpDiv: "/=";
            case OpMod: "%=";
            case OpShl: "<<=";
            case OpShr: ">>=";
            case OpXor: "^=";
            case OpAnd: "&=";
            case OpOr: "|=";
            default: "=";
        }
    }

    function emitUnop(op:Unop, postFix:Bool, e:Expr):String {
        var inner = emitExpr(e);
        var opStr = switch (op) {
            case OpIncrement: "++";
            case OpDecrement: "--";
            case OpNot: "!";
            case OpNeg: "-";
            case OpNegBits: "~";
            case OpSpread: "/* spread */";
        }
        return postFix ? '$inner$opStr' : '$opStr$inner';
    }

    function emitField(e:Expr, field:String):String {
        // Check for known API patterns
        var base = getBaseIdent(e);

        // Time.delta -> dt
        if (base == "Time" && field == "delta") {
            needsDt = true;
            return "dt";
        }

        // Gamepad stick access: gamepad.leftStick.x, gamepad.rightStick.y, etc.
        if (base == "gamepad" || base == "leftStick" || base == "rightStick") {
            return emitGamepadFieldAccess(e, field);
        }

        // transform.loc.x, transform.rot.y, etc.
        if (base == "transform") {
            return emitTransformField(e, field);
        }

        // object.transform
        if (base == "object" && field == "transform") {
            needsObj = true;
            hasTransform = true;
            return "((ArmObject*)obj)->transform";
        }

        // object.visible, object.rigid_body, etc. - direct field access on object
        if (base == "object") {
            needsObj = true;
            return '((ArmObject*)obj)->$field';
        }

        // Vec2 field access: direction.x, direction.y
        if (base != null && vec2Vars.exists(base)) {
            var vec2 = vec2Vars.get(base);
            if (field == "x") return vec2.x;
            if (field == "y") return vec2.y;
        }

        // Check for Vec2 chained call result access: direction.clone().mult(speed).x
        // The base would be a call expression
        switch (e.expr) {
            case ECall(callE, callParams):
                var chainResult = tryEmitVec2Chain(callE, callParams);
                if (chainResult != null && vec2Vars.exists(chainResult)) {
                    var vec2 = vec2Vars.get(chainResult);
                    if (field == "x") return vec2.x;
                    if (field == "y") return vec2.y;
                }
            default:
        }

        // General field access
        var baseCode = emitExpr(e);

        // Check if baseCode is a chain marker and resolve it
        if (vec2Vars.exists(baseCode)) {
            var vec2 = vec2Vars.get(baseCode);
            if (field == "x") return vec2.x;
            if (field == "y") return vec2.y;
        }

        // Detect if we need -> or .
        // Rules:
        // - Use -> only directly after a pointer cast: ((Type*)ptr)->field
        // - After any struct member access (contains ->field or .field), use .
        // - Struct members like currentScale, transform are accessed with .
        var isDirectPointerCast = (baseCode == "((ArmObject*)obj)" || baseCode == '((${traitName}Data*)data)');
        if (isDirectPointerCast) {
            return '$baseCode->$field';
        }
        // Everything else uses . (including chained access like data->currentScale.y)
        return '$baseCode.$field';
    }

    /** Map gamepad.leftStick.x -> input_stick_x(). N64 has no right stick. */
    function emitGamepadFieldAccess(e:Expr, field:String):String {
        var chain = getFieldChain(e);
        chain.push(field);

        // Pattern: gamepad.leftStick.x or gamepad.rightStick.y
        if (chain.length >= 3) {
            var stick = chain[chain.length - 2];  // leftStick or rightStick
            var axis = chain[chain.length - 1];   // x or y

            if (stick == "leftStick") {
                // N64's main analog stick
                var axisName = (axis == "x") ? "x" : "y";
                return 'input_stick_$axisName()';
            }
            if (stick == "rightStick") {
                // N64 has no right stick - return 0 as neutral
                warn("N64 has no right stick, using 0.0f");
                return '0.0f';
            }
        }

        // Pattern: gamepad.leftStick or gamepad.rightStick (struct access - shouldn't happen)
        if (field == "leftStick" || field == "rightStick") {
            // Return placeholder that will be followed by .x/.y
            return field;
        }

        warn('Unsupported gamepad field: $field');
        return '/* N64_UNSUPPORTED: gamepad.$field */';
    }

    function emitTransformField(e:Expr, field:String):String {
        needsObj = true;

        // Get the sub-field chain
        var chain = getFieldChain(e);

        // transform.loc -> ((ArmObject*)obj)->transform.pos
        // transform.rot -> ((ArmObject*)obj)->transform.rot
        // transform.scale -> ((ArmObject*)obj)->transform.scale
        if (chain.length >= 1) {
            var prop = chain[chain.length - 1];
            var cProp = switch (prop) {
                case "loc": "pos";
                case "rot": "rot";
                case "scale": "scale";
                default: prop;
            };

            // x, y, z with coordinate conversion
            var axis = switch (field) {
                case "x": "[0]";  // X stays X
                case "y": "[2]";  // Blender Y -> N64 Z (with negate for some)
                case "z": "[1]";  // Blender Z -> N64 Y
                default: '.$field';
            };

            return '((ArmObject*)obj)->transform.$cProp$axis';
        }

        return '((ArmObject*)obj)->transform.$field';
    }

    function emitCall(e:Expr, params:Array<Expr>):String {
        // Check for Math.* calls
        var mathCall = tryEmitMathCall(e, params);
        if (mathCall != null) return mathCall;

        // Check for Vec2 method calls (length, clone, mult, etc.)
        var vec2Call = tryEmitVec2Call(e, params);
        if (vec2Call != null) return vec2Call;

        // Check for object.getTrait(RigidBody) and similar
        var traitCall = tryEmitGetTraitCall(e, params);
        if (traitCall != null) return traitCall;

        // Detect API calls
        var callInfo = detectApiCall(e);
        if (callInfo != null) {
            return emitApiCall(callInfo.category, callInfo.method, params);
        }

        // Check for Armory internal calls that should be skipped
        var funcName = getFunctionName(e);
        if (shouldSkipCall(funcName)) {
            return "";  // Skip internal Armory calls
        }

        // Regular function call
        var emittedName = emitExpr(e);
        var args = [for (p in params) emitExpr(p)].join(", ");
        return '$emittedName($args)';
    }

    /** Handle object.getTrait(TraitClass) calls */
    function tryEmitGetTraitCall(e:Expr, params:Array<Expr>):String {
        return switch (e.expr) {
            case EField(base, method):
                if (method == "getTrait") {
                    var baseName = getBaseIdent(base);
                    if (baseName == "object" && params.length > 0) {
                        var traitType = getBaseIdent(params[0]);
                        if (traitType == "RigidBody") {
                            // On N64, the rigid body is directly linked to the object
                            return "((ArmObject*)obj)->rigid_body";
                        } else {
                            warn('getTrait($traitType) not supported on N64');
                            return '/* N64_UNSUPPORTED: getTrait($traitType) */';
                        }
                    }
                }
                null;
            default: null;
        };
    }

    function tryEmitMathCall(e:Expr, params:Array<Expr>):String {
        return switch (e.expr) {
            case EField(base, method):
                var baseName = getBaseIdent(base);
                if (baseName == "Math") {
                    needsMath = true;
                    var args = [for (p in params) emitExpr(p)].join(", ");
                    return switch (method) {
                        // Basic math
                        case "sqrt": 'sqrtf($args)';
                        case "abs": 'fabsf($args)';
                        case "pow": 'powf($args)';
                        // Trigonometry
                        case "sin": 'sinf($args)';
                        case "cos": 'cosf($args)';
                        case "tan": 'tanf($args)';
                        case "asin": 'asinf($args)';
                        case "acos": 'acosf($args)';
                        case "atan": 'atanf($args)';
                        case "atan2": 'atan2f($args)';
                        // Exponential/logarithmic
                        case "log": 'logf($args)';
                        case "exp": 'expf($args)';
                        // Rounding
                        case "floor": 'floorf($args)';
                        case "ceil": 'ceilf($args)';
                        case "round": 'roundf($args)';
                        // Min/max
                        case "min": 'fminf($args)';
                        case "max": 'fmaxf($args)';
                        // Constants (no args needed)
                        case "PI": 'M_PI';
                        case "POSITIVE_INFINITY": 'INFINITY';
                        case "NEGATIVE_INFINITY": '(-INFINITY)';
                        case "NaN": 'NAN';
                        default:
                            warn('Unsupported Math function: $method');
                            '/* N64_UNSUPPORTED: Math.$method */';
                    };
                }
                null;
            default: null;
        };
    }

    function tryEmitVec2Call(e:Expr, params:Array<Expr>):String {
        return switch (e.expr) {
            case EField(base, method):
                // Check if base is a Vec2 variable
                var baseName = getBaseIdent(base);
                if (baseName != null && vec2Vars.exists(baseName)) {
                    return emitVec2Method(baseName, method, params, base);
                }
                // Check for chained calls like direction.clone().mult(speed)
                var chainResult = tryEmitVec2Chain(e, params);
                if (chainResult != null) return chainResult;
                null;
            default: null;
        };
    }

    function emitVec2Method(varName:String, method:String, params:Array<Expr>, baseExpr:Expr):String {
        return switch (method) {
            case "length":
                needsMath = true;
                'sqrtf(${varName}_x * ${varName}_x + ${varName}_y * ${varName}_y)';
            case "lengthSq":
                '(${varName}_x * ${varName}_x + ${varName}_y * ${varName}_y)';
            case "clone":
                // clone() returns the same variable reference for chaining
                // The actual cloning happens at the point of use
                '__vec2_clone_${varName}';  // Marker for chain resolution
            case "mult":
                if (params.length > 0) {
                    var scalar = emitExpr(params[0]);
                    // Create a temporary result - this is typically used inline
                    '__vec2_mult_${varName}_$scalar';  // Marker for chain resolution
                } else {
                    warn("Vec2.mult() needs an argument");
                    '/* N64_UNSUPPORTED: Vec2.mult needs arg */';
                }
            case "normalize":
                needsMath = true;
                var lenExpr = 'sqrtf(${varName}_x * ${varName}_x + ${varName}_y * ${varName}_y)';
                '__vec2_norm_${varName}';  // Marker
            case "dot":
                if (params.length > 0) {
                    var other = getBaseIdent(params[0]);
                    if (other != null && vec2Vars.exists(other)) {
                        '(${varName}_x * ${other}_x + ${varName}_y * ${other}_y)';
                    } else {
                        var otherExpr = emitExpr(params[0]);
                        '(${varName}_x * $otherExpr.x + ${varName}_y * $otherExpr.y)';
                    }
                } else {
                    warn("Vec2.dot() needs an argument");
                    '/* N64_UNSUPPORTED: Vec2.dot needs arg */';
                }
            default:
                warn('Unsupported Vec2 method: $method');
                '/* N64_UNSUPPORTED: Vec2.$method */';
        };
    }

    /** Handle chained Vec2 calls like direction.clone().mult(speed) */
    function tryEmitVec2Chain(e:Expr, finalParams:Array<Expr>):String {
        // Parse the chain from right to left
        var chain:Array<{method:String, params:Array<Expr>}> = [];
        var currentExpr = e;
        var baseVarName:String = null;

        while (true) {
            switch (currentExpr.expr) {
                case EField(base, method):
                    // This could be var.method or (prevCall).method
                    var baseName = getBaseIdent(base);
                    if (baseName != null && vec2Vars.exists(baseName)) {
                        // Found the base Vec2 variable
                        baseVarName = baseName;
                        chain.unshift({method: method, params: finalParams});
                        break;
                    }
                    // Check if base is itself a call (chained)
                    switch (base.expr) {
                        case ECall(innerE, innerParams):
                            chain.unshift({method: method, params: finalParams});
                            finalParams = innerParams;
                            currentExpr = innerE;
                        default:
                            return null;  // Not a chain we can handle
                    }
                default:
                    return null;
            }
        }

        if (baseVarName == null || chain.length == 0) return null;

        // Now resolve the chain
        // Start with base variable's x/y
        var xExpr = '${baseVarName}_x';
        var yExpr = '${baseVarName}_y';

        for (link in chain) {
            switch (link.method) {
                case "clone":
                    // clone() just passes through - no change to expressions
                    continue;
                case "mult":
                    if (link.params.length > 0) {
                        var scalar = emitExpr(link.params[0]);
                        xExpr = '($xExpr * $scalar)';
                        yExpr = '($yExpr * $scalar)';
                    }
                case "normalize":
                    needsMath = true;
                    var lenExpr = 'sqrtf($xExpr * $xExpr + $yExpr * $yExpr)';
                    xExpr = '($xExpr / $lenExpr)';
                    yExpr = '($yExpr / $lenExpr)';
                case "add":
                    if (link.params.length > 0) {
                        var other = getBaseIdent(link.params[0]);
                        if (other != null && vec2Vars.exists(other)) {
                            xExpr = '($xExpr + ${other}_x)';
                            yExpr = '($yExpr + ${other}_y)';
                        }
                    }
                case "sub":
                    if (link.params.length > 0) {
                        var other = getBaseIdent(link.params[0]);
                        if (other != null && vec2Vars.exists(other)) {
                            xExpr = '($xExpr - ${other}_x)';
                            yExpr = '($yExpr - ${other}_y)';
                        }
                    }
                default:
                    return null;  // Unsupported method in chain
            }
        }

        // Return a special marker that will be resolved when accessing .x or .y
        // Store the resolved expressions temporarily with unique counter
        var tempName = '__chain_${baseVarName}_${chainCounter++}';
        vec2Vars.set(tempName, {x: xExpr, y: yExpr});
        return tempName;
    }

    function getFunctionName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, field): field;
            default: "";
        };
    }

    function shouldSkipCall(name:String):Bool {
        return switch (name) {
            // Trait lifecycle registration (handled differently on N64)
            // Valid methods from iron.Trait: notifyOnAdd, notifyOnInit, notifyOnRemove, notifyOnUpdate,
            // notifyOnLateUpdate, notifyOnFixedUpdate, notifyOnRender, notifyOnRender2D
            case "notifyOnAdd", "notifyOnInit", "notifyOnUpdate", "notifyOnRemove",
                 "notifyOnLateUpdate", "notifyOnFixedUpdate", "notifyOnRender", "notifyOnRender2D": true;
            // Object casting/creation
            case "cast", "super": true;
            // Debug/logging
            case "trace", "log": true;
            default: false;
        };
    }

    function detectApiCall(e:Expr):{category:String, method:String} {
        return switch (e.expr) {
            case EField(base, method):
                // Check for object.transform.method() pattern
                switch (base.expr) {
                    case EField(_, innerField):
                        // e.g., object.transform.rotate -> innerField = "transform"
                        if (innerField == "transform") {
                            return {category: "transform", method: method};
                        }
                        // Check root for other patterns
                        var root = getBaseIdent(base);
                        if (root != null) {
                            switch (root) {
                                case "gamepad", "keyboard", "mouse":
                                    return {category: root, method: innerField};
                                // Physics: rb.applyForce, etc.
                                case "rb":
                                    return {category: "rigidbody", method: method};
                                default:
                            }
                        }
                        return null;
                    default:
                        // Simple category.method pattern
                        var category = getBaseIdent(base);
                        if (category != null) {
                            switch (category) {
                                case "gamepad", "keyboard", "mouse", "transform", "scene", "Input", "Scene":
                                    return {category: category, method: method};
                                // Physics: PhysicsWorld.active, rb.method
                                case "PhysicsWorld":
                                    return {category: "physicsworld", method: method};
                                case "rb":
                                    return {category: "rigidbody", method: method};
                                default: null;
                            }
                        } else null;
                }
            default: null;
        }
    }

    function emitApiCall(category:String, method:String, params:Array<Expr>):String {
        var apiKey = '$category.$method';

        // Input class static methods - skip initialization (N64 input is always available)
        if (category == "Input") {
            return switch (method) {
                case "getGamepad", "getKeyboard", "getMouse": "";
                default:
                    warn('Unsupported Input method: $method');
                    '/* N64_UNSUPPORTED: Input.$method */';
            };
        }

        // Scene class static methods
        if (category == "Scene") {
            return emitSceneCall(method, params);
        }

        // Input APIs (gamepad/keyboard/mouse instance methods)
        if (category == "gamepad") {
            return emitGamepadCall(method, params);
        }

        // Transform APIs
        if (category == "transform") {
            return emitTransformCall(method, params);
        }

        // Scene APIs (lowercase scene is instance)
        if (category == "scene") {
            return emitSceneCall(method, params);
        }

        // Physics APIs - delegated to N64PhysicsMacro
        if (category == "physicsworld") {
            return N64PhysicsMacro.emitPhysicsWorldCall(method, params, this);
        }
        if (category == "rigidbody") {
            return N64PhysicsMacro.emitRigidBodyCall(method, params, this);
        }

        // Fallback
        warn('Unsupported API: $apiKey');
        return '/* N64_UNSUPPORTED: API $apiKey */';
    }

    // Physics emission moved to N64PhysicsMacro.hx

    function emitGamepadCall(method:String, params:Array<Expr>):String {
        // Get N64 function name
        var n64Func = N64Config.mapInputState(method);

        // Stick methods
        if (method == "getStickX" || method == "getStickY") {
            n64Func = N64Config.mapStick(method);
            return '$n64Func()';
        }

        // Button methods (down, started, released)
        if (params.length > 0) {
            var buttonExpr = params[0];
            var button = extractButtonName(buttonExpr);
            var n64Button = N64Config.mapButton(button);

            // Warn and use default if button is unknown
            if (n64Button == null) {
                Context.warning('N64: Unknown button "$button", using default (A button)', buttonExpr.pos);
                n64Button = N64Config.getDefaultButton();
            }

            // Track button usage
            if (!Lambda.has(inputButtons, n64Button)) {
                inputButtons.push(n64Button);
            }

            return '$n64Func($n64Button)';
        }

        return '$n64Func(${N64Config.getDefaultButton()})';
    }

    function extractButtonName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            case EConst(CIdent(s)): s;
            case EField(_, field): field;  // e.g., Button.cross -> "cross"
            default: "a";
        }
    }

    function emitTransformCall(method:String, params:Array<Expr>):String {
        needsObj = true;
        hasTransform = true;

        switch (method) {
            case "rotate":
                return emitRotate(params);
            case "translate", "move":
                return emitTranslate(params);
            case "scale":
                return emitScale(params);
            case "buildMatrix":
                return "((ArmObject*)obj)->transform.dirty = 3";
            default:
                warn('Unsupported transform method: $method');
                return '/* N64_UNSUPPORTED: transform.$method */';
        }
    }

    function emitScale(params:Array<Expr>):String {
        if (params.length == 0) {
            warn("scale() requires arguments");
            return "/* N64_UNSUPPORTED: scale() needs args */";
        }

        var first = params[0];
        switch (first.expr) {
            case EConst(CFloat(_)), EConst(CInt(_)):
                // scale(x, y, z) - three separate numbers
                if (params.length >= 3) {
                    var x = emitExpr(params[0]);
                    var y = emitExpr(params[1]);
                    var z = emitExpr(params[2]);
                    var args = N64CoordinateSystem.emitScaleArgs(x, y, z);
                    return 'it_set_scale(&((ArmObject*)obj)->transform, $args)';
                } else if (params.length == 1) {
                    // scale(uniform) - single value for all axes (no swizzle needed)
                    var s = emitExpr(params[0]);
                    return 'it_set_scale(&((ArmObject*)obj)->transform, $s, $s, $s)';
                }
            case ENew(tp, newParams):
                // scale(new Vec4(x, y, z))
                if (tp.name == "Vec4") {
                    var x:String, y:String, z:String;
                    if (newParams.length >= 3) {
                        x = emitExpr(newParams[0]);
                        y = emitExpr(newParams[1]);
                        z = emitExpr(newParams[2]);
                    } else if (newParams.length == 1) {
                        var v = emitExpr(newParams[0]);
                        x = v; y = v; z = v;
                    } else {
                        x = "1.0f"; y = "1.0f"; z = "1.0f";  // Default scale
                    }
                    var args = N64CoordinateSystem.emitScaleArgs(x, y, z);
                    return 'it_set_scale(&((ArmObject*)obj)->transform, $args)';
                }
                // Fall through to default
                var v = emitExpr(first);
                var args = N64CoordinateSystem.emitRuntimeScaleConversion(v);
                return 'it_set_scale(&((ArmObject*)obj)->transform, $args)';
            default:
                // scale(vec) - assume Vec4-like with x, y, z fields
                var v = emitExpr(first);
                var args = N64CoordinateSystem.emitRuntimeScaleConversion(v);
                return 'it_set_scale(&((ArmObject*)obj)->transform, $args)';
        }
        warn("Unsupported scale() parameter format");
        return "/* N64_UNSUPPORTED: scale() params */";
    }

    /** Emit rotate with axis resolution and coordinate conversion */
    function emitRotate(params:Array<Expr>):String {
        if (params.length < 2) {
            warn("rotate() requires axis and angle arguments");
            return "/* N64_UNSUPPORTED: rotate() needs axis and angle */";
        }

        var axisExpr = params[0];
        var angleExpr = params[1];

        // Resolve axis to N64 coordinates
        var axisInfo = resolveAxisVec(axisExpr);
        var angleCode = emitExpr(angleExpr);

        // Format floats with decimal point for C (1 -> 1.0f, not 1f)
        var xStr = floatToC(axisInfo.x);
        var yStr = floatToC(axisInfo.y);
        var zStr = floatToC(axisInfo.z);

        // Generate global axis rotation call (matches Armory's world-space rotation)
        return 'it_rotate_axis_global(&((ArmObject*)obj)->transform, $xStr, $yStr, $zStr, $angleCode)';
    }

    function floatToC(f:Float):String {
        var s = Std.string(f);
        // If no decimal point, add .0
        if (s.indexOf('.') == -1) {
            s += '.0';
        }
        return s + 'f';
    }

    /** Resolve Vec4 axis to N64 coordinates: Blender (X,Y,Z) -> N64 (X, Z, -Y) */
    function resolveAxisVec(e:Expr):{x:Float, y:Float, z:Float} {
        // Look for Vec4(x,y,z) or iron.math.Vec4(x,y,z)
        switch (e.expr) {
            case ENew(_, params) | ECall(_, params):
                var bx:Float = 0.0, by:Float = 0.0, bz:Float = 0.0;
                if (params.length >= 3) {
                    bx = getConstFloat(params[0]);
                    by = getConstFloat(params[1]);
                    bz = getConstFloat(params[2]);
                } else if (params.length == 2) {
                    bx = getConstFloat(params[0]);
                    by = getConstFloat(params[1]);
                    bz = 0.0;
                } else if (params.length == 1) {
                    var v = getConstFloat(params[0]);
                    bx = v; by = v; bz = v;
                }
                // Use centralized coordinate conversion
                return N64CoordinateSystem.convertAxisValues(bx, by, bz);
            case EField(_, field):
                // Vec4.xAxis(), etc. - convert standard Blender axes to N64
                return switch (field) {
                    case "xAxis": N64CoordinateSystem.convertAxisValues(1.0, 0.0, 0.0);
                    case "yAxis": N64CoordinateSystem.convertAxisValues(0.0, 1.0, 0.0);
                    case "zAxis": N64CoordinateSystem.convertAxisValues(0.0, 0.0, 1.0);
                    default: N64CoordinateSystem.convertAxisValues(0.0, 0.0, 1.0);  // Default Z-up in Blender
                }
            case EConst(CIdent(name)):
                // Member variable reference - look up its initialization expression
                if (vec4Exprs.exists(name)) {
                    return resolveAxisVec(vec4Exprs.get(name));
                }
            default:
        }

        return N64CoordinateSystem.convertAxisValues(0.0, 0.0, 1.0);  // Default Z axis (Blender up)
    }

    function getConstFloat(e:Expr):Float {
        return switch (e.expr) {
            case EConst(CFloat(f)): Std.parseFloat(f);
            case EConst(CInt(i)): Std.parseInt(i);
            case EUnop(OpNeg, false, inner):
                -getConstFloat(inner);
            default: 0.0;
        }
    }

    function emitTranslate(params:Array<Expr>):String {
        if (params.length == 0) {
            warn("translate() requires arguments");
            return "/* N64_UNSUPPORTED: translate() needs args */";
        }

        // Single Vec4 argument
        if (params.length == 1) {
            var vec = params[0];
            // Try to extract x,y,z from Vec4 construction
            switch (vec.expr) {
                case ENew(_, args), ECall(_, args):
                    if (args.length >= 3) {
                        var x = emitExpr(args[0]);
                        var y = emitExpr(args[1]);
                        var z = emitExpr(args[2]);
                        var posArgs = N64CoordinateSystem.emitPositionArgs(x, y, z);
                        return 'it_translate(&((ArmObject*)obj)->transform, $posArgs)';
                    }
                default:
            }
            // Runtime variable - need to swizzle at runtime
            var v = emitExpr(vec);
            var posArgs = N64CoordinateSystem.emitPositionArgs('$v.x', '$v.y', '$v.z');
            return 'it_translate(&((ArmObject*)obj)->transform, $posArgs)';
        }

        // Three separate arguments (already x, y, z)
        if (params.length >= 3) {
            var x = emitExpr(params[0]);
            var y = emitExpr(params[1]);
            var z = emitExpr(params[2]);
            var posArgs = N64CoordinateSystem.emitPositionArgs(x, y, z);
            return 'it_translate(&((ArmObject*)obj)->transform, $posArgs)';
        }

        warn("Unsupported translate() parameter format");
        return "/* N64_UNSUPPORTED: translate() params */";
    }

    function emitSceneCall(method:String, params:Array<Expr>):String {
        hasScene = true;

        switch (method) {
            case "setActive":
                if (params.length > 0) {
                    var sceneExpr = params[0];
                    // Extract scene name - if hardcoded, use target_scene member
                    var sceneName = extractSceneName(sceneExpr);
                    if (sceneName != null) {
                        targetScene = sceneName;
                        // Use target_scene member (will be added by macro)
                        return 'scene_switch_to(((${traitName}Data*)data)->target_scene)';
                    }
                    // Check if it's a member variable (stored as SceneId)
                    var memberName = getMemberName(sceneExpr);
                    if (memberName != null && memberNames.exists(memberName)) {
                        // Member variable - should be SceneId type
                        return 'scene_switch_to(((${traitName}Data*)data)->$memberName)';
                    }
                    // Fallback: emit the expression
                    var sceneId = emitExpr(sceneExpr);
                    return 'scene_switch_to($sceneId)';
                }
                return "scene_switch_to(0)";
            default:
                warn('Unsupported scene method: $method');
                return '/* N64_UNSUPPORTED: scene.$method */';
        }
    }

    function getMemberName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            default: null;
        }
    }

    function extractSceneName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)):
                // Direct string: Scene.setActive("level_2")
                s.toLowerCase();
            case EField(base, field):
                // Could be Scene.Level_2 or similar
                field.toLowerCase();
            default:
                // Could be a member variable - return null to use emitExpr
                null;
        }
    }

    function getBaseIdent(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(s)): s;
            case EField(base, _): getBaseIdent(base);
            default: null;
        }
    }

    function getFieldChain(e:Expr):Array<String> {
        var chain:Array<String> = [];
        var current = e;
        while (true) {
            switch (current.expr) {
                case EField(base, field):
                    chain.unshift(field);
                    current = base;
                case EConst(CIdent(s)):
                    chain.unshift(s);
                    break;
                default:
                    break;
            }
        }
        return chain;
    }

    function emitNew(tp:TypePath, params:Array<Expr>):String {
        var typeName = tp.name;
        var args = [for (p in params) emitExpr(p)].join(", ");

        return switch (typeName) {
            case "Vec2":
                if (params.length >= 2) {
                    var x = emitExpr(params[0]);
                    var y = emitExpr(params[1]);
                    '(ArmVec2){$x, $y}';
                } else if (params.length == 1) {
                    var v = emitExpr(params[0]);
                    '(ArmVec2){$v, $v}';
                } else {
                    "(ArmVec2){0.0f, 0.0f}";
                }
            case "Vec3", "Vec4":
                if (params.length >= 3) {
                    var x = emitExpr(params[0]);
                    var y = emitExpr(params[1]);
                    var z = emitExpr(params[2]);
                    '(ArmVec3){$x, $y, $z}';
                } else if (params.length == 1) {
                    var v = emitExpr(params[0]);
                    '(ArmVec3){$v, $v, $v}';
                } else {
                    "(ArmVec3){0.0f, 0.0f, 0.0f}";
                }
            case "String":
                if (params.length > 0) emitExpr(params[0]) else '""';
            case "Array", "Map", "StringMap", "IntMap":
                warn('$typeName not supported on N64');
                "";
            default:
                if (params.length == 0) '($typeName){0}' else '($typeName){$args}';
        };
    }

    function emitObjectDecl(fields:Array<ObjectField>):String {
        var fieldStrs:Array<String> = [];
        for (f in fields) {
            var value = emitExpr(f.expr);
            fieldStrs.push('.${ f.field } = $value');
        }
        return '{${fieldStrs.join(", ")}}';
    }

    function emitLocalFunction(func:Function):String {
        error("Local functions/closures not supported");
        return "";
    }

    function emitSwitch(e:Expr, cases:Array<Case>, edef:Null<Expr>):String {
        var switchExpr = emitExpr(e);
        var caseStrs:Array<String> = [];

        for (c in cases) {
            for (v in c.values) {
                var caseVal = emitExpr(v);
                caseStrs.push('case $caseVal:');
            }
            var body = c.expr != null ? emitExpr(c.expr) : "";
            if (body != "") {
                caseStrs.push('{ $body; break; }');
            } else {
                caseStrs.push("break;");
            }
        }

        if (edef != null) {
            var defBody = emitExpr(edef);
            caseStrs.push('default: { $defBody; break; }');
        }

        return 'switch ($switchExpr) { ${caseStrs.join(" ")} }';
    }

    function emitTry(e:Expr, catches:Array<Catch>):String {
        error("try/catch not supported");
        return emitExpr(e);
    }

    function emitThrow(e:Expr):String {
        error("throw not supported");
        return "";
    }

    function emitCast(e:Expr, t:Null<ComplexType>):String {
        var inner = emitExpr(e);
        if (t == null) return inner;
        var typeName = complexTypeToC(t);
        return '(($typeName)$inner)';
    }

    function emitIs(e:Expr, t:ComplexType):String {
        error("'is' type check not supported at runtime");
        return "true";
    }

    function complexTypeToC(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): N64Config.mapType(p.name);
            default: "void*";
        };
    }

    function emitBlock(exprs:Array<Expr>):String {
        var lines:Array<String> = [];
        for (e in exprs) {
            var code = emitExpr(e);
            if (code != "" && StringTools.trim(code) != "") {
                lines.push(code);
            }
        }
        return lines.join(";\n") + (lines.length > 0 ? ";" : "");
    }

    function emitIf(econd:Expr, eif:Expr, eelse:Expr):String {
        var cond = emitExpr(econd);

        // If condition emits empty (skipped variable), skip the whole if
        if (cond == null || cond == "" || StringTools.trim(cond) == "" || cond.indexOf("/* N64_UNSUPPORTED") >= 0) {
            return "";
        }

        var thenCode = emitExpr(eif);

        // If then block is empty, skip the whole if
        if (thenCode == null || thenCode == "" || StringTools.trim(thenCode) == "") {
            return "";
        }

        var result = 'if ($cond) { $thenCode }';
        if (eelse != null) {
            var elseCode = emitExpr(eelse);
            if (elseCode != null && elseCode != "" && StringTools.trim(elseCode) != "") {
                result += ' else { $elseCode }';
            }
        }
        return result;
    }

    function emitWhile(econd:Expr, body:Expr, normalWhile:Bool):String {
        var cond = emitExpr(econd);
        var bodyCode = emitExpr(body);
        if (normalWhile) {
            return 'while ($cond) { $bodyCode; }';
        } else {
            return 'do { $bodyCode; } while ($cond)';
        }
    }

    function emitFor(it:Expr, body:Expr):String {
        switch (it.expr) {
            case EBinop(OpInterval, startExpr, endExpr):
                var start = emitExpr(startExpr);
                var end = emitExpr(endExpr);
                var bodyCode = emitExpr(body);
                return 'for (int _i = $start; _i < $end; _i++) { $bodyCode; }';
            default:
                warn("Complex for-loop iterator not yet supported, use for (i in 0...n) syntax");
                return "";
        }
    }

    function emitVars(vars:Array<Var>):String {
        var decls:Array<String> = [];
        for (v in vars) {
            localVars.set(v.name, true);
            var typeName = v.type != null ? N64Config.mapType(typeToString(v.type)) : "float";

            // Handle Vec2 variable declarations specially (split into _x, _y floats)
            if ((typeName == "Vec2" || typeName == "ArmVec2") && v.expr != null) {
                var vec2Init = tryExtractVec2(v.expr);
                if (vec2Init != null) {
                    // Store variable name references for later field access (motion.x -> motion_x)
                    vec2Vars.set(v.name, {x: '${v.name}_x', y: '${v.name}_y'});
                    // Emit as two separate float variables with init expressions
                    decls.push('float ${v.name}_x = ${vec2Init.x}');
                    decls.push('float ${v.name}_y = ${vec2Init.y}');
                    continue;
                }
            }

            var init = v.expr != null ? ' = ${emitExpr(v.expr)}' : "";
            decls.push('$typeName ${v.name}$init');
        }
        return decls.join("; ");
    }

    /** Extract Vec2 constructor args as {x, y} C expressions, or null */
    function tryExtractVec2(e:Expr):{x:String, y:String} {
        return switch (e.expr) {
            case ENew(tp, params):
                if (tp.name == "Vec2") {
                    if (params.length >= 2) {
                        {x: emitExpr(params[0]), y: emitExpr(params[1])};
                    } else if (params.length == 1) {
                        // Copy constructor: new Vec2(otherVec) - try to resolve
                        var other = getBaseIdent(params[0]);
                        if (other != null && vec2Vars.exists(other)) {
                            var src = vec2Vars.get(other);
                            {x: src.x, y: src.y};
                        } else {
                            // Single scalar: new Vec2(val) -> (val, val)
                            var val = emitExpr(params[0]);
                            {x: val, y: val};
                        }
                    } else {
                        // Default constructor: new Vec2() -> (0, 0)
                        {x: "0.0f", y: "0.0f"};
                    }
                } else null;
            case ECall(func, params):
                // Check for Vec2(x, y) function call style
                var funcName = getFunctionName(func);
                if (funcName == "Vec2") {
                    if (params.length >= 2) {
                        {x: emitExpr(params[0]), y: emitExpr(params[1])};
                    } else if (params.length == 0) {
                        {x: "0.0f", y: "0.0f"};
                    } else null;
                } else {
                    // Check for Vec2 method calls like direction.clone().mult(speed)
                    var chainResult = tryEmitVec2Chain(func, params);
                    if (chainResult != null && vec2Vars.exists(chainResult)) {
                        vec2Vars.get(chainResult);
                    } else null;
                }
            default: null;
        };
    }

    function emitReturn(e:Expr):String {
        if (e == null) return "return";
        return 'return ${emitExpr(e)}';
    }

    function emitArrayDecl(values:Array<Expr>):String {
        var vals = [for (v in values) emitExpr(v)].join(", ");
        return '{$vals}';
    }

    function typeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): p.name;
            default: "Dynamic";
        }
    }

    // Public accessors

    public function requiresObj():Bool return needsObj;
    public function requiresDt():Bool return needsDt;
    public function requiresMath():Bool return needsMath;
    public function getInputButtons():Array<String> return inputButtons;
    public function hasTransformOps():Bool return hasTransform;
    public function hasSceneOps():Bool return hasScene;
    public function getTargetScene():String return targetScene;
    public function requiresInitialScale():Bool return needsInitialScale;
}
#end
