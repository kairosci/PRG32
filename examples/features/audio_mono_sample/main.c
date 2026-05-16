#include "prg32.h"
#include "prg32_audio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const uint8_t click_sample[] = {
    128, 168, 210, 245, 255, 230, 190, 150,
    110, 75, 45, 28, 20, 34, 60, 92,
    128, 150, 140, 130, 128,
};

void app_main(void) {
    prg32_init();
    prg32_console_write("PRG32 mono sample\n");
    prg32_audio_init(NULL);
    prg32_audio_register_sample(0, click_sample, sizeof(click_sample), 60, 0, 0, 0);

    while (1) {
        prg32_audio_play_sample(0, 255, 1024);
        vTaskDelay(pdMS_TO_TICKS(700));
        prg32_gfx_present();
    }
}
