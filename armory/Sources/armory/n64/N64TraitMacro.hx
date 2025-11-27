package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;
import haxe.macro.Type;
import sys.io.File;
import sys.FileSystem;
import haxe.Json;

/**
 * Build macro that extracts trait metadata for N64 code generation.
 *
 * This macro runs at compile-time on all classes extending iron.Trait
 * when the arm_target_n64 flag is defined. It extracts:
 * - Member variables (name, type, default value)
 * - Lifecycle functions (init, update, remove)
 * - API calls (Transform, Input, Scene, Time)
 *
 * Output is written to the build directory as JSON for the Python exporter.
 */
class N64TraitMacro {
    // Accumulated trait data across all processed traits
    static var traitData:Map<String, Dynamic> = new Map();
    static var initialized:Bool = false;

    /**
     * Build macro entry point - called for each class extending Trait.
     */
    macro public static function build():Array<Field> {
        // Initialize on first call
        if (!initialized) {
            initialized = true;
            // Register callback to write JSON after all types are processed
            Context.onAfterTyping(function(_) {
                writeTraitJson();
            });
        }

        var localClass = Context.getLocalClass();
        if (localClass == null) return null;

        var cls = localClass.get();
        var className = cls.name;
        var modulePath = cls.module;

        // Skip Iron/Armory internal traits
        if (modulePath.indexOf("iron.") == 0 || modulePath.indexOf("armory.trait.internal") == 0) {
            return null;
        }

        // Get build fields
        var fields = Context.getBuildFields();

        // Extract trait info
        var traitInfo:Dynamic = {
            name: className,
            module: modulePath,
            members: [],
            functions: {
                init: null,
                update: null,
                remove: null
            },
            apiCalls: {
                input: [],
                transform: [],
                scene: [],
                time: false
            }
        };

        // Build a map of field name -> function for method reference lookups
        var methodMap:Map<String, Function> = new Map();
        for (field in fields) {
            switch (field.kind) {
                case FFun(func):
                    methodMap.set(field.name, func);
                default:
            }
        }

        // Track which methods are registered to which lifecycle
        var lifecycleRegistrations:Map<String, String> = new Map();

        // PASS 1: Process fields - extract members and find lifecycle registrations
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    // Member variable
                    var memberInfo = extractMember(field.name, t, e);
                    if (memberInfo != null) {
                        traitInfo.members.push(memberInfo);
                    }

                case FFun(func):
                    // Analyze constructor for notifyOn* calls (both inline and method refs)
                    if (field.name == "new") {
                        analyzeForRegistrations(func.expr, traitInfo, lifecycleRegistrations, methodMap);
                    }

                case FProp(_, _, _, _):
                    // Property - skip for now
            }
        }

        // PASS 2: Process registered method bodies
        // This handles both method references AND finds chained registrations
        var processedMethods:Map<String, Bool> = new Map();
        var methodsToProcess:Array<String> = [];

        // Collect initial methods to process
        for (methodName in lifecycleRegistrations.keys()) {
            if (!processedMethods.exists(methodName)) {
                methodsToProcess.push(methodName);
            }
        }

        // Process methods (may discover more via chained registrations)
        while (methodsToProcess.length > 0) {
            var methodName = methodsToProcess.shift();
            if (processedMethods.exists(methodName)) continue;
            processedMethods.set(methodName, true);

            var func = methodMap.get(methodName);
            if (func == null || func.expr == null) continue;

            var lifecycle = lifecycleRegistrations.get(methodName);
            if (lifecycle != null) {
                // Extract method body as statements
                var statements:Array<Dynamic> = [];
                extractStatements(func.expr, statements, traitInfo);

                // Store in the appropriate lifecycle slot
                switch (lifecycle) {
                    case "init":
                        if (traitInfo.functions.init == null) {
                            traitInfo.functions.init = statements;
                        }
                    case "update":
                        if (traitInfo.functions.update == null) {
                            traitInfo.functions.update = statements;
                        }
                    case "remove":
                        if (traitInfo.functions.remove == null) {
                            traitInfo.functions.remove = statements;
                        }
                }
            }

            // Look for chained registrations inside this method
            var newRegistrations:Map<String, String> = new Map();
            analyzeForRegistrations(func.expr, traitInfo, newRegistrations, methodMap);

            // Add newly discovered methods to process queue
            for (newMethod in newRegistrations.keys()) {
                if (!processedMethods.exists(newMethod) && !lifecycleRegistrations.exists(newMethod)) {
                    lifecycleRegistrations.set(newMethod, newRegistrations.get(newMethod));
                    methodsToProcess.push(newMethod);
                }
            }
        }

        // Store trait data by class name (Blender looks up by class name)
        // Module path is stored inside traitInfo for disambiguation if needed
        traitData.set(className, traitInfo);

        // Return null = don't modify fields
        return null;
    }

    /**
     * Extract member variable info.
     */
    static function extractMember(name:String, type:Null<ComplexType>, expr:Null<Expr>):Dynamic {
        // Skip private/internal members
        if (name.charAt(0) == "_" || name.charAt(0) == "$") {
            return null;
        }

        // Skip inherited members from Trait
        var skipMembers = ["object", "name", "_add", "_init", "_remove", "_update", "_lateUpdate", "_fixedUpdate", "_render", "_render2D"];
        if (skipMembers.indexOf(name) >= 0) {
            return null;
        }

        var typeStr = complexTypeToString(type);

        // Map Haxe types to C types - only support simple primitives for N64
        var ctypeMap:Map<String, String> = [
            "Float" => "float",
            "Int" => "int32_t",
            "Bool" => "bool"
        ];

        var ctype = ctypeMap.get(typeStr);
        if (ctype == null) {
            return null;  // Unsupported type
        }

        var defaultValue:Dynamic = null;
        if (expr != null) {
            defaultValue = extractConstValue(expr);
        }

        return {
            name: name,
            type: typeStr,
            ctype: ctype,
            defaultValue: defaultValue
        };
    }

    /**
     * Convert ComplexType to string representation.
     */
    static function complexTypeToString(type:Null<ComplexType>):String {
        if (type == null) return "Dynamic";

        switch (type) {
            case TPath(p):
                return p.name;
            default:
                return "Dynamic";
        }
    }

    /**
     * Extract constant value from expression.
     */
    static function extractConstValue(expr:Expr):Dynamic {
        if (expr == null) return null;

        switch (expr.expr) {
            case EConst(c):
                switch (c) {
                    case CInt(v): return Std.parseInt(v);
                    case CFloat(v): return Std.parseFloat(v);
                    case CString(v, _): return v;
                    case CIdent(v):
                        if (v == "true") return true;
                        if (v == "false") return false;
                        return null;
                    default: return null;
                }
            case EUnop(OpNeg, false, e):
                // Handle negative numbers
                var val = extractConstValue(e);
                if (val != null && Std.isOfType(val, Float)) {
                    return -cast(val, Float);
                }
                return null;
            default:
                return null;
        }
    }

    /**
     * Analyze expression tree for notifyOn* registrations.
     * Handles both inline functions and method references.
     * Inline functions are extracted immediately; method references are recorded for later processing.
     */
    static function analyzeForRegistrations(expr:Expr, traitInfo:Dynamic, registrations:Map<String, String>, methodMap:Map<String, Function>):Void {
        if (expr == null) return;

        switch (expr.expr) {
            case ECall(e, params):
                var callName = getCallName(e);

                // Check for notifyOn* registration calls
                var lifecycle:String = null;
                switch (callName) {
                    case "notifyOnInit": lifecycle = "init";
                    case "notifyOnUpdate": lifecycle = "update";
                    case "notifyOnRemove": lifecycle = "remove";
                    default:
                }

                if (lifecycle != null && params.length > 0) {
                    var param = params[0];
                    switch (param.expr) {
                        case EFunction(_, f):
                            // Inline function - extract immediately
                            if (f.expr != null) {
                                var statements:Array<Dynamic> = [];
                                extractStatements(f.expr, statements, traitInfo);

                                // Store in the appropriate lifecycle slot
                                switch (lifecycle) {
                                    case "init":
                                        if (traitInfo.functions.init == null) {
                                            traitInfo.functions.init = statements;
                                        }
                                    case "update":
                                        if (traitInfo.functions.update == null) {
                                            traitInfo.functions.update = statements;
                                        }
                                    case "remove":
                                        if (traitInfo.functions.remove == null) {
                                            traitInfo.functions.remove = statements;
                                        }
                                }

                                // Also scan the inline function for chained registrations
                                analyzeForRegistrations(f.expr, traitInfo, registrations, methodMap);
                            }

                        case EConst(CIdent(methodName)):
                            // Method reference like: notifyOnUpdate(update)
                            registrations.set(methodName, lifecycle);

                        case EField(_, methodName):
                            // Method reference like: notifyOnUpdate(this.update)
                            registrations.set(methodName, lifecycle);

                        default:
                    }
                }

                // Continue walking params
                for (p in params) {
                    analyzeForRegistrations(p, traitInfo, registrations, methodMap);
                }

            case EBlock(exprs):
                for (e in exprs) {
                    analyzeForRegistrations(e, traitInfo, registrations, methodMap);
                }

            case EIf(econd, eif, eelse):
                analyzeForRegistrations(econd, traitInfo, registrations, methodMap);
                analyzeForRegistrations(eif, traitInfo, registrations, methodMap);
                if (eelse != null) analyzeForRegistrations(eelse, traitInfo, registrations, methodMap);

            case EWhile(econd, e, _):
                analyzeForRegistrations(econd, traitInfo, registrations, methodMap);
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case EFor(it, e):
                analyzeForRegistrations(it, traitInfo, registrations, methodMap);
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case EFunction(_, f):
                // Inline function inside expression
                if (f.expr != null) {
                    analyzeForRegistrations(f.expr, traitInfo, registrations, methodMap);
                }

            case EParenthesis(e):
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case ETernary(econd, eif, eelse):
                analyzeForRegistrations(econd, traitInfo, registrations, methodMap);
                analyzeForRegistrations(eif, traitInfo, registrations, methodMap);
                analyzeForRegistrations(eelse, traitInfo, registrations, methodMap);

            case EBinop(_, e1, e2):
                analyzeForRegistrations(e1, traitInfo, registrations, methodMap);
                analyzeForRegistrations(e2, traitInfo, registrations, methodMap);

            case EUnop(_, _, e):
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case EField(e, _):
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case EArray(e1, e2):
                analyzeForRegistrations(e1, traitInfo, registrations, methodMap);
                analyzeForRegistrations(e2, traitInfo, registrations, methodMap);

            case EArrayDecl(values):
                for (v in values) {
                    analyzeForRegistrations(v, traitInfo, registrations, methodMap);
                }

            case ENew(_, params):
                for (p in params) {
                    analyzeForRegistrations(p, traitInfo, registrations, methodMap);
                }

            case EReturn(e):
                if (e != null) analyzeForRegistrations(e, traitInfo, registrations, methodMap);

            case ESwitch(e, cases, edef):
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);
                for (c in cases) {
                    if (c.expr != null) analyzeForRegistrations(c.expr, traitInfo, registrations, methodMap);
                }
                if (edef != null) analyzeForRegistrations(edef, traitInfo, registrations, methodMap);

            case ETry(e, catches):
                analyzeForRegistrations(e, traitInfo, registrations, methodMap);
                for (c in catches) {
                    analyzeForRegistrations(c.expr, traitInfo, registrations, methodMap);
                }

            case EVars(vars):
                for (v in vars) {
                    if (v.expr != null) analyzeForRegistrations(v.expr, traitInfo, registrations, methodMap);
                }

            default:
                // No sub-expressions to walk
        }
    }

    /**
     * Get the name of a function being called.
     */
    static function getCallName(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CIdent(name)):
                return name;
            case EField(_, field):
                return field;
            default:
                return "";
        }
    }

    /**
     * Extract statements from expression block.
     */
    static function extractStatements(expr:Expr, statements:Array<Dynamic>, traitInfo:Dynamic):Void {
        switch (expr.expr) {
            case EBlock(exprs):
                for (e in exprs) {
                    var stmt = exprToStatement(e, traitInfo);
                    if (stmt != null) {
                        statements.push(stmt);
                    }
                }
            default:
                var stmt = exprToStatement(expr, traitInfo);
                if (stmt != null) {
                    statements.push(stmt);
                }
        }
    }

    /**
     * Convert an expression to a statement representation.
     */
    static function exprToStatement(expr:Expr, traitInfo:Dynamic):Dynamic {
        switch (expr.expr) {
            case ECall(e, params):
                return analyzeStatementCall(e, params, traitInfo);

            case EIf(econd, eif, eelse):
                var condStmt = exprToStatement(econd, traitInfo);
                var thenStmts:Array<Dynamic> = [];
                extractStatements(eif, thenStmts, traitInfo);
                var elseStmts:Array<Dynamic> = null;
                if (eelse != null) {
                    elseStmts = [];
                    extractStatements(eelse, elseStmts, traitInfo);
                }
                return {
                    type: "if",
                    condition: condStmt,
                    then: thenStmts,
                    else_: elseStmts
                };

            case EBinop(op, e1, e2):
                return {
                    type: "binop",
                    op: binopToString(op),
                    left: exprToStatement(e1, traitInfo),
                    right: exprToStatement(e2, traitInfo)
                };

            case EField(e, field):
                var obj = exprToStatement(e, traitInfo);
                // Check for Time API field access (e.g., Time.delta)
                var fullPath = getFieldAccessPath(expr);
                if (fullPath.indexOf("Time.") == 0) {
                    traitInfo.apiCalls.time = true;
                }
                return {
                    type: "field",
                    object: obj,
                    field: field
                };

            case EConst(c):
                switch (c) {
                    case CIdent(name):
                        return {type: "ident", name: name};
                    case CInt(v):
                        return {type: "int", value: Std.parseInt(v)};
                    case CFloat(v):
                        return {type: "float", value: Std.parseFloat(v)};
                    case CString(v, _):
                        return {type: "string", value: v};
                    default:
                        return null;
                }

            case ENew(t, params):
                var args:Array<Dynamic> = [];
                for (p in params) {
                    args.push(exprToStatement(p, traitInfo));
                }
                return {
                    type: "new",
                    typeName: t.name,
                    args: args
                };

            case EParenthesis(e):
                // Unwrap parenthesized expression - e.g., (object.getChild("x")).transform
                return exprToStatement(e, traitInfo);

            case EUnop(op, postFix, e):
                var operand = exprToStatement(e, traitInfo);
                return {
                    type: "unop",
                    op: unopToString(op),
                    postFix: postFix,
                    expr: operand
                };

            case EArray(e1, e2):
                // Array access like arr[i]
                return {
                    type: "array_access",
                    array: exprToStatement(e1, traitInfo),
                    index: exprToStatement(e2, traitInfo)
                };

            case EArrayDecl(values):
                var elements:Array<Dynamic> = [];
                for (v in values) {
                    elements.push(exprToStatement(v, traitInfo));
                }
                return {
                    type: "array",
                    elements: elements
                };

            case ETernary(econd, eif, eelse):
                return {
                    type: "ternary",
                    condition: exprToStatement(econd, traitInfo),
                    then: exprToStatement(eif, traitInfo),
                    else_: exprToStatement(eelse, traitInfo)
                };

            case EVars(vars):
                // Variable declarations
                var varDecls:Array<Dynamic> = [];
                for (v in vars) {
                    varDecls.push({
                        name: v.name,
                        expr: v.expr != null ? exprToStatement(v.expr, traitInfo) : null
                    });
                }
                return {
                    type: "vars",
                    vars: varDecls
                };

            default:
                return null;
        }
    }

    /**
     * Analyze a statement-level call (not notifyOn*).
     */
    static function analyzeStatementCall(callExpr:Expr, params:Array<Expr>, traitInfo:Dynamic):Dynamic {
        // Build full call path
        var path = getFullCallPath(callExpr);
        var args:Array<Dynamic> = [];
        for (p in params) {
            args.push(exprToStatement(p, traitInfo));
        }

        // Track API calls for the summary
        if (path.indexOf("Gamepad") >= 0 || path.indexOf("Keyboard") >= 0 || path.indexOf("Mouse") >= 0) {
            var inputCall = {
                type: getCallName(callExpr),
                args: args
            };
            traitInfo.apiCalls.input.push(inputCall);
        } else if (path.indexOf("transform") >= 0 || path.indexOf("Transform") >= 0) {
            var transformCall = {
                method: getCallName(callExpr),
                args: args
            };
            traitInfo.apiCalls.transform.push(transformCall);
        } else if (path.indexOf("Scene") >= 0) {
            var sceneCall = {
                method: getCallName(callExpr),
                args: args
            };
            traitInfo.apiCalls.scene.push(sceneCall);
        } else if (path.indexOf("Time") >= 0) {
            traitInfo.apiCalls.time = true;
        }

        return {
            type: "call",
            path: path,
            args: args
        };
    }

    /**
     * Get full dot-separated call path.
     * Handles parenthesized expressions like (object.getChild("x")).transform.rotate()
     */
    static function getFullCallPath(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CIdent(name)):
                return name;
            case EField(e, field):
                var parent = getFullCallPath(e);
                if (parent.length > 0) {
                    return parent + "." + field;
                }
                return field;
            case EParenthesis(e):
                return getFullCallPath(e);
            case ECall(e, _):
                // For chained calls like obj.getChild("x").transform
                return getFullCallPath(e);
            default:
                return "";
        }
    }

    /**
     * Get full dot-separated field access path.
     * Handles parenthesized expressions.
     */
    static function getFieldAccessPath(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CIdent(name)):
                return name;
            case EField(e, field):
                var parent = getFieldAccessPath(e);
                if (parent.length > 0) {
                    return parent + "." + field;
                }
                return field;
            case EParenthesis(e):
                return getFieldAccessPath(e);
            default:
                return "";
        }
    }

    /**
     * Convert binary operator to string.
     */
    static function binopToString(op:Binop):String {
        return switch (op) {
            case OpAdd: "+";
            case OpSub: "-";
            case OpMult: "*";
            case OpDiv: "/";
            case OpMod: "%";
            case OpEq: "==";
            case OpNotEq: "!=";
            case OpGt: ">";
            case OpGte: ">=";
            case OpLt: "<";
            case OpLte: "<=";
            case OpAnd: "&&";
            case OpOr: "||";
            case OpAssign: "=";
            case OpAssignOp(subOp): binopToString(subOp) + "=";
            default: "?";
        };
    }

    /**
     * Convert unary operator to string.
     */
    static function unopToString(op:Unop):String {
        return switch (op) {
            case OpNot: "!";
            case OpNeg: "-";
            case OpNegBits: "~";
            case OpIncrement: "++";
            case OpDecrement: "--";
            case OpSpread: "...";
        };
    }

    /**
     * Write collected trait data to JSON file.
     */
    static function writeTraitJson():Void {
        if (traitData.keys().hasNext() == false) {
            return;
        }

        // Convert map to object for JSON
        var output:Dynamic = {
            version: 1,
            traits: {}
        };

        for (name in traitData.keys()) {
            Reflect.setField(output.traits, name, traitData.get(name));
        }

        // Get output path from compiler defines or use default
        var outputDir = ".";
        var defines = Context.getDefines();
        if (defines.exists("arm_build_dir")) {
            outputDir = defines.get("arm_build_dir");
        }

        var outputPath = outputDir + "/n64_traits.json";

        // Ensure directory exists
        var dir = haxe.io.Path.directory(outputPath);
        if (dir != "" && !FileSystem.exists(dir)) {
            FileSystem.createDirectory(dir);
        }

        // Write JSON
        var jsonStr = Json.stringify(output, null, "  ");
        File.saveContent(outputPath, jsonStr);

        Context.info("N64 trait metadata written to: " + outputPath, Context.currentPos());
    }
}
#end
