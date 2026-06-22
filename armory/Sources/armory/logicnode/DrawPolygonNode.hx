package armory.logicnode;

import kha.Color;
import kha.math.Vector2;
import armory.renderpath.RenderToTexture;

#if arm_ui
using zui.GraphicsExtension;
#end

class DrawPolygonNode extends LogicNode {
	static inline var numStaticInputs = 6;

	var vertices: Array<Vector2>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
		RenderToTexture.ensure2DContext("DrawPolygonNode");

		if (vertices == null) {
			final numDynamicInputs = inputs.length - numStaticInputs;
			final numPoints = numDynamicInputs >>> 1;

			// Preallocate
			vertices = [];
			vertices.resize(numPoints);
			for (i in 0...vertices.length) {
				vertices[i] = new Vector2();
			}
		}

		for (i in 0...vertices.length) {
			vertices[i].x = inputs[numStaticInputs + i * 2 + 0].get();
			vertices[i].y = inputs[numStaticInputs + i * 2 + 1].get();
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
