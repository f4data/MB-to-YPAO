#!/bin/bash
curl -X POST "http://192.168.68.68:80/YamahaRemoteControl/ctrl" --data-binary  '<YAMAHA_AV cmd="PUT">
  <System>
    <Speaker_Preout>
      <Pattern_1>
        <Config>
          <Front>
            <Type>Large</Type>
          </Front>
          <Center>
            <Type>Large</Type>
          </Center>
          <Sur>
            <Type>Large</Type>
          </Sur>
          <Sur_Back>
            <Type>Large</Type>
          </Sur_Back>
          <Front_Presence>
            <Type>Large</Type>
          </Front_Presence>
        </Config>
      </Pattern_1>
    </Speaker_Preout>
  </System>
</YAMAHA_AV>'

