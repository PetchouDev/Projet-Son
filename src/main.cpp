#include <Audio.h>
#include "dsp.h"

MyDsp myDsp;
AudioOutputI2S out;
AudioControlSGTL5000 audioShield;
AudioConnection patchCord0(myDsp,0,out,0);
AudioConnection patchCord1(myDsp,1,out,1);

bool button_pressed = false;

void setup() {
  AudioMemory(2);
  audioShield.enable();
  audioShield.volume(0.5);
}

void loop() {

  myDsp.setFreq(random(70,500));
  delay(100);
  
 // delay(100);
  delay(100);
}
