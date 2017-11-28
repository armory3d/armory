package armory.trait.internal;

import iron.Trait;
import iron.object.Object;
import iron.object.Transform;
import iron.system.Input;
import iron.math.RayCaster;

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

	public function new() {
		super();
		
		notifyOnInit(init);

		#if (sys_krom && !arm_viewport)
		// TODO: On Windows Krom does not output to stdout, redirect to stderr..
		if (Krom.systemId() == "Windows") {
			var haxeTrace = haxe.Log.trace;
			function kromTrace(v:Dynamic, ?inf:haxe.PosInfos) {
				var str = Std.string(v);
				Krom.sysCommand('>&2 echo "$str"');
				haxeTrace(v, inf);
			}
			haxe.Log.trace = kromTrace;
		}
		#end
	}

	function init() {
		// gizmo = iron.Scene.active.getChild('ArrowGizmo');
		// arrowX = iron.Scene.active.getChild('ArrowX');
		// arrowY = iron.Scene.active.getChild('ArrowY');
		// arrowZ = iron.Scene.active.getChild('ArrowZ');

		notifyOnUpdate(update);

		if (first) {
			first = false;
			#if (kha_krom && arm_render)
			renderCapture();
			#end
		}
	}

	function update() {

		var keyboard = Input.getKeyboard();
		if (keyboard.started("esc")) {
			var viewStr = iron.Scene.active.camera != null ? '|' + iron.Scene.active.camera.V.toArray() : '';
			trace('__arm|quit' + viewStr);
		}

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

		#if (js && kha_webgl && !kha_node)
		time += iron.system.Time.delta;
		if (time > 1.0) {
			time = 0;
			reloadOnUpdate();
		}
		#end
	}

#if (js && kha_webgl && !kha_node)
	static var time = 0.0;
	static var lastMtime:Dynamic = null;
	function reloadOnUpdate() {
		// Reload page on kha.js rewrite
		var khaPath = "kha.js";
		var xhr = new js.html.XMLHttpRequest();
		xhr.open('HEAD', khaPath, true); 
		xhr.onreadystatechange = function() {
			if (xhr.readyState == 4 && xhr.status == 200) {
				var mtime = xhr.getResponseHeader('Last-Modified');
				if (lastMtime != null && mtime.toString() != lastMtime) {
					untyped __js__('window.location.reload(true)');
				}
				lastMtime = mtime;
			}
		}
		xhr.send();
	}
#end

#if (kha_krom && arm_render)
	static var frame = 0;	
	static var captured = false;
	
	#if arm_render_anim

	static var current = 0.0;
	static var framesCaptured = 0;

	@:access(kha.Scheduler)
	function renderCapture() {
		iron.App.pauseUpdates = true;
		iron.App.notifyOnRender(function(g:kha.graphics4.Graphics) {
			if (captured) return;
			kha.Scheduler.current = current;
			frame++;
			if (frame >= 2) { // Init TAA
				iron.App.pauseUpdates = false;
				if (frame % 2 == 0) { // Alternate TAA
					current += iron.system.Time.delta;
					return;
				}
				var info = iron.Scene.active.raw.capture_info;
				var path = iron.RenderPath.active;
				var tex = path.renderTargets.get("capture").image;
			
				if (tex != null) {
					var pixels = tex.getPixels();
					var bd = pixels.getData();
					var bo = new haxe.io.BytesOutput();
					var rgb = haxe.io.Bytes.alloc(tex.width * tex.height * 3);
					for (j in 0...tex.height) {
						for (i in 0...tex.width) {
							var k = j * tex.width + i;
							var l = (tex.height - j) * tex.width + i; // Reverse Y
							rgb.set(k * 3 + 0, pixels.get(l * 4 + 2));
							rgb.set(k * 3 + 1, pixels.get(l * 4 + 1));
							rgb.set(k * 3 + 2, pixels.get(l * 4 + 0));
						}
					}
					var pngwriter = new iron.format.png.Writer(bo);
					pngwriter.write(iron.format.png.Tools.buildRGB(tex.width, tex.height, rgb));
					var fname = framesCaptured + "";
					while (fname.length < 4) fname = "0" + fname;
					Krom.fileSaveBytes(info.path +  "/" + fname + ".png", bo.getBytes().getData());
				}
				if (framesCaptured++ == info.frame_end) {
					captured = true;
					kha.System.requestShutdown();
				}
			}
		});
	}

	#else

	function renderCapture() {
		iron.App.notifyOnRender(function(g:kha.graphics4.Graphics) {
			if (captured) return;
			frame++;
			if (frame >= 3) {
				var path = iron.RenderPath.active;
				var tex = path.renderTargets.get("capture").image;
				if (tex != null) {
					var pixels = tex.getPixels();
					Krom.fileSaveBytes("render.bin", pixels.getData());
				}
				captured = true;
				kha.System.requestShutdown();
			}
		});
	}
	#end
#end
}
