package armory.n64.util;

#if macro
import haxe.macro.Expr;

/**
 * Expression Utilities
 *
 * Common helper functions for working with Haxe macro expressions.
 * Reduces code duplication across converters and extractors.
 */
class ExprUtils {
    /**
     * Extract identifier name from an expression.
     * Handles both direct identifiers (x) and field access (this.x, obj.x).
     * Returns null if not an identifier pattern.
     */
    public static function extractIdentName(e:Expr):String {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CIdent(name)): return name;
            case EField(_, fieldName): return fieldName;
            default: return null;
        }
    }

    /**
     * Extract string literal from an expression.
     */
    public static function extractString(e:Expr):String {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CString(s)): return s;
            default: return null;
        }
    }

    /**
     * Extract integer literal from an expression.
     */
    public static function extractInt(e:Expr):Null<Int> {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CInt(v)): return Std.parseInt(v);
            default: return null;
        }
    }

    /**
     * Extract float literal from an expression.
     */
    public static function extractFloat(e:Expr):Null<Float> {
        if (e == null) return null;
        switch (e.expr) {
            case EConst(CFloat(v)): return Std.parseFloat(v);
            case EConst(CInt(v)): return Std.parseInt(v);
            default: return null;
        }
    }

    /**
     * Check if expression is a specific identifier.
     */
    public static function isIdent(e:Expr, name:String):Bool {
        if (e == null) return false;
        switch (e.expr) {
            case EConst(CIdent(n)): return n == name;
            default: return false;
        }
    }

    /**
     * Check if expression is a field access on a specific object.
     * E.g., isFieldOn(expr, "this", "x") returns true for `this.x`
     */
    public static function isFieldOn(e:Expr, objName:String, fieldName:String):Bool {
        if (e == null) return false;
        switch (e.expr) {
            case EField(obj, field):
                if (field != fieldName) return false;
                switch (obj.expr) {
                    case EConst(CIdent(n)): return n == objName;
                    default: return false;
                }
            default: return false;
        }
    }

    /**
     * Get the object part of a field access expression.
     * Returns null if not a field access.
     */
    public static function getFieldObject(e:Expr):Expr {
        if (e == null) return null;
        switch (e.expr) {
            case EField(obj, _): return obj;
            default: return null;
        }
    }

    /**
     * Get the field name of a field access expression.
     * Returns null if not a field access.
     */
    public static function getFieldName(e:Expr):String {
        if (e == null) return null;
        switch (e.expr) {
            case EField(_, field): return field;
            default: return null;
        }
    }
}
#end
