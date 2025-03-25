import esphome.codegen as cg
from esphome.components import event, microphone
import esphome.config_validation as cv
from esphome.const import (
CONF_ID,
CONF_MICROPHONE,
)

from . import clapper_ns

DEPENDENCIES = ["microphone"]
CODEOWNERS = ["@rpoelstra"]

CONF_DC_OFFSET_FACTOR = 'dc_offset_factor'
CONF_ENVELOPE_DECAY_FACTOR = 'envelope_decay_factor'
CONF_ONSET_THRESHOLD = 'onset_threshold'
CONF_ONSET_RATIO_THRESHOLD = 'onset_ratio_threshold'
CONF_TRANSIENT_TIMEOUT = 'transient_timeout'
CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR = 'transient_decay_threshold_factor'

CONF_TIME_WINDOW_MIN = 'minimum_time_window'
CONF_TIME_WINDOW_MAX = 'maximum_time_window'

ClapperEvent = clapper_ns.class_("ClapperEvent", event.Event, cg.Component)

CONFIG_SCHEMA = event.event_schema(ClapperEvent).extend(
{
    cv.GenerateID(): cv.declare_id(ClapperEvent),
    cv.GenerateID(CONF_MICROPHONE): cv.use_id(microphone.Microphone),
    cv.Optional(CONF_DC_OFFSET_FACTOR, default=0.9999): cv.float_range(min=0.0, max=1.0, min_included=False, max_included=False),
  cv.Optional(CONF_ENVELOPE_DECAY_FACTOR, default=0.999):  cv.float_range(min=0.0, max=1.0, min_included=False, max_included=False),
  cv.Optional(CONF_ONSET_THRESHOLD, default=1000): cv.int_, #TODO: Add range
  cv.Optional(CONF_ONSET_RATIO_THRESHOLD, default=1.58): cv.float_range(min=1.0, min_included=False),
  cv.Optional(CONF_TRANSIENT_TIMEOUT, default="100ms"): cv.positive_time_period_milliseconds,
  cv.Optional(CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR, default=0.25): cv.float_range(min=0.0, max=1.0, min_included=False, max_included=False),
  cv.Optional(CONF_TIME_WINDOW_MIN, default="250ms"): cv.positive_time_period_milliseconds,
  cv.Optional(CONF_TIME_WINDOW_MAX, default="800ms"): cv.positive_time_period_milliseconds,
}
)

async def to_code(config):
    var = await event.new_event(config, event_types=["double_clap"])
    await cg.register_component(var, config)

    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))

    cg.add(var.set_dc_offset_factor(config[CONF_DC_OFFSET_FACTOR]))
    cg.add(var.set_envelope_decay_factor(config[CONF_ENVELOPE_DECAY_FACTOR]))
    cg.add(var.set_onset_threshold(config[CONF_ONSET_THRESHOLD]))
    cg.add(var.set_onset_ratio_threshold(config[CONF_ONSET_RATIO_THRESHOLD]))
    cg.add(var.set_transient_timeout(config[CONF_TRANSIENT_TIMEOUT]))
    cg.add(var.set_transient_decay_threshold_factor(config[CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR]))
    cg.add(var.set_time_window_min(config[CONF_TIME_WINDOW_MIN]))
    cg.add(var.set_time_window_max(config[CONF_TIME_WINDOW_MAX]))
