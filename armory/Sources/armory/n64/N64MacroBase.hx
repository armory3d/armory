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
     * Convert a ComplexType to its string name (simplified).
     */
    public static function complexTypeToString(ct:ComplexType):String {
        return switch (ct) {
            case TPath(p): p.name;
            default: "Dynamic";
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
}

#end
