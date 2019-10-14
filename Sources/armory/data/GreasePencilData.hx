package armory.data;

import kha.graphics4.VertexBuffer;
import kha.graphics4.IndexBuffer;
import kha.graphics4.Usage;
import kha.graphics4.VertexStructure;
import kha.graphics4.VertexData;
import kha.graphics4.PipelineState;
import kha.graphics4.CompareMode;
import kha.graphics4.CullMode;
import kha.graphics4.ConstantLocation;
import iron.math.Vec4;
import iron.object.Transform;
import iron.data.SceneFormat;
import iron.data.ShaderData;
import iron.data.ShaderData.ShaderContext;

class GreasePencilData extends Data {

	public var name:String;
	public var raw:TGreasePencilData;
	public var layers:Array<GreasePencilLayer>;

	public static var shaderData:ShaderData = null;
	public static var structure:VertexStructure = null;
	public static var usage:Usage;
	public static var frameEnd = 0;
	static var first = true;

	public function new(raw:TGreasePencilData, done:GreasePencilData->Void) {
		super();

		this.raw = raw;
		this.name = raw.name;

		if (structure == null) {
			structure = new VertexStructure();
			structure.add("pos", VertexData.Float3);
			structure.add("col", VertexData.Float4);
			usage = Usage.StaticUsage;
		}

		if (first) {
			first = false;
			var shaderName:Array<String> = raw.shader.split("/");
			Data.getShader(shaderName[0], shaderName[1], null, function(b:ShaderData) {
				shaderData = b;
				makeLayers(done);
			});
		}
		else makeLayers(done);
	}

	function makeLayers(done:GreasePencilData->Void) {
		layers = [];
		for (l in raw.layers) {
			layers.push(new GreasePencilLayer(l));
		}
		done(this);
	}

	public static function parse(name:String, id:String, done:GreasePencilData->Void) {
		Data.getSceneRaw(name, function(format:TSceneFormat) {
			var raw:TGreasePencilData = Data.getGreasePencilRawByName(format.grease_pencil_datas, id);
			if (raw == null) {
				trace('Grease pencil data "$id" not found!');
				done(null);
			}
			new GreasePencilData(raw, done);
		});
	}

	public static function getContext(name:String):ShaderContext {
		return shaderData.getContext(name);
	}
}

class GreasePencilLayer {
	public var name:String;
	public var frames:Array<GreasePencilFrame>;
	public var currentFrame = 0;

	public function new(l:TGreasePencilLayer) {
		name = l.name;
		frames = [];
		for (f in l.frames) {
			frames.push(new GreasePencilFrame(f));
		}
	}
}

class GreasePencilFrame {
	public var vertexBuffer:VertexBuffer;
	public var vertexStrokeBuffer:VertexBuffer;
	public var indexBuffer:IndexBuffer;
	public var raw:TGreasePencilFrame;
	public var numVertices:Int;

	public function new(f:TGreasePencilFrame) {
		raw = f;
		var va = f.vertex_array.values;
		var cola = f.col_array.values;
		var colfilla = f.colfill_array.values;
		var indices = f.index_array.values;

		numVertices = Std.int(va.length / 3);

		// Fill
		vertexBuffer = new VertexBuffer(numVertices, GreasePencilData.structure, GreasePencilData.usage);
		var vertices = vertexBuffer.lock();
		var di = -1;
		for (i in 0...numVertices) {
			vertices.set(++di, va[i * 3]); // Positions
			vertices.set(++di, va[i * 3 + 1]);
			vertices.set(++di, va[i * 3 + 2]);
			vertices.set(++di, colfilla[i * 4]); // Fill color
			vertices.set(++di, colfilla[i * 4 + 1]);
			vertices.set(++di, colfilla[i * 4 + 2]);
			vertices.set(++di, colfilla[i * 4 + 3]);
		}
		vertexBuffer.unlock();

		indexBuffer = new IndexBuffer(indices.length, GreasePencilData.usage);
		var indicesA = indexBuffer.lock();
		for (i in 0...indicesA.length) indicesA[i] = indices[i];
		indexBuffer.unlock();

		// Stroke
		vertexStrokeBuffer = new VertexBuffer(numVertices, GreasePencilData.structure, GreasePencilData.usage);
		vertices = vertexStrokeBuffer.lock();
		di = -1;
		for (i in 0...numVertices) {
			vertices.set(++di, va[i * 3]); // Positions
			vertices.set(++di, va[i * 3 + 1]);
			vertices.set(++di, va[i * 3 + 2]);
			vertices.set(++di, cola[i * 4]); // Stroke color
			vertices.set(++di, cola[i * 4 + 1]);
			vertices.set(++di, cola[i * 4 + 2]);
			vertices.set(++di, cola[i * 4 + 3]);
		}
		vertexStrokeBuffer.unlock();

		// Store max frame number of all layers
		if (GreasePencilData.frameEnd < raw.frame_number) {
			GreasePencilData.frameEnd = raw.frame_number;
		}
	}

	public function delete() {
		vertexBuffer.delete();
	}
}

typedef TGreasePencilFormat = {
	@:optional var grease_pencil_datas:Array<TGreasePencilData>;
	@:optional var grease_pencil_ref:String;
}

typedef TGreasePencilData = {
	var name:String;
	var layers:Array<TGreasePencilLayer>;
	var shader:String;
}

typedef TGreasePencilLayer = {
	var name:String;
	var opacity:Float;
	var frames:Array<TGreasePencilFrame>;
}

typedef TGreasePencilFrame = {
	var frame_number:Int;
	var vertex_array:TVertexArray;
	var col_array:TVertexArray;
	var colfill_array:TVertexArray;
	var index_array:TIndexArray;
	var num_stroke_points:Uint32Array;
}
