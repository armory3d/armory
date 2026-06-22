package armory.trait.internal;

#if js

import iron.data.Data;
import iron.data.Wasm;
import iron.system.Input;
import iron.system.Time;

class WasmScript extends iron.Trait {

	var wasm: Wasm;
	public var wasmName: String;

	var objectMap: Map<Int, iron.object.Object> = new Map();

	public function new(handle: String) {
		super();
		wasmName = handle;

		// Armory API exposed to WebAssembly
		// TODO: static
		/*static*/ var imports = {
			env: {
				trace: function(i: Int) { trace(wasm.getString(i)); },
				tracef: function(f: Float) { trace(f); },
				tracei: function(i: Int) { trace(i); },

				notify_on_update: function(i: Int) { notifyOnUpdate(wasm.exports.update); },
				remove_update: function(i: Int) { removeUpdate(wasm.exports.update); },
				get_object: function(name: Int) {
					var s = wasm.getString(name);
					var o = iron.Scene.active.getChild(s);
					if (o == null) return -1;
					objectMap.set(o.uid, o);
					return o.uid;
				},
				set_transform: function(object: Int, x: Float, y: Float, z: Float, rx: Float, ry: Float, rz: Float, sx: Float, sy: Float, sz: Float) {
					var o = objectMap.get(object);
					if (o == null) return;
					var t = o.transform;
					t.loc.set(x, y, z);
					t.scale.set(sx, sy, sz);
					t.setRotation(rx, ry, rz);
				},
				set_location: function(object: Int, x: Float, y: Float, z: Float) {
					var o = objectMap.get(object);
					if (o == null) return;
					var t = o.transform;
					t.loc.set(x, y, z);
				},
				set_scale: function(object: Int, x: Float, y: Float, z: Float) {
					var o = objectMap.get(object);
					if (o == null) return;
					var t = o.transform;
					t.scale.set(x, y, z);
				},
				set_rotation: function(object: Int, x: Float, y: Float, z: Float) {
					var o = objectMap.get(object);
					if (o == null) return;
					var t = o.transform;
					t.setRotation(x, y, z);
				},

				mouse_x: function() { return Input.getMouse().x; },
				mouse_y: function() { return Input.getMouse().y; },
				mouse_started: function(button: Int) { return Input.getMouse().started(); },
				mouse_down: function(button: Int) { return Input.getMouse().down(); },
				mouse_released: function(button: Int) { return Input.getMouse().released(); },
				key_started: function(key: Int) { return Input.getKeyboard().started(Keyboard.keyCode(cast key)); },
				key_down: function(key: Int) { return Input.getKeyboard().down(Keyboard.keyCode(cast key)); },
				key_released: function(key: Int) { return Input.getKeyboard().released(Keyboard.keyCode(cast key)); },

				time_real: function() { return Time.time(); },
				time_delta: function() { return Time.delta; },

				js_eval: function(fn: Int) { js.Lib.eval(wasm.getString(fn)); },
				js_call_object: function(object: Int, fn: Int) { Reflect.callMethod(objectMap.get(object), Reflect.field(objectMap.get(object), wasm.getString(fn)), null); },
				js_call_static: function(path: Int, fn: Int) { var cpath = wasm.getString(path); var ctype = Type.resolveClass(cpath); Reflect.callMethod(ctype, Reflect.field(ctype, wasm.getString(fn)), []); },

			},
		};

		Data.getBlob(handle + ".wasm", function(b: kha.Blob) {
			wasm = Wasm.instance(b, imports);
			wasm.exports.main();
		});
	}
}

#end
