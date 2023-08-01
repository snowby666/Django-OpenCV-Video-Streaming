# Django OpenCV Video Streaming

This project utilizes Django Channels and OpenCV for Real-time ML on Video Streaming. Plus, it works when deployed into production

## Table of Contents:
- [Highlights](#highlights)
- [Installation](#installation)
- [Documentation](#documentation)
  * [How it works](#how-it-works)
  * [Optimization](#optimization)
- [Copyright](#copyright)
  * [Copyright Notice](#copyright-notice)

*Table of contents generated with [markdown-toc](http://ecotrust-canada.github.io/markdown-toc).*

## Highlights:
 - Real time video streaming using Websocket protocol (Django-Channels)
 - Integrated with OpenCV-Python for Image Processing (Emotion detection, facial landmarks, etc.)
 - Stream real-time data with C3.js

## Installation:
- First, clone the repository and enter the folder:
```
git clone https://github.com/snowby666/Django-OpenCV-Video-Streaming.git
cd Django-OpenCV-Video-Streaming
```
- Set up a virtual environment (optional)
```
python -m venv .venv
.venv\Scripts\activate.bat      
```
- Install the required packages:
```
pip install -r requirements.txt
```
#### The repository is currently compatible with Python 3.9+.
- Initialise the project:
```
python manage.py makemigrations
python manage.py migrate

```
- Finally, run the web server:
```
daphne VideoStream.asgi:application --port 8000 --bind 127.0.0.1     
```

## Documentation:

### How it works:
In this project I don't use ~`cap = cv2.VideoCapture(0)`~ to receive webcam feed since it only works on local machine. For production deployment, I choose Django Channels because it supports Websocket.
I also tried SSE + Ajax approach but the performance was inefficent.

So here the Websocket thingy

Normal example:
```python

```


## Copyright:
This program is licensed under the [GNU GPL v3](https://github.com/snowby666/Django-OpenCV-Video-Streaming/blob/main/LICENSE). All code has been written by me, [snowby666](https://github.com/snowby666).

### Copyright Notice:
```
snowby666/Django-OpenCV-Video-Streaming: a project utilizes Django Channels and OpenCV for Real-time ML on Video Streaming
Copyright (C) 2023 snowby666

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
