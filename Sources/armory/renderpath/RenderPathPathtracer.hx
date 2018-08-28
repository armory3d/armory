package armory.renderpath;

#if kha_dxr

import kha.graphics5.CommandList;
import kha.graphics5.ConstantBuffer;
import kha.graphics5.RayTraceTarget;
import kha.graphics5.RayTracePipeline;
import kha.graphics5.AccelerationStructure;
import kha.graphics5.VertexBuffer;
import kha.graphics5.IndexBuffer;
import kha.graphics5.VertexStructure;
import kha.graphics5.VertexData;
import kha.graphics5.Usage;
import kha.graphics5.TextureFormat;

import iron.RenderPath;

class RenderPathPathtracer {

	#if (rp_renderer == "Pathtracer")

	static var path:RenderPath;
	static var ready = false;

	static inline var bufferCount = 2;
	static var currentBuffer = -1;
	static var commandList: CommandList;
	static var framebuffers = new haxe.ds.Vector<kha.graphics5.RenderTarget>(bufferCount);
	static var constantBuffer: ConstantBuffer;
	static var target: RayTraceTarget;
	static var pipeline: RayTracePipeline;
	static var accel: AccelerationStructure;
	static var frame = 0.0;

	@:access(iron.data.Geometry)
	public static function init(_path:RenderPath) {
		path = _path;

		kha.Assets.loadBlobFromPath("pt_raygeneration.o", function(rayShader:kha.Blob) {
			kha.Assets.loadBlobFromPath("pt_closesthit.o", function(hitShader:kha.Blob) {
				kha.Assets.loadBlobFromPath("pt_miss.o", function(missShader:kha.Blob) {
					
					iron.system.Tween.timer(0.2, function() {
						ready = true;
					
						// Command list
						commandList = new CommandList();
						for (i in 0...bufferCount) {
							framebuffers[i] = new kha.graphics5.RenderTarget(iron.App.w(), iron.App.h(), 16, false, TextureFormat.RGBA32,
							                                   -1, -i - 1 /* hack in an index for backbuffer render targets */);
						}
						commandList.end(); // TODO: Otherwise "Reset fails because the command list was not closed"

						// Pipeline
						constantBuffer = new ConstantBuffer(21 * 4);
						pipeline = new RayTracePipeline(commandList, rayShader, hitShader, missShader, constantBuffer);

						// Acceleration structure
						var structure = new VertexStructure();
						structure.add("pos", VertexData.Float3);
						structure.add("nor", VertexData.Float3);
						var geom = iron.Scene.active.meshes[0].data.geom;

						var vb = new VertexBuffer(Std.int(geom.positions.length / 3), structure, kha.graphics5.Usage.StaticUsage);
						var vba = vb.lock();
						iron.data.Geometry.buildVertices(vba, geom.positions, geom.normals);
						vb.unlock();

						var id = geom.indices[0];
						var ib = new IndexBuffer(id.length, kha.graphics5.Usage.StaticUsage);
						var iba = ib.lock();
						for (i in 0...iba.length) iba[i] = id[i];
						ib.unlock();

						accel = new AccelerationStructure(commandList, vb, ib);

						// Output
						target = new RayTraceTarget(iron.App.w(), iron.App.h());
					});
				});
			});
		});
	}

	public static function commands() {
		if (!ready) return;

		var g = iron.App.framebuffer.g5;
		currentBuffer = (currentBuffer + 1) % bufferCount;

		constantBuffer.lock();

		var cam = iron.Scene.active.camera;
		var ct = cam.transform;
		var helpMat = iron.math.Mat4.identity();
		helpMat.setFrom(cam.V);
		helpMat.multmat(cam.P);
		helpMat.getInverse(helpMat);
		constantBuffer.setFloat(0, ct.worldx());
		constantBuffer.setFloat(4, ct.worldy());
		constantBuffer.setFloat(8, ct.worldz());
		constantBuffer.setFloat(12, 1);
		
		constantBuffer.setFloat(16, helpMat._00);
		constantBuffer.setFloat(20, helpMat._01);
		constantBuffer.setFloat(24, helpMat._02);
		constantBuffer.setFloat(28, helpMat._03);
		constantBuffer.setFloat(32, helpMat._10);
		constantBuffer.setFloat(36, helpMat._11);
		constantBuffer.setFloat(40, helpMat._12);
		constantBuffer.setFloat(44, helpMat._13);
		constantBuffer.setFloat(48, helpMat._20);
		constantBuffer.setFloat(52, helpMat._21);
		constantBuffer.setFloat(56, helpMat._22);
		constantBuffer.setFloat(60, helpMat._23);
		constantBuffer.setFloat(64, helpMat._30);
		constantBuffer.setFloat(68, helpMat._31);
		constantBuffer.setFloat(72, helpMat._32);
		constantBuffer.setFloat(76, helpMat._33);
		
		constantBuffer.setFloat(80, frame);
		frame += 1.0;
		constantBuffer.unlock();

		g.begin(framebuffers[currentBuffer]);

		commandList.begin();
		
		g.setAccelerationStructure(accel);
		g.setRayTracePipeline(pipeline);
		g.setRayTraceTarget(target);
		
		g.dispatchRays(commandList);
		g.copyRayTraceTarget(commandList, framebuffers[currentBuffer], target);
		commandList.end();
		
		g.end();
		g.swapBuffers();
	}
	#end
}

#end
