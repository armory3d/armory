package armory.logicnode;

import iron.math.Vec4;
import kha.Color;
import kha.Image;

class GetImageColorNode extends LogicNode {

	public var property0: String;
	var renderTarget: Image = null;

	public function new(tree: LogicTree) {
		super(tree);
		renderTarget = Image.createRenderTarget(iron.App.w(), iron.App.h(), kha.graphics4.TextureFormat.RGBA32,
			kha.graphics4.DepthStencilFormat.NoDepthAndStencil);
	}

	override function get(from: Int): Dynamic {

		var i: Int;
		var j: Int;

		if (property0 == 'Image'){
			i = inputs[1].get();
			j = inputs[2].get();
		} else {
			i = inputs[0].get();
			j = inputs[1].get();
		}

		renderTarget.g2.begin(true, Color.Transparent);

		renderTarget.g2.color = Color.White;

		if (property0 == 'Render' || property0 == 'Render&Render2D'){
			if (armory.renderpath.RenderPathCreator.finalTarget != null){
				var img: Image = iron.RenderPath.active.renderTargets.get("buf").image;
				renderTarget.g2.drawScaledImage(img, 0, 0, iron.App.w(), iron.App.h());
			}
		}

		if (Image.renderTargetsInvertedY()){
			renderTarget.g2.scale(1, -1);
			renderTarget.g2.translate(0, renderTarget.height);
		}

		if (property0 == 'Image'){
			var img: Image;
			iron.data.Data.getImage(inputs[0].get(), (image: Image) -> {
				img = image;
			});
			if(img != null)
				renderTarget.g2.drawScaledImage(img, 0, 0, img.width, img.height);
		}

		if (property0.indexOf('2D') > 0)
			for (f in @:privateAccess iron.App.traitRenders2D)
		    	f(renderTarget.g2);

		if (Image.renderTargetsInvertedY()){
			renderTarget.g2.scale(1, -1);
			renderTarget.g2.translate(0, renderTarget.height);
		}

	    renderTarget.g2.end();

	    var pixels = renderTarget.getPixels();

		var k = j * renderTarget.width + i;
		
		#if kha_krom
		var l = k;
		#elseif kha_html5
		var l = (renderTarget.height - j) * renderTarget.width + i;
		#end

		var r = pixels.get(l * 4 + 0)/255;
		var g = pixels.get(l * 4 + 1)/255;
		var b =	pixels.get(l * 4 + 2)/255;
		var a = pixels.get(l * 4 + 3)/255;

		var v = new Vec4(r, g, b, a);
		
		return v;

	}

}