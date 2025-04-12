#pragma once

#include "esphome/core/automation.h"
#include "clapper.h"

namespace esphome {
namespace clapper {

class ClapDetectionStateTrigger : public Trigger<ClapState> {
 public:
  explicit ClapDetectionStateTrigger(ClapperEvent *clapper) {
    clapper->add_on_clap_detection_state_callback([this](ClapState state) { this->trigger(state); });
  }
};

class DoubleClapTrigger: public Trigger<> {
public:
 explicit DoubleClapTrigger(ClapperEvent *clapper) {
   clapper->add_on_double_clap_callback([this]() { this->trigger(); });
 }
};

}  // namespace clapper
}  // namespace esphome
