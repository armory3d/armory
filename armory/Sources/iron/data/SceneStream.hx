package iron.data;

#if arm_stream

import haxe.ds.Vector;
import iron.data.SceneFormat;
import iron.data.MaterialData;
import iron.object.Object;
import iron.object.MeshObject;
import iron.object.CameraObject;
import iron.math.Vec4;

class SceneStream {

	var checkMax = 64; // Objects checked per frame
	var checkPos = 0;
	var loadMax = 8; // Max objects loaded at once
	var loading = 0; // Objects being loaded
	var loadDistance = -1;
	var unloadDistance = -1;
	var sectors: Array<StreamSector>; // 100x100 groups

	public function sceneTotal(): Int {
		return sectors[0].handles.length;
	}

	public function new() {
		sectors = [new StreamSector()];
	}

	public function remove() {}

	public function add(object_file: String, data_ref: String, sceneName: String, armature: Armature, materials: Vector<MaterialData>, parent: Object, parentObject:TObj, obj: TObj) {
		sectors[0].handles.push({ object_file: object_file, data_ref: data_ref, sceneName: sceneName, armature: armature, materials: materials, parent: parent, parentObject: parentObject, obj: obj, object: null, loading: false });
	}

	function setup(camera: CameraObject) {
		loadDistance = Std.int(camera.data.raw.far_plane * 1.1);
		unloadDistance = Std.int(camera.data.raw.far_plane * 1.5);
	}

	public function update(camera: CameraObject) {
		if (loadDistance == -1) setup(camera);

		if (loading >= loadMax) return; // Busy loading..

		var sec = sectors[0];
		var to = Std.int(Math.min(checkMax, sec.handles.length));
		for (i in 0...to) {

			var h = sec.handles[checkPos];
			checkPos++;
			if (checkPos >= sec.handles.length) checkPos = 0;

			// Check radius in sector
			var camX = camera.transform.worldx();
			var camY = camera.transform.worldy();
			var camZ = camera.transform.worldz();
			var hx = h.obj.transform.values[3];
			var hy = h.obj.transform.values[7];
			var hz = h.obj.transform.values[11];
			var cameraDistance = Vec4.distancef(camX, camY, camZ, hx, hy, hz);
			var dim = h.obj.dimensions;
			if (dim != null) {
				var r = dim[0];
				if (dim[1] > r) r = dim[1];
				if (dim[2] > r) r = dim[2];
				cameraDistance -= r;
				// TODO: handle scale & rot
			}

			if (cameraDistance < loadDistance && h.object == null && !h.loading) { // Load mesh
				// Wait for the parent object to be added to scene
				if (h.parent == null) {
					if (Scene.active.getChild(h.parentObject.name) == null) return;
					h.parent = Scene.active.getChild(h.parentObject.name);
				}

				// Start loading
				h.loading = true;
				loading++;
				iron.Scene.active.returnMeshObject(h.object_file, h.data_ref, h.sceneName, h.armature, h.materials, h.parent, h.parentObject, h.obj, function(object: Object) {
					h.object = cast(object, MeshObject);
					h.loading = false;
					loading--;
				});
				if (loading >= loadMax) return;
			}
			else if (cameraDistance > unloadDistance && h.object != null) { // Unload mesh
				// Remove objects
				h.object.remove();
				if (h.object.data.refcount <= 0) {
					iron.data.Data.deleteMesh(h.object_file + h.data_ref);
				}
				h.object = null;

				// Clear parents
				if (h.parent.name != Scene.active.raw.name) {
					h.parent = null;
				}
			}
		}
	}
}

typedef TMeshHandle = {
	var object_file: String;
	var data_ref: String;
	var sceneName: String;
	var armature: Armature;
	var materials: Vector<MaterialData>;
	var parent: Object;
	var parentObject: TObj;
	var obj: TObj;
	var object: MeshObject;
	var loading: Bool;
}

class StreamSector {
	public function new() {}
	public var handles: Array<TMeshHandle> = []; // Mesh objects
}

#end
