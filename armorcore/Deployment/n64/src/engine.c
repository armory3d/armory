#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmodel.h>

#include "../types.h"
#include "models.h"

void engine_init(void)
{
    debug_init_isviewer();
    debug_init_usblog();

    asset_init_compression(2);
    dfs_init(DFS_DEFAULT_LOCATION);

    display_init(RESOLUTION_320x240, DEPTH_16_BPP, FB_COUNT, GAMMA_NONE, FILTERS_RESAMPLE_ANTIALIAS);

    rdpq_init();

    t3d_init((T3DInitParams){});
    rdpq_text_register_font(FONT_BUILTIN_DEBUG_MONO, rdpq_font_load_builtin(FONT_BUILTIN_DEBUG_MONO));

    models_init();
}

void engine_shutdown(void)
{
    models_shutdown();
    t3d_destroy();
}
