#ifndef OIMO_MAT3_H
#define OIMO_MAT3_H

#include "Vec3.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Mat3 - 3x3 Rotation Matrix
// libdragon doesn't have a 3x3 matrix, so we define our own
// Uses row-major convention: m[row][col]
// =============================================================================

typedef struct Mat3 {
    float m[3][3];
} Mat3;

// Forward declare Quat for conversions
typedef fm_quat_t Quat;

// Construction
Mat3 mat3_new(float e00, float e01, float e02,
              float e10, float e11, float e12,
              float e20, float e21, float e22);
void mat3_init(Mat3* m, float e00, float e01, float e02,
               float e10, float e11, float e12,
               float e20, float e21, float e22);
Mat3 mat3_identity(void);

// Arithmetic
void mat3_add(Mat3* m1, const Mat3* m2);
void mat3_sub(Mat3* m1, const Mat3* m2);
void mat3_scale(Mat3* m, float s);
void mat3_mul(Mat3* m1, const Mat3* m2);
void mat3_mul_out(Mat3* out, const Mat3* a, const Mat3* b);

// Transpose / Inverse / Determinant
void mat3_transpose(Mat3* m);
Mat3 mat3_transposed(const Mat3* m);
float mat3_determinant(const Mat3* m);
void mat3_inverse(Mat3* m);

// Copy
void mat3_copy_from(Mat3* m1, const Mat3* m2);
Mat3 mat3_clone(const Mat3* m);

// Row/Column access
Vec3 mat3_get_row(const Mat3* m, int index);
Vec3 mat3_get_col(const Mat3* m, int index);
void mat3_get_row_to(const Mat3* m, int index, Vec3* dst);
void mat3_get_col_to(const Mat3* m, int index, Vec3* dst);

// Conversions
Mat3 mat3_from_quat(const Quat* q);
Quat mat3_to_quat(const Mat3* m);
Mat3 mat3_from_euler_xyz(const Vec3* euler);
Vec3 mat3_to_euler_xyz(const Mat3* m);

// Vector-Matrix multiplication
void vec3_mul_mat3(Vec3* v, const Mat3* m);

#ifdef __cplusplus
}
#endif

#endif // OIMO_MAT3_H
