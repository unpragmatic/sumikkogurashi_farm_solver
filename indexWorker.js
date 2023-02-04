importScripts('opencv.js');

onmessage = (e) => {
    console.log('Message received from main script');

    const [mainImgMat, tileMat, dest, method, mask] = e.data;
    console.log("WORKER");
    console.log(e);
    cv.matchTemplate(mainImgMat, tileMat, dest, method, mask);
    
    console.log('Posting message back to main script');
    postMessage(dest);
}