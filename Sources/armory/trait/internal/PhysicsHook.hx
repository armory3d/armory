package armory.trait.internal;

import iron.math.Vec4;
import iron.math.Mat4;
import iron.Trait;
import iron.object.MeshObject;
import iron.data.MeshData;
import iron.data.SceneFormat;
#if arm_physics
import armory.trait.internal.RigidBody;
import armory.trait.internal.PhysicsWorld;
import haxebullet.Bullet;
#end

@:keep
class PhysicsHook extends Trait {
#if (!arm_physics)
	public function new() { super(); }
#else

	var targetName:String;
	var verts:Array<Float>;

	public function new(targetName:String, verts:Array<Float>) {
		super();

		this.targetName = targetName;
		this.verts = verts;

		Scene.active.notifyOnInit(function() {
			notifyOnInit(init);
		});
	}

	function init() {
		
		// Hook to empty axes
		var target = targetName != "" ? iron.Scene.active.getChild(targetName) : null;
		var targetTransform = target != null ? target.transform : object.transform;

		var physics = PhysicsWorld.active;

		// Soft body hook
	#if arm_physics_soft
		var sb:SoftBody = object.getTrait(SoftBody);
		if (sb != null && sb.ready) {

			// Place static rigid body at target location
			var _inertia = BtVector3.create(0, 0, 0);
			var _shape = BtSphereShape.create(0.01);
			var _transform = BtTransform.create();
			_transform.setIdentity();
			// _transform.setOrigin(BtVector3.create(
				// targetTransform.loc.x,
				// targetTransform.loc.y,
				// targetTransform.loc.z));
			// _transform.setRotation(BtQuaternion.create(
				// targetTransform.rot.x,
				// targetTransform.rot.y,
				// targetTransform.rot.z,
				// targetTransform.rot.w));
			var _centerOfMassOffset = BtTransform.create();
			_centerOfMassOffset.setIdentity();
			var _motionState = BtDefaultMotionState.create(_transform, _centerOfMassOffset);
			var mass = 0.0;
			_shape.calculateLocalInertia(mass, _inertia);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia);
			var rb = BtRigidBody.create(_bodyCI);

			#if js
			var nodes = sb.body.get_m_nodes();
			#elseif cpp
			var nodes = sb.body.m_nodes;
			#end

			var mesh = cast(object, MeshObject).data.mesh;
			var numNodes = Std.int(mesh.positions.length / 3);
			for (i in 0...numNodes) {
				var node = nodes.at(i);
				#if js
				var nodePos = node.get_m_x();
				#elseif cpp
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
						sb.body.appendAnchor(i, rb, false, 1.0 / numVerts);
					}
				}
			}
			return;
		}
	#end

		// Rigid body hook
		var rb1:RigidBody = object.getTrait(RigidBody);
		if (rb1 != null && rb1.ready) {
			#if js // TODO
			var btrans = BtTransform.create();
			btrans.setIdentity();
			var dx = targetTransform.absx() - object.transform.absx();
			var dy = targetTransform.absy() - object.transform.absy();
			var dz = targetTransform.absz() - object.transform.absz();
			btrans.setOrigin(BtVector3.create(dx, dy, dz));
			var constraint = BtGeneric6DofConstraint.create(rb1.body, btrans, false); // cpp - fix rb1.body pass
			constraint.setLinearLowerLimit(BtVector3.create(0, 0, 0));
			constraint.setLinearUpperLimit(BtVector3.create(0, 0, 0));
			constraint.setAngularLowerLimit(BtVector3.create(-10, -10, -10));
			constraint.setAngularUpperLimit(BtVector3.create(10, 10, 10));
			physics.world.addConstraint(constraint, false);
			#end
			return;
		}

		// Rigid body or soft body not initialized yet
		notifyOnInit(init);
	}

#end
}
