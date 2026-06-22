cmake_minimum_required(VERSION 3.13 FATAL_ERROR)
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)

FIND_PACKAGE(Python3)
set(PYTHON ${Python3_EXECUTABLE} CACHE STRING "Python path")
set(EMSCRIPTEN_ROOT $ENV{EMSDK}/upstream/emscripten CACHE STRING "Emscripten path")
set(CMAKE_TOOLCHAIN_FILE ${EMSCRIPTEN_ROOT}/cmake/Modules/Platform/Emscripten.cmake)
set(WEBIDL_BINDER_SCRIPT ${EMSCRIPTEN_ROOT}/tools/webidl_binder.py)
set(RECAST_IDL_FILE ${CMAKE_CURRENT_SOURCE_DIR}/Sources/recast/recast.idl)
set(RECASTAPI_HEADER_FILE ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/src/recastjs.h)
set(RECAST_HEADER_FILE ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Recast/Include/Recast.h)
set(NAVMESHQUERY_HEADER_FILE ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Detour/Include/DetourNavMeshQuery.h)
set(RECAST_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/src/)
set(RECAST_ONLOAD_FILE ${CMAKE_CURRENT_SOURCE_DIR}/recastjs/onload.js)

project (recastjs)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file(GLOB_RECURSE SRC_FILES
    ${CMAKE_SOURCE_DIR}/recastnavigation/src/*.h
    ${CMAKE_SOURCE_DIR}/recastnavigation/src/*.cpp
)
file(GLOB RECASTDETOUR_FILES
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourAlloc.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourAssert.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourCommon.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourNavMesh.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourNavMeshBuilder.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourNavMeshQuery.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Detour/Source/DetourNode.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourCrowd.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourLocalBoundary.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourObstacleAvoidance.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourPathCorridor.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourPathQueue.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourCrowd/Source/DetourProximityGrid.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourTileCache/Source/DetourTileCache.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/DetourTileCache/Source/DetourTileCacheBuilder.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/Recast.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastAlloc.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastArea.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastAssert.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastContour.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastFilter.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastLayers.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastMesh.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastMeshDetail.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastRasterization.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/Recast/Source/RecastRegion.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/RecastDemo/Source/ChunkyTriMesh.cpp
    ${CMAKE_SOURCE_DIR}/recastnavigation/RecastDemo/Contrib/fastlz/fastlz.c
)

include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/src
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Detour/Include
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/DetourCrowd/Include
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/DetourTileCache/Include
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Recast/Include
  ${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/RecastDemo/Include
)

SET(EXE_NAME "recast")

ADD_LIBRARY(${EXE_NAME} ${SRC_FILES} ${RECASTDETOUR_FILES})

# Build Release by default
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build Type")

# Default is 64*1024*1024 = 64MB
set(TOTAL_MEMORY 67108864 CACHE STRING "Total Memory")

# Enable for resizable heap, with some amount of slowness
set(ALLOW_MEMORY_GROWTH 0 CACHE STRING "Allow Memory Growth")

set(EMCC_ARGS
  -flto
  --post-js glue.js
  --post-js ${RECAST_ONLOAD_FILE}
  -O3
  -s ALLOW_MEMORY_GROWTH=${ALLOW_MEMORY_GROWTH}
  -s ALLOW_TABLE_GROWTH=1
  -s EXPORTED_FUNCTIONS=["_malloc","_free"]
  -s EXPORTED_RUNTIME_METHODS=["UTF8ToString"]
  -s EXTRA_EXPORTED_RUNTIME_METHODS=["addFunction"]
  -s EXPORT_NAME="Recast"
  -s MODULARIZE=1
  -s NO_EXIT_RUNTIME=1
  -s NO_FILESYSTEM=1
  -s TOTAL_MEMORY=${TOTAL_MEMORY})

if(${CLOSURE})
  # Ignore closure errors about the bullet Node class
  # (Node is a DOM thing too)
  LIST(APPEND EMCC_ARGS
    --closure 1
    -s IGNORE_CLOSURE_COMPILER_ERRORS=1)
else()
  LIST(APPEND EMCC_ARGS
    -s NO_DYNAMIC_EXECUTION=1)
endif()

set(EMCC_JS_ARGS ${EMCC_ARGS}
  -s AGGRESSIVE_VARIABLE_ELIMINATION=1
  -s ELIMINATE_DUPLICATE_FUNCTIONS=1
  -s LEGACY_VM_SUPPORT=1
  -s SINGLE_FILE=1
  -s FILESYSTEM=0
  -s ENVIRONMENT='web')

set(EMCC_JS_ES6ARGS ${EMCC_ARGS}
  -s EXPORT_ES6=1 
  -s MODULARIZE=1 
  -s SINGLE_FILE=1
  -s FILESYSTEM=0
  -s ENVIRONMENT='web')

set(EMCC_WASM_ARGS ${EMCC_ARGS}
  -s BINARYEN_IGNORE_IMPLICIT_TRAPS=1
  -s WASM=1)

set(EMCC_GLUE_ARGS
  -c
  -I${RECAST_SRC_DIR}
  -I${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Detour/Include
  -I${CMAKE_CURRENT_SOURCE_DIR}/recastnavigation/Recast/Include
  -include${RECASTAPI_HEADER_FILE}
  -include${RECAST_HEADER_FILE}
  -include${NAVMESHQUERY_HEADER_FILE}
  )

#######################################
add_custom_command(
  OUTPUT glue.cpp glue.js
  BYPRODUCTS parser.out WebIDLGrammar.pkl
  COMMAND ${PYTHON} ${WEBIDL_BINDER_SCRIPT} ${RECAST_IDL_FILE} glue
  DEPENDS ${RECAST_IDL_FILE}
  COMMENT "Generating ${EXE_NAME} bindings"
  VERBATIM)
add_custom_command(
  OUTPUT glue.o
  COMMAND emcc glue.cpp ${EMCC_GLUE_ARGS} -o glue.o
  DEPENDS glue.cpp ${RECASTAPI_HEADER_FILE} ${RECAST_HEADER_FILE} ${NAVMESHQUERY_HEADER_FILE}
  COMMENT "Building ${EXE_NAME} bindings"
  VERBATIM)
add_custom_target(${EXE_NAME}-bindings ALL DEPENDS glue.js glue.o)

#######################################
# full UMD
add_custom_command(
  OUTPUT ${EXE_NAME}.js
  COMMAND emcc glue.o lib${EXE_NAME}.a ${EMCC_JS_ARGS} -o ${EXE_NAME}.js
  DEPENDS ${EXE_NAME}-bindings ${EXE_NAME} ${RECAST_ONLOAD_FILE}
  COMMENT "Building ${EXE_NAME} javascript"
  VERBATIM)
add_custom_target(${EXE_NAME}-javascript ALL DEPENDS ${EXE_NAME}.js)

#######################################
add_custom_command(
  OUTPUT ${EXE_NAME}.wasm.js ${EXE_NAME}.wasm.wasm
  COMMAND emcc glue.o lib${EXE_NAME}.a ${EMCC_WASM_ARGS} -o ${EXE_NAME}.wasm.js
  DEPENDS ${EXE_NAME}-bindings ${EXE_NAME} ${RECAST_ONLOAD_FILE}
  COMMENT "Building ${EXE_NAME} webassembly"
  VERBATIM)
add_custom_target(${EXE_NAME}-wasm ALL DEPENDS ${EXE_NAME}.wasm.js ${EXE_NAME}.wasm.wasm)