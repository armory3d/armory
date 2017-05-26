package armory.trait.internal;

import iron.Trait;
import zui.Zui;
import zui.Canvas;

@:keep
class CanvasScript extends Trait {

	var cui: Zui;
	var canvas:TCanvas = null;

	public function new(canvasName:String) {
		super();

		notifyOnInit(function() {

			iron.data.Data.getBlob(canvasName + '.json', function(blob:kha.Blob) {

				kha.Assets.loadFont("droid_sans", function(f:kha.Font) {

					cui = new Zui({font: f});			
					canvas = haxe.Json.parse(blob.toString());
				});
			});
		});

		notifyOnRender2D(function(g:kha.graphics2.Graphics) {
			if (canvas == null) return;

			var events = Canvas.draw(cui, canvas, g);

			for (e in events) {
				var all = armory.system.Event.get(e);
				for (entry in all) entry.onEvent();
			}
		});
	}
}
