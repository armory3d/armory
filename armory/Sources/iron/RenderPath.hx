package iron;

import kha.Image;
import kha.Color;
import kha.Scheduler;
import kha.graphics4.Graphics;
import kha.graphics4.CubeMap;
import kha.graphics4.DepthStencilFormat;
import kha.graphics4.TextureFormat;
import iron.system.Time;
import iron.data.SceneFormat;
import iron.data.MaterialData;
import iron.data.ShaderData;
import iron.data.ConstData;
import iron.data.Data;
import iron.object.Object;
import iron.object.LightObject;
import iron.object.MeshObject;
import iron.object.Uniforms;
import iron.object.Clipmap;

class RenderPath {

	public static var active: RenderPath;

	public var frameScissor = false;
	public var frameScissorX = 0;
	public var frameScissorY = 0;
	public var frameScissorW = 0;
	public var frameScissorH = 0;
	public var frameTime = 0.0;
	public var frame = 0;
	public var currentTarget: RenderTarget = null;
	public var currentFace: Int;
	public var light: LightObject = null;
	public var sun: LightObject = null;
	public var point: LightObject = null;
	#if rp_probes
	public var currentProbeIndex = 0;
	#end
	public var isProbePlanar = false;
	public var isProbeCube = false;
	public var isProbe = false;
	public var currentG: Graphics = null;
	public var frameG: Graphics;
	public var drawOrder = DrawOrder.Distance;
	public var paused = false;
	public var ready(get, null): Bool;
	function get_ready(): Bool { return loading == 0; }
	public var commands: Void->Void = null;
	public var setupDepthTexture: Void->Void = null;
	public var renderTargets: Map<String, RenderTarget> = new Map();
	public var depthToRenderTarget: Map<String, RenderTarget> = new Map();
	public var currentW: Int;
	public var currentH: Int;
	public var currentD: Int;
	var lastW = 0;
	var lastH = 0;
	var bindParams: Array<String>;
	var meshesSorted: Bool;
	var scissorSet = false;
	var viewportScaled = false;
	var lastFrameTime = 0.0;
	var loading = 0;
	var cachedShaderContexts: Map<String, CachedShaderContext> = new Map();
	var depthBuffers: Array<{name: String, format: String}> = [];
	var additionalTargets: Array<kha.Canvas>;

	#if (rp_voxels != "Off")
	public static var pre_clear = true;
	public static var res_pre_clear = true;
	public static var clipmapLevel = 0;
	public static var clipmaps:Array<Clipmap>;

	public static inline function getVoxelRes(): Int {
		#if (rp_voxelgi_resolution == 512)
		return 512;
		#elseif (rp_voxelgi_resolution == 256)
		return 256;
		#elseif (rp_voxelgi_resolution == 128)
		return 128;
		#elseif (rp_voxelgi_resolution == 64)
		return 64;
		#elseif (rp_voxelgi_resolution == 32)
		return 32;
		#elseif (rp_voxelgi_resolution == 16)
		return 16;
		#else
		return 0;
		#end
	}

	public static inline function getVoxelResZ(): Float {
		#if (rp_voxelgi_resolution_z == 1.0)
		return 1.0;
		#elseif (rp_voxelgi_resolution_z == 0.5)
		return 0.5;
		#elseif (rp_voxelgi_resolution_z == 0.25)
		return 0.25;
		#elseif (rp_voxelgi_resolution_z == 0.125)
		return 0.125;
		#else
		return 0.0;
		#end
	}
	#end

	#if arm_debug
	public static var drawCalls = 0;
	public static var batchBuckets = 0;
	public static var batchCalls = 0;
	public static var culled = 0;
	public static var numTrisMesh = 0;
	public static var numTrisShadow = 0;
	#end

	public static function setActive(renderPath: RenderPath) {
		active = renderPath;
	}

	public function new() {}

	public function renderFrame(g: Graphics) {
		if (!ready || paused || iron.App.w() == 0 || iron.App.h() == 0) return;

		if (lastW > 0 && (lastW != iron.App.w() || lastH != iron.App.h())) resize();
		lastW = iron.App.w();
		lastH = iron.App.h();

		frameTime = Time.time() - lastFrameTime;
		lastFrameTime = Time.time();

		#if arm_debug
		drawCalls = 0;
		batchBuckets = 0;
		batchCalls = 0;
		culled = 0;
		numTrisMesh = 0;
		numTrisShadow = 0;
		#end

		#if (rp_voxels != "Off")
		clipmapLevel = (clipmapLevel + 1) % Main.voxelgiClipmapCount;
		var clipmap = clipmaps[clipmapLevel];

		clipmap.voxelSize = clipmaps[0].voxelSize * Math.pow(2.0, clipmapLevel);

		var texelSize = 2.0 * clipmap.voxelSize;
		var camera = iron.Scene.active.camera;
		var center = new iron.math.Vec3(
			Math.floor(camera.transform.worldx() / texelSize) * texelSize,
			Math.floor(camera.transform.worldy() / texelSize) * texelSize,
			Math.floor(camera.transform.worldz() / texelSize) * texelSize
		);

		clipmap.offset_prev.x = Std.int((clipmap.center.x - center.x) / texelSize);
		clipmap.offset_prev.y = Std.int((clipmap.center.y - center.y) / texelSize);
		clipmap.offset_prev.z = Std.int((clipmap.center.z - center.z) / texelSize);
		clipmap.center = center;

		var res = getVoxelRes();
		var resZ = getVoxelResZ();
		var extents = new iron.math.Vec3(clipmap.voxelSize * res, clipmap.voxelSize * res, clipmap.voxelSize * resZ);
		if (clipmap.extents.x != extents.x || clipmap.extents.y != extents.y || clipmap.extents.z != extents.z)
		{
			pre_clear = true;
		}
		clipmap.extents = extents;
		#end

		// Render to screen or probe
		var cam = Scene.active.camera;
		isProbePlanar = cam != null && cam.renderTarget != null;
		isProbeCube = cam != null && cam.renderTargetCube != null;
		isProbe = isProbePlanar || isProbeCube;

		if (isProbePlanar) frameG = cam.renderTarget.g4;
		else if (isProbeCube) frameG = cam.renderTargetCube.g4;
		else frameG = g;

		currentW = iron.App.w();
		currentH = iron.App.h();
		currentD = 1;
		currentFace = -1;
		meshesSorted = false;

		for (l in Scene.active.lights) {
			if (l.visible) l.buildMatrix(Scene.active.camera);
			if (l.data.raw.type == "sun") sun = l;
			else point = l;
		}
		light = Scene.active.lights[0];

		commands();

		if (!isProbe) frame++;
	}

	public function setTarget(target: String, additional: Array<String> = null, viewportScale = 1.0) {
		if (target == "") { // Framebuffer
			currentD = 1;
			currentTarget = null;
			currentFace = -1;
			if (isProbeCube) {
				currentW = Scene.active.camera.renderTargetCube.width;
				currentH = Scene.active.camera.renderTargetCube.height;
				begin(frameG, Scene.active.camera.currentFace);
			}
			else { // Screen, planar probe
				currentW = iron.App.w();
				currentH = iron.App.h();
				if (frameScissor) setFrameScissor();
				begin(frameG);
				if (!isProbe) {
					setCurrentViewport(iron.App.w(), iron.App.h());
					setCurrentScissor(iron.App.w(), iron.App.h());
				}
			}
		}
		else { // Render target
			var rt = renderTargets.get(target);
			currentTarget = rt;
			var additionalImages: Array<kha.Canvas> = null;
			if (additional != null) {
				additionalImages = [];
				for (s in additional) {
					var t = renderTargets.get(s);
					additionalImages.push(t.image);
				}
			}
			var targetG = rt.isCubeMap ? rt.cubeMap.g4 : rt.image.g4;
			currentW = rt.isCubeMap ? rt.cubeMap.width : rt.image.width;
			currentH = rt.isCubeMap ? rt.cubeMap.height : rt.image.height;
			if (rt.is3D) currentD = rt.image.depth;
			begin(targetG, additionalImages, currentFace);
		}
		if (viewportScale != 1.0) {
			viewportScaled = true;
			var viewW = Std.int(currentW * viewportScale);
			var viewH = Std.int(currentH * viewportScale);
			currentG.viewport(0, viewH, viewW, viewH);
			currentG.scissor(0, viewH, viewW, viewH);
		}
		else if (viewportScaled) { // Reset viewport
			viewportScaled = false;
			setCurrentViewport(currentW, currentH);
			setCurrentScissor(currentW, currentH);
		}
		bindParams = null;
	}

	public function setDepthFrom(target: String, from: String) {
		var rt = renderTargets.get(target);
		rt.image.setDepthStencilFrom(renderTargets.get(from).image);
	}

	inline function begin(g: Graphics, additionalRenderTargets: Array<kha.Canvas> = null, face = -1) {
		if (currentG != null) end();
		currentG = g;
		additionalTargets = additionalRenderTargets;
		face >= 0 ? g.beginFace(face) : g.begin(additionalRenderTargets);
	}

	inline function end() {
		if (scissorSet) {
			currentG.disableScissor();
			scissorSet = false;
		}
		currentG.end();
		currentG = null;
		bindParams = null;
	}

	public function setCurrentViewportWithOffset(viewW:Int, viewH:Int, offsetX: Int, offsetY: Int) {
		currentG.viewport(iron.App.x() + offsetX, currentH - viewH + iron.App.y() - offsetY, viewW, viewH);
	}

	public function setCurrentViewport(viewW: Int, viewH: Int) {
		currentG.viewport(iron.App.x(), currentH - (viewH - iron.App.y()), viewW, viewH);
	}

	public function setCurrentScissor(viewW: Int, viewH: Int) {
		currentG.scissor(iron.App.x(), currentH - (viewH - iron.App.y()), viewW, viewH);
		scissorSet = true;
	}

	public function setFrameScissor() {
		frameG.scissor(frameScissorX, currentH - (frameScissorH - frameScissorY), frameScissorW, frameScissorH);
	}

	public function setViewport(viewW: Int, viewH: Int) {
		setCurrentViewport(viewW, viewH);
		setCurrentScissor(viewW, viewH);
	}

	public function clearTarget(colorFlag: Null<Int> = null, depthFlag: Null<Float> = null) {
		if (colorFlag == -1) { // -1 == 0xffffffff
			if (Scene.active.world != null) {
				colorFlag = Scene.active.world.raw.background_color;
			}
			else if (Scene.active.camera != null) {
				var cc = Scene.active.camera.data.raw.clear_color;
				if (cc != null) colorFlag = kha.Color.fromFloats(cc[0], cc[1], cc[2]);
			}
		}
		currentG.clear(colorFlag, depthFlag, null);
	}

	public function clearImage(target: String, color: Int) {
		var rt = renderTargets.get(target);
		rt.image.clear(0, 0, 0, rt.image.width, rt.image.height, rt.image.depth, color);
	}

	public function generateMipmaps(target: String) {
		var rt = renderTargets.get(target);
		rt.image.generateMipmaps(1000);
	}

	static inline function boolToInt(b: Bool): Int {
		return b ? 1 : 0;
	}

	public static function sortMeshesDistance(meshes: Array<MeshObject>) {
		meshes.sort(function(a, b): Int {
			#if rp_depth_texture
			var depthDiff = boolToInt(a.depthRead) - boolToInt(b.depthRead);
			if (depthDiff != 0) return depthDiff;
			#end

			return a.cameraDistance >= b.cameraDistance ? 1 : -1;
		});
	}

	public static function sortMeshesShader(meshes: Array<MeshObject>) {
		meshes.sort(function(a, b): Int {
			#if rp_depth_texture
			var depthDiff = boolToInt(a.depthRead) - boolToInt(b.depthRead);
			if (depthDiff != 0) return depthDiff;
			#end

			return a.materials[0].name >= b.materials[0].name ? 1 : -1;
		});
	}

	public function drawMeshes(context: String) {
		var isShadows = context == "shadowmap";
		if (isShadows) {
			// Disabled shadow casting for this light
			if (light == null || !light.data.raw.cast_shadow || !light.visible || light.data.raw.strength == 0) return;
		}
		// Single face attached
		if (currentFace >= 0 && light != null) light.setCubeFace(currentFace, Scene.active.camera);

		var drawn = false;

		#if arm_csm
		if (isShadows && light.data.raw.type == "sun") {
			var step = currentH; // Atlas with tiles on x axis
			for (i in 0...LightObject.cascadeCount) {
				light.setCascade(Scene.active.camera, i);
				currentG.viewport(i * step, 0, step, step);
				submitDraw(context);
			}
			drawn = true;
		}
		#end

		#if arm_clusters
		if (context == "mesh") LightObject.updateClusters(Scene.active.camera);
		#end

		if (!drawn) submitDraw(context);

		#if arm_debug
		// Callbacks to specific context
		if (contextEvents != null) {
			var ar = contextEvents.get(context);
			if (ar != null) for (i in 0...ar.length) ar[i](currentG, i, ar.length);
		}
		#end

		end();
	}

	@:access(iron.object.MeshObject)
	function submitDraw(context: String) {
		var camera = Scene.active.camera;
		var meshes = Scene.active.meshes;
		MeshObject.lastPipeline = null;

		if (!meshesSorted && camera != null) { // Order max once per frame for now
			var camX = camera.transform.worldx();
			var camY = camera.transform.worldy();
			var camZ = camera.transform.worldz();
			for (mesh in meshes) {
				mesh.computeCameraDistance(camX, camY, camZ);
				mesh.computeDepthRead();
			}
			#if arm_batch
			sortMeshesDistance(Scene.active.meshBatch.nonBatched);
			#else
			drawOrder == DrawOrder.Shader ? sortMeshesShader(meshes) : sortMeshesDistance(meshes);
			#end
			meshesSorted = true;
		}

		#if arm_batch
		Scene.active.meshBatch.render(currentG, context, bindParams);
		#else
		inline meshRenderLoop(currentG, context, bindParams, meshes);
		#end
	}

	static inline function meshRenderLoop(g: Graphics, context: String, _bindParams: Array<String>, _meshes: Array<MeshObject>) {
		var isReadingDepth = false;

		for (m in _meshes) {
			#if rp_depth_texture
				// First mesh that reads depth
				if (!isReadingDepth && m.depthRead) {
					if (context == "mesh") {
						// Copy the depth buffer so that we can read from it while writing
						active.setupDepthTexture();
					}
					#if rp_depthprepass
					else if (context == "depth") {
						// Don't render in depth prepass
						break;
					}
					#end

					isReadingDepth = true;
				}
			#end

			m.render(g, context, _bindParams);
		}
	}

	#if arm_debug
	static var contextEvents: Map<String, Array<Graphics->Int->Int->Void>> = null;
	public static function notifyOnContext(name: String, onContext: Graphics->Int->Int->Void) {
		if (contextEvents == null) contextEvents = new Map();
		var ar = contextEvents.get(name);
		if (ar == null) {
			ar = [];
			contextEvents.set(name, ar);
		}
		ar.push(onContext);
	}
	#end

	#if rp_decals
	public function drawDecals(context: String) {
		if (ConstData.boxVB == null) ConstData.createBoxData();
		for (decal in Scene.active.decals) {
			decal.render(currentG, context, bindParams);
		}
		end();
	}
	#end

	public function drawSkydome(handle: String) {
		if (ConstData.skydomeVB == null) ConstData.createSkydomeData();
		var cc: CachedShaderContext = cachedShaderContexts.get(handle);
		if (cc.context == null) return; // World data not specified
		currentG.setPipeline(cc.context.pipeState);
		Uniforms.setContextConstants(currentG, cc.context, bindParams);
		Uniforms.setObjectConstants(currentG, cc.context, null); // External hosek
		#if arm_deinterleaved
		currentG.setVertexBuffers(ConstData.skydomeVB);
		#else
		currentG.setVertexBuffer(ConstData.skydomeVB);
		#end
		currentG.setIndexBuffer(ConstData.skydomeIB);
		currentG.drawIndexedVertices();
		end();
	}

	#if rp_probes
	public function drawVolume(object: Object, handle: String) {
		if (ConstData.boxVB == null) ConstData.createBoxData();
		var cc: CachedShaderContext = cachedShaderContexts.get(handle);
		currentG.setPipeline(cc.context.pipeState);
		Uniforms.setContextConstants(currentG, cc.context, bindParams);
		Uniforms.setObjectConstants(currentG, cc.context, object);
		currentG.setVertexBuffer(ConstData.boxVB);
		currentG.setIndexBuffer(ConstData.boxIB);
		currentG.drawIndexedVertices();
		end();
	}
	#end

	public function bindTarget(target: String, uniform: String) {
		if (bindParams != null) {
			bindParams.push(target);
			bindParams.push(uniform);
		}
		else bindParams = [target, uniform];
	}

	// Full-screen triangle
	public function drawShader(handle: String) {
		// file/data_name/context
		var cc: CachedShaderContext = cachedShaderContexts.get(handle);
		if (ConstData.screenAlignedVB == null) ConstData.createScreenAlignedData();
		currentG.setPipeline(cc.context.pipeState);
		Uniforms.setContextConstants(currentG, cc.context, bindParams);
		Uniforms.setObjectConstants(currentG, cc.context, null);
		currentG.setVertexBuffer(ConstData.screenAlignedVB);
		currentG.setIndexBuffer(ConstData.screenAlignedIB);
		currentG.drawIndexedVertices();

		end();
	}

	public function getComputeShader(handle: String): kha.compute.Shader {
		return Reflect.field(kha.Shaders, handle + "_comp");
	}

	#if (kha_krom && arm_vr)
	public function drawStereo(drawMeshes: Int->Void) {
		for (eye in 0...2) {
			Krom.vrBeginRender(eye);
			drawMeshes(eye);
			Krom.vrEndRender(eye);
		}
	}
	#end

	public function loadShader(handle: String) {
		loading++;
		var cc: CachedShaderContext = cachedShaderContexts.get(handle);
		if (cc != null) {
			loading--;
			return;
		}

		cc = new CachedShaderContext();
		cachedShaderContexts.set(handle, cc);

		// file/data_name/context
		var shaderPath = handle.split("/");

		#if arm_json
		shaderPath[0] += ".json";
		#end

		Data.getShader(shaderPath[0], shaderPath[1], function(res: ShaderData) {
			cc.context = res.getContext(shaderPath[2]);
			loading--;
		});
	}

	public function unloadShader(handle: String) {
		cachedShaderContexts.remove(handle);

		// file/data_name/context
		var shaderPath = handle.split("/");
		// Todo: Handle context overrides (see Data.getShader())
		Data.cachedShaders.remove(shaderPath[1]);
	}

	public function unload() {
		for (rt in renderTargets) rt.unload();
	}

	public function resize() {
		if (kha.System.windowWidth() == 0 || kha.System.windowHeight() == 0) return;

		// Make sure depth buffer is attached to single target only and gets released once
		for (rt in renderTargets) {
			if (rt == null ||
				rt.raw.width > 0 ||
				rt.depthStencilFrom == "" ||
				rt == depthToRenderTarget.get(rt.depthStencilFrom)) {
				continue;
			}

			var nodepth: RenderTarget = null;
			for (rt2 in renderTargets) {
				if (rt2 == null ||
					rt2.raw.width > 0 ||
					rt2.depthStencilFrom != "" ||
					depthToRenderTarget.get(rt2.raw.depth_buffer) != null ||
					rt2.raw.is_image == true) {
					continue;
				}

				nodepth = rt2;
				break;
			}

			if (nodepth != null) {
				rt.image.setDepthStencilFrom(nodepth.image);
			}
		}

		// Resize textures
		for (rt in renderTargets) {
			if (rt != null && rt.raw.width == 0) {
				App.notifyOnInit(rt.image.unload);
				rt.image = createImage(rt.raw, rt.depthStencil);
			}
		}

		// Attach depth buffers
		for (rt in renderTargets) {
			if (rt != null && rt.depthStencilFrom != "") {
				rt.image.setDepthStencilFrom(depthToRenderTarget.get(rt.depthStencilFrom).image);
			}
		}

		#if (rp_voxels != "Off")
		res_pre_clear = true;
		#end
	}

	public function createRenderTarget(t: RenderTargetRaw): RenderTarget {
		var rt = createTarget(t);
		renderTargets.set(t.name, rt);
		return rt;
	}

	public function createDepthBuffer(name: String, format: String = null) {
		depthBuffers.push({ name: name, format: format });
	}

	function createTarget(t: RenderTargetRaw): RenderTarget {
		var rt = new RenderTarget(t);
		// With depth buffer
		if (t.depth_buffer != null) {
			rt.hasDepth = true;
			var depthTarget = depthToRenderTarget.get(t.depth_buffer);

			if (depthTarget == null) { // Create new one
				for (db in depthBuffers) {
					if (db.name == t.depth_buffer) {
						depthToRenderTarget.set(db.name, rt);
						rt.depthStencil = getDepthStencilFormat(db.format);
						rt.image = createImage(t, rt.depthStencil);
						break;
					}
				}
			}
			else { // Reuse
				rt.depthStencil = DepthStencilFormat.NoDepthAndStencil;
				rt.depthStencilFrom = t.depth_buffer;
				rt.image = createImage(t, rt.depthStencil);
				rt.image.setDepthStencilFrom(depthTarget.image);
			}
		}
		else { // No depth buffer
			rt.hasDepth = false;
			if (t.depth != null && t.depth > 1) rt.is3D = true;
			if (t.is_cubemap) {
				rt.isCubeMap = true;
				rt.depthStencil = DepthStencilFormat.NoDepthAndStencil;
				rt.cubeMap = createCubeMap(t, rt.depthStencil);
			}
			else {
				rt.depthStencil = DepthStencilFormat.NoDepthAndStencil;
				rt.image = createImage(t, rt.depthStencil);
			}
		}
		return rt;
	}

	function createImage(t: RenderTargetRaw, depthStencil: DepthStencilFormat): Image {
		var width = t.width == 0 ? iron.App.w() : t.width;
		var height = t.height == 0 ? iron.App.h() : t.height;
		var depth = t.depth != null ? t.depth : 0;
		if (t.displayp != null) { // 1080p/..
			if (width > height) {
				width = Std.int(width * (t.displayp / height));
				height = t.displayp;
			}
			else {
				height = Std.int(height * (t.displayp / width));
				width = t.displayp;
			}
		}
		if (t.scale != null) {
			width = Std.int(width * t.scale);
			height = Std.int(height * t.scale);
			depth = Std.int(depth * t.scale);
		}
		if (width < 1) width = 1;
		if (height < 1) height = 1;
		if (t.depth != null && t.depth > 1) { // 3D texture
			// Image only
			var img = Image.create3D(width, height, depth,
				t.format != null ? getTextureFormat(t.format) : TextureFormat.RGBA32);
			if (t.mipmaps)
				img.generateMipmaps(1000); // Allocate mipmaps
			return img;
		}
		else { // 2D texture
			if (t.is_image != null && t.is_image) { // Image
				var img = Image.create(width, height,
					t.format != null ? getTextureFormat(t.format) : TextureFormat.RGBA32);
				if (t.mipmaps)
					img.generateMipmaps(1000); // Allocate mipmaps
				return img;
			}
			else { // Render target
				return Image.createRenderTarget(width, height,
					t.format != null ? getTextureFormat(t.format) : TextureFormat.RGBA32,
					depthStencil);
			}
		}
	}

	function createCubeMap(t: RenderTargetRaw, depthStencil: DepthStencilFormat): CubeMap {
		return CubeMap.createRenderTarget(t.width,
			t.format != null ? getTextureFormat(t.format) : TextureFormat.RGBA32,
			depthStencil);
	}

	inline function getTextureFormat(s: String): TextureFormat {
		switch (s) {
			case "RGBA32": return TextureFormat.RGBA32;
			case "RGBA64": return TextureFormat.RGBA64;
			case "RGBA128": return TextureFormat.RGBA128;
			case "DEPTH16": return TextureFormat.DEPTH16;
			case "R32": return TextureFormat.A32;
			case "R16": return TextureFormat.A16;
			case "R8": return TextureFormat.L8;
			default: return TextureFormat.RGBA32;
		}
	}

	inline function getDepthStencilFormat(s: String): DepthStencilFormat {
		if (s == null || s == "") return DepthStencilFormat.DepthOnly;
		switch (s) {
			case "DEPTH24": return DepthStencilFormat.DepthOnly;
			case "DEPTH16": return DepthStencilFormat.Depth16;
			default: return DepthStencilFormat.DepthOnly;
		}
	}

	#if arm_shadowmap_atlas
	// Allow setting a target with manual end() calling, this is to render multiple times to the same image (atlas)
	// TODO: allow manual end() calling in existing functions to prevent duplicated code
	public function setTargetStream(target:String, additional:Array<String> = null, viewportScale = 1.0) {
		if (target == "") { // Framebuffer
			currentD = 1;
			currentTarget = null;
			currentFace = -1;
			if (isProbeCube) {
				currentW = Scene.active.camera.renderTargetCube.width;
				currentH = Scene.active.camera.renderTargetCube.height;
				beginStream(frameG, Scene.active.camera.currentFace);
			}
			else { // Screen, planar probe
				currentW = iron.App.w();
				currentH = iron.App.h();
				if (frameScissor) {
					setFrameScissor();
				}
				beginStream(frameG);
				if (!isProbe) {
					setCurrentViewport(iron.App.w(), iron.App.h());
					setCurrentScissor(iron.App.w(), iron.App.h());
				}
			}
		}
		else { // Render target
			var rt = renderTargets.get(target);
			currentTarget = rt;
			var additionalImages:Array<kha.Canvas> = null;
			if (additional != null) {
				additionalImages = [];
				for (s in additional) {
					var t = renderTargets.get(s);
					additionalImages.push(t.image);
				}
			}
			var targetG = rt.isCubeMap ? rt.cubeMap.g4 : rt.image.g4;
			currentW = rt.isCubeMap ? rt.cubeMap.width : rt.image.width;
			currentH = rt.isCubeMap ? rt.cubeMap.height : rt.image.height;
			if (rt.is3D) {
				currentD = rt.image.depth;
			}
			beginStream(targetG, additionalImages, currentFace);
		}
		if (viewportScale != 1.0) {
			viewportScaled = true;
			var viewW = Std.int(currentW * viewportScale);
			var viewH = Std.int(currentH * viewportScale);
			currentG.viewport(0, viewH, viewW, viewH);
			currentG.scissor(0, viewH, viewW, viewH);
		}
		else if (viewportScaled) { // Reset viewport
			viewportScaled = false;
			setCurrentViewport(currentW, currentH);
			setCurrentScissor(currentW, currentH);
		}
		bindParams = null;
	}

	inline function beginStream(g:Graphics, additionalRenderTargets:Array<kha.Canvas> = null, face = -1) {
		currentG = g;
		additionalTargets = additionalRenderTargets;
		face >= 0 ? g.beginFace(face) : g.begin(additionalRenderTargets);
	}

	public function endStream() {
		if (scissorSet) {
			currentG.disableScissor();
			scissorSet = false;
		}
		currentG.end();
		currentG = null;
		bindParams = null;
	}

	public function drawMeshesStream(context:String) {
		// Single face attached
		if (currentFace >= 0 && light != null) {
			light.setCubeFace(currentFace, Scene.active.camera);
		}

		#if arm_clusters
		if (context == "mesh") {
			LightObject.updateClusters(Scene.active.camera);
		}
		#end

		submitDraw(context);

		#if arm_debug
		// Callbacks to specific context
		if (contextEvents != null) {
			var ar = contextEvents.get(context);
			if (ar != null) {
				for (i in 0...ar.length) {
					ar[i](currentG, i, ar.length);
				}
			}
		}
		#end
	}
	#end // arm_shadowmap_atlas
}

class RenderTargetRaw {
	public var name: String;
	public var width: Int;
	public var height: Int;
	public var format: String = null;
	public var scale: Null<Float> = null;
	public var displayp: Null<Int> = null; // Set to 1080p/...
	public var depth_buffer: String = null; // 2D texture
	public var mipmaps: Null<Bool> = null;
	public var depth: Null<Int> = null; // 3D texture
	public var is_image: Null<Bool> = null; // Image
	public var is_cubemap: Null<Bool> = null; // Cubemap
	public function new() {}
}

class RenderTarget {
	public var raw: RenderTargetRaw;
	public var depthStencil: DepthStencilFormat;
	public var depthStencilFrom = "";
	public var image: Image = null; // RT or image
	public var cubeMap: CubeMap = null;
	public var hasDepth = false;
	public var is3D = false; // sampler2D / sampler3D
	public var isCubeMap = false;
	public function new(raw: RenderTargetRaw) { this.raw = raw; }
	public function unload() {
		if (image != null) image.unload();
		if (cubeMap != null) cubeMap.unload();
	}
}

class CachedShaderContext {
	public var context: ShaderContext;
	public function new() {}
}

@:enum abstract DrawOrder(Int) from Int {
	var Distance = 0; // Early-z
	var Shader = 1; // Less state changes
	// var Mix = 2; // Distance buckets sorted by shader
}
