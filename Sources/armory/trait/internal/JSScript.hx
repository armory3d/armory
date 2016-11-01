package armory.trait.internal;

import iron.Trait;

@:keep
class JSScript extends Trait {

	static var api:JSScriptAPI = null;

	public function new(scriptBlob:String) {
		super();

		iron.data.Data.getBlob(scriptBlob + '.js', function(blob:kha.Blob) {
			
			var header = "let App = armory.App;
						  let Scene = armory.Scene;
						  let Data = armory.Data;
						  let Quat = armory.math.Quat;
						  let Mat4 = armory.math.Mat4;
						  let Vec4 = armory.math.Vec4;";
			var src = header + blob.toString();
#if js
			if (api == null) api = new JSScriptAPI();
			untyped __js__("let self = {0}; eval(src);", object);
#end
		});
	}
}
