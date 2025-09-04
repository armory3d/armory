package armory.logicnode;

import kha.Color;
import iron.math.Vec4;
import armory.renderpath.RenderToTexture;

class DrawToImageNode extends LogicNode {

	var img: kha.Image = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var file: String = inputs[1].get();
		var colorVec: Vec4 = inputs[2].get();

		img = kha.Image.createRenderTarget(inputs[3].get(), inputs[4].get(),
			kha.graphics4.TextureFormat.RGBA32,
			kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

		RenderToTexture.ensureEmptyRenderTarget("DrawToImageNode");
		img.g2.begin();
		RenderToTexture.g = img.g2;
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
		RenderToTexture.g.fillRect(0, 0, img.width, img.height);
		runOutput(0);
		RenderToTexture.g = null;
		img.g2.end();

		var pixels = img.getPixels();

		var tx = inputs[5].get();
		var ty = inputs[6].get();
		var tw = inputs[7].get();
		var th = inputs[8].get();

		var bo = new haxe.io.BytesOutput();
		var rgb = haxe.io.Bytes.alloc(tw * th * 4);
		for (j in ty...ty + th) {
			for (i in tx...tx + tw) {
				var l = j * img.width + i;
				var m =  (j - ty) * tw + i - tx;

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
	}

}
