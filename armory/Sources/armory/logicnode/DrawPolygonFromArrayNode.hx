package armory.logicnode;

import kha.Color;
import kha.math.Vector2;
import armory.renderpath.RenderToTexture;

#if arm_ui
using zui.GraphicsExtension;
#end

class DrawPolygonFromArrayNode extends LogicNode {

	var vertices: Array<Vector2>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
		RenderToTexture.ensure2DContext("DrawPolygonNode");

		var vertArr: Dynamic = inputs[6].get();

		if (vertices == null) {
			// Preallocate
			vertices = [];
			vertices.resize(vertArr.length);
			for (i in 0...vertices.length) {
				vertices[i] = new Vector2();
			}
		}

		for (i in 0...vertArr.length) {
			if (Std.isOfType(vertArr[i], iron.math.Vec4) || Std.isOfType(vertArr[i], iron.math.Vec3)){
				vertices[i].x = vertArr[i].x;
				vertices[i].y = vertArr[i].y;
			} else {
				assert(Error, vertArr[i].length >= 2, "Array positions must be an array of two dimensions (X, Y)");
				vertices[i].x = vertArr[i][0];
				vertices[i].y = vertArr[i][1];
			}
		}

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (inputs[2].get()) {
			RenderToTexture.g.fillPolygon(inputs[4].get(), inputs[5].get(), vertices);
		} else {
			RenderToTexture.g.drawPolygon(inputs[4].get(), inputs[5].get(), vertices, inputs[3].get());
		}
		#end

		runOutput(0);
	}
}
