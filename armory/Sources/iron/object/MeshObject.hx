package iron.object;

import haxe.ds.Vector;
import kha.graphics4.Graphics;
import kha.graphics4.PipelineState;
import iron.math.Vec4;
import iron.math.Mat4;
import iron.data.MeshData;
import iron.data.MaterialData;
import iron.data.ShaderData;
import iron.data.SceneFormat;

class MeshObject extends Object {
	public var data: MeshData = null;
	public var materials: Vector<MaterialData>;
	public var materialIndex = 0;
	public var depthRead(default, null) = false;
	#if arm_particles
	public var particleSystems: Array<ParticleSystem> = null; // Particle owner
	public var render_emitter = true;
	#if arm_gpu_particles
	public var particleOwner: MeshObject = null; // Particle object
	public var particleChildren: Array<MeshObject> = null;
	public var particleIndex = -1;
	#end #end
	public var cameraDistance: Float;
	public var cameraList: Array<String> = null;
	public var screenSize = 0.0;
	public var frustumCulling = true;
	public var tilesheet: Tilesheet = null;
	public var skip_context: String = null; // Do not draw this context
	public var force_context: String = null; // Draw only this context
	static var lastPipeline: PipelineState = null;
	#if arm_morph_target
	public var morphTarget: MorphTarget = null;
	#end

	#if arm_veloc
	public var prevMatrix = Mat4.identity();
	#end

	public function new(data: MeshData, materials: Vector<MaterialData>) {
		super();

		this.materials = materials;
		setData(data);
		Scene.active.meshes.push(this);
	}

	public function setData(data: MeshData) {
		this.data = data;
		data.refcount++;

		#if (!arm_batch)
		data.geom.build();
		#end

		// Scale-up packed (-1,1) mesh coords
		transform.scaleWorld = data.scalePos;
	}

	#if arm_batch
	@:allow(iron.Scene)
	function batch(isLod: Bool) {
		var batched = Scene.active.meshBatch.addMesh(this, isLod);
		if (!batched) data.geom.build();
	}
	#end

	override public function remove() {
		#if arm_batch
		Scene.active.meshBatch.removeMesh(this);
		#end
		#if arm_gpu_particles
		if (particleChildren != null) {
			for (c in particleChildren) c.remove();
			particleChildren = null;
		}
		#end
		#if arm_particles
		if (particleSystems != null) {
			for (psys in particleSystems) {
				#if arm_cpu_particles psys.stop(); #end
				psys.remove();
			}
			particleSystems = null;
		}
		#end
		if (tilesheet != null) tilesheet.remove();
		if (Scene.active != null) Scene.active.meshes.remove(this);
		data.refcount--;
		super.remove();
	}

	override public function setupAnimation(oactions: Array<TSceneFormat> = null) {
		#if arm_skin
		var hasAction = parent != null && parent.raw != null && parent.raw.bone_actions != null;
		if (hasAction) {
			var armatureName = parent.name;
			animation = getParentArmature(armatureName);
			if (animation == null) animation = new BoneAnimation(armatureName);
			if (data.isSkinned) cast(animation, BoneAnimation).setSkin(this);
		}
		#end
		super.setupAnimation(oactions);
	}

	#if arm_morph_target
	override public function setupMorphTargets() {
		if (data.raw.morph_target != null) {
			morphTarget = new MorphTarget(data.raw.morph_target);
		}
	}
	#end

	#if arm_particles
	public function setupParticleSystem(sceneName: String, pref: TParticleReference) {
		if (particleSystems == null) particleSystems = [];
		var psys = new ParticleSystem(sceneName, pref, this);
		particleSystems.push(psys);
	}
	#end

	public function setupTilesheet(sceneName: String, materialRef: String, actionRef: String) {
		tilesheet = new Tilesheet(sceneName, materialRef, actionRef);
	}

	public function setTilesheet(sceneName: String, materialRef: String, actionRef: String) {
		// If same material, just play the action
		if (tilesheet != null && tilesheet.materialName == materialRef) {
			tilesheet.play(actionRef);
		} else {
			// Setup new tilesheet
			if (tilesheet != null) tilesheet.remove();
			setupTilesheet(sceneName, materialRef, actionRef);
		}
	}

	inline function isLodMaterial(): Bool {
		return (raw != null && raw.lod_material != null && raw.lod_material == true);
	}

	function setCulled(isShadow: Bool, b: Bool): Bool {
		isShadow ? culledShadow = b : culledMesh = b;
		culled = culledMesh && culledShadow;
		#if arm_debug
		if (b) RenderPath.culled++;
		#end
		return b;
	}

	public function cullMaterial(context: String): Bool {
		// Skip render if material does not contain current context
		var mats = materials;
		if (!isLodMaterial() && !validContext(mats, context)) return true;

		var isShadow = context == "shadowmap";
		if (!visibleMesh && !isShadow) return setCulled(isShadow, true);
		if (!visibleShadow && isShadow) return setCulled(isShadow, true);

		if (skip_context == context) return setCulled(isShadow, true);
		if (force_context != null && force_context != context) return setCulled(isShadow, true);

		return setCulled(isShadow, false);
	}

	function cullMesh(context: String, camera: CameraObject, light: LightObject): Bool {
		if (camera == null) return false;

		if (camera.data.raw.frustum_culling && frustumCulling) {
			// Scale radius for skinned mesh and particle system
			// TODO: define skin & particle bounds
			var radiusScale = data.isSkinned ? 2.0 : 1.0;
			#if arm_gpu_particles
			// particleSystems for update, particleOwner for render
			if (particleSystems != null || particleOwner != null) radiusScale *= 1000;
			#end
			if (context == "voxel") radiusScale *= 100;
			if (data.geom.instanced) radiusScale *= 100;
			var isShadow = context == "shadowmap";
			var frustumPlanes = isShadow ? light.frustumPlanes : camera.frustumPlanes;

			if (isShadow && light.data.raw.type != "sun") { // Non-sun light bounds intersect camera frustum
				light.transform.radius = light.data.raw.far_plane;
				if (!CameraObject.sphereInFrustum(camera.frustumPlanes, light.transform)) {
					return setCulled(isShadow, true);
				}
			}

			if (!CameraObject.sphereInFrustum(frustumPlanes, transform, radiusScale)) {
				return setCulled(isShadow, true);
			}
		}

		culled = false;
		return culled;
	}

	function skipContext(context: String, mat: MaterialData): Bool {
		if (mat.raw.skip_context != null &&
			mat.raw.skip_context == context) {
			return true;
		}
		return false;
	}

	function getContexts(context: String, materials: Vector<MaterialData>, materialContexts: Array<MaterialContext>, shaderContexts: Array<ShaderContext>) {
		for (mat in materials) {
			var found = false;
			for (i in 0...mat.raw.contexts.length) {
				if (mat.raw.contexts[i].name.substr(0, context.length) == context) {
					materialContexts.push(mat.contexts[i]);
					shaderContexts.push(mat.shader.getContext(context));
					found = true;
					break;
				}
			}
			if (!found) {
				materialContexts.push(null);
				shaderContexts.push(null);
			}
		}
	}

	public function render(g: Graphics, context: String, bindParams: Array<String>) {
		if (data == null || !data.geom.ready) return; // Data not yet streamed
		if (!visible) return; // Skip render if object is hidden
		if (cullMesh(context, Scene.active.camera, RenderPath.active.light)) return;
		var meshContext = raw != null ? context == "mesh" : false;

		if (cameraList != null && cameraList.indexOf(Scene.active.camera.name) < 0) return;

		#if arm_gpu_particles
		if (raw != null && raw.is_particle && particleOwner == null) return; // Instancing not yet set-up by particle system owner
		if (particleSystems != null && meshContext) {
			if (particleChildren == null) {
				particleChildren = [];
				for (psys in particleSystems) {
					// var c: MeshObject = cast Scene.active.getChild(psys.data.raw.instance_object);
					Scene.active.spawnObject(psys.data.raw.instance_object, null, function(o: Object) {
						if (o != null) {
							var c: MeshObject = cast o;
							c.cameraList = this.cameraList;
							particleChildren.push(c);
							c.particleOwner = this;
							c.particleIndex = particleChildren.length - 1;
						}
					});
				}
			}
			for (i in 0...particleSystems.length) {
				particleSystems[i].update(particleChildren[i]);
			}
		}
		#end
		#if arm_particles
		if (particleSystems != null && particleSystems.length > 0 && !render_emitter) return;
        if (particleSystems == null && cullMaterial(context)) return;
		#else
        if (cullMaterial(context)) return;
		#end

		// Get lod
		var mats = materials;
		var lod = this;
		if (raw != null && raw.lods != null && raw.lods.length > 0) {
			computeScreenSize(Scene.active.camera);
			initLods();
			if (context == "voxel") {
				// Voxelize using the lowest lod
				lod = cast lods[lods.length - 1];
			}
			else {
				// Select lod
				for (i in 0...raw.lods.length) {
					// Lod found
					if (screenSize > raw.lods[i].screen_size) break;
					lod = cast lods[i];
					if (isLodMaterial()) mats = lod.materials;
				}
			}
			if (lod == null) return; // Empty object
		}
		#if arm_debug
		else computeScreenSize(Scene.active.camera);
		#end
		if (isLodMaterial() && !validContext(mats, context)) return;

		// Get context
		var materialContexts: Array<MaterialContext> = [];
		var shaderContexts: Array<ShaderContext> = [];
		getContexts(context, mats, materialContexts, shaderContexts);

		Uniforms.posUnpack = data.scalePos;
		Uniforms.texUnpack = data.scaleTex;
		transform.update();

		// Render mesh
		var ldata = lod.data;

		// Next pass rendering first (inverse order)
		renderNextPass(g, context, bindParams, lod);

		for (i in 0...ldata.geom.indexBuffers.length) {

			var mi = ldata.geom.materialIndices[i];
			if (shaderContexts.length <= mi || shaderContexts[mi] == null) continue;
			materialIndex = mi;

			// Check context skip
			if (materials.length > mi && skipContext(context, materials[mi])) continue;

			var scontext = shaderContexts[mi];
			if (scontext == null) continue;
			var elems = scontext.raw.vertex_elements;

			// Uniforms
			if (scontext.pipeState != lastPipeline) {
				g.setPipeline(scontext.pipeState);
				lastPipeline = scontext.pipeState;
				// Uniforms.setContextConstants(g, scontext, bindParams);
			}
			Uniforms.setContextConstants(g, scontext, bindParams); //
			Uniforms.setObjectConstants(g, scontext, this);
			if (materialContexts.length > mi) {
				Uniforms.setMaterialConstants(g, scontext, materialContexts[mi]);
			}

			// VB / IB
			#if arm_deinterleaved
			g.setVertexBuffers(ldata.geom.get(elems));
			#else
			if (ldata.geom.instancedVB != null) {
				g.setVertexBuffers([ldata.geom.get(elems), ldata.geom.instancedVB]);
			}
			else {
				g.setVertexBuffer(ldata.geom.get(elems));
			}
			#end

			g.setIndexBuffer(ldata.geom.indexBuffers[i]);

			// Draw
			if (ldata.geom.instanced) {
				g.drawIndexedVerticesInstanced(ldata.geom.instanceCount, ldata.geom.start, ldata.geom.count);
			}
			else {
				g.drawIndexedVertices(ldata.geom.start, ldata.geom.count);
			}
		}

		#if arm_debug
		var isShadow = context == "shadowmap";
		if (meshContext) RenderPath.numTrisMesh += ldata.geom.numTris;
		else if (isShadow) RenderPath.numTrisShadow += ldata.geom.numTris;
		RenderPath.drawCalls++;
		#end

		#if arm_veloc
		prevMatrix.setFrom(transform.worldUnpack);
		#end
	}

	function validContext(mats: Vector<MaterialData>, context: String): Bool {
		for (mat in mats) if (mat.getContext(context) != null) return true;
		return false;
	}

	public inline function computeCameraDistance(camX: Float, camY: Float, camZ: Float) {
		// Render path mesh sorting
		cameraDistance = Vec4.distancef(camX, camY, camZ, transform.worldx(), transform.worldy(), transform.worldz());
	}

	public inline function computeDepthRead() {
		#if rp_depth_texture
		depthRead = false;
		for (material in materials) {
			for (context in material.contexts) {
				if (context.raw.depth_read == true) {
					depthRead = true;
					break;
				}
			}
		}
		#end
	}

	public inline function computeScreenSize(camera: CameraObject) {
		// Approx..
		// var rp = camera.renderPath;
		// var screenVolume = rp.currentW * rp.currentH;
		var tr = transform;
		var volume = tr.dim.x * tr.dim.y * tr.dim.z;
		screenSize = volume * (1.0 / cameraDistance);
		screenSize = screenSize > 1.0 ? 1.0 : screenSize;
	}

	inline function initLods() {
		if (lods == null) {
			lods = [];
			for (l in raw.lods) {
				if (l.object_ref == "") lods.push(null); // Empty
				else lods.push(Scene.active.getChild(l.object_ref));
			}
		}
	}

	function renderNextPass(g: Graphics, context: String, bindParams: Array<String>, lod: MeshObject) {
		var ldata = lod.data;
		for (i in 0...ldata.geom.indexBuffers.length) {
			var mi = ldata.geom.materialIndices[i];
			if (mi >= materials.length) continue;

			var currentMaterial: MaterialData = materials[mi];
			if (currentMaterial == null || currentMaterial.shader == null) continue;

			var nextPassName: String = currentMaterial.shader.nextPass;
			if (nextPassName == null || nextPassName == "") continue;

			var nextMaterial: MaterialData = null;
			for (mat in materials) {
				// First try exact match
				if (mat.name == nextPassName) {
					nextMaterial = mat;
					break;
				}
				// If no exact match, try to match base name for linked materials
				if (mat.name.indexOf("_") > 0 && mat.name.substr(mat.name.length - 6) == ".blend") {
					var baseName = mat.name.substring(0, mat.name.indexOf("_"));
					if (baseName == nextPassName) {
						nextMaterial = mat;
						break;
					}
				}
			}

			if (nextMaterial == null) continue;

			var nextMaterialContext: MaterialContext = null;
			var nextShaderContext: ShaderContext = null;

			for (j in 0...nextMaterial.raw.contexts.length) {
				if (nextMaterial.raw.contexts[j].name.substr(0, context.length) == context) {
					nextMaterialContext = nextMaterial.contexts[j];
					nextShaderContext = nextMaterial.shader.getContext(context);
					break;
				}
			}

			if (nextShaderContext == null) continue;
			if (skipContext(context, nextMaterial)) continue;

			var elems = nextShaderContext.raw.vertex_elements;

			// Uniforms
			if (nextShaderContext.pipeState != lastPipeline) {
				g.setPipeline(nextShaderContext.pipeState);
				lastPipeline = nextShaderContext.pipeState;
			}
			Uniforms.setContextConstants(g, nextShaderContext, bindParams);
			Uniforms.setObjectConstants(g, nextShaderContext, this);
			Uniforms.setMaterialConstants(g, nextShaderContext, nextMaterialContext);

			// VB / IB
			#if arm_deinterleaved
			g.setVertexBuffers(ldata.geom.get(elems));
			#else
			if (ldata.geom.instancedVB != null) {
				g.setVertexBuffers([ldata.geom.get(elems), ldata.geom.instancedVB]);
			}
			else {
				g.setVertexBuffer(ldata.geom.get(elems));
			}
			#end

			g.setIndexBuffer(ldata.geom.indexBuffers[i]);

			// Draw next pass for this specific geometry section
			if (ldata.geom.instanced) {
				g.drawIndexedVerticesInstanced(ldata.geom.instanceCount, ldata.geom.start, ldata.geom.count);
			}
			else {
				g.drawIndexedVertices(ldata.geom.start, ldata.geom.count);
			}
		}
	}
}
