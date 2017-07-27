package armory.trait.internal;

import iron.Trait;
#if arm_ui
import zui.Zui;
import zui.Canvas;
#end

@:keep
class CanvasScript extends Trait {

#if arm_ui

	var cui: Zui;
	var canvas:TCanvas = null;

	public function new(canvasName:String) {
		super();

		notifyOnInit(function() {

			iron.data.Data.getBlob(canvasName + '.json', function(blob:kha.Blob) {

				kha.Assets.loadFont("droid_sans", function(f:kha.Font) {

					cui = new Zui({font: f});			
					var c:TCanvas = haxe.Json.parse(blob.toString());

					// Load canvas assets
					var loaded = 0;
					for (asset in c.assets) {
						var file = asset.file;
						iron.data.Data.getImage(file, function(image:kha.Image) {
							Canvas.assetMap.set(asset.id, image);
							if (++loaded >= c.assets.length) canvas = c;
						});
					}
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

#else

	public function new(canvasName:String) { super(); }

#end
}
