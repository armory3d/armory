#include "recastjs.h"
#include "Recast.h"
#include "DetourNavMesh.h"
#include "DetourCommon.h"
#include "DetourNavMeshBuilder.h"
#include "DetourNavMesh.h"
#include "DetourNavMeshQuery.h"
#include "ChunkyTriMesh.h"

#include <stdio.h>
#include <vector>
#include <float.h>
#include <algorithm>
#include <math.h>
#include <sstream>
#include <cstring>

void Log(const char* str)
{
    std::cout << std::string(str) << std::endl;
}

int g_seed = 1337;
inline int fastrand() 
{ 
    g_seed = (214013*g_seed+2531011); 
    return (g_seed>>16)&0x7FFF; 
} 

inline float r01()
{
    return ((float)fastrand())*(1.f/32767.f);
}

// This value specifies how many layers (or "floors") each navmesh tile is expected to have.
static const int EXPECTED_LAYERS_PER_TILE = 4;
static const int MAX_LAYERS = 32;

struct TileCacheData
{
    unsigned char* data;
    int dataSize;
};

struct NavMeshintermediates
{
    ~NavMeshintermediates()
    {
        if (m_solid)
        {
            rcFreeHeightField(m_solid);
        }
        if (m_chf)
        {
            rcFreeCompactHeightfield(m_chf);
        }
        if (m_cset)
        {
            rcFreeContourSet(m_cset);
        }
        if (m_lset)
        {
            rcFreeHeightfieldLayerSet(m_lset);
        }
        if (m_chunkyMesh)
        {
            delete m_chunkyMesh;
        }
    }

    rcHeightfield* m_solid = nullptr;
    rcCompactHeightfield* m_chf = nullptr;
    rcContourSet* m_cset = nullptr;
    rcHeightfieldLayerSet* m_lset = nullptr;
    rcChunkyTriMesh* m_chunkyMesh = nullptr;

};

void NavMesh::destroy()
{
    if (m_pmesh)
    {
        rcFreePolyMesh(m_pmesh);
    }
    if (m_dmesh)
    {
        rcFreePolyMeshDetail(m_dmesh);
    }
    if (m_navData)
    {
        dtFree(m_navData);
    }
    dtFreeNavMesh(m_navMesh);
    dtFreeNavMeshQuery(m_navQuery);
    if (m_tileCache)
    {
        dtFreeTileCache(m_tileCache);
    }
    m_talloc.reset();
}

int NavMesh::rasterizeTileLayers(const int tx, const int ty,
                                    const rcConfig& cfg,
                                    TileCacheData* tiles,
                                    const int maxTiles,
                                    NavMeshintermediates& intermediates,
                                    const std::vector<unsigned char>& triareas,
                                    const std::vector<float>& verts)
{
    RecastFastLZCompressor comp;

    // Tile bounds.
    const float tcs = cfg.tileSize * cfg.cs;
    
    rcConfig tcfg;
    memcpy(&tcfg, &cfg, sizeof(tcfg));

    tcfg.bmin[0] = cfg.bmin[0] + tx*tcs;
    tcfg.bmin[1] = cfg.bmin[1];
    tcfg.bmin[2] = cfg.bmin[2] + ty*tcs;
    tcfg.bmax[0] = cfg.bmin[0] + (tx+1)*tcs;
    tcfg.bmax[1] = cfg.bmax[1];
    tcfg.bmax[2] = cfg.bmin[2] + (ty+1)*tcs;
    tcfg.bmin[0] -= tcfg.borderSize*tcfg.cs;
    tcfg.bmin[2] -= tcfg.borderSize*tcfg.cs;
    tcfg.bmax[0] += tcfg.borderSize*tcfg.cs;
    tcfg.bmax[2] += tcfg.borderSize*tcfg.cs;
    
    NavMeshintermediates tileIntermediates;
    // Allocate voxel heightfield where we rasterize our input data to.
    tileIntermediates.m_solid = rcAllocHeightfield();
    if (!tileIntermediates.m_solid)
    {
        Log("buildNavigation: Out of memory 'solid'.");
        return 0;
    }
    rcContext ctx;

    if (!rcCreateHeightfield(&ctx, *tileIntermediates.m_solid, tcfg.width, tcfg.height, tcfg.bmin, tcfg.bmax, tcfg.cs, tcfg.ch))
    {
        Log("buildNavigation: Could not create solid heightfield.");
        return 0;
    }
    
    rcChunkyTriMesh* chunkyMesh = intermediates.m_chunkyMesh;

    float tbmin[2], tbmax[2];
    tbmin[0] = tcfg.bmin[0];
    tbmin[1] = tcfg.bmin[2];
    tbmax[0] = tcfg.bmax[0];
    tbmax[1] = tcfg.bmax[2];
    int cid[512];// TODO: Make grow when returning too many items.
    const int ncid = rcGetChunksOverlappingRect(chunkyMesh, tbmin, tbmax, cid, 512);
    if (!ncid)
    {
        return 0; // empty
    }
    
    for (int i = 0; i < ncid; ++i)
    {
        const rcChunkyTriMeshNode& node = chunkyMesh->nodes[cid[i]];
        const int* ctris = &chunkyMesh->tris[node.i*3];
        const int ntris = node.n;
        
        if (!rcRasterizeTriangles(&ctx, verts.data(), verts.size(), ctris, triareas.data(), ntris, *tileIntermediates.m_solid, tcfg.walkableClimb))
        {
            return 0;
        }
    }
    
    // Once all geometry is rasterized, we do initial pass of filtering to
    // remove unwanted overhangs caused by the conservative rasterization
    // as well as filter spans where the character cannot possibly stand.
    
    //if (m_filterLowHangingObstacles)
    rcFilterLowHangingWalkableObstacles(&ctx, tcfg.walkableClimb, *tileIntermediates.m_solid);
    //if (m_filterLedgeSpans)
    rcFilterLedgeSpans(&ctx, tcfg.walkableHeight, tcfg.walkableClimb, *tileIntermediates.m_solid);
    //if (m_filterWalkableLowHeightSpans)
    rcFilterWalkableLowHeightSpans(&ctx, tcfg.walkableHeight, *tileIntermediates.m_solid);
    
    
    tileIntermediates.m_chf = rcAllocCompactHeightfield();
    if (!tileIntermediates.m_chf)
    {
       Log("buildNavigation: Out of memory 'chf'.");
        return 0;
    }
    if (!rcBuildCompactHeightfield(&ctx, tcfg.walkableHeight, tcfg.walkableClimb, *tileIntermediates.m_solid, *tileIntermediates.m_chf))
    {
        Log("buildNavigation: Could not build compact data.");
        return 0;
    }
    
    // Erode the walkable area by agent radius.
    if (!rcErodeWalkableArea(&ctx, tcfg.walkableRadius, *tileIntermediates.m_chf))
    {
        Log("buildNavigation: Could not erode.");
        return 0;
    }

    tileIntermediates.m_lset = rcAllocHeightfieldLayerSet();
    if (!tileIntermediates.m_lset)
    {
        Log("buildNavigation: Out of memory 'lset'.");
        return 0;
    }
    if (!rcBuildHeightfieldLayers(&ctx, *tileIntermediates.m_chf, tcfg.borderSize, tcfg.walkableHeight, *tileIntermediates.m_lset))
    {
        Log("buildNavigation: Could not build heighfield layers.");
        return 0;
    }
    
    int ntiles = 0;
    TileCacheData ctiles[MAX_LAYERS];
    for (int i = 0; i < rcMin(tileIntermediates.m_lset->nlayers, MAX_LAYERS); ++i)
    {
        TileCacheData* tile = &ctiles[ntiles++];
        const rcHeightfieldLayer* layer = &tileIntermediates.m_lset->layers[i];
        
        // Store header
        dtTileCacheLayerHeader header;
        header.magic = DT_TILECACHE_MAGIC;
        header.version = DT_TILECACHE_VERSION;
        
        // Tile layer location in the navmesh.
        header.tx = tx;
        header.ty = ty;
        header.tlayer = i;
        dtVcopy(header.bmin, layer->bmin);
        dtVcopy(header.bmax, layer->bmax);
        
        // Tile info.
        header.width = (unsigned char)layer->width;
        header.height = (unsigned char)layer->height;
        header.minx = (unsigned char)layer->minx;
        header.maxx = (unsigned char)layer->maxx;
        header.miny = (unsigned char)layer->miny;
        header.maxy = (unsigned char)layer->maxy;
        header.hmin = (unsigned short)layer->hmin;
        header.hmax = (unsigned short)layer->hmax;

        dtStatus status = dtBuildTileCacheLayer(&comp, &header, layer->heights, layer->areas, layer->cons,
                                                &tile->data, &tile->dataSize);
        if (dtStatusFailed(status))
        {
            return 0;
        }
    }

    // Transfer ownsership of tile data from build context to the caller.
    int n = 0;
    for (int i = 0; i < rcMin(ntiles, maxTiles); ++i)
    {
        tiles[n++] = ctiles[i];
        ctiles[i].data = 0;
        ctiles[i].dataSize = 0;
    }
    
    return n;
}

bool NavMesh::computeTiledNavMesh(const std::vector<float>& verts, const std::vector<int>& tris, rcConfig& cfg, NavMeshintermediates& intermediates, const std::vector<unsigned char>& triareas)
{
    dtStatus status;

    const int ts = (int)cfg.tileSize;
    const int tw = (cfg.width + ts-1) / ts;
    const int th = (cfg.height + ts-1) / ts;

    // Generation params.
    cfg.borderSize = cfg.walkableRadius + 3; // Reserve enough padding.
    cfg.width = cfg.tileSize + cfg.borderSize * 2;
    cfg.height = cfg.tileSize + cfg.borderSize * 2;
    
    // Tile cache params.
    dtTileCacheParams tcparams;
    memset(&tcparams, 0, sizeof(tcparams));
    rcVcopy(tcparams.orig, cfg.bmin);
    tcparams.cs = cfg.cs;
    tcparams.ch = cfg.ch;
    tcparams.width = cfg.tileSize;
    tcparams.height = cfg.tileSize;
    tcparams.walkableHeight = cfg.walkableHeight;
    tcparams.walkableRadius = cfg.walkableRadius;
    tcparams.walkableClimb = cfg.walkableClimb;
    tcparams.maxSimplificationError = cfg.maxSimplificationError;
    tcparams.maxTiles = tw * th * EXPECTED_LAYERS_PER_TILE;
    tcparams.maxObstacles = 128;

    m_tileCache = dtAllocTileCache();
    if (!m_tileCache)
    {
        Log("buildTiledNavigation: Could not allocate tile cache.");
        return false;
    }
    status = m_tileCache->init(&tcparams, &m_talloc, &m_tcomp, &m_tmproc);
    if (dtStatusFailed(status))
    {
        Log("buildTiledNavigation: Could not init tile cache.");
        return false;
    }
    
    m_navMesh = dtAllocNavMesh();
    if (!m_navMesh)
    {
        Log("buildTiledNavigation: Could not allocate navmesh.");
        return false;
    }

    dtNavMeshParams params;
    memset(&params, 0, sizeof(params));
    rcVcopy(params.orig, cfg.bmin);
    params.tileWidth = cfg.tileSize * cfg.cs;
    params.tileHeight = cfg.tileSize * cfg.cs;
    // Max tiles and max polys affect how the tile IDs are caculated.
    // There are 22 bits available for identifying a tile and a polygon.
    int tileBits = rcMin((int)dtIlog2(dtNextPow2(tw*th*EXPECTED_LAYERS_PER_TILE)), 14);
    if (tileBits > 14) tileBits = 14;
    int polyBits = 22 - tileBits;
    params.maxTiles = 1 << tileBits;
    params.maxPolys = 1 << polyBits;

    status = m_navMesh->init(&params);
    if (dtStatusFailed(status))
    {
        Log("buildTiledNavigation: Could not init navmesh.");
        return false;
    }

    intermediates.m_chunkyMesh = new rcChunkyTriMesh;
    if (!rcCreateChunkyTriMesh(verts.data(), tris.data(), tris.size() / 3, 256, intermediates.m_chunkyMesh))
    {
        Log("Unable to create chunky trimesh.");
        return false;
    }

    // Preprocess tiles.
    for (int y = 0; y < th; ++y)
    {
        for (int x = 0; x < tw; ++x)
        {
            TileCacheData tiles[MAX_LAYERS];
            memset(tiles, 0, sizeof(tiles));
            int ntiles = rasterizeTileLayers(x, y, cfg, tiles, MAX_LAYERS, intermediates, triareas, verts);
            for (int i = 0; i < ntiles; ++i)
            {
                TileCacheData* tile = &tiles[i];
                status = m_tileCache->addTile(tile->data, tile->dataSize, DT_COMPRESSEDTILE_FREE_DATA, 0);
                if (dtStatusFailed(status))
                {
                    Log("Failed adding tile to tile cache.");
                    dtFree(tile->data);
                    tile->data = 0;
                    continue;
                }
            }
        }
    }

    // Build initial meshes
    for (int y = 0; y < th; ++y)
    {
        for (int x = 0; x < tw; ++x)
        {
            m_tileCache->buildNavMeshTilesAt(x,y, m_navMesh);
        }
    }

    return true;
}

void NavMesh::build(const float* positions, const int positionCount, const int* indices, const int indexCount, const rcConfig& config)
{
    if (m_pmesh)
    {
        rcFreePolyMesh(m_pmesh);
    }
    if (m_dmesh)
    {
        rcFreePolyMeshDetail(m_dmesh);
    }
    if (m_navData)
    {
        dtFree(m_navData);
    }
    if (m_tileCache)
    {
        dtFreeTileCache(m_tileCache);
    }
    m_talloc.reset();

    NavMeshintermediates intermediates;
    std::vector<Vec3> triangleIndices;
    const float* pv = &positions[0];
    const int* t = &indices[0];

    // mesh conversion
    Vec3 bbMin(FLT_MAX);
    Vec3 bbMax(-FLT_MAX);
    triangleIndices.resize(indexCount);
    for (unsigned int i = 0; i<indexCount; i++)
    {
        int ind = (*t++) * 3;
        Vec3 v( pv[ind], pv[ind+1], pv[ind+2] );
        bbMin.isMinOf( v );
        bbMax.isMaxOf( v );
        triangleIndices[i] = v;
    }

    std::vector<float> verts;
    verts.resize(triangleIndices.size()*3);
    int nverts = triangleIndices.size();
    for (unsigned int i =0;i<triangleIndices.size();i++)
    {
        verts[i*3+0] = triangleIndices[i].x;
        verts[i*3+1] = triangleIndices[i].y;
        verts[i*3+2] = triangleIndices[i].z;
    }
    int ntris = triangleIndices.size()/3;
    std::vector<int> tris;
    tris.resize(triangleIndices.size());
    for (unsigned int i = 0;i<triangleIndices.size();i++)
    {
        tris[i] = triangleIndices.size()-i-1;
    }

    // Allocate array that can hold triangle area types.
    // If you have multiple meshes you need to process, allocate
    // and array which can hold the max number of triangles you need to process.
    std::vector<unsigned char> triareas(ntris);
    
    // Find triangles which are walkable based on their slope and rasterize them.
    // If your input data is multiple meshes, you can transform them here, calculate
    // the are type for each of the meshes and rasterize them.
    memset(triareas.data(), RC_WALKABLE_AREA, ntris * sizeof(unsigned char));

    bool keepInterResults = false;

    // Set the area where the navigation will be build.
    // Here the bounds of the input mesh are used, but the
    // area could be specified by an user defined box, etc.
    //float bmin[3] = {-20.f, 0.f, -20.f};
    //float bmax[3] = { 20.f, 1.f,  20.f};
    rcConfig cfg = config;
    cfg.walkableHeight = config.walkableHeight;
    cfg.walkableClimb = config.walkableClimb;
    cfg.walkableRadius = config.walkableRadius;
    cfg.maxEdgeLen = config.maxEdgeLen;
    cfg.maxSimplificationError = config.maxSimplificationError;
    cfg.minRegionArea = (int)rcSqr(config.minRegionArea);        // Note: area = size*size
    cfg.mergeRegionArea = (int)rcSqr(config.mergeRegionArea);    // Note: area = size*size
    cfg.maxVertsPerPoly = (int)config.maxVertsPerPoly;
    cfg.detailSampleDist = config.detailSampleDist < 0.9f ? 0 : config.cs * config.detailSampleDist;
    cfg.detailSampleMaxError = config.ch * config.detailSampleMaxError;

    rcVcopy(cfg.bmin, &bbMin.x);
    rcVcopy(cfg.bmax, &bbMax.x);

    rcCalcGridSize(cfg.bmin, cfg.bmax, cfg.cs, &cfg.width, &cfg.height);

    rcContext ctx;

    if (config.tileSize)
    {
        if (!computeTiledNavMesh(verts, tris, cfg, intermediates, triareas))
        {
            Log("Unable to create tiled navmesh");
        }
        
    }
    else 
    {
        //
        // Step 2. Rasterize input polygon soup.
        //
    
        // Allocate voxel heightfield where we rasterize our input data to.
        intermediates.m_solid = rcAllocHeightfield();
        if (!intermediates.m_solid)
        {
            Log("buildNavigation: Out of memory 'solid'.");
            return ;
        }
        if (!rcCreateHeightfield(&ctx, *intermediates.m_solid, cfg.width, cfg.height, cfg.bmin, cfg.bmax, cfg.cs, cfg.ch))
        {
            Log("buildNavigation: Could not create solid heightfield.");
            return ;
        }

        rcRasterizeTriangles(&ctx, verts.data(), nverts, tris.data(), triareas.data(), ntris, *intermediates.m_solid, cfg.walkableClimb);

        //
        // Step 3. Filter walkables surfaces.
        //
    
        // Once all geoemtry is rasterized, we do initial pass of filtering to
        // remove unwanted overhangs caused by the conservative rasterization
        // as well as filter spans where the character cannot possibly stand.
    
        rcFilterLowHangingWalkableObstacles(&ctx, cfg.walkableClimb, *intermediates.m_solid);
        rcFilterLedgeSpans(&ctx, cfg.walkableHeight, cfg.walkableClimb, *intermediates.m_solid);
        rcFilterWalkableLowHeightSpans(&ctx, cfg.walkableHeight, *intermediates.m_solid);
    

        //
        // Step 4. Partition walkable surface to simple regions.
        // 

        // Compact the heightfield so that it is faster to handle from now on.
        // This will result more cache coherent data as well as the neighbours
        // between walkable cells will be calculated.
    
        intermediates.m_chf = rcAllocCompactHeightfield();
        if (!intermediates.m_chf)
        {
            Log("buildNavigation: Out of memory 'chf'.");
            return ;
        }
    
        if (!rcBuildCompactHeightfield(&ctx, cfg.walkableHeight, cfg.walkableClimb, *intermediates.m_solid, *intermediates.m_chf))
        {
            Log("buildNavigation: Could not build compact data.");
            return ;
        }
    
        if (!keepInterResults)
        {
            rcFreeHeightField(intermediates.m_solid);
            intermediates.m_solid = nullptr;
        }
        
        // Erode the walkable area by agent radius.
        if (!rcErodeWalkableArea(&ctx, cfg.walkableRadius, *intermediates.m_chf))
        {
            Log("buildNavigation: Could not erode.");
            return ;
        }

        // Prepare for region partitioning, by calculating Distance field along the walkable surface.
        if (!rcBuildDistanceField(&ctx, *intermediates.m_chf))
        {
            Log("buildNavigation: Could not build Distance field.");
            return ;
        }

        // Partition the walkable surface into simple regions without holes.
        if (!rcBuildRegions(&ctx, *intermediates.m_chf, 0, cfg.minRegionArea, cfg.mergeRegionArea))
        {
            Log("buildNavigation: Could not build regions.");
            return ;
        }
    
        //
        // Step 5. Trace and simplify region contours.
        //
    
        // Create contours.
    
        intermediates.m_cset = rcAllocContourSet();
        if (!intermediates.m_cset)
        {
            Log("buildNavigation: Out of memory 'cset'.");
            return ;
        }
        if (!rcBuildContours(&ctx, *intermediates.m_chf, cfg.maxSimplificationError, cfg.maxEdgeLen, *intermediates.m_cset))
        {
            Log("buildNavigation: Could not create contours.");
            return ;
        }
    
        //
        // Step 6. Build polygons mesh from contours.
        //

        m_pmesh = rcAllocPolyMesh();
        if (!m_pmesh)
        {
            Log("buildNavigation: Out of memory 'pmesh'.");
            return ;
        }
        if (!rcBuildPolyMesh(&ctx, *intermediates.m_cset, cfg.maxVertsPerPoly, *m_pmesh))
        {
            Log("buildNavigation: Could not triangulate contours.");
            return ;
        }
    
        //
        // Step 7. Create detail mesh which allows to access approximate height on each polygon.
        //
        m_dmesh = rcAllocPolyMeshDetail();
        if (!m_dmesh)
        {
            Log("buildNavigation: Out of memory 'pmdtl'.");
            return ;
        }

        if (!rcBuildPolyMeshDetail(&ctx, *m_pmesh, *intermediates.m_chf, cfg.detailSampleDist, cfg.detailSampleMaxError, *m_dmesh))
        {
            Log("buildNavigation: Could not build detail mesh.");
            return ;
        }

        if (!keepInterResults)
        {
            rcFreeCompactHeightfield(intermediates.m_chf);
            intermediates.m_chf = nullptr;
            rcFreeContourSet(intermediates.m_cset);
            intermediates.m_cset = nullptr;
        }
    
        //
        // (Optional) Step 8. Create Detour data from Recast poly mesh.
        //
    
        // Only build the detour navmesh if we do not exceed the limit.
        if (cfg.maxVertsPerPoly <= DT_VERTS_PER_POLYGON)
        {
            rcPolyMesh* pmesh = m_pmesh;
            rcPolyMeshDetail* dmesh = m_dmesh;

            int navDataSize = 0;

            // Update poly flags from areas.
            for (int i = 0; i < pmesh->npolys; ++i)
            {
                if (pmesh->areas[i] == RC_WALKABLE_AREA)
                {
                    pmesh->areas[i] = 0;
                }   
                if (pmesh->areas[i] == 0)
                {
                    pmesh->flags[i] = 1;
                }
            }

            dtNavMeshCreateParams params;
            memset(&params, 0, sizeof(params));
            params.verts = pmesh->verts;
            params.vertCount = pmesh->nverts;
            params.polys = pmesh->polys;
            params.polyAreas = pmesh->areas;
            params.polyFlags = pmesh->flags;
            params.polyCount = pmesh->npolys;
            params.nvp = pmesh->nvp;
            params.detailMeshes = dmesh->meshes;
            params.detailVerts = dmesh->verts;
            params.detailVertsCount = dmesh->nverts;
            params.detailTris = dmesh->tris;
            params.detailTriCount = dmesh->ntris;
            // optional connection between areas
            params.offMeshConVerts = 0;//geom->getOffMeshConnectionVerts();
            params.offMeshConRad = 0;//geom->getOffMeshConnectionRads();
            params.offMeshConDir = 0;//geom->getOffMeshConnectionDirs();
            params.offMeshConAreas = 0;//geom->getOffMeshConnectionAreas();
            params.offMeshConFlags = 0;//geom->getOffMeshConnectionFlags();
            params.offMeshConUserID = 0;//geom->getOffMeshConnectionId();
            params.offMeshConCount = 0;//geom->getOffMeshConnectionCount();
            params.walkableHeight = config.walkableHeight;
            params.walkableRadius = config.walkableRadius;
            params.walkableClimb = config.walkableClimb;
            rcVcopy(params.bmin, pmesh->bmin);
            rcVcopy(params.bmax, pmesh->bmax);
            params.cs = cfg.cs;
            params.ch = cfg.ch;
            params.buildBvTree = true;
        
            if (!dtCreateNavMeshData(&params, &m_navData, &navDataSize))
            {
                Log("Could not build Detour navmesh.");
                return ;
            }
        
            m_navMesh = dtAllocNavMesh();
            if (!m_navMesh)
            {
                Log("Could not create Detour navmesh");
                return ;
            }
        
            dtStatus status;
        
            status = m_navMesh->init(m_navData, navDataSize, DT_TILE_FREE_DATA);
            if (dtStatusFailed(status))
            {
                Log("Could not init Detour navmesh");
                return ;
            }
        }
    }

    // common path for tile or untiled nav mesh
    if (m_navMesh)
    {
        m_navQuery = dtAllocNavMeshQuery();
        if (!m_navQuery)
        {
            dtFreeNavMesh(m_navMesh);
            m_navMesh = nullptr;
            Log("Could not allocate Navmesh query");
            return;
        }
        dtStatus status = m_navQuery->init(m_navMesh, 2048);
        if (dtStatusFailed(status))
        {
            dtFreeNavMesh(m_navMesh);
            m_navMesh = nullptr;
            Log("Could not init Detour navmesh query");
            return;
        }
    }
}

static const int NAVMESHSET_MAGIC = 'M'<<24 | 'S'<<16 | 'E'<<8 | 'T'; //'MSET';
static const int NAVMESHSET_VERSION = 1;
static const int TILECACHESET_MAGIC = 'T'<<24 | 'S'<<16 | 'E'<<8 | 'T'; //'TSET';
static const int TILECACHESET_VERSION = 1;

struct RecastHeader
{
    int magic;
    int version;
    int numTiles;
};

struct TileCacheSetHeader
{
    dtNavMeshParams meshParams;
    dtTileCacheParams cacheParams;
};

struct TileCacheTileHeader
{
    dtCompressedTileRef tileRef;
    int dataSize;
};

struct NavMeshSetHeader
{
    dtNavMeshParams params;
};

struct NavMeshTileHeader
{
    dtTileRef tileRef;
    int dataSize;
};

void NavMesh::buildFromNavmeshData(NavmeshData* navmeshData)
{
    destroy();
    unsigned char* bits = (unsigned char*)navmeshData->dataPointer;

    // Read header.
    RecastHeader recastHeader;
    size_t readLen = sizeof(RecastHeader);
    memcpy(&recastHeader, bits, readLen);
    bits += readLen;

    if (recastHeader.magic == NAVMESHSET_MAGIC)
    {
        NavMeshSetHeader header;
        size_t readLen = sizeof(NavMeshSetHeader);
        memcpy(&header, bits, readLen);
        bits += readLen;

        if (recastHeader.version != NAVMESHSET_VERSION)
        {
            return ;
        }

        dtNavMesh* mesh = dtAllocNavMesh();
        if (!mesh)
        {
            return ;
        }
        dtStatus status = mesh->init(&header.params);
        if (dtStatusFailed(status))
        {
            return ;
        }

        // Read tiles.
        for (int i = 0; i < recastHeader.numTiles; ++i)
        {
            NavMeshTileHeader tileHeader;
            readLen = sizeof(tileHeader);
            memcpy(&tileHeader, bits, readLen);
            bits += readLen;

            if (!tileHeader.tileRef || !tileHeader.dataSize)
            {
                break;
            }

            unsigned char* data = (unsigned char*)dtAlloc(tileHeader.dataSize, DT_ALLOC_PERM);
            if (!data)
            {
                break;
            }

            readLen = tileHeader.dataSize;
            memcpy(data, bits, readLen);
            bits += readLen;

            mesh->addTile(data, tileHeader.dataSize, DT_TILE_FREE_DATA, tileHeader.tileRef, 0);
        }

        m_navMesh = mesh;
    }
    else if (recastHeader.magic == TILECACHESET_MAGIC)
    {
        if (recastHeader.version != TILECACHESET_VERSION)
        {
            return;
        }
        
        TileCacheSetHeader header;
        size_t readLen = sizeof(TileCacheSetHeader);
        memcpy(&header, bits, readLen);
        bits += readLen;

        m_navMesh = dtAllocNavMesh();
        if (!m_navMesh)
        {
            return;
        }
        dtStatus status = m_navMesh->init(&header.meshParams);
        if (dtStatusFailed(status))
        {
            return;
        }

        m_tileCache = dtAllocTileCache();
        if (!m_tileCache)
        {
            return;
        }
        status = m_tileCache->init(&header.cacheParams, &m_talloc, &m_tcomp, &m_tmproc);
        if (dtStatusFailed(status))
        {
            return;
        }
            
        // Read tiles.
        for (int i = 0; i < recastHeader.numTiles; ++i)
        {
            TileCacheTileHeader tileHeader;
            size_t readLen = sizeof(tileHeader);
            memcpy(&tileHeader, bits, readLen);
            bits += readLen;

            if (!tileHeader.tileRef || !tileHeader.dataSize)
            {
                break;
            }

            unsigned char* data = (unsigned char*)dtAlloc(tileHeader.dataSize, DT_ALLOC_PERM);
            if (!data)
            {
                break;
            }

            memset(data, 0, tileHeader.dataSize);

            readLen = tileHeader.dataSize;
            memcpy(data, bits, readLen);
            bits += readLen;
            
            dtCompressedTileRef tile = 0;
            dtStatus addTileStatus = m_tileCache->addTile(data, tileHeader.dataSize, DT_COMPRESSEDTILE_FREE_DATA, &tile);
            if (dtStatusFailed(addTileStatus))
            {
                dtFree(data);
            }

            if (tile)
            {
                m_tileCache->buildNavMeshTile(tile, m_navMesh);
            }
        }
    }
    m_navQuery = dtAllocNavMeshQuery();
    if (!m_navQuery)
    {
        dtFreeNavMesh(m_navMesh);
        m_navMesh = nullptr;
        Log("Load navmesh data: Could not allocate Navmesh query");
        return ;
    }
    dtStatus status = m_navQuery->init(m_navMesh, 2048);
    if (dtStatusFailed(status))
    {
        dtFreeNavMesh(m_navMesh);
        m_navMesh = nullptr;
        Log("Load navmesh data: Could not init Detour navmesh query");
        return ;
    }
}

NavmeshData NavMesh::getNavmeshData() const
{
    if (!m_navMesh)
    {
        return {0, 0};
    }
    unsigned char* bits = nullptr;
    size_t bitsSize = 0;
    const dtNavMesh* mesh = m_navMesh;

    if (m_tileCache)
    {
        // tilecache set
        // Store header.
        RecastHeader recastHeader;
        TileCacheSetHeader header;
        recastHeader.magic = TILECACHESET_MAGIC;
        recastHeader.version = TILECACHESET_VERSION;
        recastHeader.numTiles = 0;
        for (int i = 0; i < m_tileCache->getTileCount(); ++i)
        {
            const dtCompressedTile* tile = m_tileCache->getTile(i);
            if (!tile || !tile->header || !tile->dataSize) continue;
            recastHeader.numTiles++;
        }
        memcpy(&header.cacheParams, m_tileCache->getParams(), sizeof(dtTileCacheParams));
        memcpy(&header.meshParams, m_navMesh->getParams(), sizeof(dtNavMeshParams));

        bits = (unsigned char*)realloc(bits, bitsSize + sizeof(RecastHeader));
        memcpy(&bits[bitsSize], &recastHeader, sizeof(RecastHeader));
        bitsSize += sizeof(RecastHeader);
        
        bits = (unsigned char*)realloc(bits, bitsSize + sizeof(TileCacheSetHeader));
        memcpy(&bits[bitsSize], &header, sizeof(TileCacheSetHeader));
        bitsSize += sizeof(TileCacheSetHeader);

        // Store tiles.
        for (int i = 0; i < m_tileCache->getTileCount(); ++i)
        {
            const dtCompressedTile* tile = m_tileCache->getTile(i);
            if (!tile || !tile->header || !tile->dataSize) continue;

            TileCacheTileHeader tileHeader;
            tileHeader.tileRef = m_tileCache->getTileRef(tile);
            tileHeader.dataSize = tile->dataSize;

            bits = (unsigned char*)realloc(bits, bitsSize + sizeof(tileHeader));
            memcpy(&bits[bitsSize], &tileHeader, sizeof(tileHeader));
            bitsSize += sizeof(tileHeader);

            bits = (unsigned char*)realloc(bits, bitsSize + tile->dataSize);
            memcpy(&bits[bitsSize], tile->data, tile->dataSize);
            bitsSize += tile->dataSize;
        }
    }
    else
    {
        // Mesh set
        // Store header.
        RecastHeader recastHeader;
        NavMeshSetHeader header;
        recastHeader.magic = NAVMESHSET_MAGIC;
        recastHeader.version = NAVMESHSET_VERSION;
        recastHeader.numTiles = 0;
        for (int i = 0; i < mesh->getMaxTiles(); ++i)
        {
            const dtMeshTile* tile = mesh->getTile(i);
            if (!tile || !tile->header || !tile->dataSize) continue;
            recastHeader.numTiles++;
        }
        memcpy(&header.params, mesh->getParams(), sizeof(dtNavMeshParams));
        bits = (unsigned char*)realloc(bits, bitsSize + sizeof(RecastHeader));
        memcpy(&bits[bitsSize], &recastHeader, sizeof(RecastHeader));
        bitsSize += sizeof(RecastHeader);

        bits = (unsigned char*)realloc(bits, bitsSize + sizeof(NavMeshSetHeader));
        memcpy(&bits[bitsSize], &header, sizeof(NavMeshSetHeader));
        bitsSize += sizeof(NavMeshSetHeader);

        // Store tiles.
        for (int i = 0; i < mesh->getMaxTiles(); ++i)
        {
            const dtMeshTile* tile = mesh->getTile(i);
            if (!tile || !tile->header || !tile->dataSize) continue;

            NavMeshTileHeader tileHeader;
            tileHeader.tileRef = mesh->getTileRef(tile);
            tileHeader.dataSize = tile->dataSize;

            bits = (unsigned char*)realloc(bits, bitsSize + sizeof(tileHeader));
            memcpy(&bits[bitsSize], &tileHeader, sizeof(tileHeader));
            bitsSize += sizeof(tileHeader);

            bits = (unsigned char*)realloc(bits, bitsSize + tile->dataSize);
            memcpy(&bits[bitsSize], tile->data, tile->dataSize);
            bitsSize += tile->dataSize;
        }
    }

    NavmeshData navmeshData;
    navmeshData.dataPointer = bits;
    navmeshData.size = int(bitsSize);
    return navmeshData;
}

void NavMesh::freeNavmeshData(NavmeshData* navmeshData)
{
    free(navmeshData->dataPointer);
}

void NavMesh::navMeshPoly(DebugNavMesh& debugNavMesh, const dtNavMesh& mesh, dtPolyRef ref)
{
    const dtMeshTile* tile = 0;
    const dtPoly* poly = 0;
    if (dtStatusFailed(mesh.getTileAndPolyByRef(ref, &tile, &poly)))
        return;

    const unsigned int ip = (unsigned int)(poly - tile->polys);

    if (poly->getType() == DT_POLYTYPE_OFFMESH_CONNECTION)
    {
        /*
        If we want to display links (teleport) between navmesh or inside a navmesh
        this code will be usefull for debug output.
        
        dtOffMeshConnection* con = &tile->offMeshCons[ip - tile->header->offMeshBase];

        dd->begin(DU_DRAW_LINES, 2.0f);

        // Connection arc.
        duAppendArc(dd, con->pos[0],con->pos[1],con->pos[2], con->pos[3],con->pos[4],con->pos[5], 0.25f,
                    (con->flags & 1) ? 0.6f : 0.0f, 0.6f, c);
        
        dd->end();
        */
    }
    else
    {
        const dtPolyDetail* pd = &tile->detailMeshes[ip];

        for (int i = 0; i < pd->triCount; ++i)
        {
            const unsigned char* t = &tile->detailTris[(pd->triBase+i)*4];
            Triangle triangle;
            float *pf;

            for (int j = 0; j < 3; ++j)
            {
                if (t[j] < poly->vertCount)
                {
                    pf = &tile->verts[poly->verts[t[j]]*3];
                }
                else
                {
                    pf = &tile->detailVerts[(pd->vertBase+t[j]-poly->vertCount)*3];
                }

                triangle.mPoint[2-j] = Vec3(pf[0], pf[1], pf[2]);
            }
            debugNavMesh.mTriangles.push_back(triangle);
        }
    }
}

void NavMesh::navMeshPolysWithFlags(DebugNavMesh& debugNavMesh, const dtNavMesh& mesh, const unsigned short polyFlags)
{
    for (int i = 0; i < mesh.getMaxTiles(); ++i)
    {
        const dtMeshTile* tile = mesh.getTile(i);
        if (!tile->header)
        {
            continue;
        }
        dtPolyRef base = mesh.getPolyRefBase(tile);

        for (int j = 0; j < tile->header->polyCount; ++j)
        {
            const dtPoly* p = &tile->polys[j];
            if ((p->flags & polyFlags) == 0)
            {
                continue;
            }
            navMeshPoly(debugNavMesh, mesh, base|(dtPolyRef)j);
        }
    }
}

DebugNavMesh NavMesh::getDebugNavMesh()
{
    DebugNavMesh debugNavMesh;
    navMeshPolysWithFlags(debugNavMesh, *m_navMesh,  0xFFFF);
    return debugNavMesh;
}

Vec3 NavMesh::getClosestPoint(const Vec3& position)
{
    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    dtPolyRef polyRef;

    Vec3 pos(position.x, position.y, position.z);
    m_navQuery->findNearestPoly(&pos.x, &m_defaultQueryExtent.x, &filter, &polyRef, 0);


    bool posOverlay;
    Vec3 resDetour;
    dtStatus status = m_navQuery->closestPointOnPoly(polyRef, &pos.x, &resDetour.x, &posOverlay);
    
    if (dtStatusFailed(status))
    {
        return Vec3(0.f, 0.f, 0.f);
    }
    return Vec3(resDetour.x, resDetour.y, resDetour.z);
}

Vec3 NavMesh::getRandomPointAround(const Vec3& position, float maxRadius)
{
    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    dtPolyRef polyRef;

    Vec3 pos(position.x, position.y, position.z);

    m_navQuery->findNearestPoly(&pos.x, &m_defaultQueryExtent.x, &filter, &polyRef, 0);

    dtPolyRef randomRef;
    Vec3 resDetour;
    dtStatus status = m_navQuery->findRandomPointAroundCircle(polyRef, &position.x, maxRadius,
                                         &filter, r01,
                                         &randomRef, &resDetour.x);
    if (dtStatusFailed(status))
    {
        return Vec3(0.f, 0.f, 0.f);
    }

    return Vec3(resDetour.x, resDetour.y, resDetour.z);
}

Vec3 NavMesh::moveAlong(const Vec3& position, const Vec3& destination)
{
    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    dtPolyRef polyRef;

    Vec3 pos(position.x, position.y, position.z);
    Vec3 dest(destination.x, destination.y, destination.z);

    m_navQuery->findNearestPoly(&pos.x, &m_defaultQueryExtent.x, &filter, &polyRef, 0);

    Vec3 resDetour;
    dtPolyRef visitedPoly[128];
    int visitedPolyCount;
    dtStatus status = m_navQuery->moveAlongSurface(polyRef, &pos.x, &dest.x,
        &filter,
        &resDetour.x, visitedPoly, &visitedPolyCount, sizeof(visitedPoly)/sizeof(dtPolyRef));
    if (dtStatusFailed(status))
    {
        return Vec3(0.f, 0.f, 0.f);
    }
    return Vec3(resDetour.x, resDetour.y, resDetour.z);
}

NavPath NavMesh::computePath(const Vec3& start, const Vec3& end) const
{
    NavPath navpath;
    static const int MAX_POLYS = 256;
    float straightPath[MAX_POLYS*3];

    dtPolyRef startRef;
    dtPolyRef endRef;

    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    Vec3 posStart(start.x, start.y, start.z);
    Vec3 posEnd(end.x, end.y, end.z);

    m_navQuery->findNearestPoly(&posStart.x, &m_defaultQueryExtent.x, &filter, &startRef, 0);
    m_navQuery->findNearestPoly(&posEnd.x, &m_defaultQueryExtent.x, &filter, &endRef, 0);

    dtPolyRef polys[MAX_POLYS];
    int npolys;

    m_navQuery->findPath(startRef, endRef, &posStart.x, &posEnd.x, &filter, polys, &npolys, MAX_POLYS);
    int mNstraightPath = 0;
    if (npolys)
    {
        unsigned char straightPathFlags[MAX_POLYS];
        dtPolyRef straightPathPolys[MAX_POLYS];
        int straightPathOptions;
        bool posOverPoly;
        Vec3 closestEnd = posEnd;

        if (polys[npolys-1] != endRef)
        {
            m_navQuery->closestPointOnPoly(polys[npolys-1], &end.x, &closestEnd.x, &posOverPoly );
        }
        straightPathOptions = 0;
        m_navQuery->findStraightPath(&posStart.x, &closestEnd.x, polys, npolys,
            straightPath, straightPathFlags,
            straightPathPolys, &mNstraightPath, MAX_POLYS, straightPathOptions);

        navpath.mPoints.resize(mNstraightPath);
        for (int i = 0;i<mNstraightPath;i++)
        {
            navpath.mPoints[i] = Vec3(straightPath[i*3], straightPath[i*3+1], straightPath[i*3+2]);
        }
    }
    return navpath;
}

dtObstacleRef* NavMesh::addCylinderObstacle(const Vec3& position, float radius, float height)
{
    dtObstacleRef ref(-1);
    if (!m_tileCache)
    {
        return nullptr;
    }
    
    m_tileCache->addObstacle(&position.x, radius, height, &ref);
    m_obstacles.push_back(ref);
    return &m_obstacles.back();
}

dtObstacleRef* NavMesh::addBoxObstacle(const Vec3& position, const Vec3& extent, float angle)
{
    dtObstacleRef ref(-1);
    if (!m_tileCache)
    {
        return nullptr;
    }
    m_tileCache->addBoxObstacle(&position.x, &extent.x, angle, &ref);
    m_obstacles.push_back(ref);
    return &m_obstacles.back();
}

void NavMesh::removeObstacle(dtObstacleRef* obstacle)
{
    if (!m_tileCache || !obstacle || *obstacle == -1)
    {
        return;
    }
    m_tileCache->removeObstacle(*obstacle);
    auto iter = std::find(m_obstacles.begin(), m_obstacles.end(), *obstacle);
    if (iter != m_obstacles.end())
    {
        m_obstacles.erase(iter);
    }
}

void NavMesh::update()
{
    if (!m_navMesh || !m_tileCache)
    {
        return;
    }
    m_tileCache->update(0, m_navMesh);
}

Crowd::Crowd(const int maxAgents, const float maxAgentRadius, dtNavMesh* nav) : m_defaultQueryExtent(1.f)
{
    m_crowd = dtAllocCrowd();
    m_crowd->init(maxAgents, maxAgentRadius, nav);
}

void Crowd::destroy()
{
    if (m_crowd)
    {
        dtFreeCrowd(m_crowd);
        m_crowd = NULL;
    }
}

int Crowd::addAgent(const Vec3& pos, const dtCrowdAgentParams* params)
{
    return m_crowd->addAgent(&pos.x, params);
}

void Crowd::removeAgent(const int idx)
{
    m_crowd->removeAgent(idx);
}

void Crowd::update(const float dt)
{
    m_crowd->update(dt, NULL);
}

Vec3 Crowd::getAgentPosition(int idx)
{
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    return Vec3(agent->npos[0], agent->npos[1], agent->npos[2]);
}

Vec3 Crowd::getAgentVelocity(int idx)
{
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    return Vec3(agent->vel[0], agent->vel[1], agent->vel[2]);
}

Vec3 Crowd::getAgentNextTargetPath(int idx)
{
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    return Vec3(agent->cornerVerts[0], agent->cornerVerts[1], agent->cornerVerts[2]);
}

int Crowd::getAgentState(int idx)
{
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    return agent->state;
}

bool Crowd::overOffmeshConnection(int idx)
{
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    const float triggerRadius = agent->params.radius * 2.25f;
    if (!agent->ncorners) return false;
    const bool offMeshConnection = (agent->cornerFlags[agent->ncorners-1] & DT_STRAIGHTPATH_OFFMESH_CONNECTION) ? true : false;
    if (offMeshConnection)
    {
        const float distSq = dtVdist2DSqr(agent->npos, &agent->cornerVerts[(agent->ncorners-1)*3]);
        if (distSq < triggerRadius * triggerRadius)
        {
            return true;
        }
    }
    return false;
}

void Crowd::agentGoto(int idx, const Vec3& destination)
{
    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    dtPolyRef polyRef;

    Vec3 pos(destination.x, destination.y, destination.z);
    m_crowd->getNavMeshQuery()->findNearestPoly(&pos.x, &m_defaultQueryExtent.x, &filter, &polyRef, 0);

    m_crowd->requestMoveTarget(idx, polyRef, &pos.x);
}

void Crowd::agentTeleport(int idx, const Vec3& destination)
{
    if (idx < 0 || idx > m_crowd->getAgentCount())
    {
        return;
    }

    dtQueryFilter filter;
    filter.setIncludeFlags(0xffff);
    filter.setExcludeFlags(0);

    dtPolyRef polyRef = 0;

    Vec3 pos(destination.x, destination.y, destination.z);
    m_crowd->getNavMeshQuery()->findNearestPoly(&pos.x, &m_defaultQueryExtent.x, &filter, &polyRef, 0);

    dtCrowdAgent* ag = m_crowd->getEditableAgent(idx);        

    float nearest[3];
    dtVcopy(nearest, &pos.x);
    
    ag->corridor.reset(polyRef, nearest);
    ag->boundary.reset();
    ag->partial = false;

    ag->topologyOptTime = 0;
    ag->targetReplanTime = 0;
    ag->nneis = 0;
    
    dtVset(ag->dvel, 0,0,0);
    dtVset(ag->nvel, 0,0,0);
    dtVset(ag->vel, 0,0,0);
    dtVcopy(ag->npos, nearest);
    
    ag->desiredSpeed = 0;

    if (polyRef)
        ag->state = DT_CROWDAGENT_STATE_WALKING;
    else
        ag->state = DT_CROWDAGENT_STATE_INVALID;
    
    ag->targetState = DT_CROWDAGENT_TARGET_NONE;
}

dtCrowdAgentParams Crowd::getAgentParameters(const int idx)
{
    dtCrowdAgentParams params;
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);
    params = agent->params;
    return params;
}

void Crowd::setAgentParameters(const int idx, const dtCrowdAgentParams* params)
{
    m_crowd->updateAgentParameters(idx, params);
}

NavPath Crowd::getCorners(const int idx)
{
    NavPath navpath;
    const dtCrowdAgent* agent = m_crowd->getAgent(idx);

    const float* pos = agent->cornerVerts;
    navpath.mPoints.resize(agent->ncorners);
    for (int i = 0; i < agent->ncorners; i++)
    {
        navpath.mPoints[i] = Vec3(pos[i*3], pos[i*3+1], pos[i*3+2]);
    }
    return navpath;
}

void RecastConfigHelper::destroy() {}

void RecastConfigHelper::setBMAX(rcConfig& cfg, float x, float y, float z) {
    cfg.bmax[0] = x;
    cfg.bmax[1] = y;
    cfg.bmax[2] = z;
}

void RecastConfigHelper::setBMIN(rcConfig& cfg, float x, float y, float z) {
    cfg.bmin[0] = x;
    cfg.bmin[1] = y;
    cfg.bmin[2] = z;
}

Vec3 RecastConfigHelper::getBMAX(rcConfig& cfg) {
    return Vec3(cfg.bmax[0], cfg.bmax[1], cfg.bmax[2]);
}

Vec3 RecastConfigHelper::getBMIN(rcConfig& cfg) {
    return Vec3(cfg.bmin[0], cfg.bmin[1], cfg.bmin[2]);
}