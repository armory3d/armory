package armory.n64;

#if macro
import haxe.macro.Expr;

using StringTools;
using Lambda;

/**
 * N64 C Code Emitter
 *
 * Converts Haxe expressions directly to C code strings.
 * This is the "smart" part - all resolution happens here.
 *
 * Key responsibilities:
 * - Resolve member access with inline casts: ((TraitData*)data)->member
 * - Resolve object access with inline casts: ((ArmObject*)obj)->field
 * - Resolve button names to N64 constants
 * - Resolve Vec4 axes to indices
 * - Apply coordinate system conversion (Blender Z-up → N64 Y-up)
 * - Generate final C code strings
 * - Track what features are used (buttons, transform, scene)
 *
 * Note: Inline casts are used instead of local typed pointers to save
 * stack space and avoid unnecessary pointer copies on the N64's limited hardware.
 */
class N64CEmitter {
    // Context for the current trait
    var traitName:String;
    var memberNames:Map<String, Bool>;
    var localVars:Map<String, Bool>;
    var vec4Exprs:Map<String, Expr>;  // Vec4 member init expressions for axis resolution
    var needsObj:Bool = false;
    var needsDt:Bool = false;

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
        inputButtons = [];
        this.vec4Exprs = vec4Exprs != null ? vec4Exprs : new Map();
        for (m in members) {
            memberNames.set(m, true);
        }
    }

    /**
     * Main entry: emit C code for an expression
     */
    public function emitExpr(expr:Expr):String {
        if (expr == null) return "";

        return switch (expr.expr) {
            case EConst(c): emitConst(c);
            case EBinop(op, e1, e2): emitBinop(op, e1, e2);
            case EUnop(op, postFix, e): emitUnop(op, postFix, e);
            case EField(e, field): emitField(e, field);
            case ECall(e, params): emitCall(e, params);
            case EParenthesis(e): '(${emitExpr(e)})';
            case EArray(e1, e2): '${emitExpr(e1)}[${emitExpr(e2)}]';
            case EArrayDecl(values): emitArrayDecl(values);
            case EBlock(exprs): emitBlock(exprs);
            case EIf(econd, eif, eelse): emitIf(econd, eif, eelse);
            case EWhile(econd, e, normalWhile): emitWhile(econd, e, normalWhile);
            case EFor(it, body): emitFor(it, body);
            case EVars(vars): emitVars(vars);
            case EReturn(e): emitReturn(e);
            case EBreak: "break";
            case EContinue: "continue";
            case ETernary(econd, eif, eelse): '(${emitExpr(econd)} ? ${emitExpr(eif)} : ${emitExpr(eelse)})';
            default: "/* unsupported expr */";
        }
    }

    /**
     * Emit a constant value
     */
    function emitConst(c:Constant):String {
        return switch (c) {
            case CInt(v): v;
            case CFloat(f): '${f}f';
            case CString(s): '"$s"';
            case CIdent(s): resolveIdent(s);
            case CRegexp(_, _): "/* regex unsupported */";
        }
    }

    /**
     * Resolve an identifier to C
     */
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

    /**
     * Check if this is an Armory-internal variable that should be skipped entirely
     */
    function isSkippedVariable(name:String):Bool {
        return switch (name) {
            case "camera": true;  // Camera casting not supported
            case "msg", "error": true;  // try/catch variables
            default: false;
        };
    }

    /**
     * Check if this is an input device variable (always available on N64)
     */
    function isInputVariable(name:String):Bool {
        return switch (name) {
            case "gamepad", "keyboard", "mouse": true;
            default: false;
        };
    }

    /**
     * Emit binary operation
     */
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

        // Simplify input function comparisons: `input_down(x) != 0.0f` -> `input_down(x)`
        // N64's input functions return bool, so comparison to 0 is redundant
        if ((op == OpNotEq || op == OpGt || op == OpGte) && isZeroLiteral(right)) {
            if (isInputCall(left)) {
                return left;  // Just return the bool-returning function call
            }
        }
        // Handle reversed: `0.0f != input_down(x)` -> `input_down(x)`
        if ((op == OpNotEq || op == OpLt || op == OpLte) && isZeroLiteral(left)) {
            if (isInputCall(right)) {
                return right;
            }
        }
        // Handle equality: `input_down(x) == 0.0f` -> `!input_down(x)`
        if (op == OpEq && isZeroLiteral(right) && isInputCall(left)) {
            return '!$left';
        }
        if (op == OpEq && isZeroLiteral(left) && isInputCall(right)) {
            return '!$right';
        }

        // Skip operations where either side is empty (skipped variable)
        if (left == "" || right == "") {
            return "";
        }

        // Skip assignments where right side is unsupported
        if (op == OpAssign && right == "/* unsupported expr */") {
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

    /**
     * Handle: object.transform.scale = new Vec4(x, y, z)
     * Converts to: it_set_scale(&transform, x * SCALE_FACTOR, y * SCALE_FACTOR, z * SCALE_FACTOR)
     * The scale factor (0.015) is applied because Blender Vec4 values are in Blender units
     * but N64 transform scale is already in N64 units (pre-multiplied by 0.015)
     */
    function tryEmitScaleAssign(lhs:Expr, rhs:Expr):Null<String> {
        // LHS must end with .scale, .loc, or .rot on a transform
        var chain = getFieldChain(lhs);
        if (chain.length < 3) return null;

        // Look for ["object"|"this", "transform", "scale"|"loc"|"rot"]
        var lastTwo = [chain[chain.length - 2], chain[chain.length - 1]];
        if (lastTwo[0] != "transform") return null;

        var prop = lastTwo[1];
        if (prop != "scale" && prop != "loc" && prop != "rot") return null;

        // RHS must be new Vec4(x, y, z)
        switch (rhs.expr) {
            case ENew(tp, params):
                if (tp.name != "Vec4" || params.length < 3) return null;

                var x = emitExpr(params[0]);
                var y = emitExpr(params[1]);
                var z = emitExpr(params[2]);

                if (x == "" || y == "" || z == "") return null;

                needsObj = true;
                hasTransform = true;

                var fn = 'it_set_$prop';

                if (prop == "scale") {
                    // Scale values are relative to initial scale (1.0 = original size)
                    // Multiply by _initialScale which is auto-captured in on_ready
                    // Apply coordinate swizzle: Blender (X,Y,Z) -> N64 (X,Z,Y)
                    needsInitialScale = true;
                    var data = '((' + traitName + 'Data*)data)';
                    return '$fn(&((ArmObject*)obj)->transform, ($x) * $data->_initialScale.x, ($z) * $data->_initialScale.y, ($y) * $data->_initialScale.z)';
                } else {
                    return '$fn(&((ArmObject*)obj)->transform, $x, $y, $z)';
                }

            default:
                return null;
        }
    }

    /**
     * Check if a string is a zero literal (0, 0.0, 0.0f)
     */
    function isZeroLiteral(s:String):Bool {
        return s == "0" || s == "0.0" || s == "0.0f";
    }
    /**
     * Check if a string is an input function call (input_down, input_started, input_released)
     */
    function isInputCall(s:String):Bool {
        return StringTools.startsWith(s, "input_down(") ||
               StringTools.startsWith(s, "input_started(") ||
               StringTools.startsWith(s, "input_released(");
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

    /**
     * Emit unary operation
     */
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

    /**
     * Emit field access - this is where API detection happens
     */
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

        // General field access
        var baseCode = emitExpr(e);

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

    /**
     * Emit gamepad field access: gamepad.leftStick.x -> input_stick_x()
     * Note: N64 only has one analog stick (the left stick).
     * rightStick doesn't exist on N64, so we map it to 1.0f as a constant multiplier.
     */
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
                // N64 has no right stick - return 1.0f as a neutral multiplier
                // This way expressions like `scaleSpeed * rightStick.y * dt` become `scaleSpeed * 1.0f * dt`
                return '0.0f';
            }
        }

        // Pattern: gamepad.leftStick or gamepad.rightStick (struct access - shouldn't happen)
        if (field == "leftStick" || field == "rightStick") {
            // Return placeholder that will be followed by .x/.y
            return field;
        }

        return '/* unsupported gamepad field: $field */';
    }

    /**
     * Emit transform field access with coordinate conversion
     */
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

    /**
     * Emit function call - main API mapping logic
     */
    function emitCall(e:Expr, params:Array<Expr>):String {
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

    /**
     * Get function name from call expression
     */
    function getFunctionName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            case EField(_, field): field;
            default: "";
        };
    }

    /**
     * Check if this is an Armory-internal call that should be skipped
     */
    function shouldSkipCall(name:String):Bool {
        return switch (name) {
            // Trait lifecycle registration (handled differently on N64)
            case "notifyOnInit", "notifyOnUpdate", "notifyOnRemove", "notifyOnLateUpdate": true;
            // Object casting/creation
            case "cast", "super": true;
            // Debug/logging
            case "trace", "log": true;
            default: false;
        };
    }

    /**
     * Detect if this is an API call (gamepad.down, transform.rotate, etc.)
     */
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
                                default: null;
                            }
                        } else null;
                }
            default: null;
        }
    }

    /**
     * Emit an API call with full resolution
     */
    function emitApiCall(category:String, method:String, params:Array<Expr>):String {
        var apiKey = '$category.$method';

        // Input class static methods - skip initialization (N64 input is always available)
        if (category == "Input") {
            return switch (method) {
                case "getGamepad", "getKeyboard", "getMouse": "";
                default: '/* unsupported: Input.$method */';
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

        // Fallback
        return '/* unsupported API: $apiKey */';
    }
    /**
     * Emit gamepad input call
     */
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

            // Track button usage
            if (!Lambda.has(inputButtons, n64Button)) {
                inputButtons.push(n64Button);
            }

            return '$n64Func($n64Button)';
        }

        return '$n64Func(N64_BTN_A)';
    }

    /**
     * Extract button name from expression
     */
    function extractButtonName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CString(s)): s;
            case EConst(CIdent(s)): s;
            case EField(_, field): field;  // e.g., Button.cross -> "cross"
            default: "a";
        }
    }

    /**
     * Emit transform call (rotate, translate, etc.)
     */
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
                return '/* transform.$method unsupported */';
        }
    }

    /**
     * Emit scale call with coordinate conversion
     */
    function emitScale(params:Array<Expr>):String {
        if (params.length == 0) return "/* scale needs args */";

        var first = params[0];
        switch (first.expr) {
            case EConst(CFloat(_)), EConst(CInt(_)):
                // scale(x, y, z)
                if (params.length >= 3) {
                    var x = emitExpr(params[0]);
                    var y = emitExpr(params[1]);
                    var z = emitExpr(params[2]);
                    // Scale: swap Y and Z (no negation needed for scale)
                    return 'it_set_scale(&((ArmObject*)obj)->transform, $x, $z, $y)';
                }
            default:
                // scale(vec) - assume Vec4-like with x, y, z fields
                var v = emitExpr(first);
                return 'it_set_scale(&((ArmObject*)obj)->transform, $v.x, $v.z, $v.y)';
        }
        return "/* scale: unsupported params */";
    }

    /**
     * Emit rotate call with axis resolution
     * Uses quaternion rotation via it_rotate_axis(transform, axis_x, axis_y, axis_z, angle)
     */
    function emitRotate(params:Array<Expr>):String {
        if (params.length < 2) return "/* rotate needs axis and angle */";

        var axisExpr = params[0];
        var angleExpr = params[1];

        // Resolve axis to N64 coordinates
        var axisInfo = resolveAxisVec(axisExpr);
        var angleCode = emitExpr(angleExpr);

        // Format floats with decimal point for C (1 -> 1.0f, not 1f)
        var xStr = floatToC(axisInfo.x);
        var yStr = floatToC(axisInfo.y);
        var zStr = floatToC(axisInfo.z);

        // Generate quaternion rotation call
        // it_rotate_axis handles the quaternion math internally
        return 'it_rotate_axis(&((ArmObject*)obj)->transform, $xStr, $yStr, $zStr, $angleCode)';
    }

    /**
     * Format a float for C code (ensures decimal point)
     */
    function floatToC(f:Float):String {
        var s = Std.string(f);
        // If no decimal point, add .0
        if (s.indexOf('.') == -1) {
            s += '.0';
        }
        return s + 'f';
    }

    /**
     * Resolve a Vec4 axis to N64 coordinate axis vector
     * Coordinate conversion: Blender (X,Y,Z) -> N64 (X, Z, -Y)
     */
    function resolveAxisVec(e:Expr):{x:Float, y:Float, z:Float} {
        // Look for Vec4(x,y,z) or iron.math.Vec4(x,y,z)
        switch (e.expr) {
            case ENew(_, params) | ECall(_, params):
                if (params.length >= 3) {
                    var bx = getConstFloat(params[0]);
                    var by = getConstFloat(params[1]);
                    var bz = getConstFloat(params[2]);

                    // Blender (X,Y,Z) -> N64 (X, Z, -Y)
                    return {x: bx, y: bz, z: -by};
                }
            case EField(_, field):
                // Vec4.xAxis(), etc.
                return switch (field) {
                    case "xAxis": {x: 1.0, y: 0.0, z: 0.0};
                    case "yAxis": {x: 0.0, y: 0.0, z: -1.0};  // Blender Y -> N64 -Z
                    case "zAxis": {x: 0.0, y: 1.0, z: 0.0};   // Blender Z -> N64 Y
                    default: {x: 0.0, y: 1.0, z: 0.0};
                }
            case EConst(CIdent(name)):
                // Member variable reference - look up its initialization expression
                if (vec4Exprs.exists(name)) {
                    return resolveAxisVec(vec4Exprs.get(name));
                }
            default:
        }

        return {x: 0.0, y: 1.0, z: 0.0};  // Default Y axis
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

    /**
     * Emit translate call with coordinate conversion
     */
    function emitTranslate(params:Array<Expr>):String {
        if (params.length == 0) return "/* translate needs args */";

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
                        // Blender (x,y,z) -> N64 (x,z,-y)
                        return 'it_translate(&((ArmObject*)obj)->transform, $x, $z, -($y))';
                    }
                default:
            }
            var v = emitExpr(vec);
            return 'it_translate(&((ArmObject*)obj)->transform, $v.x, $v.z, -($v.y))';
        }

        // Three separate arguments (already x, y, z)
        if (params.length >= 3) {
            var x = emitExpr(params[0]);
            var y = emitExpr(params[1]);
            var z = emitExpr(params[2]);
            // Blender (x,y,z) -> N64 (x,z,-y)
            return 'it_translate(&((ArmObject*)obj)->transform, $x, $z, -($y))';
        }

        return "/* translate: unsupported params */";
    }

    /**
     * Emit scene call
     */
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
                return '/* scene.$method unsupported */';
        }
    }

    /**
     * Get member variable name if expression is a simple identifier
     */
    function getMemberName(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(name)): name;
            default: null;
        }
    }

    /**
     * Extract scene name from expression
     */
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

    /**
     * Get the base identifier of a field chain
     */
    function getBaseIdent(e:Expr):String {
        return switch (e.expr) {
            case EConst(CIdent(s)): s;
            case EField(base, _): getBaseIdent(base);
            default: null;
        }
    }

    /**
     * Get the full field chain
     */
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

    // =============================================
    // Block / Control Flow Emission
    // =============================================

    function emitBlock(exprs:Array<Expr>):String {
        var lines:Array<String> = [];
        for (e in exprs) {
            var code = emitExpr(e);
            // Skip empty, whitespace-only, and unsupported expressions
            if (code != "" && StringTools.trim(code) != "" && code != "/* unsupported expr */") {
                lines.push(code);
            }
        }
        return lines.join(";\n") + (lines.length > 0 ? ";" : "");
    }

    function emitIf(econd:Expr, eif:Expr, eelse:Expr):String {
        var cond = emitExpr(econd);

        // If condition emits empty (skipped variable), skip the whole if
        if (cond == null || cond == "" || StringTools.trim(cond) == "" || cond.indexOf("/* unsupported") >= 0) {
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
        // For loops in Haxe are complex - simplify to while
        var bodyCode = emitExpr(body);
        return '/* for loop */ { $bodyCode; }';
    }

    function emitVars(vars:Array<Var>):String {
        var decls:Array<String> = [];
        for (v in vars) {
            localVars.set(v.name, true);
            var typeName = v.type != null ? N64Config.mapType(typeToString(v.type)) : "float";
            var init = v.expr != null ? ' = ${emitExpr(v.expr)}' : "";
            decls.push('$typeName ${v.name}$init');
        }
        return decls.join("; ");
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

    // =============================================
    // Public accessors for trait flags
    // =============================================

    public function requiresObj():Bool return needsObj;
    public function requiresDt():Bool return needsDt;
    public function getInputButtons():Array<String> return inputButtons;
    public function hasTransformOps():Bool return hasTransform;
    public function hasSceneOps():Bool return hasScene;
    public function getTargetScene():String return targetScene;
    public function requiresInitialScale():Bool return needsInitialScale;
}
#end
