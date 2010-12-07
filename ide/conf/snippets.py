# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Jaluino Plugin                                                     #
# Author: Sebastien Lelong <sebastien.lelong@gmail.com>                       #
# Copyright: (c) 2010                                                         #
# License: wxWindows License                                                  #
###############################################################################

# "templates" is the entry point, it's a dictionary containing
# declared templates. It looks like:
# template = {
#       "template_name1" : {"name"        : "template_name1",
#                            "description" : "some help text",
#                            "indent"      : True, # obey indentation ?,
#                             "template"    : "the actual template code",
#                            },
#       "template_name2" : {"name" ...},
# }

# For more about template, see http://code.google.com/p/editra-plugins/wiki/CodeTemplater

# This is a default template sets. Suggestions ? Join jallib or jaluino groups (or both).
templates = {
        "serial_hw" : {
            "name" : "serial_hw",
            "description" : "Configuration and include for serial_hardware library",
            "indent" : True,
            "templ" : """
--baudrate
const serial_hw_baudrate = #CUR115_200 -- or 19_200, 9_600, ...
include serial_hardware
serial_hw_init()
"""
        },
        "serial_sw" : {
            "name" : "serial_sw",
            "description" : "Configuration and include for serial_software library",
            "indent" : True,
            "templ" : """
--baudrate
const serial_sw_baudrate = #CUR9_600 -- or 19_200, 2_400, ...
-- RX/TX pins
alias serial_sw_tx_pin is pin_XX
alias serial_sw_rx_pin is pin_YY
alias serial_sw_tx_pin_direction is pin_XX_direction
alias serial_sw_rx_pin_direction is pin_YY_direction
serial_sw_tx_pin_direction = output
serial_sw_rx_pin_direction = input
-- inverted levels (usually it is)
const serial_sw_invert = true
include serial_software
serial_sw_init()
"""
        },
        "adc (dependent)" : {
            "name" : "adc",
            "description" : "Configuration and include for ADC library, for both *dependent* analog pins",
            "indent" : True,
            "templ" : """
-- speficy the number of channels
const byte ADC_NCHANNEL = #CUR1
-- high or low resolution ?
const bit ADC_HIGH_RESOLUTION = low
-- Any voltage references ?
const byte ADC_NVREF = 0
include adc
adc_init()
""",
       },
        "adc (independent)" : {
            "name" : "adc",
            "description" : "Configuration and include for ADC library, for both *independent* analog pins",
            "indent" : True,
            "templ" : """
-- high or low resolution ?
const bit ADC_HIGH_RESOLUTION = low
-- Any voltage references ?
const byte ADC_NVREF = 0
include adc
adc_init()
-- Now specify which pins should be configured as analog
set_analog_pin(1) -- configure AN1
set_analog_pin(4) -- configure AN4
""",
       },
       "crumboard" : {
            "name" : "crumboard",
            "description" : "Configuration and include when using crumboard shield",
            "indent" : True,
            "templ" : """
-- describe hardware setup by declaring plugged jumpers
const bit CRUMBOARD_LED1_JP1 = on   -- we've put a jumper in JP1 (use LED D1)
const bit CRUMBOARD_LED2_JP2 = on   -- and also on JP2 (use LED D2)
const bit CRUMBOARD_SW1_JP3  = on   -- we've put a jumper in JP3 (use switch SW1)
const bit CRUMBOARD_SW2_JP4  = on   -- and also on JP2 (use switch SW2)
-- now we can include crumboard library
include crumboard_shield
crumboard_init()
"""
        },
        "pseudo'get" : {
            "name" : "pseudo'get",
            "description" : "Create a pseudo'get (pseudo-variable) skeleton code from selected text",
            "indent" : True,
            "templ" : """
function ${same}'get() return #CURbyte is
   -- code here, don't forget to check returned type
end function
"""
        },
        "pseudo'put" : {
            "name" : "pseudo'put",
            "description" : "Create a pseudo'put(pseudo-variable) skeleton code from selected text",
            "indent" : True,
            "templ" : """
procedure ${same}'put(#CUR byte in data) is
   -- code here, don't forget to check input data type
end procedure
"""
        },
}
