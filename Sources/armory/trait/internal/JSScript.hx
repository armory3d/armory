package armory.trait.internal;

import iron.Trait;

@:keep
class JSScript extends Trait {

	static var api:JSScriptAPI = null;

	public function new(scriptBlob:String) {
		super();

		iron.data.Data.getBlob(scriptBlob + '.js', function(blob:kha.Blob) {
			var src = blob.toString();
#if js
			if (api == null) api = new JSScriptAPI();
			untyped __js__("eval(src);");
#end
		});
	}
}
