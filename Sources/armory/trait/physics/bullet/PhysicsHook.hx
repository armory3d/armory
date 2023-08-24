package armory.trait.physics.bullet;

#if arm_bullet

import iron.math.Vec4;
import iron.math.Mat4;
import iron.math.Quat;
import iron.Trait;
import iron.object.Object;
import iron.object.MeshObject;
import iron.object.Transform;
import iron.data.MeshData;
import iron.data.SceneFormat;
import armory.trait.physics.RigidBody;
import armory.trait.physics.PhysicsWorld;

class PhysicsHook extends Trait {

	var target: Object;
	var targetName: String;
	var targetTransform: Transform;
	var verts: Array<Float>;

	var constraint: bullet.Bt.Generic6DofConstraint = null;

	#if arm_physics_soft
	var hookRB: bullet.Bt.RigidBody = null;
	#end

	static var nullvec = true;
	static var vec1: bullet.Bt.Vector3;
	static var quat1: bullet.Bt.Quaternion;
	static var trans1: bullet.Bt.Transform;
	static var trans2: bullet.Bt.Transform;
	static var quat = new Quat();

	public function new(targetName: String, verts: Array<Float>) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Bt.Vector3(0, 0, 0);
			quat1 = new bullet.Bt.Quaternion(0, 0, 0, 0);
			trans1 = new bullet.Bt.Transform();
			trans2 = new bullet.Bt.Transform();
		}

		this.targetName = targetName;
		this.verts = verts;

		iron.Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
			notifyOnUpdate(update);
		});
	}

	function init() {
		// Hook to empty axes
		target = targetName != "" ? iron.Scene.active.getChild(targetName) : null;
		targetTransform = target != null ? target.transform : object.transform;

		var physics = PhysicsWorld.active;

		// Soft body hook
	#if arm_physics_soft
		var sb: SoftBody = object.getTrait(SoftBody);
		if (sb != null && sb.ready) {

			// Place static rigid body at target location
			trans1.setIdentity();
			vec1.setX(targetTransform.loc.x);
			vec1.setY(targetTransform.loc.y);
			vec1.setZ(targetTransform.loc.z);
			trans1.setOrigin(vec1);
			quat1.setX(targetTransform.rot.x);
			quat1.setY(targetTransform.rot.y);
			quat1.setZ(targetTransform.rot.z);
			quat1.setW(targetTransform.rot.w);
			trans1.setRotation(quat1);
			var centerOfMassOffset = trans2;
			centerOfMassOffset.setIdentity();
			var mass = 0.0;
			var motionState = new bullet.Bt.DefaultMotionState(trans1, centerOfMassOffset);
			var inertia = vec1;
			inertia.setX(0);
			inertia.setY(0);
			inertia.setZ(0);
			var shape = new bullet.Bt.SphereShape(0.01);
			shape.calculateLocalInertia(mass, inertia);
			var bodyCI = new bullet.Bt.RigidBodyConstructionInfo(mass, motionState, shape, inertia);
			hookRB = new bullet.Bt.RigidBody(bodyCI);

			#if js
			var nodes = sb.body.get_m_nodes();
			#else
			var nodes = sb.body.m_nodes;
			#end

			for (i in 0...nodes.size()) {
				var node = nodes.at(i);
				#if js
				var nodePos = node.get_m_x();
				#else
				var nodePos = node.m_x;
				#end

				// Find nodes at marked vertex group locations
				var numVerts = Std.int(verts.length / 3);
				for (j in 0...numVerts) {
					var x = verts[j * 3] + sb.vertOffsetX;
					var y = verts[j * 3 + 1] + sb.vertOffsetY;
					var z = verts[j * 3 + 2] + sb.vertOffsetZ;

					// Anchor node to rigid body
					if (Math.abs(nodePos.x() - x) < 0.01 && Math.abs(nodePos.y() - y) < 0.01 && Math.abs(nodePos.z() - z) < 0.01) {
						sb.body.appendAnchor(i, hookRB, false, 1.0 / numVerts);
					}
				}
			}
			return;
		}
	#end

		// Rigid body hook
		var rb1: RigidBody = object.getTrait(RigidBody);
		if (rb1 != null && rb1.ready) {
			trans1.setIdentity();
			vec1.setX(targetTransform.worldx() - object.transform.worldx());
			vec1.setY(targetTransform.worldy() - object.transform.worldy());
			vec1.setZ(targetTransform.worldz() - object.transform.worldz());
			trans1.setOrigin(vec1);
			constraint = new bullet.Bt.Generic6DofConstraint(rb1.body, trans1, false);
			vec1.setX(0);
			vec1.setY(0);
			vec1.setZ(0);
			constraint.setLinearLowerLimit(vec1);
			constraint.setLinearUpperLimit(vec1);
			vec1.setX(-10);
			vec1.setY(-10);
			vec1.setZ(-10);
			constraint.setAngularLowerLimit(vec1);
			vec1.setX(10);
			vec1.setY(10);
			vec1.setZ(10);
			constraint.setAngularUpperLimit(vec1);
			physics.world.addConstraint(constraint, false);
			return;
		}

		// Rigid body or soft body not initialized yet
		notifyOnInit(init);
	}

	function update() {
		#if arm_physics_soft
		if (hookRB != null) {
			trans1.setIdentity();
			vec1.setX(targetTransform.world.getLoc().x);
			vec1.setY(targetTransform.world.getLoc().y);
			vec1.setZ(targetTransform.world.getLoc().z);
			trans1.setOrigin(vec1);
			quat.fromMat(targetTransform.world);
			quat1.setX(quat.x);
			quat1.setY(quat.y);
			quat1.setZ(quat.z);
			quat1.setW(quat.w);
			trans1.setRotation(quat1);
			hookRB.setWorldTransform(trans1);
		}
		#end

		// if (constraint != null) {
		// 	vec1.setX(targetTransform.worldx() - object.transform.worldx());
		// 	vec1.setY(targetTransform.worldy() - object.transform.worldy());
		// 	vec1.setZ(targetTransform.worldz() - object.transform.worldz());
		// 	var pivot = vec1;
		// 	#if js
		// 	constraint.getFrameOffsetA().setOrigin(pivot);
		// 	#elseif cpp
		// 	constraint.setFrameOffsetAOrigin(pivot);
		// 	#end
		// }
	}

}

#end
