package iron.object;

import kha.graphics4.Graphics;
import kha.graphics4.TextureFormat;
import kha.graphics4.DepthStencilFormat;
import kha.graphics4.CubeMap;
import iron.data.ProbeData;
import iron.data.CameraData;
import iron.data.SceneFormat;
import iron.math.Vec4;
import iron.math.Mat4;

class ProbeObject extends Object {

#if rp_probes

	public var data: ProbeData;
	public var renderTarget: kha.Image = null;
	public var camera: CameraObject = null;
	public var ready = false;

	// Cubemap update
	public var perFrame = false; // Update probe every frame
	public var redraw = true; // Update probe next frame

	var m1: Mat4;
	var m2: Mat4;
	var proben: Vec4;
	var probep: Vec4;
	// static var v = new Vec4();
	static var p = new Vec4();
	static var q = new Vec4();

	public function new(data: ProbeData) {
		super();
		this.data = data;
		Scene.active.probes.push(this);
		iron.App.notifyOnInit(init);
	}

	public override function remove() {
		if (Scene.active != null) Scene.active.probes.remove(this);
		// if (camera != null) camera.remove();
		super.remove();
	}

	function init() {
		probep = transform.world.getLoc();
		proben = transform.up().normalize();
		proben.w = -probep.dot(proben);

		if (data.raw.type == "planar") {
			m1 = Mat4.identity();
			m2 = Mat4.identity();
			reflect(m1, proben, probep);
			reflect(m2, new Vec4(0, 1, 0), probep);

			transform.scale.z = 1.0; // Only take dim.z into account
			transform.buildMatrix();

			// var aspect = transform.scale.x / transform.scale.y;
			var aspect = iron.App.w() / iron.App.h(); // TODO
			var craw: TCameraData = {
				name: raw.name + "_Camera",
				near_plane: Scene.active.camera.data.raw.near_plane,
				far_plane: Scene.active.camera.data.raw.far_plane,
				fov: Scene.active.camera.data.raw.fov,
				aspect: aspect
			};
			new CameraData(craw, function(cdata: CameraData) {
				camera = new CameraObject(cdata);
				camera.renderTarget = kha.Image.createRenderTarget(
					iron.App.w(), // TODO
					iron.App.h(),
					TextureFormat.RGBA32,
					DepthStencilFormat.NoDepthAndStencil
				);
				camera.name = craw.name;
				camera.setParent(iron.Scene.active.root);
				// Make target bindable from render path
				var rt = new RenderPath.RenderTarget(new RenderPath.RenderTargetRaw());
				rt.raw.name = raw.name;
				rt.image = camera.renderTarget;
				RenderPath.active.renderTargets.set(rt.raw.name, rt);
				ready = true;
			});
		}
		else if (data.raw.type == "cubemap") {
			transform.scale.x *= transform.dim.x;
			transform.scale.y *= transform.dim.y;
			transform.scale.z *= transform.dim.z;
			transform.buildMatrix();

			var craw: TCameraData = {
				name: data.raw.name + "_Camera",
				near_plane: Scene.active.camera.data.raw.near_plane,
				far_plane: Scene.active.camera.data.raw.far_plane,
				fov: 1.5708, // pi/2
				aspect: 1.0
			};
			new CameraData(craw, function(cdata: CameraData) {
				camera = new CameraObject(cdata);
				camera.renderTargetCube = CubeMap.createRenderTarget(
					1024, // TODO
					TextureFormat.RGBA32,
					DepthStencilFormat.NoDepthAndStencil
				);
				camera.name = craw.name;
				camera.setParent(iron.Scene.active.root);
				// Make target bindable from render path
				var rt = new RenderPath.RenderTarget(new RenderPath.RenderTargetRaw());
				rt.raw.name = raw.name;
				rt.raw.is_cubemap = true;
				rt.isCubeMap = true;
				rt.cubeMap = camera.renderTargetCube;
				RenderPath.active.renderTargets.set(rt.raw.name, rt);
				ready = true;
			});
		}
	}

	static function reflect(m: Mat4, n: Vec4, p: Vec4) {
		var c = -p.dot(n);
		m._00 = 1 - 2 * n.x * n.x;
		m._10 =   - 2 * n.x * n.y;
		m._20 =   - 2 * n.x * n.z;
		m._30 =   - 2 * n.x * c;
		m._01 =   - 2 * n.x * n.y;
		m._11 = 1 - 2 * n.y * n.y;
		m._21 =   - 2 * n.y * n.z;
		m._31 =   - 2 * n.y * c;
		m._02 =   - 2 * n.x * n.z;
		m._12 =   - 2 * n.y * n.z;
		m._22 = 1 - 2 * n.z * n.z;
		m._32 =   - 2 * n.z * c;
		m._03 = 0;
		m._13 = 0;
		m._23 = 0;
		m._33 = 1;
	}

	static inline function sign(f: Float): Float {
		return f > 0.0 ? 1.0 : f < 0.0 ? -1.0 : 0.0;
	}

	static function obliqueProjection(m: Mat4, plane: Vec4) {
		// http://www.terathon.com/code/oblique.html
		p.x = (sign(plane.x) + m._20) / m._00;
		p.y = (sign(plane.y) + m._21) / m._11;
		p.z = -1.0;
		p.w = (1.0 + m._22) / m._32;
		q.setFrom(plane).mult(2.0 / plane.dot(p));
		m._02 = q.x;
		m._12 = q.y;
		m._22 = q.z + 1.0;
		m._32 = q.w;
	}

	function cullProbe(camera: CameraObject): Bool {
		if (camera.data.raw.frustum_culling) {
			if (!CameraObject.sphereInFrustum(camera.frustumPlanes, transform, 1.0)) {
				culled = true;
				return culled;
			}
		}
		culled = false;
		return culled;
	}

	public function render(g: Graphics, activeCamera: CameraObject) {
		if (camera == null || !ready || !RenderPath.active.ready || !visible || cullProbe(activeCamera)) return;

		if (data.raw.type == "planar") {
			camera.V.setFrom(m1);
			camera.V.multmat(activeCamera.V);
			camera.V.multmat(m2);
			camera.transform.local.getInverse(camera.V);
			camera.transform.decompose();
			// Skip objects below the reflection plane
			// v.setFrom(proben).applyproj(camera.V);
			// obliqueProjection(#if (arm_taa) camera.noJitterP #else camera.P #end, v);
			camera.renderFrame(g);
		}
		else if (data.raw.type == "cubemap") {
			if (perFrame || redraw) {
				for (i in 0...6) {
					camera.currentFace = i;
					#if (!kha_opengl && !kha_webgl)
					var flip = (i == 2 || i == 3) ? true : false; // Flip +Y, -Y
					#else
					var flip = false;
					#end
					CameraObject.setCubeFace(camera.V, probep, i, flip);
					camera.transform.local.getInverse(camera.V);
					camera.transform.decompose();
					camera.renderFrame(g);
				}
			}
		}

		redraw = false;
	}

#end
}
