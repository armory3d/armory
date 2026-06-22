package iron.data;

#if arm_batch

import kha.arrays.ByteArray;
import kha.graphics4.VertexBuffer;
import kha.graphics4.IndexBuffer;
import kha.graphics4.Usage;
import kha.graphics4.VertexStructure;
import kha.graphics4.Graphics;
import iron.object.MeshObject;
import iron.object.Uniforms;
import iron.data.Geometry;
import iron.data.MaterialData;
import iron.data.ShaderData;
import iron.data.SceneFormat;

@:access(iron.object.MeshObject)
class MeshBatch {

	var buckets: Map<ShaderData, Bucket> = new Map();
	public var nonBatched: Array<MeshObject> = [];

	public function new() {}

	public function remove() {
		for (b in buckets) b.remove();
	}

	public static function isBatchable(m: MeshObject): Bool {
		m.computeDepthRead();
		var batch =
			m.materials != null &&
			m.materials.length == 1 &&
			!m.data.geom.instanced &&
			!m.data.isSkinned &&
			m.data.raw.morph_target == null &&
			!m.depthRead;
		return batch;
	}

	public function addMesh(m: MeshObject, isLod: Bool): Bool {
		// No instancing, multimat, skinning, morph targets or lod batching
		if (!isBatchable(m) || isLod) {
			nonBatched.push(m);
			return false;
		}

		var shader = m.materials[0].shader;
		var b = buckets.get(shader);
		if (b == null) {
			b = new Bucket(shader);
			buckets.set(shader, b);
		}
		b.addMesh(m);
		return true;
	}

	public function removeMesh(m: MeshObject) {
		var shader = m.materials[0].shader;
		var b = buckets.get(shader);
		if (b != null) b.removeMesh(m);
		else nonBatched.remove(m);
	}

	@:access(iron.RenderPath)
	public function render(g: Graphics, context: String, bindParams: Array<String>) {

		for (b in buckets) {
			if (!b.batched) b.batch();
			if (b.meshes.length > 0 && b.meshes[0].cullMaterial(context)) continue;

			var scontext = b.shader.getContext(context);
			g.setPipeline(scontext.pipeState);
			// #if arm_deinterleaved // TODO
			// g.setVertexBuffers(b.vertexBuffers);
			// #else
			g.setVertexBuffer(b.getVertexBuffer(scontext.raw.vertex_elements));
			// #end
			g.setIndexBuffer(b.indexBuffer);

			Uniforms.setContextConstants(g, scontext, bindParams);

			RenderPath.sortMeshesDistance(b.meshes);

			for (m in b.meshes) {
				if (!m.visible) continue; // Skip render if object is hidden
				if (m.cullMesh(context, Scene.active.camera, RenderPath.active.light)) continue;

				// Get context
				var materialContexts: Array<MaterialContext> = [];
				var shaderContexts: Array<ShaderContext> = [];
				m.getContexts(context, m.materials, materialContexts, shaderContexts);

				Uniforms.posUnpack = m.data.scalePos;
				Uniforms.texUnpack = m.data.scaleTex;
				m.transform.update();

				// Render mesh
				Uniforms.setObjectConstants(g, scontext, m);
				Uniforms.setMaterialConstants(g, scontext, materialContexts[0]);

				g.drawIndexedVertices(m.data.start, m.data.count);

				#if arm_veloc
				m.prevMatrix.setFrom(m.transform.worldUnpack);
				#end

				#if arm_debug
				RenderPath.drawCalls++;
				RenderPath.batchCalls++;
				#end
			}

			#if arm_debug
			RenderPath.batchBuckets++;
			#end
		}

		// Render non-batched meshes
		inline RenderPath.meshRenderLoop(g, context, bindParams, nonBatched);
	}
}

class Bucket {

	public var batched = false;
	public var shader: ShaderData;
	var vertexBuffer: VertexBuffer;
	var vertexBufferMap: Map<String, VertexBuffer> = new Map();
	public var indexBuffer: IndexBuffer;
	public var meshes: Array<MeshObject> = [];

	public function new(shader: ShaderData) {
		this.shader = shader;
	}

	public function remove() {
		indexBuffer.delete();
		// this.vertexBuffer is in the map, so it's also deleted here
		for (buf in vertexBufferMap) buf.delete();
		meshes = [];
	}

	public function addMesh(m: MeshObject) {
		meshes.push(m);
	}

	public function removeMesh(m: MeshObject) {
		meshes.remove(m);
	}

	function copyAttribute(attribSize: Int, count: Int, to: ByteArray, toStride: Int, toOffset: Int, from: ByteArray, fromStride: Int, fromOffset: Int) {
		for (i in 0...count) {
			for (j in 0...attribSize) {
				to.setInt16((i * toStride + toOffset + j) * 2, from.getInt16((i * fromStride + fromOffset + j) * 2));
			}
		}
	}

	function extractVertexBuffer(elems: Array<TVertexElement>): VertexBuffer {
		// Build vertex buffer for specific context
		var vs = new VertexStructure();
		for (e in elems) vs.add(e.name, ShaderContext.parseData(e.data));

		var vb = new VertexBuffer(vertexBuffer.count(), vs, Usage.StaticUsage);
		var to = vb.lock();
		var from = vertexBuffer.lock();

		var toOffset = 0;
		var toStride = Std.int(vb.stride() / 2);
		var fromOffset = 0;
		var fromStride = Std.int(vertexBuffer.stride() / 2);

		for (e in elems) {
			var size = 0;
			if (e.name == "pos") { size = 4; fromOffset = 0; }
			else if (e.name == "nor") { size = 2; fromOffset = 4; }
			else if (e.name == "tex") { size = 2; fromOffset = 6; }
			copyAttribute(size, vertexBuffer.count(), to, toStride, toOffset, from, fromStride, fromOffset);
			toOffset += size;
		}

		vb.unlock();
		return vb;
	}

	public function getVertexBuffer(elems: Array<TVertexElement>): VertexBuffer {
		var s = "";
		for (e in elems) s += e.name;
		var vb = vertexBufferMap.get(s);
		if (vb == null) {
			vb = extractVertexBuffer(elems);
			vertexBufferMap.set(s, vb);
		}
		return vb;
	}

	function vertexCount(g: Geometry, hasUVs: Bool): Int {
		var vcount = g.getVerticesLength();
		if (hasUVs && g.uvs == null) {
			vcount += Std.int(g.positions.values.length / 4) * 2;
		}
		return vcount;
	}

	public function batch() {
		batched = true;

		// Ensure same vertex structure for batched meshes
		var hasUVs = false;
		for (m in meshes) {
			if (m.data.geom.uvs != null) {
				hasUVs = true;
				break;
			}
		}

		// Unique mesh datas
		var vcount = 0;
		var icount = 0;
		var mdatas: Array<MeshData> = [];
		for (m in meshes) {
			var mdFound = false;
			for (md in mdatas) {
				if (m.data == md) {
					mdFound = true;
					break;
				}
			}
			if (!mdFound) {
				mdatas.push(m.data);
				m.data.start = icount;
				m.data.count = m.data.geom.indices[0].length;
				icount += m.data.count;
				vcount += vertexCount(m.data.geom, hasUVs);
			}
		}

		if (mdatas.length == 0) return;

		// Pick UVs if present
		var vs = mdatas[0].geom.struct;
		for (md in mdatas) if (md.geom.struct.size() > vs.size()) vs = md.geom.struct;

		// Build shared buffers
		vertexBuffer = new VertexBuffer(vcount, vs, Usage.StaticUsage);
		var vertices = vertexBuffer.lock();
		var offset = 0;
		for (md in mdatas) {
			md.geom.copyVertices(vertices, offset, hasUVs);
			offset += vertexCount(md.geom, hasUVs);
		}
		vertexBuffer.unlock();

		var s = "";
		for (e in vs.elements) s += e.name;
		vertexBufferMap.set(s, vertexBuffer);

		indexBuffer = new IndexBuffer(icount, Usage.StaticUsage);
		var indices = indexBuffer.lock();
		var di = -1;
		var offset = 0;
		for (md in mdatas) {
			for (i in 0...md.geom.indices[0].length) {
				indices[++di] = md.geom.indices[0][i] + offset;
			}
			offset += Std.int(md.geom.getVerticesLength() / md.geom.structLength);
		}
		indexBuffer.unlock();
	}
}

#end
