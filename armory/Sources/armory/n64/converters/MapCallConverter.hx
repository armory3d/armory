package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import armory.n64.IRTypes;
import armory.n64.mapping.TypeMap;
import armory.n64.converters.ICallConverter;

/**
 * Converts Haxe Map operations to C arm_map functions.
 *
 * Handles:
 *   map.set(key, value) -> map_type_set(&map_expr, key, value)
 *   map.get(key)        -> map_type_get(&map_expr, key)
 *   map[key]            -> map_type_get(&map_expr, key)  (array access)
 *   map.exists(key)     -> map_type_exists(&map_expr, key)
 *   map.remove(key)     -> map_type_remove(&map_expr, key)
 */
class MapCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Check if obj is a Map type
        var objType = ctx.getExprType(obj);
        if (!TypeMap.isMapType(objType)) {
            return null;
        }

        var cType = TypeMap.getCType(objType);
        var mapExpr = extractMapExpr(obj, ctx);

        return switch (method) {
            case "set":
                convertSet(mapExpr, cType, args);
            case "get":
                convertGet(mapExpr, cType, args);
            case "exists":
                convertExists(mapExpr, cType, args);
            case "remove":
                convertRemove(mapExpr, cType, args);
            case "clear":
                convertClear(mapExpr, cType);
            default:
                null;
        };
    }

    /**
     * Extract the map expression (how to access the map variable in C).
     * For traits: data->mapName (member) or mapName (local)
     * For autoloads: c_name_mapName (member) or mapName (local)
     */
    function extractMapExpr(e:Expr, ctx:IExtractorContext):String {
        return switch (e.expr) {
            case EConst(CIdent(name)):
                // Check if it's a member or local
                if (ctx.getMemberType(name) != null) {
                    if (ctx.isAutoload()) {
                        ctx.getCName() + "_" + name;
                    } else {
                        "data->" + name;
                    }
                } else {
                    name;
                }
            case EField(obj, field):
                // Member access: this.map -> data->map or c_name_map
                if (ctx.isAutoload()) {
                    ctx.getCName() + "_" + field;
                } else {
                    "data->" + field;
                }
            default:
                "map";
        };
    }

    function convertSet(mapExpr:String, cType:String, args:Array<IRNode>):IRNode {
        return {
            type: "map_set",
            value: cType,
            props: {
                map_expr: mapExpr
            },
            children: args
        };
    }

    function convertGet(mapExpr:String, cType:String, args:Array<IRNode>):IRNode {
        return {
            type: "map_get",
            value: cType,
            props: {
                map_expr: mapExpr
            },
            children: args
        };
    }

    function convertExists(mapExpr:String, cType:String, args:Array<IRNode>):IRNode {
        return {
            type: "map_exists",
            value: cType,
            props: {
                map_expr: mapExpr
            },
            children: args
        };
    }

    function convertRemove(mapExpr:String, cType:String, args:Array<IRNode>):IRNode {
        return {
            type: "map_remove",
            value: cType,
            props: {
                map_expr: mapExpr
            },
            children: args
        };
    }

    function convertClear(mapExpr:String, cType:String):IRNode {
        return {
            type: "map_clear",
            value: cType,
            props: {
                map_expr: mapExpr
            }
        };
    }
}

#end
