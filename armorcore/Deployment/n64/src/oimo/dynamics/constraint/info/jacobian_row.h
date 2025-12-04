#pragma once

// jacobian_row.h
// 1:1 port from OimoPhysics JacobianRow.hx

#include "../../../common/vec3.h"

typedef struct OimoJacobianRow {
    OimoVec3 lin1;
    OimoVec3 lin2;
    OimoVec3 ang1;
    OimoVec3 ang2;
} OimoJacobianRow;

static inline OimoJacobianRow oimo_jacobian_row_create(void) {
    OimoJacobianRow row;
    row.lin1 = oimo_vec3_zero();
    row.lin2 = oimo_vec3_zero();
    row.ang1 = oimo_vec3_zero();
    row.ang2 = oimo_vec3_zero();
    return row;
}

static inline void oimo_jacobian_row_clear(OimoJacobianRow* row) {
    row->lin1 = oimo_vec3_zero();
    row->lin2 = oimo_vec3_zero();
    row->ang1 = oimo_vec3_zero();
    row->ang2 = oimo_vec3_zero();
}
