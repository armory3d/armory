package armory.trait.internal;

import kha.Image;
import kha.Video;
import iron.Trait;
import iron.object.MeshObject;

class MovieTexture extends Trait {

	var video:Video;
	public static var image:Image;
	public static var created = false;
	
	var videoName:String;

	function pow(pow: Int): Int {
		var ret = 1;
		for (i in 0...pow) ret *= 2;
		return ret;
	}

	function getPower2(i: Int): Int {
		var power = 0;
		while(true) {
			var res = pow(power);
			if (res >= i) return res;
			power++;
		}
	}

	public function new(videoName:String) {
		super();
		
		this.videoName = videoName;

		if (!created) {
			created = true;
			notifyOnInit(init);
		}
	}

	function init() {
		iron.data.Data.getVideo(videoName, function(vid:kha.Video) {
			video = vid;
			video.play(true);

			image = Image.createRenderTarget(getPower2(video.width()), getPower2(video.height()));

			var o = cast(object, iron.object.MeshObject);
			o.materials[0].contexts[0].textures[0] = image; // Override diffuse texture
			notifyOnRender2D(render);
		});
	}
	
	function render(g:kha.graphics2.Graphics) {
		g.end();
		
		var g2 = image.g2;
		g2.begin(true, 0xff000000);
		g2.color = 0xffffffff;
		g2.drawVideo(video, 0, 0, image.width, image.height);
		g2.end();
		
		g.begin(false);
	}
}
