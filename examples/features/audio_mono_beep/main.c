#include "prg32.h"
#include "prg32_audio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void) {
    prg32_init();
    prg32_console_write("PRG32 mono beep\n");
    prg32_audio_init(NULL);

    static const uint8_t square[] = {
        255, 255, 255, 255, 0, 0, 0, 0,
    };
    prg32_audio_register_sample(0, square, sizeof(square), 69, PRG32_AUDIO_SAMPLE_LOOP, 0, sizeof(square));
    int ch = prg32_audio_play_sample(0, 160, 1024);
    vTaskDelay(pdMS_TO_TICKS(250));
    prg32_audio_stop_channel(ch);

    while (1) {
        prg32_gfx_present();
        vTaskDelay(pdMS_TO_TICKS(16));
    }
}
