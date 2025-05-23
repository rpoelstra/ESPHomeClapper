#pragma once

#include "esphome/core/component.h"
#include "esphome/components/event/event.h"
#include "esphome/components/microphone/microphone.h"

#include <vector>

namespace esphome {
namespace clapper {

enum class State {
    START_MICROPHONE,
    STARTING_MICROPHONE,
    RUNNING,
};

enum class ClapState {
    IDLE,
    FIRST_CLAP,
    SECOND_CLAP,
    THIRD_OR_HIGHER_CLAP,
};

class ClapperEvent : public Component, public event::Event {
public:
    void setup() override;
    void loop() override;

    void add_on_clap_detection_state_callback(std::function<void(clapper::ClapState)> &&callback);
    void add_on_double_clap_callback(std::function<void()> &&callback);
    void update_state(ClapState state);

    void set_microphone(microphone::Microphone *mic) { this->mic_ = mic; }
    void set_dc_offset_factor(float factor) { this->dc_offset_factor_ = factor; }
    void set_envelope_decay_factor(float factor) { this->envelope_decay_factor_ = factor; }
    void set_onset_threshold(int16_t threshold) { this->onset_threshold_ = threshold; }
    void set_onset_ratio_threshold(float threshold) { this->onset_ratio_threshold_ = threshold; }
    void set_transient_timeout(int timeout) { this->transient_timeout_ = timeout; }
    void set_transient_decay_threshold_factor(float factor) { this->transient_decay_threshold_factor_ = factor; }

    void set_time_window_min(int window) { this->time_window_min_ = window; }
    void set_time_window_max(int window) { this->time_window_max_ = window; }

    void data_callback(const std::vector<int16_t> &data);

protected:
    //Component configuration
    microphone::Microphone *mic_{nullptr};

    CallbackManager<void(clapper::ClapState)> state_callback_{};
    CallbackManager<void()> double_clap_callback_{};

    float dc_offset_factor_;
    float envelope_decay_factor_;
    int16_t onset_threshold_;
    float onset_ratio_threshold_;
    unsigned long transient_timeout_;
    float transient_decay_threshold_factor_;

    unsigned long time_window_min_;
    unsigned long time_window_max_;

    //Component state
    State state_ {State::START_MICROPHONE};

    float dc_offset_ = 0;
    int16_t envelope_ = 0;
    int16_t previous_envelope_ = 0;
    unsigned long onset_ = 0;
    int16_t transient_peak_;

    ClapState clapState_ = ClapState::IDLE;
    bool double_clap_accepted_;
    unsigned long last_clap_ = 0;

    bool detect_clap(const std::vector<int16_t> &data);
};


}  // namespace clapper
}  // namespace esphome
