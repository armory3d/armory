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

		tree.notifyOnRender2D(render2D);
		
	}

	override function run(from: Int) {

		if (img == null)
			img = kha.Image.createRenderTarget(inputs[1].get(), inputs[2].get(),
				kha.graphics4.TextureFormat.RGBA32,
				kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

		RenderToTexture.ensureEmptyRenderTarget("DrawToScreenNode");
		img.g2.begin(inputs[15].get(), Color.Transparent);
		RenderToTexture.g = img.g2;
		runOutput(0);
		RenderToTexture.g = null;
		img.g2.end();

	}

	function render2D(g:kha.graphics2.Graphics) {

		if (img == null) return;

		colorVec = inputs[3].get();
		anchorH = inputs[4].get();
		anchorV = inputs[5].get();
		x = inputs[6].get();
		y = inputs[7].get();
		width = inputs[8].get();
		height = inputs[9].get();
		sx = inputs[10].get();
		sy = inputs[11].get();
		swidth = inputs[12].get();
		sheight = inputs[13].get();
		angle = inputs[14].get();

		drawx = x - 0.5 * width * anchorH;
		drawy = y - 0.5 * height * anchorV;
		
		g.rotate(angle, x, y);
		g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
		g.drawScaledSubImage(img, sx, sy, swidth, sheight, drawx, drawy, width, height);
		g.rotate(-angle, x, y);
	}

}
