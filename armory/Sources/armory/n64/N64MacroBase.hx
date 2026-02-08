package armory.n64;

#if macro
import haxe.macro.Context;
import haxe.macro.Expr;
import haxe.Json;
import sys.io.File;
import sys.FileSystem;

import armory.n64.IRTypes;

/**
 * N64 Macro Base - Shared Utilities
 *
 * Contains common functionality used by both N64TraitMacro and N64AutoloadMacro:
 * - IR node serialization
 * - Binary/unary operator conversion
 * - Type conversion utilities
 * - JSON output helpers
 *
 * This reduces code duplication between the two macro files.
 */
class N64MacroBase {
    // Global audio configuration (set by AudioCallConverter when Aura.init() is found)
    public static var audioConfig:Dynamic = {};

    /**
     * Serialize an IRNode to a Dynamic object for JSON output.
     */
    public static function serializeIRNode(node:IRNode):Dynamic {
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
        if (node.cName != null) obj.cName = node.cName;
        if (node.trait != null) obj.trait = node.trait;
        if (node.parent != null) obj.parent = node.parent;
        // Inherited member fields
        if (node.memberType != null) obj.memberType = node.memberType;
        if (node.owner != null) obj.owner = node.owner;
        // Callback parameter call fields
        if (node.name != null) obj.name = node.name;
        if (node.paramType != null) obj.paramType = node.paramType;
        // Callback wrapper fields (for inherited method callbacks)
        if (node.callback_name != null) obj.callback_name = node.callback_name;
        if (node.body != null && node.body.length > 0) {
            obj.body = [for (b in node.body) serializeIRNode(b)];
        }
        if (node.captures != null) obj.captures = node.captures;
        if (node.param_name != null) obj.param_name = node.param_name;
        if (node.param_type != null) obj.param_type = node.param_type;
        if (node.param_ctype != null) obj.param_ctype = node.param_ctype;

        return obj;
    }

    /**
     * Convert a Haxe binary operator to its C string representation.
     */
    public static function binopToString(op:Binop):String {
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
            case OpAssignOp(innerOp): binopToString(innerOp) + "=";
            default: "?";
        };
    }

    /**
     * Convert a Haxe unary operator to its C string representation.
     */
    public static function unopToString(op:Unop):String {
        return switch (op) {
            case OpNeg: "-";
            case OpNot: "!";
            case OpNegBits: "~";  // Bitwise NOT
            case OpIncrement: "++";
            case OpDecrement: "--";
            case OpSpread: "..."; // Should not appear in N64 code
        };
    }

    /**
     * Convert a ComplexType to its string name (including type parameters).
     * E.g., Array<BaseChannelHandle> -> "Array<BaseChannelHandle>"
     *       Map<String, Array<Int>> -> "Map<String, Array<Int>>"
     */
    public static function complexTypeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p):
                if (p.params == null || p.params.length == 0) {
                    p.name;
                } else {
                    // Build parameterized type string: Name<Param1, Param2>
                    var paramStrings = [for (tp in p.params) typeParamToString(tp)];
                    p.name + "<" + paramStrings.join(", ") + ">";
                }
            case TFunction(args, ret):
                // Handle function types like Void->Void, Float->Void
                var argTypes = [for (arg in args) complexTypeToString(arg)];
                var retType = complexTypeToString(ret);
                if (argTypes.length == 0) {
                    "Void->" + retType;
                } else {
                    argTypes.join("->") + "->" + retType;
                }
            default: "Dynamic";
        };
    }

    /**
     * Convert a TypeParam to string.
     */
    static function typeParamToString(tp:TypeParam):String {
        return switch (tp) {
            case TPType(ct): complexTypeToString(ct);
            case TPExpr(e): "Dynamic"; // Expression type params not supported
        };
    }

    /**
     * Write JSON data to a file in the build directory.
     * Creates the directory if it doesn't exist.
     */
    public static function writeJsonFile(filename:String, data:Dynamic):Void {
        var json = Json.stringify(data, null, "  ");

        var defines = Context.getDefines();
        var buildDir = defines.get("arm_build_dir");
        if (buildDir == null) buildDir = "build";

        var outPath = buildDir + "/" + filename;
        try {
            var dir = haxe.io.Path.directory(outPath);
            if (dir != "" && !FileSystem.exists(dir)) {
                FileSystem.createDirectory(dir);
            }
            File.saveContent(outPath, json);
        } catch (e:Dynamic) {
            Context.error('Failed to write $filename: $e', Context.currentPos());
        }
    }

    /**
     * Convert a constant expression to its IR node representation.
     */
    public static function constToIR(c:Constant):IRNode {
        return switch (c) {
            case CInt(v): { type: "int", value: Std.parseInt(v) };
            case CFloat(f): { type: "float", value: Std.parseFloat(f) };
            case CString(s): { type: "string", value: s };
            case CIdent("true"): { type: "bool", value: true };
            case CIdent("false"): { type: "bool", value: false };
            case CIdent("null"): { type: "null" };
            case CIdent("this"): { type: "ident", value: "this" };
            case CIdent("object"): { type: "ident", value: "object" };
            case CIdent(name): { type: "ident", value: name };
            default: { type: "skip" };
        };
    }

    /**
     * Generate struct_type and struct_def for signals with 2+ arguments.
     *
     * For signals that pass multiple arguments, we generate a payload struct:
     *   typedef struct {
     *       int32_t arg0;
     *       float arg1;
     *   } traitname_signalname_payload_t;
     *
     * @param signals Array of SignalMeta from IR
     * @param cName The C-style name prefix (e.g., "arm_node_player")
     */
    public static function generateSignalStructs(signals:Array<SignalMeta>, cName:String):Void {
        for (sig in signals) {
            var argCount = sig.arg_types.length;
            if (argCount >= 2) {
                sig.struct_type = '${cName}_${sig.name}_payload_t';
                var lines:Array<String> = ['typedef struct {'];
                for (i in 0...argCount) {
                    lines.push('    ${sig.arg_types[i]} arg$i;');
                }
                lines.push('} ${sig.struct_type};');
                sig.struct_def = lines.join('\n');
            }
        }
    }

    /**
     * Generate preamble code for signal handlers.
     *
     * The preamble extracts the payload and sets up local variables:
     * - 0 args: "(void)payload;"
     * - 1 arg:  "int32_t arg0 = (int32_t)(uintptr_t)payload;"
     * - 2+ args: Unpack from struct pointer
     *
     * @param signalHandlers Array of SignalHandlerMeta from IR
     * @param signals Array of SignalMeta to lookup arg types
     * @param dataType The data struct type name (e.g., "PlayerData")
     */
    public static function generateSignalHandlerPreambles(
        signalHandlers:Array<SignalHandlerMeta>,
        signals:Array<SignalMeta>,
        dataType:String
    ):Void {
        for (sh in signalHandlers) {
            // Find the signal this handler connects to
            for (sig in signals) {
                if (sig.name == sh.signal_name) {
                    var argTypes = sig.arg_types;
                    var argCount = argTypes.length;

                    // Cast ctx to data pointer so handler body can use 'data'
                    var dataCast = '$dataType* data = ($dataType*)ctx;';

                    if (argCount == 0) {
                        sh.preamble = '$dataCast (void)payload;';
                    } else if (argCount == 1) {
                        sh.preamble = '$dataCast ${argTypes[0]} arg0 = (${argTypes[0]})(uintptr_t)payload; (void)arg0;';
                    } else {
                        // Multiple args - unpack from struct
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
    }
}

#end
