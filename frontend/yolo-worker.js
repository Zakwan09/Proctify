
// yolo-worker.js — runs in isolated Web Worker scope, no MediaPipe conflict
// Place this file in: public/yolo-worker.js

let session = null
let ortReady = false

// Load ORT inside the worker — completely isolated from main thread
importScripts("https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.min.js")

ort.env.wasm.numThreads = 1
ort.env.wasm.wasmPaths  = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/"
ortReady = true

self.onmessage = async (e) => {
  const { type, payload } = e.data

  if (type === "load") {
    try {
      session = await ort.InferenceSession.create(payload.modelUrl, {
        executionProviders: ["wasm"],
      })
      self.postMessage({ type: "loaded", inputNames: session.inputNames, outputNames: session.outputNames })
    } catch (err) {
      self.postMessage({ type: "error", message: String(err) })
    }
  }

  if (type === "infer") {
    if (!session) { self.postMessage({ type: "result", phoneFound: false }); return }
    try {
      const { pixels, width, height } = payload
      const S = 640
      const tensor = new Float32Array(3 * S * S)
      // pixels is already 640x640 RGBA from ImageData
      for (let i = 0; i < S * S; i++) {
        tensor[i]         = pixels[i*4]   / 255  // R
        tensor[i + S*S]   = pixels[i*4+1] / 255  // G
        tensor[i + S*S*2] = pixels[i*4+2] / 255  // B
      }

      const inputName = session.inputNames[0]
      const feed = { [inputName]: new ort.Tensor("float32", tensor, [1, 3, S, S]) }
      const out  = await session.run(feed)

      const outName = session.outputNames[0]
      const raw     = out[outName].data
      const dims    = out[outName].dims

      // COCO class 67 = cell phone
      const PHONE_CLASS = 67
      const THRESH      = 0.40
      let phoneFound    = false

      if (dims[1] === 84 && dims[2] === 8400) {
        // Transposed [1,84,8400]
        for (let i = 0; i < 8400; i++) {
          if (raw[(4 + PHONE_CLASS) * 8400 + i] > THRESH) { phoneFound = true; break }
        }
      } else if (dims[1] === 8400 && dims[2] === 84) {
        // Row-major [1,8400,84]
        for (let i = 0; i < 8400; i++) {
          if (raw[i * 84 + 4 + PHONE_CLASS] > THRESH) { phoneFound = true; break }
        }
      }

      self.postMessage({ type: "result", phoneFound })
    } catch (err) {
      self.postMessage({ type: "inferError", message: String(err) })
    }
  }
}
