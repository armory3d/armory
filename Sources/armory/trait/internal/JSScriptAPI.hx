package armory.trait.internal;

#if cpp

import haxeduktape.Duktape;

// @:headerCode('
// #include <duktape.h>
// ')

class JSScriptAPI {

	var ctx:haxeduktape.DukContext;

	// static function do_tweak(ctx:cpp.RawPointer<Duk_context>):Int {
		// return 1;
	// }

    public function new(ctx:haxeduktape.DukContext) {
        this.ctx = ctx;

  //       ctx.pushGlobalObject();
  //       ctx.pushObject();

        //untyped __cpp__('
		// const duk_function_list_entry my_module_funcs[] = {
		//     { "tweak", do_tweak, 0 },
		//     { NULL, NULL, 0 }
		// }');

		// var rawctx = ctx.ctx;
		// untyped __cpp__("duk_put_function_list(rawctx, -1, my_module_funcs)");

		// ctx.putPropString("MyModule");
		// ctx.pop();
    }
}

#else

@:expose("arm")
class JSScriptAPI {

	public static var App = iron.App;
	public static var Root = iron.Root;
	public static var Time = iron.sys.Time;
	public static var Node = iron.node.Node;
	public static var Resource = iron.resource.Resource;

	public function new() { }
}

@:expose("arm.math")
class JSScriptAPIMath {

	public static var Vec4 = iron.math.Vec4;
	public static var Mat4 = iron.math.Mat4;
	public static var Quat = iron.math.Quat;
}

#end
