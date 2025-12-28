package iron.object;

import iron.data.SceneFormat;
import iron.system.Time;

class Tilesheet {
	public var tileX: Float = 0.0;
	public var tileY: Float = 0.0;
	public var flipX: Bool = false;
	public var flipY: Bool = false;
	public var paused: Bool = false;
	public var frame: Int = 0;
	public var actions: Array<TTilesheetAction>;
	public var action: TTilesheetAction = null;

	public var ready: Bool = false;
	var time: Float = 0.0;
	var onActionComplete: Void->Void = null;
	var owner: MeshObject = null;
	var currentMesh: MeshObject = null;
	var meshCache: Map<String, MeshObject> = new Map();
	var pendingAction: String = null;
	var pendingOnComplete: Void->Void = null;

	public function new(tilesheetData: TTilesheetData, ownerObject: MeshObject = null) {
		owner = ownerObject;
		actions = tilesheetData.actions;

		pendingAction = tilesheetData.start_action;
		if ((pendingAction == null || pendingAction == "") && actions.length > 0) {
			pendingAction = actions[0].name;
		}

		// If no actions need mesh swapping, ready immediately
		var hasMeshActions = false;
		for (a in actions) {
			if (a.mesh != null && a.mesh != "") {
				hasMeshActions = true;
				break;
			}
		}

		if (!hasMeshActions) {
			ready = true;
			if (pendingAction != null) {
				playAction(pendingAction);
				pendingAction = null;
			}
		}
	}

	public function update() {
		if (!ready) {
			if (tryInitialize()) {
				ready = true;
				if (pendingAction != null) {
					playAction(pendingAction, pendingOnComplete);
					pendingAction = null;
					pendingOnComplete = null;
				}
			}
			return;
		}

		if (paused || action == null || action.start >= action.end) return;

		time += Time.renderDelta;
		var frameTime = 1 / action.framerate;
		var framesToAdvance = 0;

		while (time >= frameTime) {
			time -= frameTime;
			framesToAdvance++;
		}

		if (framesToAdvance > 0) {
			setFrame(frame + framesToAdvance);
		}
	}

	function tryInitialize(): Bool {
		if (owner == null || owner.children == null) return false;

		for (child in owner.children) {
			if (Std.isOfType(child, MeshObject)) {
				var meshChild = cast(child, MeshObject);
				if (meshChild.data != null && !meshCache.exists(meshChild.data.name)) {
					meshCache.set(meshChild.data.name, meshChild);
					meshChild.visible = false;
					// Also cache by object name for flexible lookup
					if (meshChild.name != meshChild.data.name) {
						meshCache.set(meshChild.name, meshChild);
					}
				}
			}
		}

		for (a in actions) {
			if (a.mesh != null && a.mesh != "" && !meshCache.exists(a.mesh)) {
				if (findMatchingMesh(a.mesh) == null) return false;
			}
		}
		return true;
	}

	/** Find mesh by base name pattern (handles linked objects with different suffixes). */
	function findMatchingMesh(actionMeshName: String): MeshObject {
		var baseName = actionMeshName;

		// Strip "Mesh" prefix if present
		if (StringTools.startsWith(baseName, "Mesh")) {
			baseName = baseName.substr(4);
		}

		// Strip suffix after underscore (e.g., "_character.blend")
		var idx = baseName.indexOf("_");
		if (idx > 0) baseName = baseName.substr(0, idx);

		for (meshName in meshCache.keys()) {
			if (meshName.indexOf(baseName) != -1) {
				var mesh = meshCache.get(meshName);
				meshCache.set(actionMeshName, mesh); // Cache alias
				return mesh;
			}
		}
		return null;
	}

	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		if (actions == null) return;

		if (!ready) {
			pendingAction = action_ref;
			pendingOnComplete = onActionComplete;
			return;
		}

		playAction(action_ref, onActionComplete);
	}

	function playAction(action_ref: String, onComplete: Void->Void = null) {
		if (action != null && action.name == action_ref) {
			paused = false;
			return;
		}

		onActionComplete = onComplete;

		for (a in actions) {
			if (a.name == action_ref) {
				action = a;
				break;
			}
		}

		if (action == null) return;

		if (action.mesh != null && action.mesh != "") {
			var targetMesh = meshCache.get(action.mesh);
			if (targetMesh != null && targetMesh != currentMesh) {
				swapMesh(targetMesh);
			}
		}

		setFrame(action.start);
		paused = false;
		time = 0.0;
	}

	function swapMesh(meshObj: MeshObject) {
		if (owner == null || meshObj == null) return;
		currentMesh = meshObj;
		if (meshObj.data != null) owner.setData(meshObj.data);
		if (meshObj.materials != null) owner.materials = meshObj.materials;
	}

	function setFrame(f: Int) {
		frame = f;

		if (frame > action.end && action.start < action.end) {
			if (onActionComplete != null) onActionComplete();
			if (action.loop)
				setFrame(action.start);
			else
				paused = true;
			return;
		}

		var tx = frame % action.tilesx;
		var ty = Std.int(frame / action.tilesx);
		tileX = tx / action.tilesx;
		tileY = ty / action.tilesy;
	}

	public function pause() {
		paused = true;
	}

	public function resume() {
		paused = false;
	}

	public function remove() {
		ready = false;
		action = null;
		actions = null;
		owner = null;
		currentMesh = null;
		pendingAction = null;
		pendingOnComplete = null;
		meshCache.clear();
	}

	public function setFrameOffset(frame: Int) {
		if (action == null) return;
		setFrame(action.start + frame);
		paused = false;
	}

	public function getFrameOffset(): Int {
		return action != null ? frame - action.start : 0;
	}

	public function getTilesx(): Int {
		return action != null ? action.tilesx : 1;
	}

	public function getTilesy(): Int {
		return action != null ? action.tilesy : 1;
	}
}
