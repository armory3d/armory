// Msgpack parser with typed arrays
// Based on https://github.com/aaulia/msgpack-haxe
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
package iron.system;

import haxe.io.Bytes;
import haxe.io.BytesInput;
import haxe.io.BytesOutput;
import haxe.io.Eof;
import iron.data.SceneFormat;
#if (!macro)
import kha.arrays.Float32Array;
import kha.arrays.Uint32Array;
import kha.arrays.Int16Array;
#end

class ArmPack {

	public static inline function decode<T>(b: Bytes): T {
		var i = new BytesInput(b);
		i.bigEndian = false;
		return read(i);
	}

	static function read(i: BytesInput, key = "", parentKey = ""): Any {
		try {
			var b = i.readByte();
			switch (b) {
				case 0xc0: return null;
				case 0xc2: return false;
				case 0xc3: return true;
				case 0xc4: return i.read(i.readByte());
				case 0xc5: return i.read(i.readUInt16());
				case 0xc6: return i.read(i.readInt32());
				case 0xca: return i.readFloat();
				case 0xcc: return i.readByte();
				case 0xcd: return i.readUInt16();
				case 0xce: return i.readInt32();
				case 0xd0: return i.readInt8();
				case 0xd1: return i.readInt16();
				case 0xd2: return i.readInt32();
				// case 0xd3: return Int64.make(i.readInt32(), i.readInt32());
				case 0xd9: return i.readString(i.readByte());
				case 0xda: return i.readString(i.readUInt16());
				case 0xdb: return i.readString(i.readInt32());
				case 0xdc: return readArray(i, i.readUInt16(), key, parentKey);
				case 0xdd: return readArray(i, i.readInt32(), key, parentKey);
				case 0xde: return readMap(i, i.readUInt16(), key, parentKey);
				case 0xdf: return readMap(i, i.readInt32(), key, parentKey);

				default: {
					if (b < 0x80) return b; // positive fix num
					else if (b < 0x90) return readMap(i, (0xf & b), key, parentKey); // fix map
					else if (b < 0xa0) return readArray(i, (0xf & b), key, parentKey); // fix array
					else if (b < 0xc0) return i.readString(0x1f & b); // fix string
					else if (b > 0xdf) return 0xffffff00 | b; // negative fix num
				}
			}
		}
		catch (e: Eof) {}
		return null;
	}

	static function readArray(i: BytesInput, length: Int, key = "", parentKey = ""): Any {
		var b = i.readByte();
		i.position--;

		if (b == 0xca) { // Typed float32
			i.position++;
			var a = new Float32Array(length);
			for (x in 0...length) a[x] = i.readFloat();
			return a;
		}
		else if (b == 0xd2) { // Typed int32
			i.position++;
			var a = new Uint32Array(length);
			for (x in 0...length) a[x] = i.readInt32();
			return a;
		}
		else if (b == 0xd1) { // Typed int16
			i.position++;
			var a = new Int16Array(length);
			for (x in 0...length) a[x] = i.readInt16();
			return a;
		}
		else { // Dynamic type-value
			var a: Array<Dynamic> = [];
			for (x in 0...length) a.push(read(i, key, parentKey));
			return a;
		}
	}

	static function readMap(i: BytesInput, length: Int, key = "", parentKey = ""): Any {
		#if js
		var out = {};
		#else
		var out = Type.createEmptyInstance(getClass(key, parentKey));
		#end
		for (n in 0...length) {
			var k = Std.string(read(i));
			var v = read(i, k, key);
			Reflect.setField(out, k, v);
		}
		return out;
	}

	#if (!js)
	static function getClass(key: String, parentKey: String): Class<Dynamic> {
		return switch (key) {
			case "": TSceneFormat;
			case "mesh_datas": TMeshData;
			case "light_datas": TLightData;
			case "probe_datas": TProbeData;
			case "probe": TProbeData;
			case "camera_datas": TCameraData;
			case "material_datas": TMaterialData;
			case "particle_datas": TParticleData;
			case "shader_datas": TShaderData;
			case "speaker_datas": TSpeakerData;
			case "world_datas": TWorldData;
			case "terrain_datas": TTerrainData;
			case "objects": TObj;
			case "children": TObj;
			case "groups": TGroup;
			case "traits": TTrait;
			case "properties": TProperty;
			case "vertex_arrays": TVertexArray;
			case "index_arrays": TIndexArray;
			case "skin": TSkin;
			case "transform": TTransform;
			case "constraints": TConstraint;
			case "contexts": parentKey == "material_datas" ? TMaterialContext : TShaderContext;
			case "override_context": TShaderOverride;
			case "bind_constants": TBindConstant;
			case "bind_textures": TBindTexture;
			case "vertex_elements": TVertexElement;
			case "constants": TShaderConstant;
			case "texture_units": TTextureUnit;
			case "actions": TTilesheetAction;
			case "particle_refs": TParticleReference;
			case "lods": TLod;
			case "anim": TAnimation;
			case "tracks": TTrack;
			case "morph_target": TMorphTarget;
			case _: TSceneFormat;
		}
	}
	#end

	#if (!macro && armorcore)

	public static inline function encode(d: Dynamic): Bytes {
		var o = new BytesOutput();
		o.bigEndian = false;
		write(o, d);
		return o.getBytes();
	}

	static function write(o: BytesOutput, d: Dynamic) {
		switch (Type.typeof(d)) {
			case TNull: o.writeByte(0xc0);
			case TBool: o.writeByte(d ? 0xc3 : 0xc2);
			case TInt: { o.writeByte(0xd2); o.writeInt32(d); }
			case TFloat: { o.writeByte(0xca); o.writeFloat(d); }
			case TClass(c): {
				switch (Type.getClassName(c)) {
					case "String": {
						o.writeByte(0xdb);
						var b = Bytes.ofString(d);
						o.writeInt32(b.length);
						o.writeFullBytes(b, 0, b.length);
					}
					case "Array", null: { // kha.arrays give null
						o.writeByte(0xdd);
						o.writeInt32(d.length);
						var isInt16 = Std.isOfType(d, #if js js.lib.Int16Array #else Int16ArrayPrivate #end);
						var isInt = Std.isOfType(d[0], Int) && !Std.isOfType(d, #if js js.lib.Float32Array #else Float32ArrayPrivate #end);
						var isFloat = Std.isOfType(d[0], Float);

						if (isInt16) { // Int16Array
							o.writeByte(0xd1);
							for (i in 0...d.length) o.writeInt16(d[i]);
						}
						else if (isFloat && !isInt) { // Float32Array
							o.writeByte(0xca);
							for (i in 0...d.length) o.writeFloat(d[i]);
						}
						else if (isInt) { // Uint32Array
							o.writeByte(0xd2);
							for (i in 0...d.length) o.writeInt32(d[i]);
						}
						else for (i in 0...d.length) write(o, d[i]); // Array
					}
					case "haxe.io.Bytes": {
						o.writeByte(0xc6);
						o.writeInt32(d.length);
						o.writeFullBytes(d, 0, d.length);
					}
					default: writeObject(o, d);
				}
			}
			case TObject: writeObject(o, d);
			default: {}
		}
	}

	static function writeObject(o: BytesOutput, d: Dynamic) {
		var f = Reflect.fields(d);
		o.writeByte(0xdf);
		o.writeInt32(f.length);
		for (k in f) {
			o.writeByte(0xdb);
			var b = Bytes.ofString(k);
			o.writeInt32(b.length);
			o.writeFullBytes(b, 0, b.length);
			write(o, Reflect.field(d, k));
		}
	}

	#end
}
