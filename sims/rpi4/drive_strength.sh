#! /usr/bin/bash

sudo pigpiod
strength=$(4)
pigs pads 0 $strength # set GPIO pin's driver strength [mA]
exit $strength
