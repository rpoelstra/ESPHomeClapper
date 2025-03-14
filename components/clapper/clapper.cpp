#include "esphome/core/log.h"
#include "esphome/core/hal.h"
#include "clapper.h"

namespace esphome {
namespace clapper {

static const char *TAG = "clapper.component";


void ClapperEvent::setup() {
    ESP_LOGI(TAG, "Clapper setup");
    this->mic_->add_data_callback([this](const std::vector<int16_t> &data) {
        this->data_callback(data);
    });
}

void ClapperEvent::loop() {
    switch (this->state_) {
        case State::START_MICROPHONE:
            ESP_LOGD(TAG, "Starting Microphone");
            this->mic_->start();
            this->state_ = State::STARTING_MICROPHONE;
            break;
        case State::STARTING_MICROPHONE:
            if (this->mic_->is_running()) {
                ESP_LOGD(TAG, "Microphone started");
                this->state_ = State::RUNNING;
            }
            break;
        case State::RUNNING:
            if (this->double_clap_accepted_) {
                this->double_clap_accepted_ = false;
                this->trigger("double_clap");
            }
            break;
    }
}

void ClapperEvent::data_callback(const std::vector<int16_t> &data) {
    unsigned long current_time = millis();

    //Detect double claps
    if (this->detect_clap(data)) {
        //A clap was detected
        this->last_clap_ = current_time;

        switch (this->clapState_) {
            case ClapState::IDLE:
                ESP_LOGI(TAG, "First clap detected!");
                this->clapState_     = ClapState::FIRST_CLAP;
//            M5.dis.drawpix(0, CRGB(255, 128, 0));
                break;
            case ClapState::FIRST_CLAP:
                ESP_LOGI(TAG, "Second clap detected!");
                this->clapState_ = ClapState::SECOND_CLAP;
//            M5.dis.drawpix(0, CRGB(0, 0, 255));
                //We do not send event, but wait for not-a-third-clap
                break;
            case ClapState::SECOND_CLAP:
                ESP_LOGI(TAG, "Higher clap detected!");
                this->clapState_ = ClapState::THIRD_OR_HIGHER_CLAP;
//            M5.dis.drawpix(0, CRGB(255, 0, 0));
                break;
            case ClapState::THIRD_OR_HIGHER_CLAP:
                //Nothing to be done
                break;
        }
    } else if (this->last_clap_ != 0 && (current_time - this->last_clap_) > this->time_window_) {
        //No clap for a while, check various timeouts
        switch (this->clapState_) {
            case ClapState::IDLE:
                break;
            case ClapState::FIRST_CLAP:
                ESP_LOGI(TAG, "First clap timeout. Reset!");
                //            M5.dis.drawpix(0, CRGB(0, 255, 0));
                break;
            case ClapState::SECOND_CLAP:
                ESP_LOGI(TAG, "Double clap accepted!");
                this->double_clap_accepted_ = true;
                //            M5.dis.drawpix(0, CRGB(0, 255, 0));
                break;
            case ClapState::THIRD_OR_HIGHER_CLAP:
                ESP_LOGI(TAG, "Clapping stopped. Reset!");
                //            M5.dis.drawpix(0, CRGB(0, 255, 0));
                break;
        }

        this->clapState_ = ClapState::IDLE;
    }
}

// Detect a sharp spike followed by a decay within a time window
bool ClapperEvent::detect_clap(const std::vector<int16_t> &data) {
    bool clap_detected = false;

    for(int16_t sample : data) {
        //Update DC offset estimation
        this->dc_offset_ = this->dc_offset_factor_ * this->dc_offset_ + (1-this->dc_offset_factor_)*sample;

        //Remove DC offset
        sample = clamp(sample-this->dc_offset_, (float)-INT16_MAX, (float)INT16_MAX);

        //Take absolute value
        sample = abs(sample);

        //Update envelope estimation
        this->envelope_ *= this->envelope_decay_factor_;
        this->envelope_ = std::max(this->envelope_, sample);

        //Search for onset
        this->previous_envelope_ = this->previous_envelope_ == 0 ? this->envelope_ : this->previous_envelope_; //Prevent division by zero
        float ratio = this->envelope_ / (float)this->previous_envelope_;
        this->previous_envelope_ = this->envelope_;

        if (this->onset_ == 0 && this->envelope_ > this->onset_threshold_ && ratio > this->onset_ratio_threshold_) { //Only try to find an onset if we don't already have one. We also need a minimum input as not to trigger on noise
            //The ratio is high enough that we consider it an onset for a transient
            this->onset_ = millis();
            this->transient_peak_ = this->envelope_;
        }

        //After finding an onset, make sure there is a fast enough decay (or timeout)
        if (this->onset_ != 0) {
            //Update the transient_peak if it wasn't at the transient max yet
            this->transient_peak_ = std::max(this->transient_peak_, this->envelope_);

            //Check for timeout
            unsigned long transient_time = millis() - this->onset_;
            if (transient_time > this->transient_timeout_) {
                this->onset_ = 0;
            }

            //Check for decay
            if (this->envelope_ < this->transient_peak_*this->transient_decay_threshold_factor_) {
                clap_detected = true;
                this->onset_ = 0;
            }
        }
    }

    return clap_detected;
}

}  // namespace empty_component
}  // namespace esphome
