#ifndef LightFieldProbe_glsl
#define LightFieldProbe_glsl

// Compatibility and helper code from G3D
#include <g3dmath.glsl>
#include <Texture/Texture.glsl>

// From G3D, but included directly in this supplement
// because it is core to the algorithm
#include "octahedral.glsl"

const float minThickness = 0.03; // meters
const float maxThickness = 0.50; // meters

uniform sampler3D voxels;
in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

// Points exactly on the boundary in octahedral space (x = 0 and y = 0 planes) map to two different
// locations in octahedral space. We shorten the segments slightly to give unambigous locations that lead
// to intervals that lie within an octant.
const float rayBumpEpsilon    = 0.001; // meters

// If we go all the way around a cell and don't move farther than this (in m)
// then we quit the trace
const float minProgressDistance = 0.01;

//  zyx bit pattern indicating which probe we're currently using within the cell on [0, 7]
#define CycleIndex int

// On [0, L.probeCounts.x * L.probeCounts.y * L.probeCounts.z - 1]
#define ProbeIndex int

// probe xyz indices
#define GridCoord ivec3

// Enumerated value
#define TraceResult int
#define TRACE_RESULT_MISS    0
#define TRACE_RESULT_HIT     1
#define TRACE_RESULT_UNKNOWN 2

struct LightFieldSurface {
    Texture2DArray          radianceProbeGrid;
    Texture2DArray          normalProbeGrid;
    Texture2DArray          distanceProbeGrid;
    Texture2DArray          lowResolutionDistanceProbeGrid;
    Vector3int32            probeCounts;
    Point3                  probeStartPosition;
    Vector3                 probeStep;
    int                     lowResolutionDownsampleFactor;
    TextureCubeArray        irradianceProbeGrid;
    TextureCubeArray        meanDistProbeGrid;
};


float distanceSquared(Point2 v0, Point2 v1) {
    Point2 d = v1 - v0;
    return dot(d, d);
}

/** 
 \param probeCoords Integer (stored in float) coordinates of the probe on the probe grid 
 */
ProbeIndex gridCoordToProbeIndex(in LightFieldSurface L, in Point3 probeCoords) {
    return int(probeCoords.x + probeCoords.y * L.probeCounts.x + probeCoords.z * L.probeCounts.x * L.probeCounts.y);
}

GridCoord baseGridCoord(in LightFieldSurface L, Point3 X) {
    return clamp(GridCoord((X - L.probeStartPosition) / L.probeStep),
                GridCoord(0, 0, 0), 
                GridCoord(L.probeCounts) - GridCoord(1, 1, 1));
}

/** Returns the index of the probe at the floor along each dimension. */
ProbeIndex baseProbeIndex(in LightFieldSurface L, Point3 X) {
    return gridCoordToProbeIndex(L, baseGridCoord(L, X));
}


GridCoord probeIndexToGridCoord(in LightFieldSurface L, ProbeIndex index) {
    // Assumes probeCounts are powers of two.
    // Precomputing the MSB actually slows this code down substantially
    ivec3 iPos;
    iPos.x = index & (L.probeCounts.x - 1);
    iPos.y = (index & ((L.probeCounts.x * L.probeCounts.y) - 1)) >> findMSB(L.probeCounts.x);
    iPos.z = index >> findMSB(L.probeCounts.x * L.probeCounts.y);

    return iPos;
}


Color3 probeIndexToColor(in LightFieldSurface L, ProbeIndex index) {
    return gridCoordToColor(probeIndexToGridCoord(L, index));
}


/** probeCoords Coordinates of the probe, computed as part of the process. */
ProbeIndex nearestProbeIndex(in LightFieldSurface L, Point3 X, out Point3 probeCoords) {
    probeCoords = clamp(round((X - L.probeStartPosition) / L.probeStep),
                    Point3(0, 0, 0), 
                    Point3(L.probeCounts) - Point3(1, 1, 1));

    return gridCoordToProbeIndex(L, probeCoords);
}

/** 
    \param neighbors The 8 probes surrounding X
    \return Index into the neighbors array of the index of the nearest probe to X 
*/
CycleIndex nearestProbeIndices(in LightFieldSurface L, Point3 X) {
    Point3 maxProbeCoords = Point3(L.probeCounts) - Point3(1, 1, 1);
    Point3 floatProbeCoords = (X - L.probeStartPosition) / L.probeStep;
    Point3 baseProbeCoords = clamp(floor(floatProbeCoords), Point3(0, 0, 0), maxProbeCoords);

    float minDist = 10.0f;
    int nearestIndex = -1;

    for (int i = 0; i < 8; ++i) {
        Point3 newProbeCoords = min(baseProbeCoords + vec3(i & 1, (i >> 1) & 1, (i >> 2) & 1), maxProbeCoords);
        float d = length(newProbeCoords - floatProbeCoords);
        if (d < minDist) {
            minDist = d;
            nearestIndex = i;
        }       
    }

    return nearestIndex;
}


Point3 gridCoordToPosition(in LightFieldSurface L, GridCoord c) {
    return L.probeStep * Vector3(c) + L.probeStartPosition;
}


Point3 probeLocation(in LightFieldSurface L, ProbeIndex index) {
    return gridCoordToPosition(L, probeIndexToGridCoord(L, index));
}


/** GLSL's dot on ivec3 returns a float. This is an all-integer version */
int idot(ivec3 a, ivec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}


/**
   \param baseProbeIndex Index into L.radianceProbeGrid's TEXTURE_2D_ARRAY. This is the probe
   at the floor of the current ray sampling position.

   \param relativeIndex on [0, 7]. This is used as a set of three 1-bit offsets

   Returns a probe index into L.radianceProbeGrid. It may be the *same* index as 
   baseProbeIndex.

   This will wrap when the camera is outside of the probe field probes...but that's OK. 
   If that case arises, then the trace is likely to 
   be poor quality anyway. Regardless, this function will still return the index 
   of some valid probe, and that probe can either be used or fail because it does not 
   have visibility to the location desired.

   \see nextCycleIndex, baseProbeIndex
 */
ProbeIndex relativeProbeIndex(in LightFieldSurface L, ProbeIndex baseProbeIndex, CycleIndex relativeIndex) {
    // Guaranteed to be a power of 2
    ProbeIndex numProbes = L.probeCounts.x * L.probeCounts.y * L.probeCounts.z;

    ivec3 offset = ivec3(relativeIndex & 1, (relativeIndex >> 1) & 1, (relativeIndex >> 2) & 1);
    ivec3 stride = ivec3(1, L.probeCounts.x, L.probeCounts.x * L.probeCounts.y);

    return (baseProbeIndex + idot(offset, stride)) & (numProbes - 1);
}


/** Given a CycleIndex [0, 7] on a cube of probes, returns the next CycleIndex to use. 
    \see relativeProbeIndex
*/
CycleIndex nextCycleIndex(CycleIndex cycleIndex) {
    return (cycleIndex + 3) & 7;
}


float squaredLength(Vector3 v) {
    return dot(v, v);
}


/** Two-element sort: maybe swaps a and b so that a' = min(a, b), b' = max(a, b). */
void minSwap(inout float a, inout float b) {
    float temp = min(a, b);
    b = max(a, b);
    a = temp;
}


/** Sort the three values in v from least to 
    greatest using an exchange network (i.e., no branches) */
void sort(inout float3 v) {
    minSwap(v[0], v[1]);
    minSwap(v[1], v[2]);
    minSwap(v[0], v[1]);
}


/** Segments a ray into the piecewise-continuous rays or line segments that each lie within
    one Euclidean octant, which correspond to piecewise-linear projections in octahedral space.
        
    \param boundaryT  all boundary distance ("time") values in units of world-space distance 
      along the ray. In the (common) case where not all five elements are needed, the unused 
      values are all equal to tMax, creating degenerate ray segments.

    \param origin Ray origin in the Euclidean object space of the probe

    \param directionFrac 1 / ray.direction
 */
void computeRaySegments
   (in Point3           origin, 
    in Vector3          directionFrac, 
    in float            tMin,
    in float            tMax,
    out float           boundaryTs[5]) {

    boundaryTs[0] = tMin;
    
    // Time values for intersection with x = 0, y = 0, and z = 0 planes, sorted
    // in increasing order
    Vector3 t = origin * -directionFrac;
    sort(t);

    // Copy the values into the interval boundaries.
    // This loop expands at compile time and eliminates the
    // relative indexing, so it is just three conditional move operations
    for (int i = 0; i < 3; ++i) {
        boundaryTs[i + 1] = clamp(t[i], tMin, tMax);
    }

    boundaryTs[4] = tMax;
}


/** Returns the distance along v from the origin to the intersection 
    with ray R (which it is assumed to intersect) */
float distanceToIntersection(in Ray R, in Vector3 v) {
    float numer;
    float denom = v.y * R.direction.z - v.z * R.direction.y;

    if (abs(denom) > 0.1) {
        numer = R.origin.y * R.direction.z - R.origin.z * R.direction.y;
    } else {
        // We're in the yz plane; use another one
        numer = R.origin.x * R.direction.y - R.origin.y * R.direction.x;
        denom = v.x * R.direction.y - v.y * R.direction.x;
    }

    return numer / denom;
}


/**
  On a TRACE_RESULT_MISS, bumps the endTexCoord slightly so that the next segment will start at the
  right place. We do that in the high res trace because
  the ray direction variables are already available here.

  TRACE_RESULT_HIT:      This probe guarantees there IS a surface on this segment
  TRACE_RESULT_MISS:     This probe guarantees there IS NOT a surface on this segment
  TRACE_RESULT_UNKNOWN:  This probe can't provide any information
*/
TraceResult highResolutionTraceOneRaySegment
   (in LightFieldSurface lightFieldSurface,
    in Ray      probeSpaceRay,
    in Point2   startTexCoord, 
    in Point2   endTexCoord,    
    in ProbeIndex probeIndex,
    inout float tMin,
    inout float tMax,
    inout vec2  hitProbeTexCoord) {    
      
    Vector2 texCoordDelta        = endTexCoord - startTexCoord;
    float texCoordDistance       = length(texCoordDelta);
    Vector2 texCoordDirection    = texCoordDelta * (1.0 / texCoordDistance);

    float texCoordStep = lightFieldSurface.distanceProbeGrid.invSize.x * (texCoordDistance / maxComponent(abs(texCoordDelta)));
    
    Vector3 directionFromProbeBefore = octDecode(startTexCoord * 2.0 - 1.0);
    float distanceFromProbeToRayBefore = max(0.0, distanceToIntersection(probeSpaceRay, directionFromProbeBefore));

    // Special case for singularity of probe on ray
    if (false) {
        float cosTheta = dot(directionFromProbeBefore, probeSpaceRay.direction);
        if (abs(cosTheta) > 0.9999) {        
            // Check if the ray is going in the same direction as a ray from the probe through the start texel
            if (cosTheta > 0) {
                // If so, return a hit
                float distanceFromProbeToSurface = texelFetch(lightFieldSurface.distanceProbeGrid.sampler,
                    ivec3(lightFieldSurface.distanceProbeGrid.size.xy * startTexCoord, probeIndex), 0).r;
                tMax = length(probeSpaceRay.origin - directionFromProbeBefore * distanceFromProbeToSurface);
                hitProbeTexCoord = startTexCoord;
                return TRACE_RESULT_HIT;
            } else {
                // If it is going in the opposite direction, we're never going to find anything useful, so return false
                return TRACE_RESULT_UNKNOWN;
            }
        }
    }

    for (float d = 0.0f; d <= texCoordDistance; d += texCoordStep) {
        Point2 texCoord = (texCoordDirection * min(d + texCoordStep * 0.5, texCoordDistance)) + startTexCoord;

        // Fetch the probe data
        float distanceFromProbeToSurface = texelFetch(lightFieldSurface.distanceProbeGrid.sampler,
            ivec3(lightFieldSurface.distanceProbeGrid.size.xy * texCoord, probeIndex), 0).r;

        // Find the corresponding point in probe space. This defines a line through the 
        // probe origin
        Vector3 directionFromProbe = octDecode(texCoord * 2.0 - 1.0);
        
        Point2 texCoordAfter = (texCoordDirection * min(d + texCoordStep, texCoordDistance)) + startTexCoord;
        Vector3 directionFromProbeAfter = octDecode(texCoordAfter * 2.0 - 1.0);
        float distanceFromProbeToRayAfter = max(0.0, distanceToIntersection(probeSpaceRay, directionFromProbeAfter));
        float maxDistFromProbeToRay = max(distanceFromProbeToRayBefore, distanceFromProbeToRayAfter);

        if (maxDistFromProbeToRay >= distanceFromProbeToSurface) {
            // At least a one-sided hit; see if the ray actually passed through the surface, or was behind it

            float minDistFromProbeToRay = min(distanceFromProbeToRayBefore, distanceFromProbeToRayAfter);

            // Find the 3D point *on the trace ray* that corresponds to the tex coord.
            // This is the intersection of the ray out of the probe origin with the trace ray.
            float distanceFromProbeToRay = (minDistFromProbeToRay + maxDistFromProbeToRay) * 0.5;

            // Use probe information
            Point3 probeSpaceHitPoint = distanceFromProbeToSurface * directionFromProbe;
            float distAlongRay = dot(probeSpaceHitPoint - probeSpaceRay.origin, probeSpaceRay.direction);

            // Read the normal for use in detecting backfaces
            vec3 normal = octDecode(texelFetch(lightFieldSurface.normalProbeGrid.sampler, ivec3(lightFieldSurface.distanceProbeGrid.size.xy * texCoord, probeIndex), 0).xy * lightFieldSurface.normalProbeGrid.readMultiplyFirst.xy + lightFieldSurface.normalProbeGrid.readAddSecond.xy);

            // Only extrude towards and away from the view ray, not perpendicular to it
            // Don't allow extrusion TOWARDS the viewer, only away
            float surfaceThickness = minThickness
                + (maxThickness - minThickness) * 

                // Alignment of probe and view ray
                max(dot(probeSpaceRay.direction, directionFromProbe), 0.0) * 

                // Alignment of probe and normal (glancing surfaces are assumed to be thicker because they extend into the pixel)
                (2 - abs(dot(probeSpaceRay.direction, normal))) *

                // Scale with distance along the ray
                clamp(distAlongRay * 0.1, 0.05, 1.0);


            if ((minDistFromProbeToRay < distanceFromProbeToSurface + surfaceThickness) && (dot(normal, probeSpaceRay.direction) < 0)) {
                // Two-sided hit
                // Use the probe's measure of the point instead of the ray distance, since
                // the probe is more accurate (floating point precision vs. ray march iteration/oct resolution)
                tMax = distAlongRay;
                hitProbeTexCoord = texCoord;
                
                return TRACE_RESULT_HIT;
            } else {
                // "Unknown" case. The ray passed completely behind a surface. This should trigger moving to another
                // probe and is distinguished from "I successfully traced to infinity"
                
                // Back up conservatively so that we don't set tMin too large
                Point3 probeSpaceHitPointBefore = distanceFromProbeToRayBefore * directionFromProbeBefore;
                float distAlongRayBefore = dot(probeSpaceHitPointBefore - probeSpaceRay.origin, probeSpaceRay.direction);
                
                // Max in order to disallow backing up along the ray (say if beginning of this texel is before tMin from probe switch)
                // distAlongRayBefore in order to prevent overstepping
                // min because sometimes distAlongRayBefore > distAlongRay
                tMin = max(tMin, min(distAlongRay,distAlongRayBefore));

                return TRACE_RESULT_UNKNOWN;
            }
        }
        distanceFromProbeToRayBefore = distanceFromProbeToRayAfter;
    } // ray march

    return TRACE_RESULT_MISS;
}


/** Returns true on a conservative hit, false on a guaranteed miss.
    On a hit, advances lowResTexCoord to the next low res texel *after*
    the one that produced the hit.

    The texture coordinates are not texel centers...they are sub-texel 
    positions true to the actual ray. This allows chopping up the ray
    without distorting it.

    segmentEndTexCoord is the coordinate of the endpoint of the entire segment of the ray

    texCoord is the start coordinate of the segment crossing
    the low-res texel that produced the conservative hit, if the function 
    returns true.  endHighResTexCoord is the end coordinate of that 
    segment...which is also the start of the NEXT low-res texel to cross
    when resuming the low res trace.

  */
bool lowResolutionTraceOneSegment
   (in LightFieldSurface lightFieldSurface, 
    in Ray               probeSpaceRay, 
    in ProbeIndex        probeIndex, 
    inout Point2         texCoord, 
    in Point2            segmentEndTexCoord, 
    inout Point2         endHighResTexCoord) {
        
    Vector2 lowResSize    = lightFieldSurface.lowResolutionDistanceProbeGrid.size.xy;
    Vector2 lowResInvSize = lightFieldSurface.lowResolutionDistanceProbeGrid.invSize.xy;

    // Convert the texels to pixel coordinates:
    Point2 P0 = texCoord           * lowResSize;
    Point2 P1 = segmentEndTexCoord * lowResSize;

    // If the line is degenerate, make it cover at least one pixel
    // to avoid handling zero-pixel extent as a special case later
    P1 += vec2((distanceSquared(P0, P1) < 0.0001) ? 0.01 : 0.0);
    // In pixel coordinates
    Vector2 delta = P1 - P0;

    // Permute so that the primary iteration is in x to reduce
    // large branches later
    bool permute = false;
    if (abs(delta.x) < abs(delta.y)) { 
        // This is a more-vertical line
        permute = true;
        delta = delta.yx; P0 = P0.yx; P1 = P1.yx; 
    }

    float   stepDir = sign(delta.x);
    float   invdx = stepDir / delta.x;
    Vector2 dP = vec2(stepDir, delta.y * invdx);
    
    Vector3 initialDirectionFromProbe = octDecode(texCoord * 2.0 - 1.0);
    float prevRadialDistMaxEstimate = max(0.0, distanceToIntersection(probeSpaceRay, initialDirectionFromProbe));
    // Slide P from P0 to P1
    float  end = P1.x * stepDir;
    
    float absInvdPY = 1.0 / abs(dP.y);

    // Don't ever move farther from texCoord than this distance, in texture space,
    // because you'll move past the end of the segment and into a different projection
    float maxTexCoordDistance = lengthSquared(segmentEndTexCoord - texCoord);

    for (Point2 P = P0; ((P.x * sign(delta.x)) <= end); ) {
        
        Point2 hitPixel = permute ? P.yx : P;
        
        float sceneRadialDistMin = texelFetch(lightFieldSurface.lowResolutionDistanceProbeGrid.sampler, int3(hitPixel, probeIndex), 0).r;

        // Distance along each axis to the edge of the low-res texel
        Vector2 intersectionPixelDistance = (sign(delta) * 0.5 + 0.5) - sign(delta) * frac(P);

        // abs(dP.x) is 1.0, so we skip that division
        // If we are parallel to the minor axis, the second parameter will be inf, which is fine
        float rayDistanceToNextPixelEdge = min(intersectionPixelDistance.x, intersectionPixelDistance.y * absInvdPY);

        // The exit coordinate for the ray (this may be *past* the end of the segment, but the 
        // callr will handle that)
        endHighResTexCoord = (P + dP * rayDistanceToNextPixelEdge) * lowResInvSize;
        endHighResTexCoord = permute ? endHighResTexCoord.yx : endHighResTexCoord;

        if (lengthSquared(endHighResTexCoord - texCoord) > maxTexCoordDistance) {
            // Clamp the ray to the segment, because if we cross a segment boundary in oct space
            // then we bend the ray in probe and world space.
            endHighResTexCoord = segmentEndTexCoord;
        }

        // Find the 3D point *on the trace ray* that corresponds to the tex coord.
        // This is the intersection of the ray out of the probe origin with the trace ray.
        Vector3 directionFromProbe = octDecode(endHighResTexCoord * 2.0 - 1.0);
        float distanceFromProbeToRay = max(0.0, distanceToIntersection(probeSpaceRay, directionFromProbe));

        float maxRadialRayDistance = max(distanceFromProbeToRay, prevRadialDistMaxEstimate);
        prevRadialDistMaxEstimate = distanceFromProbeToRay;
        
        if (sceneRadialDistMin < maxRadialRayDistance) {
            // A conservative hit.
            //
            //  -  endHighResTexCoord is already where the ray would have LEFT the texel
            //     that created the hit.
            //
            //  -  texCoord should be where the ray entered the texel
            texCoord = (permute ? P.yx : P) * lowResInvSize;
            return true;
        }

        // Ensure that we step just past the boundary, so that we're slightly inside the next
        // texel, rather than at the boundary and randomly rounding one way or the other.
        const float epsilon = 0.001; // pixels
        P += dP * (rayDistanceToNextPixelEdge + epsilon);
    } // for each pixel on ray

    // If exited the loop, then we went *past* the end of the segment, so back up to it (in practice, this is ignored
    // by the caller because it indicates a miss for the whole segment)
    texCoord = segmentEndTexCoord;

    return false;
}


TraceResult traceOneRaySegment
   (in LightFieldSurface lightFieldSurface, 
    in Ray      probeSpaceRay, 
    in float    t0, 
    in float    t1,    
    in ProbeIndex probeIndex,
    inout float tMin, // out only
    inout float tMax, 
    inout vec2  hitProbeTexCoord) {
    
    // Euclidean probe-space line segment, composed of two points on the probeSpaceRay
    Vector3 probeSpaceStartPoint = probeSpaceRay.origin + probeSpaceRay.direction * (t0 + rayBumpEpsilon);
    Vector3 probeSpaceEndPoint   = probeSpaceRay.origin + probeSpaceRay.direction * (t1 - rayBumpEpsilon);

    // If the original ray origin is really close to the probe origin, then probeSpaceStartPoint will be close to zero
    // and we get NaN when we normalize it. One common case where this can happen is when the camera is at the probe
    // center. (The end point is also potentially problematic, but the chances of the end landing exactly on a probe 
    // are relatively low.) We only need the *direction* to the start point, and using probeSpaceRay.direction
    // is safe in that case.
    if (squaredLength(probeSpaceStartPoint) < 0.001) {
        probeSpaceStartPoint = probeSpaceRay.direction;
    }

    // Corresponding octahedral ([-1, +1]^2) space line segment.
    // Because the points are in probe space, we don't have to subtract off the probe's origin
    Point2 startOctCoord         = octEncode(normalize(probeSpaceStartPoint));
    Point2 endOctCoord           = octEncode(normalize(probeSpaceEndPoint));

    // Texture coordinates on [0, 1]
    Point2 texCoord              = startOctCoord * 0.5 + 0.5;
    Point2 segmentEndTexCoord    = endOctCoord   * 0.5 + 0.5;

    while (true) {
        Point2 endTexCoord;

        // Trace low resolution, min probe until we:
        // - reach the end of the segment (return "miss" from the whole function)
        // - "hit" the surface (invoke high-resolution refinement, and then iterate if *that* misses)
            
        // If lowResolutionTraceOneSegment conservatively "hits", it will set texCoord and endTexCoord to be the high-resolution texture coordinates.
        // of the intersection between the low-resolution texel that was hit and the ray segment.
        Vector2 originalStartCoord = texCoord;
        if (! lowResolutionTraceOneSegment(lightFieldSurface, probeSpaceRay, probeIndex, texCoord, segmentEndTexCoord, endTexCoord)) {
            // The whole trace failed to hit anything           
            return TRACE_RESULT_MISS;
        } else {

            // The low-resolution trace already guaranted that endTexCoord is no farther along the ray than segmentEndTexCoord if this point is reached,
            // so we don't need to clamp to the segment length
            TraceResult result = highResolutionTraceOneRaySegment(lightFieldSurface, probeSpaceRay, texCoord, endTexCoord, probeIndex, tMin, tMax, hitProbeTexCoord);

            if (result != TRACE_RESULT_MISS) {
                // High-resolution hit or went behind something, which must be the result for the whole segment trace
                return result;
            } 
        } // else...continue the outer loop; we conservatively refined and didn't actually find a hit

        // Recompute each time around the loop to avoid increasing the peak register count
        Vector2 texCoordRayDirection = normalize(segmentEndTexCoord - texCoord);

        if (dot(texCoordRayDirection, segmentEndTexCoord - endTexCoord) <= lightFieldSurface.distanceProbeGrid.invSize.x) {
            // The high resolution trace reached the end of the segment; we've failed to find a hit
            return TRACE_RESULT_MISS;
        } else {
            // We made it to the end of the low-resolution texel using the high-resolution trace, so that's
            // the starting point for the next low-resolution trace. Bump the ray to guarantee that we advance
            // instead of getting stuck back on the low-res texel we just verified...but, if that fails on the 
            // very first texel, we'll want to restart the high-res trace exactly where we left off, so
            // don't bump by an entire high-res texel
            texCoord = endTexCoord + texCoordRayDirection * lightFieldSurface.distanceProbeGrid.invSize.x * 0.1;
        }
    } // while low-resolution trace

    // Reached the end of the segment
    return TRACE_RESULT_MISS;
}



/**
  \param tMax On call, the stop distance for the trace. On return, the distance 
        to the new hit, if one was found. Always finite.
  \param tMin On call, the start distance for the trace. On return, the start distance
        of the ray right before the first "unknown" step.
  \param hitProbeTexCoord Written to only on a hit
  \param index probe index
 */
TraceResult traceOneProbeOct(in LightFieldSurface lightFieldSurface, in ProbeIndex index, in Ray worldSpaceRay, inout float tMin, inout float tMax, inout vec2 hitProbeTexCoord) {
    // How short of a ray segment is not worth tracing?
    const float degenerateEpsilon = 0.001; // meters
    
    Point3 probeOrigin = probeLocation(lightFieldSurface, index);
    
    Ray probeSpaceRay;
    probeSpaceRay.origin    = worldSpaceRay.origin - probeOrigin;
    probeSpaceRay.direction = worldSpaceRay.direction;

    // Maximum of 5 boundary points when projecting ray onto octahedral map; 
    // ray origin, ray end, intersection with each of the XYZ planes.
    float boundaryTs[5];
    computeRaySegments(probeSpaceRay.origin, Vector3(1.0) / probeSpaceRay.direction, tMin, tMax, boundaryTs);
    
    // for each open interval (t[i], t[i + 1]) that is not degenerate
    for (int i = 0; i < 4; ++i) {
        if (abs(boundaryTs[i] - boundaryTs[i + 1]) >= degenerateEpsilon) {
            TraceResult result = traceOneRaySegment(lightFieldSurface, probeSpaceRay, boundaryTs[i], boundaryTs[i + 1], index, tMin, tMax, hitProbeTexCoord);
            
            switch (result) {
            case TRACE_RESULT_HIT:
                // Hit!            
                return TRACE_RESULT_HIT;

            case TRACE_RESULT_UNKNOWN:
                // Failed to find anything conclusive
                return TRACE_RESULT_UNKNOWN;
            } // switch
        } // if 
    } // For each segment

    return TRACE_RESULT_MISS;
}


/** Traces a ray against the full lightfield.
    Returns true on a hit and updates \a tMax if there is a ray hit before \a tMax. 
   Otherwise returns false and leaves tMax unmodified 
   
   \param hitProbeTexCoord on [0, 1]
   
   \param fillHoles If true, this function MUST return a hit even if it is forced to use a coarse approximation
 */
bool trace(LightFieldSurface lightFieldSurface, Ray worldSpaceRay, inout float tMax, out Point2 hitProbeTexCoord, out ProbeIndex hitProbeIndex, const bool fillHoles) {
    
    hitProbeIndex = -1;

    int i = nearestProbeIndices(lightFieldSurface, worldSpaceRay.origin);
    int probesLeft = 8;
    float tMin = 0.0f;
    while (probesLeft > 0) {
        TraceResult result = traceOneProbeOct(lightFieldSurface, relativeProbeIndex(lightFieldSurface, baseIndex, i),
            worldSpaceRay, tMin, tMax, hitProbeTexCoord);
        if (result == TRACE_RESULT_UNKNOWN) {
            i = nextCycleIndex(i);
            --probesLeft;
        } else {
            if (result == TRACE_RESULT_HIT) {
                hitProbeIndex = relativeProbeIndex(lightFieldSurface, baseIndex, i);
            }
            // Found the hit point
            break;
        }
    }
    
    if ((hitProbeIndex == -1) && fillHoles) {
        // No probe found a solution, so force some backup plan 
        Point3 ignore;
        hitProbeIndex = nearestProbeIndex(lightFieldSurface, worldSpaceRay.origin, ignore);
        hitProbeTexCoord = octEncode(worldSpaceRay.direction) * 0.5 + 0.5;

        float probeDistance = texelFetch(lightFieldSurface.distanceProbeGrid.sampler, ivec3(ivec2(hitProbeTexCoord * lightFieldSurface.distanceProbeGrid.size.xy), hitProbeIndex), 0).r;
        if (probeDistance < 10000) {
            Point3 hitLocation = probeLocation(lightFieldSurface, hitProbeIndex) + worldSpaceRay.direction * probeDistance;
            tMax = length(worldSpaceRay.origin - hitLocation);
            return true;
        }
    }

    return (hitProbeIndex != -1);
}

// Engine-specific arguments and helper functions have been removed from the following code 

Irradiance3 computePrefilteredIrradiance(Point3 wsPosition) {
    GridCoord baseGridCoord = baseGridCoord(lightFieldSurface, wsPosition);
    Point3 baseProbePos = gridCoordToPosition(lightFieldSurface, baseGridCoord);
    Irradiance3 sumIrradiance = Irradiance3(0);
    float sumWeight = 0.0;
    // Trilinear interpolation values along axes
    Vector3 alpha = clamp((wsPosition - baseProbePos) / lightFieldSurface.probeStep, Vector3(0), Vector3(1));

    // Iterate over the adjacent probes defining the surrounding vertex "cage"
    for (int i = 0; i < 8; ++i) {
        // Compute the offset grid coord and clamp to the probe grid boundary
        GridCoord  offset = ivec3(i, i >> 1, i >> 2) & ivec3(1);
        GridCoord  probeGridCoord = clamp(baseGridCoord + offset, GridCoord(0), GridCoord(lightFieldSurface.probeCounts - 1));
        ProbeIndex p = gridCoordToProbeIndex(lightFieldSurface, probeGridCoord);

        // Compute the trilinear weights based on the grid cell vertex to smoothly
        // transition between probes. Avoid ever going entirely to zero because that
        // will cause problems at the border probes.
        Vector3 trilinear = lerp(1 - alpha, alpha, offset);
        float weight = trilinear.x * trilinear.y * trilinear.z;

        // Make cosine falloff in tangent plane with respect to the angle from the surface to the probe so that we never
        // test a probe that is *behind* the surface.
        // It doesn't have to be cosine, but that is efficient to compute and we must clip to the tangent plane.
        Point3 probePos = gridCoordToPosition(lightFieldSurface, probeGridCoord);
        Vector3 probeToPoint = wsPosition - probePos;
        Vector3 dir = normalize(-probeToPoint);

        // Smooth back-face test
        weight *= max(0.05, dot(dir, wsN));

        float2 temp = texture(lightFieldSurface.meanDistProbeGrid.sampler, vec4(-dir, p)).rg;
        float mean = temp.x;
        float variance = abs(temp.y - square(mean));

        float distToProbe = length(probeToPoint);
        // http://www.punkuser.net/vsm/vsm_paper.pdf; equation 5
        float t_sub_mean = distToProbe - mean;
        float chebychev = variance / (variance + square(t_sub_mean));

        weight *= ((distToProbe <= mean) ? 1.0 : max(chebychev, 0.0));

        // Avoid zero weight
        weight = max(0.0002, weight);

        sumWeight += weight;

        Vector3 irradianceDir = wsN;

        Irradiance3 probeIrradiance = texture(lightFieldSurface.irradianceProbeGrid.sampler, vec4(normalize(irradianceDir), p)).rgb;

        // Debug probe contribution by visualizing as colors
        // probeIrradiance = 0.5 * probeIndexToColor(lightFieldSurface, p);

        sumIrradiance += weight * probeIrradiance;
    }

    return 2.0 * pi * sumIrradiance / sumWeight;
}

/*
// Stochastically samples one glossy ray
Radiance3 computeGlossyRay(Point3 wsPosition, Vector3 wo, Vector3 n, ...) {
    const float rayBumpEpsilon = 0.001;

    Vector3 wi = importanceSampleBRDFDirection(wo, n);

    Ray worldSpaceRay = Ray(wsPosition + wi * rayBumpEpsilon, wi);

    float   hitDistance = 10000;
    Point2  hitProbeTexCoord;
    int     probeIndex;
    if (!trace(lightFieldSurface, worldSpaceRay, hitDistance, hitProbeTexCoord, probeIndex, FILL_HOLES == 1)) {
        // Missed the entire scene; fall back to the environment map
        return computeGlossyEnvironmentMapLighting(wi, true, glossyExponent, false);
    } else {
        // Sample the light probe radiance texture
        return textureLod(lightFieldSurface.radianceProbeGrid.sampler, float3(hitProbeTexCoord, probeIndex), 0).rgb;
    }
}
*/
#endif // Header guard
