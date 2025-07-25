from esphome import automation
import esphome.codegen as cg
from esphome.components import event, microphone
import esphome.config_validation as cv
from esphome.const import (
    CONF_ID,
    CONF_MICROPHONE,
    CONF_ON_STATE,
    CONF_TRIGGER_ID,
    PLATFORM_ESP32,
)

from . import clapper_ns

DEPENDENCIES = ["microphone"]
CODEOWNERS = ["@rpoelstra"]

CONF_PASSIVE = "passive"

CONF_ENVELOPE_DECAY_FACTOR = 'envelope_decay_factor'
CONF_ONSET_THRESHOLD = 'onset_threshold'
CONF_ONSET_RATIO_THRESHOLD = 'onset_ratio_threshold'
CONF_TRANSIENT_TIMEOUT = 'transient_timeout'
CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR = 'transient_decay_threshold_factor'

CONF_TIME_WINDOW_MIN = 'minimum_time_window'
CONF_TIME_WINDOW_MAX = 'maximum_time_window'

CONF_ON_DOUBLE_CLAP = 'on_double_clap'

ClapperEvent = clapper_ns.class_("ClapperEvent", event.Event, cg.Component)

ClapState = clapper_ns.enum("ClapState")
ClapDetectionStateTrigger = clapper_ns.class_(
    "ClapDetectionStateTrigger",
    automation.Trigger.template(),
)
#TODO: FIX AEGUMENT TYPE ABOVE (and somewhere below)

DoubleClapTrigger = clapper_ns.class_(
    "DoubleClapTrigger",
    automation.Trigger.template(),
)

StartAction = clapper_ns.class_("StartAction", automation.Action)
StopAction = clapper_ns.class_("StopAction", automation.Action)

CONFIG_SCHEMA = cv.All(
    event.event_schema(ClapperEvent).extend(
    {
        cv.GenerateID(): cv.declare_id(ClapperEvent),
        cv.Optional(CONF_MICROPHONE, default = {}): microphone.microphone_source_schema(
            min_bits_per_sample=16,
            max_bits_per_sample=16,
        ),
        cv.Optional(CONF_PASSIVE, default = False): cv.boolean,

        cv.Optional(CONF_ENVELOPE_DECAY_FACTOR, default=0.999):  cv.float_range(min=0.0, max=1.0, min_included=False, max_included=False),
        cv.Optional(CONF_ONSET_THRESHOLD, default=1000): cv.int_, #TODO: Add range
        cv.Optional(CONF_ONSET_RATIO_THRESHOLD, default=1.58): cv.float_range(min=1.0, min_included=False),
        cv.Optional(CONF_TRANSIENT_TIMEOUT, default="100ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR, default=0.25): cv.float_range(min=0.0, max=1.0, min_included=False, max_included=False),
        cv.Optional(CONF_TIME_WINDOW_MIN, default="250ms"): cv.positive_time_period_milliseconds,
        cv.Optional(CONF_TIME_WINDOW_MAX, default="800ms"): cv.positive_time_period_milliseconds,

        cv.Optional(CONF_ON_STATE): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(ClapDetectionStateTrigger),
                }
            ),

        cv.Optional(CONF_ON_DOUBLE_CLAP): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(DoubleClapTrigger),
                }
            ),
    }
    ),
    cv.only_on([PLATFORM_ESP32])
)


async def to_code(config):
    var = await event.new_event(config, event_types=["double_clap"])
    await cg.register_component(var, config)

    mic_source = await microphone.microphone_source_to_code(
        config[CONF_MICROPHONE], passive = config[CONF_PASSIVE]
    )
    cg.add(var.set_microphone_source(mic_source))

    cg.add(var.set_envelope_decay_factor(config[CONF_ENVELOPE_DECAY_FACTOR]))
    cg.add(var.set_onset_threshold(config[CONF_ONSET_THRESHOLD]))
    cg.add(var.set_onset_ratio_threshold(config[CONF_ONSET_RATIO_THRESHOLD]))
    cg.add(var.set_transient_timeout(config[CONF_TRANSIENT_TIMEOUT]))
    cg.add(var.set_transient_decay_threshold_factor(config[CONF_TRANSIENT_DECAY_THRESHOLD_FACTOR]))
    cg.add(var.set_time_window_min(config[CONF_TIME_WINDOW_MIN]))
    cg.add(var.set_time_window_max(config[CONF_TIME_WINDOW_MAX]))

    for conf in config.get(CONF_ON_STATE, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger,
            [(ClapState, "state")],
            conf,
        )

    for conf in config.get(CONF_ON_DOUBLE_CLAP, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger,
            [],
            conf,
        )

CLAPPER_ACTION_SCHEMA = automation.maybe_simple_id(
    {
        cv.GenerateID(): cv.use_id(ClapperEvent),
    }
)


@automation.register_action("clapper.start", StartAction, CLAPPER_ACTION_SCHEMA)
@automation.register_action("clapper.stop", StopAction, CLAPPER_ACTION_SCHEMA)
async def clapper_action_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var
