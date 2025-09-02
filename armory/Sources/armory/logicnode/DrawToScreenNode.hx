package armory.logicnode;

import iron.math.Vec4;
import kha.Image;
import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawToScreenNode extends LogicNode {
	var img: Image;
	var colorVec: Vec4;
	var anchorH: Int;
	var anchorV: Int;
	var x: Float;
	var y: Float;
	var width: Float;
	var height: Float;
	var sx: Float;
	var sy: Float;
	var swidth: Float;
	var sheight: Float;
	var angle: Float;

	var drawx: Float;
	var drawy: Float;

	public function new(tree: LogicTree) {
		super(tree);	
	}

	override function run(from: Int) {

		if (from == 0){
			
			if (img == null){
				runOutput(0);
				return;
			}

			colorVec = inputs[4].get();
			anchorH = inputs[5].get();
			anchorV = inputs[6].get();
			x = inputs[7].get();
			y = inputs[8].get();
			width = inputs[9].get();
			height = inputs[10].get();
			sx = inputs[11].get();
			sy = inputs[12].get();
			swidth = inputs[13].get();
			sheight = inputs[14].get();
			angle = inputs[15].get();

			drawx = x - 0.5 * width * anchorH;
			drawy = y - 0.5 * height * anchorV;
			
			RenderToTexture.g.rotate(angle, x, y);
			RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
			RenderToTexture.g.drawScaledSubImage(img, sx, sy, swidth, sheight, drawx, drawy, width, height);
			RenderToTexture.g.rotate(-angle, x, y);

			runOutput(0);

		} else {

			if (img == null)
				img = kha.Image.createRenderTarget(inputs[2].get(), inputs[3].get(),
					kha.graphics4.TextureFormat.RGBA32,
					kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

			RenderToTexture.ensureEmptyRenderTarget("DrawToScreenNode");
			img.g2.begin(inputs[16].get(), Color.Transparent);
			RenderToTexture.g = img.g2;
			runOutput(1);
			RenderToTexture.g = null;
			img.g2.end();

		}

	}


		

}
