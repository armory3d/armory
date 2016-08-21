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

#end
