#pragma once

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Max UI elements
#ifndef KOUI_MAX_LABELS
#define KOUI_MAX_LABELS 32
#endif

// Label element
typedef struct {
    int16_t pos_x, pos_y;
    const char *text;
    uint8_t font_id;
    bool visible;
} KouiLabel;

// Initialize Koui UI system
void koui_init(void);

// Clear all labels and reset pool (call on scene change)
void koui_clear(void);

// Label management
KouiLabel* koui_create_label(const char *text);  // Create label (not added to scene)
void koui_add_label(KouiLabel *label);            // Add label to render list
void koui_remove_label(KouiLabel *label);         // Remove label from render list
void koui_label_set_position(KouiLabel *label, int16_t x, int16_t y);

// Render all UI elements (call after 3D rendering, before display_show)
void koui_render(void);

#ifdef __cplusplus
}
#endif
