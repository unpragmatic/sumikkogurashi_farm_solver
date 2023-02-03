import { cv, cvTranslateError } from 'https://deno.land/x/opencv@v4.3.0-10/mod.ts'

import { Image } from "https://deno.land/x/imagescript@1.2.15/mod.ts"

// const imagePath = "test_1.jpg";
// const raw = await Deno.readFile(imagePath);

// const baseImage = decode(raw);
// console.log(baseImage);
// console.log(baseImage.data.length);
// const cvImage = cv.matFromArray(baseImage.height, baseImage.width, cv.CV_8UC4, baseImage.data);

// console.log(cvImage);

export type Match = false | {
    x: number;
    y: number;
    width: number;
    height: number;
    center?: {
        x: number;
        y: number;
    };
};

async function main() {
    const haystackPath = "test_1.jpg";
    const needlePath = "corner_1.png";

    const drawOutput = true;

    const perfStart = performance.now()

    const haystack = await Image.decode(Deno.readFileSync(haystackPath));
    const needle = await Image.decode(Deno.readFileSync(needlePath));

    const haystackMat = cv.matFromImageData({
        data: haystack.bitmap,
        width: haystack.width,
        height: haystack.height,
    });
    let needleMat = cv.matFromImageData({
        data: needle.bitmap,
        width: needle.width,
        height: needle.height,
    });
    let dst = new cv.Mat();
    cv.rotate(needleMat, dst, cv.ROTATE_90_CLOCKWISE);
    cv.rotate(dst, dst, cv.ROTATE_90_CLOCKWISE);
    cv.rotate(dst, dst, cv.ROTATE_90_CLOCKWISE);
    needleMat = dst;

    const dest = new cv.Mat();
    const mask = new cv.Mat();
    cv.matchTemplate(haystackMat, needleMat, dest, cv.TM_SQDIFF, mask);

    const result = cv.minMaxLoc(dest, mask);
    const match: Match = {
        x: result.minLoc.x,
        y: result.minLoc.y,
        width: needleMat.cols,
        height: needleMat.rows,
    };
    match.center = {
        x: match.x + (match.width * 0.5),
        y: match.y + (match.height * 0.5),
    };

    if (drawOutput) {
        haystack.drawBox(
            match.x,
            match.y,
            match.width,
            match.height,
            Image.rgbaToColor(255, 0, 0, 255),
        );
    
        // Deno.writeFileSync(`${haystackPath.replace('.jpg', '-result.jpg')}`, await needleMat.encode(0));
        Deno.writeFileSync(`${haystackPath.replace('.jpg', '-result.jpg')}`, await haystack.encode(0));
    }

    const perfEnd = performance.now()
    console.log(`Match took ${perfEnd - perfStart}ms`)

    return match.x > 0 || match.y > 0 ? match : false;
}

await main();

// const imagePath = "test_1.jpg";
// // let raw = await readFile(imagePath);
// //decode"
// // let result = decode(raw);
// const raw = await Deno.readFile(imagePath);
// const result = decode(raw);

// const message = `Height: ${result.height}, Width: ${result.width}`;
// console.log(message);
console.log("Hello");