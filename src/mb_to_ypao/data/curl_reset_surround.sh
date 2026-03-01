#!/bin/bash
curl -X POST "http://192.168.68.68:80/YamahaRemoteControl/ctrl" --data-binary  '<YAMAHA_AV cmd="PUT">
  <Main_Zone>
    <Surround>
      <Program_Sel>
        <Current>
          <Straight>On</Straight>
          <Enhancer>Off</Enhancer>
        </Current>
      </Program_Sel>
      <Adaptive_DSP_Lvl>Off</Adaptive_DSP_Lvl>
      <VSBS>Off</VSBS>
    </Surround>
  </Main_Zone>
</YAMAHA_AV>'
