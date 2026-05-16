#include "prg32.h"
#include "prg32_audio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const uint8_t soft_square[] = {
    128, 180, 225, 245, 225, 180, 128, 76,
    31, 11, 31, 76,
};

static const prg32_audio_event_t melody[] = {
    {0, PRG32_AUDIO_CMD_NOTE_ON, 0, 60},
    {4, PRG32_AUDIO_CMD_NOTE_OFF, 0, 0},
    {0, PRG32_AUDIO_CMD_NOTE_ON, 0, 64},
    {4, PRG32_AUDIO_CMD_NOTE_OFF, 0, 0},
    {0, PRG32_AUDIO_CMD_NOTE_ON, 0, 67},
    {4, PRG32_AUDIO_CMD_NOTE_OFF, 0, 0},
    {0, PRG32_AUDIO_CMD_JUMP, 0, 0},
};

void app_main(void) {
    prg32_init();
    prg32_console_write("PRG32 mono tracker\n");
    prg32_audio_init(NULL);

    prg32_audio_register_sample(0, soft_square, sizeof(soft_square), 60, PRG32_AUDIO_SAMPLE_LOOP, 0, sizeof(soft_square));
    prg32_instrument_desc_t inst = {
        .sample_id = 0,
        .default_volume = 150,
        .default_pan = 0,
        .sustain = 255,
    };
    prg32_audio_register_instrument(0, &inst);
    prg32_audio_register_track(0, melody, sizeof(melody) / sizeof(melody[0]));
    prg32_audio_set_tempo(120);
    prg32_audio_play_track(0);

    while (1) {
        prg32_gfx_present();
        vTaskDelay(pdMS_TO_TICKS(16));
    }
}
