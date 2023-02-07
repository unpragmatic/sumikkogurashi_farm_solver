from flask import Flask, flash, request, redirect, url_for, jsonify
from flask_cors import CORS

import cv2 as cv
import numpy as np
from scipy import stats


app = Flask(__name__)
CORS(app)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


tileFileNames = ["tile000.png"
,"tile001.png"
,"tile002.png"
,"tile003.png"
,"tile004.png"
,"tile006.png"
,"tile022.png"
,"tile010.png"
,"tile012.png"
,"tile013.png"
,"tile024.png"
,"tile025.png"
,"tile031.png"
,"tile034.png"
,"tile019.png"
,"tile000b.png"
,"tile004b.png"
,"tile005b.png"
,"tile006b.png"
,"tile010b.png"
,"tile013b.png"
,"tile057.png"
,"tile036.png"
,"tile056.png"
,"tile060.png"
,"tile037c.png"
,"tile046c.png"
,"tile060c.png"
,"tile001f.png"
,"tile002d.png"
,"tile003d.png"
,"tile009d.png"
,"tile010f.png"
,"tile018e.png"
,"tile011g.png"
,"tile048g.png"]


tileSize = 141
maskMat = np.zeros((tileSize, tileSize), dtype=np.uint8)
cv.circle(maskMat, (70, 70), 61, (255, 255, 255), -1)

tileMats = [ cv.imread(filename, cv.IMREAD_UNCHANGED) for filename in tileFileNames]

defaultThreshold = 0.003
tileMatThresholds = [ defaultThreshold for mat in tileMats ]
tileMatThresholds[6] = 0.001
tileMatThresholds[34] = 0.001
tileMatThresholds[35] = 0.001
print(tileMats)
print([mat.shape for mat in tileMats])


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            print(file)
            data = np.asarray(bytearray(file.read()), dtype=np.uint8)
            print(data)
            imgMat = cv.imdecode(data, cv.IMREAD_UNCHANGED)
            print(imgMat)

            matches = []
            # tileMatId = 0
            for tileMatId in range(len(tileMats)):
                print(tileMatId)
                res = cv.matchTemplate(imgMat, tileMats[tileMatId], cv.TM_SQDIFF_NORMED, mask = maskMat)

                
                # threshold = 4_000_000.0
                # threshold = 0.00275
                threshold = tileMatThresholds[tileMatId]
                for y, x in np.ndindex(res.shape):
                    value = res[y, x]
                    

                    if value < threshold:
                        print([value, tileMatId, tileFileNames[tileMatId]])
                        matches.append((x, y, tileMatId, value))

            if len(matches) == 0:
                return jsonify([[]])
                
            print(res.shape)
            print(matches)

            minX = np.amin([match[0] for match in matches])
            minY = np.amin([match[1] for match in matches])
            maxX = np.amax([match[0] for match in matches])
            maxY = np.amax([match[1] for match in matches])
            print((minX, minY, maxX, maxY))
            

            gridWidth = np.rint((maxX - minX) / tileSize).astype(np.int32) + 1
            gridHeight = np.rint((maxY - minY) / tileSize).astype(np.int32) + 1
            #1 matchVoteGrid = [[[] for x in range(gridWidth)] for y in range(gridHeight)]
            matchVoteGrid = [[[0 for tile in tileMats] for x in range(gridWidth)] for y in range(gridHeight)]

            for match in matches:
                x = match[0]
                y = match[1]
                tileId = match[2]
                value = match[3]
                normalizedX = np.rint((x - minX) / tileSize).astype(np.int32)
                normalizedY = np.rint((y - minY) / tileSize).astype(np.int32)
                #1 matchVoteGrid[normalizedY][normalizedX].append(tileId)
                totalMatchesOfTileId = len([a for a in matches if a[2] == tileId])
                matchVoteGrid[normalizedY][normalizedX][tileId] += (value / totalMatchesOfTileId)
            print(matchVoteGrid)

            grid = [[-1 for x in range(gridWidth)] for y in range(gridHeight)]
            for y, x in np.ndindex((gridHeight, gridWidth)):
                voteArray = matchVoteGrid[y][x]
                theta = np.array(voteArray)
                #1 if len(voteArray) == 0:
                #1    continue
                if len(theta[np.nonzero(theta)]) == 0:
                    continue
                
                #1 voteWinner = stats.mode(voteArray)[0][0]
                # voteWinner = np.argmin(voteArray)
                
                voteWinner = np.where( theta==np.min(theta[np.nonzero(theta)]))[0][0]
                grid[y][x] = int(voteWinner)
            
            print(grid)

            # cv.matchTemplate(canvasOutputImageMat, tileMat, dest, cv.TM_SQDIFF_NORMED, mask)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(grid)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''