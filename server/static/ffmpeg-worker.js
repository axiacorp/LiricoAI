const FFMessageType = {
  LOAD: "LOAD",
  EXEC: "EXEC",
  WRITE_FILE: "WRITE_FILE",
  READ_FILE: "READ_FILE",
  DELETE_FILE: "DELETE_FILE",
  RENAME: "RENAME",
  CREATE_DIR: "CREATE_DIR",
  LIST_DIR: "LIST_DIR",
  DELETE_DIR: "DELETE_DIR",
  ERROR: "ERROR",
  DOWNLOAD: "DOWNLOAD",
  PROGRESS: "PROGRESS",
  LOG: "LOG",
  MOUNT: "MOUNT",
  UNMOUNT: "UNMOUNT"
};

let ffmpeg;

async function load({coreURL, wasmURL, workerURL}) {
  const first = !ffmpeg;
  try {
    importScripts(coreURL);
  } catch {
    const mod = await import(coreURL);
    self.createFFmpegCore = mod.default;
  }
  if (!self.createFFmpegCore) throw new Error("failed to import ffmpeg-core.js");
  const resolvedWasm = wasmURL || coreURL.replace(/\.js$/g, ".wasm");
  const resolvedWorker = workerURL || coreURL.replace(/\.js$/g, ".worker.js");
  ffmpeg = await self.createFFmpegCore({
    mainScriptUrlOrBlob: coreURL + "#" + btoa(JSON.stringify({
      wasmURL: resolvedWasm,
      workerURL: resolvedWorker
    }))
  });
  ffmpeg.setLogger((data) => self.postMessage({type: FFMessageType.LOG, data}));
  ffmpeg.setProgress((data) => self.postMessage({type: FFMessageType.PROGRESS, data}));
  return first;
}

self.onmessage = async ({data: {id, type, data}}) => {
  const transfer = [];
  let result;
  try {
    if (type !== FFMessageType.LOAD && !ffmpeg) throw new Error("ffmpeg is not loaded");
    switch(type) {
      case FFMessageType.LOAD:
        result = await load(data || {});
        break;
      case FFMessageType.EXEC:
        ffmpeg.setTimeout(data.timeout ?? -1);
        ffmpeg.exec(...data.args);
        result = ffmpeg.ret;
        ffmpeg.reset();
        break;
      case FFMessageType.WRITE_FILE:
        ffmpeg.FS.writeFile(data.path, data.data);
        result = true;
        break;
      case FFMessageType.READ_FILE:
        result = ffmpeg.FS.readFile(data.path, {encoding: data.encoding});
        break;
      case FFMessageType.DELETE_FILE:
        ffmpeg.FS.unlink(data.path);
        result = true;
        break;
      case FFMessageType.RENAME:
        ffmpeg.FS.rename(data.oldPath, data.newPath);
        result = true;
        break;
      case FFMessageType.CREATE_DIR:
        ffmpeg.FS.mkdir(data.path);
        result = true;
        break;
      case FFMessageType.LIST_DIR: {
        const names = ffmpeg.FS.readdir(data.path);
        result = names.map(name => {
          const stat = ffmpeg.FS.stat(data.path + "/" + name);
          return {name, isDir: ffmpeg.FS.isDir(stat.mode)};
        });
        break;
      }
      case FFMessageType.DELETE_DIR:
        ffmpeg.FS.rmdir(data.path);
        result = true;
        break;
      case FFMessageType.MOUNT: {
        const fs = ffmpeg.FS.filesystems[data.fsType];
        if (!fs) throw new Error("filesystem not available");
        ffmpeg.FS.mount(fs, data.options, data.mountPoint);
        result = true;
        break;
      }
      case FFMessageType.UNMOUNT:
        ffmpeg.FS.unmount(data.mountPoint);
        result = true;
        break;
      default:
        throw new Error("unknown message type: " + type);
    }
  } catch (e) {
    self.postMessage({id, type: FFMessageType.ERROR, data: e?.toString?.() || String(e)});
    return;
  }
  if (result instanceof Uint8Array) transfer.push(result.buffer);
  self.postMessage({id, type, data: result}, transfer);
};