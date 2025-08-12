package armory.logicnode;

import iron.math.Vec4;
import kha.Image;
import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawImageRenderNode extends LogicNode {
	var img: Image;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		if (from == 1)
			tree.notifyOnRender(render);
		else {

		RenderToTexture.ensure2DContext("DrawImageRenderNode");

		final colorVec: Vec4 = inputs[3].get();
		final anchorH: Int = inputs[4].get();
		final anchorV: Int = inputs[5].get();
		final x: Float = inputs[6].get();
		final y: Float = inputs[7].get();
		final width: Float = inputs[8].get();
		final height: Float = inputs[9].get();
		final sx: Float = inputs[10].get();
		final sy: Float = inputs[11].get();
		final swidth: Float = inputs[12].get();
		final sheight: Float = inputs[13].get();
		final angle: Float = inputs[14].get();

		final drawx = x - 0.5 * width * anchorH;
		final drawy = y - 0.5 * height * anchorV;

		RenderToTexture.g.rotate(angle, x, y);

		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (img != null){
			RenderToTexture.g.color = 0xff000000;
			RenderToTexture.g.fillRect(drawx, drawy,  width, height);
			RenderToTexture.g.color = 0xffffffff;
			RenderToTexture.g.drawScaledSubImage(img, sx, sy, swidth, sheight, drawx, drawy, width, height);
		}

		RenderToTexture.g.rotate(-angle, x, y);

		runOutput(0);

		}

	}

	function render(g: kha.graphics4.Graphics) {

		var camera = inputs[2].get();

		img = kha.Image.createRenderTarget(iron.App.w(), iron.App.h(),
			kha.graphics4.TextureFormat.RGBA32,
			kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

		final sceneCam = iron.Scene.active.camera;
		final oldRT = camera.renderTarget;

		iron.Scene.active.camera = camera;
		camera.renderTarget = img;

		camera.renderFrame(g);

		img = camera.renderTarget;

		if (inputs[15].get()){

			img = kha.Image.createRenderTarget(iron.App.w(), iron.App.h(),
				kha.graphics4.TextureFormat.RGBA32,
				kha.graphics4.DepthStencilFormat.NoDepthAndStencil);

			img.g2.begin(true, Color.Transparent);

			img.g2.color = Color.White;
			img.g2.drawImage(camera.renderTarget, 0, 0);

			if (kha.Image.renderTargetsInvertedY()){
				img.g2.scale(1, -1);
				img.g2.translate(0, iron.App.h());
			}
			else
				img.g2.scale(1, 1);

			for (f in @:privateAccess iron.App.traitRenders2D){
		    	f(img.g2);
		    }
		    
		    img.g2.end();

		}

		camera.renderTarget = oldRT;
		iron.Scene.active.camera = sceneCam;

		tree.removeRender(render);

	}

}
