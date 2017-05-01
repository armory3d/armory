package armory.trait.internal;

import iron.Trait;
import iron.object.Object;
import iron.object.Transform;
import iron.system.Input;
import iron.math.RayCaster;

@:keep
class SpaceArmory extends Trait {

	var gizmo:Object;
	var arrowX:Object;
	var arrowY:Object;
	var arrowZ:Object;
	var selected:Transform = null;

	var moveX = false;
	var moveY = false;
	var moveZ = false;

	static var first = true;

#if js
	static var patchTime = 0.0;
	static var lastMtime:Dynamic;
	static var lastSize:Dynamic;
#end

	public function new() {
		super();
		
		notifyOnInit(init);
	}

	function init() {
		// gizmo = iron.Scene.active.getChild('ArrowGizmo');
		// arrowX = iron.Scene.active.getChild('ArrowX');
		// arrowY = iron.Scene.active.getChild('ArrowY');
		// arrowZ = iron.Scene.active.getChild('ArrowZ');

		notifyOnUpdate(update);

		if (first) {
			first = false;
			#if (js && webgl)
			electronRenderCapture();
			#end
		}
	}

	function update() {

		var keyboard = Input.getKeyboard();
		if (keyboard.started("esc")) trace('__arm|quit');

		// var mouse = Input.getMouse();
		// if (mouse.started("right")) {
		// 	var transforms:Array<Transform> = [];
		// 	for (o in iron.Scene.active.meshes) transforms.push(o.transform);
		// 	var hit = RayCaster.getClosestBoxIntersect(transforms, mouse.x, mouse.y, iron.Scene.active.camera);
		// 	if (hit != null) {
		// 		var loc = hit.loc;
		// 		// gizmo.transform.loc.set(loc.x, loc.y, loc.z);
		// 		// gizmo.transform.buildMatrix();
		// 		selected = hit;
		// 		trace('__arm|select|' + selected.object.name);
		// 	}
		// }

		// if (selected != null) {
		// 	if (mouse.started()) {

		// 		var transforms = [arrowX.transform, arrowY.transform, arrowZ.transform];

		// 		var hit = RayCaster.getClosestBoxIntersect(transforms, mouse.x, mouse.y, iron.Scene.active.camera);
		// 		if (hit != null) {
		// 			if (hit.object.name == 'ArrowX') moveX = true;
		// 			else if (hit.object.name == 'ArrowY') moveY = true;
		// 			else if (hit.object.name == 'ArrowX') moveZ = true;
		// 		}
		// 	}

		// 	if (moveX || moveY || moveZ) {
		// 		Input.occupied = true;

				
		// 		if (moveX) selected.loc.x += mouse.deltaX / 110.0;
		// 		if (moveY) selected.loc.y += mouse.deltaX / 110.0;
		// 		if (moveZ) selected.loc.z += mouse.deltaX / 110.0;
				
		// 		selected.buildMatrix();

		// 		// gizmo.transform.loc.set(selected.loc.x, selected.loc.y, selected.loc.z);
		// 		// gizmo.transform.buildMatrix();
		// 	}
		// }

		// if (mouse.released()) {
		// 	Input.occupied = false;
		// 	// Move operator creator into separate class..
		// 	// Map directly to bl operators - setx to translate
		// 	if (moveX) trace('__arm|setx|' + selected.object.name + '|' + selected.loc.x);
		// 	moveX = moveY = moveZ = false;
		// }
	}

#if (js && webgl)
	public static function getRenderResult():js.html.Uint8Array {
		var gl = kha.SystemImpl.gl;
		var w = gl.drawingBufferWidth;
		var h = gl.drawingBufferHeight;
		var pixels = new js.html.Uint8Array(w * h * 4);
		gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, js.html.webgl.GL.RGBA, js.html.webgl.GL.UNSIGNED_BYTE, pixels);
		return pixels;
		// var bytes = haxe.io.Bytes.ofData(pixels.buffer);
		// var pngdata = armory.trait.internal.png.Tools.buildRGB(w, h, bytes);
		// var output = new haxe.io.BytesOutput();
		// var writer = new armory.trait.internal.png.Writer(output);
		// writer.write(pngdata);
		// return output.getBytes();
	}
	
	function electronRenderCapture() {
		var electron = untyped __js__('window && window.process && window.process.versions["electron"]');
		if (electron) {
			untyped __js__('var fs = require("fs");');
			
			App.notifyOnUpdate(function() {
				patchTime += iron.system.Time.delta;
				
				if (patchTime > 0.2) {
					patchTime = 0;
					var repatch = false;
					untyped __js__('
						if (fs.existsSync(__dirname + "/" + "render.msg")) {
							{0} = true;
							fs.unlinkSync(__dirname + "/" + "render.msg");
						}'
					, repatch);

					if (repatch) {
						var pixels = getRenderResult();
						untyped __js__('
							fs.writeFileSync(__dirname + "/render.bin", new Buffer({0}));
						', pixels);
						var w = kha.SystemImpl.gl.drawingBufferWidth;
						var h = kha.SystemImpl.gl.drawingBufferHeight;
						trace("__arm|render" + "|" + w + "|" + h);
					}
					// Compare mtime and size of file
					// untyped __js__('fs.stat(__dirname + "/" + {0} + ".arm", function(err, stats) {', Scene.active.raw.name);
					// untyped __js__('	if ({0} > stats.mtime || {0} < stats.mtime || {1} !== stats.size) { if ({0} !== undefined) { {2} = true; } {0} = stats.mtime; {1} = stats.size; }', lastMtime, lastSize, repatch);
					// if (repatch) {
					// }
					// untyped __js__('});');
				}
			});
		}
	}
#end
}
