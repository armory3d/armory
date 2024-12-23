package iron.object;

import kha.arrays.Float32Array;
import kha.graphics4.TextureFormat;
import kha.graphics4.Usage;
import iron.math.Mat4;
import iron.math.Vec4;
import iron.data.LightData;
import iron.object.CameraObject;

class LightObject extends Object {

	public var data: LightData;

	#if rp_shadowmap
	#if arm_shadowmap_atlas
	public var tileNotifyOnRemove: Void -> Void;
	public var lightInAtlas = false;
	public var culledLight = false;
	public static var pointLightsData: kha.arrays.Float32Array = null;
	public var shadowMapScale = 1.0; // When in forward if this defaults to 0.0, the atlas are not drawn before being bound.
	// Data used in uniforms
	public var tileOffsetX: Array<Float> = [0.0];
	public var tileOffsetY: Array<Float> = [0.0];
	public var tileScale: Array<Float> = [1.0];
	#end
	// Cascades
	public static var cascadeCount = 1;
	public static var cascadeSplitFactor = 0.8;
	public static var cascadeBounds = 1.0;
	#if arm_csm
	var cascadeData: Float32Array = null;
	var cascadeVP: Array<Mat4>;
	var camSlicedP: Array<Mat4> = null;
	var cascadeSplit: Array<kha.FastFloat>;
	var bias = Mat4.identity();
	#else
	var camSlicedP: Mat4 = null;
	#end
	#end // rp_shadowmap

	#if (arm_csm || arm_clusters)
	static var helpMat = Mat4.identity();
	#end

	// Clusters
	#if arm_clusters
	static var slicesX = 16;
	static var slicesY = 16;
	static var slicesZ = 16;
	static inline var maxLights = getMaxLights();
	public static inline var maxLightsCluster = getMaxLightsCluster(); // Mirror shader constant
	static inline var clusterNear = 3.0;
	public static var lightsArray: Float32Array = null;
	#if arm_spot
	public static var lightsArraySpot: Float32Array = null;
	#end
	public static var clustersData: kha.Image = null;
	static var lpos = new Vec4();
	public static var LWVPMatrixArray: Float32Array = null;
	#end // arm_clusters

	public var V: Mat4 = Mat4.identity();
	public var P: Mat4 = null;
	public var VP: Mat4 = Mat4.identity();

	public var frustumPlanes: Array<FrustumPlane> = null;
	static var m = Mat4.identity();
	static var eye = new Vec4();
	#if rp_shadowmap
	static var corners: Array<Vec4> = null;
	#end

	public function new(data: LightData) {
		super();

		this.data = data;

		var type = data.raw.type;
		var fov = data.raw.fov;

		if (type == "sun") {
			#if rp_shadowmap
			if (corners == null) {
				corners = [];
				for (i in 0...8) corners.push(new Vec4());
			}
			P = Mat4.identity();
			#else
			P = Mat4.ortho(-1, 1, -1, 1, data.raw.near_plane, data.raw.far_plane);
			#end
			#if arm_shadowmap_atlas
			this.shadowMapScale = 1.0;
			#end
		}
		else if (type == "point" || type == "area") {
			P = Mat4.persp(fov, 1, data.raw.near_plane, data.raw.far_plane);
		}
		else if (type == "spot") {
			P = Mat4.persp(fov, 1, data.raw.near_plane, data.raw.far_plane);
		}

		Scene.active.lights.push(this);
	}

	override public function remove() {
		if (Scene.active != null) Scene.active.lights.remove(this);
		final rp = RenderPath.active;
		if (rp.light == this) { rp.light = null; }
		if (rp.point == this) { rp.point = null; }
		else if (rp.sun == this) { rp.sun = null; }
		#if rp_shadowmap
		#if arm_shadowmap_atlas
		if (tileNotifyOnRemove != null) {
			tileNotifyOnRemove();
			tileNotifyOnRemove = null;
		}
		#end
		#end
		super.remove();
	}

	public function buildMatrix(camera: CameraObject) {
		transform.buildMatrix();
		if (data.raw.type == "sun") { // Cover camera frustum
			#if (rp_shadowmap && !arm_csm) // Otherwise set cascades on mesh draw
			setCascade(camera, 0);
			#else
			V.getInverse(transform.world);
			updateViewFrustum(camera);
			#end
		}
		else { // Point, spot, area
			V.getInverse(transform.world);
			updateViewFrustum(camera);
		}
	}

	#if rp_shadowmap

	static inline function setCorners() {
		corners[0].set(-1.0, -1.0, 1.0);
		corners[1].set(-1.0, -1.0, -1.0);
		corners[2].set(-1.0, 1.0, 1.0);
		corners[3].set(-1.0, 1.0, -1.0);
		corners[4].set(1.0, -1.0, 1.0);
		corners[5].set(1.0, -1.0, -1.0);
		corners[6].set(1.0, 1.0, 1.0);
		corners[7].set(1.0, 1.0, -1.0);
	}

	static inline function mix(a: Float, b: Float, f: Float): Float {
		return a * (1 - f) + b * f;
	}

	public function setCascade(camera: CameraObject, cascade: Int) {
		m.setFrom(camera.V);

		#if arm_csm
		if (camSlicedP == null) {
			camSlicedP = [];
			cascadeSplit = [];
			var ortho = camera.data.raw.ortho;
			if (ortho == null) {
				var aspect = camera.data.raw.aspect != null ? camera.data.raw.aspect : iron.App.w() / iron.App.h();
				var fov = camera.data.raw.fov;
				var near = camera.data.raw.near_plane;
				var far = camera.data.raw.far_plane;
				var factor = cascadeCount > 2 ? cascadeSplitFactor : cascadeSplitFactor * 0.25;
				for (i in 0...cascadeCount) {
					var f = i + 1.0;
					var cfar = mix(
						near + (f / cascadeCount) * (far - near),
						near * Math.pow(far / near, f / cascadeCount),
						factor);
					cascadeSplit.push(cfar);
					camSlicedP.push(Mat4.persp(fov, aspect, near, cfar));
				}
			}
			else {
				for (i in 0...cascadeCount) {
					cascadeSplit.push(data.raw.far_plane);
					camSlicedP.push(Mat4.ortho(ortho[0], ortho[1], ortho[2], ortho[3], data.raw.near_plane, data.raw.far_plane));
				}
			}
		}
		m.multmat(camSlicedP[cascade]);
		#else
		if (camSlicedP == null) { // Fit to light far plane
			var ortho = camera.data.raw.ortho;
			if (ortho == null) {
				var fov = camera.data.raw.fov;
				var near = data.raw.near_plane;
				var far = data.raw.far_plane;
				var aspect = camera.data.raw.aspect != null ? camera.data.raw.aspect : iron.App.w() / iron.App.h();
				camSlicedP = Mat4.persp(fov, aspect, near, far);
			}
			else {
				// camSlicedP = camera.P;
				camSlicedP = Mat4.ortho(ortho[0], ortho[1], ortho[2], ortho[3], data.raw.near_plane, data.raw.far_plane);
			}
		}
		m.multmat(camSlicedP);
		#end

		m.getInverse(m);
		V.getInverse(transform.world);
		V.toRotation();
		m.multmat(V);
		setCorners();
		for (v in corners) {
			v.applymat4(m);
			v.set(v.x / v.w, v.y / v.w, v.z / v.w);
		}

		var minx = corners[0].x;
		var miny = corners[0].y;
		var minz = corners[0].z;
		var maxx = corners[0].x;
		var maxy = corners[0].y;
		var maxz = corners[0].z;
		for (v in corners) {
			if (v.x < minx) minx = v.x;
			if (v.x > maxx) maxx = v.x;
			if (v.y < miny) miny = v.y;
			if (v.y > maxy) maxy = v.y;
			if (v.z < minz) minz = v.z;
			if (v.z > maxz) maxz = v.z;
		}

		// Adjust frustum size by longest diagonal - fix rotation swim
		var diag0 = Vec4.distance(corners[0], corners[7]);
		var offx = (diag0 - (maxx - minx)) * 0.5;
		var offy = (diag0 - (maxy - miny)) * 0.5;
		minx -= offx;
		maxx += offx;
		miny -= offy;
		maxy += offy;

		// Snap to texel coords - fix translation swim
		var smsize = data.raw.shadowmap_size;
		#if arm_csm // Cascades
		smsize = Std.int(smsize / 4);
		#end
		var worldPerTexelX = (maxx - minx) / smsize;
		var worldPerTexelY = (maxy - miny) / smsize;
		var worldPerTexelZ = (maxz - minz) / smsize;
		minx = Math.floor(minx / worldPerTexelX) * worldPerTexelX;
		miny = Math.floor(miny / worldPerTexelY) * worldPerTexelY;
		minz = Math.floor(minz / worldPerTexelZ) * worldPerTexelZ;
		maxx = Math.floor(maxx / worldPerTexelX) * worldPerTexelX;
		maxy = Math.floor(maxy / worldPerTexelY) * worldPerTexelY;
		maxz = Math.floor(maxz / worldPerTexelZ) * worldPerTexelZ;

		var hx = (maxx - minx) / 2;
		var hy = (maxy - miny) / 2;
		var hz = (maxz - minz) / 2;
		V._30 = -(minx + hx);
		V._31 = -(miny + hy);
		V._32 = -(minz + hz);

		// (-hz * 4 * cascadeBounds) - include shadow casters out of view frustum
		m = Mat4.ortho(-hx, hx, -hy, hy, -hz * 4 * cascadeBounds, hz);
		P.setFrom(m);

		updateViewFrustum(camera);

		#if arm_csm
		if (cascadeVP == null) {
			cascadeVP = [];
			for (i in 0...cascadeCount) {
				cascadeVP.push(Mat4.identity());
			}
		}
		cascadeVP[cascade].setFrom(VP);
		#end
	}
	#end // rp_shadowmap

	function updateViewFrustum(camera: CameraObject) {
		VP.multmats(P, V);

		// Frustum culling enabled
		if (camera.data.raw.frustum_culling) {
			if (frustumPlanes == null) {
				frustumPlanes = [];
				for (i in 0...6) frustumPlanes.push(new FrustumPlane());
			}
			CameraObject.buildViewFrustum(VP, frustumPlanes);
		}
	}

	public function setCubeFace(face: Int, camera: CameraObject) {
		// Set matrix to match cubemap face
		eye.set(transform.worldx(), transform.worldy(), transform.worldz());
		#if (!kha_opengl && !kha_webgl && !arm_shadowmap_atlas)
		var flip = (face == 2 || face == 3) ? true : false; // Flip +Y, -Y
		#else
		var flip = false;
		#end
		CameraObject.setCubeFace(V, eye, face, flip);
		updateViewFrustum(camera);
	}

	#if arm_csm
	public function getCascadeData(): Float32Array {
		// Cascade mats + split distances
		if (cascadeData == null) {
			cascadeData = new Float32Array(cascadeCount * 16 + 4);
		}
		if (cascadeVP == null) return cascadeData;

		// 4 cascade mats + split distances
		for (i in 0...cascadeCount) {
			m.setFrom(cascadeVP[i]);
			bias.setFrom(Uniforms.biasMat);
			#if (!arm_shadowmap_atlas)
			bias._00 /= cascadeCount; // Atlas offset
			bias._30 /= cascadeCount;
			bias._30 += i * (1 / cascadeCount);
			#else
			// tile matrix
			helpMat.setIdentity();
			// scale [0-1] coords to [0-tilescale]
			helpMat._00 = this.tileScale[i];
			helpMat._11 = this.tileScale[i];
			// offset coordinate start from [0, 0] to [tile-start-x, tile-start-y]
			helpMat._30 = this.tileOffsetX[i];
			helpMat._31 = this.tileOffsetY[i];
			bias.multmat(helpMat);
			#if (!kha_opengl)
			helpMat.setIdentity();
			helpMat._11 = -1.0;
			helpMat._31 = 1.0;
			bias.multmat(helpMat);
			#end
			#end
			m.multmat(bias);
			cascadeData[i * 16] = m._00;
			cascadeData[i * 16 + 1] = m._01;
			cascadeData[i * 16 + 2] = m._02;
			cascadeData[i * 16 + 3] = m._03;
			cascadeData[i * 16 + 4] = m._10;
			cascadeData[i * 16 + 5] = m._11;
			cascadeData[i * 16 + 6] = m._12;
			cascadeData[i * 16 + 7] = m._13;
			cascadeData[i * 16 + 8] = m._20;
			cascadeData[i * 16 + 9] = m._21;
			cascadeData[i * 16 + 10] = m._22;
			cascadeData[i * 16 + 11] = m._23;
			cascadeData[i * 16 + 12] = m._30;
			cascadeData[i * 16 + 13] = m._31;
			cascadeData[i * 16 + 14] = m._32;
			cascadeData[i * 16 + 15] = m._33;
		}
		cascadeData[cascadeCount * 16    ] = cascadeSplit[0];
		cascadeData[cascadeCount * 16 + 1] = cascadeSplit[1];
		cascadeData[cascadeCount * 16 + 2] = cascadeSplit[2];
		cascadeData[cascadeCount * 16 + 3] = cascadeSplit[3];
		return cascadeData;
	}
	#end // arm_csm

	#if arm_clusters

	// Centralize discarding conditions when iterating over lights
	// Important to avoid issues later with "misaligned" data in uniforms (lightsArray, clusterData, LWVPSpotArray)
	public inline static function discardLight(light: LightObject) {
		return !light.visible || light.data.raw.strength == 0.0 || light.data.raw.type == "sun";
	}
	// Discarding conditions but with culling included
	public inline static function discardLightCulled(light: LightObject) {
		return #if arm_shadowmap_atlas light.culledLight || #end discardLight(light);
	}

	#if (arm_shadowmap_atlas && arm_shadowmap_atlas_lod)
	// Arbitrary function to map from [0-16] to [1.0-0.0]
	public inline static function zToShadowMapScale(z: Int, max: Int): Float {
 		return 0.25 * Math.sqrt(-z + max);
	}
	#end

	static function getRadius(strength: kha.FastFloat): kha.FastFloat {
		// (1.0 / (dist * dist)) * strength = 0.01
		return Math.sqrt(strength / 0.004);
	}

	inline static function distSliceX(f: Float, lpos: Vec4): Float {
		return (lpos.x - f * lpos.z) / Math.sqrt(1.0 + f * f);
	}

	inline static function distSliceY(f: Float, lpos: Vec4): Float {
		return (lpos.y - f * lpos.z) / Math.sqrt(1.0 + f * f);
	}

	static function sliceToDist(camera: CameraObject, z: Int): Float {
		var cnear = clusterNear + camera.data.raw.near_plane;
		switch (z) {
			case 0:
				return camera.data.raw.near_plane;
			case 1:
				return cnear;
			default: {
				var depthl = (z - 1) / (slicesZ - 1);
				return Math.exp(depthl * Math.log(camera.data.raw.far_plane - cnear + 1.0)) + cnear - 1.0;
			}
		}
	}

	public static function updateClusters(camera: CameraObject) {
		// Reference: https://newq.net/publications/more/s2015-many-lights-course
		var lights = Scene.active.lights;

		#if arm_spot // Point lamps first
		lights.sort(function(a, b): Int {
			return a.data.raw.type >= b.data.raw.type ? 1 : -1;
		});
		#end

		if (clustersData == null) {
			var lines = #if (arm_spot) 2 #else 1 #end;
			clustersData = kha.Image.create(slicesX * slicesY * slicesZ, lines + maxLightsCluster, TextureFormat.L8, Usage.DynamicUsage);
		}

		var bytes = clustersData.lock();

		var stride = slicesX * slicesY * slicesZ;
		for (i in 0...stride) {
			bytes.set(i, 0);
			#if arm_spot
			bytes.set(i + stride * (maxLightsCluster + 1), 0);
			#end
		}

		var fovtan = Math.tan(camera.data.raw.fov * 0.5);
		var stepY = (2.0 * fovtan) / slicesY;
		var aspect = RenderPath.active.currentW / RenderPath.active.currentH;
		var stepX = (2.0 * fovtan * aspect) / slicesX;

		var n = lights.length > maxLights ? maxLights : lights.length;
		var i = 0;
		for (l in lights) {
			if (discardLight(l)) continue;
			if (i >= n) break;
			// Light bounds
			lpos.set(l.transform.worldx(), l.transform.worldy(), l.transform.worldz());
			lpos.applymat4(camera.V);
			lpos.z *= -1.0;
			var radius = getRadius(l.data.raw.strength);
			var minX = 0;
			var minY = 0;
			var minZ = 0;
			var maxX = slicesX;
			var maxY = slicesY;
			var maxZ = slicesZ;
			while (minX <= slicesX) {
				if (distSliceX(stepX * (minX + 1 - slicesX * 0.5), lpos) <= radius) break;
				minX++;
			}
			while (maxX >= minX) {
				if (-distSliceX(stepX * (maxX - 1 - slicesX * 0.5), lpos) <= radius) { maxX--; break; }
				maxX--;
			}
			while (minY <= slicesY) {
				if (distSliceY(stepY * (minY + 1 - slicesY * 0.5), lpos) <= radius) break;
				minY++;
			}
			while (maxY >= minY) {
				if (-distSliceY(stepY * (maxY - 1 - slicesY * 0.5), lpos) <= radius) { maxY--; break; }
				maxY--;
			}
			while (minZ <= slicesZ) {
				if (sliceToDist(camera, minZ + 1) >= lpos.z - radius) break;
				minZ++;
			}
			while (maxZ >= minZ) {
				if (sliceToDist(camera, maxZ - 1) <= lpos.z + radius) break;
				maxZ--;
			}
			#if arm_shadowmap_atlas
			l.culledLight = maxZ < 0 || minX > maxX || minY > maxY;
			l.shadowMapScale = l.culledLight ? 0.0 : #if arm_shadowmap_atlas_lod zToShadowMapScale(minZ, slicesZ) #else 1.0 #end;
			// Discard lights that are outside of the view
			if (l.culledLight) {
				continue;
			}
			#end
			// Mark affected clusters
			for (z in minZ...maxZ + 1) {
				for (y in minY...maxY + 1) {
					for (x in minX...maxX + 1) {
						var cluster = x + y * slicesX + z * slicesX * slicesY;
						var numLights = bytes.get(cluster);
						if (numLights < maxLightsCluster) {
							numLights++;
							bytes.set(cluster, numLights);
							bytes.set(cluster + stride * numLights, i);
							#if arm_spot
							if (l.data.raw.type == "spot") {
								// Last line
								var numSpots = bytes.get(cluster + stride * (maxLightsCluster + 1)) + 1;
								bytes.set(cluster + stride * (maxLightsCluster + 1), numSpots);
							}
							#end
						}
					}
				}
			}
			i++;
		}
		clustersData.unlock();

		updateLightsArray(); // TODO: only update on light change
	}

	static function updateLightsArray() {
		if (lightsArray == null) { // vec4x3 - 1: pos, a, color, b, 2: dir, c
			lightsArray = new Float32Array(maxLights * 4 * 3);
			#if arm_spot
			lightsArraySpot = new Float32Array(maxLights * 4 * 2);
			#end
		}
		var lights = Scene.active.lights;
		var n = lights.length > maxLights ? maxLights : lights.length;
		var i = 0;
		for (l in lights) {
			if (discardLightCulled(l)) continue;
			if (i >= n) break;

			// light position
			lightsArray[i * 12    ] = l.transform.worldx();
			lightsArray[i * 12 + 1] = l.transform.worldy();
			lightsArray[i * 12 + 2] = l.transform.worldz();
			lightsArray[i * 12 + 3] = 0.0; // padding or spot scale x

			// light color
			var f = l.data.raw.strength;
			lightsArray[i * 12 + 4] = l.data.raw.color[0] * f;
			lightsArray[i * 12 + 5] = l.data.raw.color[1] * f;
			lightsArray[i * 12 + 6] = l.data.raw.color[2] * f;
			lightsArray[i * 12 + 7] = 0.0; // padding or spot scale y

			// other data
			lightsArray[i * 12 + 8] = l.data.raw.shadows_bias; // bias
			lightsArray[i * 12 + 9] = 0.0; // cutoff for detecting spot
			lightsArray[i * 12 + 10] = l.data.raw.cast_shadow ? 1.0 : 0.0; // hasShadows
			lightsArray[i * 12 + 11] = 0.0; // padding

			#if arm_spot
			if (l.data.raw.type == "spot") {
				lightsArray[i * 12 + 9] = l.data.raw.spot_size;

				var dir = l.look().normalize();
				lightsArraySpot[i * 8    ] = dir.x;
				lightsArraySpot[i * 8 + 1] = dir.y;
				lightsArraySpot[i * 8 + 2] = dir.z;
				lightsArraySpot[i * 8 + 3] = l.data.raw.spot_blend;

				// Premultiply scale with z component
				var scale = l.transform.scale;
				lightsArray[i * 12 + 3] = scale.z == 0.0 ? 0.0 : scale.x / scale.z;
				lightsArray[i * 12 + 7] = scale.z == 0.0 ? 0.0 : scale.y / scale.z;

				final right = l.right().normalize();
				lightsArraySpot[i * 8 + 4] = right.x;
				lightsArraySpot[i * 8 + 5] = right.y;
				lightsArraySpot[i * 8 + 6] = right.z;
				lightsArraySpot[i * 8 + 7] = 0.0; // padding
			}
			#end
			i++;
		}
	}

	public static function updateLWVPMatrixArray(object: Object, type: String) {
		if (LWVPMatrixArray == null) {
			LWVPMatrixArray = new Float32Array(maxLightsCluster * 16);
		}

		var lights = Scene.active.lights;
		var n = lights.length > maxLightsCluster ? maxLightsCluster : lights.length;
		var i = 0;

		for (light in lights) {
			if (i >= n) {
				break;
			}
			if (discardLightCulled(light)) continue;
			if (light.data.raw.type == type) {
				m.setFrom(light.VP);
				m.multmat(Uniforms.biasMat);
				#if arm_shadowmap_atlas
				// tile matrix
				helpMat.setIdentity();
				// scale [0-1] coords to [0-tilescale]
				helpMat._00 = light.tileScale[0];
				helpMat._11 = light.tileScale[0];
				// offset coordinate start from [0, 0] to [tile-start-x, tile-start-y]
				helpMat._30 = light.tileOffsetX[0];
				helpMat._31 = light.tileOffsetY[0];
				m.multmat(helpMat);
				#if (!kha_opengl)
				helpMat.setIdentity();
				helpMat._11 = -1.0;
				helpMat._31 = 1.0;
				m.multmat(helpMat);
				#end
				#end

				LWVPMatrixArray[i * 16    ] = m._00;
				LWVPMatrixArray[i * 16 + 1] = m._01;
				LWVPMatrixArray[i * 16 + 2] = m._02;
				LWVPMatrixArray[i * 16 + 3] = m._03;
				LWVPMatrixArray[i * 16 + 4] = m._10;
				LWVPMatrixArray[i * 16 + 5] = m._11;
				LWVPMatrixArray[i * 16 + 6] = m._12;
				LWVPMatrixArray[i * 16 + 7] = m._13;
				LWVPMatrixArray[i * 16 + 8] = m._20;
				LWVPMatrixArray[i * 16 + 9] = m._21;
				LWVPMatrixArray[i * 16 + 10] = m._22;
				LWVPMatrixArray[i * 16 + 11] = m._23;
				LWVPMatrixArray[i * 16 + 12] = m._30;
				LWVPMatrixArray[i * 16 + 13] = m._31;
				LWVPMatrixArray[i * 16 + 14] = m._32;
				LWVPMatrixArray[i * 16 + 15] = m._33;
			}
			i++;
		}
		return LWVPMatrixArray;
	}

	public static inline function getMaxLights(): Int {
		#if (rp_max_lights == 8)
		return 8;
		#elseif (rp_max_lights == 16)
		return 16;
		#elseif (rp_max_lights == 24)
		return 24;
		#elseif (rp_max_lights == 32)
		return 32;
		#elseif (rp_max_lights == 64)
		return 64;
		#else
		return 4;
		#end
	}

	public static inline function getMaxLightsCluster(): Int {
		#if (rp_max_lights_cluster == 8)
		return 8;
		#elseif (rp_max_lights_cluster == 16)
		return 16;
		#elseif (rp_max_lights_cluster == 24)
		return 24;
		#elseif (rp_max_lights_cluster == 32)
		return 32;
		#elseif (rp_max_lights_cluster == 64)
		return 64;
		#else
		return 4;
		#end
	}
	#end // arm_clusters

	public inline function right(): Vec4 {
		return new Vec4(V._00, V._10, V._20);
	}

	public inline function up(): Vec4 {
		return new Vec4(V._01, V._11, V._21);
	}

	public inline function look(): Vec4 {
		return new Vec4(V._02, V._12, V._22);
	}
}
