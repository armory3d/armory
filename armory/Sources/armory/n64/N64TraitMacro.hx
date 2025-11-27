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

        // Process each field
        for (field in fields) {
            switch (field.kind) {
                case FVar(t, e):
                    // Member variable
                    var memberInfo = extractMember(field.name, t, e);
                    if (memberInfo != null) {
                        traitInfo.members.push(memberInfo);
                    }

                case FFun(func):
                    // Function - check if it's new() constructor
                    if (field.name == "new") {
                        // Analyze constructor for notifyOn* calls
                        analyzeConstructor(func, traitInfo);
                    }

                case FProp(_, _, _, _):
                    // Property - skip for now
            }
        }

        // Store trait data
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
     * Analyze constructor for notifyOn* calls and extract function bodies.
     */
    static function analyzeConstructor(func:Function, traitInfo:Dynamic):Void {
        if (func.expr == null) return;

        // Walk the expression tree looking for notifyOn* calls
        walkExpr(func.expr, traitInfo);
    }

    /**
     * Recursively walk expression tree.
     */
    static function walkExpr(expr:Expr, traitInfo:Dynamic):Void {
        if (expr == null) return;

        switch (expr.expr) {
            case ECall(e, params):
                // Check if this is a notifyOn* call
                analyzeCall(e, params, traitInfo);
                // Also walk params
                for (p in params) {
                    walkExpr(p, traitInfo);
                }

            case EBlock(exprs):
                for (e in exprs) {
                    walkExpr(e, traitInfo);
                }

            case EIf(econd, eif, eelse):
                walkExpr(econd, traitInfo);
                walkExpr(eif, traitInfo);
                if (eelse != null) walkExpr(eelse, traitInfo);

            case EWhile(econd, e, _):
                walkExpr(econd, traitInfo);
                walkExpr(e, traitInfo);

            case EFor(it, e):
                walkExpr(it, traitInfo);
                walkExpr(e, traitInfo);

            case EFunction(_, f):
                // Inline function - analyze its body
                if (f.expr != null) {
                    walkExpr(f.expr, traitInfo);
                }

            default:
                // Continue walking
        }
    }

    /**
     * Analyze a function call expression.
     */
    static function analyzeCall(callExpr:Expr, params:Array<Expr>, traitInfo:Dynamic):Void {
        // Get the function name being called
        var callName = getCallName(callExpr);

        switch (callName) {
            case "notifyOnInit":
                if (params.length > 0) {
                    traitInfo.functions.init = extractFunctionBody(params[0], traitInfo);
                }
            case "notifyOnUpdate":
                if (params.length > 0) {
                    traitInfo.functions.update = extractFunctionBody(params[0], traitInfo);
                }
            case "notifyOnRemove":
                if (params.length > 0) {
                    traitInfo.functions.remove = extractFunctionBody(params[0], traitInfo);
                }
            default:
                // API call tracking now happens in extractStatements/exprToStatement
                // to avoid duplicate tracking
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
     * Extract function body as statement list.
     */
    static function extractFunctionBody(expr:Expr, traitInfo:Dynamic):Array<Dynamic> {
        var statements:Array<Dynamic> = [];

        switch (expr.expr) {
            case EFunction(_, f):
                if (f.expr != null) {
                    extractStatements(f.expr, statements, traitInfo);
                }
            default:
        }

        return statements;
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
     */
    static function getFullCallPath(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CIdent(name)):
                return name;
            case EField(e, field):
                var parent = getFullCallPath(e);
                return parent + "." + field;
            default:
                return "";
        }
    }

    /**
     * Get full dot-separated field access path.
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
