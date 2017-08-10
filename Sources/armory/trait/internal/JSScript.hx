package armory.trait.internal;

import iron.Trait;

class JSScript extends Trait {

	static var api:JSScriptAPI = null;

	public function new(scriptName:String) {
		super();

		notifyOnInit(function() {

			iron.data.Data.getBlob(scriptName + '.js', function(blob:kha.Blob) {
			
				var header = "var App = armory.App;
							  var Scene = armory.Scene;
							  var Data = armory.Data;
							  var Quat = armory.math.Quat;
							  var Mat4 = armory.math.Mat4;
							  var Vec4 = armory.math.Vec4;";
				var src = header + blob.toString();
#if js
				if (api == null) api = new JSScriptAPI();
				untyped __js__("var self = {0};", object);
#if !webgl // Krom
				untyped __js__("var window = this;");
#end
				untyped __js__("eval(src);");
#end
			});

		});
	}
}
