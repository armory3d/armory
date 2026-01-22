package iron.object;

import iron.App;
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
	var onReady: Void->Void = null;
	var onEvent: String->Void = null; // Callback for tilesheet events
	var prevFrame: Int = -1; // Track previous frame to detect changes
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

		if (tilesheetData.flipx != null) flipX = tilesheetData.flipx;
		if (tilesheetData.flipy != null) flipY = tilesheetData.flipy;

		// If no actions need mesh swapping, ready immediately
		var hasMeshActions: Bool = false;
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
			if (onReady != null) onReady();
		}
	}

	public function update() {
		if (App.pauseUpdates) return;

		if (!ready) {
			if (tryInitialize()) {
				ready = true;
				if (pendingAction != null) {
					playAction(pendingAction, pendingOnComplete);
					pendingAction = null;
					pendingOnComplete = null;
				}
				if (onReady != null) onReady();
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
		if (owner == null) return false;

		// If no children, use the owner mesh itself
		if (owner.children == null || owner.children.length == 0) {
			if (owner.data != null && !meshCache.exists(owner.data.name)) {
				meshCache.set(owner.data.name, owner);
				// Also cache by object name for flexible lookup
				if (owner.name != owner.data.name) {
					meshCache.set(owner.name, owner);
				}
			}
		} else {
			// Use child meshes for mesh swapping
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

	public function notifyOnReady(callback: Void->Void) {
		onReady = callback;
		if (ready) onReady();
	}

	public function notifyOnEvent(callback: String->Void) {
		onEvent = callback;
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

		prevFrame = -1; // Reset previous frame for new action
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
			// Check for events on last frame before completing
			checkEvents(prevFrame, action.end);
			if (onActionComplete != null) onActionComplete();
			if (action.loop) {
				prevFrame = -1; // Reset for loop
				setFrame(action.start);
			} else {
				paused = true;
			}
			return;
		}

		// Check for events between previous frame and current frame
		checkEvents(prevFrame, frame);
		prevFrame = frame;

		var tx = frame % action.tilesx;
		var ty = Std.int(frame / action.tilesx);
		tileX = tx / action.tilesx;
		tileY = ty / action.tilesy;
	}

	/** Check and fire events for frames between fromFrame (exclusive) and toFrame (inclusive). */
	function checkEvents(fromFrame: Int, toFrame: Int) {
		if (onEvent == null || action == null || action.events == null) return;

		// Convert to action-relative frame numbers
		var relativeFrom = fromFrame - action.start;
		var relativeTo = toFrame - action.start;

		for (evt in action.events) {
			// Fire event if it falls in the range (fromFrame, toFrame]
			if (evt.frame > relativeFrom && evt.frame <= relativeTo) {
				onEvent(evt.name);
			}
		}
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
		onEvent = null;
		prevFrame = -1;
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

	public function getTilesX(): Int {
		return action != null ? action.tilesx : 1;
	}

	public function getTilesY(): Int {
		return action != null ? action.tilesy : 1;
	}
}
