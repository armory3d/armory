package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;

/**
 * Interface for call converters.
 *
 * Each converter handles a specific category of method calls
 * (Scene, Canvas, Physics, Math, etc.) and converts them to IR nodes.
 */
interface ICallConverter {
    /**
     * Attempt to convert a method call to an IR node.
     *
     * @param obj The object expression the method is called on
     * @param method The method name being called
     * @param args Pre-converted IR nodes for arguments
     * @param rawParams Original Haxe expressions for arguments (for special handling)
     * @param ctx The extractor context for accessing shared state
     * @return IR node if this converter handles the call, null otherwise
     */
    function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode;
}

/**
 * Context interface that converters use to access shared extraction state.
 * This decouples converters from TraitExtractor implementation details.
 */
interface IExtractorContext {
    // Convert an expression to IR
    function exprToIR(e:Expr):IRNode;

    // Get the Haxe type of an expression
    function getExprType(e:Expr):String;

    // Extract a string literal from an expression
    function extractStringArg(e:Expr):String;

    // Get trait metadata (for setting flags like uses_physics, uses_input)
    function getMeta():TraitMeta;

    // Access to member types (for type checking)
    function getMemberType(name:String):String;

    // Get C-safe trait name (for generating handler names)
    function getCName():String;

    // Method lookup (for extracting handler bodies)
    function getMethod(name:String):haxe.macro.Expr.Function;

    // Events map access (for contact/signal handlers)
    function getEvents():Map<String, Array<IRNode>>;

    // Add a signal handler for extraction
    function addSignalHandler(callbackName:String, signalName:String):Void;

    // Update signal arg types from emit() call
    function updateSignalArgTypes(signalName:String, params:Array<Expr>):Void;

    // Infer expression type (for signal arg types)
    function inferExprType(e:Expr):String;
}
#end

