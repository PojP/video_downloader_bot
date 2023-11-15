import fs from "fs";

import chalk from "chalk";
import parseArgs from "minimist";
import { Listr } from "listr2";
import { v4 as uuidv4 } from "uuid";

import { availableLangs, additionalTTS } from "./config/constants.js";
import validate from "./utils/validator.js";
import getVideoId from "./utils/getVideoId.js";
import translateVideo from "./translateVideo.js";
import logger from "./utils/logger.js";
import downloadFile from "./download.js";

var PROTO_PATH = "grpc/translate.proto";

import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";

var packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
var translate_proto = grpc.loadPackageDefinition(packageDefinition).translate;
// LANG PAIR
let REQUEST_LANG = "en";
let RESPONSE_LANG = "ru";

// ARG PARSER
const argv = parseArgs(process.argv.slice(2));

const OUTPUT_DIR = ".";

if (availableLangs.includes(argv.lang)) {
  REQUEST_LANG = argv.lang;
  console.log(`Request language is set to ${REQUEST_LANG}`);
}

if ([...availableLangs, ...additionalTTS].includes(argv.reslang)) {
  RESPONSE_LANG = argv.reslang;
  console.log(`Responsevar PROTO_PATH = __dirname + '/../../protos/helloworld.proto';

var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
var hello_proto = grpc.loadPackageDefinition(packageDefinition).helloworld;

/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {
  callback(null, {message: 'Hello ' + call.request.name});
}

/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  var server = new grpc.Server();
  server.addService(hello_proto.Greeter.service, {sayHello: sayHello});
  server.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), () => {
    server.start();
  });
}

main(); language is set to ${RESPONSE_LANG}`);
}

// TASKS
const tasks = new Listr([], {
  concurrent: true,
  exitOnError: false,
});

const translate = async (finalURL, task) => {
  let test;

  try {
    await translateVideo(
      finalURL,
      REQUEST_LANG,
      RESPONSE_LANG,
      null,
      (success, urlOrError) => {
        if (success) {
          if (!urlOrError) {
            throw new Error(
              chalk.red("The response doesn't contain a download link"),
            );
          }

          task.title = "Video translated successfully.";
          console.info(`Audio Link (${finalURL}): "${chalk.gray(urlOrError)}"`);
          // console.log("TEST", success, urlOrError)
          test = {
            success,
            urlOrError,
          };

          return;
        }

        if (urlOrError === "The translation will take a few minutes") {
          task.title = `The translation is slightly delayed...`;
        } else {
          throw new Error(chalk.red(urlOrError));
        }
      },
    );
  } catch (e) {
    return {
      success: false,
      urlOrError: e.message,
    };
  }

  return test;
};

async function download_mptrs(call, callback) {
  const url = call.request.link;

  if (Boolean(OUTPUT_DIR) && !fs.existsSync(OUTPUT_DIR)) {
    try {
      fs.mkdirSync(OUTPUT_DIR);
    } catch {
      throw new Error("Invalid output directory");
    }
  }

  const service = validate(url);
  if (!service) {
    console.error(chalk.red(`URL: ${url} is unknown service`));
    return callback(null, { filename: `URL: ${url} is unknown service` });
  }

  const videoId = getVideoId(service.host, url);
  if (!videoId) {
    console.error(chalk.red(`Entered unsupported link: ${url}`));
    return callback(null, { filename: `Entered unsupported link: ${url}` });
  }

  tasks.add([
    {
      title: `Performing various tasks (ID: ${videoId}).`,
      task: async (ctx, task) =>
        task.newListr(
          (parent) => [
            {
              title: `Forming a link to the video`,
              task: async () => {
                const finalURL = `${service.url}${videoId}`;
                if (!finalURL) {
                  throw new Error(`Entered unsupported link: ${finalURL}`);
                }
                parent.finalURL = finalURL;
              },
            },
            {
              title: `Translating (ID: ${videoId}).`,
              exitOnError: false,
              task: async (ctxSub, subtask) => {
                // ! TODO: НЕ РАБОТАЕТ ЕСЛИ ВИДЕО НЕ ИМЕЕТ ПЕРЕВОДА
                await new Promise(async (resolve, reject) => {
                  try {
                    let result;
                    result = await translate(parent.finalURL, subtask);
                    // console.log("transalting", result)
                    if (typeof result !== "object") {
                      await new Promise(async (resolve) => {
                        const intervalId = setInterval(async () => {
                          // console.log("interval...", result)
                          result = await translate(parent.finalURL, subtask);
                          if (typeof result === "object") {
                            // console.log("finished", parent.translateResult)
                            clearInterval(intervalId);
                            resolve(result);
                          }
                        }, 30000);
                      });
                    }
                    // console.log("translated", result)
                    parent.translateResult = result;
                    if (!result.success) {
                      subtask.title = result.urlOrError;
                    }
                    resolve(result);
                  } catch (e) {
                    reject(e);
                  }
                });
                // console.log("RESULT", res)
              },
            },
            {
              title: `Downloading (ID: ${videoId}).`,
              exitOnError: false,
              enabled: Boolean(OUTPUT_DIR),
              task: async (ctxSub, subtask) => {
                // await sleep(5000)
                if (
                  !(
                    parent.translateResult?.success &&
                    parent.translateResult?.urlOrError
                  )
                ) {
                  throw new Error(
                    chalk.red(
                      `Downloading failed! Link "${parent.translateResult?.urlOrError}" not found`,
                    ),
                  );
                }

                const taskSubTitle = `(ID: ${videoId})`;
                await downloadFile(
                  parent.translateResult.urlOrError,
                  `${OUTPUT_DIR}/${videoId}---${uuidv4()}.mp3`,
                  subtask,
                  `(ID: ${videoId})`,
                )
                  .then(() => {
                    subtask.title = `Download ${taskSubTitle} completed!`;
                  })
                  .catch((e) => {
                    subtask.title = `Error. Download ${taskSubTitle} failed! Reason: ${e.message}`;
                    callback(null, { message: subtask.title });
                  });
              },
            },
            {
              title: `Finish (ID: ${videoId}).`,
              task: () => {
                parent.title = `Translating finished! (ID: ${videoId}).`;
                return callback(null, {
                  filename: `${OUTPUT_DIR}/${videoId}---${uuidv4()}.mp3`,
                });
              },
            },
          ],
          {
            concurrent: false,
            rendererOptions: {
              collapseSubtasks: false,
            },
            exitOnError: false,
          },
        ),
    },
  ]);

  try {
    await tasks.run();
  } catch (e) {
    console.error(e);
  }
}

/**
 * Implements the SayHello RPC method.
 */
function sayHello(call, callback) {
  callback(null, { message: "Hello " + call.request.name });
}

/**
 * Starts an RPC server that receives requests for the Greeter service at the
 * sample server port
 */
function main() {
  try {
    var server = new grpc.Server();
    server.addService(translate_proto.VoTranslate.service, {
      DownloadTranslation: download_mptrs,
    });
    server.bindAsync(
      "0.0.0.0:50051",
      grpc.ServerCredentials.createInsecure(),
      () => {
        server.start();
      },
    );
  } catch (e) {
    console.error(e);
  }
}

await main();
