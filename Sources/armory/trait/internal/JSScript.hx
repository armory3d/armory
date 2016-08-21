package armory.trait.internal;

import iron.Trait;

class JSScript extends Trait {

#if cpp
	static var ctx:haxeduktape.DukContext = null;
	static var api:JSScriptAPI;
#end

    public function new(scriptBlob:String) {
        super();

        var src =  Reflect.field(kha.Assets.blobs, scriptBlob + '_js').toString();

#if js
        untyped __js__("eval(src);");
#else
		if (ctx == null) {
			ctx = new haxeduktape.DukContext();
			api = new JSScriptAPI(ctx);
		}
		ctx.evalString(src);
		// ctx.evalString('print(123)');
#end
    }
}
