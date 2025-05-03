from flask import Flask, render_template, request
from markupsafe import escape
import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Dictionary to map Speakers (MB) to Yamaha
dict_speakers = {
    "Front Left": "Front_L",
    "Front Right": "Front_R",
    "Center": "Center",
    "LFE": "Subwoofer_1",
    "Surround Right": "Sur_R",
    "Surround Left": "Sur_L",
    "Surround Back Right": "Sur_Back_R",
    "Surround Back Left": "Sur_Back_L",
    "Middle Height Right": "Front_Presence_R",
    "Middle Height Left": "Front_Presence_L"
}

# Dictionary to restore the frequency values
dict_freq = {
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
    "16000 Hz": "16.0 kHz"
}

# Dictionary to restore the rounded Q values
dict_q = {
    "0.5": "0.500",
    "0.62": "0.630",
    "0.79": "0.794",
    "1": "1.000",
    "1.25": "1.260",
    "1.58": "1.587",
    "2": "2.000",
    "2.51": "2.520",
    "3.17": "3.175",
    "4": "4.000",
    "5.03": "5.040",
    "6.34": "6.350",
    "8": "8.000",
    "10.07": "10.080"
}

avr_reset_peq_xml = '''<YAMAHA_AV cmd="PUT">
    <System>
        <Speaker_Preout>
            <Pattern_1>
                <PEQ>
                    <Manual_Data>
                        <Front_L>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Front_L>
                        <Center>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Center>
                        <Front_R>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Front_R>
                        <Front_Presence_L>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Front_Presence_L>
                        <Front_Presence_R>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Front_Presence_R>
                        <Sur_R>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Sur_R>
                        <Sur_Back_R>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Sur_Back_R>
                        <Sur_Back_L>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Sur_Back_L>
                        <Sur_L>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                            <Band_5>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_5>
                            <Band_6>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_6>
                            <Band_7>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_7>
                        </Sur_L>
                        <Subwoofer_1>
                            <Band_1>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_1>
                            <Band_2>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_2>
                            <Band_3>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_3>
                            <Band_4>
                                <Gain>
                                    <Val>0</Val>
                                </Gain>
                                <Q>1.000</Q>
                            </Band_4>
                        </Subwoofer_1>
                    </Manual_Data>
                </PEQ>
            </Pattern_1>
        </Speaker_Preout>
    </System>
</YAMAHA_AV>'''

avr_get_levels_xml = '''<YAMAHA_AV cmd="GET">
    <System>
        <Speaker_Preout>
            <Pattern_1>
                <Lvl>GetParam</Lvl>
            </Pattern_1>
        </Speaker_Preout>
    </System>
</YAMAHA_AV>'''


def parse_speaker_name(speaker):
    """
    Function to parse the Speaker Name (MB) to Yamaha Web format
    """
    return dict_speakers[speaker]

def parse_frequency_value(freq):
    """
    Function to parse the Frequency value (MB) to Yamaha Web format
    """
    return dict_freq[freq]

def parse_gain_value(gain):
    """
    Function to parse the Gain value (MB) to Yamaha Web format
    """
    value = gain.split()[0].strip()
    return int(float(value)*10)

def parse_q_value(q):
    """
    Function to parse the Q value (MB) to Yamaha Web format
    """
    return dict_q[q]

def create_filter_element(filter_data: dict):
    """
    Function to create XML elements
    """
    filter_element = ET.Element(f"Band_{filter_data['number']}")

    if 'Frequency' in filter_data:
        freq = ET.SubElement(filter_element, "Freq")
        freq.text = str(filter_data['Frequency'])

    if 'Gain' in filter_data:
        gain = ET.SubElement(filter_element, "Gain")
        val = ET.SubElement(gain, "Val")
        val.text = str(filter_data['Gain'])

    if 'Q factor' in filter_data:
        q = ET.SubElement(filter_element, "Q")
        q.text = str(filter_data['Q factor'])

    return filter_element

def parse_text_to_xml(text):
    """
    Function to parse the text file and create XML structure
    """
    lines = text.strip().split('\n')
    manual_data = ET.Element("Manual_Data")
    current_section = None

    for line in lines:
        line = line.strip()
        if line.endswith('='):
            current_section = ET.SubElement(manual_data, parse_speaker_name(prev_line))
        elif line.startswith('Filter'):
            filter_data = {'number': line.split()[1].strip(':')}
        elif line.startswith('-'):
            key, value = line.split(':')
            if key.strip('- ') == 'Frequency':  
                filter_data[key.strip('- ')] = parse_frequency_value(value.strip())
            if key.strip('- ') == 'Q factor':  
                filter_data[key.strip('- ')] = parse_q_value(value.strip())
            if key.strip('- ') == 'Gain':
                filter_data[key.strip('- ')] = parse_gain_value(value.strip())
                current_section.append(create_filter_element(filter_data))
        prev_line = line

    return manual_data

def create_peq_request_xml(text):
    manual_data = parse_text_to_xml(text)

    root = ET.Element("YAMAHA_AV", cmd="PUT")
    system = ET.SubElement(root, "System")
    speaker_preout = ET.SubElement(system, "Speaker_Preout")
    pattern_1 = ET.SubElement(speaker_preout, "Pattern_1")
    peq = ET.SubElement(pattern_1, "PEQ") 
    peq.append(manual_data)

    #return ET.ElementTree(root)
    return root

def parse_mb_calibration_into_ypao_xml(lines):
    myxml = create_peq_request_xml(lines)

    # # Parse the XML string
    xml_str = ET.tostring(myxml, encoding='utf-8', method='xml')

    return xml_str
    
def prettify_xml(xml_str):
    # Pretty print the XML
    xml_str_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
    print(xml_str_pretty)
    return xml_str_pretty

def publish_ypao_configuration_to_avr(xml_str, avr_ip):
    # Replace with your AVR's IP address
    # avr_ip = "192.168.88.253"
    url = f"http://{avr_ip}:80/YamahaRemoteControl/ctrl"
    payload = xml_str

    headers = {'Content-Type': 'application/xml'}
    response = requests.post(url, headers=headers, data=payload)

    return response

def process_avr_response(response):
    if response.status_code == 200:
        response_xml = ET.fromstring(response.text)
        rc_value = response_xml.get("RC")

        if rc_value == "0":
            return ("PEQ values updated successfully!", response.status_code)
        else:
            return ("Failed to update PEQ values. The receiver should be Powered on.", response.text, response.status_code)
    else:
        return ("Failed to update PEQ values. Failed to connect to Yamaha AVR.", response.status_code, response.text)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        ip = request.form.get('ip')
        
        if action == 'reset':
            xml_str = avr_reset_peq_xml
            response_txt = "PEQ Values not reset"

            response = publish_ypao_configuration_to_avr(xml_str, ip)
            response_txt = process_avr_response(response)

            xml_str_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
            return render_template('index.html', response=response_txt, avr_data=escape(xml_str_pretty))
        
        if action == 'submit':
            f = request.files['file']
            if f:
                #filename = secure_filename(f.filename)
                filename = f.filename
                f.save(filename)
                try:
                    with open(filename, 'r') as file:
                        content = file.read()
                except FileNotFoundError:
                    return 'File not found!'
                except PermissionError:
                    return 'Permission denied!'
                except Exception as e:
                    return 'Error reading file: ' + str(e)
                
                xml_str = parse_mb_calibration_into_ypao_xml(content)
                response_txt = "Not applied to AVR"

                response = publish_ypao_configuration_to_avr(xml_str, ip)
                response_txt = process_avr_response(response)

                xml_str_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
                return render_template('index.html', response=response_txt, mb_data=content, avr_data=escape(xml_str_pretty))
    return render_template("index.html")

@app.route("/about")
def about():
    return "This is the about page."

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
