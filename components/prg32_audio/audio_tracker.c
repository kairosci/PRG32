#include "audio_internal.h"

static uint32_t tick_ms(void) {
    uint16_t bpm = g_prg32_audio.tracker.tempo_bpm;
    if (bpm == 0) {
        bpm = 120;
    }
    return 60000u / ((uint32_t)bpm * 4u);
}

static void execute_event(const prg32_audio_event_t *event) {
    switch (event->command) {
    case PRG32_AUDIO_CMD_NOTE_ON:
    {
        uint8_t channel = event->arg0 % CONFIG_PRG32_AUDIO_MAX_VOICES;
        prg32_audio_note_on(channel,
                            channel,
                            event->arg1,
                            g_prg32_audio.channel_volume[channel]);
        break;
    }
    case PRG32_AUDIO_CMD_NOTE_OFF:
        prg32_audio_note_off(event->arg0);
        break;
    case PRG32_AUDIO_CMD_SET_VOLUME:
        prg32_audio_set_channel_volume(event->arg0, event->arg1);
        break;
    case PRG32_AUDIO_CMD_SET_PAN:
        prg32_audio_set_channel_pan(event->arg0, (int8_t)event->arg1);
        break;
    case PRG32_AUDIO_CMD_SET_TEMPO:
        prg32_audio_set_tempo(event->arg0 ? event->arg0 : 120);
        break;
    case PRG32_AUDIO_CMD_PLAY_SAMPLE:
        prg32_audio_play_sample(event->arg0, event->arg1, PRG32_AUDIO_PITCH_BASE);
        break;
    default:
        break;
    }
}

void prg32_audio_play_track(uint16_t track_id) {
    if (track_id >= PRG32_AUDIO_MAX_TRACKS ||
        !g_prg32_audio.tracks[track_id].present) {
        return;
    }
    prg32_audio_lock();
    g_prg32_audio.tracker.active = true;
    g_prg32_audio.tracker.track_id = track_id;
    g_prg32_audio.tracker.event_index = 0;
    g_prg32_audio.tracker.tick_accum = 0;
    g_prg32_audio.tracker.next_delta = 0;
    prg32_audio_unlock();
}

void prg32_audio_stop_track(void) {
    prg32_audio_lock();
    g_prg32_audio.tracker.active = false;
    prg32_audio_unlock();
}

void prg32_audio_set_tempo(uint16_t bpm) {
    if (bpm < 30) {
        bpm = 30;
    }
    if (bpm > 300) {
        bpm = 300;
    }
    prg32_audio_lock();
    g_prg32_audio.tracker.tempo_bpm = bpm;
    prg32_audio_unlock();
}

void prg32_audio_tracker_step(uint32_t elapsed_ms) {
    if (!g_prg32_audio.tracker.active || elapsed_ms == 0) {
        return;
    }

    prg32_audio_lock();
    prg32_audio_tracker_state_t *tracker = &g_prg32_audio.tracker;
    if (tracker->track_id >= PRG32_AUDIO_MAX_TRACKS ||
        !g_prg32_audio.tracks[tracker->track_id].present) {
        tracker->active = false;
        prg32_audio_unlock();
        return;
    }
    prg32_audio_track_slot_t *track = &g_prg32_audio.tracks[tracker->track_id];
    tracker->tick_accum += elapsed_ms;
    uint32_t ms_per_tick = tick_ms();

    while (tracker->active && tracker->tick_accum >= ms_per_tick) {
        tracker->tick_accum -= ms_per_tick;
        if (tracker->next_delta > 0) {
            tracker->next_delta--;
            continue;
        }
        if (tracker->event_index >= track->event_count) {
            tracker->active = false;
            break;
        }

        prg32_audio_event_t event = track->events[tracker->event_index++];
        tracker->next_delta = event.delta_ticks;
        if (event.command == PRG32_AUDIO_CMD_JUMP) {
            uint32_t target = ((uint32_t)event.arg1 << 8) | event.arg0;
            if (target < track->event_count) {
                tracker->event_index = target;
            } else {
                tracker->active = false;
            }
        } else if (event.command == PRG32_AUDIO_CMD_END) {
            tracker->active = false;
        } else {
            prg32_audio_unlock();
            execute_event(&event);
            prg32_audio_lock();
        }
    }
    prg32_audio_unlock();
}
