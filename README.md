# ESPHomeClapper

ESPHomeClapper is an ESPHome component that allows you to trigger automations in Home Assistant by clapping your hands. It detects a double clap and sends an event to Home Assistant which you can use to trigger your automation.

ESPHomeClapper uses a transient detection algorithm which requires exactly two transients within a time period to fire the event. As such, it also responds to other percusive sounds as if they were claps.

## Installation

### ESPHome
Since ESPHomeClapper uses the microphone component, which is only supported on the ESP32 platform, ESPHomeClapper also only supports the ESP32 platform.

Add the following to your YAML file to make use of ESPHomeClapper. Make sure to adapt the `i2s_audio` and `microphone` sections to your board. 

```
esphome:
  min_version: 2024.7.1

esp32:
  framework:
    type: esp-idf

external_components:
  - source: github://rpoelstra/ESPHomeClapper@main
    components: [ clapper ]
  - source: github://pr#8181
    components: [ i2s_audio, microphone ]

i2s_audio:
  - i2s_lrclk_pin: GPIO33
    i2s_bclk_pin: GPIO19

microphone:
  - platform: i2s_audio
    i2s_din_pin: GPIO23
    adc_type: external
    bits_per_sample: 16bit
    pdm: true

event:
    - platform: clapper
      name: My Clapper
```

### Home Assistant

In the automation editor in Home Assistant select 'Entity' as automation trigger and then select 'State'. Select your clapper as the entity. You can leave all other fields blank. 

## Configuration variables

- **dc_offset_factor** (_Optional_): Factor that controls how fast the system will respond to changes in the DC offset of the signal. Should be very close to 1. Defaults to 0.9999. 
- **envelope_decay_factor** (_Optional_): Factor that controls how fast the system decays after a signal peak. Should be close to 1. Defaults to 0.999.
- **onset_threshold** (_Optional_): Minimum signal input required for an onset to be detected. Defaults to 1000.
- **onset_ratio_threshold** (_Optional_): Ratio between two consequtive samples that will be required for the onset to be marked as such. Defaults to 1.58.
- **transient_timeout** (_Optional_): The maximum allowed time for the transient to last to be detected as a clap. Defaults to 100 ms.
- **transient_decay_threshold_factor** (_Optional_): The minimum decay the transient such have in the timeout period to be detected as a clap. Defaults to 0.25.
- **minimum_time_window** (_Optional_): The minimum time between claps for them to be considered a grouped event. Defaults to 250 ms.
- **maximum_time_window** (_Optional_): The maximum time between claps for them to be considered a grouped event. Defaults to 500 ms.

## Full example

The following YAML is a full configuration example for the M5Stack Atom Echo:
```
esphome:
  name: clapper
  min_version: 2024.7.1

esp32:
  board: m5stack-atom
  framework:
    type: esp-idf

logger:
api:

ota:
  - platform: esphome

wifi:
  ssid: <YOUR SSID>
  password: <YOUR PASSSWORD>

external_components:
  - source: github://rpoelstra/ESPHomeClapper@main
    components: [ clapper ]
  - source: github://pr#8181
    components: [ i2s_audio, microphone ]

i2s_audio:
  - i2s_lrclk_pin: GPIO33
    i2s_bclk_pin: GPIO19

microphone:
  - platform: i2s_audio
    i2s_din_pin: GPIO23
    adc_type: external
    bits_per_sample: 16bit
    pdm: true

event:
    - platform: clapper
      name: My Clapper
```
