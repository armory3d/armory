package armory.trait.internal;

import iron.Trait;
#if arm_ui
import iron.Scene;
import zui.Zui;
import armory.ui.Canvas;
#end

class CanvasScript extends Trait {

	public var cnvName: String;
#if arm_ui

	var cui: Zui;
	var canvas: TCanvas = null;

	public var ready(get, null): Bool;
	function get_ready(): Bool { return canvas != null; }

	var onReadyFuncs: Array<Void->Void> = null;

	/**
		Create new CanvasScript from canvas
		@param canvasName Name of the canvas
		@param font font file (Optional)
	**/
	public function new(canvasName: String, font: String = Canvas.defaultFontName) {
		super();
		cnvName = canvasName;

		iron.data.Data.getBlob(canvasName + ".json", function(blob: kha.Blob) {

			iron.data.Data.getBlob("_themes.json", function(tBlob: kha.Blob) {
				if (@:privateAccess tBlob.get_length() != 0) {
					Canvas.themes = haxe.Json.parse(tBlob.toString());
				}
				else {
					trace("\"_themes.json\" is empty! Using default theme instead.");
				}

				if (Canvas.themes.length == 0) {
					Canvas.themes.push(armory.ui.Themes.light);
				}

				iron.data.Data.getFont(font, function(defaultFont: kha.Font) {
					var c: TCanvas = Canvas.parseCanvasFromBlob(blob);
					if (c.theme == null) c.theme = Canvas.themes[0].NAME;
					cui = new Zui({font: defaultFont, theme: Canvas.getTheme(c.theme)});

					if (c.assets == null || c.assets.length == 0) canvas = c;
					else { // Load canvas assets
						var loaded = 0;
						for (asset in c.assets) {
							var file = asset.name;
							if (Canvas.isFontAsset(file)) {
								iron.data.Data.getFont(file, function(f: kha.Font) {
									Canvas.assetMap.set(asset.id, f);
									if (++loaded >= c.assets.length) canvas = c;
								});
							} else {
								iron.data.Data.getImage(file, function(image: kha.Image) {
									Canvas.assetMap.set(asset.id, image);
									if (++loaded >= c.assets.length) canvas = c;
								});
							}
						}
					}
				});
			});
		});

		notifyOnRender2D(function(g: kha.graphics2.Graphics) {
			if (canvas == null) return;

			setCanvasDimensions(kha.System.windowWidth(), kha.System.windowHeight());
			var events = Canvas.draw(cui, canvas, g);

			for (e in events) {
				var all = armory.system.Event.get(e);
				if (all != null) for (entry in all) entry.onEvent();
			}

			if (onReadyFuncs != null) {
				for (f in onReadyFuncs) {
					f();
				}
				onReadyFuncs.resize(0);
			}
		});
	}

	/**
		Run the given callback function `f` when the canvas is loaded and ready.

		@see https://github.com/armory3d/armory/wiki/traits#canvas-trait-events
	**/
	public function notifyOnReady(f: Void->Void) {
		if (onReadyFuncs == null) onReadyFuncs = [];
		onReadyFuncs.push(f);
	}

	/**
		Returns an element of the canvas.
		@param name The name of the element
		@return TElement
	**/
	public function getElement(name: String): TElement {
		for (e in canvas.elements) if (e.name == name) return e;
		return null;
	}

	/**
		Returns an array of the elements of the canvas.
		@return Array<TElement>
	**/
	public function getElements(): Array<TElement> {
		return canvas.elements;
	}

	/**
		Returns the canvas object of this trait.
		@return TCanvas
	**/
	public function getCanvas(): Null<TCanvas> {
		return canvas;
	}

	/**
		Set the UI scale factor.
	**/
	public inline function setUiScale(factor: Float) {
		cui.setScale(factor);
	}

	/**
		Get the UI scale factor.
	**/
	public inline function getUiScale(): Float {
		return cui.ops.scaleFactor;
	}

	@:deprecated("Please use setCanvasVisible() instead")
	public inline function setCanvasVisibility(visible: Bool) {
		setCanvasVisible(visible);
	}

	/**
		Set whether the active canvas is visible.

		Note that elements of invisible canvases are not rendered and computed,
		so it is not possible to interact with those elements on the screen.
	**/
	public inline function setCanvasVisible(visible: Bool) {
		canvas.visible = visible;
	}

	/**
		Get whether the active canvas is visible.
	**/
	public inline function getCanvasVisible(): Bool {
		return canvas.visible;
	}

	/**
		Set dimensions of canvas
		@param x Width
		@param y Height
	**/
	public function setCanvasDimensions(x: Int, y: Int){
		canvas.width = x;
		canvas.height = y;
	}
	/**
		Set font size of the canvas
		@param fontSize Size of font to be setted
	**/
	public function setCanvasFontSize(fontSize: Int) {
		cui.t.FONT_SIZE = fontSize;
		cui.setScale(cui.ops.scaleFactor);
	}

	public function getCanvasFontSize(): Int {
		return cui.t.FONT_SIZE;
	}

	public function setCanvasInputTextFocus(e: Handle, focus: Bool) {
		if (focus == true){
			@:privateAccess cui.startTextEdit(e);
		} else {
			@:privateAccess cui.deselectText();
		}
	}

	// Contains data
	@:access(armory.ui.Canvas)
	@:access(zui.Handle)
	public function getHandle(name: String): Handle {
		// Consider this a temporary solution
		return Canvas.h.children[getElement(name).id];
	}

	public static function getActiveCanvas(): CanvasScript {
		var activeCanvas = Scene.active.getTrait(CanvasScript);
		if (activeCanvas == null) activeCanvas = Scene.active.camera.getTrait(CanvasScript);

		assert(Error, activeCanvas != null, "Could not find a canvas trait on the active scene or camera");

		return activeCanvas;
	}

#else

	public function new(canvasName: String) { super(); cnvName = canvasName; }

#end
}
