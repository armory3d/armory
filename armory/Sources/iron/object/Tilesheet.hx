package iron.object;

import iron.data.Data;
import iron.data.SceneFormat;
import iron.system.Time;
import iron.Scene;

using StringTools;

class Tilesheet {

	public var tileX = 0.0; // Tile offset on tilesheet texture 0-1
	public var tileY = 0.0;
	public var flipX = false;
	public var flipY = false;

	public var actions: Array<TTilesheetAction>;
	public var action: TTilesheetAction = null;
	var ready: Bool = false;

	public var paused = false;
	public var frame = 0;
	var time = 0.0;
	var onActionComplete: Void->Void = null;
	var owner: MeshObject = null;
	var currentMesh: MeshObject = null; // Currently active mesh (from children)
	var meshCache: Map<String, MeshObject> = new Map(); // Cache of child meshes by name

	var pendingAction: String = null; // Action to play once ready
	var pendingOnComplete: Void->Void = null;
	var hasMeshActions: Bool = false; // Whether any action requires mesh swapping

	/**
	 * Create a tilesheet from embedded object tilesheet data.
	 * @param tilesheetData The tilesheet data embedded in the object
	 * @param ownerObject The MeshObject that owns this tilesheet
	 */
	public function new(tilesheetData: TTilesheetData, ownerObject: MeshObject = null) {
		owner = ownerObject;
		actions = tilesheetData.actions;

		// Check if any actions require mesh swapping
		for (a in actions) {
			if (a.mesh != null && a.mesh != "") {
				hasMeshActions = true;
				break;
			}
		}

		// Store start action
		pendingAction = tilesheetData.start_action;
		if ((pendingAction == null || pendingAction == "") && actions.length > 0) {
			pendingAction = actions[0].name;
		}

		// If no meshes needed, we're ready immediately
		if (!hasMeshActions) {
			ready = true;
			if (pendingAction != null) {
				playAction(pendingAction);
				pendingAction = null;
			}
		}
	}

	/**
	 * Called every frame. Handles initialization and animation.
	 */
	public function update() {
		// Initialization: wait for all required meshes to be available
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

		// Animation update
		if (paused || action == null || action.start >= action.end) return;

		time += Time.renderDelta;

		var frameTime = 1 / action.framerate;
		var framesToAdvance = 0;

		while (time >= frameTime) {
			time -= frameTime;
			framesToAdvance++;
		}

		if (framesToAdvance != 0) {
			setFrame(frame + framesToAdvance);
		}
	}

	/**
	 * Try to cache all required child meshes.
	 * Returns true when all expected meshes are cached.
	 */
	function tryInitialize(): Bool {
		if (owner == null || owner.children == null) return false;

		// Scan children for MeshObjects with loaded data
		for (child in owner.children) {
			if (Std.isOfType(child, MeshObject)) {
				var meshChild = cast(child, MeshObject);
				if (meshChild.data != null) {
					// Cache by mesh data name
					if (!meshCache.exists(meshChild.data.name)) {
						meshCache.set(meshChild.data.name, meshChild);
						trace('Tilesheet: Cached mesh by data name: "${meshChild.data.name}"');
						meshChild.visible = false;
					}
					// Also cache by object name if different from mesh data name
					if (meshChild.name != meshChild.data.name && !meshCache.exists(meshChild.name)) {
						meshCache.set(meshChild.name, meshChild);
						trace('Tilesheet: Also cached by object name: "${meshChild.name}"');
					}
				}
			}
		}

		// Check if all required meshes (from actions) are available
		for (a in actions) {
			if (a.mesh != null && a.mesh != "") {
				if (!meshCache.exists(a.mesh)) {
					// Try to find a mesh with matching prefix (handles linked objects with different suffixes)
					var foundMatch = findMatchingMesh(a.mesh);
					if (foundMatch == null) {
						trace('Tilesheet: Missing mesh for action "${a.name}": looking for "${a.mesh}"');
						return false;
					}
				}
			}
		}
		return true;
	}

	/**
	 * Find a mesh that matches the action name pattern when exact match fails.
	 * This handles linked objects where mesh names have different suffixes.
	 * E.g., action wants "MeshIdle_paulie.blend" but we have "Idle_ruler.blend"
	 */
	function findMatchingMesh(actionMeshName: String): MeshObject {
		// Extract the base action name (e.g., "Idle" from "MeshIdle_paulie.blend" or "Idle_paulie.blend")
		var baseName = actionMeshName;

		// Remove common prefixes
		if (StringTools.startsWith(baseName, "Mesh")) {
			baseName = baseName.substr(4);
		}

		// Remove suffix after underscore (e.g., "_paulie.blend")
		var underscoreIdx = baseName.indexOf("_");
		if (underscoreIdx > 0) {
			baseName = baseName.substr(0, underscoreIdx);
		}

		trace('Tilesheet: Looking for mesh matching base name: "$baseName"');

		// Find a cached mesh that contains the base name
		for (meshName in meshCache.keys()) {
			if (StringTools.contains(meshName, baseName)) {
				var mesh = meshCache.get(meshName);
				// Also add this as an alias for future lookups
				meshCache.set(actionMeshName, mesh);
				trace('Tilesheet: Found match "$meshName" for "$actionMeshName"');
				return mesh;
			}
		}

		return null;
	}

	/**
	 * Play a tilesheet action by name.
	 */
	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		if (actions == null) return;

		if (!ready) {
			// Queue action until ready
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

		this.onActionComplete = onComplete;

		// Find the action
		for (a in actions) {
			if (a.name == action_ref) {
				action = a;
				break;
			}
		}

		if (action == null) return;

		// Handle mesh swap
		if (action.mesh != null && action.mesh != "" && owner != null) {
			var targetMesh = meshCache.get(action.mesh);
			if (targetMesh != null && targetMesh != currentMesh) {
				swapMesh(targetMesh);
			}
		}

		setFrame(action.start);
		paused = false;
		time = 0.0;
	}

	/**
	 * Swap to a different mesh by copying its geometry and materials to the owner.
	 */
	function swapMesh(meshObj: MeshObject) {
		if (owner == null || meshObj == null) return;

		currentMesh = meshObj;

		if (meshObj.data != null) {
			owner.setData(meshObj.data);
		}

		if (meshObj.materials != null) {
			owner.materials = meshObj.materials;
		}
	}

	function setFrame(f: Int) {
		frame = f;

		if (frame > action.end && action.start < action.end) {
			if (onActionComplete != null) onActionComplete();
			if (action.loop) setFrame(action.start);
			else paused = true;
			return;
		}

		var tx = frame % action.tilesx;
		var ty = Std.int(frame / action.tilesx);
		tileX = tx * (1 / action.tilesx);
		tileY = ty * (1 / action.tilesy);
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
		if (action == null) return 0;
		return frame - action.start;
	}

	public function getTilesx(): Int {
		return action != null ? action.tilesx : 1;
	}

	public function getTilesy(): Int {
		return action != null ? action.tilesy : 1;
	}
}
