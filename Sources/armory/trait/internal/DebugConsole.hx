package armory.trait.internal;

import iron.Trait;
#if arm_debug
import kha.Scheduler;
import iron.object.CameraObject;
import iron.object.MeshObject;
import zui.Zui;
import zui.Id;
#end

#if arm_debug
@:access(zui.Zui)
@:access(armory.logicnode.LogicNode)
#end
class DebugConsole extends Trait {

#if (!arm_debug)
	public function new() { super(); }
#else

	public var visible = true;
	var ui:Zui;
	var scaleFactor = 1.0;

	var lastTime = 0.0;
	var frameTime = 0.0;
	var totalTime = 0.0;
	var frames = 0;

	var frameTimeAvg = 0.0;
	var frameTimeAvgMin = 0.0;
	var frameTimeAvgMax = 0.0;
	var renderPathTime = 0.0;
	var renderPathTimeAvg = 0.0;
	var updateTime = 0.0;
	var updateTimeAvg = 0.0;
	var animTime = 0.0;
	var animTimeAvg = 0.0;
	var physTime = 0.0;
	var physTimeAvg = 0.0;
	var graph:kha.Image = null;
	var graphA:kha.Image = null;
	var graphB:kha.Image = null;
	var benchmark = false;
	var benchFrames = 0;
	var benchTime = 0.0;

	var selectedObject:iron.object.Object;
	var selectedType = "";
	static var lrow = [1/2, 1/2];
	static var row4 = [1/4, 1/4, 1/4, 1/4];

	public static var debugFloat = 1.0;
	public static var watchNodes:Array<armory.logicnode.LogicNode> = [];

	public function new(scaleFactor = 1.0) {
		super();

		this.scaleFactor = scaleFactor;

		iron.data.Data.getFont('font_default.ttf', function(font:kha.Font) {
			ui = new Zui({scaleFactor: scaleFactor, font: font});
			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
			if (haxeTrace == null) {
				haxeTrace = haxe.Log.trace;
				haxe.Log.trace = consoleTrace;
			}
			// Toggle console
			kha.input.Keyboard.get().notify(null, null, function(char: String) {
				if (char == "~") visible = !visible;
				else if (char == "[") { debugFloat -= 0.1; trace(debugFloat); }
				else if (char == "]") { debugFloat += 0.1; trace(debugFloat); }
			});
		});
	}

	var debugDrawSet = false;

	function selectObject(o:iron.object.Object) {
		selectedObject = o;

		if (!debugDrawSet) {
			debugDrawSet = true;
			armory.trait.internal.DebugDraw.notifyOnRender(function(draw:armory.trait.internal.DebugDraw) {
				if (selectedObject != null) draw.bounds(selectedObject.transform);
			});
		}
	}

	function updateGraph() {
		if (graph == null) {
			graphA = kha.Image.createRenderTarget(280, 33);
			graphB = kha.Image.createRenderTarget(280, 33);
			graph = graphA;
		}
		else graph = graph == graphA ? graphB : graphA;
		var graphPrev = graph == graphA ? graphB : graphA;

		graph.g2.begin(true, 0x00000000);
		graph.g2.color = 0xffffffff;
		graph.g2.drawImage(graphPrev, -3, 0);

		var avg = Math.round(frameTimeAvg * 1000);
		var miss = avg > 16.7 ? (avg - 16.7) / 16.7 : 0.0;
		graph.g2.color = kha.Color.fromFloats(miss, 1 - miss, 0, 1.0);
		graph.g2.fillRect(280 - 3, 33 - avg, 3, avg);

		graph.g2.color = 0xff000000;
		graph.g2.fillRect(280 - 3, 33 - 17, 3, 1);
		
		graph.g2.end();
	}

	static var haxeTrace:Dynamic->haxe.PosInfos->Void = null;
	static var lastTraces:Array<String> = [''];
	static function consoleTrace(v:Dynamic, ?inf:haxe.PosInfos) {
		lastTraces.unshift(Std.string(v));
		if (lastTraces.length > 10) lastTraces.pop();
		haxeTrace(v, inf);
	}

	function render2D(g:kha.graphics2.Graphics) {
		if (!visible) return;
		var hwin = Id.handle();
		var htab = Id.handle({position: 0});
		var ww = Std.int(280 * scaleFactor);
		var wx = iron.App.w() - ww;
		var wy = 0;
		var wh = iron.App.h();

		// var bindG = ui.windowDirty(hwin, wx, wy, ww, wh) || hwin.redraws > 0;
		var bindG = true;
		if (bindG) g.end();
		
		ui.begin(g);
		if (ui.window(hwin, wx, wy, ww, wh, true)) {

			if (ui.tab(htab, '')) {}

			if (ui.tab(htab, 'Scene')) {

				if (ui.panel(Id.handle({selected: true}), "Outliner")) {
					ui.indent();
					
					var i = 0;
					function drawList(h:zui.Zui.Handle, o:iron.object.Object) {
						if (o.name.charAt(0) == '.') return; // Hidden
						var b = false;
						if (selectedObject == o) {
							ui.g.color = 0xff205d9c;
							ui.g.fillRect(0, ui._y, ui._windowW, ui.ELEMENT_H());
							ui.g.color = 0xffffffff;
						}
						if (o.children.length > 0) {
							ui.row([1/13, 12/13]);
							b = ui.panel(h.nest(i, {selected: true}), "", 0, true);
							ui.text(o.name);
						}
						else {
							ui._x += 18; // Sign offset
							ui.text(o.name);
							ui._x -= 18;
						}
						if (ui.isReleased) {
							selectObject(o);
						}
						i++;
						if (b) {
							for (c in o.children) {
								ui.indent();
								drawList(h, c);
								ui.unindent();
							}
						}
					}
					for (c in iron.Scene.active.root.children) {
						drawList(Id.handle(), c);
					}

					ui.unindent();
				}
				
				if (selectedObject == null) selectedType = "";

				if (ui.panel(Id.handle({selected: true}), 'Properties $selectedType')) {
					ui.indent();
					
					if (selectedObject != null) {

						var h = Id.handle();
						h.selected = selectedObject.visible;
						selectedObject.visible = ui.check(h, "Visible");

						var loc = selectedObject.transform.loc;
						var scale = selectedObject.transform.scale;
						var rot = selectedObject.transform.rot.getEuler();
						var dim = selectedObject.transform.dim;
						rot.mult(180 / 3.141592);
						var f = 0.0;

						ui.row(row4);
						ui.text("Location");

						h = Id.handle();
						h.text = roundfp(loc.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						if (ui.changed) loc.x = f;

						h = Id.handle();
						h.text = roundfp(loc.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (ui.changed) loc.y = f;

						h = Id.handle();
						h.text = roundfp(loc.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (ui.changed) loc.z = f;

						ui.row(row4);
						ui.text("Rotation");
						
						h = Id.handle();
						h.text = roundfp(rot.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						var changed = false;
						if (ui.changed) { changed = true; rot.x = f; }

						h = Id.handle();
						h.text = roundfp(rot.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (ui.changed) { changed = true; rot.y = f; }

						h = Id.handle();
						h.text = roundfp(rot.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (ui.changed) { changed = true; rot.z = f; }

						if (changed && selectedObject.name != "Scene") {
							rot.mult(3.141592 / 180);
							selectedObject.transform.rot.fromEuler(rot.x, rot.y, rot.z);
							selectedObject.transform.buildMatrix();
							#if arm_physics
							var rb = selectedObject.getTrait(armory.trait.physics.RigidBody);
							if (rb != null) rb.syncTransform();
							#end
						}

						ui.row(row4);
						ui.text("Scale");
						
						h = Id.handle();
						h.text = roundfp(scale.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						if (ui.changed) scale.x = f;

						h = Id.handle();
						h.text = roundfp(scale.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (ui.changed) scale.y = f;

						h = Id.handle();
						h.text = roundfp(scale.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (ui.changed) scale.z = f;

						ui.row(row4);
						ui.text("Dimensions");

						h = Id.handle();
						h.text = roundfp(dim.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						if (ui.changed) dim.x = f;

						h = Id.handle();
						h.text = roundfp(dim.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (ui.changed) dim.y = f;

						h = Id.handle();
						h.text = roundfp(dim.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (ui.changed) dim.z = f;

						selectedObject.transform.dirty = true;

						if (selectedObject.traits.length > 0) {
							ui.text("Traits:");
							for (t in selectedObject.traits) {
								ui.text(Type.getClassName(Type.getClass(t)));
							}
						}

						if (selectedObject.name == "Scene") {
							selectedType = "(Scene)";
							var p = iron.Scene.active.world.probe;
							p.raw.strength = ui.slider(Id.handle({value: p.raw.strength}), "Env Strength", 0.0, 5.0, true);
						}
						else if (Std.is(selectedObject, iron.object.LightObject)) {
							selectedType = "(Light)";
							var light = cast(selectedObject, iron.object.LightObject);
							light.data.raw.strength = ui.slider(Id.handle({value: light.data.raw.strength / 10}), "Strength", 0.0, 5.0, true) * 10;
						}
						else if (Std.is(selectedObject, iron.object.CameraObject)) {
							selectedType = "(Camera)";
							var cam = cast(selectedObject, iron.object.CameraObject);
							var fovHandle = Id.handle({value: Std.int(cam.data.raw.fov * 100) / 100});
							cam.data.raw.fov = ui.slider(fovHandle, "FoV", 0.3, 2.0, true);
							if (ui.changed) {
								cam.buildProjection();
							}
						}
						else {
							selectedType = "(Object)";
							
						}
					}

					ui.unindent();
				}
			}

			var avg = Math.round(frameTimeAvg * 10000) / 10;
			var fpsAvg = avg > 0 ? Math.round(1000 / avg) : 0;
			if (ui.tab(htab, '$avg ms')) {

				if (ui.panel(Id.handle({selected: true}), 'Performance')) {
					if (graph != null) ui.image(graph);
					ui.indent();

					ui.row(lrow);
					ui.text('Frame');
					ui.text('$avg ms / $fpsAvg fps', Align.Right);
					
					ui.row(lrow);
					ui.text('Render-path');
					ui.text(Math.round(renderPathTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text('Script');
					ui.text(Math.round((updateTimeAvg - physTimeAvg - animTimeAvg) * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text('Animation');
					ui.text(Math.round(animTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text('Physics');
					ui.text(Math.round(physTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), 'Draw')) {
					ui.indent();

					ui.row(lrow);
					var numMeshes = iron.Scene.active.meshes.length;
					ui.text("Meshes");
					ui.text(numMeshes + "", Align.Right);

					ui.row(lrow);
					ui.text('Draw calls');
					ui.text(iron.RenderPath.drawCalls + "", Align.Right);

					ui.row(lrow);
					ui.text('Tris mesh');
					ui.text(iron.RenderPath.numTrisMesh + "", Align.Right);

					ui.row(lrow);
					ui.text('Tris shadow');
					ui.text(iron.RenderPath.numTrisShadow + "", Align.Right);

					#if arm_batch
					ui.row(lrow);
					ui.text('Batch calls');
					ui.text(iron.RenderPath.batchCalls + "", Align.Right);

					ui.row(lrow);
					ui.text('Batch buckets');
					ui.text(iron.RenderPath.batchBuckets + "", Align.Right);
					#end

					ui.row(lrow);
					ui.text('Culled'); // Assumes shadow context for all meshes
					ui.text(iron.RenderPath.culled + ' / ' + numMeshes * 2, Align.Right);
					
					#if arm_stream
					ui.row(lrow);
					var total = iron.Scene.active.sceneStream.sceneTotal();
					ui.text('Streamed');
					ui.text('$numMeshes / $total', Align.Right);
					#end

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), 'Render Targets')) {
					ui.indent();
					#if (kha_opengl || kha_webgl)
					ui.imageInvertY = true;
					#end
					for (rt in iron.RenderPath.active.renderTargets) {
						ui.text(rt.raw.name);
						if (rt.image != null && !rt.is3D) {
							ui.image(rt.image);
						}
					}
					#if (kha_opengl || kha_webgl)
					ui.imageInvertY = false;
					#end
					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), 'Cached Materials')) {
					ui.indent();
					for (c in iron.data.Data.cachedMaterials) {
						ui.text(c.name);
					}
					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), 'Cached Shaders')) {
					ui.indent();
					for (c in iron.data.Data.cachedShaders) {
						ui.text(c.name);
					}
					ui.unindent();
				}

				// if (ui.panel(Id.handle({selected: false}), 'Cached Textures')) {
				// 	ui.indent();
				// 	for (c in iron.data.Data.cachedImages) {
				// 		ui.image(c);
				// 	}
				// 	ui.unindent();
				// }
			}
			if (ui.tab(htab, lastTraces[0] == '' ? 'Console' : lastTraces[0].substr(0, 20))) {
				#if js
				if (ui.panel(Id.handle({selected: false}), 'Script')) {
					ui.indent();
					var t = ui.textInput(Id.handle());
					if (ui.button("Run")) {
						try { trace("> " + t); js.Lib.eval(t); }
						catch(e:Dynamic) { trace(e); }
					}
					ui.unindent();
				}
				#end
				if (ui.panel(Id.handle({selected: true}), 'Log')) {
					ui.indent();
					if (ui.button("Clear")) {
						lastTraces[0] = '';
						lastTraces.splice(1, lastTraces.length - 1);
					}
					for (t in lastTraces) ui.text(t);
					ui.unindent();
				}
			}

			if (watchNodes.length > 0 && ui.tab(htab, "Watch")) {
				for (n in watchNodes) {
					ui.text(n.tree.object.name + '.' + n.tree.name + '.' + n.name + ' = ' + n.get(0));
				}
			}

			ui.separator();
		}

		ui.end(bindG);
		if (bindG) g.begin(false);

		totalTime += frameTime;
		renderPathTime += iron.App.renderPathTime;
		frames++;
		if (totalTime > 1.0) {
			hwin.redraws = 1;
			var t = totalTime / frames;
			// Second frame
			if (frameTimeAvg > 0) {
				if (t < frameTimeAvgMin || frameTimeAvgMin == 0) frameTimeAvgMin = t;
				if (t > frameTimeAvgMax || frameTimeAvgMax == 0) frameTimeAvgMax = t;
			}

			frameTimeAvg = t;

			if (benchmark) {
				benchFrames++;
				if (benchFrames > 10) benchTime += t;
				if (benchFrames == 20) trace(Std.int((benchTime / 10) * 1000000) / 1000); // ms
			}
			
			renderPathTimeAvg = renderPathTime / frames;
			updateTimeAvg = updateTime / frames;
			animTimeAvg = animTime / frames;
			physTimeAvg = physTime / frames;
			
			totalTime = 0;
			renderPathTime = 0;
			updateTime = 0;
			animTime = 0;
			physTime = 0;
			frames = 0;

			if (htab.position == 2) {
				g.end();
				updateGraph(); // Profile tab selected
				g.begin(false);
			}
		}
		frameTime = Scheduler.realTime() - lastTime;
		lastTime = Scheduler.realTime();
	}

	function update() {
		armory.trait.WalkNavigation.enabled = !(ui.isScrolling || (ui.currentWindow != null && ui.currentWindow.dragging));
		updateTime += iron.App.updateTime;
		animTime += iron.object.Animation.animationTime;
	#if arm_physics
		physTime += armory.trait.physics.PhysicsWorld.physTime;
	#end
	}

	static function roundfp(f:Float, precision = 2):Float {
		f *= Math.pow(10, precision);
		return Math.round(f) / Math.pow(10, precision);
	}
#end
}
