package armory.trait.internal;

#if arm_debug

import kha.graphics4.PipelineState;
import kha.graphics4.VertexStructure;
import kha.graphics4.VertexBuffer;
import kha.graphics4.IndexBuffer;
import kha.graphics4.VertexData;
import kha.graphics4.Usage;
import kha.graphics4.ConstantLocation;
import kha.graphics4.CompareMode;
import kha.graphics4.CullMode;
import iron.math.Vec4;
import iron.math.Mat4;
using armory.object.TransformExtension;

class DebugDraw {

	static var inst: DebugDraw = null;

	public var color: kha.Color = 0xffff0000;
	public var strength = 0.02;

	var vertexBuffer: VertexBuffer;
	var indexBuffer: IndexBuffer;
	var pipeline: PipelineState;

	var vp: Mat4;
	var vpID: ConstantLocation;

	var vbData: kha.arrays.ByteArray;
	var ibData: kha.arrays.Uint32Array;

	static inline var maxLines = 300;
	static inline var maxVertices = maxLines * 4;
	static inline var maxIndices = maxLines * 6;
	var lines = 0;

	function new() {
		inst = this;

		var structure = new VertexStructure();
		structure.add("pos", VertexData.Float3);
		structure.add("col", VertexData.Float3);
		pipeline = new PipelineState();
		pipeline.inputLayout = [structure];
		#if arm_deferred
		pipeline.fragmentShader = kha.Shaders.getFragment("line_deferred.frag");
		#else
		pipeline.fragmentShader = kha.Shaders.getFragment("line.frag");
		#end
		pipeline.vertexShader = kha.Shaders.getVertex("line.vert");
		pipeline.depthWrite = true;
		pipeline.depthMode = CompareMode.Less;
		pipeline.cullMode = CullMode.None;
		pipeline.compile();
		vpID = pipeline.getConstantLocation("ViewProjection");
		vp = Mat4.identity();

		vertexBuffer = new VertexBuffer(maxVertices, structure, Usage.DynamicUsage);
		indexBuffer = new IndexBuffer(maxIndices, Usage.DynamicUsage);
	}

	static var g: kha.graphics4.Graphics;

	public static function notifyOnRender(f: DebugDraw->Void) {
		if (inst == null) inst = new DebugDraw();
		iron.RenderPath.notifyOnContext("mesh", function(g4: kha.graphics4.Graphics, i: Int, len: Int) {
			g = g4;
			if (i == 0) inst.begin();
			f(inst);
			if (i == len - 1) inst.end();
		});
	}

	static var objPosition: Vec4;
	static var vx = new Vec4();
	static var vy = new Vec4();
	static var vz = new Vec4();
	public function bounds(transform: iron.object.Transform) {
		objPosition = transform.getWorldPosition();
		var dx = transform.dim.x / 2;
		var dy = transform.dim.y / 2;
		var dz = transform.dim.z / 2;

		var up = transform.world.up();
		var look = transform.world.look();
		var right = transform.world.right();
		up.normalize();
		look.normalize();
		right.normalize();

		vx.setFrom(right);
		vx.mult(dx);
		vy.setFrom(look);
		vy.mult(dy);
		vz.setFrom(up);
		vz.mult(dz);

		lineb(-1, -1, -1,  1, -1, -1);
		lineb(-1,  1, -1,  1,  1, -1);
		lineb(-1, -1,  1,  1, -1,  1);
		lineb(-1,  1,  1,  1,  1,  1);

		lineb(-1, -1, -1, -1,  1, -1);
		lineb(-1, -1,  1, -1,  1,  1);
		lineb( 1, -1, -1,  1,  1, -1);
		lineb( 1, -1,  1,  1,  1,  1);

		lineb(-1, -1, -1, -1, -1,  1);
		lineb(-1,  1, -1, -1,  1,  1);
		lineb( 1, -1, -1,  1, -1,  1);
		lineb( 1,  1, -1,  1,  1,  1);
	}

	static var v1 = new Vec4();
	static var v2 = new Vec4();
	static var t = new Vec4();
	function lineb(a: Int, b: Int, c: Int, d: Int, e: Int, f: Int) {
		v1.setFrom(objPosition);
		t.setFrom(vx); t.mult(a); v1.add(t);
		t.setFrom(vy); t.mult(b); v1.add(t);
		t.setFrom(vz); t.mult(c); v1.add(t);

		v2.setFrom(objPosition);
		t.setFrom(vx); t.mult(d); v2.add(t);
		t.setFrom(vy); t.mult(e); v2.add(t);
		t.setFrom(vz); t.mult(f); v2.add(t);

		linev(v1, v2);
	}

	public inline function linev(v1: Vec4, v2: Vec4) {
		line(v1.x, v1.y, v1.z, v2.x, v2.y, v2.z);
	}

	static var midPoint = new Vec4();
	static var midLine = new Vec4();
	static var corner1 = new Vec4();
	static var corner2 = new Vec4();
	static var corner3 = new Vec4();
	static var corner4 = new Vec4();
	static var cameraLook = new Vec4();
	public function line(x1: Float, y1: Float, z1: Float, x2: Float, y2: Float, z2: Float) {

		if (lines >= maxLines) { end(); begin(); }

		midPoint.set(x1 + x2, y1 + y2, z1 + z2);
		midPoint.mult(0.5);

		midLine.set(x1, y1, z1);
		midLine.sub(midPoint);

		var camera = iron.Scene.active.camera;
		cameraLook = camera.transform.getWorldPosition();
		cameraLook.sub(midPoint);

		var lineWidth = cameraLook.cross(midLine);
		lineWidth.normalize();
		lineWidth.mult(strength);

		corner1.set(x1, y1, z1).add(lineWidth);
		corner2.set(x1, y1, z1).sub(lineWidth);
		corner3.set(x2, y2, z2).sub(lineWidth);
		corner4.set(x2, y2, z2).add(lineWidth);

		var i = lines * 24; // 4 * 6 (structure len)
		addVbData(i, [corner1.x, corner1.y, corner1.z, color.R, color.G, color.B]);
		i += 6;
		addVbData(i, [corner2.x, corner2.y, corner2.z, color.R, color.G, color.B]);
		i += 6;
		addVbData(i, [corner3.x, corner3.y, corner3.z, color.R, color.G, color.B]);
		i += 6;
		addVbData(i, [corner4.x, corner4.y, corner4.z, color.R, color.G, color.B]);

		i = lines * 6;
		ibData[i    ] = lines * 4;
		ibData[i + 1] = lines * 4 + 1;
		ibData[i + 2] = lines * 4 + 2;
		ibData[i + 3] = lines * 4 + 2;
		ibData[i + 4] = lines * 4 + 3;
		ibData[i + 5] = lines * 4;

		lines++;
	}

	function begin() {
		lines = 0;
		vbData = vertexBuffer.lock();
		ibData = indexBuffer.lock();
	}

	function end() {
		vertexBuffer.unlock();
		indexBuffer.unlock();

		g.setVertexBuffer(vertexBuffer);
		g.setIndexBuffer(indexBuffer);
		g.setPipeline(pipeline);
		var camera = iron.Scene.active.camera;
		vp.setFrom(camera.V);
		vp.multmat(camera.P);
		g.setMatrix(vpID, vp.self);
		g.drawIndexedVertices(0, lines * 6);
	}

	inline function addVbData(i: Int, data: Array<Float>) {
		for (offset in 0...6) {
			vbData.setFloat32(i + offset, data[offset]);
		}
	}
}

#end
