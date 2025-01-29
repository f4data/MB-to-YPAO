# MB-to-YPAO

Convert the Magic Beans calibration output format to YPAO format and push it to the AVR


## Installation

### Command line execution
1. Clone the repository: `git clone https://github.com/f4data/MB-to-YPAO.git`
2. Create a virtual environment `virtualenv .venv`
3. Activate it `source .venv/bin/activate`
4. Install the requirements: `pip install -r requirements.txt`
5. Run the application: `python app.py`

### Docker execution
1. Run the following command:
```
docker run \
-name mb-to-ypao \
-p 5002:5002 \
ghcr.io/f4data/mb-to-ypao:latest
```

## Usage

1. Run Magic Beans and store the file(s)
2. Open a web browser and navigate to `http://localhost:5002` or `http://<docker_server_ip>:5002`
3. Switch ON your Yamaha AVR
4. Provide the IP Address of your Yamaha AVR
5. Select the file you want to upload
6. Done
