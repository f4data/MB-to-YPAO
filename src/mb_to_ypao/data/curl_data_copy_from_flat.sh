#!/bin/bash
curl -X POST "http://192.168.68.68:80/YamahaRemoteControl/ctrl" --data-binary  '<YAMAHA_AV cmd="PUT">
  <System>
    <Speaker_Preout>
      <Pattern_1>
        <PEQ>
          <Sel>Manual</Sel>        
          <Data_Copy_From>Flat</Data_Copy_From>
        </PEQ>
      </Pattern_1>
    </Speaker_Preout>
  </System>
  <Main_Zone>
    <Sound_Video>
      <YPAO_Volume>On</YPAO_Volume>  
    </Sound_Video>
  </Main_Zone>
</YAMAHA_AV>'
