package armory.logicnode;

import iron.object.CameraObject;
import kha.Color;

class WriteImageNode extends LogicNode {

	var file: String;
	var camera: CameraObject;
	var renderTarget: kha.Image;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		// Relative or absolute path to file
		file = inputs[1].get();

		assert(Error, iron.App.w() % inputs[3].get() == 0 && iron.App.h() % inputs[4].get() == 0, "Aspect ratio must match display resolution ratio");

		camera = inputs[2].get();
		renderTarget = kha.Image.createRenderTarget(inputs[3].get(), inputs[4].get(),
			kha.graphics4.TextureFormat.RGBA32,
			kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

		tree.notifyOnRender(render);
		
	}

	function render(g: kha.graphics4.Graphics) {

		var ready = false;
		final sceneCam = iron.Scene.active.camera;
		final oldRT = camera.renderTarget;

		iron.Scene.active.camera = camera;
		camera.renderTarget = renderTarget;

		camera.renderFrame(g);

		var tex = camera.renderTarget;

		camera.renderTarget = oldRT;
		iron.Scene.active.camera = sceneCam;

		if (inputs[9].get()){

			tex = kha.Image.createRenderTarget(inputs[3].get(), inputs[4].get(),
				kha.graphics4.TextureFormat.RGBA32,
				kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

			tex.g2.begin(true, Color.Transparent);

			tex.g2.color = Color.White;
			tex.g2.drawScaledImage(renderTarget, 0, 0, inputs[3].get(), inputs[4].get());

			var scl = inputs[3].get() / iron.App.w();

			if (kha.Image.renderTargetsInvertedY()){
				tex.g2.scale(scl, -scl);
				tex.g2.translate(0, inputs[4].get());
			}
			else
				tex.g2.scale(scl, scl);

			for (f in @:privateAccess iron.App.traitRenders2D){
		    	f(tex.g2);
		    }
		    
		    tex.g2.end();

		}

		var pixels = tex.getPixels();

		for (i in 0...pixels.length){
			if (pixels.get(i) != 0){ ready = true; break; }
		}

		//wait for getPixels ready
		if (ready) { 

			var tx = inputs[5].get();
			var ty = inputs[6].get();
			var tw = inputs[7].get();
			var th = inputs[8].get();

			var bo = new haxe.io.BytesOutput();
			var rgb = haxe.io.Bytes.alloc(tw * th * 4);
			for (j in ty...ty + th) {
				for (i in tx...tx + tw) {
					var k = j * tex.width + i;
					var m =  (j - ty) * tw + i - tx;
					
					#if kha_krom
					var l = k;
					#elseif kha_html5
					var l = (tex.height - j) * tex.width + i;
					#end

					//ARGB 0xff
					rgb.set(m * 4 + 0, pixels.get(l * 4 + 3));
					rgb.set(m * 4 + 1, pixels.get(l * 4 + 0)); 
					rgb.set(m * 4 + 2, pixels.get(l * 4 + 1));
					rgb.set(m * 4 + 3, pixels.get(l * 4 + 2));
				}
			}

			var imgwriter = new iron.format.bmp.Writer(bo);
			imgwriter.write(iron.format.bmp.Tools.buildFromARGB(tw, th, rgb));

			#if kha_krom
			Krom.fileSaveBytes(Krom.getFilesLocation() +  "/" + file, bo.getBytes().getData());
	
			#elseif kha_html5
			var blob = new js.html.Blob([bo.getBytes().getData()], {type: "application"});
	        var url = js.html.URL.createObjectURL(blob);
	        var a = cast(js.Browser.document.createElement("a"), js.html.AnchorElement);
	        a.href = url;
	        a.download = file;
	        a.click();
	        js.html.URL.revokeObjectURL(url);
			#end

			runOutput(0);

			tree.removeRender(render);

		}

	}

}
