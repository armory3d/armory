package armory.trait.internal;

import kha.Image;
import kha.Video;

import iron.Trait;
import iron.object.MeshObject;

/**
	Replaces the diffuse texture of the first material of the trait's object
	with a video texture.

	@see https://github.com/armory3d/armory_examples/tree/master/material_movie
**/
class MovieTexture extends Trait {

	/**
		Caches all render targets used by this trait for re-use when having
		multiple videos of the same size. The lookup only takes place on trait
		initialization.

		Map layout: `[width => [height => image]]`
	**/
	static var imageCache: Map<Int, Map<Int, Image>> = new Map();

	var video: Video;
	var image: Image;

	var videoName: String;

	function pow(pow: Int): Int {
		var ret = 1;
		for (i in 0...pow) ret *= 2;
		return ret;
	}

	function getPower2(i: Int): Int {
		var power = 0;
		while (true) {
			var res = pow(power);
			if (res >= i) return res;
			power++;
		}
	}

	public function new(videoName: String) {
		super();

		this.videoName = videoName;

		notifyOnInit(init);
	}

	function init() {
		iron.data.Data.getVideo(videoName, function(vid: kha.Video) {
			video = vid;
			video.play(true);

			var w = getPower2(video.width());
			var h = getPower2(video.height());

			// Lazily fill the outer map
			var hMap: Map<Int, Image> = imageCache[w];
			if (hMap == null) {
				imageCache[w] = new Map<Int, Image>();
			}

			image = imageCache[w][h];
			if (image == null) {
				imageCache[w][h] = image = Image.createRenderTarget(w, h);
			}

			var o = cast(object, MeshObject);
			o.materials[0].contexts[0].textures[0] = image; // Override diffuse texture
			notifyOnRender2D(render);
		});
	}

	function render(g: kha.graphics2.Graphics) {
		g.end();

		var g2 = image.g2;
		g2.begin(true, 0xff000000);
		g2.color = 0xffffffff;
		g2.drawVideo(video, 0, 0, image.width, image.height);
		g2.end();

		g.begin(false);
	}
}
