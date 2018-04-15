package armory.trait.internal;

import iron.data.Data;
import iron.data.Wasm;

class WasmScript extends iron.Trait {
	var wasm:Wasm;

	static function arm_log(i:Int):Void {
		trace(i);
	}

	static var importObject = {
		env: {
			arm_log: arm_log
		}
	};

	public function new(handle:String) {
		super();

		Data.getBlob(handle, function(b:kha.Blob) {
			wasm = Wasm.instance(b, importObject);
			wasm.exports.main();
		});
	}
}
