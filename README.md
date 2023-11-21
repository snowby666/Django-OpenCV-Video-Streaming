<div align='center'>

# Django OpenCV Video Streaming
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-397/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Last Commit](https://img.shields.io/github/last-commit/snowby666/Django-OpenCV-Video-Streaming)
<br>
<p><em>This project utilizes Django Channels and OpenCV for Real-time ML on Video Streaming. Plus, it works when deployed to production.</em></p>

</div>

![Demo](https://github.com/snowby666/Django-OpenCV-Video-Streaming/blob/main/.examples/walkthrough.gif)

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
 - Real time video streaming using WebSockets protocol (Django-Channels)
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
> [!NOTE]
> The repository is currently compatible with Python 3.9+
- Initialise the project:
```
python manage.py makemigrations
python manage.py migrate
```
- Finally, run the web server:
```
daphne VideoStream.asgi:application --port 8000 --bind 127.0.0.1     
```
- If you want to test the project in production, you can set up a Ngrok tunnel or run the existed one inside this project's folder [ngrok.ipynb](https://github.com/snowby666/Django-OpenCV-Video-Streaming/blob/main/ngrok.ipynb)
```
from pyngrok import ngrok
ngrok.kill()
# You can get your authtoken from https://dashboard.ngrok.com/auth
# I prepared this token for you, but you can get your own
auth_token = '2MBBpglFtyIYedSYhqf3J9qadxk_3aCaoe72L8oBJZbm8kmMo' 
ngrok.set_auth_token(auth_token)

ngrok.connect(8000)
```

## Documentation:

### How it works:
In this project, I don't use ~`cap = cv2.VideoCapture(0)`~ to retrieve webcam feed since it only works on local machine. For production deployment, I choose [Django Channels](https://channels.readthedocs.io/en/latest/) because it supports Websocket.
I also tried SSE + Ajax approach but the performance was inefficent.

With WebSockets implemented to this project, we can stream data persistently between Client and Server. 
Here an illustration about the differences between the normal HTTP request-response cycles and WebSockets:

![http](https://cdn.discordapp.com/attachments/957946068836950026/1135866429120450590/image.png)
![websocket](https://cdn.discordapp.com/attachments/957946068836950026/1135866799028699136/image.png)

### Optimization:

- Client-side (capture each frame from the user's webcam in the browser, then encode it into bytes, and send it to the Server-side)

- Example:
```js
  var ws = new WebSocket(
      ws_scheme + '://' + window.location.host + '/'
      );
      ws.onopen = (event) => {
          console.log('websocket connected!!!');
      };
      ws.onmessage = (event) => {
      //console.log("WebSocket message received: ", event.data);
      frameUpdate = event.data;
      img.src = "data:image/jpeg;base64," + frameUpdate;
      
      };
      ws.onclose = (event) => {
          console.log('Close');
      };
      if (navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
      video.srcObject = stream;
      video.play();
      var width = video.width;
      var height = video.height;
      var delay = 100; // adjust the delay to fit your needs (ms)
      var jpegQuality = 0.7; // adjust the quality to fit your needs (0.0 -> 1.0)

      setInterval(function() {
      context.drawImage(video, 0, 0, width, height);
      canvas.toBlob(function(blob) {
          if (ws.readyState == WebSocket.OPEN) {
              if (mode == true){
                  ws.send(new Uint8Array([]));
              } else {
                  ws.send(blob);
              }
          }
      }, 'image/jpeg', jpegQuality);
      }, delay);

    });}
```
- Server-side (decode the Bytes data from Client-side. Next, we can use OpenCV for Image Processing with any ML/AI algorithm or heavy computational processes of your choice. Finally, the frame will be encoded to Base64 and passed back to Client-side to update the src of canvas)

- Example:
```python
 async def receive(self, bytes_data):
    if not (bytes_data):
        self.i = 0
        self.fps = 0
        self.prev = 0
        self.new = 0
        print('Closed connection')
        await self.close()
    else:
        self.frame = await self.loop.run_in_executor(None, cv2.imdecode, np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.frame = cv2.resize(self.frame, (500, 500))
        self.gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
        self.i += 1
        
        # Face detection and feature extraction
        self.detections = await self.loop.run_in_executor(None, detector, self.gray, 0)
        if (self.detections):
            # In this case, we only take the first face found
            self.detection = self.detections[0]
            self.x1, self.y1, self.x2, self.y2 = self.detection.left(), self.detection.top(), self.detection.right(), self.detection.bottom()
            await self.draw_border(self.frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2, 20, 10)
            
            self.shape = await self.loop.run_in_executor(None, predictor, self.frame, self.detection)
            self.shape = face_utils.shape_to_np(self.shape)
            
            # Feature extraction
            self.leyebrow = self.shape[lBegin:lEnd]
            self.reyebrow = self.shape[rBegin:rEnd]
            self.openmouth = self.shape[l_lower:l_upper]
            self.innermouth =self. shape[i_lower:i_upper]
            self.lefteye = self.shape[el_lower:el_upper]
            self.righteye = self.shape[er_lower:er_upper]
            
            # Convex hull
            self.reyebrowhull = cv2.convexHull(self.reyebrow)
            self.leyebrowhull = cv2.convexHull(self.leyebrow)
            self.openmouthhull = cv2.convexHull(self.openmouth) 
            self.innermouthhull = cv2.convexHull(self.innermouth)
            self.leyehull = cv2.convexHull(self.lefteye)
            self.reyehull = cv2.convexHull(self.righteye)
            self.emotion = await self.loop.run_in_executor(None, get_emotion, self.detection, self.gray)
            
            await self.fps_count()  
            cv2.putText(self.frame, "FPS: {}".format((self.fps)), (330,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
            cv2.putText(self.frame, "Frames: {}".format((self.i)), (220,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
            cv2.putText(self.frame, "Emotion: {}".format((self.emotion)), (50,40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (54, 161, 255), 1)
            cv2.drawContours(self.frame, [self.reyebrowhull, self.leyebrowhull, self.openmouthhull, self.innermouthhull, self.leyehull, self.reyehull], -1, (219, 255, 99), 1)
            
        # Encoding and sending the image
        self.buffer_img = await self.loop.run_in_executor(None, cv2.imencode, '.jpeg', self.frame)
        self.b64_img = base64.b64encode(self.buffer_img[1]).decode('utf-8')
        # Send the base64 encoded image back to the client
        asyncio.sleep(100/1000)
        await self.send(self.b64_img)
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
