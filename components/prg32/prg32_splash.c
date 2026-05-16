#include "prg32.h"
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stddef.h>

#ifndef CONFIG_PRG32_SPLASH_ENABLED
#define CONFIG_PRG32_SPLASH_ENABLED 1
#endif

#ifndef CONFIG_PRG32_SPLASH_DURATION_MS
#define CONFIG_PRG32_SPLASH_DURATION_MS 900
#endif

static int text_center_x(const char *text) {
    size_t len = 0;
    if (text) {
        while (text[len] != '\0') {
            len++;
        }
    }
    int width = (int)len * 8;
    if (width >= PRG32_GAME_W) {
        return 0;
    }
    return (PRG32_GAME_W - width) / 2;
}

void prg32_splash_draw(const char *title,
                       const char *subtitle,
                       uint16_t bg,
                       uint16_t fg,
                       uint16_t accent) {
    if (!title) {
        title = "PRG32";
    }
    if (!subtitle) {
        subtitle = "";
    }

    prg32_gfx_clear(bg);
    prg32_gfx_rect(0, 0, PRG32_GAME_W, 6, accent);
    prg32_gfx_rect(0, PRG32_GAME_H - 6, PRG32_GAME_W, 6, accent);
    prg32_gfx_rect(34, 54, 252, 2, accent);
    prg32_gfx_rect(34, 138, 252, 2, accent);

    for (int i = 0; i < 5; ++i) {
        int x = 72 + i * 36;
        prg32_gfx_rect(x, 72, 20, 20, accent);
        prg32_gfx_rect(x + 4, 76, 12, 12, bg);
    }

    int title_x = text_center_x(title);
    int subtitle_x = text_center_x(subtitle);
    prg32_gfx_text8(title_x + 1, 98 + 1, title, accent, bg);
    prg32_gfx_text8(title_x, 98, title, fg, bg);
    prg32_gfx_text8(subtitle_x, 116, subtitle, fg, bg);
}

void prg32_splash_show(const char *title,
                       const char *subtitle,
                       uint32_t duration_ms,
                       uint16_t bg,
                       uint16_t fg,
                       uint16_t accent) {
    prg32_splash_draw(title, subtitle, bg, fg, accent);
    prg32_gfx_present();
    if (duration_ms > 0) {
        vTaskDelay(pdMS_TO_TICKS(duration_ms));
    }
}

void prg32_splash_show_default(void) {
#if CONFIG_PRG32_SPLASH_ENABLED
    prg32_splash_show("PRG32",
                      "RISC-V GAME RUNTIME",
                      CONFIG_PRG32_SPLASH_DURATION_MS,
                      PRG32_COLOR_BLACK,
                      PRG32_COLOR_WHITE,
                      PRG32_COLOR_CYAN);
#endif
}
