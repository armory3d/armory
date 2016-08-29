package armory.trait.internal;

#if cpp

// import haxeduktape.Duktape;

// @:headerCode('
// #include <duktape.h>
// ')

class JSScriptAPI {
/*
	static var ctx:haxeduktape.DukContext;

	static function console_log(rawctx:cpp.RawPointer<Duk_context>):Int {		
		var arg = ctx.requireNumber(0);
		trace(arg);
    	// ctx.pushNumber(arg * arg);
		return 1;
	}

    public function new(_ctx:haxeduktape.DukContext) {
        ctx = _ctx;
        var rawctx = ctx.ctx;

        // Console
        ctx.pushGlobalObject();
        ctx.pushObject();

        untyped __cpp__('
		const duk_function_list_entry console_module_funcs[] = {
		    { "log", console_log, 1 },
		    { NULL, NULL, 0 }
		}');

		untyped __cpp__("duk_put_function_list(rawctx, -1, console_module_funcs)");

		ctx.putPropString("console");
		ctx.pop();
    }
*/
}

#else

@:expose("armory")
class JSScriptAPI {

	public static var App = iron.App;
	public static var Scene = iron.Scene;
	public static var Time = iron.sys.Time;
	public static var Object = iron.object.Object;
	public static var Data = iron.data.Data;

	public function new() { }
}

@:expose("armory.math")
class JSScriptAPIMath {

	public static var Vec4 = iron.math.Vec4;
	public static var Mat4 = iron.math.Mat4;
	public static var Quat = iron.math.Quat;
}

#end
