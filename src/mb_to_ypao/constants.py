"""Mapping tables and static XML payloads used for MB → YPAO conversion."""

# ---------------------------------------------------------------------------
# Speaker name mapping: MultEQ-X (MB) label  →  Yamaha XML tag
# ---------------------------------------------------------------------------
SPEAKERS: dict[str, str] = {
    "Front Left": "Front_L",
    "Front Right": "Front_R",
    "Center": "Center",
    "LFE": "Subwoofer_1",
    "Surround Right": "Sur_R",
    "Surround Left": "Sur_L",
    "Surround Back Right": "Sur_Back_R",
    "Surround Back Left": "Sur_Back_L",
    "Middle Height Right": "Front_Presence_R",
    "Middle Height Left": "Front_Presence_L",
}

# ---------------------------------------------------------------------------
# GEQ frequency label mapping: geq text label  →  Yamaha XML tag name
# ---------------------------------------------------------------------------
GEQ_FREQUENCIES: dict[str, str] = {
    "63 Hz": "Gain_63_Hz",
    "160 Hz": "Gain_160_Hz",
    "400 Hz": "Gain_400_Hz",
    "1000 Hz": "Gain_1_kHz",
    "2500 Hz": "Gain_2_5_kHz",
    "6300 Hz": "Gain_6_3_kHz",
    "16000 Hz": "Gain_16_kHz",
}

# ---------------------------------------------------------------------------
# Frequency value mapping: MultEQ-X display value  →  Yamaha YPAO value
# ---------------------------------------------------------------------------
PEQ_FREQUENCIES: dict[str, str] = {
    "15.5 Hz": "15.6 Hz",
    "19.6 Hz": "19.7 Hz",
    "24.7 Hz": "24.8 Hz",
    "31.2 Hz": "31.3 Hz",
    "39.3 Hz": "39.4 Hz",
    "49.59 Hz": "49.6 Hz",
    "62.5 Hz": "62.5 Hz",
    "78.69 Hz": "78.7 Hz",
    "99.19 Hz": "99.2 Hz",
    "125 Hz": "125.0 Hz",
    "157.5 Hz": "157.5 Hz",
    "198.3 Hz": "198.4 Hz",
    "198 Hz": "198.4 Hz",
    "250 Hz": "250.0 Hz",
    "315 Hz": "315.0 Hz",
    "396.8 Hz": "396.9 Hz",
    "500 Hz": "500.0 Hz",
    "630 Hz": "630.0 Hz",
    "793.7 Hz": "793.7 Hz",
    "1000 Hz": "1.00 kHz",
    "1260 Hz": "1.26 kHz",
    "1590 Hz": "1.59 kHz",
    "2000 Hz": "2.00 kHz",
    "2520 Hz": "2.52 kHz",
    "3170 Hz": "3.17 kHz",
    "4000 Hz": "4.00 kHz",
    "5040 Hz": "5.04 kHz",
    "6350 Hz": "6.35 kHz",
    "8000 Hz": "8.00 kHz",
    "10100 Hz": "10.1 kHz",
    "12700 Hz": "12.7 kHz",
    "16000 Hz": "16.0 kHz",
}

# ---------------------------------------------------------------------------
# Q-factor mapping: MultEQ-X rounded Q  →  Yamaha YPAO Q
# ---------------------------------------------------------------------------
Q_FACTORS: dict[str, str] = {
    "0.5": "0.500",
    "0.50": "0.500",
    "0.62": "0.630",
    "0.79": "0.794",
    "1": "1.000",
    "1.25": "1.260",
    "1.26": "1.260",
    "1.58": "1.587",
    "1.59": "1.587",
    "2": "2.000",
    "2.51": "2.520",
    "2.52": "2.520",
    "3.17": "3.175",
    "4": "4.000",
    "5.03": "5.040",
    "6.34": "6.350",
    "8": "8.000",
    "10.07": "10.080",
}

# ---------------------------------------------------------------------------
# Static XML payloads sent to the Yamaha AVR
# ---------------------------------------------------------------------------

_PEQ_BAND_RESET_7 = """
            <Band_1><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_1>
            <Band_2><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_2>
            <Band_3><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_3>
            <Band_4><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_4>
            <Band_5><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_5>
            <Band_6><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_6>
            <Band_7><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_7>"""

_PEQ_BAND_RESET_4 = """
            <Band_1><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_1>
            <Band_2><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_2>
            <Band_3><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_3>
            <Band_4><Gain><Val>0</Val></Gain><Q>1.000</Q></Band_4>"""

AVR_RESET_PEQ_XML: str = (
    '<YAMAHA_AV cmd="PUT"><System><Speaker_Preout><Pattern_1><PEQ><Manual_Data>'
    f"<Front_L>{_PEQ_BAND_RESET_7}</Front_L>"
    f"<Center>{_PEQ_BAND_RESET_7}</Center>"
    f"<Front_R>{_PEQ_BAND_RESET_7}</Front_R>"
    f"<Front_Presence_L>{_PEQ_BAND_RESET_7}</Front_Presence_L>"
    f"<Front_Presence_R>{_PEQ_BAND_RESET_7}</Front_Presence_R>"
    f"<Sur_R>{_PEQ_BAND_RESET_7}</Sur_R>"
    f"<Sur_Back_R>{_PEQ_BAND_RESET_7}</Sur_Back_R>"
    f"<Sur_Back_L>{_PEQ_BAND_RESET_7}</Sur_Back_L>"
    f"<Sur_L>{_PEQ_BAND_RESET_7}</Sur_L>"
    f"<Subwoofer_1>{_PEQ_BAND_RESET_4}</Subwoofer_1>"
    "</Manual_Data></PEQ></Pattern_1></Speaker_Preout></System></YAMAHA_AV>"
)

AVR_GET_LEVELS_XML: str = (
    '<YAMAHA_AV cmd="GET"><System><Speaker_Preout><Pattern_1>'
    "<Lvl>GetParam</Lvl>"
    "</Pattern_1></Speaker_Preout></System></YAMAHA_AV>"
)

# ---------------------------------------------------------------------------
# Preparation XML payloads (extracted from shell scripts)
# ---------------------------------------------------------------------------

AVR_GET_STATUS_XML: str = (
    '<YAMAHA_AV cmd="GET"><System><Config>GetParam</Config></System></YAMAHA_AV>'
)

AVR_SET_PEQ_THROUGH_XML: str = (
    '<YAMAHA_AV cmd="PUT"><System><Speaker_Preout><Pattern_1><PEQ>'
    "<Sel>Through</Sel>"
    "<Manual_Data><Reset>Execute</Reset></Manual_Data>"
    "</PEQ></Pattern_1></Speaker_Preout></System>"
    "<Main_Zone><Sound_Video>"
    "<YPAO_Volume>Off</YPAO_Volume>"
    "</Sound_Video></Main_Zone></YAMAHA_AV>"
)

AVR_DATA_COPY_FROM_FLAT_XML: str = (
    '<YAMAHA_AV cmd="PUT"><System><Speaker_Preout><Pattern_1><PEQ>'
    "<Sel>Manual</Sel>"
    "<Data_Copy_From>Flat</Data_Copy_From>"
    "</PEQ></Pattern_1></Speaker_Preout></System>"
    "<Main_Zone><Sound_Video>"
    "<YPAO_Volume>On</YPAO_Volume>"
    "</Sound_Video></Main_Zone></YAMAHA_AV>"
)

AVR_SET_SPK_LARGE_XML: str = (
    '<YAMAHA_AV cmd="PUT"><System><Speaker_Preout><Pattern_1><Config>'
    "<Front><Type>Large</Type></Front>"
    "<Center><Type>Large</Type></Center>"
    "<Sur><Type>Large</Type></Sur>"
    "<Sur_Back><Type>Large</Type></Sur_Back>"
    "<Front_Presence><Type>Large</Type></Front_Presence>"
    "</Config></Pattern_1></Speaker_Preout></System></YAMAHA_AV>"
)

AVR_RESET_SURROUND_XML: str = (
    '<YAMAHA_AV cmd="PUT"><Main_Zone><Surround>'
    "<Program_Sel><Current>"
    "<Straight>On</Straight>"
    "<Enhancer>Off</Enhancer>"
    "</Current></Program_Sel>"
    "<Adaptive_DSP_Lvl>Off</Adaptive_DSP_Lvl>"
    "<VSBS>Off</VSBS>"
    "</Surround></Main_Zone></YAMAHA_AV>"
)

AVR_RESET_SOUND_VIDEO_XML: str = (
    '<YAMAHA_AV cmd="PUT">'
    "<System><Sound_Video>"
    "<Dynamic_Range>MAX</Dynamic_Range>"
    "</Sound_Video></System>"
    "<Main_Zone>"
    "<Volume><Subwoofer_Trim>0</Subwoofer_Trim></Volume>"
    "<Sound_Video>"
    "<Tone><Bass>0</Bass><Treble>0</Treble></Tone>"
    "<Pure_Direct><Mode>Off</Mode></Pure_Direct>"
    "<Extra_Bass>Off</Extra_Bass>"
    "<Adaptive_DRC>Off</Adaptive_DRC>"
    "<Dialogue_Adjust>"
    "<Dialogue_Lvl>0</Dialogue_Lvl>"
    "<Dialogue_Lift>0</Dialogue_Lift>"
    "<DTS_Dialogue_Control>0</DTS_Dialogue_Control>"
    "</Dialogue_Adjust>"
    "</Sound_Video>"
    "</Main_Zone></YAMAHA_AV>"
)
