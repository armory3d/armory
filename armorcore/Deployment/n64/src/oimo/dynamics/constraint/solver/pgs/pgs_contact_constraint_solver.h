// pgs_contact_constraint_solver.h
// 1:1 port from OimoPhysics PgsContactConstraintSolver.hx
// Projected Gauss-Seidel (Sequential Impulse) solver
#ifndef OIMO_DYNAMICS_CONSTRAINT_SOLVER_PGS_CONTACT_CONSTRAINT_SOLVER_H
#define OIMO_DYNAMICS_CONSTRAINT_SOLVER_PGS_CONTACT_CONSTRAINT_SOLVER_H

#include "../../../../common/vec3.h"
#include "../../../../common/mat3.h"
#include "../../../../common/setting.h"
#include "../../../../common/math_util.h"
#include "../../../time_step.h"
#include "../../info/jacobian_row.h"
#include "../../info/contact/contact_solver_info.h"
#include "../contact_solver_mass_data_row.h"
#include "../../contact/contact_constraint.h"
#include "../../../rigidbody/rigid_body.h"

typedef struct OimoPgsContactConstraintSolver {
    OimoContactConstraint* constraint;
    OimoContactSolverInfo info;
    OimoContactSolverMassDataRow massData[OIMO_MAX_MANIFOLD_POINTS];
    OimoRigidBody* _b1;
    OimoRigidBody* _b2;
    bool _addedToIsland;
} OimoPgsContactConstraintSolver;

static inline void oimo_pgs_contact_solver_init(OimoPgsContactConstraintSolver* solver, OimoContactConstraint* constraint) {
    solver->constraint = constraint;
    solver->info = oimo_contact_solver_info_create();
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        solver->massData[i] = oimo_contact_solver_mass_data_row_create();
    }
    solver->_b1 = NULL;
    solver->_b2 = NULL;
    solver->_addedToIsland = false;
}

// Pre-solve velocity - compute mass data - 1:1 from PgsContactConstraintSolver.preSolveVelocity
static inline void oimo_pgs_contact_solver_pre_solve_velocity(
    OimoPgsContactConstraintSolver* solver,
    OimoTimeStep* timeStep
) {
    oimo_contact_constraint_get_velocity_solver_info(solver->constraint, timeStep, &solver->info);

    solver->_b1 = solver->info.b1;
    solver->_b2 = solver->info.b2;

    OimoScalar invM1 = solver->_b1->_invMass;
    OimoScalar invM2 = solver->_b2->_invMass;

    OimoMat3 invI1 = solver->_b1->_invInertia;
    OimoMat3 invI2 = solver->_b2->_invInertia;

    // Compute mass data for each row
    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoJacobianRow* j;

        // Normal mass
        j = &row->jacobianN;
        md->invMLinN1 = oimo_vec3_scale(j->lin1, invM1);
        md->invMLinN2 = oimo_vec3_scale(j->lin2, invM2);
        md->invMAngN1 = oimo_mat3_mul_vec3(&invI1, j->ang1);
        md->invMAngN2 = oimo_mat3_mul_vec3(&invI2, j->ang2);

        md->massN = invM1 + invM2 + oimo_vec3_dot(md->invMAngN1, j->ang1) + oimo_vec3_dot(md->invMAngN2, j->ang2);
        if (oimo_abs(md->massN) > OIMO_EPSILON) md->massN = 1.0f / md->massN;

        // Tangent/binormal mass
        OimoJacobianRow* jt = &row->jacobianT;
        OimoJacobianRow* jb = &row->jacobianB;
        md->invMLinT1 = oimo_vec3_scale(jt->lin1, invM1);
        md->invMLinT2 = oimo_vec3_scale(jt->lin2, invM2);
        md->invMLinB1 = oimo_vec3_scale(jb->lin1, invM1);
        md->invMLinB2 = oimo_vec3_scale(jb->lin2, invM2);
        md->invMAngT1 = oimo_mat3_mul_vec3(&invI1, jt->ang1);
        md->invMAngT2 = oimo_mat3_mul_vec3(&invI2, jt->ang2);
        md->invMAngB1 = oimo_mat3_mul_vec3(&invI1, jb->ang1);
        md->invMAngB2 = oimo_mat3_mul_vec3(&invI2, jb->ang2);

        // Compute effective mass matrix for friction
        OimoScalar invMassTB00 = invM1 + invM2 + oimo_vec3_dot(md->invMAngT1, jt->ang1) + oimo_vec3_dot(md->invMAngT2, jt->ang2);
        OimoScalar invMassTB01 = oimo_vec3_dot(md->invMAngT1, jb->ang1) + oimo_vec3_dot(md->invMAngT2, jb->ang2);
        OimoScalar invMassTB10 = invMassTB01;
        OimoScalar invMassTB11 = invM1 + invM2 + oimo_vec3_dot(md->invMAngB1, jb->ang1) + oimo_vec3_dot(md->invMAngB2, jb->ang2);

        OimoScalar invDet = invMassTB00 * invMassTB11 - invMassTB01 * invMassTB10;
        if (oimo_abs(invDet) > OIMO_EPSILON) invDet = 1.0f / invDet;

        md->massTB00 = invMassTB11 * invDet;
        md->massTB01 = -invMassTB01 * invDet;
        md->massTB10 = -invMassTB10 * invDet;
        md->massTB11 = invMassTB00 * invDet;
    }
}

// Warm start - apply accumulated impulses - 1:1 from PgsContactConstraintSolver.warmStart
static inline void oimo_pgs_contact_solver_warm_start(
    OimoPgsContactConstraintSolver* solver,
    OimoTimeStep* timeStep
) {
    OimoVec3 lv1 = solver->_b1->_vel;
    OimoVec3 lv2 = solver->_b2->_vel;
    OimoVec3 av1 = solver->_b1->_angVel;
    OimoVec3 av2 = solver->_b2->_angVel;

    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactImpulse* imp = row->impulse;
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoJacobianRow* jt = &row->jacobianT;
        OimoJacobianRow* jb = &row->jacobianB;

        OimoScalar impulseN = imp->impulseN;
        OimoScalar impulseT = oimo_vec3_dot(imp->impulseL, jt->lin1);
        OimoScalar impulseB = oimo_vec3_dot(imp->impulseL, jb->lin1);
        imp->impulseT = impulseT;
        imp->impulseB = impulseB;

        // Adjust impulse for variable time step
        imp->impulseN *= timeStep->dtRatio;
        imp->impulseT *= timeStep->dtRatio;
        imp->impulseB *= timeStep->dtRatio;

        // Apply impulses
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinN1, impulseN));
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinT1, impulseT));
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinB1, impulseB));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinN2, impulseN));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinT2, impulseT));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinB2, impulseB));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngN1, impulseN));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngT1, impulseT));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngB1, impulseB));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngN2, impulseN));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngT2, impulseT));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngB2, impulseB));
    }

    solver->_b1->_vel = lv1;
    solver->_b2->_vel = lv2;
    solver->_b1->_angVel = av1;
    solver->_b2->_angVel = av2;
}

// Solve velocity constraints - 1:1 from PgsContactConstraintSolver.solveVelocity
static inline void oimo_pgs_contact_solver_solve_velocity(OimoPgsContactConstraintSolver* solver) {
    OimoVec3 lv1 = solver->_b1->_vel;
    OimoVec3 lv2 = solver->_b2->_vel;
    OimoVec3 av1 = solver->_b1->_angVel;
    OimoVec3 av2 = solver->_b2->_angVel;

    // Solve friction first
    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoContactImpulse* imp = row->impulse;
        OimoJacobianRow* j;

        // Measure relative velocity along tangent
        OimoScalar rvt = 0.0f;
        j = &row->jacobianT;
        rvt += oimo_vec3_dot(lv1, j->lin1);
        rvt -= oimo_vec3_dot(lv2, j->lin2);
        rvt += oimo_vec3_dot(av1, j->ang1);
        rvt -= oimo_vec3_dot(av2, j->ang2);

        // Measure relative velocity along binormal
        OimoScalar rvb = 0.0f;
        j = &row->jacobianB;
        rvb += oimo_vec3_dot(lv1, j->lin1);
        rvb -= oimo_vec3_dot(lv2, j->lin2);
        rvb += oimo_vec3_dot(av1, j->ang1);
        rvb -= oimo_vec3_dot(av2, j->ang2);

        OimoScalar impulseT = -(rvt * md->massTB00 + rvb * md->massTB01);
        OimoScalar impulseB = -(rvt * md->massTB10 + rvb * md->massTB11);

        OimoScalar oldImpulseT = imp->impulseT;
        OimoScalar oldImpulseB = imp->impulseB;
        imp->impulseT += impulseT;
        imp->impulseB += impulseB;

        // Cone friction
        OimoScalar maxImpulse = row->friction * imp->impulseN;
        if (oimo_abs(maxImpulse) <= OIMO_EPSILON) {
            imp->impulseT = 0.0f;
            imp->impulseB = 0.0f;
        } else {
            OimoScalar impulseLengthSq = imp->impulseT * imp->impulseT + imp->impulseB * imp->impulseB;
            if (impulseLengthSq > maxImpulse * maxImpulse) {
                OimoScalar invL = maxImpulse / oimo_sqrt(impulseLengthSq);
                imp->impulseT *= invL;
                imp->impulseB *= invL;
            }
        }

        impulseT = imp->impulseT - oldImpulseT;
        impulseB = imp->impulseB - oldImpulseB;

        // Apply delta impulse
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinT1, impulseT));
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinB1, impulseB));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinT2, impulseT));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinB2, impulseB));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngT1, impulseT));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngB1, impulseB));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngT2, impulseT));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngB2, impulseB));
    }

    // Solve normal
    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoContactImpulse* imp = row->impulse;
        OimoJacobianRow* j;

        // Measure relative velocity along normal
        OimoScalar rvn = 0.0f;
        j = &row->jacobianN;
        rvn += oimo_vec3_dot(lv1, j->lin1);
        rvn -= oimo_vec3_dot(lv2, j->lin2);
        rvn += oimo_vec3_dot(av1, j->ang1);
        rvn -= oimo_vec3_dot(av2, j->ang2);

        OimoScalar impulseN = (row->rhs - rvn) * md->massN;

        // Clamp impulse (only pushing, no pulling)
        OimoScalar oldImpulseN = imp->impulseN;
        imp->impulseN += impulseN;
        if (imp->impulseN < 0.0f) imp->impulseN = 0.0f;
        impulseN = imp->impulseN - oldImpulseN;

        // Apply delta impulse
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinN1, impulseN));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinN2, impulseN));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngN1, impulseN));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngN2, impulseN));
    }

    solver->_b1->_vel = lv1;
    solver->_b2->_vel = lv2;
    solver->_b1->_angVel = av1;
    solver->_b2->_angVel = av2;
}

// Update position data for position solver
static inline void oimo_pgs_contact_solver_update_position_data(OimoPgsContactConstraintSolver* solver) {
    oimo_contact_constraint_sync_manifold(solver->constraint);
    oimo_contact_constraint_get_position_solver_info(solver->constraint, &solver->info);

    OimoScalar invM1 = solver->_b1->_invMass;
    OimoScalar invM2 = solver->_b2->_invMass;

    OimoMat3 invI1 = solver->_b1->_invInertia;
    OimoMat3 invI2 = solver->_b2->_invInertia;

    // Compute mass data
    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoJacobianRow* j = &row->jacobianN;

        md->invMLinN1 = oimo_vec3_scale(j->lin1, invM1);
        md->invMLinN2 = oimo_vec3_scale(j->lin2, invM2);
        md->invMAngN1 = oimo_mat3_mul_vec3(&invI1, j->ang1);
        md->invMAngN2 = oimo_mat3_mul_vec3(&invI2, j->ang2);

        md->massN = invM1 + invM2 + oimo_vec3_dot(md->invMAngN1, j->ang1) + oimo_vec3_dot(md->invMAngN2, j->ang2);
        if (oimo_abs(md->massN) > OIMO_EPSILON) md->massN = 1.0f / md->massN;
    }
}

// Pre-solve position
static inline void oimo_pgs_contact_solver_pre_solve_position(
    OimoPgsContactConstraintSolver* solver,
    OimoTimeStep* timeStep
) {
    oimo_pgs_contact_solver_update_position_data(solver);

    // Clear position impulses
    for (int i = 0; i < solver->info.numRows; i++) {
        solver->info.rows[i].impulse->impulseP = 0.0f;
    }
}

// Solve position with split impulse - 1:1 from PgsContactConstraintSolver.solvePositionSplitImpulse
static inline void oimo_pgs_contact_solver_solve_position_split_impulse(OimoPgsContactConstraintSolver* solver) {
    OimoVec3 lv1 = solver->_b1->_pseudoVel;
    OimoVec3 lv2 = solver->_b2->_pseudoVel;
    OimoVec3 av1 = solver->_b1->_angPseudoVel;
    OimoVec3 av2 = solver->_b2->_angPseudoVel;

    // Solve normal
    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoContactImpulse* imp = row->impulse;
        OimoJacobianRow* j = &row->jacobianN;

        // Measure relative velocity
        OimoScalar rvn = 0.0f;
        rvn += oimo_vec3_dot(lv1, j->lin1);
        rvn -= oimo_vec3_dot(lv2, j->lin2);
        rvn += oimo_vec3_dot(av1, j->ang1);
        rvn -= oimo_vec3_dot(av2, j->ang2);

        OimoScalar impulseP = (row->rhs - rvn) * md->massN * OIMO_POSITION_SPLIT_IMPULSE_BAUMGARTE;

        // Clamp impulse
        OimoScalar oldImpulseP = imp->impulseP;
        imp->impulseP += impulseP;
        if (imp->impulseP < 0.0f) imp->impulseP = 0.0f;
        impulseP = imp->impulseP - oldImpulseP;

        // Apply delta impulse
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinN1, impulseP));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinN2, impulseP));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngN1, impulseP));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngN2, impulseP));
    }

    solver->_b1->_pseudoVel = lv1;
    solver->_b2->_pseudoVel = lv2;
    solver->_b1->_angPseudoVel = av1;
    solver->_b2->_angPseudoVel = av2;
}

// Solve position with NGS - 1:1 from PgsContactConstraintSolver.solvePositionNgs
static inline void oimo_pgs_contact_solver_solve_position_ngs(
    OimoPgsContactConstraintSolver* solver,
    OimoTimeStep* timeStep
) {
    oimo_pgs_contact_solver_update_position_data(solver);

    OimoVec3 lv1 = oimo_vec3_zero();
    OimoVec3 lv2 = oimo_vec3_zero();
    OimoVec3 av1 = oimo_vec3_zero();
    OimoVec3 av2 = oimo_vec3_zero();

    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactSolverMassDataRow* md = &solver->massData[i];
        OimoContactImpulse* imp = row->impulse;
        OimoJacobianRow* j = &row->jacobianN;

        // Estimate translation along the normal
        OimoScalar rvn = 0.0f;
        rvn += oimo_vec3_dot(lv1, j->lin1);
        rvn -= oimo_vec3_dot(lv2, j->lin2);
        rvn += oimo_vec3_dot(av1, j->ang1);
        rvn -= oimo_vec3_dot(av2, j->ang2);

        OimoScalar impulseP = (row->rhs - rvn) * md->massN * OIMO_POSITION_NGS_BAUMGARTE;

        // Clamp impulse
        OimoScalar oldImpulseP = imp->impulseP;
        imp->impulseP += impulseP;
        if (imp->impulseP < 0.0f) imp->impulseP = 0.0f;
        impulseP = imp->impulseP - oldImpulseP;

        // Apply delta impulse
        lv1 = oimo_vec3_add(lv1, oimo_vec3_scale(md->invMLinN1, impulseP));
        lv2 = oimo_vec3_sub(lv2, oimo_vec3_scale(md->invMLinN2, impulseP));
        av1 = oimo_vec3_add(av1, oimo_vec3_scale(md->invMAngN1, impulseP));
        av2 = oimo_vec3_sub(av2, oimo_vec3_scale(md->invMAngN2, impulseP));
    }

    oimo_rigid_body_apply_translation(solver->_b1, &lv1);
    oimo_rigid_body_apply_translation(solver->_b2, &lv2);
    oimo_rigid_body_apply_rotation(solver->_b1, &av1);
    oimo_rigid_body_apply_rotation(solver->_b2, &av2);
}

// Post solve - store lateral impulse and accumulate contact impulses
// 1:1 from PgsContactConstraintSolver.postSolve
static inline void oimo_pgs_contact_solver_post_solve(OimoPgsContactConstraintSolver* solver) {
    OimoVec3 lin1 = oimo_vec3_zero();
    OimoVec3 ang1 = oimo_vec3_zero();
    OimoVec3 ang2 = oimo_vec3_zero();

    for (int i = 0; i < solver->info.numRows; i++) {
        OimoContactSolverInfoRow* row = &solver->info.rows[i];
        OimoContactImpulse* imp = row->impulse;
        OimoJacobianRow* jn = &row->jacobianN;
        OimoJacobianRow* jt = &row->jacobianT;
        OimoJacobianRow* jb = &row->jacobianB;
        OimoScalar impN = imp->impulseN;
        OimoScalar impT = imp->impulseT;
        OimoScalar impB = imp->impulseB;

        // Store lateral impulse
        OimoVec3 impulseL = oimo_vec3_zero();
        impulseL = oimo_vec3_add(impulseL, oimo_vec3_scale(jt->lin1, impT));
        impulseL = oimo_vec3_add(impulseL, oimo_vec3_scale(jb->lin1, impB));
        imp->impulseL = impulseL;

        // Accumulate contact impulses
        lin1 = oimo_vec3_add(lin1, oimo_vec3_scale(jn->lin1, impN));
        ang1 = oimo_vec3_add(ang1, oimo_vec3_scale(jn->ang1, impN));
        ang2 = oimo_vec3_add(ang2, oimo_vec3_scale(jn->ang2, impN));
        lin1 = oimo_vec3_add(lin1, oimo_vec3_scale(jt->lin1, impT));
        ang1 = oimo_vec3_add(ang1, oimo_vec3_scale(jt->ang1, impT));
        ang2 = oimo_vec3_add(ang2, oimo_vec3_scale(jt->ang2, impT));
        lin1 = oimo_vec3_add(lin1, oimo_vec3_scale(jb->lin1, impB));
        ang1 = oimo_vec3_add(ang1, oimo_vec3_scale(jb->ang1, impB));
        ang2 = oimo_vec3_add(ang2, oimo_vec3_scale(jb->ang2, impB));
    }

    solver->_b1->_linearContactImpulse = oimo_vec3_add(solver->_b1->_linearContactImpulse, lin1);
    solver->_b1->_angularContactImpulse = oimo_vec3_add(solver->_b1->_angularContactImpulse, ang1);
    solver->_b2->_linearContactImpulse = oimo_vec3_sub(solver->_b2->_linearContactImpulse, lin1);
    solver->_b2->_angularContactImpulse = oimo_vec3_sub(solver->_b2->_angularContactImpulse, ang2);

    oimo_contact_constraint_sync_manifold(solver->constraint);
}

#endif // OIMO_DYNAMICS_CONSTRAINT_SOLVER_PGS_CONTACT_CONSTRAINT_SOLVER_H
