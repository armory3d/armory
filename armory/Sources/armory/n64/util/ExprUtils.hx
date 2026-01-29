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
}
#end
