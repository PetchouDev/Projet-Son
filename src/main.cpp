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

  if(digitalRead(0) == 1 and button_pressed == false){
    button_pressed = true;
    myDsp.setGain();
  }
  if(digitalRead(0) == 0 and button_pressed == true){
    button_pressed = false;
  }
  
 // delay(100);
  delay(100);
}
