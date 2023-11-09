package armory.logicnode;

import iron.math.Vec4;
import kha.Video;
import kha.Color;
import armory.renderpath.RenderToTexture;



class DrawVideoNode extends LogicNode {
	var vidName: Dynamic;
	var lastVidName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}
	
	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawVideoNode");
		
		var vidData: Dynamic = inputs[1].get();
		var video = kha.js.Video.fromElement(vidData);
		final colorVec: Vec4 = inputs[2].get();
		final anchorH: Int = inputs[3].get();
		final anchorV: Int = inputs[4].get();
		final x: Float = inputs[5].get();
		final y: Float = inputs[6].get();
		final width: Float = inputs[7].get();
		final height: Float = inputs[8].get();
		final angle: Float = inputs[9].get();

		final drawx = x - 0.5 * width * anchorH;
		final drawy = y - 0.5 * height * anchorV;

		RenderToTexture.g.rotate(angle, x, y);
	

		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
		RenderToTexture.g.drawVideo(video, drawx, drawy, width, height);
		RenderToTexture.g.rotate(-angle, x, y);

		runOutput(0);
		 
	}
}
