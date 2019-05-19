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

class DebugDraw {

	static var inst:DebugDraw = null;

	public var color:kha.Color = 0xffff0000;
	public var strength = 0.02;

	var vertexBuffer:VertexBuffer;
	var indexBuffer:IndexBuffer;
	var pipeline:PipelineState;

	var vp:Mat4;
	var vpID:ConstantLocation;

	var vbData:kha.arrays.Float32Array;
	var ibData:kha.arrays.Uint32Array;

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
		pipeline.fragmentShader = kha.Shaders.line_deferred_frag;
		#else
		pipeline.fragmentShader = kha.Shaders.line_frag;
		#end
		pipeline.vertexShader = kha.Shaders.line_vert;
		pipeline.depthWrite = true;
		pipeline.depthMode = CompareMode.Less;
		pipeline.cullMode = CullMode.None;
		pipeline.compile();
		vpID = pipeline.getConstantLocation("VP");
		vp = Mat4.identity();

		vertexBuffer = new VertexBuffer(maxVertices, structure, Usage.DynamicUsage);
		indexBuffer = new IndexBuffer(maxIndices, Usage.DynamicUsage);
	}

	static var g:kha.graphics4.Graphics;

	public static function notifyOnRender(f:DebugDraw->Void) {
		if (inst == null) inst = new DebugDraw();
		iron.RenderPath.notifyOnContext("mesh", function(g4:kha.graphics4.Graphics, i:Int, len:Int) {
			g = g4;
			if (i == 0) inst.begin();
			f(inst);
			if (i == len - 1) inst.end();
		});
	}

	static var v:Vec4;
	static var vx = new Vec4();
	static var vy = new Vec4();
	static var vz = new Vec4();
	public function bounds(t:iron.object.Transform) {
		v = t.world.getLoc();
		var dx = t.dim.x / 2;
		var dy = t.dim.y / 2;
		var dz = t.dim.z / 2;
		
		var up = t.world.up();
		var look = t.world.look();
		var right = t.world.right();
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
	function lineb(a:Int, b:Int, c:Int, d:Int, e:Int, f:Int) {
		v1.setFrom(v);
		t.setFrom(vx); t.mult(a); v1.add(t);
		t.setFrom(vy); t.mult(b); v1.add(t);
		t.setFrom(vz); t.mult(c); v1.add(t);

		v2.setFrom(v);
		t.setFrom(vx); t.mult(d); v2.add(t);
		t.setFrom(vy); t.mult(e); v2.add(t);
		t.setFrom(vz); t.mult(f); v2.add(t);

		linev(v1, v2);
	}

	public inline function linev(v1:Vec4, v2:Vec4) {
		line(v1.x, v1.y, v1.z, v2.x, v2.y, v2.z);
	}

	public function line(x1:Float, y1:Float, z1:Float, x2:Float, y2:Float, z2:Float) {
		
		if (lines >= maxLines) { end(); begin(); }

		var camera = iron.Scene.active.camera;
		var l = camera.right();
		l.add(camera.up());

		var i = lines * 24; // 4 * 6 (structure len)
		vbData.set(i    , x1);
		vbData.set(i + 1, y1);
		vbData.set(i + 2, z1);
		vbData.set(i + 3, color.R);
		vbData.set(i + 4, color.G);
		vbData.set(i + 5, color.B);

		vbData.set(i + 6, x2);
		vbData.set(i + 7, y2);
		vbData.set(i + 8, z2);
		vbData.set(i + 9, color.R);
		vbData.set(i + 10, color.G);
		vbData.set(i + 11, color.B);

		vbData.set(i + 12, x2 + strength * l.x);
		vbData.set(i + 13, y2 + strength * l.y);
		vbData.set(i + 14, z2 + strength * l.z);
		vbData.set(i + 15, color.R);
		vbData.set(i + 16, color.G);
		vbData.set(i + 17, color.B);

		vbData.set(i + 18, x1 + strength * l.x);
		vbData.set(i + 19, y1 + strength * l.y);
		vbData.set(i + 20, z1 + strength * l.z);
		vbData.set(i + 21, color.R);
		vbData.set(i + 22, color.G);
		vbData.set(i + 23, color.B);

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
}

#end
