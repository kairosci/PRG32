#include "audio_internal.h"
#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_err.h"

static i2s_chan_handle_t g_i2s_tx;

int prg32_audio_i2s_start(const prg32_audio_config_t *config) {
#if !CONFIG_PRG32_AUDIO_ENABLED || CONFIG_PRG32_DISPLAY_QEMU_RGB
    (void)config;
    return -1;
#else
    if (!config || config->gpio_bclk < 0 || config->gpio_lrclk < 0 ||
        config->gpio_data < 0) {
        return -1;
    }

    if (config->gpio_sd >= 0) {
        gpio_config_t sd = {
            .pin_bit_mask = 1ULL << config->gpio_sd,
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE,
        };
        gpio_config(&sd);
        gpio_set_level(config->gpio_sd, 1);
    }

    i2s_chan_config_t chan_cfg =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num = 4;
    chan_cfg.dma_frame_num = PRG32_AUDIO_MIX_FRAMES;

    esp_err_t err = i2s_new_channel(&chan_cfg, &g_i2s_tx, NULL);
    if (err != ESP_OK) {
        g_i2s_tx = NULL;
        return -1;
    }

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(config->sample_rate),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
            I2S_DATA_BIT_WIDTH_16BIT,
            I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = config->gpio_bclk,
            .ws = config->gpio_lrclk,
            .dout = config->gpio_data,
            .din = I2S_GPIO_UNUSED,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };

    err = i2s_channel_init_std_mode(g_i2s_tx, &std_cfg);
    if (err == ESP_OK) {
        err = i2s_channel_enable(g_i2s_tx);
    }
    if (err != ESP_OK) {
        i2s_del_channel(g_i2s_tx);
        g_i2s_tx = NULL;
        return -1;
    }
    return 0;
#endif
}

void prg32_audio_i2s_stop(void) {
    if (g_i2s_tx) {
        i2s_channel_disable(g_i2s_tx);
        i2s_del_channel(g_i2s_tx);
        g_i2s_tx = NULL;
    }
}

int prg32_audio_i2s_write(const int16_t *samples,
                          size_t frames,
                          prg32_audio_mode_t mode) {
    if (!g_i2s_tx || !samples || frames == 0) {
        return -1;
    }
    size_t written = 0;
    size_t channels = mode == PRG32_AUDIO_MODE_STEREO ? 2u : 1u;
    size_t bytes = frames * channels * sizeof(int16_t);
    if (mode == PRG32_AUDIO_MODE_MONO) {
        static int16_t stereo[PRG32_AUDIO_MIX_FRAMES * 2];
        if (frames > PRG32_AUDIO_MIX_FRAMES) {
            return -1;
        }
        for (size_t i = 0; i < frames; ++i) {
            stereo[i * 2] = samples[i];
            stereo[i * 2 + 1] = samples[i];
        }
        samples = stereo;
        bytes = frames * 2u * sizeof(int16_t);
    }
    esp_err_t err = i2s_channel_write(g_i2s_tx,
                                      samples,
                                      bytes,
                                      &written,
                                      portMAX_DELAY);
    return err == ESP_OK && written == bytes ? 0 : -1;
}
