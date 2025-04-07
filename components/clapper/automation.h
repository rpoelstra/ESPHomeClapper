#pragma once

#include "esphome/core/automation.h"
#include "clapper.h"

namespace esphome {
namespace clapper {

class ClapDetectionStateTrigger : public Trigger<> {
 public:
  explicit ClapDetectionStateTrigger(ClapperEvent *clapper) {
    clapper->add_on_clap_detection_state_callback([this]() { this->trigger(); });
  }
};

}  // namespace clapper
}  // namespace esphome
