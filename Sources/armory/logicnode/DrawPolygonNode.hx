package armory.logicnode;

import kha.Color;
import kha.math.Vector2;

using kha.graphics2.GraphicsExtension;

class DrawPolygonNode extends LogicNode {
	static inline var numStaticInputs = 6;

	var vertices: Array<Vector2>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawPolygonNode");

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
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (inputs[2].get()) {
			OnRender2DNode.g.fillPolygon(inputs[4].get(), inputs[5].get(), vertices);
		} else {
			OnRender2DNode.g.drawPolygon(inputs[4].get(), inputs[5].get(), vertices, inputs[3].get());
		}

		runOutput(0);
	}
}
