package armory.trait.internal;

import iron.Trait;
#if arm_ui
import zui.Zui;
import zui.Canvas;
#end

class CanvasScript extends Trait {

#if arm_ui

	var cui: Zui;
	var canvas:TCanvas = null;

	public var ready(get, null):Bool;
	function get_ready():Bool { return canvas != null; }

	public function new(canvasName:String) {
		super();

		iron.data.Data.getBlob(canvasName + '.json', function(blob:kha.Blob) {

			iron.data.Data.getFont("font_default.ttf", function(f:kha.Font) {

				cui = new Zui({font: f, theme: zui.Themes.light});			
				var c:TCanvas = haxe.Json.parse(blob.toString());
				
				if (c.assets == null || c.assets.length == 0) canvas = c;
				// Load canvas assets
				else {
					var loaded = 0;
					for (asset in c.assets) {
						var file = asset.name;
						iron.data.Data.getImage(file, function(image:kha.Image) {
							Canvas.assetMap.set(asset.id, image);
							if (++loaded >= c.assets.length) canvas = c;
						});
					}
				}
			});
		});

		notifyOnRender2D(function(g:kha.graphics2.Graphics) {
			if (canvas == null) return;

			var events = Canvas.draw(cui, canvas, g);

			for (e in events) {
				var all = armory.system.Event.get(e);
				if (all != null) for (entry in all) entry.onEvent();
			}

			if (onReady != null) { onReady(); onReady = null; }
		});
	}

	var onReady:Void->Void = null;
	public function notifyOnReady(f:Void->Void) {
		onReady = f;
	}

	// Defines layout
	public function getElement(name:String):TElement {
		for (e in canvas.elements) if (e.name == name) return e;
		return null;
	}
	
	// Returns canvas array of elements
	public function getElements():Array<TElement> {
		return canvas.elements;
	}

	// Contains data
	@:access(zui.Canvas)
	@:access(zui.Handle)
	public function getHandle(name:String):Handle {
		// Consider this a temporary solution
		return Canvas.h.children[getElement(name).id];
	}

#else

	public function new(canvasName:String) { super(); }

#end
}
