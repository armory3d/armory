package iron.object;

import kha.graphics4.Graphics;
import kha.graphics4.CubeMap;
import iron.Scene;
import iron.RenderPath;
import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.data.CameraData;

class CameraObject extends Object {

	public var data: CameraData;
	public var P: Mat4;
	#if arm_taa
	public var noJitterP = Mat4.identity();
	var frame = 0;
	#end
	public var V: Mat4;
	public var prevV: Mat4 = null;
	public var VP: Mat4;
	public var frustumPlanes: Array<FrustumPlane> = null;
	public var renderTarget: kha.Image = null; // Render camera view to texture
	public var renderTargetCube: CubeMap = null;
	public var currentFace = 0;

	static var temp = new Vec4();
	static var q = new Quat();
	static var sphereCenter = new Vec4();
	static var vcenter = new Vec4();
	static var vup = new Vec4();

	#if arm_vr
	var helpMat = Mat4.identity();
	public var leftV = Mat4.identity();
	public var rightV = Mat4.identity();
	#end

	public function new(data: CameraData) {
		super();

		this.data = data;

		#if arm_vr
		iron.system.VR.initButton();
		#end

		buildProjection();

		V = Mat4.identity();
		VP = Mat4.identity();

		if (data.raw.frustum_culling) {
			frustumPlanes = [];
			for (i in 0...6) frustumPlanes.push(new FrustumPlane());
		}

		Scene.active.cameras.push(this);
	}

	public function buildProjection(screenAspect: Null<Float> = null) {
		if (data.raw.ortho != null) {
			P = Mat4.ortho(data.raw.ortho[0], data.raw.ortho[1], data.raw.ortho[2], data.raw.ortho[3], data.raw.near_plane, data.raw.far_plane);
		}
		else {
			if (screenAspect == null) screenAspect = iron.App.w() / iron.App.h();
			var aspect = data.raw.aspect != null ? data.raw.aspect : screenAspect;
			P = Mat4.persp(data.raw.fov, aspect, data.raw.near_plane, data.raw.far_plane);
		}
		#if arm_taa
		noJitterP.setFrom(P);
		#end
	}

	override public function remove() {
		Scene.active.cameras.remove(this);
		// if (renderTarget != null) renderTarget.unload();
		// if (renderTargetCube != null) renderTargetCube.unload();
		super.remove();
	}

	public function renderFrame(g: Graphics) {
		#if arm_taa
		projectionJitter();
		#end

		buildMatrix();

		RenderPath.active.renderFrame(g);

		prevV.setFrom(V);
	}

	#if arm_taa
	function projectionJitter() {
		var w = RenderPath.active.currentW;
		var h = RenderPath.active.currentH;
		P.setFrom(noJitterP);
		var x = 0.0;
		var y = 0.0;
		if (frame % 2 == 0) {
			x = 0.25;
			y = 0.25;
		}
		else {
			x = -0.25;
			y = -0.25;
		}
		P._20 += x / w;
		P._21 += y / h;
		frame++;
	}
	#end

	public function buildMatrix() {
		transform.buildMatrix();

		// Prevent camera matrix scaling
		// TODO: discards position affected by scaled camera parent
		var sc = transform.world.getScale();
		if (sc.x != 1.0 || sc.y != 1.0 || sc.z != 1.0) {
			temp.set(1.0 / sc.x, 1.0 / sc.y, 1.0 / sc.z);
			transform.world.scale(temp);
		}

		V.getInverse(transform.world);
		VP.multmats(P, V);

		#if arm_vr
		var vr = kha.vr.VrInterface.instance;
		if (vr != null && vr.IsPresenting()) {
			leftV.setFrom(V);
			helpMat.self = vr.GetViewMatrix(0);
			leftV.multmat(helpMat);

			rightV.setFrom(V);
			helpMat.self = vr.GetViewMatrix(1);
			rightV.multmat(helpMat);
		}
		else {
			leftV.setFrom(V);
		}
		VP.multmats(P, leftV);
		#else
		VP.multmats(P, V);
		#end

		if (data.raw.frustum_culling) {
			buildViewFrustum(VP, frustumPlanes);
		}

		// First time setting up previous V, prevents first frame flicker
		if (prevV == null) {
			prevV = Mat4.identity();
			prevV.setFrom(V);
		}
	}

	public static function buildViewFrustum(VP: Mat4, frustumPlanes: Array<FrustumPlane>) {
		// Left plane
		frustumPlanes[0].setComponents(VP._03 + VP._00, VP._13 + VP._10, VP._23 + VP._20, VP._33 + VP._30);
		// Right plane
		frustumPlanes[1].setComponents(VP._03 - VP._00, VP._13 - VP._10, VP._23 - VP._20, VP._33 - VP._30);
		// Top plane
		frustumPlanes[2].setComponents(VP._03 - VP._01, VP._13 - VP._11, VP._23 - VP._21, VP._33 - VP._31);
		// Bottom plane
		frustumPlanes[3].setComponents(VP._03 + VP._01, VP._13 + VP._11, VP._23 + VP._21, VP._33 + VP._31);
		// Near plane
		frustumPlanes[4].setComponents(VP._02, VP._12, VP._22, VP._32);
		// Far plane
		frustumPlanes[5].setComponents(VP._03 - VP._02, VP._13 - VP._12, VP._23 - VP._22, VP._33 - VP._32);
		// Normalize planes
		for (plane in frustumPlanes) plane.normalize();
	}

	public static function sphereInFrustum(frustumPlanes: Array<FrustumPlane>, t: Transform, radiusScale = 1.0, offsetX = 0.0, offsetY = 0.0, offsetZ = 0.0): Bool {
		// Use scale when radius is changing
		var radius = t.radius * radiusScale;
		for (plane in frustumPlanes) {
			sphereCenter.set(t.worldx() + offsetX, t.worldy() + offsetY, t.worldz() + offsetZ);
			// Outside the frustum
			if (plane.distanceToSphere(sphereCenter, radius) + radius * 2 < 0) {
				return false;
			}
		}
		return true;
	}

	public static function setCubeFace(m: Mat4, eye: Vec4, face: Int, flip = false) {
		// Set matrix to match cubemap face
		vcenter.setFrom(eye);
		var f = flip ? -1.0 : 1.0;
		switch (face) {
			case 0: // x+
				vcenter.addf(1.0 * f, 0.0, 0.0);
				vup.set(0.0, -1.0 * f, 0.0);
			case 1: // x-
				vcenter.addf(-1.0 * f, 0.0, 0.0);
				vup.set(0.0, -1.0 * f, 0.0);
			case 2: // y+
				vcenter.addf(0.0, 1.0 * f, 0.0);
				vup.set(0.0, 0.0, 1.0 * f);
			case 3: // y-
				vcenter.addf(0.0, -1.0 * f, 0.0);
				vup.set(0.0, 0.0, -1.0 * f);
			case 4: // z+
				vcenter.addf(0.0, 0.0, 1.0 * f);
				vup.set(0.0, -1.0 * f, 0.0);
			case 5: // z-
				vcenter.addf(0.0, 0.0, -1.0 * f);
				vup.set(0.0, -1.0 * f, 0.0);
		}
		m.setLookAt(eye, vcenter, vup);
	}

	public inline function right(): Vec4 {
		return new Vec4(transform.local._00, transform.local._01, transform.local._02);
	}

	public inline function up(): Vec4 {
		return new Vec4(transform.local._10, transform.local._11, transform.local._12);
	}

	public inline function look(): Vec4 {
		return new Vec4(-transform.local._20, -transform.local._21, -transform.local._22);
	}

	public inline function rightWorld(): Vec4 {
		return new Vec4(transform.world._00, transform.world._01, transform.world._02);
	}

	public inline function upWorld(): Vec4 {
		return new Vec4(transform.world._10, transform.world._11, transform.world._12);
	}

	public inline function lookWorld(): Vec4 {
		return new Vec4(-transform.world._20, -transform.world._21, -transform.world._22);
	}
}

class FrustumPlane {
	public var normal = new Vec4(1.0, 0.0, 0.0);
	public var constant = 0.0;

	public function new() {}

	public function normalize() {
		var inverseNormalLength = 1.0 / normal.length();
		normal.mult(inverseNormalLength);
		constant *= inverseNormalLength;
	}

	public function distanceToSphere(sphereCenter: Vec4, sphereRadius: Float): Float {
		return (normal.dot(sphereCenter) + constant) - sphereRadius;
	}

	public inline function setComponents(x: Float, y: Float, z: Float, w: Float) {
		normal.set(x, y, z);
		constant = w;
	}
}
