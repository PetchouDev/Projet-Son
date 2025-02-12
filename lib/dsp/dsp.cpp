#include "dsp.h"

#define AUDIO_OUTPUTS 2

#define MULT_16 32767

MyDsp::MyDsp() : 
AudioStream(AUDIO_OUTPUTS, new audio_block_t*[AUDIO_OUTPUTS]),
sine(AUDIO_SAMPLE_RATE_EXACT),
echoL(AUDIO_SAMPLE_RATE_EXACT,10000),
echoR(AUDIO_SAMPLE_RATE_EXACT,8000)
{
  echoL.setDel(10000);
  echoL.setFeedback(0.5);
  echoR.setDel(8000);
  echoR.setFeedback(0.2);
}

MyDsp::~MyDsp(){}

// set sine wave frequency
void MyDsp::setFreq(float freq){
  sine.setFrequency(freq);
}
void MyDsp::setGain(){
    setFreq(random(100,1400));
}


void MyDsp::update(void) {
  audio_block_t* outBlock[AUDIO_OUTPUTS];
  for (int channel = 0; channel < AUDIO_OUTPUTS; channel++) {
    outBlock[channel] = allocate();
    if (outBlock[channel]) {
      for (int i = 0; i < AUDIO_BLOCK_SAMPLES; i++) {
        
        if(channel==0){
          float currentSample = echoL.tick(sine.tick())*gain;
        currentSample = max(-1,min(1,currentSample));
        int16_t val = currentSample*MULT_16;
        outBlock[channel]->data[i] = val;
          echoL.setFeedback(0.5);
        }else{
          float currentSample = echoR.tick(sine.tick())*gain;
        currentSample = max(-1,min(1,currentSample));
        int16_t val = currentSample*MULT_16;
        outBlock[channel]->data[i] = val;
          echoR.setFeedback(0.2);
        }
      }
    }
  }
  for (int channel = 0; channel < AUDIO_OUTPUTS; channel++) {
    transmit(outBlock[channel], channel);
      release(outBlock[channel]);
  }
}
