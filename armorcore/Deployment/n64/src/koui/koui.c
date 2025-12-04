#include "koui.h"
#include "../data/fonts.h"
#include <libdragon.h>
#include <stdlib.h>
#include <string.h>

// Static label pool - avoids malloc() in hot paths
static KouiLabel g_label_pool[KOUI_MAX_LABELS];
static uint8_t g_label_pool_used = 0;

// Render list - pointers to labels that should be rendered
static KouiLabel* g_render_list[KOUI_MAX_LABELS];
static uint8_t g_render_count = 0;

// Default font ID for rendering
static uint8_t g_default_font_rdpq_id = 0;
static bool g_initialized = false;

void koui_init(void)
{
    if (g_initialized) return;
    g_initialized = true;

    g_label_pool_used = 0;
    g_render_count = 0;
    memset(g_label_pool, 0, sizeof(g_label_pool));
    memset(g_render_list, 0, sizeof(g_render_list));

    // Get the first font (index 0) as default for Koui labels
    rdpq_font_t *font = fonts_get(0);
    if (font) {
        g_default_font_rdpq_id = fonts_get_rdpq_id(0);
        // Set default style 0 to white - this avoids per-frame color setting
        rdpq_font_style(font, 0, &(rdpq_fontstyle_t){
            .color = RGBA32(255, 255, 255, 255)
        });
    }
}

KouiLabel* koui_create_label(const char *text)
{
    // Allocate from static pool - no malloc!
    if (g_label_pool_used >= KOUI_MAX_LABELS) return NULL;
    KouiLabel *label = &g_label_pool[g_label_pool_used++];

    label->text = text;
    label->pos_x = 0;
    label->pos_y = 0;
    label->font_id = g_default_font_rdpq_id;
    label->visible = true;

    return label;
}

void koui_add_label(KouiLabel *label)
{
    if (!label || g_render_count >= KOUI_MAX_LABELS) return;

    // Check if already in render list
    for (uint8_t i = 0; i < g_render_count; i++) {
        if (g_render_list[i] == label) return;
    }

    g_render_list[g_render_count++] = label;
}

void koui_remove_label(KouiLabel *label)
{
    if (!label) return;

    // Find in render list
    for (uint8_t i = 0; i < g_render_count; i++) {
        if (g_render_list[i] == label) {
            // Shift remaining down
            for (uint8_t j = i; j < g_render_count - 1; j++) {
                g_render_list[j] = g_render_list[j + 1];
            }
            g_render_count--;
            break;
        }
    }

    // Note: Label stays in pool until scene reset (no free needed)
}

void koui_clear(void)
{
    // Reset label pool and render list (call on scene change)
    g_label_pool_used = 0;
    g_render_count = 0;
    memset(g_label_pool, 0, sizeof(g_label_pool));
    memset(g_render_list, 0, sizeof(g_render_list));
}

void koui_label_set_position(KouiLabel *label, int16_t x, int16_t y)
{
    if (label) {
        label->pos_x = x;
        label->pos_y = y;
    }
}

void koui_render(void)
{
    // Early exit if nothing to render
    if (g_render_count == 0 || g_default_font_rdpq_id == 0) return;

    // Begin 2D text rendering mode
    rdpq_set_mode_standard();
    rdpq_mode_combiner(RDPQ_COMBINER_TEX_FLAT);
    rdpq_mode_blender(RDPQ_BLENDER_MULTIPLY);

    // Render all visible labels in render list
    for (uint8_t i = 0; i < g_render_count; i++) {
        KouiLabel *label = g_render_list[i];
        if (!label || !label->visible || !label->text) continue;

        rdpq_text_print(NULL, label->font_id, label->pos_x, label->pos_y + 15, label->text);
    }
}
