const API_BASE_URI = "http://localhost:5000"
const NANOSECONDS_PY = 1;
const MICROSECONDS_PY = 1000 * NANOSECONDS_PY
const MILLISECONDS_PY = 1000 * MICROSECONDS_PY

const MILLISECONDS_JS = 1;
const SECONDS_JS = 1000 * MILLISECONDS_JS;

module.exports = {
    ROOT_PATH: API_BASE_URI,
    MILLISECONDS_PY: MILLISECONDS_PY,
    SECONDS_JS: SECONDS_JS
  };