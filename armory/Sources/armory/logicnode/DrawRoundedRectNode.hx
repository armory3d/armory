package armory.logicnode;

import kha.Color;
import kha.math.Vector2;
import armory.renderpath.RenderToTexture;

#if arm_ui
using zui.GraphicsExtension;
#end

class DrawRoundedRectNode extends LogicNode {

	var vertices: Array<Vector2>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
		RenderToTexture.ensure2DContext("DrawPolygonNode");

		final anchorH: Int = inputs[4].get();
		final anchorV: Int = inputs[5].get();
		final x: Float = inputs[8].get();
		final y: Float = inputs[9].get();
		final width: Float = inputs[10].get();
		final height: Float = inputs[11].get();
		final drawx = x - 0.5 * width * anchorH;
		final drawy = y - 0.5 * height * anchorV;
		final angle: Float = inputs[12].get();

		var vertArr: Dynamic = drawRoundedRect(drawx, drawy, width, height, inputs[7].get(), inputs[6].get());

		if (vertices == null || vertices.length != vertArr.length) {
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

		RenderToTexture.g.rotate(angle, x, y);
		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (inputs[2].get()) {
			RenderToTexture.g.fillPolygon(0, 0, vertices);
		} else {
			RenderToTexture.g.drawPolygon(0, 0, vertices, inputs[3].get());
		}
		#end

		RenderToTexture.g.rotate(-angle, x, y);
		runOutput(0);
	}

	function drawRoundedRect(x:Float, y:Float, width:Float, height:Float, radius:Float, segments:Int):Array<Array<Float>> {
        var vertices:Array<Array<Float>> = [];

        vertices.push([x + radius, y]);
        vertices.push([x + width - radius, y]);

        for (i in 0...segments) {
            var angle:Float = Math.PI / 2 * (segments - i) / segments;
            vertices.push([
                x + width - radius + Math.cos(angle) * radius,
                y + radius - Math.sin(angle) * radius
            ]);
        }

        vertices.push([x + width, y + radius]);
        vertices.push([x + width, y + height - radius]);

        for (i in 0...segments) {
            var angle:Float = Math.PI / 2 * i / segments;
            vertices.push([
                x + width - radius + Math.cos(angle) * radius,
                y + height - radius + Math.sin(angle) * radius
            ]);
        }
		
        vertices.push([x + width - radius, y + height]);
        vertices.push([x + radius, y + height]);

		for (i in 0...segments) {
            var angle:Float = Math.PI / 2 * (segments - i) / segments;
            vertices.push([
                x + radius - Math.cos(angle) * radius,
                y + height - radius + Math.sin(angle) * radius
            ]);
        }

        vertices.push([x, y + height - radius]);

        for (i in 0...segments) {
            var angle:Float = Math.PI / 2 * i / segments;
            vertices.push([
                x + radius - Math.cos(angle) * radius,
                y + radius - Math.sin(angle) * radius
            ]);
        }

        return vertices;
    }
}
