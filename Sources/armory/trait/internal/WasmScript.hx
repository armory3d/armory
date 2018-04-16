package armory.trait.internal;

#if js

import iron.data.Data;
import iron.data.Wasm;

class WasmScript extends iron.Trait {
	var wasm:Wasm;

	var objectMap:Map<Int, iron.object.Object> = new Map();

	public function new(handle:String) {
		super();

		// Armory API exposed to WebAssembly
		// TODO: static
		/*static*/ var imports = {
			env: {
				trace: function(i:Int) { trace(wasm.getString(i)); },
				tracef: function(f:Float) { trace(f); },
				tracei: function(i:Int) { trace(i); },
				notify_on_update: function(i:Int) { notifyOnUpdate(wasm.exports.update); },
				remove_update: function(i:Int) { removeUpdate(wasm.exports.update); },
				get_object: function(name:Int) {
					var s = wasm.getString(name);
					var o = iron.Scene.active.getChild(s);
					objectMap.set(o.uid, o);
					return o.uid;
				},
				set_transform: function(object:Int, x:Float, y:Float, z:Float, rx:Float, ry:Float, rz:Float, sx:Float, sy:Float, sz:Float) {
					var t = objectMap.get(object).transform;
					t.loc.set(x, y, z);
					t.scale.set(sx, sy, sz);
					t.setRotation(rx, ry, rz);
				},
			},
		};

		Data.getBlob(handle + ".wasm", function(b:kha.Blob) {
			wasm = Wasm.instance(b, imports);
			wasm.exports.main();
		});
	}
}

#end
