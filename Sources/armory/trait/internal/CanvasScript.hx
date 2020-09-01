package armory.trait.internal;

import iron.Trait;
#if arm_ui
import zui.Zui;
import zui.Canvas;
#end

class CanvasScript extends Trait {

#if arm_ui

	var cui: Zui;
	var canvas: TCanvas = null;

	public var ready(get, null): Bool;
	function get_ready(): Bool { return canvas != null; }

	/**
	 * Create new CanvasScript from canvas
	 * @param canvasName Name of the canvas
	 * @param font font file (Optional)
	 */
	public function new(canvasName: String, font: String = "font_default.ttf") {
		super();

		iron.data.Data.getBlob(canvasName + ".json", function(blob: kha.Blob) {

			iron.data.Data.getBlob("_themes.json", function(tBlob: kha.Blob) {
				if (tBlob.get_length() != 0) {
					Canvas.themes = haxe.Json.parse(tBlob.toString());
				}
				else {
					trace("\"_themes.json\" is empty! Using default theme instead.");
				}

				if (Canvas.themes.length == 0) {
					Canvas.themes.push(zui.Themes.light);
				}

				iron.data.Data.getFont(font, function(f: kha.Font) {
					var c: TCanvas = haxe.Json.parse(blob.toString());
					if (c.theme == null) c.theme = Canvas.themes[0].NAME;
					cui = new Zui({font: f, theme: Canvas.getTheme(c.theme)});

					if (c.assets == null || c.assets.length == 0) canvas = c;
					else { // Load canvas assets
						var loaded = 0;
						for (asset in c.assets) {
							var file = asset.name;
							iron.data.Data.getImage(file, function(image: kha.Image) {
								Canvas.assetMap.set(asset.id, image);
								if (++loaded >= c.assets.length) canvas = c;
							});
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

			if (onReady != null) { onReady(); onReady = null; }
		});
	}

	var onReady: Void->Void = null;
	public function notifyOnReady(f: Void->Void) {
		onReady = f;
	}

	/**
	 * Returns an element of the canvas.
	 * @param name The name of the element
	 * @return TElement
	 */
	public function getElement(name: String): TElement {
		for (e in canvas.elements) if (e.name == name) return e;
		return null;
	}

	/**
	 * Returns an array of the elements of the canvas.
	 * @return Array<TElement>
	 */
	public function getElements(): Array<TElement> {
		return canvas.elements;
	}

	/**
	 * Returns the canvas object of this trait.
	 * @return TCanvas
	 */
	public function getCanvas(): Null<TCanvas> {
		return canvas;
	}

	/**
	 * Set UI scale factor.
	 * @param factor Scale factor.
	 */
	 public function setUiScale(factor:Float) {
		cui.setScale(factor);
	}

	/**
	 * Set visibility of canvas
	 * @param visible Whether canvas should be visible or not
	*/
	public function setCanvasVisibility(visible: Bool){
		for (e in canvas.elements) e.visible = visible;
	}
	
	/**
	 * Set dimensions of canvas
	 * @param x Width
	 * @param y Height
	 */
	public function setCanvasDimensions(x: Int, y: Int){
		canvas.width = x;
		canvas.height = y;
	}
	/**
	 * Set font size of the canvas
	 * @param fontSize Size of font to be setted
	 */
	public function setCanvasFontSize(fontSize: Int) {
		cui.t.FONT_SIZE = fontSize;
	}

	// Contains data
	@:access(zui.Canvas)
	@:access(zui.Handle)
	public function getHandle(name: String): Handle {
		// Consider this a temporary solution
		return Canvas.h.children[getElement(name).id];
	}

#else

	public function new(canvasName: String) { super(); }

#end
}
