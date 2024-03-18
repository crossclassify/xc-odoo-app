// Initialize the agent at application startup.
// Some ad blockers or browsers will block Fingerprint CDN URL.
// To fix this, please use the NPM package instead.
const fpPromise = import("https://openfpcdn.io/fingerprintjs/v3").then(
  (FingerprintJS) => FingerprintJS.load()
);
// const fpPromise_pro = import("https://fpjscdn.net/v3/NnFaftayuhsrZmnMWNka")
//   .catch(() => console.log("Error"))
//   .then((FingerprintJS) => FingerprintJS.load())
//   .catch(() => console.log("Error"));
