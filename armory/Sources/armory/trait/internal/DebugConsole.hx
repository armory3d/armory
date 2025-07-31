package armory.trait.internal;

import iron.Trait;
#if arm_debug
import kha.Scheduler;
import armory.ui.Canvas;
import iron.object.CameraObject;
import iron.object.MeshObject;
import zui.Zui;
import zui.Id;
using armory.object.TransformExtension;
#if arm_shadowmap_atlas
import armory.renderpath.Inc.ShadowMapTile;
import armory.renderpath.Inc.ShadowMapAtlas;
#end
#end

#if arm_debug
@:access(zui.Zui)
@:access(armory.logicnode.LogicNode)
#end
class DebugConsole extends Trait {

#if (!arm_debug)
	public function new() { super(); }
#else

	public static var visible = true;
	public static var traceWithPosition = true;
	public static var fpsAvg = 0.0;

	/**
		Whether any window of the debug console was hovered in the last drawn frame.
		If `visible` is `false`, the value of this variable is also `false`.
	**/
	// NOTE If there is more than one debug console for whatever reason
	//  (technically possible but stupid) this will only work for the last drawn debug console
	public static var isDebugConsoleHovered(default, null) = false;

	static var ui: Zui;
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
	var graph: kha.Image = null;
	var graphA: kha.Image = null;
	var graphB: kha.Image = null;
	var benchmark = false;
	var benchFrames = 0;
	var benchTime = 0.0;

	var selectedObject: iron.object.Object;
	var selectedType = "";
	var selectedTraits = new Array<Trait>();
	static var lrow = [1 / 2, 1 / 2];
	static var row4 = [1 / 4, 1 / 4, 1 / 4, 1 / 4];

	public static var debugFloat = 1.0;
	public static var watchNodes: Array<armory.logicnode.LogicNode> = [];

	static var positionConsole: PositionStateEnum = PositionStateEnum.Right;
	var shortcutVisible = kha.input.KeyCode.Tilde;
	var shortcutScaleIn = kha.input.KeyCode.OpenBracket;
	var shortcutScaleOut = kha.input.KeyCode.CloseBracket;

	var mouse: iron.system.Input.Mouse;

	#if arm_shadowmap_atlas
	var lightColorMap: Map<String, Int> = new Map();
	var lightColorMapCount = 0;
	var smaLogicTime = 0.0;
	var smaLogicTimeAvg = 0.0;
	var smaRenderTime = 0.0;
	var smaRenderTimeAvg = 0.0;
	#end

	public function new(scaleFactor = 1.0, scaleDebugConsole = 1.0, positionDebugConsole = 2, visibleDebugConsole = 1,
	traceWithPosition = 1, keyCodeVisible = kha.input.KeyCode.Tilde, keyCodeScaleIn = kha.input.KeyCode.OpenBracket,
	keyCodeScaleOut = kha.input.KeyCode.CloseBracket) {
		super();
		this.scaleFactor = scaleFactor;
		this.mouse = iron.system.Input.getMouse();
		DebugConsole.traceWithPosition = traceWithPosition == 1;

		iron.data.Data.getFont(Canvas.defaultFontName, function(font: kha.Font) {
			ui = new Zui({scaleFactor: scaleFactor, font: font});
			// Set settings
			setScale(scaleDebugConsole);
			setVisible(visibleDebugConsole == 1);
			setPosition(positionDebugConsole);
			shortcutVisible = keyCodeVisible;
			shortcutScaleIn = keyCodeScaleIn;
			shortcutScaleOut = keyCodeScaleOut;

			notifyOnRender2D(render2D);
			notifyOnUpdate(update);
			if (haxeTrace == null) {
				haxeTrace = haxe.Log.trace;
				haxe.Log.trace = consoleTrace;
			}
			// Toggle console
			kha.input.Keyboard.get().notify(null, function(key: kha.input.KeyCode) {
				// DebugFloat
				if (key == kha.input.KeyCode.OpenBracket) {
					debugFloat -= 0.1;
					trace("debugFloat = " + debugFloat);
				}
				else if (key == kha.input.KeyCode.CloseBracket){
					debugFloat += 0.1;
					trace("debugFloat = " + debugFloat);
				}
				// Shortcut - Visible
				if (key == shortcutVisible) visible = !visible;
				// Scale In
				else if (key == shortcutScaleIn) {
					var debugScale = getScale() - 0.1;
					if (debugScale > 0.3) {
						setScale(debugScale);
					}
				}
				// Scale Out
				else if (key == shortcutScaleOut) {
					var debugScale = getScale() + 0.1;
					if (debugScale < 10.0) {
						setScale(debugScale);
					}
				}
			}, null);
		});
	}

	var debugDrawSet = false;

	function selectObject(o: iron.object.Object) {
		selectedObject = o;

		if (!debugDrawSet) {
			debugDrawSet = true;
			armory.trait.internal.DebugDraw.notifyOnRender(function(draw: armory.trait.internal.DebugDraw) {
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

	static var haxeTrace: Dynamic->haxe.PosInfos->Void = null;
	static var lastTraces: Array<String> = [""];
	static function consoleTrace(v: Dynamic, ?inf: haxe.PosInfos) {
		lastTraces.unshift(haxe.Log.formatOutput(v, traceWithPosition ? inf : null));
		if (lastTraces.length > 100) lastTraces.pop();
		haxeTrace(v, inf);
	}

	function render2D(g: kha.graphics2.Graphics) {
		var hwin = Id.handle();
		var htab = Id.handle({position: 0});

		var avg = Math.round(frameTimeAvg * 10000) / 10;
		fpsAvg = avg > 0 ? Math.round(1000 / avg) : 0;

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

			#if arm_shadowmap_atlas
			smaLogicTimeAvg = smaLogicTime / frames;
			smaLogicTime = 0;

			smaRenderTimeAvg = smaRenderTime / frames;
			smaRenderTime = 0;
			#end

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

		isDebugConsoleHovered = false;
		if (!visible) return;

		var ww = Std.int(280 * scaleFactor * getScale());
		// RIGHT
		var wx = iron.App.w() - ww;
		var wy = 0;
		var wh = iron.App.h();
		// Check position
		switch (positionConsole) {
			case PositionStateEnum.Left: wx = 0;
			case PositionStateEnum.Center: wx = Math.round(iron.App.w() / 2 - ww / 2);
			case PositionStateEnum.Right: wx = iron.App.w() - ww;
		}

		// var bindG = ui.windowDirty(hwin, wx, wy, ww, wh) || hwin.redraws > 0;
		var bindG = true;
		if (bindG) g.end();

		ui.begin(g);

		if (ui.window(hwin, wx, wy, ww, wh, true)) {

			if (ui.tab(htab, "")) {}

			if (ui.tab(htab, "Scene")) {

				if (ui.panel(Id.handle({selected: true}), "Outliner: obj.uid_obj.name")) {
					ui.indent();
					ui._y -= ui.ELEMENT_OFFSET();

					var listX = ui._x;
					var listW = ui._w;

					function drawObjectNameInList(object: iron.object.Object, selected: Bool) {
						var _y = ui._y;
						
						if (object.parent.name == 'Root' && object.raw == null)
							ui.text(object.uid+'_'+object.name+' ('+iron.Scene.active.raw.world_ref+')');
						else
							ui.text(object.uid+'_'+object.name);


						if (object == iron.Scene.active.camera) {
							var tagWidth = 100;
							var offsetX = listW - tagWidth;

							var prevX = ui._x;
							var prevY = ui._y;
							var prevW = ui._w;
							ui._x = listX + offsetX;
							ui._y = _y;
							ui._w = tagWidth;
							ui.g.color = selected ? kha.Color.White : kha.Color.fromFloats(0.941, 0.914, 0.329, 1.0);
							ui.drawString(ui.g, "Active Camera", null, 0, Right);
							ui._x = prevX;
							ui._y = prevY;
							ui._w = prevW;
						}
					}

					var lineCounter = 0;
					function drawList(listHandle: zui.Zui.Handle, currentObject: iron.object.Object) {
						if (currentObject.name.charAt(0) == ".") return; // Hidden
						var b = false;

						var isLineSelected = currentObject == selectedObject;

						// Highlight every other line
						if (lineCounter % 2 == 0) {
							ui.g.color = ui.t.SEPARATOR_COL;
							ui.g.fillRect(0, ui._y, ui._windowW, ui.ELEMENT_H());
							ui.g.color = 0xffffffff;
						}

						// Highlight selected line
						if (isLineSelected) {
							ui.g.color = 0xff205d9c;
							ui.g.fillRect(0, ui._y, ui._windowW, ui.ELEMENT_H());
							ui.g.color = 0xffffffff;
						}

						if (currentObject.children.length > 0) {
							ui.row([1 / 13, 12 / 13]);
							b = ui.panel(listHandle.nest(lineCounter, {selected: true}), "", true, false, false);
							drawObjectNameInList(currentObject, isLineSelected);
						}
						else {
							ui._x += 18; // Sign offset

							// Draw line that shows parent relations
							ui.g.color = ui.t.ACCENT_COL;
							ui.g.drawLine(ui._x - 10, ui._y + ui.ELEMENT_H() / 2, ui._x, ui._y + ui.ELEMENT_H() / 2);
							ui.g.color = 0xffffffff;

							drawObjectNameInList(currentObject, isLineSelected);
							ui._x -= 18;
						}

						lineCounter++;
						// Undo applied offset for row drawing caused by endElement() in Zui.hx
						ui._y -= ui.ELEMENT_OFFSET();

						if (ui.isReleased) {
							selectObject(currentObject);
						}

						if (b) {
							var currentY = ui._y;
							for (child in currentObject.children) {
								ui.indent();
								drawList(listHandle, child);
								ui.unindent();
							}

							// Draw line that shows parent relations
							ui.g.color = ui.t.ACCENT_COL;
							ui.g.drawLine(ui._x + 14, currentY, ui._x + 14, ui._y - ui.ELEMENT_H() / 2);
							ui.g.color = 0xffffffff;
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
						if (Std.isOfType(selectedObject, iron.object.CameraObject) && selectedObject != iron.Scene.active.camera) {
							ui.row([1/2, 1/2]);
						}

						var h = Id.handle();
						h.selected = selectedObject.visible;
						selectedObject.visible = ui.check(h, "Visible");

						if (Std.isOfType(selectedObject, iron.object.CameraObject) && selectedObject != iron.Scene.active.camera) {
							if (ui.button("Set Active Camera")) {
								iron.Scene.active.camera = cast selectedObject;
							}
						}

						var localPos = selectedObject.transform.loc;
						var worldPos = selectedObject.transform.getWorldPosition();
						var scale = selectedObject.transform.scale;
						var rot = selectedObject.transform.rot.getEuler();
						var dim = selectedObject.transform.dim;
						rot.mult(180 / 3.141592);
						var f = 0.0;

						ui.text("Transforms");
						ui.indent();

						ui.row(row4);
						ui.text("World Loc");
						// Read-only currently
						ui.enabled = false;
						h = Id.handle();
						h.text = roundfp(worldPos.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						h = Id.handle();
						h.text = roundfp(worldPos.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						h = Id.handle();
						h.text = roundfp(worldPos.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						ui.enabled = true;

						ui.row(row4);
						ui.text("Local Loc");

						h = Id.handle();
						h.text = roundfp(localPos.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						if (h.changed) localPos.x = f;

						h = Id.handle();
						h.text = roundfp(localPos.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (h.changed) localPos.y = f;

						h = Id.handle();
						h.text = roundfp(localPos.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (h.changed) localPos.z = f;

						ui.row(row4);
						ui.text("Rotation");

						h = Id.handle();
						h.text = roundfp(rot.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						var changed = false;
						if (h.changed) { changed = true; rot.x = f; }

						h = Id.handle();
						h.text = roundfp(rot.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (h.changed) { changed = true; rot.y = f; }

						h = Id.handle();
						h.text = roundfp(rot.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (h.changed) { changed = true; rot.z = f; }

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
						if (h.changed) scale.x = f;

						h = Id.handle();
						h.text = roundfp(scale.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (h.changed) scale.y = f;

						h = Id.handle();
						h.text = roundfp(scale.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (h.changed) scale.z = f;

						ui.row(row4);
						ui.text("Dimensions");

						h = Id.handle();
						h.text = roundfp(dim.x) + "";
						f = Std.parseFloat(ui.textInput(h, "X"));
						if (h.changed) dim.x = f;

						h = Id.handle();
						h.text = roundfp(dim.y) + "";
						f = Std.parseFloat(ui.textInput(h, "Y"));
						if (h.changed) dim.y = f;

						h = Id.handle();
						h.text = roundfp(dim.z) + "";
						f = Std.parseFloat(ui.textInput(h, "Z"));
						if (h.changed) dim.z = f;

						selectedObject.transform.dirty = true;
						ui.unindent();

						if (selectedObject.traits.length > 0) {
							ui.text("Traits:");
							ui.indent();
							for (t in selectedObject.traits) {
								ui.row([3/4, 1/4]);
								ui.text(Type.getClassName(Type.getClass(t)));

								if (ui.button("Details")) {
									if (selectedTraits.indexOf(t) == -1) {
										selectedTraits.push(t);
									}
								}
								if (ui.isHovered) ui.tooltip("Open details about the trait in another window");
							}
							ui.unindent();
						}

						if (selectedObject.properties != null) {
							ui.text("Properties:");
							ui.indent();

							for (name => value in selectedObject.properties) {
								ui.row([1/2, 1/2]);
								ui.text(name);
								ui.text(dynamicToUIString(value), Align.Right);
							}

							ui.unindent();
						}

						var col: Array<String> = [];
				
						for (g in iron.Scene.active.raw.groups){
							if(iron.Scene.active.getGroup(g.name).indexOf(selectedObject) != -1) col.push(g.name);
						}

						if (col.length > 0) {
							ui.text("Collections: "+col.length);
							ui.indent();

							for (i => name in col) {
								ui.text((i+1)+'-> '+name);
							}

							ui.unindent();
						}


						if (selectedObject.name == "Scene") {
							selectedType = "(Scene)";
							if (iron.Scene.active.world != null) {
								var p = iron.Scene.active.world.probe;
								p.raw.strength = ui.slider(Id.handle({value: p.raw.strength}), "Env Strength", 0.0, 5.0, true);
							}
							else {
								ui.text("This scene has no world data to edit.");
							}
						}
						else if (Std.isOfType(selectedObject, iron.object.LightObject)) {
							selectedType = "(Light)";
							var light = cast(selectedObject, iron.object.LightObject);
							var lightHandle = Id.handle();
							lightHandle.value = light.data.raw.strength / 10;
							light.data.raw.strength = ui.slider(lightHandle, "Strength", 0.0, 5.0, true) * 10;
							#if arm_shadowmap_atlas
							ui.text("status: " + (light.culledLight ? "culled" : "rendered"));
							ui.text("shadow map size: " + light.data.raw.shadowmap_size);
							#end
						}
						else if (Std.isOfType(selectedObject, iron.object.CameraObject)) {
							selectedType = "(Camera)";
							var cam = cast(selectedObject, iron.object.CameraObject);
							var fovHandle = Id.handle();
							fovHandle.value = Std.int(cam.data.raw.fov * 100) / 100;
							cam.data.raw.fov = ui.slider(fovHandle, "Field of View", 0.3, 2.0, true);
							if (fovHandle.changed) {
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

			if (ui.tab(htab, '$avg ms')) {

				if (ui.panel(Id.handle({selected: true}), "Performance")) {
					if (graph != null) ui.image(graph);
					ui.indent();

					ui.row(lrow);
					ui.text("Frame");
					ui.text('$avg ms / $fpsAvg fps', Align.Right);

					ui.row(lrow);
					ui.text("Render-path");
					ui.text(Math.round(renderPathTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text("Script");
					ui.text(Math.round((updateTimeAvg - physTimeAvg - animTimeAvg) * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text("Animation");
					ui.text(Math.round(animTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text("Physics");
					ui.text(Math.round(physTimeAvg * 10000) / 10 + " ms", Align.Right);

					#if arm_shadowmap_atlas
					ui.row(lrow);
					ui.text("Shadow Map Atlas (Logic)");
					ui.text(Math.round(smaLogicTimeAvg * 10000) / 10 + " ms", Align.Right);

					ui.row(lrow);
					ui.text("Shadow Map Atlas (Render)");
					ui.text(Math.round(smaRenderTimeAvg * 10000) / 10 + " ms", Align.Right);
					#end

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), "Draw")) {
					ui.indent();

					ui.row(lrow);
					var numMeshes = iron.Scene.active.meshes.length;
					ui.text("Meshes");
					ui.text(numMeshes + "", Align.Right);

					ui.row(lrow);
					ui.text("Draw calls");
					ui.text(iron.RenderPath.drawCalls + "", Align.Right);

					ui.row(lrow);
					ui.text("Tris mesh");
					ui.text(iron.RenderPath.numTrisMesh + "", Align.Right);

					ui.row(lrow);
					ui.text("Tris shadow");
					ui.text(iron.RenderPath.numTrisShadow + "", Align.Right);

					#if arm_batch
					ui.row(lrow);
					ui.text("Batch calls");
					ui.text(iron.RenderPath.batchCalls + "", Align.Right);

					ui.row(lrow);
					ui.text("Batch buckets");
					ui.text(iron.RenderPath.batchBuckets + "", Align.Right);
					#end

					ui.row(lrow);
					ui.text("Culled"); // Assumes shadow context for all meshes
					ui.text(iron.RenderPath.culled + " / " + numMeshes * 2, Align.Right);

					#if arm_stream
					ui.row(lrow);
					var total = iron.Scene.active.sceneStream.sceneTotal();
					ui.text("Streamed");
					ui.text('$numMeshes / $total', Align.Right);
					#end

					ui.unindent();
				}

				#if arm_shadowmap_atlas
				if (ui.panel(Id.handle({selected: false}), "Shadow Map Atlases")) {
					inline function highLightNext(color: kha.Color = null) {
						ui.g.color = color != null ? color : -13882324;
						ui.g.fillRect(ui._x, ui._y, ui._windowW, ui.ELEMENT_H());
						ui.g.color = 0xffffffff;
					}

					inline function drawScale(text: String, y: Float, fromX: Float, toX: Float, bottom = false) {
						var _off = bottom ? -4 : 4;
						ui.g.drawLine(fromX, y, toX, y);
						ui.g.drawLine(fromX, y, fromX, y + _off);
						ui.g.drawLine(toX, y, toX, y + _off);

						var _w = ui._w;
						ui._w = Std.int(Math.abs(toX - fromX));
						ui.text(text, Align.Center);
						ui._w = _w;
					}

					/**
					 * create a kha Color from HSV (Hue, Saturation, Value)
					 * @param h expected Hue from [0, 1].
					 * @param s expected Saturation from [0, 1].
					 * @param v expected Value from [0, 1].
					 * @return kha.Color
					 */
					function colorFromHSV(h: Float, s: Float, v: Float): kha.Color {
						// https://stackoverflow.com/a/17243070
						var r = 0.0; var g = 0.0; var b = 0.0;

						var i = Math.floor(h * 6);
						var f = h * 6 - i;
						var p = v * (1 - s);
						var q = v * (1 - f * s);
						var t = v * (1 - (1 - f) * s);

						switch (i % 6) {
							case 0: { r = v; g = t; b = p; }
							case 1: { r = q; g = v; b = p; }
							case 2: { r = p; g = v; b = t; }
							case 3: { r = p; g = q; b = v; }
							case 4: { r = t; g = p; b = v; }
							case 5: { r = v; g = p; b = q; }
						}

						return kha.Color.fromFloats(r, g, b);
					}

					function drawTiles(tile: ShadowMapTile, atlas: ShadowMapAtlas, atlasVisualSize: Float) {
						var color: Null<kha.Color> = kha.Color.fromFloats(0.1, 0.1, 0.1);
						var borderColor = color;
						var tileScale = (tile.size / atlas.sizew) * atlasVisualSize; //* 0.95;
						var x = (tile.coordsX / atlas.sizew) * atlasVisualSize;
						var y = (tile.coordsY / atlas.sizew) * atlasVisualSize;

						if (tile.light != null) {
							color = lightColorMap.get(tile.light.name);
							if (color == null) {
								color = colorFromHSV(Math.random(), 0.7, Math.random() * 0.5 + 0.5);

								lightColorMap.set(tile.light.name, color);
								lightColorMapCount++;
							}
							ui.fill(x + tileScale * 0.019, y + tileScale * 0.03, tileScale * 0.96, tileScale * 0.96, color);
						}
						ui.rect(x, y, tileScale, tileScale, borderColor);

						#if arm_shadowmap_atlas_lod
						// draw children tiles
						for (t in tile.tiles)
							drawTiles(t, atlas, atlasVisualSize);
						#end
					}

					ui.indent(false);
					ui.text("Constants:");
					highLightNext();
					ui.text('Tiles Used Per Point Light: ${ ShadowMapTile.tilesLightType("point") }');
					ui.text('Tiles Used Per Spot Light: ${ ShadowMapTile.tilesLightType("spot") }');
					highLightNext();
					ui.text('Tiles Used For Sun: ${ ShadowMapTile.tilesLightType("sun") }');
					ui.unindent(false);

					ui.indent(false);
					var i = 0;
					for (atlas in ShadowMapAtlas.shadowMapAtlases) {
						if (ui.panel(Id.handle({selected: false}).nest(i), atlas.target )) {
							ui.indent(false);
							// Draw visual representation of the atlas
							var atlasVisualSize = ui._windowW * 0.92;

							drawScale('${atlas.sizew}px', ui._y + ui.ELEMENT_H() * 0.9, ui._x, ui._x + atlasVisualSize);

							// reset light color map when lights are removed
							if (lightColorMapCount > iron.Scene.active.lights.length) {
								lightColorMap = new Map();
								lightColorMapCount = 0;
							}

							for (tile in atlas.tiles)
								drawTiles(tile, atlas, atlasVisualSize);
							// set vertical space for atlas visual representation
							ui._y += atlasVisualSize + 3;

							var tilesRow = atlas.currTileOffset == 0 ? 1 : atlas.currTileOffset;
							var tileScale = atlasVisualSize / tilesRow;
							drawScale('${atlas.baseTileSizeConst}px', ui._y, ui._x, ui._x + tileScale, true);

							// general atlas information
							highLightNext();
							ui.text('Max Atlas Size: ${atlas.maxAtlasSizeConst}, ${atlas.maxAtlasSizeConst} px');
							highLightNext();

							// show detailed information per light
							if (ui.panel(Id.handle({selected: false}).nest(i).nest(0), "Lights in Atlas")) {
								ui.indent(false);
								var j = 1;
								for (tile in atlas.activeTiles) {
									var textCol = ui.t.TEXT_COL;
									var lightCol = lightColorMap.get(tile.light.name);
									if (lightCol != null)
										ui.t.TEXT_COL = lightCol;
									#if arm_shadowmap_atlas_lod
									if (ui.panel(Id.handle({selected: false}).nest(i).nest(j), tile.light.name)) {
										ui.t.TEXT_COL = textCol;
										ui.indent(false);
										ui.text('Shadow Map Size: ${tile.size}, ${tile.size} px');
										ui.unindent(false);
									}
									#else
									ui.indent(false);
									ui.text(tile.light.name);
									ui.unindent(false);
									#end
									ui.t.TEXT_COL = textCol;
									j++;
								}
								ui.unindent(false);
							}

							// show unused tiles statistics
							#if arm_shadowmap_atlas_lod
							// WIP
							#else
							var unusedTiles = atlas.tiles.length;
							#if arm_shadowmap_atlas_single_map
								for (tile in atlas.activeTiles)
									unusedTiles -= ShadowMapTile.tilesLightType(tile.light.data.raw.type);
							#else
								unusedTiles -= atlas.activeTiles.length * ShadowMapTile.tilesLightType(atlas.lightType);
							#end
							ui.text('Unused tiles: ${unusedTiles}');
							#end

							var rejectedLightsNames = "";
							if (atlas.rejectedLights.length > 0) {
								for (l in atlas.rejectedLights)
									rejectedLightsNames += l.name + ", ";
								rejectedLightsNames = rejectedLightsNames.substr(0, rejectedLightsNames.length - 2);
								highLightNext(kha.Color.fromFloats(0.447, 0.247, 0.188));
								ui.text('Not enough space in atlas for ${atlas.rejectedLights.length} light${atlas.rejectedLights.length > 1 ? "s" : ""}:');
								ui.indent();
								ui.text(${rejectedLightsNames});
								ui.unindent(false);
							}

							ui.unindent(false);
						}
						i++;
					}
					ui.unindent(false);
					ui.unindent(false);
				}
				#end

				if (ui.panel(Id.handle({selected: false}), "Render Targets")) {
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

				if (ui.panel(Id.handle({selected: false}), "Cached Materials")) {
					ui.indent();
					for (c in iron.data.Data.cachedMaterials) {
						ui.text(c.name);
					}
					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), "Cached Shaders")) {
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
			if (ui.tab(htab, lastTraces[0] == "" ? "Console" : lastTraces[0].substr(0, 20))) {
				#if js
				if (ui.panel(Id.handle({selected: false}), "Script")) {
					ui.indent();
					var t = ui.textInput(Id.handle());
					if (ui.button("Run")) {
						try { trace("> " + t); js.Lib.eval(t); }
						catch (e: Dynamic) { trace(e); }
					}
					ui.unindent();
				}
				#end
				if (ui.panel(Id.handle({selected: true}), "Log")) {
					ui.indent();

					final h = Id.handle();
					h.selected = DebugConsole.traceWithPosition;
					DebugConsole.traceWithPosition = ui.check(h, "Print With Position");
					if (ui.isHovered) ui.tooltip("Whether to prepend the position of print/trace statements to the printed text");

					if (ui.button("Clear")) {
						lastTraces[0] = "";
						lastTraces.splice(1, lastTraces.length - 1);
					}
					if (ui.isHovered) ui.tooltip("Clear the log output");

					final eh = ui.t.ELEMENT_H;
					ui.t.ELEMENT_H = ui.fontSize;
					for (t in lastTraces) ui.text(t);
					ui.t.ELEMENT_H = eh;

					ui.unindent();
				}
			}

			if (watchNodes.length > 0 && ui.tab(htab, "Watch")) {
				var lineCounter = 0;
				for (n in watchNodes) {
					if (ui.panel(Id.handle({selected: true}).nest(lineCounter), n.tree.object.name + "." + n.tree.name + "." + n.name + " : ")){
						ui.indent();
						ui.g.color = ui.t.SEPARATOR_COL;
						ui.g.fillRect(0, ui._y, ui._windowW, ui.ELEMENT_H());
						ui.g.color = 0xffffffff;
						ui.text(Std.string(n.get(0)));
						ui.unindent();
					}
					lineCounter++;
				}
			}

			ui.separator();
		}
		isDebugConsoleHovered = isDebugConsoleHovered || isZuiWindowHovered(hwin, wx, wy);

		// Draw trait debug windows
		var handleWinTrait = Id.handle();
		for (trait in selectedTraits) {
			var objectID = trait.object.uid;
			var traitIndex = trait.object.traits.indexOf(trait);

			var handleWindow = handleWinTrait.nest(objectID).nest(traitIndex);
			// This solution is not optimal, dragged windows will change their
			// position if the selectedTraits array is changed.
			wx = positionConsole == PositionStateEnum.Left ? wx + ww + 8 : wx - ww - 8;
			wy = 0;

			handleWindow.redraws = 1;
			ui.window(handleWindow, wx, wy, ww, wh, true);

			if (ui.button("Close Trait View")) {
				selectedTraits.remove(trait);
				handleWinTrait.nest(objectID).unnest(traitIndex);
				continue;
			}

			ui.row([1/2, 1/2]);
			ui.text("Trait:");
			ui.text(Type.getClassName(Type.getClass(trait)), Align.Right);
			ui.row([1/2, 1/2]);
			ui.text("Extends:");
			ui.text(Type.getClassName(Type.getSuperClass(Type.getClass(trait))), Align.Right);
			ui.row([1/2, 1/2]);
			ui.text("Object:");
			ui.text(trait.object.name, Align.Right);
			ui.separator();

			if (ui.panel(Id.handle().nest(objectID).nest(traitIndex), "Attributes")) {
				ui.indent();

				for (fieldName in Reflect.fields(trait)) {
					ui.row([1/2, 1/2]);
					ui.text(fieldName + "");

					var fieldValue = Reflect.field(trait, fieldName);

					ui.text(dynamicToUIString(fieldValue), Align.Right);
				}

				ui.unindent();
			}
			isDebugConsoleHovered = isDebugConsoleHovered || isZuiWindowHovered(handleWindow, wx, wy);
		}

		ui.end(bindG);
		if (bindG) g.begin(false);
	}

	function dynamicToUIString(value: Dynamic): String {
		final valueClass = Type.getClass(value);

		// Don't convert objects to string, Haxe includes _all_ object fields
		// (recursively) by default which does not fit in the UI and can cause performance issues
		if (Reflect.isObject(value) && valueClass != String) {
			if (valueClass != null) {
				return '<${Type.getClassName(valueClass)}>';
			}
			// Given value has no class, anonymous data structures for example
			return "<???>";
		}

		return Std.string(value);
	}

	function update() {
		armory.trait.WalkNavigation.enabled = !(ui.isScrolling || ui.dragHandle != null);
		updateTime += iron.App.updateTime;
		animTime += iron.object.Animation.animationTime;
	#if arm_physics
		physTime += armory.trait.physics.PhysicsWorld.physTime;
	#end
	#if arm_shadowmap_atlas
		smaLogicTime += armory.renderpath.Inc.shadowsLogicTime;
		smaRenderTime += armory.renderpath.Inc.shadowsRenderTime;
	#end
	}

	function isZuiWindowHovered(hwin: zui.Zui.Handle, wx: Int, wy: Int): Bool {
		var mouseWindowSpaceX = mouse.x - wx - hwin.dragX;
		var mouseWindowSpaceY = mouse.y - wy - hwin.dragY;

		return (
			   mouseWindowSpaceX >= 0 && mouseWindowSpaceX < hwin.lastMaxX
			&& mouseWindowSpaceY >= 0 && mouseWindowSpaceY < hwin.lastMaxY
		);
	}

	static function roundfp(f: Float, precision = 2): Float {
		f *= Math.pow(10, precision);
		return Math.round(f) / Math.pow(10, precision);
	}

	public static function getVisible(): Bool {
		return visible;
	}

	public static function setVisible(value: Bool) {
		visible = value;
	}

	public static function getScale(): Float {
		return ui.SCALE();
	}

	public static function setScale(value: Float) {
		ui.setScale(value);
	}

	public static function setPosition(value: PositionStateEnum) {
		positionConsole = value;
	}

	public static function getPosition(): PositionStateEnum {
		return positionConsole;
	}

	public static function getFramerate(): Float {
		return fpsAvg;
	}
#end
}

enum abstract PositionStateEnum(Int) from Int {
	var Left;
	var Center;
	var Right;
}
