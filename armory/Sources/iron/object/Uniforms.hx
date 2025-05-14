package iron.object;

import kha.graphics4.Graphics;
import kha.graphics4.ConstantLocation;
import kha.graphics4.TextureAddressing;
import kha.graphics4.TextureFilter;
import kha.graphics4.MipMapFilter;
import kha.arrays.Float32Array;
import iron.math.Vec4;
import iron.math.Quat;
import iron.math.Mat3;
import iron.math.Mat4;
import iron.data.WorldData;
import iron.data.MaterialData;
import iron.data.ShaderData;
import iron.data.SceneFormat;
import iron.system.Input;
import iron.system.Time;
import iron.RenderPath;
using StringTools;

// Structure for setting shader uniforms
class Uniforms {

	#if (kha_opengl || (kha_webgl && !arm_shadowmap_atlas) || (!kha_webgl && arm_shadowmap_atlas))
	public static var biasMat = new Mat4(
		0.5, 0.0, 0.0, 0.5,
		0.0, 0.5, 0.0, 0.5,
		0.0, 0.0, 0.5, 0.5,
		0.0, 0.0, 0.0, 1.0);
	#else // d3d
	public static var biasMat = new Mat4(
		0.5, 0.0, 0.0, 0.5,
		0.0, -0.5, 0.0, 0.5,
		0.0, 0.0, 0.5, 0.5,
		0.0, 0.0, 0.0, 1.0);
	#end
	public static var helpMat = Mat4.identity();
	public static var helpMat2 = Mat4.identity();
	public static var helpMat3 = Mat3.identity();
	public static var helpVec = new Vec4();
	public static var helpVec2 = new Vec4();
	public static var helpQuat = new Quat(); // Keep at identity

	public static var externalTextureLinks: Array<Object->MaterialData->String->kha.Image> = null;
	public static var externalMat4Links: Array<Object->MaterialData->String->Mat4> = null;
	public static var externalVec4Links: Array<Object->MaterialData->String->Vec4> = null;
	public static var externalVec3Links: Array<Object->MaterialData->String->Vec4> = null;
	public static var externalVec2Links: Array<Object->MaterialData->String->Vec4> = null;
	public static var externalFloatLinks: Array<Object->MaterialData->String->Null<kha.FastFloat>> = null;
	public static var externalFloatsLinks: Array<Object->MaterialData->String->Float32Array> = null;
	public static var externalIntLinks: Array<Object->MaterialData->String->Null<Int>> = null;
	public static var posUnpack: Null<kha.FastFloat> = null;
	public static var texUnpack: Null<kha.FastFloat> = null;

	#if (rp_resolution_filter == "Point")
	public static var defaultFilter = TextureFilter.PointFilter;
	#else
	public static var defaultFilter = TextureFilter.LinearFilter;
	#end

	public static function setContextConstants(g: Graphics, context: ShaderContext, bindParams: Array<String>) {
		if (context.raw.constants != null) {
			for (i in 0...context.raw.constants.length) {
				var c = context.raw.constants[i];
				setContextConstant(g, context.constants[i], c);
			}
		}

		// Texture context constants
		if (bindParams != null) { // Bind targets
			for (i in 0...Std.int(bindParams.length / 2)) {
				var pos = i * 2; // bind params = [texture, samplerID]
				var rtID = bindParams[pos];
				var samplerID = bindParams[pos + 1];
				var attachDepth = false; // Attach texture depth if '_' is prepended
				var char = rtID.charAt(0);
				if (char == "_") {
					attachDepth = true;
					rtID = rtID.substr(1);
				}
				var rt = attachDepth ? RenderPath.active.depthToRenderTarget.get(rtID) : RenderPath.active.renderTargets.get(rtID);
				bindRenderTarget(g, rt, context, samplerID, attachDepth);
			}
		}

		// Texture links
		if (context.raw.texture_units != null) {
			for (j in 0...context.raw.texture_units.length) {
				var tulink = context.raw.texture_units[j].link;
				if (tulink == null) continue;

				if (tulink.charAt(0) == "$") { // Link to embedded data
					g.setTexture(context.textureUnits[j], Scene.active.embedded.get(tulink.substr(1)));
					if (tulink.endsWith(".raw")) { // Raw 3D texture
						g.setTexture3DParameters(context.textureUnits[j], TextureAddressing.Repeat, TextureAddressing.Repeat, TextureAddressing.Repeat, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
					}
					else { // 2D texture
						g.setTextureParameters(context.textureUnits[j], TextureAddressing.Repeat, TextureAddressing.Repeat, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
					}
				}
				else {
					switch (tulink) {
						case "_envmapRadiance": {
							var w = Scene.active.world;
							if (w != null) {
								g.setTexture(context.textureUnits[j], w.probe.radiance);
								g.setTextureParameters(context.textureUnits[j], TextureAddressing.Repeat, TextureAddressing.Repeat, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.LinearMipFilter);
							}
						}
						case "_envmap": {
							var w = Scene.active.world;
							if (w != null) {
								g.setTexture(context.textureUnits[j], w.envmap);
								g.setTextureParameters(context.textureUnits[j], TextureAddressing.Repeat, TextureAddressing.Repeat, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
							}
						}
						#if arm_clusters
						case "_clustersData": {
							g.setTexture(context.textureUnits[j], LightObject.clustersData);
							g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.PointFilter, TextureFilter.PointFilter, MipMapFilter.NoMipFilter);
						}
						#end
					}
				}
			}
		}
	}

	public static function setObjectConstants(g: Graphics, context: ShaderContext, object: Object) {
		if (context.raw.constants != null) {
			for (i in 0...context.raw.constants.length) {
				var c = context.raw.constants[i];
				setObjectConstant(g, object, context.constants[i], c);
			}
		}

		// Texture object constants
		// External
		if (externalTextureLinks != null) {
			if (context.raw.texture_units != null) {
				for (j in 0...context.raw.texture_units.length) {
					var tu = context.raw.texture_units[j];
					if (tu.link == null) continue;
					var tuAddrU = getTextureAddressing(tu.addressing_u);
					var tuAddrV = getTextureAddressing(tu.addressing_v);
					var tuFilterMin = getTextureFilter(tu.filter_min);
					var tuFilterMag = getTextureFilter(tu.filter_mag);
					var tuMipMapFilter = getMipMapFilter(tu.mipmap_filter);

					for (f in externalTextureLinks) {
						var image = f(object, currentMat(object), tu.link);
						if (image != null) {
							tu.link.endsWith("_depth") ?
								g.setTextureDepth(context.textureUnits[j], image) :
								g.setTexture(context.textureUnits[j], image);
							g.setTextureParameters(context.textureUnits[j], tuAddrU, tuAddrV, tuFilterMin, tuFilterMag, tuMipMapFilter);
							break;
						}
					}
				}
			}
		}
	}

	static function bindRenderTarget(g: Graphics, rt: RenderTarget, context: ShaderContext, samplerID: String, attachDepth: Bool) {
		if (rt != null) {
			var tus = context.raw.texture_units;

			for (j in 0...tus.length) { // Set texture
				if (samplerID == tus[j].name) {
					var isImage = tus[j].is_image != null && tus[j].is_image;
					var paramsSet = false;

					if (rt.raw.depth > 1) { // sampler3D
						g.setTexture3DParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.AnisotropicFilter, MipMapFilter.NoMipFilter);
						paramsSet = true;
					}

					if (isImage) {
						// Multiple voxel volumes, always set params
						g.setImageTexture(context.textureUnits[j], rt.image); // image2D/3D
						if (rt.raw.name.startsWith("voxels_")) {
							g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
						}
						else if (rt.raw.name.startsWith("voxels"))
						{
							g.setTexture3DParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
						}
						else
						{
							g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.LinearMipFilter);
						}
						paramsSet = true;
					}
					else if (rt.isCubeMap) {
						if (attachDepth) g.setCubeMapDepth(context.textureUnits[j], rt.cubeMap); // samplerCube
						else g.setCubeMap(context.textureUnits[j], rt.cubeMap); // samplerCube
					}
					else {
						if (attachDepth) g.setTextureDepth(context.textureUnits[j], rt.image); // sampler2D
						else g.setTexture(context.textureUnits[j], rt.image); // sampler2D
					}

					if (!paramsSet && rt.raw.mipmaps != null && rt.raw.mipmaps == true && !isImage) {
						g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.LinearMipFilter);
						paramsSet = true;
					}

					if (!paramsSet) {
						if (rt.raw.name.startsWith("bloom")) {
							// Use bilinear filter for bloom mips to get correct blur
							g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.LinearMipFilter);
						}
						if (samplerID.startsWith("shadowMap")) {
							if (rt.isCubeMap) {
								#if (!arm_legacy)
								g.setCubeMapCompareMode(context.textureUnits[j], true);
								#end
							}
							else {
								g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.LinearFilter, TextureFilter.LinearFilter, MipMapFilter.NoMipFilter);
								#if (!arm_legacy)
								g.setTextureCompareMode(context.textureUnits[j], true);
								#end
							}
							paramsSet = true;
						}
						else if (attachDepth) {
							g.setTextureParameters(context.textureUnits[j], TextureAddressing.Clamp, TextureAddressing.Clamp, TextureFilter.PointFilter, TextureFilter.PointFilter, MipMapFilter.NoMipFilter);
							paramsSet = true;
						}
					}

					if (!paramsSet) {
						// No filtering when sampling render targets
						var oc = context.overrideContext;
						var allowParams = oc == null || oc.shared_sampler == null || oc.shared_sampler == samplerID;
						if (allowParams) {
							var addressing = (oc != null && oc.addressing == "repeat") ? TextureAddressing.Repeat : TextureAddressing.Clamp;
							var filter = (oc != null && oc.filter == "point") ? TextureFilter.PointFilter : defaultFilter;
							g.setTextureParameters(context.textureUnits[j], addressing, addressing, filter, filter, MipMapFilter.NoMipFilter);
						}
						paramsSet = true;
					}
				}
			}
		}
	}

	static function setContextConstant(g: Graphics, location: ConstantLocation, c: TShaderConstant): Bool {
		if (c.link == null) return true;

		var camera = Scene.active.camera;
		var light = RenderPath.active.light;

		if (c.type == "mat4") {
			var m: Mat4 = null;
			switch (c.link) {
				case "_viewMatrix": {
					#if arm_centerworld
					m = vmat(camera.V);
					#else
					m = camera.V;
					#end
				}
				case "_transposeViewMatrix": {
					helpMat.setFrom(camera.V);
					helpMat.transpose3x3();
					m = helpMat;
				}
				case "_projectionMatrix": {
					m = camera.P;
				}
				case "_inverseProjectionMatrix": {
					helpMat.getInverse(camera.P);
					m = helpMat;
				}
				case "_inverseViewProjectionMatrix": {
					#if arm_centerworld
					helpMat.setFrom(vmat(camera.V));
					#else
					helpMat.setFrom(camera.V);
					#end
					helpMat.multmat(camera.P);
					helpMat.getInverse(helpMat);
					m = helpMat;
				}
				case "_viewProjectionMatrix": {
					#if arm_centerworld
					m = vmat(camera.V);
					m.multmat(camera.P);
					#else
					m = camera.VP;
					#end
				}
				case "_prevViewProjectionMatrix": {
					helpMat.setFrom(camera.prevV);
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				case "_lightViewProjectionMatrix": {
					if (light != null) {
						m = light.VP;
					}
				}
				case "_biasLightViewProjectionMatrix": {
					if (light != null) {
						helpMat.setFrom(light.VP);
						helpMat.multmat(biasMat);
						m = helpMat;
					}
				}
				case "_skydomeMatrix": {
					var tr = camera.transform;
					helpVec.set(tr.worldx(), tr.worldy(), tr.worldz() - 3.5); // Sky
					var bounds = camera.data.raw.far_plane * 0.95;
					helpVec2.set(bounds, bounds, bounds);
					helpMat.compose(helpVec, helpQuat, helpVec2);
					helpMat.multmat(camera.V);
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				default: // Unknown uniform
					return false;
			}

			g.setMatrix(location, m != null ? m.self : kha.math.FastMatrix4.identity());
			return true;
		}
		else if (c.type == "vec4") {
			var v: Vec4 = null;
			helpVec.set(0, 0, 0, 0);
			switch (c.link) {
				#if arm_debug
				case "_input": {
					helpVec.set(Input.getMouse().x / iron.App.w(), Input.getMouse().y / iron.App.h(), Input.getMouse().down() ? 1.0 : 0.0, 0.0);
					v = helpVec;
				}
				#end
				default:
					return false;
			}

			if (v != null) {
				g.setFloat4(location, v.x, v.y, v.z, v.w);
			}
			else {
				g.setFloat4(location, 0, 0, 0, 0);
			}
			return true;
		}
		else if (c.type == "vec3") {
			var v: Vec4 = null;
			helpVec.set(0, 0, 0);
			switch (c.link) {
				case "_lightPosition": {
					if (light != null) {
						#if arm_centerworld
						var t = camera.transform;
						helpVec.set(light.transform.worldx() - t.worldx(), light.transform.worldy() - t.worldy(), light.transform.worldz() - t.worldz());
						#else
						helpVec.set(light.transform.worldx(), light.transform.worldy(), light.transform.worldz());
						#end
						v = helpVec;
					}
				}
				case "_lightDirection": {
					if (light != null) {
						helpVec = light.look().normalize();
						v = helpVec;
					}
				}
				case "_sunDirection": {
					var sun = RenderPath.active.sun;
					if (sun != null) {
						helpVec = sun.look().normalize();
						v = helpVec;
					}
				}
				case "_sunColor": {
					var sun = RenderPath.active.sun;
					if (sun != null) {
						var str = sun.visible ? sun.data.raw.strength : 0.0;
						helpVec.set(sun.data.raw.color[0] * str, sun.data.raw.color[1] * str, sun.data.raw.color[2] * str);
						v = helpVec;
					}
				}
				case "_pointPosition": {
					var point = RenderPath.active.point;
					if (point != null) {
						#if arm_centerworld
						var t = camera.transform;
						helpVec.set(point.transform.worldx() - t.worldx(), point.transform.worldy() - t.worldy(), point.transform.worldz() - t.worldz());
						#else
						helpVec.set(point.transform.worldx(), point.transform.worldy(), point.transform.worldz());
						#end
						v = helpVec;
					}
				}
				#if arm_spot
				case "_spotDirection": {
					var point = RenderPath.active.point;
					if (point != null) {
						helpVec = point.look().normalize();
						v = helpVec;
					}
				}
				case "_spotRight": {
					var point = RenderPath.active.point;
					if (point != null) {
						helpVec = point.right().normalize();
						v = helpVec;
					}
				}
				#end
				case "_pointColor": {
					var point = RenderPath.active.point;
					if (point != null) {
						var str = point.visible ? point.data.raw.strength : 0.0;
						helpVec.set(point.data.raw.color[0] * str, point.data.raw.color[1] * str, point.data.raw.color[2] * str);
						v = helpVec;
					}
				}
				#if arm_ltc
				case "_lightArea0": {
					if (light != null && light.data.raw.size != null) {
						var f2: kha.FastFloat = 0.5;
						var sx: kha.FastFloat = light.data.raw.size * f2;
						var sy: kha.FastFloat = light.data.raw.size_y * f2;
						helpVec.set(-sx, sy, 0.0);
						helpVec.applymat(light.transform.world);
						v = helpVec;
					}
				}
				case "_lightArea1": {
					if (light != null && light.data.raw.size != null) {
						var f2: kha.FastFloat = 0.5;
						var sx: kha.FastFloat = light.data.raw.size * f2;
						var sy: kha.FastFloat = light.data.raw.size_y * f2;
						helpVec.set(sx, sy, 0.0);
						helpVec.applymat(light.transform.world);
						v = helpVec;
					}
				}
				case "_lightArea2": {
					if (light != null && light.data.raw.size != null) {
						var f2: kha.FastFloat = 0.5;
						var sx: kha.FastFloat = light.data.raw.size * f2;
						var sy: kha.FastFloat = light.data.raw.size_y * f2;
						helpVec.set(sx, -sy, 0.0);
						helpVec.applymat(light.transform.world);
						v = helpVec;
					}
				}
				case "_lightArea3": {
					if (light != null && light.data.raw.size != null) {
						var f2: kha.FastFloat = 0.5;
						var sx: kha.FastFloat = light.data.raw.size * f2;
						var sy: kha.FastFloat = light.data.raw.size_y * f2;
						helpVec.set(-sx, -sy, 0.0);
						helpVec.applymat(light.transform.world);
						v = helpVec;
					}
				}
				#end
				case "_cameraPosition": {
					// #if arm_centerworld
					// helpVec.set(0, 0, 0);
					// #else
					helpVec.set(camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
					// #end
					v = helpVec;
				}
				case "_cameraLook": {
					helpVec = camera.lookWorld().normalize();
					v = helpVec;
				}
				case "_cameraUp": {
					helpVec = camera.upWorld().normalize();
					v = helpVec;
				}
				case "_cameraRight": {
					helpVec = camera.rightWorld().normalize();
					v = helpVec;
				}
				case "_backgroundCol": {
					if (camera.data.raw.clear_color != null) helpVec.set(camera.data.raw.clear_color[0], camera.data.raw.clear_color[1], camera.data.raw.clear_color[2]);
					v = helpVec;
				}
				case "_hosekSunDirection": {
					var w = Scene.active.world;
					if (w != null) {
						// Clamp Z for night cycle
						helpVec.set(w.raw.sun_direction[0],
									w.raw.sun_direction[1],
									w.raw.sun_direction[2] > 0 ? w.raw.sun_direction[2] : 0);
						v = helpVec;
					}
				}
				#if rp_probes
				case "_probeNormal": {
					v = Scene.active.probes[RenderPath.active.currentProbeIndex].transform.up().normalize();
				}
				case "_probePosition": {
					v = Scene.active.probes[RenderPath.active.currentProbeIndex].transform.world.getLoc();
				}
				#end
				default:
					return false;
			}

			if (v != null) {
				g.setFloat3(location, v.x, v.y, v.z);
			}
			else {
				g.setFloat3(location, 0.0, 0.0, 0.0);
			}
			return true;
		}
		else if (c.type == "vec2") {
			var v: Vec4 = null;
			helpVec.set(0, 0, 0);
			switch (c.link) {
				case "_vec2x": {
					v = helpVec;
					v.x = 1.0;
					v.y = 0.0;
				}
				case "_vec2xInv": {
					v = helpVec;
					v.x = 1.0 / RenderPath.active.currentW;
					v.y = 0.0;
				}
				case "_vec2x2": {
					v = helpVec;
					v.x = 2.0;
					v.y = 0.0;
				}
				case "_vec2x2Inv": {
					v = helpVec;
					v.x = 2.0 / RenderPath.active.currentW;
					v.y = 0.0;
				}
				case "_vec2y": {
					v = helpVec;
					v.x = 0.0;
					v.y = 1.0;
				}
				case "_vec2yInv": {
					v = helpVec;
					v.x = 0.0;
					v.y = 1.0 / RenderPath.active.currentH;
				}
				case "_vec2y2": {
					v = helpVec;
					v.x = 0.0;
					v.y = 2.0;
				}
				case "_vec2y2Inv": {
					v = helpVec;
					v.x = 0.0;
					v.y = 2.0 / RenderPath.active.currentH;
				}
				case "_vec2y3": {
					v = helpVec;
					v.x = 0.0;
					v.y = 3.0;
				}
				case "_vec2y3Inv": {
					v = helpVec;
					v.x = 0.0;
					v.y = 3.0 / RenderPath.active.currentH;
				}
				case "_windowSize": {
					v = helpVec;
					v.x = App.w();
					v.y = App.h();
				}
				case "_screenSize": {
					v = helpVec;
					v.x = RenderPath.active.currentW;
					v.y = RenderPath.active.currentH;
				}
				case "_screenSizeInv": {
					v = helpVec;
					v.x = 1.0 / RenderPath.active.currentW;
					v.y = 1.0 / RenderPath.active.currentH;
				}
				case "_aspectRatio": {
					v = helpVec;
					v.x = RenderPath.active.currentH / RenderPath.active.currentW;
					v.y = RenderPath.active.currentW / RenderPath.active.currentH;
					v.x = v.x > 1.0 ? 1.0 : v.x;
					v.y = v.y > 1.0 ? 1.0 : v.y;
				}
				case "_cameraPlane": {
					v = helpVec;
					v.x = camera.data.raw.near_plane;
					v.y = camera.data.raw.far_plane;
				}
				case "_cameraPlaneProj": {
					var near = camera.data.raw.near_plane;
					var far = camera.data.raw.far_plane;
					v = helpVec;
					v.x = far / (far - near);
					v.y = (-far * near) / (far - near);
				}
				case "_lightPlane": {
					if (light != null) {
						v = helpVec;
						v.x = light.data.raw.near_plane;
						v.y = light.data.raw.far_plane;
					}
				}
				case "_lightPlaneProj": { // shadowCube
					if (light != null) {
						var near: kha.FastFloat = light.data.raw.near_plane;
						var far: kha.FastFloat = light.data.raw.far_plane;
						var a: kha.FastFloat = far + near;
						var b: kha.FastFloat = far - near;
						var f2: kha.FastFloat = 2.0;
						var c = f2 * far * near;
						v = helpVec;
						v.x = a / b;
						v.y = c / b;
					}
				}
				case "_shadowMapSize": {
					if (light != null && light.data.raw.cast_shadow) {
						v = helpVec;
						v.x = v.y = light.data.raw.shadowmap_size;
					}
				}
				default:
					return false;
			}

			if (v != null) {
				g.setFloat2(location, v.x, v.y);
			}
			else {
				g.setFloat2(location, 0.0, 0.0);
			}
			return true;
		}
		else if (c.type == "float") {
			var f: Null<kha.FastFloat> = null;
			switch (c.link) {
				case "_time": {
					f = Time.time();
				}
				case "_sunShadowsBias": {
					var sun = RenderPath.active.sun;
					f = sun == null ? 0.0 : sun.data.raw.shadows_bias;
				}
				case "_pointShadowsBias": {
					var point = RenderPath.active.point;
					f = point == null ? 0.0 : point.data.raw.shadows_bias;
				}
				case "_envmapStrength": {
					f = Scene.active.world == null ? 0.0 : Scene.active.world.probe.raw.strength;
				}
				case "_aspectRatioF": {
					f = RenderPath.active.currentW / RenderPath.active.currentH;
				}
				case "_aspectRatioWindowF": {
					f = iron.App.w() / iron.App.h();
				}
				case "_frameScale": {
					f = RenderPath.active.frameTime / Time.delta;
				}
				case "_fieldOfView": {
					f = camera.data.raw.fov;
				}
				default:
					return false;
			}

			g.setFloat(location, f != null ? f : 0);
			return true;
		}
		else if (c.type == "floats") {
			var fa: Float32Array = null;
			switch (c.link) {
				case "_envmapIrradiance": {
					fa = Scene.active.world == null ? WorldData.getEmptyIrradiance() : Scene.active.world.probe.irradiance;
				}
				#if arm_clusters
				case "_lightsArray": {
					fa = LightObject.lightsArray;
				}
				#if arm_spot
				case "_lightsArraySpot": {
					fa = LightObject.lightsArraySpot;
				}
				#end
				#if arm_shadowmap_atlas
				case "_pointLightsAtlasArray": {
					fa = LightObject.pointLightsData;
				}
				#end
				#end // arm_clusters
				#if arm_csm
				case "_cascadeData": {
					for (l in Scene.active.lights) {
						if (l.data.raw.type == "sun") {
							fa = l.getCascadeData();
							break;
						}
					}
				}
				#end
			}

			if (fa != null) {
				g.setFloats(location, fa);
				return true;
			}
		}
		else if (c.type == "int") {
			var i: Null<Int> = null;
			switch (c.link) {
				case "_envmapNumMipmaps": {
					var w = Scene.active.world;
					i = w != null ? w.probe.raw.radiance_mipmaps + 1 - 2 : 1; // Include basecolor and exclude 2 scaled mips
				}
				default:
					return false;
			}

			g.setInt(location, i != null ? i : 0);
			return true;
		}
		return false;
	}

	static function setObjectConstant(g: Graphics, object: Object, location: ConstantLocation, c: TShaderConstant) {
		if (c.link == null) return;

		var camera = Scene.active.camera;
		var light = RenderPath.active.light;

		if (c.type == "mat4") {
			var m: Mat4 = null;
			switch (c.link) {
				case "_worldMatrix": {
					#if arm_centerworld
					m = wmat(object.transform.worldUnpack, camera);
					#else
					m = object.transform.worldUnpack;
					#end
				}
				case "_inverseWorldMatrix": {
					#if arm_centerworld
					helpMat.getInverse(wmat(object.transform.worldUnpack, camera));
					#else
					helpMat.getInverse(object.transform.worldUnpack);
					#end
					m = helpMat;
				}
				case "_worldViewProjectionMatrix": {
					helpMat.setFrom(object.transform.worldUnpack);
					helpMat.multmat(camera.V);
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				case "_worldViewProjectionMatrixSphere": { // Billboard
					var t = object.transform;
					helpMat.setFrom(t.worldUnpack);
					helpMat.multmat(camera.V);
					var scl = new Vec4(t.scale.x, t.scale.y, t.scale.z);
					scl.mult(t.scaleWorld);
					helpMat._00 = scl.x; helpMat._10 = 0.0;   helpMat._20 = 0.0;
					helpMat._01 = 0.0;   helpMat._11 = scl.y; helpMat._21 = 0.0;
					helpMat._02 = 0.0;   helpMat._12 = 0.0;   helpMat._22 = scl.z;
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				case "_worldViewProjectionMatrixCylinder": { // Billboard - x rot 90deg
					var t = object.transform;
					helpMat.setFrom(t.worldUnpack);
					helpMat.multmat(camera.V);
					var scl = new Vec4(t.scale.x, t.scale.y, t.scale.z);
					scl.mult(t.scaleWorld);
					helpMat._00 = scl.x; helpMat._20 = 0.0;
					helpMat._01 = 0.0;   helpMat._21 = 0.0;
					helpMat._02 = 0.0;   helpMat._22 = scl.y;
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				case "_worldViewMatrix": {
					helpMat.setFrom(object.transform.worldUnpack);
					helpMat.multmat(camera.V);
					m = helpMat;
				}
				#if arm_veloc
				case "_prevWorldViewProjectionMatrix": {
					helpMat.setFrom(cast(object, MeshObject).prevMatrix);
					helpMat.multmat(camera.prevV);
					// helpMat.multmat(camera.prevP);
					helpMat.multmat(camera.P);
					m = helpMat;
				}
				case "_prevWorldMatrix": {
					m = cast(object, MeshObject).prevMatrix;
				}
				#end
				case "_sunWorldMatrix": {
					var sun = RenderPath.active.sun;
					if (sun != null) {
						helpMat.setFrom(sun.transform.worldUnpack);
						m = helpMat;
					}
				}
				case "_lightWorldViewProjectionMatrix": {
					if (light != null) {
						// object is null for DrawQuad
						object == null ? helpMat.setIdentity() : helpMat.setFrom(object.transform.worldUnpack);
						helpMat.multmat(light.VP);
						m = helpMat;
					}
				}
				case "_lightWorldViewProjectionMatrixSphere": {
					if (light != null) {
						helpMat.setFrom(object.transform.worldUnpack);

						// Align to camera..
						helpMat.multmat(camera.V);
						helpMat._00 = 1.0; helpMat._10 = 0.0; helpMat._20 = 0.0;
						helpMat._01 = 0.0; helpMat._11 = 1.0; helpMat._21 = 0.0;
						helpMat._02 = 0.0; helpMat._12 = 0.0; helpMat._22 = 1.0;
						helpMat2.getInverse(camera.V);
						helpMat.multmat(helpMat2);

						helpMat.multmat(light.VP);
						m = helpMat;
					}
				}
				case "_lightWorldViewProjectionMatrixCylinder": {
					if (light != null) {
						helpMat.setFrom(object.transform.worldUnpack);

						// Align to camera..
						helpMat.multmat(camera.V);
						helpMat._00 = 1.0; helpMat._20 = 0.0;
						helpMat._01 = 0.0; helpMat._21 = 0.0;
						helpMat._02 = 0.0; helpMat._22 = 1.0;
						helpMat2.getInverse(camera.V);
						helpMat.multmat(helpMat2);

						helpMat.multmat(light.VP);
						m = helpMat;
					}
				}
				case "_biasLightWorldViewProjectionMatrix": {
					if (light != null)  {
						// object is null for DrawQuad
						object == null ? helpMat.setIdentity() : helpMat.setFrom(object.transform.worldUnpack);
						helpMat.multmat(light.VP);
						helpMat.multmat(biasMat);
						m = helpMat;
					}
				}
				case "_biasLightWorldViewProjectionMatrixSun": {
					for (l in iron.Scene.active.lights) {
						if (l.data.raw.type == "sun") {
							// object is null for DrawQuad
							object == null ? helpMat.setIdentity() : helpMat.setFrom(object.transform.worldUnpack);
							helpMat.multmat(l.VP);
							helpMat.multmat(biasMat);
							#if arm_shadowmap_atlas
							// tile matrix
							helpMat2.setIdentity();
							// scale [0-1] coords to [0-tilescale]
							helpMat2._00 = l.tileScale[0];
							helpMat2._11 = l.tileScale[0];
							// offset coordinate start from [0, 0] to [tile-start-x, tile-start-y]
							helpMat2._30 = l.tileOffsetX[0];
							helpMat2._31 = l.tileOffsetY[0];
							helpMat.multmat(helpMat2);
							#if (!kha_opengl)
							helpMat2.setIdentity();
							helpMat2._11 = -1.0;
							helpMat2._31 = 1.0;
							helpMat.multmat(helpMat2);
							#end
							#end
							m = helpMat;
							break;
						}
					}
				}
				#if rp_probes
				case "_probeViewProjectionMatrix": {
					helpMat.setFrom(Scene.active.probes[RenderPath.active.currentProbeIndex].camera.V);
					helpMat.multmat(Scene.active.probes[RenderPath.active.currentProbeIndex].camera.P);
					m = helpMat;
				}
				#end
				#if arm_particles
				case "_particleData": {
					var mo = cast(object, MeshObject);
					if (mo.particleOwner != null && mo.particleOwner.particleSystems != null) {
						m = mo.particleOwner.particleSystems[mo.particleIndex].getData();
					}
				}
				#end
			}

			if (m == null) {
				#if arm_spot
				if (c.link.startsWith("_biasLightWorldViewProjectionMatrixSpot")) {
					var light = getSpot(c.link.charCodeAt(c.link.length - 1) - "0".code);
					if (light != null) {
						object == null ? helpMat.setIdentity() : helpMat.setFrom(object.transform.worldUnpack);
						helpMat.multmat(light.VP);
						helpMat.multmat(biasMat);
						m = helpMat;
					}
				}
				if (c.link.startsWith("_biasLightViewProjectionMatrixSpot")) {
					var light = getSpot(c.link.charCodeAt(c.link.length - 1) - "0".code);
					if (light != null) {
						helpMat.setFrom(light.VP);
						helpMat.multmat(biasMat);
						m = helpMat;
					}
				}
				#end
			}

			if (m == null && externalMat4Links != null) {
				for (fn in externalMat4Links) {
					m = fn(object, currentMat(object), c.link);
					if (m != null) break;
				}
			}

			if (m == null) return;
			g.setMatrix(location, m.self);
		}
		else if (c.type == "mat3") {
			var m: Mat3 = null;
			switch (c.link) {
				case "_normalMatrix": {
					helpMat.getInverse(object.transform.world);
					helpMat.transpose3x3();
					helpMat3.setFrom4(helpMat);
					m = helpMat3;
				}
				case "_normalMatrixSphere": {
					helpMat.setFrom(object.transform.world);
					// Align to camera..
					helpMat.multmat(camera.V);
					helpMat._00 = 1.0; helpMat._10 = 0.0; helpMat._20 = 0.0;
					helpMat._01 = 0.0; helpMat._11 = 1.0; helpMat._21 = 0.0;
					helpMat._02 = 0.0; helpMat._12 = 0.0; helpMat._22 = 1.0;
					helpMat2.getInverse(camera.V);
					helpMat.multmat(helpMat2);
					helpMat2.getInverse(helpMat);
					helpMat2.transpose3x3();
					helpMat3.setFrom4(helpMat2);
					m = helpMat3;
				}
				case "_normalMatrixCylinder": {
					helpMat.setFrom(object.transform.world);
					// Align to camera..
					helpMat.multmat(camera.V);
					helpMat._00 = 1.0; helpMat._20 = 0.0;
					helpMat._01 = 0.0; helpMat._21 = 0.0;
					helpMat._02 = 0.0; helpMat._22 = 1.0;
					helpMat2.getInverse(camera.V);
					helpMat.multmat(helpMat2);
					helpMat2.getInverse(helpMat);
					helpMat2.transpose3x3();
					helpMat3.setFrom4(helpMat2);
					m = helpMat3;
				}
				case "_viewMatrix3": {
					#if arm_centerworld
					helpMat3.setFrom4(vmat(camera.V));
					#else
					helpMat3.setFrom4(camera.V);
					#end
					m = helpMat3;
				}
			}

			if (m == null) return;
			g.setMatrix3(location, m.self);
		}
		else if (c.type == "vec4") {
			var v: Vec4 = null;
			helpVec.set(0, 0, 0);

			switch (c.link) {
				#if arm_spot
				case "_spotData": {
					// spot size (cutoff), spot blend (exponent)
					var point = RenderPath.active.point;
					if (point != null) {
						v = helpVec;
						v.x = point.data.raw.spot_size;
						v.y = point.data.raw.spot_blend;
						var scale = point.transform.scale;
						v.z = scale.z == 0.0 ? 0.0 : scale.x / scale.z;
						v.w = scale.z == 0.0 ? 0.0 : scale.y / scale.z;
					}
				}
				#end
			}

			if (v == null && externalVec4Links != null) {
				for (fn in externalVec4Links) {
					v = fn(object, currentMat(object), c.link);
					if (v != null) break;
				}
			}

			if (v == null) return;
			g.setFloat4(location, v.x, v.y, v.z, v.w);
		}
		else if (c.type == "vec3") {
			var v: Vec4 = null;
			helpVec.set(0, 0, 0);
			switch (c.link) {
				case "_dim": { // Model space
					var d = object.transform.dim;
					var s = object.transform.scale;
					helpVec.set((d.x / s.x), (d.y / s.y), (d.z / s.z));
					v = helpVec;
				}
				case "_halfDim": { // Model space
					var d = object.transform.dim;
					var s = object.transform.scale;
					helpVec.set((d.x / s.x) / 2, (d.y / s.y) / 2, (d.z / s.z) / 2);
					v = helpVec;
				}
			}

			if (v == null && externalVec3Links != null) {
				for (f in externalVec3Links) {
					v = f(object, currentMat(object), c.link);
					if (v != null) break;
				}
			}

			if (v == null) return;
			g.setFloat3(location, v.x, v.y, v.z);
		}
		else if (c.type == "vec2") {
			var vx: Null<kha.FastFloat> = null;
			var vy: Null<kha.FastFloat> = null;
			switch (c.link) {
				case "_tilesheetOffset": {
					var ts = cast(object, MeshObject).activeTilesheet;
					vx = ts.tileX;
					vy = ts.tileY;
				}
				case "_tilesheetTiles": {
					var ts = cast(object, MeshObject).activeTilesheet;
					vx = ts.raw.tilesx;
					vy = ts.raw.tilesy;
				}
				#if arm_morph_target
				case "_morphScaleOffset": {
					var mt = cast(object, MeshObject).morphTarget;
					vx = mt.scaling;
					vy = mt.offset;
				}
				case "_morphDataDim": {
					var mt = cast(object, MeshObject).morphTarget;
					vx = mt.numMorphTargets;
					vy = mt.morphBlockSize / mt.morphImageSize;
				}
				#end
			}

			if (vx == null && externalVec2Links != null) {
				for (fn in externalVec2Links) {
					var v = fn(object, currentMat(object), c.link);
					if (v != null) {
						vx = v.x;
						vy = v.y;
						break;
					}
				}
			}

			if (vx == null) return;
			g.setFloat2(location, vx, vy);
		}
		else if (c.type == "float") {
			var f: Null<kha.FastFloat> = null;
			switch (c.link) {
				case "_objectInfoIndex": {
					f = object.uid;
				}
				case "_objectInfoMaterialIndex": {
					f = currentMat(object).uid;
				}
				case "_objectInfoRandom": {
					f = object.urandom;
				}
				case "_posUnpack": {
					f = posUnpack != null ? posUnpack : 1.0;
				}
				case "_texUnpack": {
					f = texUnpack != null ? texUnpack : 1.0;
				}
			}

			if (f == null && externalFloatLinks != null) {
				for (fn in externalFloatLinks) {
					var res = fn(object, currentMat(object), c.link);
					if (res != null) {
						f = res;
						break;
					}
				}
			}

			if (f == null) return;
			g.setFloat(location, f);
		}
		else if (c.type == "floats") {
			var fa: Float32Array = null;
			switch (c.link) {
				#if arm_skin
				case "_skinBones": {
					if (object.animation != null) {
						fa = cast(object.animation, BoneAnimation).skinBuffer;
					}
				}
				#end
				#if (arm_clusters && arm_spot)
				case "_biasLightWorldViewProjectionMatrixSpotArray": {
					fa = LightObject.updateLWVPMatrixArray(object, "spot");
				}
				#end // arm_clusters
				#if arm_morph_target
				case "_morphWeights": {
					fa = cast(object, MeshObject).morphTarget.morphWeights;
				}
				#end
			}

			if (fa == null && externalFloatsLinks != null) {
				for (fn in externalFloatsLinks) {
					fa = fn(object, currentMat(object), c.link);
					if (fa != null) break;
				}
			}

			if (fa == null) return;
			g.setFloats(location, fa);
		}
		else if (c.type == "int") {
			var i: Null<Int> = null;
			switch (c.link) {
				case "_uid": {
					i = object.uid;
				}
			}

			if (i == null && externalIntLinks != null) {
				for (fn in externalIntLinks) {
					var res = fn(object, currentMat(object), c.link);
					if (res != null) {
						i = res;
						break;
					}
				}
			}

			if (i == null) return;
			g.setInt(location, i);
		}
	}

	public static function setMaterialConstants(g: Graphics, context: ShaderContext, materialContext: MaterialContext) {
		if (materialContext.raw.bind_constants != null) {
			for (i in 0...materialContext.raw.bind_constants.length) {
				var matc = materialContext.raw.bind_constants[i];
				var pos = -1;
				for (i in 0...context.raw.constants.length) {
					if (context.raw.constants[i].name == matc.name) {
						pos = i;
						break;
					}
				}
				if (pos == -1) continue;
				var c = context.raw.constants[pos];

				setMaterialConstant(g, context.constants[pos], c, matc);
			}
		}

		if (materialContext.textures != null) {
			for (i in 0...materialContext.textures.length) {
				var mname = materialContext.raw.bind_textures[i].name;

				for (j in 0...context.textureUnits.length) {
					var sname = context.raw.texture_units[j].name;
					if (mname == sname) {
						g.setTexture(context.textureUnits[j], materialContext.textures[i]);
						// After texture sampler have been assigned, set texture parameters
						materialContext.setTextureParameters(g, i, context, j);
						break;
					}
				}
			}
		}
	}

	#if arm_spot
	static function getSpot(index: Int): LightObject {
		var i = 0;
		for (l in Scene.active.lights) {
			if (l.data.raw.type != "spot" && l.data.raw.type != "area") continue;
			if (i == index) return l;
			i++;
		}
		return null;
	}
	#end

	static function currentMat(object: Object): MaterialData {
		if (object != null && Std.isOfType(object, iron.object.MeshObject)) {
			var mo = cast(object, MeshObject);
			return mo.materials[mo.materialIndex];
		}
		#if rp_decals
		if (object != null && Std.isOfType(object, iron.object.DecalObject)) {
			var mo = cast(object, DecalObject);
			return mo.material;
		}
		#end
		return null;
	}

	static function setMaterialConstant(g: Graphics, location: ConstantLocation, c: TShaderConstant, matc: TBindConstant) {
		switch (c.type) {
			case "vec4": g.setFloat4(location, matc.vec4Value[0], matc.vec4Value[1], matc.vec4Value[2], matc.vec4Value[3]);
			case "vec3": g.setFloat3(location, matc.vec3Value[0], matc.vec3Value[1], matc.vec3Value[2]);
			case "vec2": g.setFloat2(location, matc.vec2Value[0], matc.vec2Value[1]);
			case "float": g.setFloat(location,  matc.floatValue);
			case "bool": g.setBool(location, matc.boolValue);
			case "int": g.setInt(location, matc.intValue);
		}
	}

	#if arm_centerworld
	static var mm1: Mat4 = Mat4.identity();
	static var mm2: Mat4 = Mat4.identity();
	static function wmat(m: Mat4, cam: CameraObject): Mat4 {
		var t = cam.transform;
		mm1.setFrom(m);
		mm1._30 -= t.worldx();
		mm1._31 -= t.worldy();
		mm1._32 -= t.worldz();
		return mm1;
	}
	static function vmat(m: Mat4): Mat4 {
		mm2.setFrom(m);
		mm2._30 = 0;
		mm2._31 = 0;
		mm2._32 = 0;
		return mm2;
	}
	#end

	static inline function getTextureAddressing(s: String): TextureAddressing {
		return switch (s) {
			case "clamp": TextureAddressing.Clamp;
			case "mirror": TextureAddressing.Mirror;
			default: TextureAddressing.Repeat;
		}
	}

	static inline function getTextureFilter(s: String): TextureFilter {
		return switch (s) {
			case "anisotropic": TextureFilter.AnisotropicFilter;
			case "point": TextureFilter.PointFilter;
			default: TextureFilter.LinearFilter;
		}
	}

	static inline function getMipMapFilter(s: String): MipMapFilter {
		return switch (s) {
			case "linear": MipMapFilter.LinearMipFilter;
			case "point": MipMapFilter.PointMipFilter;
			default: MipMapFilter.NoMipFilter;
		}
	}
}
