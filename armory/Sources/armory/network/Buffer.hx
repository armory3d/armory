package armory.network;

import haxe.io.Bytes;

class Buffer {
	public var available(default, null):Int = 0;
	public var length(default, null):Int = 0;
	private var currentOffset:Int = 0;
	private var currentData: Bytes = null;
	private var chunks:Array<Bytes> = [];

	public function new() {}

	public function writeByte(v:Int) {
		var b = Bytes.alloc(1);
		b.set(0, v);
		writeBytes(b);
	}

	public function writeShort(v:Int) {
		var b = Bytes.alloc(2);
		b.set(0, (v >> 8) & 0xFF);
		b.set(1, (v >> 0) & 0xFF);
		writeBytes(b);
	}

	public function writeInt(v:Int) {
		var b = Bytes.alloc(4);
		b.set(0, (v >> 24) & 0xFF);
		b.set(1, (v >> 16) & 0xFF);
		b.set(2, (v >> 8) & 0xFF);
		b.set(3, (v >> 0) & 0xFF);
		writeBytes(b);
	}

	public function writeBytes(data:Bytes) {
		chunks.push(data);
		available += data.length;
		length = available;
	}

	public function readAllAvailableBytes():Bytes {
		return readBytes(available);
	}

	public function readLine():String {
		var bytes = readUntil("\n");
		if (bytes == null) {
			return null;
		}
		return StringTools.trim(bytes.toString());
	}

	public function readLinesUntil(delimiter:String):Array<String> {
		var bytes = readUntil(delimiter);
		if (bytes == null) {
			return null;
		}
		return StringTools.trim(bytes.toString()).split("\n");
	}


	public function readUntil(delimiter:String):Bytes {
		var dl = delimiter.length;

		for (i in 0 ... available - dl) {
			var matched = true;
			for (j in 0 ... dl) {
				if (peekByte(currentOffset + i + j + 1) == delimiter.charCodeAt(j)) {
					continue;
				}
				matched = false;
				break;
			}

			if (matched) {
				var bytes = readBytes(i + dl + 1);
				return bytes;
			}
		}

		return null;
	}

	public function readBytes(count:Int):Bytes {
		var count2 = Std.int(Math.min(count, available));
		var out = Bytes.alloc(count2);
		for (n in 0 ... count2) out.set(n, readByte());
		return out;
	}

	public function readUnsignedShort():UInt {
		var h = readByte();
		var l = readByte();
		return (h << 8) | (l << 0);
	}

	public function readUnsignedInt():UInt {
		var v3 = readByte();
		var v2 = readByte();
		var v1 = readByte();
		var v0 = readByte();
		return (v3 << 24) | (v2 << 16) | (v1 << 8) | (v0 << 0);
	}

	public function readByte():Int {
		if (available <= 0) throw 'No bytes available';
		while (currentData == null || currentOffset >= currentData.length) {
			currentOffset = 0;
			currentData = chunks.shift();
		}
		available--;
		length = available;
		return currentData.get(currentOffset++);
	}

	public function peekByte(offset:Int):Int {
		if (available <= 0) throw 'No bytes available';
		var tempOffset = offset;
		var tempData = chunks[0];
		if (tempData == null) {
			tempData = currentData;
		}
		var chunkIndex = 0;
		while (tempOffset >= tempData.length) {
			tempOffset -= tempData.length;
			chunkIndex++;
			tempData = chunks[chunkIndex];
		}
		return tempData.get(tempOffset);
	}

	public function peekUntil(byte:Int):Int {
		var tempOffset = currentOffset;
		var tempData = chunks[0];
		if (tempData == null) {
			tempData = currentData;
		}
		var chunkIndex = 0;
		while (tempOffset >= tempData.length) {
			tempOffset -= tempData.length;
			chunkIndex++;
			tempData = chunks[chunkIndex];
		}
		while (tempOffset < tempData.length) {
			if (tempData.get(tempOffset) == byte) {
				return tempOffset + 1;
			}
			tempOffset++;
		}

		return -1;
	}

	public function endsWith(e:String):Bool {
		var i = available - e.length;
		var n = currentOffset;

		if (i <= 0) {
			return false;
		}

		while (i < available) {
			if (peekByte(i) != e.charCodeAt(n)) {
				return false;
			}
			i++;
			n++;
		}

		return true;
	}
}
