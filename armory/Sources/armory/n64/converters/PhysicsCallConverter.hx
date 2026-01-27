package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;
import armory.n64.util.ExprUtils;

using StringTools;

/**
 * Converts physics API calls to C OimoPhysics operations.
 * Handles: applyForce, applyImpulse, setLinearVelocity, getLinearVelocity, etc.
 * Also handles contact subscription: notifyOnContact, removeContact
 */
class PhysicsCallConverter implements ICallConverter {
    static var physicsMethods = [
        "applyForce", "applyImpulse", "setLinearVelocity", "getLinearVelocity",
        "setAngularVelocity", "getAngularVelocity", "setLinearFactor", "setAngularFactor"
    ];

    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check for contact subscription first
        if (method == "notifyOnContact" || method == "removeContact") {
            ctx.getMeta().uses_physics = true;
            return convertContactSubscription(method, args, rawParams, ctx);
        }

        // Check for physics methods on any object
        if (Lambda.has(physicsMethods, method)) {
            ctx.getMeta().uses_physics = true;
            // For N64, physics always applies to the current object
            return convertPhysicsCall(method, { type: "ident", value: "object" }, args);
        }

        // Check for object.physics.method() pattern
        switch (obj.expr) {
            case EField(innerObj, "physics"):
                ctx.getMeta().uses_physics = true;
                var objIR = ctx.exprToIR(innerObj);
                return convertPhysicsCall(method, objIR, args);
            case EConst(CIdent("physics")):
                ctx.getMeta().uses_physics = true;
                return convertPhysicsCall(method, { type: "ident", value: "object" }, args);
            default:
        }

        return null;
    }

    function convertPhysicsCall(method:String, objIR:IRNode, args:Array<IRNode>):IRNode {
        // Physics calls use OimoVec3 which needs coordinate swizzle
        // Template uses {obj} for object and {0} for first arg (vec)
        var c_code = switch (method) {
            case "applyForce":
                "{ OimoVec3 _f = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_force({obj}->rigid_body, &_f); }";
            case "applyImpulse":
                "{ OimoVec3 _i = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_apply_impulse({obj}->rigid_body, &_i); }";
            case "setLinearVelocity":
                "{ OimoVec3 _v = (OimoVec3){({0}).x, ({0}).z, -({0}).y}; physics_set_linear_velocity({obj}->rigid_body, &_v); }";
            case "getLinearVelocity":
                "physics_get_linear_velocity({obj}->rigid_body)";
            default:
                null;
        };

        if (c_code == null) return { type: "skip" };

        return {
            type: "physics_call",
            c_code: c_code,
            object: objIR,
            args: args
        };
    }

    function convertContactSubscription(method:String, args:Array<IRNode>, params:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Extract handler function name from first argument
        if (params.length == 0) return { type: "skip" };

        var handlerName = ExprUtils.extractIdentName(params[0]);

        if (handlerName == null) return { type: "skip" };

        var isSubscribe = (method == "notifyOnContact");
        var meta = ctx.getMeta();
        var cName = ctx.getCName();

        // Build full C handler name
        var fullHandlerName = cName + "_contact_" + handlerName;

        meta.contact_events.push({
            event_name: handlerName,
            handler_name: fullHandlerName,
            subscribe: isSubscribe
        });

        // If subscribing, extract the handler method body
        if (isSubscribe) {
            var func = ctx.getMethod(handlerName);
            if (func != null) {
                var events = ctx.getEvents();
                var eventKey = "contact_" + handlerName;
                if (!events.exists(eventKey)) {
                    events.set(eventKey, []);
                    extractContactHandler(func, events.get(eventKey), ctx);
                }
            }
        }

        // Return skip - the actual subscription is done at init time by Python
        return { type: "skip" };
    }

    function extractContactHandler(func:Function, eventNodes:Array<IRNode>, ctx:IExtractorContext):Void {
        if (func.expr == null) return;

        switch (func.expr.expr) {
            case EBlock(exprs):
                for (expr in exprs) {
                    var node = ctx.exprToIR(expr);
                    if (node != null && node.type != "skip") {
                        eventNodes.push(node);
                    }
                }
            default:
                var node = ctx.exprToIR(func.expr);
                if (node != null && node.type != "skip") {
                    eventNodes.push(node);
                }
        }
    }
}

#end