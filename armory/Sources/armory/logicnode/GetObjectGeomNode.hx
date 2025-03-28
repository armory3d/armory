package armory.logicnode;

import iron.object.MeshObject;
import iron.math.Vec4;

class GetObjectGeomNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: MeshObject = inputs[0].get();

		if (object == null) return null;

		if (from == 5)
			return object.vertex_groups;

		if (from == 6){
			var keys = [];
			if (object.vertex_groups != null)
				for (key in object.vertex_groups.keys())
					keys.push(key);

			return keys;
		}

		if (object.data == null) return null;

		var pos: Array<Vec4> = [];
		var nor: Array<Vec4> = [];

		var positions = object.data.geom.positions.values;
		var scl = object.data.scalePos;
		var normals = object.data.geom.normals.values;

		for (i in 0...Std.int(positions.length/4)){
			pos.push(new Vec4(positions[i*4]*scl/32767, positions[i*4+1]*scl/32767, positions[i*4+2]*scl/32767, 1));
			nor.push(new Vec4(normals[i*2]/32767, normals[i*2+1]/32767, positions[i*4+3]/32767, 1));
		}

		if (from == 0)
			return pos;

		if (from == 1)
			return nor;


		if (from == 2){
			var index = [];
			for (i in 0...pos.length)
				index.push(i);
			
			var unique: Array<Dynamic> = [];
			
			for (item in pos)
				if (unique.indexOf(Std.string(item)) == -1)
					unique.push(Std.string(item));

			for (u in 0...unique.length)
				for (i in 0...pos.length)
					if(Std.string(pos[i]) == unique[u]) index[i] = u;  

			return index;
		}

		var ind: Array<Int> = [];

		if (from == 3 || from == 4){
			var matInd: Array<Int> = [];
			
			var indices = object.data.geom.indices;

			for (i in 0...indices.length){
				for(j in 0...Std.int(indices[i].length))
					matInd.push(i);
				for (j in 0...indices[i].length)
					ind.push(indices[i][j]);
			}
			
			var matIndex = [];
			for (i in 0...pos.length)
				matIndex.push(matInd[ind.indexOf(i)]);

			if (from == 3)
				return matIndex;
		}


		if (from == 4){
			var face = 0;
			var faceIndex = [];

			for(i in 0...Std.int(ind.length/3)-1){
				var ar = ind.slice(i*3, i*3+3).concat(ind.slice((i+1)*3, (i+1)*3+3));
				var unique = [];
				for (item in ar)
					if (unique.indexOf(item) == -1)
						unique.push(item);
				faceIndex.push(face);
				if (unique.length == ar.length)
					face+=1;			
			}
			faceIndex.push(face);

			var faceIndexF = [];
			for (f in faceIndex)
				for (i in 0...3) 
					faceIndexF.push(f);

			var faceInd = [];
			for (i in 0...pos.length)
				faceInd.push(faceIndexF[ind.indexOf(i)]);

			return faceInd;
		}

		return null;
		
	}
}