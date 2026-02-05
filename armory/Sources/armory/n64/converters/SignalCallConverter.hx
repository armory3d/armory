package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import armory.n64.IRTypes;
import armory.n64.mapping.TypeMap;
import armory.n64.converters.ICallConverter;
import armory.n64.util.ExprUtils;

/**
 * Converts Signal method calls to C signal_* functions.
 * Handles: connect, disconnect, emit for both instance and global signals.
 * Supports both named function references and anonymous inline functions.
 */
class SignalCallConverter implements ICallConverter {
    static var anonCounter:Int = 0;

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Only handle Signal methods
        if (method != "connect" && method != "disconnect" && method != "emit") {
            return null;
        }

        // Check if object is a Signal type
        var objType = ctx.getExprType(obj);
        if (objType == "Signal") {
            return convertSignalCall(method, obj, args, rawParams, ctx);
        }

        // Check memberTypes directly for this.signalName pattern
        var memberName = ExprUtils.extractIdentName(obj);

        if (memberName != null && ctx.getMemberType(memberName) == "Signal") {
            return convertSignalCall(method, obj, args, rawParams, ctx);
        }

        // Check for global signal pattern: ClassName.signalName.method()
        switch (obj.expr) {
            case EField(classExpr, signalName):
                switch (classExpr.expr) {
                    case EConst(CIdent(className)):
                        // This is ClassName.signalName.method() - global signal
                        return convertGlobalSignalCall(method, className, signalName, args, rawParams, ctx);
                    default:
                }
            default:
        }

        return null;
    }

    function convertSignalCall(method:String, signalExpr:Expr, args:Array<IRNode>, params:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Get the signal member name from the expression
        var signalName = ExprUtils.extractIdentName(signalExpr);

        if (signalName == null) {
            return { type: "skip" };
        }

        switch (method) {
            case "connect":
                if (params.length > 0) {
                    // Try to extract as named function reference first
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        ctx.addSignalHandler(callbackName, signalName);
                        return {
                            type: "signal_call",
                            value: "connect",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                signal_name: signalName,
                                callback: callbackName
                            }
                        };
                    }

                    // Check for anonymous function
                    var anonResult = extractAnonymousCallback(params[0], signalName, ctx);
                    if (anonResult != null) {
                        ctx.addSignalHandler(anonResult.callbackName, signalName);
                        return {
                            type: "signal_call",
                            value: "connect",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                signal_name: signalName,
                                callback: anonResult.callbackName,
                                inline_callback: anonResult.inlineCallback
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "disconnect":
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        return {
                            type: "signal_call",
                            value: "disconnect",
                            c_code: 'signal_disconnect({signal_ptr}, {handler});',
                            props: {
                                signal_name: signalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "emit":
                ctx.updateSignalArgTypes(signalName, params);
                var argCount = params.length;

                var c_code:String;
                if (argCount == 0) {
                    c_code = 'signal_emit({signal_ptr}, NULL);';
                } else if (argCount == 1) {
                    c_code = 'signal_emit({signal_ptr}, (void*)(uintptr_t)({0}));';
                } else {
                    var argPlaceholders = [for (i in 0...argCount) '{$i}'];
                    c_code = '{struct_type} _p = {' + argPlaceholders.join(', ') + '}; signal_emit({signal_ptr}, &_p);';
                }

                return {
                    type: "signal_call",
                    value: "emit",
                    c_code: c_code,
                    props: {
                        signal_name: signalName,
                        arg_count: argCount
                    },
                    args: args
                };

            default:
                return { type: "skip" };
        }
    }

    function convertGlobalSignalCall(method:String, className:String, signalName:String, args:Array<IRNode>, params:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Handle global/static signals: GameEvents.gemCollected.emit()
        var globalSignalName = 'g_${className.toLowerCase()}_$signalName';

        // Track this global signal
        var meta = ctx.getMeta();
        if (!Lambda.has(meta.global_signals, globalSignalName)) {
            meta.global_signals.push(globalSignalName);
        }

        switch (method) {
            case "connect":
                if (params.length > 0) {
                    // Try to extract as named function reference first
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        ctx.addSignalHandler(callbackName, signalName);
                        return {
                            type: "global_signal_call",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                global_signal: globalSignalName,
                                callback: callbackName
                            }
                        };
                    }

                    // Check for anonymous function
                    var anonResult = extractAnonymousCallback(params[0], signalName, ctx);
                    if (anonResult != null) {
                        ctx.addSignalHandler(anonResult.callbackName, signalName);
                        return {
                            type: "global_signal_call",
                            c_code: 'signal_connect({signal_ptr}, {handler}, data);',
                            props: {
                                global_signal: globalSignalName,
                                callback: anonResult.callbackName,
                                inline_callback: anonResult.inlineCallback
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "disconnect":
                if (params.length > 0) {
                    var callbackName = extractFunctionRef(params[0]);
                    if (callbackName != null) {
                        return {
                            type: "global_signal_call",
                            c_code: 'signal_disconnect({signal_ptr}, {handler});',
                            props: {
                                global_signal: globalSignalName,
                                callback: callbackName
                            }
                        };
                    }
                }
                return { type: "skip" };

            case "emit":
                var argCount = params.length;
                var c_code:String;
                if (argCount == 0) {
                    c_code = 'signal_emit({signal_ptr}, NULL);';
                } else if (argCount == 1) {
                    c_code = 'signal_emit({signal_ptr}, (void*)(uintptr_t)({0}));';
                } else {
                    c_code = 'signal_emit({signal_ptr}, (void*){0});';
                }
                return {
                    type: "global_signal_call",
                    c_code: c_code,
                    props: {
                        global_signal: globalSignalName
                    },
                    args: args
                };

            default:
                return { type: "skip" };
        }
    }

    /**
     * Extract an anonymous function callback, generating a unique name and IR body.
     * Returns null if the expression is not an anonymous function.
     */
    function extractAnonymousCallback(e:Expr, signalName:String, ctx:IExtractorContext):{ callbackName:String, inlineCallback:Dynamic } {
        switch (e.expr) {
            case EFunction(_, func):
                // It's an anonymous function: function(param: Type) { ... }
                var cName = ctx.getCName();
                var callbackName = '${signalName}_cb_${anonCounter++}';

                // Extract function parameters
                var params:Array<Dynamic> = [];
                if (func.args != null) {
                    for (arg in func.args) {
                        var paramName = arg.name;
                        var haxeType = "Dynamic";
                        if (arg.type != null) {
                            haxeType = haxe.macro.ComplexTypeTools.toString(arg.type);
                        }
                        var ctype = TypeMap.getCType(haxeType);
                        params.push({
                            name: paramName,
                            haxe_type: haxeType,
                            ctype: ctype
                        });
                    }
                }

                // Extract function body as IR nodes
                var bodyNodes:Array<Dynamic> = [];
                if (func.expr != null) {
                    switch (func.expr.expr) {
                        case EBlock(exprs):
                            for (expr in exprs) {
                                var node = ctx.exprToIR(expr);
                                if (node != null && node.type != "skip") {
                                    bodyNodes.push(node);
                                }
                            }
                        default:
                            var node = ctx.exprToIR(func.expr);
                            if (node != null && node.type != "skip") {
                                bodyNodes.push(node);
                            }
                    }
                }

                return {
                    callbackName: callbackName,
                    inlineCallback: {
                        callback_name: callbackName,
                        params: params,
                        body: bodyNodes
                    }
                };

            default:
                return null;
        }
    }

    function extractFunctionRef(e:Expr):String {
        return ExprUtils.extractIdentName(e);
    }
}

#end